#! /usr/bin/env bash

# Exit in case of error
set -e

TEST_RESULTS_DIR=${TEST_RESULTS_DIR-./reports}
TEST_RESULTS_INTEGRATION=${TEST_RESULTS_INTEGRATION-./junit-integration.xml}
TEST_RESULTS_UNIT=${TEST_RESULTS_UNIT-./junit-unit.xml}
TEST_RESULTS_UI=${TEST_RESULTS_UI-./junit-ui.xml}

echo "Test results will be saved in: ${TEST_RESULTS_DIR}"

BACKEND_URL="http://backend"
FRONTEND_URL="http://frontend"
DEPLOYED_AT=$(date '+%Y%m%d.%H%M%S')
REVISION=$(git --git-dir=./.git rev-parse --short HEAD)

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
docker-compose -f docker-stack.yml exec -T backend-tests pytest -vvv --junitxml="${TEST_RESULTS_INTEGRATION}" --base-url="${BACKEND_URL}" ./tests/integration
docker-compose -f docker-stack.yml exec -T backend-tests pytest -vvv --junitxml="${TEST_RESULTS_UI}" --base-url="${FRONTEND_URL}" ./tests/ui
# Comment this line out to leave the stack running. Useful for test development.
docker-compose -f docker-stack.yml down -v --remove-orphans
