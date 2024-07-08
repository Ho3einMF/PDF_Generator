import hashlib
import os

from django.conf import settings
from django.utils.crypto import get_random_string
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def calculate_image_checksum(image):
    image.seek(0)
    return hashlib.sha256(image.read()).hexdigest()


def signature_upload_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return f'{get_random_string(length=16)}{extension}'


def generate_pdf_name(signature_image_name):
    basename = os.path.splitext(signature_image_name)[0]
    return f'{basename}.pdf'


def generate_pdf_file(pdf_path, user_full_name, today, signature_image_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)

    c.drawString(100, 700, user_full_name)
    c.drawString(100, 600, today)
    c.drawImage(ImageReader(signature_image_path), 100, 400, mask='auto', width=100, height=100)

    c.save()
