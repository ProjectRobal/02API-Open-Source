# Serwer projektu SmartKon/02

## Struktura projektu:
- django - folder z obrazem serwera django
- mqtt - konfiguracja serwera mqtt eclipse-mosquitto
- sql - konfiguracja/buckup serwera bazy danych mysql

## Uruchamianie:

Przygotowane są trzy skrypty:
- dev.sh - wersja developerska
- stagging.sh - wersja stagging
- prod.sh - wersja produkcyjna

Każdy skrypt posiada następujące polecenia:

- build - zbuduj kontenery
- rebuild - purge + build
- up - uruchom i utwórz kontenery
- down - zatrzymaj i usuń kontenery
- start - uruchom kontenery
- stop - zatrzymaj kontenery
- run - zbuduj i uruchom kontenery
- purge - usuń kontenery wraz z ich danymi
- debug - uruchom terminal bash na kontenerze django
- init_root - utwórz użytkownika roota w django
- init_mqtt - ustaw użytkownika dla serwera mqtt
- help - komenda pomoc

By uruchomić serwer wybieramy nasz skrypt i używamy polecenia up:

skrypt.sh run

## Zastosowane obrazy:
- mqtt https://hub.docker.com/_/eclipse-mosquitto
- sql https://hub.docker.com/_/mysql
