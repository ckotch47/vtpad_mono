# base image
FROM node:20.20.0

RUN mkdir /src && chown node:node /src
RUN mkdir /src/node_modules/ && chmod -R 777 /src/node_modules/
RUN mkdir /src/node_modules/.cache && chmod -R 777 /src/node_modules/.cache
RUN chown node:node /src/node_modules/
RUN chown node:node /src/node_modules/.cache
# set working directory
WORKDIR /src

# add `/app/node_modules/.bin` to $PATH
ENV PATH /src/node_modules/.bin:$PATH

COPY ./ /src
COPY ./.env /src/.env
# install and cache app dependencies
COPY package.json /src/package.json
COPY package-lock.json /src/package-lock.json

RUN npm ci
RUN npm i -g serve
RUN npm run build

