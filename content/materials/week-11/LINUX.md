# 격리 실습 · HTTP 접근 규칙을 바꾸고 복구하기

요약: 준비된 Docker Linux 컨테이너의 테스트 서버에서 허용 규칙 한 항목을 바꿔 새 HTTP 요청·대기 포트·로그·카운터를 비교한다. 서버 중지와 정책 DROP을 구별하고 복구·정리한다.

## 실행 환경과 파일

본인 PC의 PowerShell 또는 소유한 격리 Linux 호스트에서 **Docker Engine의 Linux 컨테이너와 Docker Compose v2 이상**을 사용한다. Docker 사용 권한이 필요하다. Windows에서는 Docker Desktop의 Linux 엔진을 사용한다. 접속 중인 공용 서버의 Docker·SSH·호스트 방화벽 설정은 변경하지 않는다.

진행자는 다음 **다섯 파일을 같은 새 개인 폴더**에 내려받는다. `Dockerfile.txt`를 포함해 모두 표시된 이름대로 보관한다. 셸 파일은 LF 줄바꿈을 유지한다. NAT CSV는 분석용이며 이미지에 넣지 않는다.

- <a download href="../../labs/week-11/Dockerfile.txt">Dockerfile.txt</a> — Alpine3.22에 curl·iproute2·nftables·Python3을 설치한다.
- <a download href="../../labs/week-11/compose.txt">compose.txt</a> — 서버1개·클라이언트2개와 내부망을 준비한다. 확장자를 바꾸지 않고 `-f`로 지정한다.
- <a download href="../../labs/week-11/policy.sh">policy.sh</a> — 서버 컨테이너 안의 전용 `inet w11` 표만 교체한다.
- <a download href="../../labs/week-11/service.sh">service.sh</a> — 테스트용 Python HTTP 프로세스를 시작·중지한다.
- <a download href="../../labs/week-11/nat-table.txt">nat-table.txt</a> — 제공 NAT 대응표, 직접 캡처가 아닌 설명용 값이다.

HTTP 본문 `/srv/index.txt`는 Dockerfile.txt가 직접 만든다.

### 소유와 대역을 먼저 확인하기

아래 모든 명령은 내려받은 폴더의 **호스트 셸**에서 입력한다. `-p w11me`는 본인 전용 프로젝트다. 처음 만들기 전에 다음 조회에서 같은 이름의 기존 작업이 없는지 확인한다.

```sh
docker version
docker compose version
docker compose ls -a
docker network ls
```

프로젝트 이름이 이미 쓰이면 모든 명령의 `w11me`를 다른 영숫자 이름으로 일관되게 바꾼다. 기존 프로젝트를 덮어쓰지 않는다. `docker network inspect <조회한-네트워크-이름>`으로 IPAM의 Subnet을 읽어 **172.30.111.0/24와 겹치는 대역이 없는지** 확인한다. `<...>`는 실제 조회한 이름으로 치환하며 그대로 실행하지 않는다. 호스트·VPN 경로 충돌도 진행자가 확인한다. 같은 Docker 엔진에서 다른 프로젝트 이름을 써도 같은 고정 대역은 충돌한다. 충돌하면 다른 엔진을 쓰거나 진행자가 compose·policy·교재의 모든 주소를 함께 바꿔 다시 검증한다. 다른 실습망을 삭제하지 않는다.

### 준비하기

```sh
docker compose -p w11me -f compose.txt config --quiet
docker compose -p w11me -f compose.txt up -d --build
docker compose -p w11me -f compose.txt ps
docker compose -p w11me -f compose.txt exec -T server sh /lab/service.sh start
docker compose -p w11me -f compose.txt exec -T server ss -lntp
```

이미지와 패키지를 받는 빌드 단계에는 인터넷이 필요하다. 버전 태그 아래의 패키지 업데이트까지 완전히 고정한 재현은 아니므로 실제 `nft --version`, `python3 --version`도 확인한다. 설치는 모임 전에 끝낸다. 서버가 running이어도 HTTP 프로세스의 준비는 별도다. `ss`의 LISTEN과 `0.0.0.0:8080`을 확인하고 A1의 요청까지 성공해야 준비 완료다. 시작 직후 대기 포트가 아직 없으면 다시 조회하고, 계속 없으면 HTTP 로그를 읽는다.

서버=.20, A=.11, B=.12이며 모두172.30.111.0/24다. 전용 bridge의 `internal: true`, 호스트 포트 공개 없음, 호스트 네트워크·Docker 소켓·호스트 파일 마운트 없음으로 실험 범위를 제한한다. 서버에만 `NET_ADMIN`을 추가해 그 컨테이너의 nftables를 바꾼다. 컨테이너 밖에서 policy.sh를 실행하지 않는다. 호스트 접근까지 모두 차단하는 악성 코드용 보안 샌드박스라는 뜻은 아니다.

이 실습은 NAT를 구축하지 않는다. 같은 내부 bridge의 IP 통신·실제 커널 INPUT 필터·TCP·HTTP를 관찰한다. 7·9주 모형에 없는 방화벽 기능을 가정하지 않는다. 호스트 방화벽 전체를 끄거나 `flush ruleset`을 실행하지 않는다.

<span id="lab-a"></span>
## 필수 A · 한 규칙 변경·비교·복구

### A1. 정상 기준과 출발지 비교

```sh
docker compose -p w11me -f compose.txt exec -T client-a ip -4 route get 172.30.111.20
docker compose -p w11me -f compose.txt exec -T client-a curl --noproxy "*" --connect-timeout 2 --max-time 3 -i http://172.30.111.20:8080/index.txt
docker compose -p w11me -f compose.txt exec -T client-b curl --noproxy "*" --connect-timeout 2 --max-time 3 -i http://172.30.111.20:8080/index.txt
docker compose -p w11me -f compose.txt exec -T server nft -a list table inet w11
docker compose -p w11me -f compose.txt exec -T server cat /tmp/http.log
```

A의 route get은 직접 연결 경로와 `src 172.30.111.11`을 보여야 한다. A 요청은 HTTP200과 `week11-test`, B 요청은 DROP 때문에 curl의 제한 시간 오류가 기준이다. B의 실패는 **예상된 비교 결과**다. `--noproxy "*"`는 프록시 환경변수로 우회하지 않게 하고, 시간 옵션은 실패를 유한하게 끝낸다. 셸에서 명령마다 결과를 읽고 다음 줄로 간다. 실패 줄을 정상 응답으로 기록하지 않는다.

서버의 .11 허용 카운터와 나머지8080 DROP 카운터, HTTP 로그의 A 주소·GET·200을 찾는다. B는 HTTP까지 도달하지 않아 해당 GET 로그가 없어야 한다. 로그 없음만으로 차단 위치를 확정할 수 없으므로 요청·카운터·규칙을 함께 본다. 재전송 때문에 카운터가 요청 횟수와 같을 필요는 없다.

### A2. 테스트용 규칙 하나를 직접 변경

바꾸기 전 ‘서버가 계속 LISTEN인데 A의 새 요청만 어떤 결과가 될까’를 예상한다.

```sh
docker compose -p w11me -f compose.txt exec -T server sh /lab/policy.sh block
docker compose -p w11me -f compose.txt exec -T client-a curl --noproxy "*" --connect-timeout 2 --max-time 3 -i http://172.30.111.20:8080/index.txt
docker compose -p w11me -f compose.txt exec -T server ss -lntp
docker compose -p w11me -f compose.txt exec -T server nft -a list table inet w11
docker compose -p w11me -f compose.txt exec -T server cat /tmp/http.log
```

같은 출발지·목적지·포트 조건의 **accept 하나만 drop으로 바뀐다.** A는 새 curl 프로세스로 새 연결을 만든다. 제한 시간 실패, LISTEN 유지, .11 DROP 카운터 증가, 새 GET 로그 없음이 비교 기준이다. 정책 교체 때 카운터는0부터 다시 시작하므로 교체 전후 숫자를 누적 요청 수로 빼지 않는다. 로그는 누적되므로 기존 A1의 GET을 새 요청으로 착각하지 않는다.

앞쪽 established 허용은 남아 있다. 기존 연결이 살아 있을 수 있으므로 ‘현재 모든 연결을 차단했다’고 해석하지 않는다. 커널 추적 전체 삭제·관리 접속 변경 없이 **새 연결에 대한 정책 효과**만 비교한다.

### A3. 규칙을 복구한 뒤 같은 요청

```sh
docker compose -p w11me -f compose.txt exec -T server sh /lab/policy.sh allow
docker compose -p w11me -f compose.txt exec -T client-a curl --noproxy "*" --connect-timeout 2 --max-time 3 -i http://172.30.111.20:8080/index.txt
docker compose -p w11me -f compose.txt exec -T server nft -a list table inet w11
docker compose -p w11me -f compose.txt exec -T server cat /tmp/http.log
```

A의 HTTP200·본문·새 로그와 accept 복구를 확인한다. B의 제한은 원래 정책대로 남는다. 규칙 전후 설정·같은 요청·서버 근거와 복구를 각자 개인 파일에 한 번 보관하고 자기 말로 설명한다. 다른 사람이 실행한 출력만 읽으면 직접 수행 보충이 남는다.

## 필수 B · 서버 중지와 NAT 대응표

### B1. 같은 정책에서 서버만 중지·복구

```sh
docker compose -p w11me -f compose.txt exec -T server sh /lab/service.sh stop
docker compose -p w11me -f compose.txt exec -T client-a curl --noproxy "*" --connect-timeout 2 --max-time 3 -i http://172.30.111.20:8080/index.txt
docker compose -p w11me -f compose.txt exec -T server ss -lntp
docker compose -p w11me -f compose.txt exec -T server nft -a list table inet w11
docker compose -p w11me -f compose.txt exec -T server sh /lab/service.sh start
docker compose -p w11me -f compose.txt exec -T client-a curl --noproxy "*" --connect-timeout 2 --max-time 3 -i http://172.30.111.20:8080/index.txt
```

allow 상태에서 HTTP만 중지하면8080 LISTEN이 없어지고 이 격리 환경에서는 보통 연결 거부(curl7)를 본다. DROP 상태의 제한 시간 실패(curl28)와 비교한다. 다른 장비의 REJECT나 경로 장애도 비슷한 증상을 만들 수 있으므로 오류 번호만으로 일반화하지 않는다. 재시작 뒤 LISTEN·HTTP200으로 복구를 확인한다. `docker exec` 제어는 IP 기반 SSH가 아니므로 INPUT DROP 상황에서도 사용할 수 있다.

### B2. 제공 표 분석

[NAT 대응표](CONCEPTS.md#w11-k1)의 B와 C에 대해 요청/응답의 안쪽·바깥쪽 5튜플을 각각 읽는다. 바깥 응답의 목적지40002를 어느 내부 호스트·포트로 복원하는지, 안쪽과 바깥쪽 규칙의 출발지가 왜 다를 수 있는지 설명한다. CSV는 제공 분석이며 실제 NAT 장치를 바꿨다는 근거가 아니다. [복습 Q1~Q3](REVIEW.md)으로 확인한다.

## 실패하면 무엇을 볼까?

| 증상 | 구별할 관찰·다음 행동 |
| --- | --- |
| Docker pipe·permission denied | Linux 엔진 실행·본인 Docker 사용 권한 확인. 권한 없이 호스트 방화벽이나 소켓 권한을 풀지 않음 |
| overlap·이미 존재하는 프로젝트 | 중단하고 소유 이름·고정 대역 재확인. 다른 컨테이너/네트워크 삭제 금지 |
| nft Operation not permitted | server 서비스의 NET_ADMIN·엔진 지원·컨테이너 생존 확인. privileged/호스트 실행으로 우회하지 않음 |
| 셸 구문 오류·파일 없음 | 이름·Dockerfile build context·LF 확인. 편집 후에는 이미지를 다시 빌드/생성해야 반영됨 |
| A도 A1부터 실패 | server 로그·8080 바인딩·실제 .11 출발지·규칙과 카운터를 차례로 대조. localhost는 자기 컨테이너라는 점 확인 |
| 시작 중복 또는 stop 실패 | service.sh는 중복 실행/없는 PID를 오류로 알림. 프로세스·LISTEN 확인 후 자기 프로젝트를 down/up하고 준비부터 재현 가능 |
| 규칙 바꿔도 기존 요청 성공 | established 규칙과 연결 재사용 여부 확인. 새 curl 프로세스로 재시험 |
| GET404 | TCP/HTTP는 도달했지만 경로가 없음. `/index.txt` 철자 확인. 방화벽을 열어 고치지 않음 |

권한이 없으면 표·규칙·제공 예를 분석하고 직접 변경·복구는 가능한 환경에서 보충한다. 분석 결과를 실제 실행 결과로 쓰지 않는다.

## 코드와 구성 읽기

Dockerfile.txt는 도구 설치→본문 생성→두 셸 파일 복사 순서다. compose의 `build.context: .`은 이 폴더를 빌드 입력으로 쓰고 `dockerfile: Dockerfile.txt`가 파일 이름을 지정한다. 서버만 policy.sh를 allow로 실행하고 sleep으로 컨테이너를 유지한다. service.sh의 HTTP 프로세스는 별도이므로 서비스 중지와 컨테이너 종료를 구별할 수 있다. `python3 -m http.server`는 로컬 학습용이며 운영 서버로 배포하지 않는다.

policy.sh의 `case`는 allow/block만 받으며 다른 입력이면 종료코드2로 끝난다. 기존 `inet w11`이 있으면 그 표의 삭제와 새 구성을 한 파일에 묶는다. `nft --check`로 검증한 뒤 `nft --file`로 적용하므로 셸의 명령 여러 개 사이에 방화벽 전체가 빈 상태가 되지 않는다. 추적 표는 지우지 않고 규칙 카운터만 새로 만든다. 다른 표·호스트 규칙은 변경하지 않는다.

service.sh는 PID 파일로 자신이 시작한 HTTP를 중지한다. `&`는 HTTP를 뒤에서 실행하고 `$!`는 그 프로세스 번호다. `> ... 2>&1`은 출력·오류를 같은 로그로 보낸다. `start`는 이미 실행 중이면 오류, `stop`은 PID가 없으면 오류다. 새 start는 이전 HTTP 로그를 덮어쓰므로 필요한 출력은 stop/start 전에 보관한다. 이 스크립트는 한 개인이 순서대로 다루는 새 컨테이너용이며 여러 사람이 동시에 조작하지 않는다.

## 복구와 종료

진행 중에는 A3의 allow·HTTP start·정상 요청으로 복구한다. HTTP가 이미 실행 중이면 start를 반복하지 않는다. 상태가 꼬이면 자기 프로젝트만 아래 명령으로 제거한 뒤 준비부터 다시 시작할 수 있다. 종료 전 필요한 로그·규칙 출력은 개인 파일에 보관한다.

```sh
docker compose -p w11me -f compose.txt down
docker compose -p w11me -f compose.txt ps -a
docker network ls
```

자기 컨테이너3개와 `w11me_practice`가 사라졌는지 확인한다. 다운로드 원문·빌드 이미지·다른 프로젝트는 남는다. 전역 prune·다른 망 삭제·SSH 규칙 변경은 하지 않는다. [공식 명령·범위](SOURCES.md)를 참고한다.
