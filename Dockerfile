FROM python:slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SUPERUSER_PASSWORD admin

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev python3-dev

COPY . /app

RUN pip install -r requirements.txt

RUN python manage.py collectstatic

RUN python manage.py makemigrations --noinput && python manage.py migrate --noinput

RUN python manage.py createsuperuser --user admin --email test@tets.com --noinput

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
