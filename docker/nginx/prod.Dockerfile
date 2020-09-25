FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/nginx/nginx.prod.conf /etc/nginx/conf.d/nginx.conf
COPY ./docker/nginx/dhparam.pem /etc/ssl/dhparam.pem
