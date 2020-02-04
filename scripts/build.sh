#!/bin/bash

# Exit in case of error
set -e

[ "${DOMAIN}" = '' ] && echo "ERROR: Remember to set DOMAIN=cops-staging.openstax.org" && exit 1
[ "${TAG}" = '' ] && echo "WARNING: Using TAG=latest" && sleep 5

TAG=${TAG-latest} \
FRONTEND_ENV=${FRONTEND_ENV-production}
docker-compose \
-f docker-compose.deploy.build.yml \
-f docker-compose.deploy.images.yml \
config > docker-stack.yml

docker-compose -f docker-stack.yml build --no-cache
