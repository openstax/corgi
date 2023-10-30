#!/usr/bin/env bash
export DOMAIN="corgi-staging.ce.openstax.org"
export STACK_NAME="corgi_stag"
export SUBNET="172.28.1.0/24"
set +x
SESSION_SECRET="$(dd if=/dev/urandom bs=1024 count=1 | base64)"
set -x
export SESSION_SECRET

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "SUBNET=$SUBNET"
echo "${NEWLINE}"
