#! /usr/bin/env bash

# Exit in case of error
set -e

TEST_RESULTS=${TEST_RESULTS-./junit.xml}

echo "Test results will be saved in: ${TEST_RESULTS}"

DOMAIN=backend \
docker-compose \
    -f docker-compose.shared.base-images.yml \
    -f docker-compose.shared.depends.yml \
    -f docker-compose.shared.env.yml \
    -f docker-compose.deploy.build.yml \
    -f docker-compose.tests.yml \
    config > docker-stack.yml

docker-compose -f docker-stack.yml build
docker-compose -f docker-stack.yml down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker-compose -f docker-stack.yml up -d
docker-compose -f docker-stack.yml exec backend-tests wait-for-it -t 10 db:5432
docker-compose -f docker-stack.yml exec db psql -h db -d postgres -U postgres -c "DROP DATABASE IF EXISTS tests"
docker-compose -f docker-stack.yml exec db psql -h db -d postgres -U postgres -c "CREATE DATABASE tests ENCODING 'UTF8'"
docker-compose -f docker-stack.yml exec backend-tests wait-for-it -t 10 backend:80
docker-compose -f docker-stack.yml exec -T backend-tests pytest ./tests -vvv --junitxml="${TEST_RESULTS}"
docker-compose -f docker-stack.yml down -v --remove-orphans
