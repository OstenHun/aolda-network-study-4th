"""Loopback HTTP/1.1 teaching server; not a production server."""

import argparse
import itertools
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class StudyServer(ThreadingHTTPServer):
    # Each accepted connection gets one id, even if the OS reuses a file descriptor.
    connection_ids = itertools.count(1)
    daemon_threads = True

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(5)
        if self.tls_context is not None:
            try:
                connection = self.tls_context.wrap_socket(connection, server_side=True)
            except OSError:
                connection.close()
                raise
        return connection, address


class StudyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        self.connection_id = next(self.server.connection_ids)

    def do_GET(self):
        # The representation is fixed. This server checks one exact ETag value,
        # rather than implementing the complete HTTP conditional-request grammar.
        etag = '"study-v1"'
        status = 200
        body = b"study representation v1\n"
        if self.path not in ("/resource", "/close"):
            status = 404
            body = b"not found\n"
        elif self.headers.get("If-None-Match") == etag:
            status = 304
            body = b""

        if self.path == "/close" or self.headers.get("Connection", "").lower() == "close":
            self.close_connection = True

        self.send_response(status)
        self.send_header("X-Connection-ID", str(self.connection_id))
        if status != 404:
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", "max-age=0, must-revalidate")
        if status != 304:
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
        # A 304 has no message content; its framing ends after the headers.
        if self.close_connection:
            self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)
        print(f"connection={self.connection_id} path={self.path} status={status}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8086)
    parser.add_argument("--cert", help="TLS server certificate PEM")
    parser.add_argument("--key", help="TLS private key PEM, kept outside public files")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    if bool(args.cert) != bool(args.key):
        parser.error("--cert and --key must be supplied together")

    context = None
    if args.cert:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_alpn_protocols(["http/1.1"])
        try:
            context.load_cert_chain(args.cert, args.key)
        except (OSError, ssl.SSLError) as error:
            parser.error(f"cannot load TLS files: {error}")

    try:
        with StudyServer(("127.0.0.1", args.port), StudyHandler) as server:
            server.tls_context = context
            scheme = "https" if context else "http"
            print(f"Listening: {scheme}://127.0.0.1:{args.port}; Ctrl+C stops", flush=True)
            server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("Stopped; listener closed", flush=True)
    except OSError as error:
        parser.exit(1, f"Cannot listen: {error}\n")


if __name__ == "__main__":
    main()
