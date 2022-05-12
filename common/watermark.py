from PIL import Image, ImageDraw, ImageFont
from turtle import position


def add_water_mark(path, text_to_add):
    image = Image.open(path)
    watermark_image = image.copy()

    draw = ImageDraw.Draw(watermark_image)

    # choose a font and size
    font = ImageFont.truetype("arial.ttf", 50)

    # add water mark
    position(0, 0)
    color = (0, 0, 0)

    draw.text(position, text_to_add, color, font=font)

    return watermark_image
