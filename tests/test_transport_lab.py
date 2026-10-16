"""Run the teaching program over real local sockets, including failure recovery."""
import contextlib
import importlib.util
import io
from pathlib import Path
import socket
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'content/labs/week-04/transport_lab.py'
spec = importlib.util.spec_from_file_location('transport_lab', SCRIPT)
lab = importlib.util.module_from_spec(spec)
previous_bytecode = sys.dont_write_bytecode
try:
    # Imported participant code lives inside the public input directory.
    sys.dont_write_bytecode = True
    spec.loader.exec_module(lab)
finally:
    sys.dont_write_bytecode = previous_bytecode


class TransportLab(unittest.TestCase):
    def command(self, *args):
        return [sys.executable, str(SCRIPT), *args]

    def free_port(self, transport):
        kind = socket.SOCK_STREAM if transport == 'tcp' else socket.SOCK_DGRAM
        with socket.socket(socket.AF_INET, kind) as probe:
            probe.bind(('127.0.0.1', 0))
            return probe.getsockname()[1]

    def test_normal_echo_and_wrong_port_recovery(self):
        for transport in ('tcp', 'udp'):
            with self.subTest(transport=transport):
                port = self.free_port(transport)
                wrong = self.free_port(transport)
                while wrong == port:
                    wrong = self.free_port(transport)
                server = subprocess.Popen(self.command(transport, 'server', '--port', str(port), '--timeout', '5'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    ready = server.stdout.readline()
                    self.assertIn('127.0.0.1', ready)
                    failed = subprocess.run(self.command(transport, 'client', '--port', str(wrong), '--timeout', '0.2'), capture_output=True, text=True, timeout=3)
                    self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
                    self.assertIn('Stopped:', failed.stderr)
                    client = subprocess.run(self.command(transport, 'client', '--port', str(port), '--timeout', '2', '--read-size', '1'), capture_output=True, text=True, timeout=4)
                    self.assertEqual(client.returncode, 0, client.stderr)
                    output, error = server.communicate(timeout=4)
                    self.assertEqual(server.returncode, 0, error)
                    if transport == 'tcp':
                        self.assertIn("b'hellonetwork\\n'", client.stdout)
                        self.assertIn("b'hellonetwork\\n'", output)
                        self.assertEqual(client.stdout.count('TCP chunk:'), 13)
                    else:
                        self.assertEqual(client.stdout.count('UDP app reply:'), 2)
                        self.assertEqual(output.count('UDP datagram'), 2)
                finally:
                    if server.poll() is None:
                        server.kill()
                        server.communicate()

    def test_stream_partial_reads_eof_and_size_limit(self):
        for message, expected in [(b'hello\n', b'hello\n'), (b'hello', ValueError), (b'x' * 65 + b'\n', ValueError)]:
            sender, receiver = socket.socketpair()
            with self.subTest(message=message), sender, receiver:
                sender.sendall(message)
                sender.shutdown(socket.SHUT_WR)
                receiver.settimeout(1)
                with contextlib.redirect_stdout(io.StringIO()):
                    if expected is ValueError:
                        with self.assertRaises(ValueError):
                            lab.read_line(receiver, 3)
                    else:
                        self.assertEqual(lab.read_line(receiver, 3), expected)

    def test_input_errors_fail_before_network_access(self):
        for option, value in [('--port', '1023'), ('--port', '65536'), ('--read-size', '0'), ('--timeout', '0'), ('--timeout', '301'), ('--timeout', 'nan')]:
            with self.subTest(option=option, value=value):
                result = subprocess.run(self.command('tcp', 'client', option, value), capture_output=True, text=True, timeout=3)
                self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
