"""Small loopback TCP/UDP comparison. No network configuration changes."""
import argparse
import socket
import sys

HOST = "127.0.0.1"
PARTS = (b"hello", b"network\n")


def read_line(connection, read_size):
    """The application, rather than TCP, defines newline as the message end."""
    message = b""
    while not message.endswith(b"\n"):
        chunk = connection.recv(read_size)
        print("TCP chunk:", repr(chunk), flush=True)
        if not chunk:
            raise ValueError("EOF before newline: incomplete application message")
        message += chunk
        if len(message) > 64:
            raise ValueError("message exceeds this example's 64-byte limit")
    return message


def run_tcp(options):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as endpoint:
        endpoint.settimeout(options.timeout)
        if options.role == "server":
            # Reuse supports a repeat after our own closed TCP listener.
            endpoint.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            endpoint.bind((HOST, options.port))
            endpoint.listen(1)
            print("TCP LISTEN", endpoint.getsockname(), flush=True)
            connection, peer = endpoint.accept()
            with connection:
                connection.settimeout(options.timeout)
                print("TCP accepted", peer, flush=True)
                message = read_line(connection, options.read_size)
                connection.sendall(message)
                print("TCP app message:", repr(message), flush=True)
        else:
            endpoint.connect((HOST, options.port))
            print("TCP local", endpoint.getsockname(), "peer", endpoint.getpeername(), flush=True)
            for part in PARTS:
                endpoint.sendall(part)
            message = read_line(endpoint, options.read_size)
            if message != b"".join(PARTS):
                raise ValueError("unexpected TCP echo")
            print("TCP app reply:", repr(message), flush=True)


def run_udp(options):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as endpoint:
        endpoint.settimeout(options.timeout)
        if options.role == "server":
            endpoint.bind((HOST, options.port))
            print("UDP bound", endpoint.getsockname(), flush=True)
            # Each recvfrom reads one datagram. 64 fits both fixed messages.
            for number in range(2):
                message, peer = endpoint.recvfrom(64)
                print("UDP datagram", number + 1, repr(message), "from", peer, flush=True)
                endpoint.sendto(message, peer)
        else:
            for part in PARTS:
                endpoint.sendto(part, (HOST, options.port))
                print("UDP sent", repr(part), "local", endpoint.getsockname(), flush=True)
                message, peer = endpoint.recvfrom(64)
                if peer != (HOST, options.port) or message != part:
                    raise ValueError("unexpected UDP echo or peer")
                print("UDP app reply:", repr(message), "from", peer, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transport", choices=("tcp", "udp"))
    parser.add_argument("role", choices=("server", "client"))
    parser.add_argument("--port", type=int, default=18404)
    parser.add_argument("--read-size", type=int, choices=range(1, 65), default=3)
    parser.add_argument("--timeout", type=float, default=60)
    options = parser.parse_args()
    if not 1024 <= options.port <= 65535:
        parser.error("--port must be between 1024 and 65535")
    if not 0 < options.timeout <= 300:
        parser.error("--timeout must be greater than 0 and at most 300 seconds")
    try:
        if options.transport == "tcp":
            run_tcp(options)
        else:
            run_udp(options)
    except (OSError, ValueError) as error:
        print("Stopped:", error, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Stopped by Ctrl+C; sockets closed.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
