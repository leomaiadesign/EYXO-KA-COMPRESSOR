import io, time
from PIL import Image, ImageOps

img = Image.open('static/temp/b1fb60d39b634de392f11230d6fc01cf/orig_2_200_PizzaPrime_PopUp_884x1178.png').convert("RGBA")
target_bytes = 200 * 1024

start = time.time()
best_img = None
strategies = [('posterize', 7), ('posterize', 5), ('posterize', 3), ('quantize', 256), ('quantize', 128)]

for strat_type, param in strategies:
    q_io = io.BytesIO()
    if strat_type == 'posterize':
        r, g, b, a = img.split()
        temp_img = Image.merge('RGBA', (ImageOps.posterize(r, param), ImageOps.posterize(g, param), ImageOps.posterize(b, param), ImageOps.posterize(a, param)))
    else:
        temp_img = img.quantize(colors=param, method=Image.Quantize.FASTOCTREE, dither=1)
        
    # TEST SAVE
    temp_img.save(q_io, format='PNG', compress_level=6)
    size = q_io.tell()
    best_img = temp_img
    if size <= target_bytes:
        break

# FINAL OPTIMIZED SAVE
final_io = io.BytesIO()
best_img.save(final_io, format='PNG', optimize=True)
print("Time taken:", time.time() - start, "Final size:", len(final_io.getvalue()))
