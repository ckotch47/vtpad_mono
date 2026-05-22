
# pull the official docker image
FROM python:3.10

# set work directory
#WORKDIR /app
COPY ./.env /.env

# install dependencies
COPY ./requirements.txt /requirements.txt
RUN mkdir "uploads"
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./app /app

