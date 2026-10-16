"""종료 조건 하나를 바꿔 같은 메시지를 보내고 JSON 결과 한 줄을 기록한다."""

import argparse
import json
import math
import socket
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=18085)
    parser.add_argument('--message', default='hello')
    parser.add_argument('--ending', choices=['line', 'eof', 'hold'], default='line')
    parser.add_argument('--timeout', type=float, default=3)
    args = parser.parse_args()
    data = args.message.encode('utf-8')
    if not 1024 <= args.port <= 65535:
        parser.error('port must be between 1024 and 65535')
    if b'\n' in data or b'\r' in data or len(data) > 256:
        parser.error('message must be at most 256 UTF-8 bytes, without CR or LF')
    if not math.isfinite(args.timeout) or not 0.1 <= args.timeout <= 5:
        parser.error('timeout must be between 0.1 and 5 seconds')
    started = time.monotonic()
    result = {'ending': args.ending, 'outcome': None, 'reply': None}
    try:
        with socket.create_connection(('127.0.0.1', args.port), timeout=args.timeout) as connection:
            if args.ending == 'line':
                data += b'\n'
            connection.sendall(data)
            if args.ending == 'eof':
                # 보내는 방향만 닫는다. 응답은 계속 받을 수 있다.
                connection.shutdown(socket.SHUT_WR)
            reply = bytearray()
            deadline = time.monotonic() + args.timeout
            while b'\n' not in reply:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError()
                connection.settimeout(remaining)
                chunk = connection.recv(64)
                if not chunk:
                    raise EOFError('reply ended before LF')
                reply.extend(chunk)
                if len(reply) > 4096:
                    raise ValueError('reply too long')
            result['reply'] = json.loads(reply.partition(b'\n')[0].decode('utf-8'))
            result['outcome'] = 'reply'
    except TimeoutError:
        result['outcome'] = 'timeout'
    except (OSError, EOFError, ValueError) as error:
        result['outcome'] = 'communication_error'
        result['error'] = type(error).__name__
    result['elapsed_ms'] = round((time.monotonic() - started) * 1000, 2)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['outcome'] == 'reply' and result['reply']['outcome'] == 'frame_ok' else 1


if __name__ == '__main__':
    raise SystemExit(main())
