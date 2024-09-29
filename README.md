# Serwer projektu SmartKon/02

## Opis:
 Jest to warstwa sieciowa projektu 02 Koła Naukowego Robotyków KoNaR, którego byłem kordynatorem. Z powodu zmianny kierunku i założeni projektu oraz utraty motywacji zrzekłem się tego stanowiska. To co udało mi się napisać w ramach tego projektu udostępniam wiec jako open source. Ktokolwiek to czyta może z tym projektem zrobić to co mu się żwynie podoba. 

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

skrypt.sh up

## Plik konfiguracyjny

Przykładowy pliki konfiguracyjny znajdują się w folderze build/dev/conf znajduję się tam:
- django.env - plik z konfiguracją głównego serwera django
- sql.env - plik z konfiguracją serwera SQL
- tasks.ini - konfiguracja tasków dla ofeli kontenera wykonującego taski CRON
- mqtt - folder z konfiguracją eclipse-mosquitto

Pilki należy skopiować i wsadzić do folderów /build/prod lub /build/stagging i wprowadzić tam swoje konfigurację.
Konfigurację te są zmienneymi konfiguracyjnymi ich znaczenie można znaleźć w dokumentacji kontenerów oraz w pliku settings.py od kontenera z django.

## Zastosowane obrazy:
- mqtt https://hub.docker.com/_/eclipse-mosquitto
- sql https://hub.docker.com/_/mysql
- ofelia https://hub.docker.com/r/mcuadros/ofelia

## Dokumenty:

- [Ogólny opis projektu 02](https://github.com/user-attachments/files/17180067/opis.pdf)
- [Dokumentacja 02API](https://github.com/user-attachments/files/17180071/02Api.pdf)
- [Twarde założenia projektu które udało bądzi nie udało mi się zaimplementować](https://github.com/user-attachments/files/17180074/manifest.pdf)
