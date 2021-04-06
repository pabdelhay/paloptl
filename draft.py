# pull official base image
FROM python:3.8.3-alpine
#FROM ubuntu:18.04

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip

# Pillow
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install Pillow

# Postgres
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# python3 -m pip install -r requirements.txt --no-cache-dir && \
RUN apk --purge del .build-deps

COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# copy project
COPY . .