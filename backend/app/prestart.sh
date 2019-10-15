#! /usr/bin/env bash
# The image used by the backend expects for this file to be here.
# https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/python3.7/start-reload.sh#L18
# Without it there are some issues. This can be fixed by creating
# our own image. For now we'll go with this as the "prod" method.

# Let the DB start
python ./bin/db_wait.py

# Run migrations
alembic upgrade head
