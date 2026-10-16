"""기존 루프백 HTTP GET을 최대 5번 수행한다. 재시도는 하지 않는다."""

import argparse
import http.client
import json
import math
import time


def check_once(port, request_path, timeout, attempt):
    result = {'attempt': attempt, 'path': request_path, 'outcome': None,
              'status': None, 'body': None, 'error': None}
    started = time.monotonic()
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
    try:
        connection.request('GET', request_path, headers={'Connection': 'close'})
        response = connection.getresponse()
        result['status'] = response.status
        body = response.read(65537)
        if len(body) > 65536:
            result['outcome'] = 'body_limit'
        elif response.length not in (None, 0):
            # Content-Length보다 적게 받은 EOF를 정상 응답으로 세지 않는다.
            result['outcome'] = 'incomplete_body'
        else:
            result['body'] = body.decode('utf-8', errors='replace')
            if 200 <= response.status < 300:
                result['outcome'] = 'http_success'
            else:
                result['outcome'] = 'http_error'
    except TimeoutError:
        result['outcome'] = 'timeout'
    except (OSError, http.client.HTTPException) as error:
        result['outcome'] = 'communication_error'
        result['error'] = type(error).__name__
    finally:
        connection.close()
    result['elapsed_ms'] = round((time.monotonic() - started) * 1000, 2)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=18081)
    parser.add_argument('--path', default='/echo?message=w15')
    parser.add_argument('--count', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=1)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or not 1 <= args.count <= 5:
        parser.error('port must be 1024..65535; count must be 1..5')
    if not math.isfinite(args.timeout) or not 0.1 <= args.timeout <= 3:
        parser.error('timeout must be 0.1..3 seconds')
    if not args.path.startswith('/') or args.path.startswith('//') or len(args.path) > 512:
        parser.error('path must start with one slash and be at most 512 characters')
    if any(ord(character) < 33 or ord(character) > 126 for character in args.path):
        parser.error('path must use printable ASCII; percent-encode other characters')
    failed = False
    for attempt in range(1, args.count + 1):
        result = check_once(args.port, args.path, args.timeout, attempt)
        print(json.dumps(result, ensure_ascii=False), flush=True)
        if result['outcome'] != 'http_success':
            failed = True
        if attempt < args.count:
            time.sleep(0.2)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
