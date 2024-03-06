FROM  python:3.11.2-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /pack

COPY requirements.txt /pack
COPY packages.txt /pack

RUN curl -sL https://deb.nodesource.com/setup_18.x |  bash -
RUN apt update
RUN xargs -a packages.txt apt install -y
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./compose/dev/entrypoint.sh /pack/entrypoint.sh
COPY ./compose/dev/entry_tailwind.sh /pack/entry_tailwind.sh

COPY ./debug /app

EXPOSE 8000
RUN chmod +x /pack/entrypoint.sh
RUN chmod +x /pack/entry_tailwind.sh

WORKDIR /app

CMD ["/pack/entrypoint.sh"]