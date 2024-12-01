from functools import lru_cache
from io import BytesIO

from PIL import Image
import random


@lru_cache(maxsize=1000)
def is_difference_within_tolerance(tuple1, tuple2, tolerance=52):
    return all(abs(a - b) <= tolerance for a, b in zip(tuple1, tuple2))


def replace_colors(input_image_path, colors, num_squares=52):
    image = Image.open(input_image_path).convert('RGB')
    width, height = image.size
    print(num_squares, width, height)
    pixels = image.load()
    pixel_size = int(min(width / num_squares, height / num_squares)) + 1
    unique_colors = set()

    for y in range(height):
        for x in range(width):
            unique_colors.add(pixels[x, y])

    color_map = {color: random.choice(colors) for color in unique_colors}
    print(len(color_map))

    processed_colors = set()

    for temp_color in unique_colors:
        if temp_color in processed_colors:
            continue
        replacement = color_map[temp_color]
        for color in unique_colors:
            if color not in processed_colors and is_difference_within_tolerance(temp_color, color):
                color_map[color] = replacement
                processed_colors.add(color)

    for y in range(height):
        for x in range(width):
            pixels[x, y] = color_map[pixels[x, y]]

    image = image.resize(
        (width // pixel_size, height // pixel_size),
        resample=Image.NEAREST
    )

    image = image.resize(
        (width, height),
        resample=Image.NEAREST
    )

    output = BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)
    return output
