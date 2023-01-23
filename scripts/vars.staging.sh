#!/usr/bin/env bash
export DOMAIN="corgi-staging.ce.openstax.org"
export STACK_NAME="corgi_stag"
export TRAEFIK_TAG="traefik-staging"
set +x
SESSION_SECRET="$(dd if=/dev/urandom bs=1024 count=1 | base64)"
set -x
export SESSION_SECRET

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "TRAEFIK_TAG=$TRAEFIK_TAG"
echo "${NEWLINE}"
