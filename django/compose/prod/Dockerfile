FROM python:3.11.2-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt /app
RUN apt-get update && apt-get upgrade -y
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./compose/prod/entrypoint.sh /app/entrypoint.sh
COPY ./src /app

EXPOSE 8000
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
