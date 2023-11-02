#!/usr/bin/env bash

export DOMAIN="corgi-hotdog.ce.openstax.org"
export STACK_NAME="corgi_hotdog"
set +x
SESSION_SECRET="$(dd if=/dev/urandom bs=1024 count=1 2> /dev/null | base64)"
set -x
export SESSION_SECRET

NEWLINE=$'\n'
echo "${NEWLINE}The following environment variables were set:${NEWLINE}"
echo "DOMAIN=$DOMAIN"
echo "STACK_NAME=$STACK_NAME"
echo "${NEWLINE}"
