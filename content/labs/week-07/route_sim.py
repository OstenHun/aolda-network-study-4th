"""Small IPv4 routing simulator. No sockets, shell commands, or host route changes."""

import copy
import ipaddress
import json
from pathlib import Path


def load_topology():
    # The supplied, fixed topology lives beside this script, regardless of cwd.
    filename = Path(__file__).with_name("topology.txt")
    with filename.open(encoding="utf-8-sig") as source:
        return json.load(source)


def choose_route(routes, destination):
    """Choose the most specific matching prefix in this one-table model."""
    address = ipaddress.IPv4Address(destination)
    selected = None
    longest = -1
    for route in routes:
        network = ipaddress.IPv4Network(route["prefix"])
        if address in network and network.prefixlen > longest:
            selected = route
            longest = network.prefixlen
    return selected


def show(nodes):
    for name, node in nodes.items():
        print(name, "addresses:", ", ".join(node["addresses"]))
        for route in node["routes"]:
            print(" ", route["prefix"], "via", route["via"], route["kind"])


def walk(nodes, start, destination, ttl):
    # Each router forwards once with a one-unit TTL decrement. End hosts do not.
    current = start
    while True:
        node = nodes[current]
        if destination in node["addresses"]:
            print(current, "DELIVERED", destination, "ttl", ttl)
            return True
        if node["router"]:
            ttl -= 1
            if ttl <= 0:
                print(current, "TTL_EXPIRED (model; no ICMP packet sent)")
                return False
        route = choose_route(node["routes"], destination)
        if route is None:
            print(current, "NO_ROUTE to", destination)
            return False
        # 'direct' resolves to the destination; 'via' resolves to a neighbor IP.
        next_ip = route["via"]
        if next_ip == "direct":
            next_ip = destination
        next_node = node["neighbors"].get(next_ip)
        if next_node is None:
            print(current, "NO_NEIGHBOR for", next_ip)
            return False
        print(current, "match", route["prefix"], "next", next_ip,
              "->", next_node, "ttl", ttl)
        current = next_node


def probe(nodes, start, end, ttl):
    source = nodes[start]["addresses"][0]
    destination = nodes[end]["addresses"][0]
    print("FORWARD", source, "->", destination)
    if not walk(nodes, start, destination, ttl):
        print("ROUND_TRIP FAIL (forward)")
        return
    print("RETURN", destination, "->", source)
    # The reply is a new packet with its own initial TTL.
    if walk(nodes, end, source, ttl):
        print("ROUND_TRIP OK (simulated)")
    else:
        print("ROUND_TRIP FAIL (return)")


def delete_route(nodes, name, prefix):
    network = str(ipaddress.IPv4Network(prefix))
    for route in nodes[name]["routes"]:
        if route["prefix"] == network:
            if route["kind"] != "static":
                raise ValueError("Only static routes may be deleted")
            nodes[name]["routes"].remove(route)
            print("DELETED", name, network, "(memory only)")
            return
    raise ValueError("Route not found; nothing changed")


def main():
    original = load_topology()
    nodes = copy.deepcopy(original)
    print("IPv4 routing model; Python 3.12+; no real packets or host changes")
    print("show | probe a b [ttl 1..255] | delete r2 192.0.2.0/24 | restore | quit")
    while True:
        try:
            words = input("sim> ").split()
            if not words:
                continue
            if words == ["quit"]:
                break
            if words == ["show"]:
                show(nodes)
            elif words == ["restore"]:
                nodes = copy.deepcopy(original)
                print("RESTORED all original routes")
            elif words[0] == "probe" and len(words) in (3, 4):
                start, end = words[1:3]
                if start not in ("a", "b") or end not in ("a", "b") or start == end:
                    raise ValueError("Use probe a b or probe b a")
                ttl = 64
                if len(words) == 4:
                    ttl = int(words[3])
                if not 1 <= ttl <= 255:
                    raise ValueError("TTL must be 1..255")
                probe(nodes, start, end, ttl)
            elif words[0] == "delete" and len(words) == 3:
                if words[1] not in ("r1", "r2"):
                    raise ValueError("Use router r1 or r2")
                delete_route(nodes, words[1], words[2])
            else:
                raise ValueError("Unknown command; see the command line above")
        except ValueError as error:
            print("INPUT_ERROR:", error)
        except (EOFError, KeyboardInterrupt):
            break
    print("Stopped; in-memory changes discarded")


if __name__ == "__main__":
    try:
        main()
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Cannot read topology.txt: {error}") from error
