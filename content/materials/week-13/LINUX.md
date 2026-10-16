# 13주차 · 자기 클라우드 조회와 테스트 요청

요약: 실제 자원과 양끝 요청을 확인하고 본인 테스트 허용 규칙만 제거·복구한다. 1주차 HTTP 코드와 5~6주 DNS·TLS를 재사용한다. 클라우드 직접 수행 A와 가공 크기 분석 B의 근거를 나누고 관리 경로는 변경하지 않는다.

<span id="preflight"></span>

## 실행 위치·허용 범위부터 확인

아래 셸 예시는 **Linux** 기준이다. 서버는 기존 본인 VM, 클라이언트는 허가된 PC 또는 다른 VM이다. 클라우드 조회/규칙 명령은 이미 인증된 본인 관리 셸 또는 콘솔에서 실행한다. 로그인 비밀값을 파일·공개 기록에 넣지 않는다. Windows PC에서 요청한다면 `curl` 대신 `curl.exe`, 종료 코드는 `$LASTEXITCODE`를 사용하며 Linux의 변수·`printf` 문법을 그대로 붙여 넣지 않는다. Windows Schannel에서 학습용 CA의 폐기 상태를 확인하지 못하면 검증을 끄지 말고 준비된 Linux curl에서 재현하며 해당 환경 차이를 남긴다.

진행자와 다음 조건을 확인한 뒤 A를 실행한다. 하나라도 불명확하면 가공 사례를 분석하고 직접 수행은 보충한다.

- 현재 프로젝트/VM과 자원 소유권·사용 허가, 현재 접속·할당량·도구를 확인했다. 새 유료 자원·VM 생성이 기본 전제는 아니다.
- 관리 SSH와 별도 콘솔/복구 경로가 있고 기존 관리 주소·기본 경로·TCP22·공용망을 바꾸지 않는다.
- 서버 port에 **미리 준비된 테스트 전용 보안 그룹**이 연결되어 있으며 다른 VM/업무와 공유하지 않는다. 그룹 연결 자체와 기존 그룹/규칙은 변경하지 않는다.
- 서버 port의 모든 그룹/remote group·전체 프로토콜 허용까지 확인해 실험 TCP 8080을 중복 허용하는 규칙이 없다. 클라이언트 egress·호스트 정책은 이 요청/반환을 허용하며 여기서 임의 수정하지 않는다.
- 클라우드 정책이 보는 실제 출발지와 허가된 `/32`를 확인했다. PC 주소가 NAT/VPN을 지나면 PC 인터페이스 주소와 다를 수 있다. 불명확하다고 전체 인터넷 허용으로 넓히지 않는다.
- 해당 포트가 사용되지 않고 같은 요청·로그를 양끝에서 볼 수 있다. stateful/stateless·정책 전파 조건도 확인한다.

<span id="cloud-lab"></span>

## 필수 A1 · 실제 자원과 왕복 경로 읽기

콘솔의 **프로젝트→인스턴스→네트워크/포트→서브넷/라우터→보안 그룹 규칙**을 따라 자기 자원을 읽는다. CLI가 준비되어 있다면 다음과 같이 조회한다. `REPLACE_...`는 출력에서 확인한 자신의 ID로 **각각 치환**한다. 인증이나 권한이 실패하면 다음 변경 명령으로 넘어가지 않는다.

```sh
openstack server show REPLACE_VM_ID
openstack port list --server REPLACE_VM_ID
openstack port show REPLACE_SERVER_PORT_ID
openstack network show REPLACE_NETWORK_ID
openstack subnet show REPLACE_SUBNET_ID
openstack router list
openstack router show REPLACE_ROUTER_ID
openstack port list --device-id REPLACE_ROUTER_ID
openstack security group show REPLACE_APPLIED_GROUP_ID
openstack security group rule list --long REPLACE_APPLIED_GROUP_ID
```

network/subnet/port의 연결 ID·fixed IP/MAC·gateway, router의 연결 subnet/외부 gateway/추가 route, port의 모든 보안 그룹·port security를 대조한다. 실제 router가 없거나 해당 요청에 쓰이지 않으면 그 사실을 그린다. 그룹 조회는 적용된 **각 그룹**에 반복한다. floating IP를 쓴다면 `openstack floating ip list`에서 대응 port/fixed IP를 읽는다. 관리자 전용 provider/물리 설정을 얻기 위해 권한을 높이지 않는다.

서버 VM에서 조회한다. `REPLACE_CLIENT_IP`는 서버가 반환할 클라이언트 주소다.

```sh
hostname
ip -br -4 address
ip -4 route show
ip -4 route get REPLACE_CLIENT_IP
ss -lntp
```

Linux 클라이언트에서도 `ip -4 route get REPLACE_TARGET_IP`를 읽는다. URL 목적지와 서버 NIC의 fixed IP가 다른 NAT 경로라면 변환 전후·관찰 위치를 나눈다. 같은 subnet의 직접 전달과 router 경유를 구별하고 반환도 그린다. Linux의 선택 dev/via/src와 클라우드 객체를 연결하되 실제 packet 통과는 A2에서 확인한다.

## 필수 A2 · 같은 요청을 양끝에서 확인

새 실행 파일은 [1주차 server.py](../../labs/week-01/server.py)의 `Handler`를 그대로 쓴다. 두 파일을 **같은 본인 실습 폴더**에 둔다. 서버 코드를 수정하거나 기존 1주차 바인딩을 바꾸지 않는다.

- <a download href="../../labs/week-13/cloud_service.py">cloud_service.py 내려받기</a>
- <a download href="../../labs/week-01/server.py">재사용 server.py 내려받기</a>

Python3.10+·curl·ip·ss가 필요하다. 서버 셸에서 `SERVER_PRIVATE`를 VM에 실제 설정된 허가된 IPv4로 치환하고 시작한다. floating IP나 `0.0.0.0`을 넣지 않는다. 출력은 이 셸에 보존한다.

```sh
SERVER_PRIVATE='REPLACE_SERVER_FIXED_IP'
python3 cloud_service.py --bind "$SERVER_PRIVATE" --port 8080
```

다른 서버 셸의 `ss -lntp`에서 **그 주소:8080 LISTEN**을 찾는다. 서버 자신의 사설 주소로 `/echo?message=w13-local`을 요청해 프로그램부터 확인한다. 루프백에 bind하지 않았으므로 루프백 URL을 쓰지 않는다. 이 로컬 요청은 클라우드 ingress 검증이 아니다.

### 테스트 허용 규칙 준비

본인 관리 셸에서 값을 실제 허가된 전용 그룹 ID·정책이 보는 출발지 `/32`로 치환한다. 이미 같은 규칙이 있으면 소유권/사용처를 확인하며 **남의 규칙을 삭제하거나 새 규칙으로 간주하지 않는다**. 중복/소유권이 불명확하면 전용 환경을 준비해 보충한다.

```sh
TEST_GROUP='REPLACE_DEDICATED_GROUP_ID'
CLIENT_CIDR='REPLACE_VERIFIED_CLIENT_IPV4/32'
openstack security group rule create --ingress --ethertype IPv4 --protocol tcp --dst-port 8080 --remote-ip "$CLIENT_CIDR" --description w13-owned-http "$TEST_GROUP"
```

성공한 출력의 **새 rule ID**와 ingress/IPv4/TCP/8080/remote IP/group을 따로 보관한다. 실패·결과 불명이면 목록/상세를 다시 조회해 실제 생성 여부를 확인한다. 같은 생성 명령을 무작정 반복하지 않는다. 아직 규칙이 반영되지 않았으면 조회/새 요청으로 확인한다.

클라이언트 Linux 셸에서 실제 접근 대상 주소를 정하고 새 curl 프로세스로 요청한다. VM 간이면 보통 fixed IP, 허가된 PC 경로면 확인한 주소를 쓴다.

```sh
TARGET='REPLACE_REACHABLE_TARGET_IP'
curl --noproxy '*' --connect-timeout 3 --max-time 8 -iv "http://$TARGET:8080/echo?message=w13-before"
printf 'exit=%s\n' "$?"
```

정상 기준은 종료0·HTTP200·`w13-before` 본문, 서버 JSON의 같은 path/message·status200·client 주소다. `client`는 **서버가 본** 주소/임시 TCP포트로 PC 원래 주소와 같지 않을 수 있다. timestamp가 없는 1주차 로그는 요청의 고유 message와 실행 순서로 대응한다. 매 실습의 꼬리표는 겹치지 않게 정하고 비밀값은 넣지 않는다. `/missing`의 HTTP404는 서비스가 응답한 것이며 TCP 차단과 다르다.

<span id="policy-change"></span>

## 필수 A3 · 본인 규칙 하나 제거→새 요청→복구

서버·경로·출발지·포트는 유지한다. 관리 셸에서 본인이 방금 만든 rule만 고른다. 아래는 한 줄씩 실행하고 실제 출력이 예상과 다르면 멈춘다.

```sh
OWN_RULE='REPLACE_JUST_CREATED_RULE_ID'
openstack security group rule show "$OWN_RULE"
```

show 결과를 A2의 본인 생성 출력과 대조한다. 일치한 **TCP 8080 ingress 허용 하나만** 제거한다. 관리/다른 서비스 규칙은 대상이 아니다.

```sh
openstack security group rule delete "$OWN_RULE"
openstack security group rule list --long "$TEST_GROUP"
```

클라이언트에서 message만 `w13-block`으로 바꿔 같은 curl 명령을 **새 프로세스로** 실행한다. 이 사례의 예상은 제한 시간 실패·HTTP 없음, 서버 LISTEN 유지·해당 GET 로그 없음이다. 실제 구현은 거부 오류 등 다른 현상을 보일 수 있으므로 종료 코드/정책/양끝 근거를 읽는다. 계속200이면 중복 허용·잘못된 그룹/port·상태 추적/전파를 재확인하고 관리 규칙/연결 추적을 지워 억지로 실패시키지 않는다.

결과와 관계없이 준비한 복구를 실행한다. **A2와 같은 create 명령**으로 동일한 방향·주소족·프로토콜·포트·remote IP·group을 복구하고 새 ID를 기록한다. ID가 바뀌어도 정책 조건이 같은지를 비교한다. 생성 실패 시 콘솔/정책 소유자에게 복구를 맡기고 복구 완료로 표시하지 않는다.

```sh
openstack security group rule create --ingress --ethertype IPv4 --protocol tcp --dst-port 8080 --remote-ip "$CLIENT_CIDR" --description w13-owned-http "$TEST_GROUP"
```

다시 조회한 뒤 `w13-after` 새 요청의0·200·본문·서버 로그를 확인한다. 이전 성공 로그를 복구 증거로 쓰지 않는다. 권한이 없으면 [가공 cloud-case](../../labs/week-13/cloud-case.txt)의 C0\~C3을 분석하고 직접 운영은 보충한다. [11주차 격리 변경/복구](../week-11/LINUX.md)는 그 환경의 직접 수행 근거이며 실제 보안 그룹 변경으로 대체하지 않는다.

<span id="identity"></span>

## A4 · 기존 DNS·TLS 근거를 같은 대상에 연결

5\~6주의 본인 출력에서 질의한 이름/리졸버/주소족, URL 이름·실제 주소·CA/기간/SAN·검증 결과를 찾아 자기 서비스 경로에 대응한다. 다른 VM·루프백의 예제였다면 그 차이를 밝힌다. 연결하지 못한 항목은 아래 준비된 대상으로 보충하며 이름/인증서 초기 생성은 진행자가 맡는다.

1. 허가된 테스트 이름이 준비되었다면 클라이언트의 `getent ahostsv4 study.test`와 기존 DNS 질의 도구로 실제 A/리졸버·캐시 조건을 확인한다. `getent`는 NSS 설정에 따라 hosts도 볼 수 있으므로 이것만 DNS 패킷 증거로 부르지 않는다. 이름이 없으면 결과를 만들어 내거나 공용 DNS/hosts를 임의 변경하지 않는다.
2. 서버는 [6주차 인증서 준비](../week-06/FACILITATOR.md#tls-setup)의 CA·`study.test` SAN 서버 인증서를 사용한다. 짧은 인증서는 사용할 날 유효기간을 확인한다. CA **공개** 인증서만 별도 신뢰 경로로 클라이언트에 전달한다. 서버/CA 개인키는 공유하지 않는다.
3. 기존 HTTP 서버와 별도 셸에서 아래 TLS listener를 같은 VM의 실제 주소에 켠다. 준비자가 TCP8443의 해당 출발지만 허용하는 정책·호스트 정책을 미리 확인한다. 이 규칙은 A3의 변경 대상8080과 구별한다.

```sh
python3 cloud_service.py --bind "$SERVER_PRIVATE" --port 8443 --cert REPLACE_SERVER_CERT_PEM --key REPLACE_SERVER_KEY_PEM
```

클라이언트 실습 폴더에 확인한 `ca.pem`을 두고 아래 정상→이름 변경→복구를 비교한다. `TARGET`은 A2와 같은 확인된 접근 주소다. 인증서 이름은 `study.test`이고 DNS/hosts 변경 없이 주소를 지정한다.

```sh
curl --noproxy '*' --connect-timeout 3 --max-time 8 --cacert ca.pem --resolve "study.test:8443:$TARGET" -iv 'https://study.test:8443/echo?message=w13-tls-before'
printf 'exit=%s\n' "$?"
curl --noproxy '*' --connect-timeout 3 --max-time 8 --cacert ca.pem --resolve "wrong.test:8443:$TARGET" -iv 'https://wrong.test:8443/echo?message=w13-tls-wrong'
printf 'exit=%s\n' "$?"
curl --noproxy '*' --connect-timeout 3 --max-time 8 --cacert ca.pem --resolve "study.test:8443:$TARGET" -iv 'https://study.test:8443/echo?message=w13-tls-after'
printf 'exit=%s\n' "$?"
```

정상/복구는 검증을 켠 종료0·HTTP200·같은 message의 서버 로그, 이름 변경은 검증 실패(통상 curl60)·HTTP 없음·해당 GET 없음이 기준이다. `--resolve` 비교는 **DNS 성공을 증명하지 않으며**, 실제 이름 해석은1번 근거로 분리한다. 기존 루프백 TLS만 있거나 현재 원격8443이 막히면 준비/보충을 남긴다. `-k`·시스템 CA 추가·인증 경고 제거를 복구로 쓰지 않는다.

### 정리와 직접 수행 근거

HTTP/TLS 서버의 **자기 실행 셸에서 Ctrl+C**로 각각 종료하고 `ss -lntp`로 해당 listener가 사라졌는지 확인한다. A3 복구 결과를 남긴 후 관리 셸에서 복구 때 새로 생성한 본인8080 rule ID를 show로 재확인해 제거하고 실습 전 규칙 상태로 돌린다. 임시8443 rule을 준비자가 만들었다면 그 소유자가 자기 rule만 정리한다. 그룹/기존 규칙·주소·router·관리 접속은 유지한다.

근거는 O01 자원/왕복 그림, O02 주소·대기·이름/TLS·양끝 요청, O03 동일조건의 정책 전후/복구로 묶어 개인 파일에 한 번 보관한다. 직접 수행과 제공 분석·미확인을 구별한다. 복구가 불명확하면 정상200만 보고 정리를 끝내지 않는다.

<span id="mtu-analysis"></span>

## 필수 B · 크기 사례 분석

<a download href="../../labs/week-13/mtu-cases.txt">mtu-cases.txt 내려받기</a>의 M0\~M4는 **가공 사례·계산**이다. 실제 VM MTU·학교 내부 터널·패킷을 조회한 기록이 아니다.

- M0에서 내부 IP1450/1500이 각각 바깥 IP에서 차지하는 크기와 한도를 비교한다. 외부 Ethernet을 중복 차감하지 않는다.
- M1의 작은/큰 패킷과 DF·ICMP를 읽고 송신자의 다음 행동을 설명한다. 같은 HTTP URL의 성공/실패를 패킷 길이와 동일시하지 않는다.
- M2에서 조각 두 개의 데이터 합·8바이트 배수·offset을 검산한다. 조각의 헤더 비용 때문에 전체 전송량이 원래 IP 길이보다 커지는 이유를 말한다.
- M3에서 IPv6 라우터/출발지의 역할과 ICMPv6를 비교한다.
- M4의 IPv4/IPv6 TCP 데이터 예산과 옵션 12bytes 조건을 계산한다. MSS 광고와 실제 데이터 길이를 구별한다.

실제 크기 변경은 필수가 아니다. 선택 격리 환경이 있다면 진행자가 별도 콘솔·정상 설정·복구를 준비해 관찰 위치/방향·패킷 크기를 맞춘다. 관리 VM의 MTU·기본 경로·ICMP 정책을 바꾸지 않는다. 호스트 캡처는 offload 때문에 큰 버퍼처럼 보일 수 있어 실제 선로 패킷 크기로 바로 단정하지 않는다.

<span id="code-reading"></span>

## 코드 읽기 · 새로 구현한 HTTP는 없다

| 단계 | 읽을 코드/문법 | 이유와 관찰 |
| --- | --- | --- |
| 가져오기 | `from server import Handler` | 같은 폴더의1주차 GET 처리기를 재사용. 파일이 없으면 import 오류로 시작 못 함 |
| 입력/검사 | argparse·IPv4Address·범위·cert/key 쌍 | 주소 하나/비특권 port, 잘못된 입력·인증서 준비 오류는 listener 전에 중단 |
| TLS 준비 | SSLContext·load_cert_chain | 인증서가 있을 때만 TLS를 씌움. 없으면 HTTP. TLS1.2 이상, 실제 협상은 클라이언트 결과로 확인 |
| 실행/종료 | `with ThreadingHTTPServer`·try/except | 해당 로컬 주소에 대기, 오류는 종료1, Ctrl+C 후 socket 정리 |
| 응답 | 1주차 `do_GET`·urlsplit/parse_qs·JSON | `/echo`200·다른 path404, UTF-8 bytes/Content-Length와 서버 response 로그, 요청마다 연결 닫힘 |

`--bind`를 바꿔도 경로/보안 그룹을 자동 생성하지 않는다. Handler의 원래 루프백 실행은 그대로다. 정상200→없는 경로404→정상200, 잘못된 bind/port·파일 누락·인증서 오류·포트 충돌·종료를 구별한다. TLS 실패 때 HTTP 로그가 없다는 사실이 TCP 시도도 없었다는 뜻은 아니다. 코드 설명을 읽은 것과 본인이 실행/설명한 것은 별도로 확인한다.

<a download href="../../labs/week-13/cloud-case.txt">가공 cloud-case.txt 내려받기</a> · [문제](REVIEW.md) · [분리 해설](ANSWERS.md) · [출처](SOURCES.md)
