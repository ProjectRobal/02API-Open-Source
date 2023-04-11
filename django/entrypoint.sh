#!/bin/sh

python3 -u manage.py makemigrations

python3 -u manage.py migrate

python3 -u manage.py runserver 0.0.0.0:8000
