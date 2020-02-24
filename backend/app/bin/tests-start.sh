#! /usr/bin/env bash
set -e

wait-for-it -t 10 backend:80 -- pytest ./tests -vvv --junitxml="$TEST_RESULTS"/junit.xml
