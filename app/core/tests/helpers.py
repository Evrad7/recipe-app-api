from io import BytesIO
from PIL import Image
from django.core.files.images import ImageFile


def get_image_file():
    buffer = BytesIO()
    image = Image.new("RGB", (10, 10), color="green")
    image.save(buffer, format="PNG")
    image.seek(0)
    image_field = ImageFile(buffer, "test.png")
    return image_field
