import io, os
from PIL import Image, ImageOps

img = Image.new('RGBA', (800, 800), (255, 0, 0, 128))
# Let's add some noise/gradient to make it compressible but not trivial
for x in range(800):
    for y in range(800):
        img.putpixel((x, y), (x % 256, y % 256, (x+y) % 256, 255))

orig_io = io.BytesIO()
img.save(orig_io, format='PNG', optimize=True)
print("Original size:", len(orig_io.getvalue()) // 1024, "KB")

# Quantize 256
q_io = io.BytesIO()
img.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(q_io, format='PNG', optimize=True)
print("Quantized 256 size:", len(q_io.getvalue()) // 1024, "KB")

# Posterize 7, 6, 5, 4 bits
for bits in [7, 6, 5, 4, 3]:
    r, g, b, a = img.split()
    r = ImageOps.posterize(r, bits)
    g = ImageOps.posterize(g, bits)
    b = ImageOps.posterize(b, bits)
    # optionally posterize alpha
    p_img = Image.merge('RGBA', (r, g, b, a))
    
    p_io = io.BytesIO()
    p_img.save(p_io, format='PNG', optimize=True)
    print(f"Posterized {bits} bits size:", len(p_io.getvalue()) // 1024, "KB")

