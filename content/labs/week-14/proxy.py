"""고정된 두 루프백 서버에만 GET을 전달하는 학습용 프록시."""

import argparse
import http.client
import json
import os
from pathlib import Path
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

BACKENDS = {'a': 18081, 'b': 18082}


class LabServer(ThreadingHTTPServer):
    # Linux에서는 종료 직후 재시작을 허용하고 Windows에서는 중복 바인딩을 막는다.
    allow_reuse_address = os.name != 'nt'


def enabled_backends(path):
    # 매 요청마다 설정을 읽어 재시작 없이 한 서버를 제외·복귀시킨다.
    names = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(names, list) or not names or any(name not in BACKENDS for name in names):
        raise ValueError('expected a non-empty array containing a and/or b')
    if len(set(names)) != len(names):
        raise ValueError('duplicate backend')
    return names


def request_backend(name, path, timeout):
    connection = http.client.HTTPConnection('127.0.0.1', BACKENDS[name], timeout=timeout)
    try:
        connection.request('GET', path, headers={'Connection': 'close'})
        response = connection.getresponse()
        body = response.read(65537)
        if len(body) > 65536:
            raise ValueError('backend body exceeds 64 KiB')
        return response.status, body, response.getheader('X-Backend', 'unknown')
    finally:
        connection.close()


class Proxy(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def reply(self, status, body, backend='none'):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Backend', backend)
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        start = time.perf_counter()
        status, backend = 503, 'none'
        try:
            names = enabled_backends(self.server.config)
            health = {}
            # 요청 시점에 두 서버를 확인한다. 주기적 감시나 운영용 LB는 아니다.
            for name in BACKENDS:
                try:
                    code, _, identity = request_backend(name, '/health', 0.5)
                    health[name] = code == 200 and identity == name
                except (OSError, http.client.HTTPException, ValueError):
                    health[name] = False
            eligible = [name for name in names if health[name]]
            path = urlsplit(self.path)
            if path.path == '/status':
                status = 200
                body = json.dumps({'enabled': names, 'health': health, 'eligible': eligible}).encode()
            elif path.path != '/echo':
                status = 404
                body = b'{"error":"not found"}'
            elif not eligible:
                body = b'{"error":"no healthy enabled backend"}'
            else:
                with self.server.selection_lock:
                    backend = eligible[self.server.next_index % len(eligible)]
                    self.server.next_index += 1
                try:
                    # 실패한 실제 요청을 다른 서버에 자동 재전송하지 않는다.
                    status, body, identity = request_backend(backend, self.path, 2)
                    if identity != backend:
                        raise ValueError('backend identity mismatch')
                except (OSError, http.client.HTTPException, ValueError):
                    status = 502
                    body = b'{"error":"selected backend request failed"}'
            self.reply(status, body, backend)
        except (BrokenPipeError, ConnectionResetError):
            # 클라이언트가 먼저 닫아도 서버 전체를 중단하지 않는다.
            pass
        except (OSError, ValueError, TypeError):
            status = 503
            self.reply(status, b'{"error":"invalid or unreadable config"}')
        finally:
            print(json.dumps({'event': 'proxy_done', 'path': self.path, 'status': status,
                              'backend': backend, 'elapsed_ms': round((time.perf_counter()-start)*1000, 2)}), flush=True)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--port', type=int, default=18080)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or args.port in BACKENDS.values():
        parser.error('choose a non-backend port between 1024 and 65535')
    try:
        enabled_backends(args.config)
    except (OSError, ValueError, TypeError) as error:
        parser.error(f'invalid config: {error}')
    try:
        with LabServer(('127.0.0.1', args.port), Proxy) as service:
            service.config = args.config
            service.selection_lock = threading.Lock()
            service.next_index = 0
            print(json.dumps({'event': 'listening', 'address': service.server_address}), flush=True)
            service.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('Stopped; listener closed', flush=True)
    except OSError as error:
        parser.exit(1, f'Cannot listen: {error}\n')


if __name__ == '__main__':
    main()
