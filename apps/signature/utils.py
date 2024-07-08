import hashlib
import os

from django.utils.crypto import get_random_string


def calculate_image_checksum(image):
    image.seek(0)
    return hashlib.sha256(image.read()).hexdigest()


def signature_upload_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return f'{get_random_string(length=16)}{extension}'


def generate_pdf_name(signature_image_name):
    basename = os.path.splitext(signature_image_name)[0]
    return f'{basename}.pdf'
