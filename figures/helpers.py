import io
from PIL import Image

def figure_to_image(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    return img

def combine_images_vertical(images):
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    image = Image.new('RGB', (max_width, total_height))
    y_offset = 0

    for im in images:
        width, height = im.size
        image.paste(im, (0, y_offset))
        y_offset += height

    return image

