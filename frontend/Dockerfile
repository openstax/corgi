FROM node:18-alpine as node_modules

WORKDIR /deps

COPY package*.json ./

RUN set -ex && \
    npm install


# ---
FROM node:18-alpine as builder

WORKDIR /build

COPY rollup.config.js package.json tsconfig.json ./
COPY src src
COPY public public
COPY --from=node_modules /deps/node_modules ./node_modules

RUN set -ex && \
    npm run build && \
    rm -rf node_modules


# ---
FROM nginx:1.19

WORKDIR /app

ARG API_URL=http://backend
ARG API_URL_BROWSER=/
ENV API_URL=${API_URL}
ENV API_URL_BROWSER=${API_URL_BROWSER}

COPY --from=builder /build/public ./public
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

CMD ["nginx", "-g", "daemon off;"]