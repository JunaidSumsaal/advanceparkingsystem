FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /app/


RUN adduser --disabled-password --gecos '' appuser \
&& chown -R appuser /app
USER appuser

# Migrations daone to postgress sql already
# RUN python manage.py makemigrations &&\
# python manage.py migrate

# RUN python manage.py seed

RUN python manage.py collectstatic --no-input

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=core.settings

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=4", "--threads=2", "--timeout=120"]