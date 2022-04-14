#! /usr/bin/env bash

# Exit in case of error
set -e

TEST_RESULTS=${TEST_RESULTS-./junit.xml}

echo "Test results will be saved in: ${TEST_RESULTS}"

export DEPLOYED_AT=$(date '+%Y%m%d.%H%M%S')
export REVISION=$(git --git-dir=./.git rev-parse --short HEAD)
export DOMAIN=${DOMAIN-backend}
export BASE_URL=${FQDN-http://backend}

DOMAIN=${DOMAIN} \
REVISION=${REVISION} \
TAG=${TAG} \
STACK_NAME=${STACK_NAME} \
DEPLOYED_AT=${DEPLOYED_AT} \
docker-compose \
    -f docker-compose.stack.ci.yml \
    config > docker-stack.yml

docker-compose -f docker-stack.yml build
docker-compose -f docker-stack.yml down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker-compose -f docker-stack.yml up -d
docker-compose -f docker-stack.yml exec backend-tests wait-for-it -t 10 db:5432
docker-compose -f docker-stack.yml exec db psql -h db -d postgres -U postgres -c "DROP DATABASE IF EXISTS tests"
docker-compose -f docker-stack.yml exec db psql -h db -d postgres -U postgres -c "CREATE DATABASE tests ENCODING 'UTF8'"
docker-compose -f docker-stack.yml restart backend
docker-compose -f docker-stack.yml exec backend-tests wait-for-it -t 10 backend:80
docker-compose -f docker-stack.yml exec -T backend-tests pytest ./tests/integration -vvv --junitxml="${TEST_RESULTS}" --base-url="${BASE_URL}"
# Comment this line out to leave the stack running. Useful for test development.
docker-compose -f docker-stack.yml down -v --remove-orphans
