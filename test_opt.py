import io, time
from PIL import Image, ImageOps

img = Image.open('static/temp/b1fb60d39b634de392f11230d6fc01cf/orig_2_200_PizzaPrime_PopUp_884x1178.png').convert("RGBA")

# Test with optimize=True
start = time.time()
q_io = io.BytesIO()
img.save(q_io, format='PNG', optimize=True)
print("True:", time.time() - start, len(q_io.getvalue()))

# Test with compress_level=1
start = time.time()
q_io = io.BytesIO()
img.save(q_io, format='PNG', compress_level=1)
print("Level 1:", time.time() - start, len(q_io.getvalue()))

# Test with default (compress_level=6)
start = time.time()
q_io = io.BytesIO()
img.save(q_io, format='PNG')
print("Default:", time.time() - start, len(q_io.getvalue()))
