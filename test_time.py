import io, time
from PIL import Image, ImageOps

img = Image.open('static/temp/b1fb60d39b634de392f11230d6fc01cf/orig_2_200_PizzaPrime_PopUp_884x1178.png').convert("RGBA")
target_bytes = 200 * 1024

start = time.time()
best_data = None
strategies = [
    ('posterize', 7),
    ('posterize', 6),
    ('posterize', 5),
    ('posterize', 4),
    ('posterize', 3),
    ('quantize', 256),
    ('quantize', 128)
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
        temp_img = img.quantize(colors=param, method=Image.Quantize.FASTOCTREE, dither=0)
        
    temp_img.save(q_io, format='PNG', optimize=True)
    size = q_io.tell()
    print(f"Tested {strat_type} {param}: {size // 1024} KB")
    if size <= target_bytes:
        best_data = q_io.getvalue()
        break

print("Time taken:", time.time() - start)
