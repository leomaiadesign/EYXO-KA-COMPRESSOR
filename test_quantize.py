import io
from PIL import Image
# Create a dummy RGBA image with gradient
img = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
try:
    print("Testing FASTOCTREE...")
    q1 = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=0)
    print("FASTOCTREE success")
    
    print("Testing MEDIANCUT with dither=1...")
    q2 = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=1)
    print("MEDIANCUT success")
except Exception as e:
    print("ERROR:", type(e), e)
