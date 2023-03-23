#!/bin/bash

if [ "$1" = "build" ]; then

    docker compose build

elif [ "$1" = "up" ]; then

    docker compose up

elif [ "$1" = "down" ]; then

    docker compose down

elif [ "$1" = "start "]; then

    docker compose start

elif [ "$1" = "stop "]; then

    docker compose stop

elif [ "$1" = "run" ]; then

    docker compose build
    docker compose up

elif [ "$1" = "purge" ]; then

    docker compose rm -f -s -v
    rm -R  sql/data
    rm -R mqtt/data

elif [ "$1" = "debug" ]; then

    docker compose run -i web bash

elif [ "$1" = "init_root" ]; then

    docker compose run -T web python manage.py createsuperuser --noinput

fi
