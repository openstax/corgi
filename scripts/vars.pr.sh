#!/usr/bin/env bash

[ "${PR_NUMBER}" = '' ] && echo "ERROR: Remember to set paramater for PR_NUMBER. e.g. PR_NUMBER=458" && exit 1

export DOMAIN="corgi-$PR_NUMBER.ce.openstax.org"
export STACK_NAME="corgi_$PR_NUMBER"
export TRAEFIK_TAG="traefik-$PR_NUMBER"
export FQDN="https://$DOMAIN"

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "TRAEFIK_TAG=$TRAEFIK_TAG"
echo "FQDN=$FQDN"
echo "${NEWLINE}"
