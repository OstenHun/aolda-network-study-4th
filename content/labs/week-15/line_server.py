"""한 연결에서 LF로 끝나는 UTF-8 메시지 하나를 받는 루프백 학습 서버."""

import argparse
import json
import math
import os
import socket
import time


def read_line(connection):
    # recv 크기는 패킷 크기가 아니다. 일부러 3바이트씩 읽어 누적을 관찰한다.
    received = bytearray()
    deadline = time.monotonic() + 2.0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return 'timeout', bytes(received)
        connection.settimeout(remaining)
        try:
            chunk = connection.recv(min(3, 257 - len(received)))
        except TimeoutError:
            return 'timeout', bytes(received)
        print(json.dumps({'event': 'recv', 'bytes': len(chunk), 'hex': chunk.hex()}), flush=True)
        if not chunk:
            return 'eof_incomplete', bytes(received)
        received.extend(chunk)
        if b'\n' in received:
            line, _, _ = received.partition(b'\n')
            if len(line) > 256:
                return 'too_long', bytes(line)
            # 한 연결에 한 메시지만 받는다. 뒤의 바이트는 다음 요청으로 처리하지 않는다.
            return 'frame_ok', bytes(line)
        if len(received) > 256:
            return 'too_long', bytes(received)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=18085)
    parser.add_argument('--delay', type=float, default=0)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('port must be between 1024 and 65535')
    if not math.isfinite(args.delay) or not 0 <= args.delay <= 1:
        parser.error('delay must be between 0 and 1 second')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            if os.name != 'nt':
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('127.0.0.1', args.port))
            listener.listen(1)
            print(json.dumps({'event': 'listening', 'port': args.port}), flush=True)
            while True:
                connection, _ = listener.accept()
                with connection:
                    try:
                        outcome, data = read_line(connection)
                        message = None
                        if outcome == 'frame_ok':
                            try:
                                message = data.decode('utf-8')
                            except UnicodeDecodeError:
                                outcome = 'invalid_utf8'
                        print(json.dumps({'event': 'received', 'outcome': outcome,
                                          'bytes': len(data), 'message': message}, ensure_ascii=False), flush=True)
                        # 수신 로그와 응답 도착은 다르다. 대기 중 클라이언트가 먼저 종료할 수 있다.
                        time.sleep(args.delay)
                        reply = json.dumps({'outcome': outcome, 'message': message}, ensure_ascii=False)
                        connection.settimeout(1.0)
                        connection.sendall((reply + '\n').encode('utf-8'))
                        print(json.dumps({'event': 'reply_written', 'outcome': outcome}), flush=True)
                    except OSError as error:
                        print(json.dumps({'event': 'connection_error', 'error': type(error).__name__}), flush=True)
    except KeyboardInterrupt:
        print('Stopped; sockets closed', flush=True)
    except OSError as error:
        parser.exit(1, f'Cannot listen: {error}\n')


if __name__ == '__main__':
    main()
