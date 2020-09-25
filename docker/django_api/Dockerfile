# pull official base image
FROM python:3.7

# set work directory
WORKDIR /

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies and netcat
RUN apt-get update \
    && apt-get install -y libpq-dev python3-dev netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./docker/django_api/entrypoint.sh ./entrypoint.sh

# create logs folder
RUN mkdir logs/

# set work directory
WORKDIR /app

# copy backend folder
COPY ./website_monitor/ ./

# run entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
