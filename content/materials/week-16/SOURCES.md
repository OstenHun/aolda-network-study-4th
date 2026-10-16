# 16주차 공식 출처 · 관찰의 범위를 대조하기

요약: 필수는 HTTP404의 의미와 Python HTTPConnection의 대기 제한을 짧게 읽는다. ss·curl·소켓·성능 원리는 필요한 때 앞 교재와 공식 절로 돌아간다. 진단 절차·문항·계산은 자체 구성이고 제공 분석과 실측을 구별한다.

## 함께 읽을 필수 범위

확인일 2026-10-17. 약7분은 추정이며 문서 전체를 읽거나 새 도구를 모두 익히는 과제가 아니다. 이번 실습의 주입 원인을 찾는 정답표로 사용하지 않는다.

| 공식 자료·읽을 정확한 범위 | 찾을 내용·활동 | 추정 |
| --- | --- | --- |
| [RFC 9110 §15.5.5 · 404 Not Found](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.5)의 첫 문단 | 대상 자원의 현재 표현을 못 찾거나 존재를 드러내지 않는다는 HTTP 응답 의미. 연결 실패와 구별, D1 | 3분 |
| [Python 3.14 HTTPConnection](https://docs.python.org/3.14/library/http.client.html#http.client.HTTPConnection)의 첫 정의 문단 | host/port와 선택 timeout, 연결 시도 같은 블로킹 작업 제한. 실행 전체의 마감으로 읽지 않음, K2 | 4분 |

영문 `representation`은 여기서 HTTP로 주고받는 자원의 표현, `blocking operation`은 완료를 기다리는 작업을 뜻한다. 막히면 [K1·K2](CONCEPTS.md)와 실제 코드를 먼저 읽는다. 404는 HTTP 응답이지만 의도한 프로그램/업무 성공의 증거까지 자동으로 넓히지 않는다.

## 코드·명령이 막힐 때의 참조

| 공식 자료·선택할 절 | 지지하는 범위 |
| --- | --- |
| [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html)의 OPTIONS 중 `-n`, `-l`, `-p`, `-t`, EXPRESSION의 포트 필터·EXAMPLES | 로컬 TCP 대기 소켓·프로세스 조회. -p 정보가 보이는 권한 조건은 실제 호스트에서 확인 |
| [curl --noproxy](https://curl.se/docs/manpage.html#--noproxy), [--connect-timeout](https://curl.se/docs/manpage.html#--connect-timeout), [--max-time](https://curl.se/docs/manpage.html#--max-time), [--fail](https://curl.se/docs/manpage.html#--fail), [Exit codes](https://curl.se/docs/manpage.html#EXIT) | 루프백 프록시 우회·연결/총시간·HTTP 오류/도구 종료 정책. 필수 명령은 --fail을 사용하지 않음 |
| [Python BaseHTTPRequestHandler](https://docs.python.org/3.14/library/http.server.html#http.server.BaseHTTPRequestHandler), [HTTPResponse.read](https://docs.python.org/3.14/library/http.client.html#http.client.HTTPResponse.read) | 재사용 Handler의 역할과 응답 본문 읽기. 학습 서버를 운영 서비스로 확대하지 않음 |
| [Python recv](https://docs.python.org/3.14/library/socket.html#socket.socket.recv), [shutdown](https://docs.python.org/3.14/library/socket.html#socket.socket.shutdown), [monotonic](https://docs.python.org/3.14/library/time.html#time.monotonic) | 앞선 코드의 부분 수신·EOF·송신 방향 종료·경과 시간/수신 마감 |
| [RFC 9112 §9.3 · Persistence](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3) | 키트의 명시적 close를 HTTP/1.1 전체가 지속 연결을 못 한다는 뜻으로 일반화하지 않음 |

## 앞 근거·학습 범위 재사용

성능 계산·혼잡은 [14주 공식 출처](../week-14/SOURCES.md), 소켓·시간·멱등성은 [15주 출처](../week-15/SOURCES.md), 실제 클라우드 정책·DNS/TLS는 [13주 출처](../week-13/SOURCES.md)의 지정 절을 재사용한다. 필요한 항목만 돌아가며 모든 문서를 새 필수 읽기로 늘리지 않는다. 전체 주제 지도는 [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer)에서 다시 찾을 수 있다. 로드맵은 범위 색인이며 개인 수행이나 기업 기출의 증거가 아니다.

## 자료 성격과 재사용 조건

정상→가설/관찰→최소 변경→복구의 학습 순서와 C16 연결·문항·가공 수치 계산은 스터디 자체 구성이다. 외부 코드·문제·이미지를 새로 복제하지 않고 기존 공개 코드를 재사용했다. Python 공식 API는 PSF License의 참조, RFC는 해당 문서 저작권 고지를 따른다. Linux 도구 문서와 실제 설치 버전의 도움말을 함께 확인한다. 공식 문서 열람·자료 제작·가공 분석을 실제 Linux/클라우드 수행이나 참가자 독립 이해로 바꾸어 쓰지 않는다.
