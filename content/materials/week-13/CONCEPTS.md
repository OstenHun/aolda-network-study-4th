# 13주차 · 가상 자원과 실제 요청, 크기의 경계

요약: 가상 network·subnet·port·router와 보안 그룹을 실제 왕복 요청에 대응한다. DNS·바인딩·정책·TLS·서비스를 나누고 MTU·MSS·캡슐화·IPv4/IPv6 PMTUD를 제공 사례로 설명한다.

[개인 공부 정리](README.md#personal-notes)에서는 이 교재의 핵심·혼동 구별을 주요 질문과 내 답에 연결한다. 먼저 설명하고 해설과 비교한 뒤, 확인한 근거와 고친 이해를 기존 개인 노트에 보완한다.

## 앞 개념에서 출발하기

`ip route get`은 내 커널의 선택을 보여 준다. [7주차](../week-07/CONCEPTS.md)의 조회 성공만으로 왕복 통신이 증명되지는 않는다. [11주차](../week-11/CONCEPTS.md)에서 주소 변환과 접근 허용을, [12주차](../week-12/CONCEPTS.md)에서 터널과 암호화를 나눴다. 이번에는 그 역할을 자기 클라우드의 실제 설정과 양끝 관찰에 붙인다.

<span id="cloud-objects"></span>

## W13-K1 · 자원 이름을 주소·연결점·다음 홉에 대응한다

**기억 문장:** VM이 실행 중이라는 상태와 요청을 전달할 경로·정책·서비스가 갖춰졌다는 상태는 다르다.

| 자원 | 역할과 조회할 값 | 혼동하지 않을 것 |
| --- | --- | --- |
| project / VM | 자원의 소유 범위 / 실행하는 가상 컴퓨터. 실제 선택한 프로젝트·VM ID | 같은 프로젝트가 모든 통신 허용을 뜻하지 않음 |
| network / subnet | 가상 연결망 / 주소 블록·gateway·주소 할당 설정 | 화면의 network 이름과 Linux 인터페이스 이름은 같을 필요 없음 |
| Neutron port | VM NIC 등을 망에 연결하는 객체. fixed IP·MAC·network·보안 그룹 | TCP 8080 같은 전송 계층 포트 번호와 다른 의미 |
| router | 서로 다른 망 사이 L3 전달·필요한 NAT. 연결 subnet·외부 gateway·경로 | 같은 subnet의 VM 간 요청이 항상 router를 거치지는 않음 |
| security group | port에 적용되는 ingress/egress 허용 규칙 묶음 | IP 경로나 애플리케이션 listener를 만들지 않음 |

fixed IP는 port에 할당된 주소다. floating IP는 외부에서 fixed IP로 연결할 때 쓰는 주소/NAT 대응일 수 있다. 모든 환경에 floating IP가 있거나 필요한 것은 아니다. 기존 VPN/사내 경로로 사설 주소를 직접 쓰는 경우와 구별한다. [Neutron의 Subnets·Ports·Routers·Security groups](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html#subnets)가 정의의 근거다.

```text
허가된 클라이언트 → 실제 목적지 주소 → [필요한 경로·NAT] → 서버 port/보안 그룹
                                                           ↓
클라이언트 결과 ← 반환 경로·필요한 역변환 ← 호스트 정책 ← 주소:TCP포트의 서비스
```

이 그림은 논리적 확인 지점이다. 구현상 보안 그룹/NAT가 어느 물리 장비에서 실행되는지까지 확정하지 않는다. 같은 subnet이라면 직접 경로, 다른 subnet이라면 선택된 다음 홉을 자기 출력에 맞춰 그린다. 외부 주소로 요청했다면 변환 전후 목적지와 서버가 본 출발지를 따로 적는다. 자기 VM의 `ip`·`ss` 출력만으로 물리 호스트의 스위치·VXLAN 사용을 알아냈다고 하지 않는다.

## W13-K2 · 이름·경로·허용·대기·신원을 순서대로 구별한다

**기억 문장:** DNS 성공은 주소를 얻은 근거이고, 서비스 성공은 올바른 대상까지 요청·검증·응답을 확인한 근거다.

바인딩은 프로그램이 받을 로컬 주소/포트를 정하는 일이다. `127.0.0.1:8080`에만 대기하면 다른 VM이 서버의 사설 주소로 보내는 요청을 받지 못한다. `0.0.0.0`은 모든 로컬 IPv4 인터페이스를 대상으로 하는 바인딩 값이며 접속 URL에 쓸 원격 주소가 아니다. 이번 실습은 허가된 주소 **하나**를 명시한다. 클라우드 floating IP가 VM에 직접 설정되지 않았다면 그 주소에 bind하지 않는다.

| 확인 지점 | 관찰할 근거 | 그 근거만으로 모르는 것 |
| --- | --- | --- |
| 이름 해석 | `getent ahostsv4`, 기존 DNS 질의의 A/AAAA·캐시 조건 | 호스트/리졸버/NSS의 결과와 실제 DNS 응답은 구분. TCP 성공은 미확인 |
| 경로·정책 | 양쪽 route get, port의 모든 보안 그룹, 호스트 정책 | 조회만으로 실제 패킷 통과/반환 보장 못 함 |
| 서비스 대기 | 서버 `ss -lntp`의 로컬 주소·포트/프로세스 | 클라이언트에서 접근 가능하다는 뜻 아님 |
| TLS 신원 | URL 이름·SAN·신뢰 CA·유효기간, 검증을 켠 curl | DNS 성공이나 HTTP 사용자 로그인과 다름 |
| 요청·응답 | curl의 실제 연결 대상/종료 코드·상태·본문과 서버의 같은 요청 로그 | HTTP200 하나가 모든 경로/크기/부하의 정상은 아님 |

OpenStack 보안 그룹은 허용 규칙을 합쳐 적용한다. 특정 그룹에서 허용을 빼도 다른 적용 그룹에 전체 프로토콜·넓은 CIDR·remote group 허용이 남으면 요청이 될 수 있다. 명시적 deny를 앞에 끼워 넣는 [11주차 nft 순서 모형](../week-11/CONCEPTS.md)과 구별한다. stateful 그룹은 허용된 흐름의 반환을 추적하지만 stateless 설정·구현/운영 정책은 실제 조회로 확인한다. **NAT는 주소 변환이지 접근 허가가 아니다.** [공식 Security groups](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html#security-groups)를 기준으로 자기 설정을 대조한다.

새 요청을 보내며 조건을 한 가지씩 바꾼다. curl 제한 시간 실패와 새 HTTP 로그 없음은 요청이 HTTP 처리까지 오지 않았다는 단서다. 이것만으로 보안 그룹 차단을 확정하지 않는다. 경로·호스트 정책·잘못된 대상·관찰 위치도 후보이며 변경 전후 설정과 복구가 함께 있어야 한다. 기존 연결/상태 캐시·정책 전파 시간 때문에 삭제 직후 모든 연결이 끊어진다고 약속하지 않는다.

5\~6주 근거는 이름→실제 대상→검증 이름/CA→HTTP 로그 순서로 이 서비스에 연결한다. `--resolve`는 주소를 강제로 정하면서 URL 이름/SNI/검증 이름을 유지하므로 DNS 장애와 TLS 이름 문제를 나누는 비교에 쓴다. **실제 DNS가 정상이라는 증거는 아니다.** [curl 인증서 안내](https://curl.se/docs/sslcerts.html)와 [6주차 TLS](../week-06/LINUX.md#tls-lab)를 재사용한다.

<span id="packet-size"></span>

## W13-K3 · 패킷의 크기는 경계를 지날 때 다시 계산한다

**기억 문장:** MTU는 링크의 IP 패킷 크기 한도이고 MSS는 TCP 데이터 한도다. 캡슐화로 바깥 헤더가 붙으면 같은 망에서 내부 데이터에 남는 공간이 줄 수 있다.

MTU(maximum transmission unit)는 링크가 한 번에 운반하는 IP 패킷의 최대 크기다. PMTU(path MTU)는 특정 방향의 경로가 허용하는 최소 링크 MTU이며 로컬 인터페이스 MTU와 같을 필요가 없다. MSS(maximum segment size)는 TCP가 받을 수 있다고 광고하는 **TCP 데이터** 최대 크기다. IP/TCP 헤더·HTTP 본문·Ethernet 프레임 전체 크기와 다르며, 실제 송신은 상대 MSS와 PMTU·옵션 등을 함께 고려한다.

```text
외부 IP 패킷 = [외부 IP·터널 헤더 등 H] + [내부 IP 패킷]
외부 IP MTU 1500, 주어진 추가 비용 H=50 → 내부 IP 한도 1450
내부 IPv4 20 + TCP 20 + 데이터 1410 = 1450 (옵션 없음)
```

H=50은 [제공 사례 M0](../../labs/week-13/mtu-cases.txt)의 가정이다. 내부 Ethernet까지 포함한 추가 비용인지, 외부 IP MTU/프레임 중 어느 크기를 기준으로 하는지 맞춰야 한다. 같은 헤더를 두 번 빼지 않는다. 이 수치를 실제 클라우드의 VXLAN 설정이나 모든 터널의 고정 비용으로 쓰지 않는다. 암호화·패딩·VLAN·외부 IPv6에 따라 달라진다.

| IP MTU 1450, 옵션/확장 헤더 없음 | 기본 헤더 | TCP 데이터 예산 |
| --- | --- | --- |
| IPv4 + TCP | 20 + 20 bytes | 1410 bytes |
| IPv6 + TCP | 40 + 20 bytes | 1390 bytes |

IPv4 TCP 옵션 12bytes를 실제 넣는 세그먼트는 데이터 예산이 1398bytes로 줄어든다. **MSS 광고값** 계산에서는 고정 IP/TCP 헤더만 빼며, 송신자는 실제 옵션/확장 헤더만큼 데이터 길이를 조절한다. 모든 패킷이 광고 MSS만큼 가득 차거나 모든 TCP의 MSS가 1410이라는 뜻은 아니다. [RFC6691 §2](https://www.rfc-editor.org/rfc/rfc6691.html#section-2)의 광고와 실제 전송 구별을 따른다.

### IPv4·IPv6·ICMP를 함께 읽기

| 너무 큰 IP 패킷이 라우터에 도착 | 기본 처리와 필요한 근거 |
| --- | --- |
| IPv4 DF=0 | 단편화가 가능하다. 조각마다 IP 헤더가 생기고 목적지에서 재조립한다. 중간 정책이 조각을 버릴 수도 있음 |
| IPv4 DF=1 | 라우터가 단편화하지 못해 폐기하고 ICMP type3/code4와 다음 홉 MTU를 돌려준다. 송신자가 PMTU를 낮춰 크기를 조절하는 것이 고전 PMTUD |
| IPv6 | 라우터는 단편화하지 않는다. ICMPv6 Packet Too Big(type2/code0)로 알리고 송신자가 크기를 조절하거나 필요한 경우 출발지에서 단편화 |

PMTUD는 Path MTU Discovery, 경로 MTU를 알아내는 절차다. IPv4의 DF는 Don't Fragment, 단편화하지 말라는 비트다. ICMP는 오류/제어 정보를 전달하며 echo(ping)만을 뜻하지 않는다. 크기 통보가 차단되면 작은 요청/핸드셰이크는 되는데 큰 데이터가 멈추는 상황이 가능하다. 다만 같은 증상에 서버 처리·응답 정책·손실 등 다른 원인이 있으므로 **증상만으로 MTU 확정은 금물**이다. 전송 계층 탐지 등 다른 구현도 있어 모든 전송을 ICMP 하나로만 설명하지 않는다.

[RFC1191 §2/§4](https://www.rfc-editor.org/rfc/rfc1191.html#section-2)·[RFC8200 §4.5](https://www.rfc-editor.org/rfc/rfc8200.html#section-4.5)/[§5](https://www.rfc-editor.org/rfc/rfc8200.html#section-5)·[RFC8201 §1/§3/§6](https://www.rfc-editor.org/rfc/rfc8201.html#section-3)를 제공 사례와 대조한다. IPv6 링크의 최소 1280 요구와 그보다 작은 매체의 하위 적응은 별도 조건이며 여기의 1450 사례와 충돌하지 않는다. 실제 MTU/ICMP 설정 변경은 선택 격리 실험으로 남긴다.

## 헷갈리는 구별 두 가지

1. **가상 port와 TCP port:** 전자는 NIC 연결 객체·IP/MAC/그룹, 후자는 전송 계층 서비스 번호다. 같은 번호라고 대응하지 않는다.
2. **MTU와 MSS:** 전자는 IP 패킷/경로의 제약, 후자는 TCP 데이터 광고다. UDP·HTTP 본문 전체를 MSS로 나누거나 MTU를 인증/접근 허가로 설명하지 않는다.

## 개발 사례 · 이름은 맞는데 요청이 멈춘다

사설 테스트 이름이 올바른 주소를 반환하고 VM은 실행 중이다. 클라이언트는 시간 제한에 걸렸으며 서버의 GET 로그는 없다. W13-D1\~D3은 [함께 찾을 질문](WORKSHEET.md), 필수 답안 요소는 [분리 해설](ANSWERS.md#development)에 있다. 먼저 경로·대기·정책을 구별한 뒤 크기 의존 증상이 추가될 때 다른 관찰을 고른다.

[직접 실습/제공 분석](LINUX.md) · [공식 읽기 범위](SOURCES.md) · [개념 색인](../CONCEPT_INDEX.md)
