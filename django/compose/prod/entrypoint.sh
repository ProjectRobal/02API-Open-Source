#!/bin/sh

python3 -u manage.py collectstatic --noinput

python3 -u manage.py runserver --noreload 0.0.0.0:8000