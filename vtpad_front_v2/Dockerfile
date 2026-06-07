# base image
FROM node:20.20.0-slim

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
ENV npm_config_network_concurrency=1
ENV npm_config_maxsockets=1

# install and cache app dependencies
COPY package.json /src/package.json
COPY package-lock.json /src/package-lock.json
RUN set -eux; \
    mkdir -p /src/node_modules/.cache; \
    for attempt in 1 2 3; do \
      npm ci --prefer-offline --no-audit --no-fund --no-progress --foreground-scripts && break; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      echo "npm ci failed, retrying in 10s (attempt $attempt/3)"; \
      sleep 10; \
    done

COPY ./.env /src/.env
COPY ./ /src

RUN npm i -g serve
RUN npm run build
