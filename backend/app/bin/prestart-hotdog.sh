#! /usr/bin/env bash

cd /app/hotdog || exit
uvicorn "main:server" --host 0.0.0.0 --port 3000 &
pid=$!
sleep 0.5
if ! jobs -p | grep $pid &> /dev/null; then
    echo "Failed to start hotdog"
    exit 1
fi
cd - || exit

# shellcheck source=SCRIPTDIR/prestart-dev.sh
source ./bin/prestart-dev.sh
