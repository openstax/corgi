#!/usr/bin/env bash

set -euo pipefail

ends-with() { [[ ${#2} -le ${#1} && "${1:$((${#1}-${#2}))}" == "$2" ]]; }
starts-with() { [[ ${#2} -le ${#1} && "${1:0:${#2}}" == "$2" ]]; }

read-secrets-spec() {
    # Flatten the spec recursively, joining keys on "/"
    # This should match handling of nested keys in openstax/aws-ruby
    # shellcheck disable=SC2016
    yq -r --arg top_key "$2" '
        def flattenspec(obj; pk):
            obj | to_entries | .[] |
            (if pk != "" then [pk, .key] | join("/") else .key end) as $key |
            if (.value | type) == "object" then
                flattenspec(.value; $key)
            else
                [$key, .value] | join("\t")
            end;
        flattenspec(.[$top_key]; "")
    ' "$1"
}

read-secrets-keys() {
    read-secrets-spec "$@" | cut -d$'\t' -f1
}

get-secrets() {
    aws ssm get-parameters \
        --with-decryption \
        --names "$@" \
        --output text \
        --query 'Parameters[*].[Name, Value]'
}

get-secrets-env() {
    local secret_name secret_value fq_secret_names
    fq_secret_names=()

    for secret_name in "$@"; do
        if starts-with "$secret_name" "/"; then
            fq_secret_names+=("$secret_name")
        else
            fq_secret_names+=("$SECRETS_NAMESPACE/$secret_name")
        fi
    done

    while IFS=$'\t' read -r secret_name secret_value; do
        # Chop off the namespace and replace remaining slashes with underscore
        # Example: /...namespace/github/api_token -> GITHUB_API_TOKEN
        echo -n "$secret_name" | \
            awk -v prefix="$SECRETS_NAMESPACE/" '{
                sub(prefix, "")
                gsub(/[-\/]/, "_")
                printf toupper($0)
            }'
        echo -n =
        echo "$secret_value"
    done < <(get-secrets "${fq_secret_names[@]}")
}

if [[ "${DEBUG_STUB_AWS:-0}" -eq 1 ]]; then
    echo "### STUBBING AWS CALLS ###" >&2
    get-secrets() {
        local i
        i=0
        for name in "$@"; do echo -e "$name\t$((i++))"; done
    }
fi

: "${SECRETS_NAMESPACE:?}"

here="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$here/.." && pwd)"
env_file="${ENV_FILE:-$repo_root/.env}"
secrets_spec="${SECRETS_SPEC:-$repo_root/secrets_spec.yml}"
readonly here repo_root env_file secrets_spec

if ends-with "$SECRETS_NAMESPACE" "/"; then
    SECRETS_NAMESPACE="${SECRETS_NAMESPACE:0:$((${#SECRETS_NAMESPACE}-1))}"
fi

if test -z "${1:-}"; then
    while read -r line; do
        set -- "$@" "$line"
    done < <(read-secrets-keys "$secrets_spec" "production")
fi

get-secrets-env "$@" >> "$env_file"
