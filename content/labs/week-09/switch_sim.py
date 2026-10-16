"""Week 09, simulator v1: converged L2 state, never host networking.

Equal-cost point-to-point trunks, one common spanning tree, independent VLAN
learning, and one two-member LACP group. No BPDUs/LACPDUs, timers or IP stack.
"""

import argparse
import copy
import json
import shlex
from collections import deque
from pathlib import Path


class SwitchLab:
    def __init__(self, config):
        self.original = copy.deepcopy(config)
        self.reset()

    def reset(self):
        self.config = copy.deepcopy(self.original)
        self.fdb = {}
        self.revision = 0

    def active_members(self):
        group = self.config.get("lacp")
        if group is None:
            return []
        # This is a settled compatibility rule, not LACP packet exchange.
        if "active" not in group["modes"].values():
            return []
        return sorted(name for name, up in group["members"].items() if up)

    def live_links(self):
        live = {}
        for name, link in self.config["links"].items():
            usable = link["up"]
            if name == "po1":
                usable = usable and bool(self.active_members())
            if usable:
                live[name] = link
        return live

    def spanning_tree(self):
        """Recompute settled roots, root ports and designated ports per component.

        All trunks cost 1. Bridge IDs are unique small ranks in this lab.
        VLAN admission is separate from the common control-plane topology.
        """
        bridges = self.config["bridges"]
        links = self.live_links()
        adjacency = {bridge: [] for bridge in bridges}
        for name, link in links.items():
            a, b = link["ends"]
            adjacency[a].append((b, name))
            adjacency[b].append((a, name))
        roots, distances, parent = {}, {}, {}
        remaining = set(bridges)
        while remaining:
            seed = min(remaining)
            component = {seed}
            queue = deque([seed])
            while queue:
                node = queue.popleft()
                for peer, _ in adjacency[node]:
                    if peer not in component:
                        component.add(peer)
                        queue.append(peer)
            root = min(component, key=bridges.get)
            distances[root] = 0
            queue = deque([root])
            while queue:
                node = queue.popleft()
                for peer, _ in adjacency[node]:
                    if peer not in distances:
                        distances[peer] = distances[node] + 1
                        queue.append(peer)
            for node in component:
                roots[node] = root
                if node != root:
                    candidates = []
                    for peer, name in adjacency[node]:
                        if distances[peer] + 1 == distances[node]:
                            candidates.append((bridges[peer], name))
                    parent[node] = min(candidates)[1]
            remaining -= component
        roles = {}
        for name, link in self.config["links"].items():
            if name not in links:
                for node in link["ends"]:
                    roles[node, name] = "disabled"
                continue
            designated = min(link["ends"], key=lambda n: (distances[n], bridges[n]))
            for node in link["ends"]:
                role = "blocked"
                if node == designated:
                    role = "designated"
                elif parent.get(node) == name:
                    role = "root"
                roles[node, name] = role
        return roots, distances, roles

    def frame(self, source, destination, flow=0):
        """Learn source on ingress, then forward/filter/flood within that VLAN."""
        hosts = self.config["hosts"]
        sender = hosts[source]
        vlan = sender["vlan"]
        _, _, roles = self.spanning_tree()
        events = [f"FRAME {source}->{destination} vlan={vlan} flow={flow}"]
        reached = []
        queue = deque([(sender["switch"], "host:" + source)])
        seen = set()
        while queue:
            switch, ingress = queue.popleft()
            if switch in seen:
                raise RuntimeError("forwarding loop: simulator invariant failed")
            seen.add(switch)
            key = (switch, vlan, sender["mac"])
            self.fdb[key] = ingress
            events.append(f"LEARN {switch} vlan={vlan} {sender['mac']} via={ingress}")
            target_port = None
            if destination != "broadcast":
                target_mac = hosts[destination]["mac"]
                target_port = self.fdb.get((switch, vlan, target_mac))
            decision = "FLOOD"
            if target_port is not None:
                decision = "UNICAST"
            events.append(f"{decision} {switch} ingress={ingress}")
            for host_name, host in hosts.items():
                port = "host:" + host_name
                eligible = host["switch"] == switch and host["vlan"] == vlan
                if eligible and port != ingress and target_port in (None, port):
                    reached.append(host_name)
                    events.append(f"DELIVER {host_name}")
            for name, link in self.live_links().items():
                if switch not in link["ends"] or name == ingress:
                    continue
                if target_port not in (None, name):
                    continue
                peer = next(n for n in link["ends"] if n != switch)
                if vlan not in link["vlans"]:
                    events.append(f"DROP {switch}/{name} VLAN-not-allowed")
                    continue
                if roles[switch, name] == "blocked" or roles[peer, name] == "blocked":
                    events.append(f"BLOCK {switch}/{name} STP")
                    continue
                detail = ""
                if name == "po1":
                    members = self.active_members()
                    member = members[flow % len(members)]
                    detail = f" member={member}"
                events.append(f"TX {switch}/{name}->{peer} tag={vlan}{detail}")
                queue.append((peer, name))
        return reached, events

    def show(self):
        roots, costs, roles = self.spanning_tree()
        lines = [f"SIM v1 settled revision={self.revision}; no wire packets/timers"]
        for node in sorted(roots):
            lines.append(f"BRIDGE {node} id={self.config['bridges'][node]} root={roots[node]} cost={costs[node]}")
        for (node, port), role in sorted(roles.items()):
            state = "forwarding"
            if role in ("blocked", "disabled"):
                state = role
            lines.append(f"PORT {node}/{port} role={role} state={state}")
        for name, host in self.config["hosts"].items():
            lines.append(f"ACCESS {host['switch']}/host:{name} vlan={host['vlan']} mac={host['mac']}")
        for name, link in self.config["links"].items():
            lines.append(f"TRUNK {name} up={link['up']} allowed={link['vlans']}")
        if "lacp" in self.config:
            group = self.config["lacp"]
            selected = self.active_members()
            lines.append(f"LACP modes={group['modes']} logical=po1 selected={len(selected)} min_links=1")
            for name, up in group["members"].items():
                collecting = name in selected and self.config["links"]["po1"]["up"]
                lines.append(f"MEMBER {name} carrier={up} collecting/distributing={collecting}")
        for (switch, vlan, mac), port in sorted(self.fdb.items()):
            lines.append(f"FDB {switch} vlan={vlan} {mac} via={port}")
        return lines

    def execute(self, line):
        parts = shlex.split(line)
        if not parts or parts[0].startswith("#"):
            return []
        command = parts[0]
        if parts == ["show"]:
            return self.show()
        if parts == ["reset"]:
            self.reset()
            return ["RESET original config; FDB empty"]
        if parts == ["help"]:
            return ["show | frame A B|broadcast [flow] | probe A B [flow]",
                    "link NAME up|down | vlan HOST 10|20 | allow LINK 10,20",
                    "mode BRIDGE active|passive | reset | quit"]
        if command in ("frame", "probe") and len(parts) in (3, 4):
            source, destination = parts[1:3]
            flow = 0
            if len(parts) == 4:
                flow = int(parts[3])
            if flow < 0:
                raise ValueError("flow must be nonnegative")
            if source not in self.config["hosts"]:
                raise ValueError("unknown source host")
            if destination not in self.config["hosts"] and destination != "broadcast":
                raise ValueError("unknown destination host")
            if source == destination or (command == "probe" and destination == "broadcast"):
                raise ValueError("probe needs two different hosts")
            reached, events = self.frame(source, destination, flow)
            if command == "probe":
                success = destination in reached
                if success:
                    back, reply = self.frame(destination, source, flow)
                    events += reply
                    success = source in back
                result = "FAIL"
                if success:
                    result = "PASS"
                events.append(f"PROBE {result} (simulated L2 request/reply, not ping/HTTP)")
            return events
        # Validate first; invalid commands leave every state field unchanged.
        if command == "link" and len(parts) == 3 and parts[2] in ("up", "down"):
            name = parts[1]
            members = self.config.get("lacp", {}).get("members", {})
            if name in members:
                members[name] = parts[2] == "up"
            elif name in self.config["links"]:
                self.config["links"][name]["up"] = parts[2] == "up"
            else:
                raise ValueError("unknown link")
        elif command == "vlan" and len(parts) == 3:
            vlan = int(parts[2])
            if parts[1] not in self.config["hosts"] or vlan not in (10, 20):
                raise ValueError("host must exist; supported VLANs are 10 and 20")
            self.config["hosts"][parts[1]]["vlan"] = vlan
        elif command == "allow" and len(parts) == 3:
            vlans = sorted(set(int(value) for value in parts[2].split(",")))
            if parts[1] not in self.config["links"] or not set(vlans) <= {10, 20}:
                raise ValueError("link must exist; supported VLANs are 10 and 20")
            self.config["links"][parts[1]]["vlans"] = vlans
        elif command == "mode" and len(parts) == 3 and parts[2] in ("active", "passive"):
            group = self.config.get("lacp")
            if group is None or parts[1] not in group["modes"]:
                raise ValueError("bridge is not a LACP endpoint")
            group["modes"][parts[1]] = parts[2]
        else:
            raise ValueError("invalid command; enter help")
        self.revision += 1
        self.fdb.clear()
        return ["CHANGED " + line, "SETTLED recomputed; all FDB cleared by model"]


def load_lab(filename):
    config = json.loads(Path(filename).read_text(encoding="utf-8"))
    # Only shipped named topologies are supported. Do not silently accept broken
    # custom wiring as a successful exercise.
    required = ("bridges", "hosts", "links")
    if not all(key in config for key in required):
        raise ValueError("config needs bridges, hosts, links")
    bridges = config["bridges"]
    if not bridges or len(set(bridges.values())) != len(bridges):
        raise ValueError("bridge ranks must be unique")
    for host in config["hosts"].values():
        if host["switch"] not in bridges or host["vlan"] not in (10, 20):
            raise ValueError("invalid host switch/VLAN")
    for link in config["links"].values():
        ends = link["ends"]
        if len(ends) != 2 or len(set(ends)) != 2 or not set(ends) <= set(bridges):
            raise ValueError("invalid point-to-point link")
        if not set(link["vlans"]) <= {10, 20} or not isinstance(link["up"], bool):
            raise ValueError("invalid trunk VLAN/state")
    if "lacp" in config:
        group = config["lacp"]
        if "po1" not in config["links"] or set(group["modes"]) != set(config["links"]["po1"]["ends"]):
            raise ValueError("LACP endpoints must match po1")
        if not group["members"] or not all(isinstance(up, bool) for up in group["members"].values()):
            raise ValueError("invalid members")
        if not set(group["modes"].values()) <= {"active", "passive"}:
            raise ValueError("invalid LACP mode")
    elif "po1" in config["links"]:
        raise ValueError("po1 needs a LACP group")
    return SwitchLab(config)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="stp.txt or lacp.txt")
    args = parser.parse_args()
    try:
        lab = load_lab(args.config)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"CONFIG ERROR: {error}\n")
    print("SIM v1: in-memory L2 only. Enter help. quit/EOF/Ctrl+C discards changes.")
    while True:
        try:
            line = input("sim> ")
            if line.strip() == "quit":
                return
            for event in lab.execute(line):
                print(event)
        except (EOFError, KeyboardInterrupt):
            print("\nEXIT; no host network changed")
            return
        except (ValueError, KeyError) as error:
            print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
