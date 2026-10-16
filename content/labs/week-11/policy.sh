#!/bin/sh
set -eu
# Change only the new HTTP connection verdict in this container's own table.
case "${1:-}" in
  allow) verdict=accept ;;
  block) verdict=drop ;;
  *) echo 'usage: sh /lab/policy.sh allow|block' >&2; exit 2 ;;
esac

# Keep replacement atomic: remove/recreate only inet w11 in one nft transaction.
delete_line=''
if nft list table inet w11 >/dev/null 2>&1; then
  delete_line='delete table inet w11'
fi
cat > /tmp/w11.nft <<EOF
$delete_line
table inet w11 {
  chain input {
    type filter hook input priority 0; policy drop;
    iifname "lo" accept
    ct state established,related counter accept
    ip saddr 172.30.111.11 ip daddr 172.30.111.20 tcp dport 8080 counter $verdict
    tcp dport 8080 counter drop
  }
}
EOF
nft --check --file /tmp/w11.nft
nft --file /tmp/w11.nft
nft list table inet w11
