#!/bin/bash

python3 manage.py tailwind install --no-input

python3 manage.py tailwind build --no-input

python3 manage.py tailwind start --no-input