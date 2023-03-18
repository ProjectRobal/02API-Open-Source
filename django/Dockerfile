FROM --platform=$BUILDPLATFORM python:3.11.2-alpine3.17

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=80

WORKDIR /app
COPY requirements.txt /app
RUN apt update && apt upgrade -y
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app

EXPOSE 8000
ENTRYPOINT [ "python3" ]
CMD ["manage.py","runserver","0.0.0.0:8000"]
