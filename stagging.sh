#!/bin/bash

mkdir -p django/web/media
mkdir -p build/stagging/sql_buckups/daily
mkdir -p build/stagging/sql_buckups/weekly
mkdir -p build/stagging/sql_buckups/monthly
mkdir -p build/stagging/conf1/mqtt/log/

cd build/stagging

cmd="help"

if [ $# -ge 1 ]
  then
    cmd=$1
fi

if [ $cmd = "build" ]; then

    docker compose -f compose.yml build

elif [ $cmd = "rebuild" ]; then

    docker compose -f compose.yml rm -f -s -v
    rm -R  sql/data
    rm -R mqtt/data
    docker compose -f compose.yml build

elif [ $cmd = "up" ]; then

    docker compose -f compose.yml up -d

elif [ $cmd = "down" ]; then

    docker compose -f compose.yml down

elif [ $cmd = "start" ]; then

    docker compose -f compose.yml start

elif [ $cmd = "stop" ]; then

    docker compose -f compose.yml stop

elif [ $cmd = "run" ]; then

    docker compose -f compose.yml cp ../../django/src/. web:/app
    docker compose -f compose.yml  up -d

elif [ $cmd = "purge" ]; then

    docker compose -f compose.yml rm  -s -v
    rm -R  sql/data
    rm -R mqtt/data

elif [ $cmd = "debug" ]; then

    docker compose -f compose.yml exec -i web bash

elif [ $cmd = "logs" ]; then

    docker compose -f compose.yml logs

elif [ $cmd = "init_root" ]; then

    docker compose -f compose.yml exec  web python3 manage.py createsuperuser --noinput

elif [ $cmd = "migrate" ]; then

    docker compose -f compose.yml exec -T web python3 manage.py makemigrations --noinput
    docker compose -f compose.yml exec -T web python3 manage.py migrate --noinput

elif [ $cmd = "init_mqtt" ]; then

    docker compose -f compose.yml exec -T mqtt mosquitto_passwd -U /mosquitto/config/password.txt

elif [ $cmd = "restore" ]; then

    docker compose -f compose.yml exec -T db pg_restore -v --if-exists -c -U prod -d domena_db /backup/$2/db

elif [ $cmd = "restore_copy" ]; then

    docker compose exec -T db pg_restore -v --if-exists -c -U prod -d domena_db /backup/$2

elif [ $cmd = "copy_db" ]; then

    docker compose exec -T db pg_dump -Fc -U prod -Z 9 -f /backup/$2 domena_db

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
echo "migrate - przeprowadzi migrację"
echo "init_root - utwórz użytkownika roota w django"
echo "init_mqtt - ustaw użytkownika dla serwera mqtt"
echo "restore - załaduj buckup bazy danych, do wyboru: "
echo "  -daily - codzienny"
echo "  -weekly - tygodniowy"
echo "  -monthly - miesieczny"
echo "restore_copy - załaduj kopię bazy danych z folderu buckup"
echo "copy_db - stwórz kopię bazy danych do folderu buckup"
echo "help - komenda pomoc"

fi
