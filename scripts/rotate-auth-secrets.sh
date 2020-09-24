#!/usr/bin/env bash
set -e

[[ -z "$COPS_HTACCESS_FILE" ]] && echo "Error: COPS_HTACCESS_FILE not set" && exit 1
[[ -s "$COPS_HTACCESS_FILE" ]] || ( echo "Error: COPS_HTACCESS_FILE does not exist or is empty" && exit 1 )

docker secret create basic-auth-users-temp $COPS_HTACCESS_FILE
set +e

cops_test_proxy_target="cops_stag_proxy"
auth_secret_name="basic-auth-users"
auth_secret_name_temp="${auth_secret_name}-temp"

revert_any_temp() {
  echo "Cleaning up (conflicting target errors are ok)..."
  for cops_proxy_target in cops_stag_proxy cops_prod_proxy; do
    docker service update --secret-rm $auth_secret_name_temp $cops_proxy_target
    docker service update --secret-add $auth_secret_name $cops_proxy_target
  done
  docker secret rm $auth_secret_name_temp
  echo "Done."
}
trap revert_any_temp ERR
trap revert_any_temp EXIT

echo "Creating a temp rotation on staging for acceptance..."
docker service update --secret-rm $auth_secret_name $cops_test_proxy_target
docker service update --secret-add "source=${auth_secret_name_temp},target=${auth_secret_name}" $cops_test_proxy_target
echo "Temp rotation in place on staging. Try it: https://cops-staging.openstax.org"
read  -n 1 -p "(R)evert | (a)ccept: " accept_char

echo

if [[ "$accept_char" = "a" ]] || [[ "$accept_char" = "A" ]]; then
  echo -n "Promoting rotation in "
  echo -n "5 " && sleep 1
  echo -n "4 " && sleep 1
  echo -n "3 " && sleep 1
  echo -n "2 " && sleep 1
  echo -n "1 " && sleep 1
  echo

  docker service update --secret-rm $auth_secret_name_temp $cops_test_proxy_target

  for cops_proxy_target in cops_stag_proxy cops_prod_proxy; do
    docker service update --secret-rm $auth_secret_name $cops_proxy_target
  done
  docker secret rm $auth_secret_name
  docker secret create $auth_secret_name $COPS_HTACCESS_FILE
  for cops_proxy_target in cops_stag_proxy cops_prod_proxy; do
    docker service update --secret-add $auth_secret_name $cops_proxy_target
  done
else
  echo "Reverting..."
fi

# Both branches end with clean-up exit trap
exit 0
