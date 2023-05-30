FROM nginx

RUN mkdir /usr/share/static
RUN mkdir /usr/share/media

COPY ./nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
ENTRYPOINT [ "" ]
CMD ["nginx", "-g", "daemon off;"]