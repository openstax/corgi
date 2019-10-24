FROM nginx:1.16-alpine

RUN apk add --update nodejs npm yarn

WORKDIR /app

COPY package*.json /app/

RUN yarn global add pm2
RUN yarn install

COPY ./ /app/

RUN yarn build

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

CMD nginx ; pm2-runtime start npm --name "frontend" -- start
