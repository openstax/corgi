#! /usr/bin/env bash
set -e

wait-for-it -t 10 backend:80 -- pytest ./tests --driver=Chrome --base-url=http://frontend --headless -vvv
