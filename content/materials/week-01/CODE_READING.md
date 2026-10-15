# 코드로 따라가는 요청과 응답

요약: 실제 server.py를 요청 읽기·경로 판정·본문 만들기·응답 보내기·로그 남기기 순서로 읽는다. Python 문법을 처음 보는 사람도 출력과 연결할 수 있게 설명하며 Node 클라이언트는 선택으로 다룬다.

## 1. 처음에는 이 질문 하나만 따라가세요

**“내가 보낸 hello가 어디에서 읽혀서 응답에 들어갈까?”** [정상 요청](linux.html)을 한 번 실행한 뒤 2~4절을 약 10~15분 동안 읽습니다. 프로그램을 처음부터 혼자 작성하거나 모든 문법을 외우는 것은 이번 주 목표가 아닙니다.

| 파일·도구 | 하는 일 | 이번에 읽을 범위 |
| --- | --- | --- |
| `server.py` | 요청을 받아 상태와 본문을 정하는 Python 서버 | 필수 실습 파일. 아래 다섯 단계부터 읽기 |
| `curl` | 서버에 요청하고 받은 내용을 보여주는 명령 | 직접 구현할 필요 없이 명령·출력과 코드 연결 |
| `client.mts` | 연결 주소·헤더·본문을 더 나눠 출력하는 Node 클라이언트 | 선택. 기본 실습 후 궁금한 경우에만 읽기 |

```text
셸 B: curl → HTTP GET /echo?message=hello
                        ↓ 같은 Linux 안의 TCP 연결
셸 A: server.py → 경로 확인 → 응답 데이터 → HTTP 200 + JSON 본문
                        ↓
셸 B: curl 화면에 받은 상태·헤더·본문 표시
```

Python의 HTTP 라이브러리가 요청을 받는 일을 맡습니다. 우리 코드는 **요청을 받았을 때 어떤 응답을 만들지**를 정합니다. `/echo`라는 이름은 이 코드가 정한 처리 경로이며 폴더나 파일을 자동으로 열어 주는 기능이 아닙니다.

## 2. Python 문법이 낯설 때 볼 작은 안내

| 코드에서 볼 모양 | 이 파일에서는 이렇게 읽습니다 |
| --- | --- |
| `import json` | Python이 제공하는 JSON 처리 도구 가져오기 |
| `class Handler(BaseHTTPRequestHandler):` | 기본 HTTP 처리 기능을 바탕으로 우리 요청 처리 방법 정의하기 |
| `def do_GET(self):` | GET 요청을 받았을 때 실행할 동작. 이 이름을 보고 HTTP 라이브러리가 호출함 |
| `self.path` | 지금 처리하는 요청의 경로와 쿼리. 예: `/echo?message=hello` |
| `status_code = 200` | 변수에 값 저장. 오른쪽 값을 왼쪽 이름으로 기억하기 |
| `request_url.path == "/echo"` | 두 값이 같은지 비교. 위의 `=`와 역할이 다름 |
| `if ...:` / `else:` | 조건이 맞으면 첫 블록, 아니면 다른 블록 실행 |
| `{"message": message}` | `message`라는 이름과 변수의 값을 짝지은 딕셔너리 |
| `["hello"]` / `[0]` | 값의 목록 / 그 목록의 첫 값. Python은 위치를 0부터 셈 |
| `.get("message", ["hello"])` | message 항목이 있으면 그 목록, 없으면 기본 목록 사용 |

`self`는 **지금 요청을 처리하는 객체 자신**을 가리킵니다. 요청마다 경로·클라이언트 주소 같은 정보가 그 객체에 있습니다. 들여쓰기는 같은 동작 묶음을 표시하므로 코드를 바꿀 때 그대로 유지합니다. `#` 뒤는 사람이 읽는 주석이며 실행되지 않습니다.

## 3. hello 요청을 다섯 단계로 따라가기

아래 값은 코드를 설명하는 예시입니다. 실제 실행 결과는 [개인 실습 기록](../week-01-prestudy.html#start)이나 별도 증거 파일에 남기고, 함께 확인한 근거 위치와 바뀐 설명은 [팀 활동](worksheet.html)에 적습니다.

| 순서 | 코드에서 찾을 부분 | hello 요청에서 일어나는 일 |
| --- | --- | --- |
| ① 요청 읽기 | `urlsplit(self.path)` | 경로 `/echo`와 쿼리 `message=hello`를 나눔 |
| ② 응답 결정 | `if request_url.path == "/echo":` | 맞으면 상태 200, message를 읽어 `{"message": "hello"}` 데이터 준비. 다른 경로면 상태 404와 오류 데이터 준비 |
| ③ 전송할 본문 만들기 | `json.dumps(...)`와 `.encode("utf-8")` | Python 데이터를 JSON 문자열로 만든 뒤 전송할 바이트로 변환 |
| ④ 응답 보내기 | `send_response`부터 `wfile.write`까지 | 상태·헤더를 정하고 빈 줄 뒤에 본문 바이트를 보냄 |
| ⑤ 서버 기록 남기기 | `response_event`와 `print(...)` | 서버 터미널에 요청한 쪽·경로·상태·본문 크기 출력 |

②에서 `parse_qs`는 `message=hello`를 `{"message": ["hello"]}`처럼 읽습니다. 같은 이름이 여러 번 올 수 있어 값이 목록입니다. 이 키트는 **빈 값은 건너뛰고, 남은 첫 message를 사용하며, 없으면 hello**를 사용합니다. 예를 들어 `/echo`, `/echo?message=`, `/echo?message=first&message=second`의 메시지는 각각 `hello`, `hello`, `first`입니다.

③의 딕셔너리·JSON 문자열·바이트는 서로 다른 형태입니다. Python 내부에서는 딕셔너리로 다루고, 통신할 때는 JSON 형식의 글자를 UTF-8 바이트로 보냅니다. 한글은 글자 수와 바이트 수가 다를 수 있어 `Content-Length`에는 <strong>변환한 뒤의 <code>len(body)</code></strong>를 사용합니다. 이 키트의 `{"message": "hello"}` 본문은 공백을 포함해 20바이트입니다.

## 4. 코드와 터미널 출력 연결하기

| 코드 | curl에서 찾아볼 결과 |
| --- | --- |
| `self.send_response(status_code)` | `< HTTP/1.1 200 OK` 또는 `< HTTP/1.1 404 Not Found` |
| `self.send_header("Content-Type", ...)` | 받은 본문이 JSON·UTF-8이라는 헤더 |
| `self.send_header("Content-Length", str(len(body)))` | 본문 바이트 수. HTTP 헤더 전체의 크기가 아님 |
| `self.send_header("Connection", "close")` | 이번 키트는 응답 뒤 연결을 닫겠다는 안내 |
| `self.end_headers()` | 상태·헤더 다음에 빈 줄을 넣고 헤더 전송을 마침 |
| `self.wfile.write(body)` | `{"message": "hello"}` 또는 오류 본문 |

`send_response`와 `send_header`는 보낼 헤더를 준비하고 `end_headers`에서 보냅니다. 그러므로 헤더 설정 순서 뒤에 `end_headers()`, 그다음에 본문 쓰기가 옵니다. 실제 HTTP 메시지에는 curl의 표시 기호 `<`가 들어 있지 않습니다.

**`print`는 네트워크로 응답을 보내는 코드가 아닙니다.** `print`가 남긴 `event`, `client`, `path`, `status`, `bytes`는 셸 A의 로그이고, 클라이언트로 보내는 JSON은 ②에서 만든 `response_data`입니다. 같은 상태 값을 사용하지만 기록되는 위치와 목적이 다릅니다.

`log_message`는 Python의 기본 접속 로그 대신 실습용 JSON 로그를 보이게 하는 부분입니다. 처음에는 바꿀 필요가 없습니다. 이 JSON 로그도 상대가 모든 데이터를 읽었다는 확인서는 아니므로 실제 curl 출력과 함께 대조합니다.

## 5. 실제 서버 파일 읽기

[server.py 내려받기](../../labs/week-01/server.py). 아래 펼침에는 공유 키트와 같은 파일의 코드가 들어 있습니다. 설명만 읽고 이해가 안 되는 부분은 해당 이름을 코드에서 찾아보세요.

<!-- SERVER_SOURCE -->

실행 순서는 파일의 위에서 아래로 한 번만 흐르는 것과 다릅니다. 먼저 import·클래스 정의를 읽고, 맨 아래 `if __name__ == "__main__":`에서 서버를 시작합니다. **클래스를 정의한 시점에는 `do_GET`의 본문이 실행되지 않습니다.** 이후 GET 요청이 들어올 때마다 라이브러리가 `do_GET`을 호출합니다.

맨 아래에서 `--port`는 명령줄로 받은 서버 포트이고 생략하면 8080입니다. `127.0.0.1`에 바인딩하므로 같은 Linux 안에서 통신합니다. `serve_forever()`가 요청을 기다리는 동안 셸 A는 그대로 두고 셸 B에서 curl을 실행합니다. A에서 Ctrl+C를 누르면 `KeyboardInterrupt`를 처리하고 서버를 닫습니다. `with`는 그 블록을 나갈 때 서버 자원을 정리합니다.

## 6. 코드의 뜻을 확인하는 작은 문제

먼저 예상하고, 한 번에 조건 하나만 바꿉니다. 기본 코드를 보관한 뒤 자기 실습 사본을 사용하세요. 서버 파일을 수정했다면 실행 중인 서버를 Ctrl+C로 종료하고 다시 시작해야 바뀐 코드가 적용됩니다.

1. 코드는 그대로 두고 URL의 `hello`만 `again`으로 바꿉니다. 코드의 어느 변수와 응답의 어느 부분이 바뀔까요?
2. 코드는 그대로 두고 `/missing`을 요청합니다. `else` 블록이 실행되는 이유와, 이때도 응답을 보내는 부분이 실행되는지 설명하세요.
3. 선택: **서버 코드의 기본 메시지 `hello` 하나만 `hi`로 바꿉니다.** `/echo`로 요청한 뒤, `/echo?message=hello`로 요청하면 각각 무엇이 나올까요? 확인 후 기본 코드를 복구하고 재시작하세요.

풀이 뒤 확인: 1번은 읽은 message와 응답 본문이 바뀌고 서버 포트는 유지됩니다. 2번은 경로가 `/echo`와 달라 상태 404와 오류 본문을 만들고 같은 응답 전송 부분을 실행합니다. 3번의 메시지는 차례로 `hi`, `hello`입니다. URL에 명시한 값은 기본값보다 우선하기 때문입니다.

## 7. 선택 — Node 클라이언트의 읽는 순서

기본 실습은 curl이면 충분합니다. Node가 이미 준비되어 있고 <strong>“받은 본문을 프로그램에서는 어떻게 읽을까?”</strong>가 궁금할 때 봅니다. [키트 실행 안내](../../labs/week-01/README.md)의 명령을 사용합니다.

`callback`(콜백)은 어떤 일이 발생했을 때 실행하도록 넘겨 둔 함수입니다. `response.on("data", ...)`는 “데이터가 도착하면 이 함수를 실행해 달라”는 등록입니다. 파일에 적힌 순서대로 응답·연결·오류 로그가 모두 즉시 출력되는 것이 아닙니다.

```text
성공할 때의 대표 순서:
request(요청 시작) → connected(TCP 연결) → response(상태·헤더 받음)
  → data(본문 일부를 받음, 여러 번일 수 있음) → end(본문 읽기 끝) → body 로그
```

코드는 `data` 이벤트마다 본문을 모으고 `end`에서 모인 본문을 한 번 출력합니다. data 덩어리 하나가 TCP 패킷 하나라는 뜻은 아닙니다. TCP 패킷의 경계와 프로그램에 전달되는 데이터 묶음은 같다고 가정하지 않습니다.

| 코드·이벤트 | 왜 필요한가 |
| --- | --- |
| `process.argv[2]` | 명령 뒤에 쓴 URL을 읽음. 없으면 기본 실습 URL 사용 |
| `get(target, { agent: false }, ...)` | GET 요청 시작. 이 키트에서는 연결을 재사용하지 않고 관찰 |
| `setEncoding("utf8")` | 받은 본문을 UTF-8 문자열로 읽음 |
| `body += chunk` | 여러 번 올 수 있는 본문 조각을 순서대로 이어 붙임 |
| `socket.once("connect", ...)` | 연결된 뒤 실제 local·remote IP와 포트를 기록 |
| `setTimeout` / `clearTimeout` | 요청이 끝없이 기다리지 않게 3초 제한을 걸고 완료·오류 때 타이머 정리 |
| `process.exitCode` | 프로그램이 끝날 때 셸에 보고할 결과. 정상 0, HTTP 400 이상 2, 연결·전송 오류 1이라는 자체 규칙 |

`elapsed_ms`는 이 프로그램이 요청 시작부터 잰 시간입니다. 서버 처리·실행 비용도 포함하며 순수 네트워크 지연은 아닙니다. 404에서는 HTTP 응답을 받은 뒤 종료 코드 2를 정합니다. `network_error`는 연결·전송·시간 제한 오류이며 응답을 얼마나 받았는지는 실제 로그를 함께 봅니다.

[client.mts 내려받기](../../labs/week-01/client.mts). TypeScript의 `: string`, `: object` 등은 값의 종류를 표시합니다. 이 실행 방식에서는 표시를 제거해 실행하므로 타입 오류를 자동 검사해 준다는 뜻은 아닙니다.

<!-- CLIENT_SOURCE -->

## 다음 행동과 참고

코드에서 상태를 정하는 곳, 본문을 보내는 곳, 서버 로그를 남기는 곳을 가리킬 수 있다면 [Linux 실습](linux.html)으로 돌아가 직접 확인합니다. 설명을 서로 대조할 때는 [팀 활동](worksheet.html)을 사용합니다. 자세한 소켓 구현·스레드 원리·TypeScript 전체 문법은 이번 필수 범위가 아닙니다.

- [Python HTTP 서버](https://docs.python.org/3/library/http.server.html): `BaseHTTPRequestHandler`, `do_GET`, 헤더·본문 처리.
- [Python URL·쿼리 해석](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs): 경로 분리, 쿼리 목록과 빈 값 처리.
- [Node HTTP](https://nodejs.org/api/http.html#httpgetoptions-callback): 요청·응답 이벤트. 실행한 Node 버전의 문서와 함께 확인.

본문의 코드 흐름·예시·질문은 이 키트를 설명하기 위해 작성했습니다. 실제 Linux 실행 결과는 별도로 확인합니다.
