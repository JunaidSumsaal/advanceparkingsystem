FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    proj-bin \
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

ENV DJANGO_SETTINGS_MODULE=core.settings

EXPOSE $PORT

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers=4", "--threads=2", "--timeout=120"]
