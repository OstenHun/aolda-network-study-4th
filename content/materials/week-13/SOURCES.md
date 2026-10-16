# 13주차 · 공식 근거와 짧은 읽기

요약: 클라우드 객체·보안 그룹과 IPv4/IPv6 크기 처리의 필요한 공식 절만 함께 읽는다. CLI·Python·curl은 실습 근거로 찾으며 전체 문서 필독을 요구하지 않는다. 제공 주소·기록·문항은 자체 가공 자료다.

## 필수 공동 읽기 · 약 10분 추정

기존 공동 탐색 20분 중 아래 약 10분을 읽고 나머지 시간은 교재/자기 출력에 대응한다. 시간은 추정이며 실제 초보자 소요 시간은 사용 때 다시 확인한다. 세 문서 전체를 추가로 읽거나 발표를 준비할 필요는 없다.

| 공식 문서·지정 범위 | 목적·함께 찾을 것 | 분량 |
| --- | --- | --- |
| [Neutron Intro의 Subnets·Ports·Routers·Security groups](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html#subnets): 앞 세 소절의 정의, Security groups의 도입 두 문단과 stateful 문단만 | subnet/port/router의 역할, port 단위 규칙·합쳐진 허용·반환 추적. anti-spoofing 상세 목록은 제외 | 필수 4분 |
| [RFC1191 §2 Protocol overview](https://www.rfc-editor.org/rfc/rfc1191.html#section-2): 첫 두 문단 | IPv4 DF·too big·ICMP 통보 뒤 송신자의 PMTU 조절. 옛 576 기본값 권고를 현재 운용에 복사하지 않음 | 필수 3분 |
| [RFC8200 §4.5 Fragment Header](https://www.rfc-editor.org/rfc/rfc8200.html#section-4.5)의 도입 문단과 [§5 Packet Size Issues](https://www.rfc-editor.org/rfc/rfc8200.html#section-5)의 첫 두 문단 | 출발지만 단편화/라우터는 하지 않음, 최소 링크 MTU1280·하위 적응. 상위 프로토콜 상세는 선택 | 필수 3분 |

ingress/egress는 port 기준 방향, PMTU는 경로에서 가장 작은 MTU, DF는 단편화 금지, PTB는 너무 큰 패킷 통보다. 막히면 [K1 자원표·K2 관찰표·K3 크기 식](CONCEPTS.md)으로 돌아가 같은 말을 한국어로 찾는다. 명령 실행은 [실습](LINUX.md)의 현재 허가/복구 조건부터 확인한다.

## 선택·명령/기술 근거

확인일은 2026-10-17 KST다. latest의 제품 버전과 실제 클라우드/CLI 버전은 다를 수 있어 현재 help·콘솔 출력과 대조한다. 다음은 필독 추가분이 아니라 필요한 절을 찾는 목록이다.

| 자료 | 사용할 절·채택 범위 | 읽기 목적/선택 분량 |
| --- | --- | --- |
| [OpenStack 조회·규칙](https://docs.openstack.org/python-openstackclient/latest/cli/command-objects/network/v2/index.html#security-group-rule-create) | port, network, subnet, router, floating ip의 조회와 그룹/규칙의 list·show. rule create의 방향·주소족·프로토콜·목적 포트·출발지·설명, delete의 rule ID | 실습 조회/본인 규칙의 생성·복구 근거. 필요한 명령당 선택 1\~2분 |
| [VM 조회](https://docs.openstack.org/python-openstackclient/latest/cli/command-objects/compute/v2/index.html#server-show) | server show | VM 조회 근거·선택 1분. 인증 설정/생성은 범위 밖 |
| [Neutron 가상망](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html#self-service-networks) | Self-service networks: network 종류와 NAT/floating IP·다양한 구현 도입 | 논리 자원과 실제 배포 구별·선택 3분. 이 클라우드의 VXLAN/특정 L3 agent를 단정하는 근거로 쓰지 않음 |
| [RFC6691 §2](https://www.rfc-editor.org/rfc/rfc6691.html#section-2) | MSS 광고는 고정 헤더 차감, 실제 송신 데이터는 옵션 고려 | K3/M4·선택 2분 |
| [RFC791 §3.1](https://www.rfc-editor.org/rfc/rfc791.html#section-3.1) | Flags·Fragment Offset·Total Length 필드 | M2의 DF/MF·8byte offset·헤더 구별·선택 3분 |
| [RFC1191 §4](https://www.rfc-editor.org/rfc/rfc1191.html#section-4) | Router specification·ICMP 형식/next-hop MTU | IPv4 type3/code4·선택 2분 |
| [RFC8201 §1·§3·§6](https://www.rfc-editor.org/rfc/rfc8201.html#section-1) | Introduction의 PTB 차단/black hole, Protocol Overview의 크기 조절, Security Considerations의 PLPMTUD 구별 | IPv6 PMTUD/black hole·선택 3분. 모든 구현의 유일한 탐지 방식으로 일반화하지 않음 |
| [RFC4443 §3.2](https://www.rfc-editor.org/rfc/rfc4443.html#section-3.2) | Packet Too Big 형식/type2/code0·MTU | M3의 오류 통보 필드·선택 2분 |
| [Python HTTP](https://docs.python.org/3/library/http.server.html) | HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler, 학습용 서버의 보안 한계 | 기존 1주 Handler/실행기·선택 3분. 운영 서비스로 권장하지 않음 |
| [Python TLS](https://docs.python.org/3/library/ssl.html) | SSLContext의 서버 모드, minimum_version, load_cert_chain, wrap_socket | 준비된 인증서·TLS 실행기·선택 3분 |
| [curl SSL Certificates](https://curl.se/docs/sslcerts.html)·[curl manpage --resolve](https://curl.se/docs/manpage.html#--resolve) | Verification·CA file·resolve의 host/port/address 매핑 | A4의 검증/강제 매핑, 5\~6주 재사용·선택 3분 |

## 출처와 관찰의 경계

OpenStack 공식 설명은 제품의 가능한 구성과 기본 동작이며 학교/개인 클라우드의 현재 설정 조회가 아니다. RFC는 지정한 프로토콜/범위를 지지하고 구현의 현재 설정/보안 권고 전체를 보장하지 않는다. Python 버전별 새 HTTPSServer에 의존하지 않고 기존 ThreadingHTTPServer·SSLContext를 쓴다.

가공 cloud-case·mtu-cases·핵심 기억 문장·개발 질문/복습/해설은 자체 작성이다. 1주차 Handler·5\~6주 DNS/TLS·11주 격리 정책·12주 경로/보호 경계를 재사용하며 기업 기출로 표시하지 않는다. 외부 원문·그림·문제/코드를 길게 복제하지 않고 필요한 주장을 자체 설명해 공식 절로 연결한다. 실제 운영/참가자 이해는 본인 환경 근거로 확인한다.
