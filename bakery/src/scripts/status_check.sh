#!/bin/bash
job_id=$(cat "${RESOURCE}/id")
subsequent_failures=0
while true; do
  curl -w "%{http_code}" -o response "$API_ROOT/jobs/${job_id}" > status_code
  timestamp=$(date '+%H:%M:%S')
  status_code="$(cat status_code)"
  if [[ "$status_code" = "200" ]]; then
    subsequent_failures=0
    current_job_status_id=$(jq -r '.status.id' response)
    case "$current_job_status_id" in
      2 | 3)
        echo "${timestamp} | Pipeline running, no intervention needed"
        ;;
      4 | 5)
        echo "${timestamp} | Pipeline completed, no intervention needed"
        sleep 1
        exit 0
        ;;
      6)
        echo "${timestamp} | Job aborted via UI, torpedoing the build"
        sleep 1
        exit 1
        ;;
      *)
        echo "${timestamp} | Unknown job status id ('${current_job_status_id}'), torpedoing the build"
        sleep 1
        exit 1
        ;;
    esac
  elif [[ "$((++subsequent_failures))" -gt "2" ]]; then
    echo "${timestamp} | Unable to check status code ('${status_code}'), torpedoing the build"
    sleep 1
    exit 1
  fi
  sleep 30
done
