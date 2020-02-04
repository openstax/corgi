#!/bin/bash

# Exit in case of error
set -e

[ "${DOMAIN}" = '' ] && echo "ERROR: Remember to set DOMAIN=cops.openstax.org" && exit 1
[ "${TAG}" = '' ] && echo "WARNING: Using TAG=latest" && sleep 5

TAG=${TAG-latest} \
FRONTEND_ENV=${FRONTEND_ENV-production} \
source ./scripts/build.sh

docker-compose -f docker-stack.yml push
