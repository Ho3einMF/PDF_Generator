import jdatetime

from apps.signature.exceptions import PDFGenerationFailed


def check_numbers_of_pdf_pages(expected_page_number, pdf_page_number):
    if expected_page_number != pdf_page_number:
        raise PDFGenerationFailed(f'Incorrect number of pages: '
                                  f'expected_page_number {expected_page_number} '
                                  f'pdf_page_number: {pdf_page_number}')


def check_pdf_user_full_name(expected_user_full_name, pdf_user_full_name):
    if expected_user_full_name != pdf_user_full_name:
        raise PDFGenerationFailed(f'Incorrect full name: '
                                  f'expected_user_full_name: {expected_user_full_name} '
                                  f'pdf_user_full_name: {pdf_user_full_name}')


def check_pdf_today_date(expected_today_date, pdf_today_date):
    year, month, day = map(int, pdf_today_date.split(' / '))
    pdf_today_date = jdatetime.date(year, month, day).strftime('%Y / %m / %d')

    if expected_today_date != pdf_today_date:
        raise PDFGenerationFailed(f'Incorrect date today: '
                                  f'expected_today_date: {expected_today_date} pdf_today_date: {pdf_today_date}')


def check_numbers_of_pdf_images(expected_image_number, pdf_image_number):
    if expected_image_number != pdf_image_number:
        raise PDFGenerationFailed(f'Signature image not inserted: '
                                  f'expected_image_number: {expected_image_number} '
                                  f'pdf_image_number : {pdf_image_number}')
