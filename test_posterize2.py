import io, os
from PIL import Image, ImageOps

img = Image.open('static/temp/b1fb60d39b634de392f11230d6fc01cf/orig_2_200_PizzaPrime_PopUp_884x1178.png').convert("RGBA")

orig_io = io.BytesIO()
img.save(orig_io, format='PNG', optimize=True)
print("Original size:", len(orig_io.getvalue()) // 1024, "KB")

q_io = io.BytesIO()
img.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=0).save(q_io, format='PNG', optimize=True)
print("Quantized 256 size:", len(q_io.getvalue()) // 1024, "KB")

for bits in [7, 6, 5, 4, 3]:
    r, g, b, a = img.split()
    r = ImageOps.posterize(r, bits)
    g = ImageOps.posterize(g, bits)
    b = ImageOps.posterize(b, bits)
    # optionally posterize alpha
    a = ImageOps.posterize(a, bits)
    p_img = Image.merge('RGBA', (r, g, b, a))
    
    p_io = io.BytesIO()
    p_img.save(p_io, format='PNG', optimize=True)
    print(f"Posterized {bits} bits size:", len(p_io.getvalue()) // 1024, "KB")

