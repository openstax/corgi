#! /usr/bin/env bash

cd /app/app || exit

MODULE_NAME=${MODULE_NAME:-main}
CALLABLE_NAME=${CALLABLE_NAME:-server}
SESSION_SECRET="$(dd if=/dev/urandom bs=1024 count=1 2>/dev/null | base64)"
export SESSION_SECRET

uvicorn "${MODULE_NAME}:${CALLABLE_NAME}" --host 0.0.0.0 --port 80 --debug
