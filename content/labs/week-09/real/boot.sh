#!/bin/sh
set -eu
mkdir -p /run/openvswitch /etc/openvswitch /evidence
ovsdb-tool create /etc/openvswitch/conf.db /usr/share/openvswitch/vswitch.ovsschema
ovsdb-server --remote=punix:/run/openvswitch/db.sock --pidfile --detach
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach
printf 'w09-real-l2\n' > /run/w09-lab-owned
echo 'READY: isolated week09 lab; use /lab/lab.sh'
trap 'exit 0' INT TERM
while :; do sleep 1 & wait $!; done
