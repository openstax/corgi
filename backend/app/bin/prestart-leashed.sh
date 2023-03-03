#! /usr/bin/env bash

# Let the DB start
python ./bin/db_wait.py

# Run migrations
alembic upgrade head

export MODULE_NAME=leashed

# shellcheck source=SCRIPTDIR/live-reload.sh
source ./bin/live-reload.sh
