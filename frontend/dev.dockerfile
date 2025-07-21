FROM nginx:1.29 AS dev-runner

ENV NODE_MAJOR=18
RUN apt-get update && apt-get install -y build-essential ca-certificates curl gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y nodejs git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

ARG API_URL=http://backend
ARG API_URL_BROWSER=/
ENV API_URL=${API_URL}
ENV API_URL_BROWSER=${API_URL_BROWSER}

COPY ./nginx.dev.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY ./package*.json ./
RUN npm i

CMD nginx && npm i && npm run dev

# ---

FROM dev-runner AS hotdog-runner

COPY . .

CMD nginx && npm i && npm run hotdog && npm run dev
