# IPv6 비교와 단일 장애 진단 실습

요약: 같은 Linux에서 IPv4/IPv6 주소·경로와 루프백 관찰을 비교한다. IPv6 통신 대안은 제공 trace다. 기존 HTTP 실습의 단일 장애는 원인을 가린 상태로 각자 진단·재현·복구한다.

## 준비와 실행 위치

기존 Linux VM의 셸 두 개를 사용한다. `hostname`, `pwd`, `python3 --version`, `curl --version`, `ip -V`로 위치·도구를 확인한다. 루프백은 그 명령을 실행한 호스트 자신이다. 주소·기본 경로·방화벽·시스템 DNS·SSH 설정을 바꾸지 않는다. 외부 IPv6나 새 자원은 필요 없다. 도구/권한이 없으면 제공 분석과 직접 수행 보충을 구별한다.

<span id="ipv6-lab"></span>

## A · IPv4/IPv6를 같은 호스트에서 비교하기

### A1 · 주소와 경로 조회

일반 사용자로 실행한다. `-4`/`-6`은 주소 계열, `show`는 조회다. 실제 주소는 공개 기록에 복사하지 않는다.

```sh
ip -4 address show
ip -6 address show
ip -4 route show
ip -6 route show
ip -4 route get 127.0.0.1
ip -6 route get ::1
ip -4 neigh show
ip -6 neigh show
```

`inet`/`inet6`, 접두사, `scope host`/`link`/`global`, `dev`·`via`·`src` 또는 경로 부재를 짚는다. 기본 `route show`에 루프백 경로가 없더라도 local 표를 사용하는 `get` 결과와 모순이 아닐 수 있다. 필요할 때만 `ip -6 route show table local`로 대조한다. `get`은 패킷을 보내지 않는 커널 조회다. 두 계열에서 같은 인터페이스 이름이 보여도 주소·경로·도달 조건은 각각 확인한다. 이웃 표가 비어 있다고 IPv6가 반드시 고장난 것은 아니다. [공식 명령](SOURCES.md#commands).

### A2 · 정상 조건을 바꿔 재조회

`ping`이 준비돼 있고 루프백 ICMP 요청이 허용될 때만 각 두 번 보낸다. 두 번째 계열로 바꾼 뒤 첫 계열을 재실행한다. 상태 설정은 바꾸지 않는다.

```sh
ping -4 -n -c 2 -W 1 127.0.0.1
ping -6 -n -c 2 -W 1 ::1
ping -4 -n -c 2 -W 1 127.0.0.1
```

정상 기준은 각 루프백의 응답과 전송/수신 개수다. 시간값은 고정하지 않는다. `::1`은 같은 호스트에서 끝나므로 외부 IPv6 경로·DNS AAAA·Ethernet NDP를 검증한 것이 아니다. 권한 오류, IPv6 비활성·주소/경로 부재가 나오면 임의 활성화나 sudo 설정 변경을 하지 않는다. A1 조회와 아래 제공 trace를 비교하고 실제 `::1` 통신은 보충으로 구별한다. Ctrl+C로 중단할 수 있고 정상 종료 후 남는 서버는 없다.

### A3 · 제공 IPv6 trace 비교

<a download href="../../labs/week-08/ipv6-trace.txt">ipv6-trace.txt 내려받기</a>는 실제 캡처가 아닌 **자체 가공 사건 기록**이다. 첫 부분은 `lo`에서 `::1` Echo Request/Reply, 둘째는 별도 격리 Ethernet의 문서용 두 주소와 빈 이웃 캐시를 가정한다. 두 부분은 같은 실험의 연속 캡처가 아니다.

```text
L1 lo ::1 → ::1 ICMPv6 Echo Request id=8 seq=1
L2 lo ::1 → ::1 ICMPv6 Echo Reply   id=8 seq=1
E1 A → ff02::1:ff00:20 NS target=2001:db8:8:1::20
E2 B → A NA target=2001:db8:8:1::20 link-address=02:00:00:00:00:20
E3 A → B ICMPv6 Echo Request id=9 seq=1
E4 B → A ICMPv6 Echo Reply   id=9 seq=1
```

L1/L2에서 링크 주소 질의가 없는 이유, E1/E2의 NS/NA 역할과 E3/E4의 도달성 범위를 설명한다. NDP가 ICMPv6라는 이유로 모든 ICMPv6를 이웃 주소 확인으로 부르지 않는다. Echo는 다른 메시지다. 캐시가 이미 있으면 E1/E2가 새로 안 보일 수 있다. 파일에는 주소/인터페이스 조회 예시도 있으며 본인 Linux 실측으로 바꾸어 적지 않는다.

<span id="diagnosis"></span>

## B · C08 정답을 숨긴 단일 장애 하나

진행자가 [기존 6주차 서버](../week-06/LINUX.md)의 개인 루프백 환경에 새 단일 사례를 준비한다. 고정 파트너나 교대는 필요하지 않지만, 참가자는 아래 정상 계약과 증상만 받고 **원인 선택·설정 명령·해설은 보지 않는다.** 같은 참가자가 이미 원인을 보았다면 다른 단일 조건이나 다른 포트/경로의 새 사례를 받는다. 혼자라서 가릴 수 없다면 연습으로 표시하고 모임에서 새 사례로 독립 진단을 보충한다.

정상 계약은 “본인 Linux, Python 제공 서버, HTTP/1.1, `127.0.0.1:8086/resource`에 GET하면 200과 `study representation v1`을 받는다”다. 포트가 사용 중이면 준비자가 본인의 빈 비특권 포트로 바꾸고 계약·URL을 함께 갱신한다. 참가자에게 전달하는 사례 URL은 준비자가 정하며 한 조건만 정상과 다르다. 404·서버 중지·잘못된 포트 중 하나를 사용한다. DNS/TLS가 없는 이 사례만으로 실제 DNS/TLS 장애를 재현했다고 쓰지 않는다.

1. 전달받은 **사례 URL 그대로** 한 번 요청하고 출력을 읽는다. 아래 `case_url`의 값만 전달받은 것으로 바꾼다. 기본 줄은 정상 요청의 문법 예시이며 숨긴 장애 자체가 아니다.

```sh
case_url=http://127.0.0.1:8086/resource
curl --noproxy '*' --http1.1 --connect-timeout 3 --max-time 5 -iv "$case_url"
echo $?
```

2. 원인 가설 둘을 먼저 나누고 이를 구별할 관찰 하나를 고른다. 서버 중지·포트 불일치·HTTP 경로 불일치는 결과가 어떻게 다를까? 필요하면 `ss -ltn 'sport = :8086'`, 서버 셸 로그·사례 URL을 조회한다. 커넥션 거부만으로 서버 중지와 다른 포트 요청을 확정하지 않는다.
3. 확인한 근거로 **본인 테스트 서비스/요청의 한 조건만** 고친다. 남의 프로세스는 종료하지 않는다. 본인 서버를 다시 켤 필요가 있으면 제공 파일이 있는 폴더에서 `python3 http_server.py --port 8086`을 사용한다. 정상 계약의 URL로 재요청해 200·본문·서버 로그를 대조한다.
4. 원인을 설명한 뒤 진행자가 허용한 같은 조건을 본인이 한 번 재현하고 동일 증상인지 확인한다. 원래 정상 조건으로 복구하고 다시 200을 확인한다. 최초 진단은 원인 공개 전, 재현은 진단 뒤 수행이다. 진단 뒤 받은 도움을 최초 독립 진단처럼 쓰지 않는다.
5. 본인 서버 셸에서 Ctrl+C로 종료한다. `ss -ltn 'sport = :8086'`에서 본인 listener가 정리됐는지 확인한다. 주소·경로·정책 변경은 없다.

완료 근거는 최초 증상·가설 둘·둘을 가른 출력·한 조건 수정·동일 장애 재현·최종 정상/정리다. 기존 활동의 짧은 설명에서 보이며 고정 기록 양식은 없다. `curl`은 기본적으로 404도 전송 자체는 성공해 종료 코드 0일 수 있으므로 HTTP 상태와 함께 읽는다. 제공 예제나 해설만 분석하면 직접 진단·재현은 미완료다.

## 기존 코드와 제공 자료를 읽는 지도

새 전송 모형 코드는 만들지 않는다. <a download href="../../labs/week-06/http_server.py">기존 http_server.py</a>의 `main` 입력/루프백 대기 → `StudyServer.get_request` 연결 → `StudyHandler.do_GET` 경로 판단 → 상태/본문/로그 → Ctrl+C 정리 순서로 읽는다. `/resource`와 그 외 경로의 분기, `Content-Length`의 바이트 길이, 연결 성공과 HTTP 상태의 차이를 짚는다. `--port`는 서버 포트를, URL은 클라이언트 목적 포트를 바꾼다. 둘을 동시에 바꿨다면 포트 불일치라는 단일 장애가 사라질 수 있다. 문법·TLS 선택 모드는 [6주차 코드 읽기](../week-06/LINUX.md#코드-읽기--입력에서-응답과-정리까지)를 참고한다.

7주차를 보충할 때만 <a download href="../../labs/week-07/route_sim.py">route_sim.py</a>와 <a download href="../../labs/week-07/topology.txt">topology.txt</a>를 같은 폴더에 두고 [7주차 명령](../week-07/LINUX.md#simulator)으로 정상→반환 경로 하나 삭제→restore를 복습한다. 이것은 고정 A–R1–R2–B 교육 모형이며 실제 TCP/ARP/OS 경로나 Linux 패킷 실측이 아니다. B를 마친 사람의 추가 필수 실습으로 늘리지 않는다.

전송 시간축은 <a download href="../../labs/week-08/loss-timeline.txt">loss-timeline.txt</a>에서 ACK 의미·수신 보관·재전송 집합을 읽는다. 제공 파일을 실행 코드·실측 로그로 오해하지 않는다. [Q7\~Q8](REVIEW.md)과 [분리 해설](ANSWERS.md)을 진단 뒤에 대조한다.
