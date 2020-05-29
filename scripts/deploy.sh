#!/usr/bin/env bash

# Exit in case of error
set -e

[ "${DOMAIN}" = '' ] && echo "ERROR: Remember to set DOMAIN=cops-staging.openstax.org" && exit 1
[ "${TRAEFIK_TAG}" = '' ] && echo "ERROR: Remember to set TRAEFIK_TAG=traefik-staging" && exit 1
[ "${STACK_NAME}" = '' ] && echo "ERROR: Remember to set STACK_NAME=cops-stag" && exit 1
[ "${TAG}" = '' ] && echo "WARNING: Using TAG=latest" && sleep 5

DOMAIN=${DOMAIN} \
TRAEFIK_TAG=${TRAEFIK_TAG} \
STACK_NAME=${STACK_NAME} \
TAG=${TAG-latest} \
docker-compose \
-f docker-compose.shared.admin.yml \
-f docker-compose.shared.base-images.yml \
-f docker-compose.shared.depends.yml \
-f docker-compose.shared.env.yml \
-f docker-compose.deploy.command.yml \
-f docker-compose.deploy.images.yml \
-f docker-compose.deploy.labels.yml \
-f docker-compose.deploy.networks.yml \
-f docker-compose.deploy.volumes-placement.yml \
-f docker-compose.deploy.settings.yml \
-f docker-compose.deploy.logging.yml \
config > docker-stack.yml

docker-auto-labels docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME}"
