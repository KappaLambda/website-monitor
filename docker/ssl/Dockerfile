# pull official base image
FROM python:3.6

# set work directory
WORKDIR /usr/src/certs

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && git clone https://github.com/lukas2511/dehydrated \
    && cd dehydrated \
    && mkdir hooks \
    && git clone https://github.com/kappataumu/letsencrypt-cloudflare-hook hooks/cloudflare \
    && pip install --upgrade pip \
    && pip install -r hooks/cloudflare/requirements.txt

WORKDIR /usr/src/certs/dehydrated

COPY ./docker/ssl/config /usr/src/certs/dehydrated/config
COPY ./docker/ssl/domains.txt /usr/src/certs/dehydrated/domains.txt
