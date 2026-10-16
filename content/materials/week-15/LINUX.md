# 15주차 실습 · 종료 조건과 자동 기록을 직접 비교하기

요약: 루프백 소켓의 종료 입력을 한 가지 바꿔 메시지 완료·EOF를 비교하고 원복한다. 기존 HTTP 서버의 200·404·중지·복구를 수동 요청과 최대 5회 자동 기록으로 대조한다. 코드·출력·정리 순서를 함께 읽는다.

## 준비와 실행 위치

본인에게 허가된 기존 Linux VM 한 대, Python 3.10 이상·curl·ss, 본인 셸 두 개를 사용한다. 모든 명령은 **같은 VM의 같은 실습 폴더**에서 실행한다. sudo나 패키지 설치·방화벽/관리 SSH 변경은 필요하지 않다. 아래 파일을 개인 폴더에 내려받거나 전달한다. 서로 다른 주차의 파일도 이 폴더에 함께 둔다.

- <a download href="../../labs/week-15/line_server.py">line_server.py 내려받기</a> · <a download href="../../labs/week-15/line_client.py">line_client.py 내려받기</a>
- <a download href="../../labs/week-15/check_http.py">check_http.py 내려받기</a> · <a download href="../../labs/week-01/server.py">기존 1주 server.py 내려받기</a>
- <a download href="../../labs/week-15/observations.txt">가공 관찰 사례 내려받기</a>

```bash
python3 --version
curl --version
command -v ss
python3 -m py_compile line_server.py line_client.py check_http.py server.py
ss -ltn 'sport = :18085'
ss -ltn 'sport = :18081'
```

두 포트에 기존 리스너가 있으면 타인의 프로세스를 종료하지 않는다. 다른 미사용 비특권 포트를 정해 서버·클라이언트·curl의 포트를 모두 맞춘다. 파일이 없거나 도구/접속이 안 되면 제공 사례로 분석하고 직접 수행은 보충한다. 루프백 주소를 공인 주소로 바꿀 필요는 없다.

<span id="socket-lab"></span>

## 실험 A · 같은 본문에서 종료 조건만 바꾸기

### A1. 정상 기준을 본다

셸 A에서 서버를 전경으로 실행한다. 4주차 `transport_lab.py`의 LF 누적 방식을 이어 수신 마감·종료 판정을 분리한 예제다. 연결마다 최대 3바이트씩 읽고 LF를 찾는다. 서버는 Ctrl+C로 끝낼 때까지 여러 연결을 순서대로 받는다.

```bash
python3 -u line_server.py --port 18085
```

셸 B에서 본문은 `hello`로 고정한다. 출력 파일은 본인 폴더에 남기며 `>`는 같은 이름의 파일을 덮어쓴다. 보존할 파일이 있으면 이름을 바꾼다.

```bash
python3 line_client.py --port 18085 --message hello --ending line > socket-normal.jsonl
echo "exit=$?"
cat socket-normal.jsonl
```

정상 기준은 종료 코드 0, 클라이언트 `outcome=reply`·응답 `frame_ok`·message `hello`다. 서버의 여러 `recv` 길이를 합쳐 LF까지 6바이트인지 확인한다. 호출 길이/횟수를 TCP 세그먼트 수로 옮겨 적지 않는다.

### A2. 종료 입력 하나를 바꾼 뒤 원복한다

바꿀 입력은 **`--ending line`을 `--ending eof`로** 한 가지다. 코드에서 이 인자가 `shutdown(SHUT_WR)`로 이어지는 위치를 짚고 예상한 뒤 실행한다. 본문·포트·서버 코드는 유지한다.

```bash
python3 line_client.py --port 18085 --message hello --ending eof > socket-eof.jsonl
echo "exit=$?"
cat socket-eof.jsonl
python3 line_client.py --port 18085 --message hello --ending line > socket-restored.jsonl
echo "exit=$?"
cat socket-restored.jsonl
```

`eof`에서는 서버 `recv`에 0바이트가 나타나고 `eof_incomplete`, 클라이언트 종료 코드 1을 예상한다. 응답을 받았지만 LF 경계를 충족하지 못했다는 뜻이다. 복구는 첫 명령과 같은 `line` 입력으로 다시 `frame_ok`·종료 0을 확인한다. 세 파일과 같은 요청의 서버 `received` 로그를 대조하고, 경계·EOF 분기·시간제한 분기를 자기 말로 설명한다.

### A3. 시간이 남으면 한 조건만 더 비교한다

```bash
python3 line_client.py --port 18085 --message hello --ending hold
```

서버 수신 시작 약 2초 뒤 응답 안의 `timeout`을 예상한다. 클라이언트의 기본 응답 대기 3초보다 짧기 때문이다. `reply.outcome=timeout`은 **서버가 보낸 판정**, 최상위 `outcome=timeout`은 **클라이언트의 대기 초과**다. OS 지연으로 정확한 시간은 달라질 수 있다.

추가 선택: 셸 A 서버를 Ctrl+C로 끝내고 `--delay 0.8`을 붙여 다시 실행한다. 셸 B의 `line` 요청에 `--timeout 0.2`만 붙인다. 클라이언트 timeout과 서버 `received=frame_ok`가 함께 가능한지 본다. 서버 `reply_written`이 보여도 클라이언트 수신을 보장하지 않는다. 대기 종료 뒤 서버를 Ctrl+C로 끝내고 **delay 없이 재시작 → 원래 line 명령 → 정상**을 확인한다. 이 예제는 영구적인 업무 변경을 하지 않으며 멱등성은 [교재의 가공 사례](CONCEPTS.md#W15-K3)로 설명한다.

A를 끝내면 셸 A에서 Ctrl+C로 자기 서버를 닫고 `ss -ltn 'sport = :18085'`로 리스너가 사라졌는지 확인한다.

<span id="http-lab"></span>

## 실험 B · 수동 관찰과 자동 기록을 같은 기준으로 비교하기

### B1. 기존 서비스에서 200과 404를 구별한다

셸 A에서 기존 1주 서버를 실행한다.

```bash
python3 -u server.py --port 18081
```

셸 B에서 각 curl 명령 직후 종료 코드를 읽는다. `--noproxy '*'`는 이 루프백 요청이 프록시 설정을 거치지 않도록 한다. `--fail`은 쓰지 않는다.

```bash
curl --noproxy '*' -sS -i --connect-timeout 1 --max-time 3 'http://127.0.0.1:18081/echo?message=w15'
echo "exit=$?"
curl --noproxy '*' -sS -i --connect-timeout 1 --max-time 3 'http://127.0.0.1:18081/missing'
echo "exit=$?"
python3 check_http.py --port 18081 --path '/echo?message=w15' --count 3 > http-normal.jsonl
echo "exit=$?"
cat http-normal.jsonl
python3 check_http.py --port 18081 --path '/missing' --count 3 > http-404.jsonl
echo "exit=$?"
cat http-404.jsonl
```

정상은 `200`·`{"message": "w15"}`와 자동 `http_success` 3줄·종료 0이다. 없는 경로는 curl에 `404`·오류 JSON이 보이며 curl 종료 코드는 0일 수 있다. 자동은 `http_error`·404를 3줄 기록하고 종료 1이다. **도구마다 종료 코드 정책이 다르므로 상태·본문·서버 로그까지 비교한다.** 수동 1회와 자동 3회는 서로 다른 요청이며 서버에는 경로별 4개의 응답 로그가 생긴다.

### B2. 같은 정상 입력으로 중지·복구를 비교한다

변경은 셸 A에서 **자기 server.py를 Ctrl+C로 중지**하는 한 가지다. 셸 B에서 같은 정상 URL/경로를 반복한다.

```bash
curl --noproxy '*' -sS -i --connect-timeout 1 --max-time 3 'http://127.0.0.1:18081/echo?message=w15'
echo "exit=$?"
python3 check_http.py --port 18081 --path '/echo?message=w15' --count 3 > http-stopped.jsonl
echo "exit=$?"
cat http-stopped.jsonl
ss -ltn 'sport = :18081'
```

리스너가 없다면 연결 실패·curl 비0·자동 `communication_error`/`status=null`과 종료 1을 예상한다. OS의 연결 거절 대기나 정책에 따라 `timeout`이 먼저 기록될 수도 있다. 다른 프로세스가 포트를 차지했으면 이 예상과 다를 수 있으므로 리스너를 확인한다. 응답이 없다는 이유만으로 특정 방화벽이나 DNS를 원인으로 확정하지 않는다.

복구는 셸 A에서 첫 명령 그대로 서버를 재시작하는 것이다. 셸 B에서 정상 curl과 자동 3회 명령을 다시 실행하되 자동 출력은 `http-restored.jsonl`에 저장한다. 200·message·`http_success`·종료 0과 서버 로그를 다시 확인한다. 정상/중지/복구의 입력과 횟수는 같아야 한다. 각 3회의 시간만으로 p99·용량·가용성 비율을 일반화하지 않는다.

### B3. 비교를 마치고 정리한다

수동 상태·본문·종료 코드, 자동 `attempt/status/outcome/error/elapsed_ms`, 같은 경로의 서버 로그를 대응한다. 자동 점검이 빠뜨린 관찰이 있는지 설명한다. [가공 사례](../../labs/week-15/observations.txt)의 숫자를 본인 결과로 복사하지 않는다. 서버를 Ctrl+C로 종료하고 두 포트의 리스너가 없어졌는지 확인한다. 실행한 명령·출력과 복구 근거는 개인 파일에 한 번 보관한다.

<span id="code-reading"></span>

## 코드 읽기 지도

| 파일·단계 | 입력 → 판단 → 실행 → 출력 | 읽을 문법·실패/정리 |
| --- | --- | --- |
| `line_client.py` main 앞부분 | 인자 → UTF-8 길이/종료 조건 검증 → 연결·sendall | argparse는 잘못된 인자를 종료 2로 거절. bytes와 str 구별 |
| client 중간 | line이면 LF 추가, eof이면 SHUT_WR, hold이면 둘 다 안 함 → 응답 누적 | `with`가 정상·오류 때 소켓 닫음. 바꿀 입력은 ending 한 개 |
| `line_server.py` read_line | recv(최대3) → 누적 → LF/EOF/257바이트/마감 판정 | bytearray는 수정 가능한 바이트 배열. partition으로 첫 LF 분리, `b''`와 빈 문자열 구별 |
| server main | 완성한 본문 디코딩 → received 로그 → 선택 대기 → JSON 응답 | UnicodeDecodeError 분리, OSError 로그, Ctrl+C로 리스너/연결 정리 |
| `check_http.py` check_once | 새 GET → 상태/본문 확인 → 오류 분류 → 한 결과 반환 | `finally`는 실패에도 close. 64KiB 상한·잘린 Content-Length 검사 |
| check main | count 1\~5 검증 → 순서대로 호출·출력 → 0.2초 간격 | 한 번이라도 성공 이외면 최종 종료 1. 실패를 성공으로 바꾸는 재시도 없음 |

Python의 `None`은 JSON의 `null`로 기록된다. `try/except`는 예상 실패를 분류하고, `raise SystemExit(main())`는 반환한 수를 셸 종료 코드로 전달한다. `time.monotonic()`의 차이는 벽시계 조정에 덜 영향을 받는 경과 시간이며 실제 시각을 나타내지 않는다. 서버 수신 마감과 HTTP의 개별 소켓 대기 제한은 다르다.

자기 말로 확인한다: LF 전에 EOF가 오면 어느 분기로 가는가? 한글이 recv 사이에 나뉘어도 왜 디코딩이 가능한가? HTTP 404가 자동 종료 1이어도 어떤 통신은 이미 성공했는가? [복습](REVIEW.md)과 [공식 근거](SOURCES.md)로 이어 간다.
