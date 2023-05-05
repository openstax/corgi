FROM nginx:1.19

RUN apt-get update && apt-get install -y build-essential \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

ARG API_URL=http://backend
ARG API_URL_BROWSER=/
ENV API_URL=${API_URL}
ENV API_URL_BROWSER=${API_URL_BROWSER}

COPY ./nginx.dev.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

CMD npm run bootcamp && nginx && npm i && npm run dev