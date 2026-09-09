import os
import io
import zipfile
import shutil
import uuid
import time
import subprocess
from flask import Flask, render_template, request, send_file, flash
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash'

TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

def cleanup_old_batches():
    """Remove batch folders older than 1 hour"""
    now = time.time()
    for batch_dir in os.listdir(TEMP_FOLDER):
        batch_path = os.path.join(TEMP_FOLDER, batch_dir)
        if os.path.isdir(batch_path):
            if now - os.path.getmtime(batch_path) > 3600:
                try:
                    shutil.rmtree(batch_path)
                except Exception:
                    pass

def get_file_size_kb(filepath):
    return round(os.path.getsize(filepath) / 1024, 2)

def calculate_bento_classes(width, height):
    ratio = width / height
    classes = []
    
    if ratio > 1.5:
        classes.append('span-col-2')
    elif ratio < 0.7:
        classes.append('span-row-2')
    
    if width > 1000 and height > 1000 and 0.8 <= ratio <= 1.2:
        classes.append('span-col-2 span-row-2')
        
    return " ".join(classes)

def get_pngquant_start_index(original_bytes, target_bytes):
    """Calcula o índice de início das estratégias pngquant baseado no percentual
    de redução necessário. Nunca começa mais agressivo que 128 colors (idx 5)
    para preservar qualidade visual e usar o budget de KB da melhor forma."""
    if target_bytes <= 0 or original_bytes <= 0:
        return 0
    ratio = target_bytes / original_bytes
    if ratio > 0.70:   # Redução < 30%: começa em quality 80-100
        return 0
    elif ratio > 0.50: # Redução 30–50%: começa em quality 40-60
        return 2
    elif ratio > 0.35: # Redução 50–65%: começa em 256 colors
        return 4
    elif ratio > 0.20: # Redução 65–80%: começa em 256 colors
        return 4
    else:              # Redução > 80%: começa em 128 colors (não 32!)
        return 5

def get_pil_start_index(original_bytes, target_bytes):
    """Calcula o índice de início do fallback PIL com o mesmo princípio."""
    if target_bytes <= 0 or original_bytes <= 0:
        return 0
    ratio = target_bytes / original_bytes
    if ratio > 0.50:
        return 0
    elif ratio > 0.35:
        return 5  # Começa em quantize 256
    elif ratio > 0.20:
        return 7  # Começa em quantize 64
    else:
        return 8  # Começa em quantize 32

def snap_palette_alpha(png_bytes):
    """Snapa o alpha da PALETA para 0 ou 255 após o pngquant.
    Preserva a seleção de cores do libimagequant e elimina pixels semi-transparentes.
    Mesma abordagem do TinyPNG: quantiza com info completa, limpa alpha depois."""
    try:
        img = Image.open(io.BytesIO(png_bytes))
        if img.mode != 'P' or 'transparency' not in img.info:
            return png_bytes
        trans = img.info['transparency']
        if isinstance(trans, bytes):
            new_trans = bytes(255 if v >= 128 else 0 for v in trans)
        elif isinstance(trans, int):
            new_trans = 0
        else:
            return png_bytes
        out = io.BytesIO()
        img.save(out, format='PNG', transparency=new_trans)
        return out.getvalue()
    except Exception:
        return png_bytes

def compress_image_data(img, target_bytes):
    img_io = io.BytesIO()
    img.save(img_io, format='PNG', compress_level=6)
    best_data = img_io.getvalue()
    
    if target_bytes > 0 and len(best_data) > target_bytes:
        pngquant_strategies = [
            ['--quality', '80-100', '--speed', '4'],
            ['--quality', '60-80', '--speed', '4'],
            ['--quality', '40-60', '--speed', '4'],
            ['--quality', '20-40', '--speed', '4'],
            ['256', '--speed', '4'],
            ['128', '--speed', '4'],
            ['64', '--speed', '4'],
            ['32', '--speed', '4'],
            ['16', '--speed', '4']
        ]
        
        start_idx = get_pngquant_start_index(len(best_data), target_bytes)
        
        success_pngquant = False
        original_best_data = best_data
        
        for params in pngquant_strategies[start_idx:]:
            try:
                cmd = ['pngquant', '--strip'] + params + ['-']
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                out, err = process.communicate(input=original_best_data, timeout=20)
                
                if process.returncode == 0:
                    best_data = snap_palette_alpha(out)
                    success_pngquant = True
                    if len(best_data) <= target_bytes:
                        break
            except subprocess.TimeoutExpired:
                process.kill()
                break
            except Exception:
                break
        
        if not success_pngquant:
            strategies = [
                ('posterize', 7),
                ('posterize', 6),
                ('posterize', 5),
                ('posterize', 4),
                ('posterize', 3),
                ('quantize', 256),
                ('quantize', 128),
                ('quantize', 64),
                ('quantize', 32),
                ('quantize', 16),
                ('quantize', 8)
            ]
            
            pil_start = get_pil_start_index(len(original_best_data), target_bytes)
            
            best_temp_img = img
            for strat_type, param in strategies[pil_start:]:
                q_io = io.BytesIO()
                if strat_type == 'posterize':
                    r, g, b, a = img.split()
                    r = ImageOps.posterize(r, param)
                    g = ImageOps.posterize(g, param)
                    b = ImageOps.posterize(b, param)
                    a = ImageOps.posterize(a, param)
                    temp_img = Image.merge('RGBA', (r, g, b, a))
                else:
                    temp_img = img.quantize(colors=param, method=Image.Quantize.FASTOCTREE, dither=1)
                        
                temp_img.save(q_io, format='PNG', compress_level=6)
                best_temp_img = temp_img
                if q_io.tell() <= target_bytes:
                    break
            
            final_io = io.BytesIO()
            best_temp_img.save(final_io, format='PNG', optimize=True)
            best_data = snap_palette_alpha(final_io.getvalue())
            
    return best_data

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        return {"status": "error", "message": "Nenhum arquivo enviado."}, 400
        
    cleanup_old_batches()
    
    batch_id = uuid.uuid4().hex
    batch_path = os.path.join(TEMP_FOLDER, batch_id)
    os.makedirs(batch_path, exist_ok=True)
    
    uploaded_data = []
    
    for idx, file in enumerate(files):
        if file and file.filename.lower().endswith('.png'):
            original_filename = secure_filename(file.filename)
            safe_name = f"{idx}_{original_filename}"
            orig_path = os.path.join(batch_path, f"orig_{safe_name}")
            file.save(orig_path)
            
            orig_size_kb = get_file_size_kb(orig_path)
            uploaded_data.append({
                "safe_name": safe_name,
                "original_filename": original_filename,
                "orig_size": orig_size_kb
            })
            
    return {"status": "success", "batch_id": batch_id, "files": uploaded_data}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', images=None, existing_files=[], batch_id=None)

    batch_id = request.form.get('batch_id')
    if not batch_id:
        flash('Nenhum lote especificado.')
        return render_template('index.html', images=None, existing_files=[], batch_id=None)
        
    batch_path = os.path.join(TEMP_FOLDER, batch_id)
    if not os.path.isdir(batch_path):
        flash('Sessão expirada ou lote inválido. Por favor, envie as imagens novamente.')
        return render_template('index.html', images=None, existing_files=[], batch_id=None)

    current_origs = sorted([f for f in os.listdir(batch_path) if f.startswith('orig_')])
    
    if not current_origs:
        flash('Nenhuma imagem disponível para processar.')
        return render_template('index.html', images=None, existing_files=[], batch_id=batch_id)

    processed_images = []
    
    for orig_file in current_origs:
        try:
            parts = orig_file.split('_', 2)
            idx = parts[1]
            original_filename = parts[2] if len(parts) >= 3 else orig_file
            safe_name = f"{idx}_{original_filename}"
            
            orig_path = os.path.join(batch_path, orig_file)
            comp_path = os.path.join(batch_path, f"comp_{safe_name}")
            
            orig_size_kb = get_file_size_kb(orig_path)
            
            target_kb_str = request.form.get(f'target_kb_{safe_name}', '')
            target_kb = int(target_kb_str) if target_kb_str.isdigit() else 0
            target_bytes = target_kb * 1024
            
            img = Image.open(orig_path).convert("RGBA")
            width, height = img.size
            bento_classes = calculate_bento_classes(width, height)
            
            best_data = compress_image_data(img, target_bytes)
            
            with open(comp_path, 'wb') as f:
                f.write(best_data)
            comp_size_kb = get_file_size_kb(comp_path)
            
            # Lógica de Nomenclatura Inteligente visual (UI)
            display_name = original_filename
            if re.match(r'^\d+', display_name):
                display_name = re.sub(r'^\d+(_?)', f"{round(comp_size_kb)}\\1", display_name)
            
            processed_images.append({
                'name': display_name,
                'safe_name': safe_name,
                'url': f'/static/temp/{batch_id}/comp_{safe_name}?t={os.path.getmtime(comp_path)}',
                'orig_size': orig_size_kb,
                'comp_size': comp_size_kb,
                'bento_classes': bento_classes,
                'target_kb': target_kb if target_kb > 0 else ''
            })
        except Exception as e:
            print(f"Erro em {orig_file}: {e}")

    if not processed_images:
        flash('Nenhum arquivo PNG válido foi processado.')
        return render_template('index.html', images=None, existing_files=[], batch_id=batch_id)

    existing_files = [{"safe_name": p['safe_name'], "original_filename": p['name'], "orig_size": p['orig_size'], "target_kb": p['target_kb']} for p in processed_images]

    return render_template('index.html', images=processed_images, existing_files=existing_files, batch_id=batch_id)

@app.route('/delete/<batch_id>/<safe_name>', methods=['POST'])
def delete_file(batch_id, safe_name):
    if not batch_id or not safe_name:
        return {"status": "error", "message": "Parâmetros inválidos"}, 400
        
    batch_path = os.path.join(TEMP_FOLDER, batch_id)
    orig_path = os.path.join(batch_path, f"orig_{safe_name}")
    comp_path = os.path.join(batch_path, f"comp_{safe_name}")
    try:
        if os.path.exists(orig_path): os.remove(orig_path)
        if os.path.exists(comp_path): os.remove(comp_path)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/api/ping', methods=['GET', 'OPTIONS'])
def api_ping():
    if request.method == 'OPTIONS':
        return '', 204, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, OPTIONS'}
    return {"status": "awake"}, 200, {'Access-Control-Allow-Origin': '*'}

@app.route('/api/compress', methods=['POST', 'OPTIONS'])
def api_compress():
    if request.method == 'OPTIONS':
        return '', 204, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type, multipart/form-data'}
    
    if 'image' not in request.files:
        return {"error": "Nenhuma imagem enviada."}, 400, {'Access-Control-Allow-Origin': '*'}
        
    file = request.files['image']
    target_kb = request.form.get('target_kb', type=int)
    if target_kb is None:
        target_kb = 0
    target_bytes = target_kb * 1024
    
    try:
        img = Image.open(file).convert("RGBA")
        best_data = compress_image_data(img, target_bytes)
        memory_file = io.BytesIO(best_data)
        memory_file.seek(0)
        
        response = send_file(memory_file, mimetype='image/png', as_attachment=True, download_name=file.filename)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        return {"error": str(e)}, 500, {'Access-Control-Allow-Origin': '*'}

def make_unique_filename(filename, seen_set):
    name, ext = os.path.splitext(filename)
    counter = 1
    new_name = filename
    while new_name in seen_set:
        new_name = f"{name}_{counter:02d}{ext}"
        counter += 1
    seen_set.add(new_name)
    return new_name

@app.route('/api/zip', methods=['POST', 'OPTIONS'])
def api_zip():
    if request.method == 'OPTIONS':
        return '', 204, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type, multipart/form-data'}
    
    memory_file = io.BytesIO()
    seen_names = set()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for key, file in request.files.items():
            unique_name = make_unique_filename(file.filename, seen_names)
            zf.writestr(unique_name, file.read())
            
    memory_file.seek(0)
    response = send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='EYXO_Comprimidas.zip'
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/download/<batch_id>')
def download(batch_id):
    if not batch_id:
        return "Batch ID não fornecido", 400
        
    batch_path = os.path.join(TEMP_FOLDER, batch_id)
    if not os.path.isdir(batch_path):
        return "Lote não encontrado ou expirado", 404
        
    comp_files = sorted([f for f in os.listdir(batch_path) if f.startswith('comp_')])
    
    if not comp_files:
        return "Nenhum arquivo processado encontrado", 404
        
    if len(comp_files) == 1:
        single_file = comp_files[0]
        file_path = os.path.join(batch_path, single_file)
        parts = single_file.split('_', 2)
        clean_name = parts[2] if len(parts) >= 3 else single_file
        
        # Lógica de Nomenclatura Inteligente
        size_kb = round(os.path.getsize(file_path) / 1024)
        if re.match(r'^\d+', clean_name):
            clean_name = re.sub(r'^\d+(_?)', f"{size_kb}\\1", clean_name)
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=clean_name
        )
        
    memory_file = io.BytesIO()
    zip_basename = "imagens"
    
    first_file = comp_files[0]
    parts = first_file.split('_', 2)
    clean_name = parts[2] if len(parts) >= 3 else first_file
    zip_basename = clean_name.split('_')[0]
    if not zip_basename:
        zip_basename = "imagens"
    
    final_zip_name = f"{zip_basename}_comprimido.zip"
    
    seen_names = set()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in comp_files:
            file_path = os.path.join(batch_path, filename)
            parts = filename.split('_', 2)
            clean_name = parts[2] if len(parts) >= 3 else filename
            
            # Lógica de Nomenclatura Inteligente para o ZIP
            size_kb = round(os.path.getsize(file_path) / 1024)
            if re.match(r'^\d+', clean_name):
                clean_name = re.sub(r'^\d+(_?)', f"{size_kb}\\1", clean_name)
                
            unique_name = make_unique_filename(clean_name, seen_names)
            zf.write(file_path, unique_name)
                
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=final_zip_name
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
