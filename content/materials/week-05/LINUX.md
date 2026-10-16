# 5주차 · 이름 질의와 서비스 요청 비교하기

요약: Linux에서 허가된 이름의 DNS 응답과 서비스 요청을 나누어 읽는다. 같은 로컬 IP에서 Host 조건을 바꿔 복구하고 주소·경로·DNS 설정을 조회한 뒤 제공 DHCP trace의 옵션과 순서를 분석한다.

## 준비와 실행 위치

기존 Linux VM에 접속한 셸 A/B를 사용한다. 모든 `127.0.0.1`은 명령을 실행한 VM 자신이다. 관리자 권한 없이 진행하며 주소·라우팅·방화벽·SSH·시스템 DNS 설정을 바꾸지 않는다. 기존 접속·도구·대상 사용 권한은 시작 전에 확인한다.

```sh
command -v dig
command -v curl
command -v python3
ip -br addr
ip route
cat /etc/resolv.conf
```

`dig`는 보통 Ubuntu의 `dnsutils` 또는 배포판의 BIND 도구 패키지에 있다. 없으면 진행자에게 기존 설치 경로를 확인한다. 도구 설치 권한이 없다면 임의로 시스템을 바꾸지 않는다. 제공 출력 분석으로 공부한 부분과 아직 못 한 직접 질의·요청을 구분한다.

<span id="experiment-a"></span>
## 실습 A · 질의와 요청을 직접 비교하기

### A1 · 같은 이름을 두 도구로 보기

아래 `example.com`은 공개 예제 이름이다. 기본 질의는 현재 설정된 DNS 경로를 사용한다. 실습망에서 외부 질의·요청을 허용하는지 확인하고, 제한되어 있으면 진행자가 허가한 **이름과 그 이름을 서비스하는 URL**을 같은 대상으로 바꾼다. 무작위 서버나 다른 사람의 서비스에 반복 요청하지 않는다. 예제 사이트의 응답·주소·TTL·가용성은 고정되지 않는다.

```sh
name=example.com
dig "$name" A +time=2 +tries=1
dig "$name" AAAA +time=2 +tries=1
dig "$name" A +time=2 +tries=1
curl --noproxy '*' -4 --connect-timeout 3 --max-time 8 -sS -o /dev/null \
  -w 'http=%{http_code} remote=%{remote_ip}\n' "https://$name/"
```

각 dig에서 `status`, `ANSWER SECTION`의 이름·형식·TTL·주소, `SERVER`를 읽는다. `+short`로 줄이지 않아 서버와 상태를 함께 본다. A와 AAAA는 별도 질의다. AAAA 레코드가 있어도 VM에서 IPv6 통신이 가능한지는 아직 모른다. curl의 `-4`는 이번 비교를 IPv4로 고정한다.

정상 기준은 DNS 응답에서 필요한 주소를 읽고, curl에서 원격 IP와 HTTP 응답을 따로 확인하는 것이다. 특정 주소·TTL·200을 미리 본인 결과로 적지 않는다. curl 오류이면 메시지와 종료 코드를 읽는다. 아래 줄을 **해당 curl 직후** 실행하면 종료 코드가 나온다.

```sh
echo $?
```

DNS 응답을 받았는데 curl이 실패하면 포트·경로·정책·서버·TLS 등 서로 다른 가설을 세운다. 404 같은 HTTP 응답은 연결 자체 실패와 다르다. curl은 기본적으로 HTTP 4xx를 전송 실패 종료 코드로 바꾸지 않는다. 두 dig의 시간이 짧거나 TTL이 줄었다는 이유만으로 전체 DNS 캐시 상태를 단정하지 않는다. [제공 TTL 모형](CONCEPTS.md#cache)에서 캐시 유무를 확실한 조건으로 비교한다.

선택으로 첫 A 응답의 IPv4 하나를 `server_ip`에 직접 옮겨 같은 이름·같은 IP로 재요청한다. 아래 값은 **실제 A 응답으로 바꾼 뒤** 실행한다.

```sh
server_ip=192.0.2.20
curl --noproxy '*' -4 --resolve "$name:443:$server_ip" \
  --connect-timeout 3 --max-time 8 -sS -o /dev/null \
  -w 'http=%{http_code} remote=%{remote_ip}\n' "https://$name/"
```

192.0.2.20은 문서용 자리 표시이며 그대로 요청할 대상이 아니다. `--resolve`는 지정한 이름·포트에 주소를 주는 curl 옵션이다. URL의 이름을 유지해 Host와 TLS 신원 조건을 보존한다. 이 요청은 해당 이름의 DNS 조회를 우회하므로 DNS 성공 근거가 아니다. 프록시가 필수인 환경에서는 `--noproxy '*'`로 직접 접속할 수 없으므로 이 비교를 중단하고 별도 허가된 환경에서 보충한다. 시스템 프록시 설정을 고치지 않는다.

### A2 · 목적 IP를 고정하고 Host만 바꾸기

외부 서비스의 동작에 의존하지 않고 같은 IP의 이름 조건을 확인한다. <a download href="../../labs/week-05/host_server.py">host_server.py 내려받기</a>를 허용된 파일 전달 경로로 VM의 개인 작업 폴더에 둔다. `lab.test`는 로컬 예제 이름이며 공용 DNS에 등록하거나 `/etc/hosts`를 수정하지 않는다.

셸 A에서 파일이 있는 폴더를 확인하고 비어 있는 포트를 사용한다.

```sh
python3 host_server.py --help
ss -ltn 'sport = :18405'
python3 host_server.py
```

이미 대기 중인 다른 프로세스가 있으면 종료시키지 않는다. `--port`로 본인 서버의 빈 비특권 포트를 정하고 아래 모든 URL·`--resolve` 포트도 함께 바꾼다. `Listening`이 나온 뒤 셸 B에서 실행한다.

```sh
# 정상: 이름은 lab.test, 목적지는 같은 VM의 루프백
curl --noproxy '*' --max-time 5 -i \
  --resolve lab.test:18405:127.0.0.1 http://lab.test:18405/

# 한 조건 변경: URL의 이름을 IP로 바꾼다
curl --noproxy '*' --max-time 5 -i http://127.0.0.1:18405/

# 복구: 처음의 이름과 주소 지정으로 재요청한다
curl --noproxy '*' --max-time 5 -i \
  --resolve lab.test:18405:127.0.0.1 http://lab.test:18405/
```

이 제공 서버의 정상→변경→복구 기준은 `200 name matched` → `421 unexpected Host` → `200 name matched`다. 실제 본문은 줄을 나눠 상태 문구와 `Host=...`를 보여 준다. 서버 로그에서도 GET 경로와 상태를 짝짓는다. 421은 이 예제가 선택한 응답이며 모든 웹 서버가 IP 요청을 이렇게 거절하는 것은 아니다. 세 번 모두 TCP·HTTP 왕복은 있었고 두 번째에는 Host 조건이 달라졌다.

여기서 `--resolve`로 매핑한 이름은 **DNS 패킷을 보낸 실험이 아니다**. A1의 실제 DNS 질의와 구별한다. HTTPS에서 IP URL을 쓰면 SNI·인증서 이름 조건도 달라질 수 있다는 점을 [6주차](../week-06/CONCEPTS.md)로 이어간다. 이 예제는 암호화 없는 로컬 HTTP다.

선택으로 정상 URL의 경로만 `/missing`으로 바꾸면 404가 나온다. 이름·연결은 같고 경로 조건이 달라진 것이다. 이후 `/`로 복구한다. 끝나면 셸 A에서 `Ctrl+C`로 **본인 서버만** 종료하고, `ss -ltn 'sport = :18405'`에서 대기 소켓이 사라졌는지 확인한다. 셸 변수는 아래로 지운다. 시스템 설정 복구는 필요하지 않다.

```sh
unset name server_ip
```

### 코드 읽기 · 필수 참가자 코드

코드는 Python 표준 라이브러리만 사용한다. 다운로드한 [host_server.py](../../labs/week-05/host_server.py)를 열고 다음 순서로 읽는다. 새로 작성할 과제는 아니다.

| 위치 | 목적·처음 만나는 문법 | 출력과 질문 |
| --- | --- | --- |
| main의 argparse | `--port`를 정수로 읽고 1024~65535 검사 | 왜 비특권 포트만 받을까? 잘못된 값은 시작 전에 멈춘다 |
| HTTPServer의 with | 127.0.0.1에만 바인딩하고 종료 시 소켓 정리 | 외부 VM에서 접속할 수 있을까? |
| while와 handle_request | 요청을 한 번씩 받아 반복, 한 번에 한 요청 처리 | 60초 timeout은 대기 주기이며 서버 자동 종료 시간이 아니다 |
| do_GET의 if/elif/else | Host를 먼저 비교하고 경로를 비교 | IP URL도 TCP·HTTP 도착은 했는데 왜 421일까? |
| encode와 len | 본문을 UTF-8 바이트로 만들고 길이 지정 | Content-Length는 글자 수일까 바이트 수일까? |
| except | Ctrl+C 정리와 포트 점유 등 OS 오류 구별 | 다른 프로세스를 죽이지 않고 어떻게 빈 포트를 고를까? |

이 서버의 HTTP 기본 응답 버전은 Python의 HTTP/1.0이며 연결을 닫는다. 지속 연결 성능 실측에 사용하지 않는다. TLS·DNS 서버·DHCP 서버 코드는 아니다.

<span id="experiment-b"></span>
## 실습 B · 설정 출처 조회와 DHCP 제공 분석

### VM에서 적용된 값을 조회하기

```sh
ip -4 addr show
ip -4 route show
cat /etc/resolv.conf
```

주소·접두사와 기본 경로의 `via`·`dev`, nameserver를 읽는다. `127.0.0.53` 같은 값은 로컬 stub일 수 있다. `resolvectl status`가 있는 systemd 환경에서는 링크별 DNS를 조회한다. NetworkManager를 쓰고 `nmcli`가 있으면 다음 읽기 전용 명령으로 적용 값과 DHCP 옵션을 본다. 두 도구가 모든 Linux에 있는 것은 아니다.

```sh
command -v resolvectl
command -v nmcli
# 설치되어 있고 해당 관리자를 쓰는 환경에서만 실행
resolvectl status
nmcli -f GENERAL,IP4,DHCP4 device show
```

설정 관리자·주소의 출처를 확인하지 못하면 “주소는 확인, DHCP 여부는 미확인”으로 구분한다. 전체 설정·원시 출력을 공개 게시하지 않는다. 실제 주소·호스트명·다른 인터페이스 정보는 개인 근거에만 보관한다. `dhclient -r`, 네트워크 서비스 재시작, 공유망 DHCP 서버 실행은 하지 않는다.

### 제공 trace에서 한 조건을 바꾸기

[교재의 가공 trace](CONCEPTS.md#dhcp-trace)를 열어 거래 ID, 메시지 방향·포트, REQUEST의 선택 서버, ACK의 다섯 설정을 짚는다. 이는 제공 분석이며 VM의 실제 DHCP 통신을 캡처한 결과가 아니다.

1. 정상 ACK에서 자기 주소, 같은 망 범위, 기본 경로 후보, DNS 질의 대상을 설명한다.
2. DNS 옵션만 `192.0.2.54`이고 **그 주소에서 DNS 응답을 하지 않는 조건**으로 바꾸어 생각한다. 주소·경로 조회와 새 이름 질의 중 무엇이 달라질까? 기존 캐시가 있으면 증상이 가려질 수도 있다.
3. DNS 옵션을 `.53`으로 되돌린 정상 trace와 비교해 설명을 복구한다. VM의 실제 설정을 바꾸는 단계는 없다.

완료 근거는 A의 질의·요청 및 200→421→200 출력, B의 실제 설정 조회에서 확인한 범위, 제공 DHCP 순서·옵션의 자기 설명이다. A를 제공 분석으로만 읽었다면 직접 수행은 보충으로 남긴다.

## 실패를 구별하고 보충하기

| 증상 | 다음에 확인할 것 | 피할 결론 |
| --- | --- | --- |
| dig timeout | SERVER·허용된 질의 경로·망 정책 | 이름이 없다고 단정 |
| NOERROR인데 주소 없음 | 질의 형식·별칭·응답 섹션 | 모든 주소/서비스가 없다고 단정 |
| curl 이름 해석 실패 | 실제 앱/OS 경로와 dig 대상 차이·프록시 | 서버 프로그램 중지라고 단정 |
| curl 연결 실패/시간 초과 | 목적 IP·포트·경로·정책·서버 대기 | DNS 성공을 서비스 정상으로 확대 |
| 로컬 421 | URL의 이름·명시 포트·Host 본문 | 연결 자체가 실패했다고 판단 |
| bind 오류 | 본인 포트의 ss 결과·다른 빈 포트 | 기존 프로세스 강제 종료 |

패킷을 추가로 분석할 때는 [WireSalmon](https://taerim0.github.io/WireSalmon/) 또는 Wireshark를 사용할 수 있다. 공개 웹 분석 도구는 실시간 캡처 대신 허가된 저장 파일을 읽는 용도로 쓰고, 제공 예제·직접 캡처를 구별한다. 이번 필수는 본문 trace 분석이며 새 캡처 권한을 요구하지 않는다.
