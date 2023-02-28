#!/bin/bash

# Exit in case of error
set -e

# shellcheck source=SCRIPTDIR/build.sh
FRONTEND_ENV=${FRONTEND_ENV-production} \
source ./scripts/build.sh

docker-compose -f docker-stack.yml push
