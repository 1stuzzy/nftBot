from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


async def get_photo(user_id):
    img = Image.open("pictures\\template.jpg")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("Roboto-Bold.ttf", 25)

    draw.text((100, 115), str(user_id), (0, 0, 0), font=font)
    img.save(f"pictures\\{user_id}.jpg")
