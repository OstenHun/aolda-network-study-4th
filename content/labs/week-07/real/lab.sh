#!/bin/sh
set -eu
test "$(cat /run/w07-owned 2>/dev/null)" = w07-real-route || {
    echo 'Use docker compose exec lab sh /lab/lab.sh; never run on the host.' >&2
    exit 2
}
usage() {
    echo 'lab.sh up|show|lookup|forward-restore|down'
    echo 'lab.sh ping [ICMP-ID: 1..65535]'
    echo 'lab.sh return down|up  OR  lab.sh link down|up (R1-R2 only)'
    exit 2
}
stamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
note() { { stamp; printf '%s\n' "$*"; } | tee -a /evidence/actions.log; }
cleanup() {
    for file in /run/w07-capture-*.pid; do
        test -f "$file" || continue
        kill -INT "$(cat "$file")" 2>/dev/null || true
    done
    sleep 1
    for node in a r1 r2 b; do
        if ip netns list | cut -d ' ' -f 1 | grep -qx "$node"; then ip netns del "$node"; fi
    done
    # Also remove owned ends left by a partial setup before their namespace move.
    for port in a0 r1a r1x r2x r2b b0; do
        if ip link show dev "$port" >/dev/null 2>&1; then ip link del dev "$port"; fi
    done
    rm -f /run/w07-capture-*.pid /run/w07-active
    echo 'CLEAN: owned namespaces/links removed; /evidence remains'
}
end() {
    port=$1; node=$2; name=$3; address=$4
    ip link set "$port" netns "$node"
    ip -n "$node" link set "$port" name "$name"
    ip -n "$node" address add "$address" dev "$name"
    ip -n "$node" link set "$name" up
}
capture() {
    node=$1; port=$2; label=$3
    ip netns exec "$node" tcpdump -U -n -s 0 -i "$port" -w "/evidence/$label.pcap" \
        >"/evidence/$label.capture.log" 2>&1 &
    echo "$!" > "/run/w07-capture-$label.pid"
    tries=0
    until grep -q 'listening on' "/evidence/$label.capture.log"; do
        kill -0 "$(cat "/run/w07-capture-$label.pid")"
        tries=$((tries + 1)); test "$tries" -lt 30 || return 1
        sleep 0.1
    done
}
action=${1:-}
if test "$action" = up; then
    test "$#" -eq 1 || usage
    test ! -f /run/w07-active || { echo 'Already active; down first.' >&2; exit 2; }
    test -z "$(ip netns list)" || { echo 'Refusing existing namespaces.' >&2; exit 2; }
    test -z "$(ls -A /evidence)" || { echo 'Evidence exists; copy it out and recreate.' >&2; exit 2; }
    for port in a0 r1a r1x r2x r2b b0; do
        if ip link show dev "$port" >/dev/null 2>&1; then echo "Refusing existing $port" >&2; exit 2; fi
    done
    touch /run/w07-active
    trap 'result=$?; trap - EXIT; cleanup; exit "$result"' EXIT
    for node in a r1 r2 b; do ip netns add "$node"; ip -n "$node" link set lo up; done
    ip link add a0 type veth peer name r1a
    ip link add r1x type veth peer name r2x
    ip link add r2b type veth peer name b0
    end a0 a eth0 192.0.2.10/24
    end r1a r1 lan0 192.0.2.1/24
    end r1x r1 transit0 198.51.100.1/30
    end r2x r2 transit0 198.51.100.2/30
    end r2b r2 lan0 203.0.113.1/24
    end b0 b eth0 203.0.113.20/24
    for router in r1 r2; do
        # ip netns exec creates a private mount namespace. This temporary proc
        # mount permits ONLY this network namespace's forwarding/rp_filter writes.
        ip netns exec "$router" sh -ec '
            mount -t proc proc /proc
            sysctl -qw net.ipv4.ip_forward=1
            for file in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$file"; done
        '
    done
    ip -n a route add default via 192.0.2.1
    ip -n r1 route add 203.0.113.0/24 via 198.51.100.2
    ip -n r2 route add 192.0.2.0/24 via 198.51.100.1
    ip -n b route add default via 203.0.113.1
    capture r1 lan0 a-edge
    capture r2 lan0 b-edge
    note 'UP: A--R1--R2--B; static routes; no alternative path'
    trap - EXIT
    exit 0
fi
case "$action" in show|lookup|ping|return|link|forward-restore|down) ;; *) usage ;; esac
test -f /run/w07-active || { echo 'No active lab; nothing changed.' >&2; exit 2; }
case "$action" in
    show)
        test "$#" -eq 1 || usage
        stamp
        for node in a r1 r2 b; do
            echo "=== $node ==="
            ip -n "$node" -br address show
            ip -n "$node" -4 route show
            ip -n "$node" neigh show
        done
        for router in r1 r2; do
            echo "=== $router forwarding/rp_filter ==="
            ip netns exec "$router" sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter net.ipv4.conf.lan0.rp_filter net.ipv4.conf.transit0.rp_filter
        done
        ;;
    lookup)
        test "$#" -eq 1 || usage
        echo 'R1: forward request (lookup only)'
        ip -n r1 route get 203.0.113.20 from 192.0.2.10 iif lan0 || true
        echo 'R2: return reply (lookup only)'
        ip -n r2 route get 192.0.2.10 from 203.0.113.20 iif lan0 || true
        ;;
    ping)
        test "$#" -le 2 || usage
        id=${2:-700}
        case "$id" in ''|*[!0-9]*) usage ;; esac
        test "$id" -ge 1 && test "$id" -le 65535 || usage
        note "PING: A to B, ICMP id=$id"
        ip netns exec a ping -n -c 3 -W 1 -e "$id" 203.0.113.20
        ;;
    return|link)
        test "$#" -eq 2 || usage
        case "$2" in up|down) ;; *) usage ;; esac
        note "$action $2"
        if test "$action" = link; then
            ip -n r1 link set dev transit0 "$2"
        elif test "$2" = down; then
            ip -n r2 route del 192.0.2.0/24 via 198.51.100.1
        else
            ip -n r2 route replace 192.0.2.0/24 via 198.51.100.1
        fi
        ;;
    forward-restore)
        test "$#" -eq 1 || usage
        note 'FORWARD RESTORE: R1 static route to B'
        ip -n r1 route replace 203.0.113.0/24 via 198.51.100.2
        ;;
    down)
        test "$#" -eq 1 || usage
        note DOWN
        cleanup
        ;;
esac
