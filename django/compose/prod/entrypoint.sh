#!/bin/bash

apt update -y

xargs -a /app/packages.txt apt install -y

pip3 install -r /app/requirements.txt --no-cache-dir

echo "Collecing static files"
python3  manage.py collectstatic --noinput

python3  manage.py makemigrations auth02

echo "Database migration"
python3 manage.py migrate

echo "Run server"
python3  manage.py runserver --noreload 0.0.0.0:8000