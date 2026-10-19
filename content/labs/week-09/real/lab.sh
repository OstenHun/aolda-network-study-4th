#!/bin/sh
# Run only in the dedicated Compose container. All links/namespaces are local.
set -eu
test "$(cat /run/w09-lab-owned 2>/dev/null)" = w09-real-l2 || {
    echo 'Use docker compose exec lab sh /lab/lab.sh ...; never run on the host.' >&2
    exit 2
}

usage() {
    echo 'lab.sh stp|lacp up|show|ping|down'
    echo 'lab.sh stp link l13 down|up'
    echo 'lab.sh lacp link m1 down|up'
    echo 'lab.sh lacp mode active|passive  (s1 only; s2 stays passive)'
    exit 2
}

mode=${1:-}; action=${2:-}
case "$mode" in stp|lacp) ;; *) usage ;; esac
current=$(cat /run/w09-mode 2>/dev/null || true)

# Capture only dedicated experiment links. No host/management traffic exists here.
capture() {
    iface=$1
    tcpdump -U -n -s 0 -i "$iface" -w "/evidence/$mode-$iface.pcap" \
        >"/evidence/$mode-$iface.capture.log" 2>&1 &
    echo "$!" > "/run/w09-capture-$iface.pid"
    count=0
    until grep -q 'listening on' "/evidence/$mode-$iface.capture.log"; do
        kill -0 "$(cat "/run/w09-capture-$iface.pid")"
        count=$((count + 1))
        test "$count" -lt 30 || return 1
        sleep 0.1
    done
}

cleanup() {
    for pidfile in /run/w09-capture-*.pid; do
        test -f "$pidfile" || continue
        kill -INT "$(cat "$pidfile")" 2>/dev/null || true
    done
    sleep 1
    for host in ha hb; do
        if ip netns list | cut -d ' ' -f 1 | grep -qx "$host"; then ip netns del "$host"; fi
    done
    if test "$mode" = lacp; then
        ovs-vsctl --if-exists del-br s1
        ovs-vsctl --if-exists del-br s2
    fi
    for iface in s1p2 s1p3 s2p3 s2a s3b s1a s2b m1a m2a s1 s2 s3; do
        if ip link show dev "$iface" >/dev/null 2>&1; then ip link del dev "$iface"; fi
    done
    rm -f /run/w09-capture-*.pid /run/w09-mode
    echo 'CLEAN: experiment namespaces/links removed; evidence remains in /evidence'
}

pair() { ip link add "$1" type veth peer name "$2"; }
host() {
    ns=$1; port=$2; address=$3; mac=$4
    ip netns add "$ns"
    ip link add "$port" type veth peer name eth0 netns "$ns"
    ip -n "$ns" link set lo up
    ip -n "$ns" link set eth0 address "$mac"
    ip -n "$ns" address add "$address/24" dev eth0
    ip -n "$ns" link set eth0 up
}

stp_up() {
    for n in 1 2 3; do
        ip link add "s$n" address "02:00:09:00:00:0$n" type bridge \
            priority "$((n * 4096))" vlan_filtering 1 vlan_default_pvid 0
        # This iproute2 uses clock_t ticks, not seconds, for bridge timer inputs.
        # USER_HZ=100: max_age 6s, listening/learning 4s each, hello 1s.
        ip link set "s$n" type bridge max_age 600
        ip link set "s$n" type bridge forward_delay 400 hello_time 100
        ip link set "s$n" type bridge stp_state 1
        ip link set "s$n" up
    done
    pair s1p2 s2p1; pair s1p3 s3p1; pair s2p3 s3p2
    for port in s1p2 s1p3 s2p1 s2p3 s3p1 s3p2; do
        sw=$(printf '%s' "$port" | cut -c 1-2)
        ip link set "$port" master "$sw"
        bridge link set dev "$port" cost 10
        bridge vlan add dev "$port" vid 10
    done
    host ha s2a 192.0.2.10 02:00:09:00:0a:01
    host hb s3b 192.0.2.20 02:00:09:00:0b:01
    ip link set s2a master s2; ip link set s3b master s3
    bridge vlan add dev s2a vid 10 pvid untagged
    bridge vlan add dev s3b vid 10 pvid untagged
    for port in s1p2 s1p3 s2p1 s2p3 s3p1 s3p2 s2a s3b; do ip link set "$port" up; done
    capture s3p2; capture s1p3
}

lacp_up() {
    # Separate from STP: no STP on OVS bonds, no fallback to an unnegotiated link.
    ovs-vsctl add-br s1 -- set Bridge s1 other_config:hwaddr=02:00:09:00:00:01
    ovs-vsctl add-br s2 -- set Bridge s2 other_config:hwaddr=02:00:09:00:00:02
    pair m1a m1b; pair m2a m2b
    ovs-vsctl add-bond s1 po1 m1a m2a lacp=active bond_mode=balance-tcp \
        other_config:lacp-time=fast other_config:lacp-system-id=02:00:09:00:00:01 \
        other_config:lacp-fallback-ab=false vlan_mode=trunk trunks=10
    ovs-vsctl add-bond s2 po2 m1b m2b lacp=passive bond_mode=balance-tcp \
        other_config:lacp-time=fast other_config:lacp-system-id=02:00:09:00:00:02 \
        other_config:lacp-fallback-ab=false vlan_mode=trunk trunks=10
    host ha s1a 192.0.2.10 02:00:09:00:0a:01
    host hb s2b 192.0.2.20 02:00:09:00:0b:01
    ovs-vsctl add-port s1 s1a tag=10
    ovs-vsctl add-port s2 s2b tag=10
    for port in m1a m1b m2a m2b s1a s2b; do ip link set "$port" up; done
    capture m1a; capture m2a
}

case "$action" in
    up)
        test "$#" -eq 2 || usage
        test -z "$current" || { echo 'A lab is active; down it first.' >&2; exit 2; }
        for iface in s1 s2 s3 m1a m2a s1a s2a s2b s3b; do
            if ip link show dev "$iface" >/dev/null 2>&1; then echo "Refusing existing $iface" >&2; exit 2; fi
        done
        test -z "$(ip netns list)" || { echo 'Refusing existing namespaces' >&2; exit 2; }
        # Captures belong to one run. Copy them out/down the container before rerunning.
        test -z "$(ls -A /evidence)" || { echo 'Evidence exists; copy it out and recreate the container.' >&2; exit 2; }
        echo "$mode" > /run/w09-mode
        trap 'result=$?; trap - EXIT; cleanup; exit "$result"' EXIT
        "${mode}_up"
        trap - EXIT
        echo 'STARTED: wait for observed convergence, then show/ping; up is not a success test.'
        ;;
    show)
        test "$#" -eq 2 || usage
        test "$current" = "$mode" || { echo 'This mode is not active' >&2; exit 2; }
        date -u '+%Y-%m-%dT%H:%M:%SZ'
        if test "$mode" = stp; then
            ip -d link show type bridge
            bridge -d link show
            bridge vlan show
            bridge fdb show
        else
            ovs-appctl lacp/show
            ovs-appctl bond/show
            ovs-vsctl show
        fi
        ;;
    ping)
        test "$#" -eq 2 || usage
        test "$current" = "$mode" || { echo 'This mode is not active' >&2; exit 2; }
        ip netns exec ha ping -n -c 3 -W 1 192.0.2.20
        ;;
    link)
        test "$#" -eq 4 || usage
        test "$current" = "$mode" || { echo 'This mode is not active' >&2; exit 2; }
        case "$4" in up|down) ;; *) usage ;; esac
        case "$mode:$3" in stp:l13) port=s1p3 ;; lacp:m1) port=m1a ;; *) usage ;; esac
        date -u '+%Y-%m-%dT%H:%M:%SZ'
        ip link set dev "$port" "$4"
        ip -br link show dev "$port"
        ;;
    mode)
        test "$#" -eq 3 && test "$mode" = lacp || usage
        test "$current" = lacp || { echo 'LACP mode is not active' >&2; exit 2; }
        case "$3" in active|passive) ;; *) usage ;; esac
        ovs-vsctl set Port po1 "lacp=$3"
        ;;
    down)
        test "$#" -eq 2 || usage
        test "$current" = "$mode" || { echo 'This mode is not active; nothing removed.' >&2; exit 2; }
        cleanup
        ;;
    *) usage ;;
esac
