#!/usr/bin/env bash

export DOMAIN="corgi-hotdog.ce.openstax.org"
export STACK_NAME="corgi_hotdog"
export COMPOSE_FILE_PATH="docker-compose.stack.hotdog.yml"

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "${NEWLINE}"
