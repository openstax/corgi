#!/usr/bin/env bash
export DOMAIN="corgi.ce.openstax.org"
export STACK_NAME="corgi_prod"
export SUBNET="172.28.2.0/24"
set +x
SESSION_SECRET="$(dd if=/dev/urandom bs=1024 count=1 | base64)"
set -x
export SESSION_SECRET
