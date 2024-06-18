from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

img = Image.open("pictures\\template.jpg")
draw = ImageDraw.Draw(img)

font = ImageFont.truetype("Roboto-Bold.ttf", 25)

draw.text((100, 115), "947353888", (0, 0, 0), font=font)
img.show()
