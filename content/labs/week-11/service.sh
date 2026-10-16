#!/bin/sh
set -eu
# The container stays running when this HTTP process stops.
case "${1:-}" in
  start)
    if test -f /tmp/http.pid && kill -0 "$(cat /tmp/http.pid)" 2>/dev/null; then
      echo 'HTTP already running' >&2; exit 1
    fi
    python3 -u -m http.server 8080 --bind 0.0.0.0 --directory /srv > /tmp/http.log 2>&1 &
    echo $! > /tmp/http.pid
    ;;
  stop)
    if ! test -f /tmp/http.pid; then
      echo 'HTTP pid file missing' >&2; exit 1
    fi
    kill "$(cat /tmp/http.pid)"
    rm /tmp/http.pid
    ;;
  *) echo 'usage: sh /lab/service.sh start|stop' >&2; exit 2 ;;
esac
