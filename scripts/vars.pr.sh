#!/usr/bin/env bash
export DOMAIN="corgi-$PR_NUMBER.ce.openstax.org"
export STACK_NAME="corgi_$PR_NUMBER"
export TRAEFIK_TAG="traefik-$PR_NUMBER"

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "TRAEFIK_TAG=$TRAEFIK_TAG"
echo "${NEWLINE}"
