FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app/

RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser /app
USER appuser

RUN python manage.py makemigrations &&\
python manage.py migrate

RUN python manage.py seed

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=4", "--threads=2", "--timeout=120"]