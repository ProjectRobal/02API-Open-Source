#!/bin/bash


function on_close() {

    python3  manage.py migrate

}

trap 'on_close' SIGTERM

python3  manage.py collectstatic --noinput

python3  manage.py makemigrations

python3  manage.py migrate

python3  manage.py createsuperuser --noinput

python3  manage.py runserver --noreload 0.0.0.0:8000