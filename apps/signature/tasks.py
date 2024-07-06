import os.path
import time

import jdatetime
from billiard.exceptions import TimeLimitExceeded
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.cache import caches
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from apps.signature.models import Signature
from apps.signature.utils import generate_pdf_path


signature_cache = caches['signature']


@shared_task(time_limit=5, autoretry_for=(TimeLimitExceeded,), max_retries=3)
def generate_pdf(user_id):

    signature = Signature.objects.filter(user_id=user_id).select_related('user').first()

    try:

        # time.sleep(10)

        # Generate a PDF file
        pdf_path = generate_pdf_path(signature.image.name)
        c = canvas.Canvas(os.path.join(settings.MEDIA_ROOT, pdf_path), pagesize=letter)

        c.drawString(100, 700, signature.user.get_full_name())
        c.drawString(100, 600, jdatetime.date.today().strftime('%Y / %m / %d'))
        c.drawImage(ImageReader(signature.image.path), 100, 400, mask='auto', width=100, height=100)

        c.save()

        # Save pdf file to database
        signature.pdf = pdf_path
        signature.save()

        # remove from cache
        signature_cache.delete_pattern(f'{signature.user.id}')

    except MaxRetriesExceededError as e:
        # remove from cache
        signature_cache.delete_pattern(f'{signature.user.id}')
        raise e
