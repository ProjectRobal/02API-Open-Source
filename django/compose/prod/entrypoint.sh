#!/bin/bash

echo "Collecing static files"
python3  manage.py collectstatic --noinput

python3  manage.py makemigrations auth02

echo "Database migration"
python3 manage.py migrate

echo "Run server"
python3  manage.py runserver --noreload 0.0.0.0:8000