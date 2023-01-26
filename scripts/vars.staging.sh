#!/usr/bin/env bash
export DOMAIN="corgi-staging.ce.openstax.org"
export STACK_NAME="corgi_stag"
export TRAEFIK_TAG="traefik-staging"
export SUBNET="172.28.1.0/24"

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "TRAEFIK_TAG=$TRAEFIK_TAG"
echo "SUBNET=$SUBNET"
echo "${NEWLINE}"
