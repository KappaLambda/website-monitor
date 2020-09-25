#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $WEBSITE_MONITOR_DB_HOST $WEBSITE_MONITOR_DB_PORT; do
      sleep 0.1
      echo "Still waiting..."
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"
