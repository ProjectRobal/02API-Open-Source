#!/bin/bash

export IP_ADDR="$(./get_ip.sh)"

echo Current IP Addr $IP_ADDR

cd build/dev

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

    docker compose exec -i web bash

elif [ $cmd = "remigrate" ]; then

    #docker compose exec -i db pg_dump --data-only -Fc  -U devs -Z 9 -f /backup/db domena_db

    docker compose exec -i web ./remigrate.sh

    #docker compose exec -T db pg_restore -v -U devs -d domena_db /backup/db

    #docker compose exec -T db rm /backup/db

elif [ $cmd = "makemigration" ]; then

    docker compose exec -i web python3 -u manage.py makemigrations -v 3

elif [ $cmd = "migrate" ]; then
    
    docker compose exec -i web python3 -u manage.py migrate -v 3

elif [ $cmd = "init_root" ]; then

    docker compose exec -T web python manage.py createsuperuser --noinput

elif [ $cmd = "init_mqtt" ]; then

    docker compose run -T mqtt mosquitto_passwd -U /mosquitto/config/password.txt

elif [ $cmd = "restore" ]; then

    docker compose exec -T db pg_restore -v --if-exists -c -U devs -d domena_db /backup/$2/db

elif [ $cmd = "restore_copy" ]; then

    docker compose exec -T db pg_restore -v --if-exists -c -U devs -d domena_db /backup/$2

elif [ $cmd = "copy_db" ]; then

    docker compose exec -T db pg_dump -Fc -U devs -Z 9 -f /backup/$2 domena_db

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
echo "init_root - utwórz użytkownika roota w django"
echo "init_mqtt - ustaw użytkownika dla serwera mqtt"
echo "remigrate - ponów migracje"
echo "restore - załaduj buckup bazy danych, do wyboru: "
echo "  -daily - codzienny"
echo "  -weekly - tygodniowy"
echo "  -monthly - miesieczny"
echo "restore_copy - załaduj kopię bazy danych z folderu buckup"
echo "copy_db - stwórz kopię bazy danych do folderu buckup"
echo "help - komenda pomoc"

fi
