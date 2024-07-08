import os.path

import jdatetime
from billiard.exceptions import TimeLimitExceeded
from celery import shared_task, chain
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.cache import caches
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from apps.signature.exceptions import PDFGenerationFailed
from apps.signature.models import Signature
from apps.signature.utils import generate_pdf_name


signature_cache = caches['signature']


@shared_task(autoretry_for=(TimeLimitExceeded,), max_retries=2, default_retry_delay=1)
def pdf_generate(user_id):

    print('pdf_generate exception')

    signature = Signature.objects.filter(user_id=user_id).select_related('user').first()

    try:
        user_full_name = signature.user.get_full_name()
        today = jdatetime.date.today().strftime('%Y / %m / %d')

        # Generate a PDF file
        pdf_name = generate_pdf_name(signature.image.name)
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_name)
        c = canvas.Canvas(pdf_path, pagesize=letter)

        c.drawString(100, 700, user_full_name)
        c.drawString(100, 600, today)
        c.drawImage(ImageReader(signature.image.path), 100, 400, mask='auto', width=100, height=100)

        c.save()

        print('pdf_generate success')
        return {
            'signature_id': signature.id,
            'pdf_name': pdf_name,
            'pdf_path': pdf_path,
            'expected_user_full_name': user_full_name,
            'expected_today': today
        }

    except MaxRetriesExceededError as e:
        # remove from cache
        signature_cache.delete_pattern(f'{signature.user.id}')
        raise e


@shared_task()
def pdf_check(pdf_generate_results):

    print('pdf_check start')

    pdf_path = pdf_generate_results['pdf_path']
    expected_user_full_name = pdf_generate_results['expected_user_full_name']
    expected_today = pdf_generate_results['expected_today']

    pdf = PdfReader(pdf_path)

    # Number of pages
    number_of_pages = len(pdf.pages)
    if number_of_pages != 1:
        raise PDFGenerationFailed(f'Incorrect number of pages: {number_of_pages}')

    # Text of the page
    text = pdf.pages[0].extract_text()
    pdf_user_full_name, pdf_today = text.split('\n')[:2]

    # Full name
    if expected_user_full_name != pdf_user_full_name:
        raise PDFGenerationFailed(f'Incorrect full name: '
                                  f'expected_user_full_name: {expected_user_full_name} '
                                  f'pdf_user_full_name: {pdf_user_full_name}')

    # Today
    year, month, day = map(int, pdf_today.split(' / '))
    pdf_today = jdatetime.date(year, month, day).strftime('%Y / %m / %d')

    if expected_today != pdf_today:
        raise PDFGenerationFailed(f'Incorrect date today: '
                                  f'expected_today: {expected_today} pdf_today: {pdf_today}')

    # Signature image
    number_of_images = len(pdf.pages[0].images)
    if number_of_images != 1:
        raise PDFGenerationFailed(f'Signature image not inserted: #Images: {number_of_images}')

    print('pdf_check success')

    # Save pdf file to database
    signature = Signature.objects.filter(id=pdf_generate_results['signature_id']).first()
    signature.pdf = pdf_generate_results['pdf_name']
    signature.save()

    # remove from cache
    signature_cache.delete_pattern(f'{signature.user.id}')


@shared_task(bind=True)
def pdf_task_manger(self, res=None, user_id=None, retries=0):

    print('pdf_task_manger start')
    print(f'user_id {user_id}')
    print(f'retries {retries}')

    if retries > 5:
        return

    chain(pdf_generate.s(user_id),
          pdf_check.s().on_error(pdf_task_manger.s(user_id=user_id, retries=retries + 1))
          ).apply_async()

    print('pdf_task_manger success', flush=True)
