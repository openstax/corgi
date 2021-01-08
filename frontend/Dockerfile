FROM nginx:1.19-alpine

RUN apk add --update nodejs npm

WORKDIR /app

COPY package*.json /app/

RUN npm install --global pm2
RUN npm ci

COPY ./ /app/

ARG API_URL=http://backend
ARG API_URL_BROWSER=/
ENV API_URL=${API_URL}
ENV API_URL_BROWSER=${API_URL_BROWSER}

RUN npm run build

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

CMD nginx ; pm2-runtime start npm --name "frontend" -- start
