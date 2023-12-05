#!/bin/bash

apt update -y

xargs -a /app/packages.txt apt install -y

pip3 install -r /app/requirements.txt --no-cache-dir


function on_close() {

    python3  manage.py migrate

}

trap 'on_close' SIGTERM

python3  manage.py collectstatic --noinput

python3  manage.py makemigrations

python3  manage.py migrate

python3  manage.py createsuperuser --noinput

python3  manage.py runserver --noreload 0.0.0.0:8000