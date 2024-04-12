#!/usr/bin/env bash

export DOMAIN="corgi-staging.ce.openstax.org"
export STACK_NAME="corgi_stag"
export SUBNET="172.28.1.0/24"
export COMPOSE_FILE_PATH="docker-compose.stack.release.yml"

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "SUBNET=$SUBNET"
echo "${NEWLINE}"
