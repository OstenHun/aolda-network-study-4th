# 15주차 공식 출처 · 필요한 절부터 읽기

요약: 필수는 Python 소켓의 수신·경계·종료와 HTTP 멱등성의 짧은 지정 범위다. API·시간·curl 문서는 코드가 막힐 때 참조한다. 자체 프로토콜·문항·가공 출력과 공식 문서의 주장 범위를 구별한다.

## 함께 읽을 필수 범위

확인일 2026-10-17. 필수 약10분은 추정이다. 문서 전체와 모든 예제 구현을 요구하지 않는다. 모르는 용어는 [K1\~K3](CONCEPTS.md)로 돌아가 설명한다.

| 공식 자료·정확한 범위 | 함께 찾을 것·용도 | 예상 |
| --- | --- | --- |
| [Python 3.14 Socket HOWTO · Using a Socket](https://docs.python.org/3.14/howto/sockets.html#using-a-socket)의 `Now we come to the major stumbling block`으로 시작하는 문단부터 `The choice is entirely yours`로 끝나는 문단까지. 중간의 HTTP 설명은 아래 한계와 함께 읽음 | 부분 send/recv·0바이트·앱 경계의 선택, A의 누적 이유 | 4분 |
| [socket.recv](https://docs.python.org/3.14/library/socket.html#socket.socket.recv)의 첫 문단, [socket.shutdown](https://docs.python.org/3.14/library/socket.html#socket.socket.shutdown)의 첫 문단 | maximum은 ‘최대’, 빈 bytes와 SHUT_WR의 의미. 수신 종료와 양방향 전체 종료 구별 | 3분 |
| [RFC 9110 §9.2.2 Idempotent Methods](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)의 첫 두 문단과 `A client SHOULD NOT automatically retry`로 시작하는 문단 | 의도한 효과·응답/로그 차이·비멱등 요청의 자동 재시도 조건, Q8 | 3분 |

HOWTO는 소켓 원리의 입문 자료다. 중간의 ‘HTTP가 소켓을 한 번만 쓴다’는 설명을 현대 HTTP 전체에 적용하지 않는다. HTTP/1.1은 지속 연결을 사용할 수 있고 경계 규칙도 따로 있다([RFC 9112 §6](https://www.rfc-editor.org/rfc/rfc9112.html#section-6), [§9.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3)). 이번 LF 소켓과 기존 Handler의 명시적 close 조건으로 한정한다. RFC의 GET 멱등성도 서버가 그 의미대로 구현한다는 전제이며 무제한 재시도를 권하지 않는다.

## 코드·명령을 확인할 참조

| 공식 자료·선택 범위 | 지지하는 내용 |
| --- | --- |
| [socket.sendall](https://docs.python.org/3.14/library/socket.html#socket.socket.sendall), [settimeout](https://docs.python.org/3.14/library/socket.html#socket.socket.settimeout), [Timeouts and the connect method](https://docs.python.org/3.14/library/socket.html#timeouts-and-the-connect-method) | 전송/대기와 처리 완료 구별, 작업별 시간제한·연결 |
| [time.monotonic](https://docs.python.org/3.14/library/time.html#time.monotonic), [sleep](https://docs.python.org/3.14/library/time.html#time.sleep) | 경과 시간·마감/남은 시간, 실제 대기가 길어질 수 있음 |
| [HTTPConnection](https://docs.python.org/3.14/library/http.client.html#http.client.HTTPConnection), [HTTPResponse.read](https://docs.python.org/3.14/library/http.client.html#http.client.HTTPResponse.read) | GET·응답·본문 읽기·소켓 timeout. HTTP 파서는 표준 라이브러리 재사용 |
| [http.server](https://docs.python.org/3.14/library/http.server.html#http.server.BaseHTTPRequestHandler) | 기존 Handler 재사용, 학습용 루프백 서버. 운영 서비스 용도로 확대하지 않음 |
| [curl --max-time](https://curl.se/docs/manpage.html#--max-time), [--fail](https://curl.se/docs/manpage.html#--fail)와 [Exit codes](https://curl.se/docs/manpage.html#EXIT) | 수동 요청 총시간 상한·HTTP 오류 때 종료 정책·연결 실패. --fail을 쓰지 않는 명령의 해석 |

## 자료의 성격과 재사용

공식 문서와 실제 코드 API를 대조해 자체 설명·LF 프로토콜·문항·가공 사례를 만들었다. 외부 코드나 문제 전체를 복제하지 않았다. Python 문서는 PSF License의 공식 참조이고 RFC 원문은 해당 문서의 저작권 고지를 따른다. Python 3.14를 기준으로 공통 API를 읽으며 Linux의 설치 버전은 실행 전에 확인한다. 이번 제공 사례는 실측 로그가 아니다.

[network engineer roadmap](https://roadmap.sh/network-engineer)은 Shell/Scripting·APIs·Automation의 위치를 확인하는 선택 색인이다. 이를 모든 도구 습득이나 기업 공통 기출의 근거로 쓰지 않는다. Ansible·Terraform 실제 자원 변경과 대규모 장비 자동화는 이번 필수에 포함하지 않는다.
