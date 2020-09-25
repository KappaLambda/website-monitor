#!/bin/bash

if [ $HOSTNAME == "vagrant" ]
then
    echo "Django to developemnt settings"
    export DJANGO_SETTINGS_MODULE="website_monitor.settings.dev"
    export GUNICORN_CMD_ARGS="--reload"
else
    echo "Django to production settings"
fi

$(pyenv which gunicorn) \
    --timeout 90 \
    --workers 3 \
    --chdir $(git rev-parse --show-toplevel)/website_monitor/ \
    --bind unix:/tmp/website-monitor.sock \
    website_monitor.wsgi:application
