FROM python:3.11.2-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt /app
COPY packages.txt /app

RUN apt-get update
RUN xargs -a packages.txt apt install -y
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./compose/prod/entrypoint.sh /app/entrypoint.sh
COPY ./src /app

EXPOSE 8000
RUN chmod +x /app/entrypoint.sh

RUN python3 manage.py tailwind install

ENTRYPOINT ["./entrypoint.sh"]
