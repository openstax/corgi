#!/usr/bin/env bash

# Exit in case of error
set -euo pipefail

if test -n "${DEBUG_RUN_LOCAL:-}"; then
    run_script() {
        if test -n "${SSH_HOST:-}"; then
            echo "ERROR: SSH_HOST and DEBUG_RUN_LOCAL should not both be set"
            exit 111
        fi
        env -i HOME="$HOME" PATH="$PATH" bash -seuxo pipefail
    }
else
    run_script() {
        ssh "${SSH_HOST:?}" 'bash -seuo pipefail'
    }
fi

try_find_tag() {
    service_name="$1"
    : "${service_name:?}"
    tag=""
    while read -r _id name _mode _replicas image _ports; do
        if [[ "$name" == "$service_name" ]]; then
            tag="$(echo "$image" | cut -d: -f2)"
            break
        fi
    done
    echo "$tag"
}

service_list="$(echo "docker service ls" | run_script)"
scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

staging_fe_tag=$(echo "$service_list" | try_find_tag "corgi_stag_frontend")
staging_be_tag=$(echo "$service_list" | try_find_tag "corgi_stag_backend")

prod_fe_tag=$(echo "$service_list" | try_find_tag "corgi_prod_frontend")
prod_be_tag=$(echo "$service_list" | try_find_tag "corgi_prod_backend")

: "${staging_fe_tag:?}"
: "${staging_be_tag:?}"
[[ "$staging_fe_tag" = "$staging_be_tag" ]] || (echo "Err: Frontend and backend tags differ" && exit 3)
[[ "$staging_fe_tag" =~ ^[0-9]{8}[.][0-9]{6}$ ]] || (echo "Err: Bad format for tag" && exit 4)

echo "Script dir: ${scripts_dir}"
echo "Detected STAGING tags frontend ($staging_fe_tag) and backend ($staging_be_tag)"
echo "Detected PROD tags frontend ($prod_fe_tag) and backend ($prod_be_tag)"

echo -n "Promoting in "
echo -n "5 " && sleep 1
echo -n "4 " && sleep 1
echo -n "3 " && sleep 1
echo -n "2 " && sleep 1
echo -n "1 " && sleep 1
echo


# shellcheck disable=SC1091
source "$scripts_dir/vars.common.sh"
# shellcheck disable=SC1091
source "$scripts_dir/vars.prod.sh"
export TAG="$staging_fe_tag"
# shellcheck disable=SC1091
source "$scripts_dir/deploy.sh"
