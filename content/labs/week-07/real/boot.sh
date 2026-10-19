#!/bin/sh
set -eu
mkdir -p /evidence
printf 'w07-real-route\n' > /run/w07-owned
echo 'READY: isolated week07 lab; use /lab/lab.sh'
trap 'exit 0' INT TERM
while :; do sleep 1 & wait $!; done
