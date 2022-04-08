#! /usr/bin/env bash

# Exit in case of error
set -e

TEST_RESULTS=${TEST_RESULTS-./junit.xml}

echo "Test results will be saved in: ${TEST_RESULTS}"

DOMAIN=backend \
REVISION=dev \
TAG=dev \
STACK_NAME=dev \
DEPLOYED_AT=20210101.111111 \
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
docker-compose -f docker-stack.yml exec -T backend-tests pytest ./tests -vvv -m "ui or integration" --junitxml="${TEST_RESULTS}"
# Comment this line out to leave the stack running. Useful for test development.
docker-compose -f docker-stack.yml down -v --remove-orphans
