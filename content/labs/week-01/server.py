"""1주차 실습: 같은 Linux VM 안에서 요청을 받아 응답하는 작은 HTTP 서버."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        # BaseHTTPRequestHandler가 GET 요청을 받으면 이 메서드를 호출한다.
        # 1. 요청 URL을 경로(/echo)와 물음표 뒤의 질의 문자열로 나눈다.
        request_url = urlsplit(self.path)

        # 2. 경로에 따라 응답 상태와 JSON 내용을 정한다.
        if request_url.path == "/echo":
            status_code = 200
            query_parameters = parse_qs(request_url.query)
            # 빈 값은 건너뛴다. 남은 message가 없으면 hello, 여러 개면 첫 값을 쓴다.
            message_values = query_parameters.get("message", ["hello"])
            message = message_values[0]
            response_data = {"message": message}
        else:
            status_code = 404
            response_data = {"error": "not found"}

        # 3. 화면에 보이는 글자와 실제 전송 바이트 수는 다를 수 있다.
        # 한글도 그대로 읽히는 JSON을 만들고 UTF-8 바이트로 바꾼다.
        body = json.dumps(response_data, ensure_ascii=False).encode("utf-8")

        # 4. 상태줄과 헤더를 보낸 뒤 본문을 보낸다.
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # 요청마다 연결을 닫아 실습 로그와 패킷을 구분하기 쉽게 한다.
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

        # 5. 서버에서 관찰한 요청과 응답을 한 줄의 JSON으로 남긴다.
        response_event = {
            "event": "response",
            "client": self.client_address,
            "path": self.path,
            "status": status_code,
            "bytes": len(body),
        }
        print(json.dumps(response_event, ensure_ascii=False), flush=True)

    def log_message(self, format, *args):
        # 기본 접속 로그 대신 위의 JSON 로그를 실습 증거로 사용한다.
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    # 127.0.0.1은 이 VM 안에서만 접근 가능한 루프백 주소다.
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(json.dumps({"event": "listening", "address": server.server_address}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass  # Ctrl+C를 누르면 서버를 종료한다.
