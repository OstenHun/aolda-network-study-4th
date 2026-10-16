#!/bin/sh
# Remove only the default route inside this new lab container.
set -eu
if ip -4 route show default | read -r route; then
    ip -4 route del default
fi
exec /usr/lib/frr/docker-start
