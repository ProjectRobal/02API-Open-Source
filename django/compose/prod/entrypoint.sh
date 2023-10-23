#!/bin/sh

if [$1 == "migrate"]
then;

python3 -u manage.py makemigrations

python3 -u manage.py migrate

else

python3 -u manage.py collectstatic --noinput

python3 -u manage.py runserver --noreload 0.0.0.0:8000

fi