#!/usr/bin/env bash

# Exit in case of error
set -euo pipefail

if test -n "${DEBUG_RUN_LOCAL:-}"; then
    if test -n "${SSH_HOST:-}"; then
        echo "ERROR: SSH_HOST and DEBUG_RUN_LOCAL should not both be set"
        exit 111
    fi
    run_script() {
        env -i HOME="$HOME" PATH="$PATH" bash -seuxo pipefail
    }
else
    run_script() {
        ssh "${SSH_HOST:?}" 'bash -seuo pipefail'
    }
fi

: "${DOMAIN:?'Remember to set DOMAIN. e.g. DOMAIN=corgi-staging.openstax.org'}"
: "${STACK_NAME:?'Remember to set STACK_NAME. e.g. STACK_NAME=corgi-stag'}"
: "${TAG:?'Remember to set TAG'}"
REVISION=$(git --git-dir=./.git rev-parse --short HEAD)
DEPLOYED_AT=$(date '+%Y%m%d.%H%M%S')

echo "Now updating $STACK_NAME with: 
TAG=$TAG
REVISION=$REVISION
DOMAIN=$DOMAIN
DEPLOYED_AT=$DEPLOYED_AT"

base64_gzipped_compose_file="$(gzip -kc "${COMPOSE_FILE_PATH:?}" | base64)"
# EVERY variable used in ANY stack should be input to the stack deploy command
# 1. This makes it easier to tell at a glance which variables exist
# 2. When this runs, the command will not inherit the environment
# 3. The compose files can define which variables are required (via ${varname:?})
run_script <<EOF
    echo "$base64_gzipped_compose_file" | base64 -d | gzip -dc | \
    DOMAIN="$DOMAIN" \
    STACK_NAME="$STACK_NAME" \
    TAG="$TAG" \
    REVISION="$REVISION" \
    DEPLOYED_AT="$DEPLOYED_AT" \
    SESSION_SECRET="$SESSION_SECRET" \
    TRAEFIK_PUBLIC_NETWORK="$TRAEFIK_PUBLIC_NETWORK" \
    TRAEFIK_PUBLIC_TAG="$TRAEFIK_PUBLIC_TAG" \
    DOCKER_IMAGE_BACKEND="$DOCKER_IMAGE_BACKEND" \
    DOCKER_IMAGE_FRONTEND="$DOCKER_IMAGE_FRONTEND" \
    SUBNET="${SUBNET:-}" \
    GITHUB_API_TOKEN="${GITHUB_API_TOKEN:-}" \
    GITHUB_OAUTH_ID="${GITHUB_OAUTH_ID:-}" \
    GITHUB_OAUTH_SECRET="${GITHUB_OAUTH_SECRET:-}" \
    POSTGRES_SERVER="${POSTGRES_SERVER:-}" \
    POSTGRES_DB="${POSTGRES_DB:-}" \
    POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}" \
    POSTGRES_USER="${POSTGRES_USER:-}" \
    docker stack deploy -c - --with-registry-auth "$STACK_NAME"
EOF
