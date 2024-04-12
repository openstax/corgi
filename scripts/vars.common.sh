#!/usr/bin/env bash

set +x
export TRAEFIK_PUBLIC_NETWORK=traefik-public
export TRAEFIK_PUBLIC_TAG=traefik-public
export DOCKER_IMAGE_BACKEND=backend
export DOCKER_IMAGE_FRONTEND=frontend
SESSION_SECRET="$(dd if=/dev/urandom bs=1024 count=1 2>/dev/null | base64)"
export SESSION_SECRET
