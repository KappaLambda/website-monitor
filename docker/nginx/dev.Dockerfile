FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/nginx/nginx.dev.conf /etc/nginx/conf.d/nginx.conf
