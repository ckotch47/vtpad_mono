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
ENV npm_config_audit=false
ENV npm_config_fund=false
ENV npm_config_fetch_timeout=600000
ENV npm_config_fetch_retries=5
ENV npm_config_fetch_retry_mintimeout=20000
ENV npm_config_fetch_retry_maxtimeout=120000

# install and cache app dependencies
COPY package.json /src/package.json
COPY package-lock.json /src/package-lock.json
RUN set -eux; \
    for attempt in 1 2 3; do \
      npm ci --prefer-offline --no-audit --no-fund --no-progress && break; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      echo "npm ci failed, retrying in 10s (attempt $attempt/3)"; \
      sleep 10; \
    done

COPY ./.env /src/.env
COPY ./ /src

RUN npm i -g serve
RUN npm run build
