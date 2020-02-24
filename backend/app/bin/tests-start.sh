#! /usr/bin/env bash
set -e

TEST_RESULT_PATH=${TEST_RESULT_PATH:-.}

echo "Saving Test Results to : ${TEST_RESULT_PATH}"

wait-for-it -t 10 backend:80 -- pytest ./tests -vvv --junitxml="${TEST_RESULT_PATH}/junit.xml"
