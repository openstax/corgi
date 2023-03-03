#! /usr/bin/env bash

cd /app/app || exit

MODULE_NAME=${MODULE_NAME:-main}
CALLABLE_NAME=${CALLABLE_NAME:-server}

uvicorn "${MODULE_NAME}:${CALLABLE_NAME}" --host 0.0.0.0 --port 80 --debug
