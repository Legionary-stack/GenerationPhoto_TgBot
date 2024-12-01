from io import BytesIO

from PIL import Image, ImageDraw
import numpy as np


def halftone_effect(input_image_path, max_square_size=10):
    image = Image.open(input_image_path).convert('L')
    width, height = image.size
    pixels = np.array(image)

    halftone_image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(halftone_image)

    for y in range(0, height, max_square_size):
        for x in range(0, width, max_square_size):
            block = pixels[y:y + max_square_size, x:x + max_square_size]
            average_brightness = np.mean(block)

            square_size = int((1 - average_brightness / 255) * max_square_size)

            top_left_x = x + (max_square_size - square_size) // 2
            top_left_y = y + (max_square_size - square_size) // 2

            draw.rectangle(
                [top_left_x, top_left_y, top_left_x + square_size, top_left_y + square_size],
                fill='black'
            )

    output = BytesIO()
    halftone_image.save(output, format="JPEG")
    output.seek(0)
    return output
