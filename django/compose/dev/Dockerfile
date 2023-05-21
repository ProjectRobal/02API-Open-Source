FROM --platform=$BUILDPLATFORM python:3.11.2-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app
COPY requirements.txt /app
COPY ./compose/dev/entrypoint.sh /app/entrypoint.sh

RUN apt-get update && apt-get upgrade -y
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./src /app

EXPOSE 8000
RUN chmod +x /app/entrypoint.sh
CMD ["./entrypoint.sh"]
