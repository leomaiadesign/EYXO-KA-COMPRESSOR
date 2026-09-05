import os
import io
import zipfile
import shutil
import uuid
import time
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
            
            img_io = io.BytesIO()
            img.save(img_io, format='PNG', optimize=True)
            best_data = img_io.getvalue()
            
            if target_bytes > 0 and len(best_data) > target_bytes:
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
                
                for strat_type, param in strategies:
                    q_io = io.BytesIO()
                    if strat_type == 'posterize':
                        r, g, b, a = img.split()
                        r = ImageOps.posterize(r, param)
                        g = ImageOps.posterize(g, param)
                        b = ImageOps.posterize(b, param)
                        a = ImageOps.posterize(a, param)
                        temp_img = Image.merge('RGBA', (r, g, b, a))
                    else:
                        # Fallback seguro: usa FASTOCTREE com dither=1 (Suaviza sombras)
                        temp_img = img.quantize(colors=param, method=Image.Quantize.FASTOCTREE, dither=1)
                            
                    temp_img.save(q_io, format='PNG', optimize=True)
                    if q_io.tell() <= target_bytes:
                        best_data = q_io.getvalue()
                        break
                    best_data = q_io.getvalue()
            
            with open(comp_path, 'wb') as f:
                f.write(best_data)
            comp_size_kb = get_file_size_kb(comp_path)
            
            processed_images.append({
                'name': original_filename,
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
    
    final_zip_name = f"{zip_basename}_comprimido.zip"
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in comp_files:
            file_path = os.path.join(batch_path, filename)
            parts = filename.split('_', 2)
            clean_name = parts[2] if len(parts) >= 3 else filename
            zf.write(file_path, clean_name)
                
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=final_zip_name
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
