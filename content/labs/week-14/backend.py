"""1주차 Handler에 식별자·제한된 처리 대기·상태 확인을 붙이는 루프백 실습 서버."""

import argparse
import json
import os
import time
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

from server import Handler


class LabServer(ThreadingHTTPServer):
    # 같은 포트의 기존 실습과 겹쳐 실행하지 않는다.
    allow_reuse_address = os.name != 'nt'


class Backend(Handler):
    def end_headers(self):
        self.send_header('X-Backend', self.server.backend_id)
        super().end_headers()

    def do_GET(self):
        start = time.perf_counter()
        if urlsplit(self.path).path == '/health':
            body = b'ok\n'
            self.send_response(200)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)
        else:
            # 망을 바꾸지 않고 요청 처리 전에 기다린다. /health에는 지연을 넣지 않는다.
            time.sleep(self.server.delay)
            super().do_GET()
        print(json.dumps({'event': 'backend_done', 'backend': self.server.backend_id,
                          'path': self.path, 'elapsed_ms': round((time.perf_counter()-start)*1000, 2)}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', required=True, choices=['a', 'b'])
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--delay', type=float, default=0)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('port must be between 1024 and 65535')
    if not 0 <= args.delay <= 0.5:
        parser.error('delay must be between 0 and 0.5 seconds')
    try:
        with LabServer(('127.0.0.1', args.port), Backend) as service:
            service.backend_id = args.id
            service.delay = args.delay
            print(json.dumps({'event': 'listening', 'backend': args.id,
                              'address': service.server_address, 'delay_s': args.delay}), flush=True)
            service.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('Stopped; listener closed', flush=True)
    except OSError as error:
        parser.exit(1, f'Cannot listen: {error}\n')


if __name__ == '__main__':
    main()
