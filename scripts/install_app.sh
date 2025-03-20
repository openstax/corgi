#!/bin/bash

# Exit with non-zero status if a simple command fails, even with piping
# https://stackoverflow.com/a/4346420/1664216

set -euo pipefail

# Script to run on the deployed server when the code has been
# updated (or on first deployment)

here="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$here/.." && pwd)"
backend_path="$repo_root/backend"
app_path="$backend_path/app"

cd "$app_path"

# Created during pyenv and poetry setup in ansible
source "$HOME/pyenv-init"
source "$HOME/poetry-init"

# Update pip
pip install -U pip

# Install exact versions from poetry.lock
pip install -r <(poetry export -f requirements.txt)

# Required by install_secrets.sh
pip install yq

echo "Oll Korrect" >&2
