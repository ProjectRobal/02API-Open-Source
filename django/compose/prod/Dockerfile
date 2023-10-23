FROM python:3.11.2-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app
COPY requirements.txt /app
COPY ./compose/prod/entrypoint.sh /app/entrypoint.
COPY ./compsoe/prod/migrate.sh /app/migrate.sh

RUN apt-get update && apt-get upgrade -y
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./src /app

EXPOSE 8000
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/migrate.sh
ENTRYPOINT ["./entrypoint.sh"]
