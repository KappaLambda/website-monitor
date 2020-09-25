FROM node:lts

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global

COPY ./package*.json ./
RUN npm install

COPY . .
