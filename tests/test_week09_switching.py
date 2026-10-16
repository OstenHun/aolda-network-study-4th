"""Behavior checks for the shipped isolated Week 09 simulator."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

LAB = Path(__file__).resolve().parents[1] / "content/labs/week-09"
SPEC = importlib.util.spec_from_file_location("switch_sim", LAB / "switch_sim.py")
SIM = importlib.util.module_from_spec(SPEC)
BYTECODE_SETTING = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    SPEC.loader.exec_module(SIM)
finally:
    sys.dont_write_bytecode = BYTECODE_SETTING


class SwitchingTests(unittest.TestCase):
    def setUp(self):
        self.lab = SIM.load_lab(LAB / "stp.txt")

    def probe(self, source="A", destination="B", flow=0):
        return self.lab.execute(f"probe {source} {destination} {flow}")[-1]

    def test_source_learning_and_known_destination(self):
        _, first = self.lab.frame("A", "B")
        self.assertIn("FLOOD S2 ingress=host:A", first)
        self.assertEqual(self.lab.fdb["S2", 10, "02:00:00:00:09:01"], "host:A")
        self.assertFalse(any(key[2] == "02:00:00:00:09:02" for key in self.lab.fdb))
        self.lab.frame("B", "A")
        _, last = self.lab.frame("A", "B")
        self.assertIn("UNICAST S2 ingress=host:A", last)

    def test_vlan_broadcast_isolation(self):
        reached, events = self.lab.frame("A", "broadcast")
        self.assertEqual(reached, ["B"])
        self.assertTrue(any("tag=10" in event for event in events))
        self.assertIn("FAIL", self.probe("A", "C"))

    def test_vlan_change_recovery(self):
        self.assertIn("PASS", self.probe())
        self.lab.execute("vlan B 20")
        self.assertEqual(self.lab.fdb, {})
        self.assertIn("FAIL", self.probe())
        self.assertIn("PASS", self.probe("B", "C"))
        self.lab.execute("vlan B 10")
        self.assertIn("PASS", self.probe())
        self.assertIn("FAIL", self.probe("B", "C"))

    def test_stp_roles_and_transition(self):
        roots, costs, roles = self.lab.spanning_tree()
        self.assertEqual(set(roots.values()), {"S1"})
        self.assertEqual(costs["S3"], 1)
        self.assertEqual(roles["S3", "l23"], "blocked")
        self.lab.execute("link l13 down")
        roots, costs, roles = self.lab.spanning_tree()
        self.assertEqual((roots["S3"], costs["S3"], roles["S3", "l23"]), ("S1", 2, "root"))
        events = self.lab.execute("probe A B")
        self.assertTrue(any("TX S2/l23->S3" in event for event in events))
        self.assertIn("PASS", events[-1])
        self.lab.execute("link l13 up")
        self.assertEqual(self.lab.spanning_tree()[2]["S3", "l23"], "blocked")
        self.assertIn("PASS", self.probe())

    def test_disconnected_component_elects_local_root(self):
        self.lab.execute("link l13 down")
        self.lab.execute("link l23 down")
        self.assertEqual(self.lab.spanning_tree()[0]["S3"], "S3")
        self.assertIn("FAIL", self.probe())
        self.lab.execute("reset")
        self.assertIn("PASS", self.probe())

    def test_trunk_admission_does_not_change_common_stp(self):
        before = self.lab.spanning_tree()
        self.lab.execute("allow l13 20")
        self.assertEqual(before, self.lab.spanning_tree())
        self.assertIn("FAIL", self.probe())
        self.lab.execute("allow l13 10,20")
        self.assertIn("PASS", self.probe())

    def test_all_link_combinations_are_loop_free(self):
        from itertools import product
        for states in product(("up", "down"), repeat=3):
            self.lab.reset()
            for name, state in zip(("l12", "l13", "l23"), states):
                self.lab.execute(f"link {name} {state}")
            reached, events = self.lab.frame("A", "broadcast")
            self.assertLessEqual(reached.count("B"), 1)
            self.assertNotIn("C", reached)

    def test_lacp_member_transition_and_hash(self):
        self.lab = SIM.load_lab(LAB / "lacp.txt")
        self.assertEqual(self.lab.active_members(), ["m1", "m2"])
        flow0 = self.lab.execute("probe A B 0")
        flow1 = self.lab.execute("probe A B 1")
        self.assertTrue(any("member=m1" in event for event in flow0))
        self.assertTrue(any("member=m2" in event for event in flow1))
        self.lab.execute("link m1 down")
        self.assertEqual(self.lab.active_members(), ["m2"])
        for flow in (0, 1, 7):
            events = self.lab.execute(f"probe A B {flow}")
            self.assertIn("PASS", events[-1])
            self.assertTrue(any("member=m2" in event for event in events))
            self.assertFalse(any("member=m1" in event for event in events))
        self.lab.execute("link m1 up")
        self.assertEqual(len(self.lab.active_members()), 2)
        self.assertIn("PASS", self.probe())

    def test_lacp_all_down_and_mode_recovery(self):
        self.lab = SIM.load_lab(LAB / "lacp.txt")
        for name in ("m1", "m2"):
            self.lab.execute(f"link {name} down")
        self.assertIn("FAIL", self.probe())
        self.lab.reset()
        self.lab.execute("mode S1 passive")
        self.assertEqual(self.lab.active_members(), [])
        self.assertIn("FAIL", self.probe())
        self.assertTrue(all(self.lab.config["lacp"]["members"].values()))
        self.lab.execute("mode S2 active")
        self.assertIn("PASS", self.probe())
        self.lab.reset()
        self.assertEqual(self.lab.config["lacp"]["modes"]["S1"], "active")

    def test_invalid_commands_are_atomic(self):
        for command in ("vlan B 99", "allow l13 10,99", "link absent down",
                        "mode S1 passive", "probe A unknown", "probe A B -1",
                        "probe A broadcast", "probe A A", "link l13 invalid"):
            before = copy.deepcopy((self.lab.config, self.lab.fdb, self.lab.revision))
            with self.assertRaises(ValueError, msg=command):
                self.lab.execute(command)
            self.assertEqual(before, (self.lab.config, self.lab.fdb, self.lab.revision))

    def test_cli_error_recovery_eof_and_no_config_write(self):
        original = (LAB / "stp.txt").read_bytes()
        result = subprocess.run([sys.executable, str(LAB / "switch_sim.py"), str(LAB / "stp.txt")],
                                input="vlan B 99\nprobe A B\n", text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("ERROR:", result.stdout)
        self.assertIn("PROBE PASS", result.stdout)
        self.assertIn("no host network changed", result.stdout)
        self.assertEqual((LAB / "stp.txt").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
