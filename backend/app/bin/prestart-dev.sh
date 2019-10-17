#! /usr/bin/env bash

# Let the DB start
python ./bin/db_wait.py

# Run migrations
alembic upgrade head

source ./bin/live-reload.sh

# Create initial data in DB
#python /app/app/initial_data.py
