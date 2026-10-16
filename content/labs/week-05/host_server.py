"""Loopback-only HTTP example: compare the URL name while keeping the IP fixed."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer


class HostHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Host includes the explicit non-default port used in the URL.
        expected_host = f"lab.test:{self.server.server_port}"
        received_host = self.headers.get("Host", "")
        if received_host != expected_host:
            status = 421
            message = "unexpected Host"
        elif self.path != "/":
            status = 404
            message = "path not found"
        else:
            status = 200
            message = "name matched"

        body = f"{message}\nHost={received_host}\n".encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18405)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")

    try:
        # Bind only to this host; a second VM cannot connect to this listener.
        with HTTPServer(("127.0.0.1", args.port), HostHandler) as server:
            server.timeout = 60
            print(f"Listening on 127.0.0.1:{args.port}; Ctrl+C to stop", flush=True)
            while True:
                server.handle_request()
    except KeyboardInterrupt:
        print("Stopped; listener closed")
    except OSError as error:
        parser.exit(1, f"Server error: {error}\n")


if __name__ == "__main__":
    main()
