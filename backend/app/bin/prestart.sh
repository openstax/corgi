#! /usr/bin/env bash

source ./bin/live-reload.sh

# Let the DB start
python ./bin/db_wait.py

# Run migrations
alembic upgrade head

# Create initial data in DB
#python /app/app/initial_data.py
