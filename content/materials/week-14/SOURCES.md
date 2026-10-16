# 14주차 · 공식 근거와 짧은 읽기

요약: cwnd/rwnd·고전 혼잡 제어와 curl 시간의 필요한 공식 문단을 함께 읽는다. 지연·BDP·HTTP API는 계산/실습 근거로 찾아보며 전체 문서 필독을 요구하지 않는다. 그래프·문항·제공 사례는 자체 작성이다.

## 필수 공동 읽기 · 약 10분 추정

기존 공동 탐색 중 아래 문단을 읽고 교재·자기 출력에 대응한다. 실제 초보자 소요 시간은 사용 때 확인한다. 영어가 막히면 [K1\~K3](CONCEPTS.md)의 한국어 설명으로 돌아간다.

| 공식 문서·정확한 지정 범위 | 함께 찾을 것 | 예상 분량 |
| --- | --- | --- |
| [RFC5681 §2](https://www.rfc-editor.org/rfc/rfc5681.html#section-2)의 RECEIVER WINDOW·CONGESTION WINDOW·FLIGHT SIZE 정의만 | rwnd/cwnd와 미확인 데이터의 구별 | 필수 3분 |
| [RFC5681 §3.1](https://www.rfc-editor.org/rfc/rfc5681.html#section-3.1)의 “The slow start algorithm is used when”부터 slow start 종료 설명까지, “During congestion avoidance”의 RTT당 증가 문단 | 문턱 전후의 증가 구별. 초기 윈도 상수표·계산 알고리즘 상세는 제외 | 필수 4분 |
| [curl --write-out](https://curl.se/docs/manpage.html#--write-out)의 time_connect·time_starttransfer·time_total 세 정의 | 시작부터의 시간·앱 처리 포함. 전체 시간을 망 RTT로 쓰지 않기 | 필수 3분 |

## 계산·구현의 근거와 선택 읽기

확인일은 2026-10-17 KST다. 아래는 필독 추가분이 아니라 필요할 때 찾는 범위다. RFC5681은 고전 모형의 근거이며 현재 모든 TCP의 상수·전체 궤적을 보장하지 않는다.

<style>.week14-sources table { min-width: 740px; } .week14-sources th:first-child, .week14-sources td:first-child { min-width: 150px; } .week14-sources th:last-child, .week14-sources td:last-child { min-width: 180px; }</style>

<div class="week14-sources">

| 자료 | 확인할 절·채택 범위 | 읽기 목적·선택 분량 |
| --- | --- | --- |
| [Kurose·Ross End-to-end delay](https://gaia.cs.umass.edu/kurose_ross/interactive/end-end-delay.php) | Problem·Solution의 전송 L/R·전파 거리/속도·합산 | K1 계산의 교재 저자 자료. 자체 문제의 처리·큐잉·노드 수는 별도 가정 · 선택 3분 |
| [Kurose·Ross §1.4 지식 확인](https://gaia.cs.umass.edu/kurose_ross/knowledgechecks/problem.php?c=1&s=4) | Components of packet delay의 처리·큐잉·전송·전파 구별 | K1의 네 성분 · 선택 2분. 전체 문제를 추가 과제로 요구하지 않음 |
| [RFC6349 §3.3.1](https://www.rfc-editor.org/rfc/rfc6349.html#section-3.3.1) | BDP식·TCP receive window/RTT 전송률 | K2 크기와 상한 · 선택 2분. Informational 측정 프레임워크이며 운영 버퍼 설정 지시로 쓰지 않음 |
| [RFC5681 §3.1·§3.2](https://www.rfc-editor.org/rfc/rfc5681.html#section-3.2) | timeout의 LW/문턱, 세 중복 ACK와 빠른 재전송·복구 뒤 윈도 | 제공 그래프의 손실 사건 · 선택 4분. cwnd 대신 FlightSize를 쓰는 조건 유지 |
| [Python http.server](https://docs.python.org/3/library/http.server.html) | ThreadingHTTPServer·BaseHTTPRequestHandler·send_header/end_headers·보안 주의 | 기존 Handler 상속·리스너·응답 경계 · 선택 3분. 운영용 공개 서버로 권장하지 않음 |
| [Python http.client](https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection) | HTTPConnection의 timeout·request/getresponse/close, HTTPResponse.read/getheader | 고정 백엔드 GET·본문/식별자·실패 후 정리 · 선택 3분 |
| [Python time](https://docs.python.org/3/library/time.html#time.perf_counter) | perf_counter·sleep | 경과 시간 구간·요청 처리 대기 · 선택 2분 |
| [Python socketserver](https://docs.python.org/3/library/socketserver.html#socketserver.BaseServer.allow_reuse_address) | allow_reuse_address·server_bind의 설정 역할 | LabServer의 주소 재사용 설정 · 선택 1분. OS별 실제 재시작은 실행 환경에서도 확인 |
| [Python os.replace](https://docs.python.org/3/library/os.html#os.replace) | 같은 파일시스템 교체·성공 시 원자성 | enabled.txt를 완성한 임시 파일로 교체 · 선택 1분 |
| [curl manpage](https://curl.se/docs/manpage.html#--max-time) | --noproxy·--connect-timeout·--max-time·--dump-header·--output·--write-out, EXIT CODES | 프록시 환경변수 우회·시간 상한·헤더/본문·통신 오류와 HTTP 구별 · 필요한 명령당 1분 |

</div>

## 재사용과 관찰의 경계

1주 Handler·6주 HTTP 시간/연결·13주 동일 요청과 양끝 로그를 재사용한다. backend/proxy의 고정 포트·매 요청 health·후보 선택·재시도 없음은 **제공 코드의 동작**이며 일반 TCP/LB 표준이 아니다. 코드를 직접 읽고 실행해 확인한다. 운영 Nginx 등의 구성과 같다고 주장하지 않는다.

지연/윈도 문제·그래프 SVG와 CSV 형식 원본·observations.txt·개발/복습 질문은 자체 교육 자료다. 가공한 제공 시간을 실측으로 쓰거나 기업 기출로 표시하지 않는다. 외부 원문·그림·문제를 길게 복제하지 않고 자체 설명과 지정 절로 연결한다. [실습](LINUX.md) · [개념 색인](../CONCEPT_INDEX.md).
