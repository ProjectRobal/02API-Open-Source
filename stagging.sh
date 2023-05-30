#!/bin/bash

cd build/stagging

cmd="help"

if [ $# -ge 1 ]
  then
    cmd=$1
fi

if [ $cmd = "build" ]; then

    docker compose build

elif [ $cmd = "rebuild" ]; then

    docker compose rm -f -s -v
    rm -R  sql/data
    rm -R mqtt/data
    docker compose build

elif [ $cmd = "up" ]; then

    docker compose up

elif [ $cmd = "down" ]; then

    docker compose down

elif [ $cmd = "start" ]; then

    docker compose start

elif [ $cmd = "stop" ]; then

    docker compose stop

elif [ $cmd = "run" ]; then

    docker compose build
    docker compose up

elif [ $cmd = "purge" ]; then

    docker compose rm -f -s -v
    rm -R  sql/data
    rm -R mqtt/data

elif [ $cmd = "debug" ]; then

    docker compose run -i web bash

elif [ $cmd = "init_root" ]; then

    docker compose run -T web python manage.py createsuperuser --noinput

elif [ $cmd = "migrate" ]; then

    docker compose run -T web python manage.py makemigrations --noinput
    docker compose run -T web python manage.py migrate --noinput

elif [ $cmd = "init_mqtt" ]; then

    docker-compose run -T mqtt mosquitto_passwd -U /mosquitto/config/password.txt

elif [ $cmd = "help" ]; then

echo "build - zbuduj kontenery"
echo "rebuild - purge + build"
echo "up - uruchom i utwórz kontenery"
echo "down - zatrzymaj i usuń kontenery"
echo "start - uruchom kontenery"
echo "stop - zatrzymaj kontenery"
echo "run - zbuduj i uruchom kontenery"
echo "purge - usuń kontenery wraz z ich danymi"
echo "debug - uruchom terminal bash na kontenerze django"
echo "migrate - uruchom migracje na django"
echo "init_root - utwórz użytkownika roota w django"
echo "init_mqtt - ustaw użytkownika dla serwera mqtt"
echo "help - komenda pomoc"

fi
