"""1주차 server.py의 Handler를 허가된 IPv4 주소에 연결하는 학습용 실행기."""

import argparse
import ipaddress
import json
import ssl
from http.server import ThreadingHTTPServer

from server import Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", required=True, help="이 VM에 실제 설정된 IPv4 주소")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--cert", help="TLS 서버 공개 인증서 PEM")
    parser.add_argument("--key", help="공유하지 않는 TLS 서버 개인키 PEM")
    args = parser.parse_args()

    # 전체 인터페이스 대신 관찰할 주소 하나를 고른다. 허가 여부는 실행 전에 확인한다.
    try:
        address = ipaddress.IPv4Address(args.bind)
    except ipaddress.AddressValueError:
        parser.error("--bind requires an IPv4 address")
    if address.is_unspecified or address.is_multicast or address.is_reserved or address.is_link_local:
        parser.error("--bind requires a usable unicast address")
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    if bool(args.cert) != bool(args.key):
        parser.error("--cert and --key must be supplied together")

    context = None
    if args.cert:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        try:
            context.load_cert_chain(args.cert, args.key)
        except (OSError, ssl.SSLError) as error:
            parser.error(f"cannot load TLS files: {error}")

    try:
        with ThreadingHTTPServer((str(address), args.port), Handler) as service:
            if context is not None:
                service.socket = context.wrap_socket(service.socket, server_side=True)
            scheme = "http"
            if context is not None:
                scheme = "https"
            print(json.dumps({"event": "listening", "address": service.server_address,
                              "scheme": scheme}), flush=True)
            service.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("Stopped; listener closed", flush=True)
    except OSError as error:
        parser.exit(1, f"Cannot listen: {error}\n")


if __name__ == "__main__":
    main()
