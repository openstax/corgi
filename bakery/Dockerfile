FROM python:3.7-stretch

LABEL maintainer="OpenStax Content Engineering"

COPY ./src/scripts /code/scripts
COPY ./requirements.txt /code
WORKDIR /code/

RUN pip install -r requirements.txt
