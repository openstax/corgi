#! /usr/bin/env bash

cd /app/app

uvicorn main:server --host 0.0.0.0 --port 80 --debug
