import io
from PIL import Image
img = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
try:
    print("Testing FASTOCTREE with dither=1...")
    q2 = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=1)
    print("FASTOCTREE dither=1 success")
except Exception as e:
    print("ERROR:", type(e), e)
    
try:
    print("Testing LIBIMAGEQUANT with dither=1...")
    q3 = img.quantize(colors=256, method=Image.Quantize.LIBIMAGEQUANT, dither=1)
    print("LIBIMAGEQUANT dither=1 success")
except Exception as e:
    print("ERROR:", type(e), e)
