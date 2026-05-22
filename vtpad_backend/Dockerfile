
# pull the official docker image
FROM python:3.13-slim

# set work directory
WORKDIR /app

# install system dependencies for packages with native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./.env /.env

# install dependencies
COPY ./requirements.txt /requirements.txt
RUN mkdir "uploads"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./app /app

