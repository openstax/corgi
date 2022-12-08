#!/usr/bin/env bash

# Exit in case of error
set -e

[ "${DOMAIN}" = '' ] && echo "ERROR: Remember to set DOMAIN. e.g. DOMAIN=cops-staging.openstax.org" && exit 1
[ "${TRAEFIK_TAG}" = '' ] && echo "ERROR: Remember to set TRAEFIK_TAG. e.g. TRAEFIK_TAG=traefik-staging" && exit 1
[ "${STACK_NAME}" = '' ] && echo "ERROR: Remember to set STACK_NAME. e.g. STACK_NAME=cops-stag" && exit 1
[ "${TAG}" = '' ] && echo "ERROR: Remember to set TAG." && exit 1

REVISION=$(git --git-dir=./.git rev-parse --short HEAD)
DEPLOYED_AT=$(date '+%Y%m%d.%H%M%S')

echo "DOMAIN=${DOMAIN}
TRAEFIK_TAG=${TRAEFIK_TAG}
STACK_NAME=${STACK_NAME}
TAG=${TAG}
REVISION=${REVISION}
DEPLOYED_AT=${DEPLOYED_AT}"

set +x
DOMAIN=${DOMAIN} \
TRAEFIK_TAG=${TRAEFIK_TAG} \
STACK_NAME=${STACK_NAME} \
TAG=${TAG} \
REVISION=${REVISION} \
DEPLOYED_AT=${DEPLOYED_AT} \
SUBNET=${SUBNET} \
SESSION_SECRET=${SESSION_SECRET} \
docker-compose \
-f docker-compose.stack.release.yml \
config > docker-stack.yml

docker -H ssh://corgi stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME}"
