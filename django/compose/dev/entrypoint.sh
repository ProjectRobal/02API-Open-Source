#!/bin/sh

python3 -u manage.py makemigrations

python3 -u manage.py migrate

python3 -u manage.py createsuperuser --noinput

python3 -u manage.py runserver --noreload 0.0.0.0:8000