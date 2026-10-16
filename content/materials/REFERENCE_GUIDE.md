# 네트워크 스터디 참고자료 안내

요약: 로드맵은 16주 학습 범위, 자체 교재는 입문 설명과 실습, Kurose·Ross는 패킷 관찰에 활용한다. 공식 자료의 읽을 범위와 실제 Linux 실행 검증을 구분한다.

1주차 참가자는 [필수/선택 읽기와 시간](week-01/SOURCES.md)을 먼저 확인한다. 16주 전체 목록을 1주차 과제로 읽지 않는다.

## 자료를 고르는 방법

- 아래 공식 자료의 소개·목차에서 학습할 범위를 확인한다. 원문 읽기와 실제 Linux 직접 실행은 구분한다.
- 주차별 학습 목표는 [16주 커리큘럼](../CURRICULUM.md)에서 확인하고, 이 문서는 참고자료의 위치와 읽을 범위를 찾는 데 쓴다.
- 주차별 필수 자료 1~2개의 지정 절을 먼저 읽는다. 영어 원문 전체 정독이나 사이트의 모든 과제 완료를 공통 과제로 두지 않는다.
- 초반에는 [자체 교재](week-01/index.html)의 설명과 안내 실습으로 시작하고, 독립 재현은 그때까지 배운 범위에서 진행한다.
- 실습 전 Linux 접속·도구·권한을 확인한다. 접속이 막히면 제공 출력·캡처를 함께 분석하고 직접 실행은 별도로 보충한다. 개인 PC는 SSH·자료 읽기·패킷 분석에 사용한다.

## 범위와 기초 설명

| ID | 공식 자료 | 이번 스터디에서 읽을 범위 |
| --- | --- | --- |
| R01 | [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer) | Introduction, 모델·장치·주소, Core/Application Protocols, Switching/Routing, Security, Wireless, Cloud, 관측·자동화의 범위 지도. 나열 순서를 16주 수업 순서로 그대로 사용하지 않음 |
| R02 | [MIT Missing Semester](https://missing.csail.mit.edu/) | 터미널 열기·이동·명령 실행, 필요할 때 SSH·셸·Git 항목. 네트워크 본 과정의 선수 과목 전체로 요구하지 않음 |

R01의 상세 그래프는 공식 페이지의 공개 로드맵 데이터에서 항목명을 확인했다. 16주의 순서·필수 분량·평가는 이 스터디를 위한 설계이며 roadmap.sh의 공식 16주 과정이 아니다.

## 자체 교재와 실습

[1주차 학습 홈](week-01/index.html)에서 개념 교재·Linux 실습·팀 활동·복습 문제·해설을 찾을 수 있다. [실행 키트](../labs/week-01/README.md)의 명령과 예상 출력은 사용할 Linux 환경에서 먼저 확인한다. 참가자의 직접 실행, 진행자의 시연, 제공 출력·캡처 분석을 각각 구분해 기록한다.

2~16주차 실습은 [커리큘럼](../CURRICULUM.md)의 질문을 기준으로 주차 준비 때 만든다. 주소 계산·이웃 캐시·소켓·DNS·정책 변경은 그 주에 사용할 명령과 권한을 확인한 뒤 안내한다. 접속 또는 캡처가 막혀 제공 자료로 분석했다면 개인 실행이나 직접 캡처 완료로 표시하지 않는다.

## 패킷 관찰과 공식 기술 자료

| ID | 공식 자료 | 활용 범위 |
| --- | --- | --- |
| P01 | [Kurose·Ross Wireshark Labs](https://gaia.cs.umass.edu/kurose_ross/wireshark.php) | Getting Started, HTTP, Ethernet/ARP, ICMP, TCP/UDP, DNS/DHCP, TLS, WiFi 중 주차 질문과 관련된 부분만 선택. 실습 자료와 예제 trace 목록이 있음 |
| P02 | [Cisco Getting Started with Packet Tracer](https://www.netacad.com/courses/getting-started-cisco-packet-tracer/1000) | 시뮬레이터 소개·다운로드·기본 조작. 공식 소개의 무료·2시간 입문 과정. 가입·설치·로그인 조건은 사용 전에 확인 |
| P03 | [Cisco 802.1Q Trunking](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6000-series-switches/10599-88.html) | 트렁크와 태그의 Background Theory. 오래된 장비별 명령을 모든 시뮬레이터에 그대로 적용하지 않음 |
| P04 | [RFC 8200 — IPv6](https://www.rfc-editor.org/rfc/rfc8200) | 진행자가 IPv6 기본 헤더·주소 체계와 IPv4 비교 설명을 검증할 때 사용. 참가자 전체 정독 과제 아님 |
| P05 | [RFC 1191 — Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc1191) | IPv4 MTU·크기·ICMP 관계를 확인하는 진행자 참고. IPv6 동작과 혼용하지 않음 |
| P06 | [OpenStack Networking concepts](https://docs.openstack.org/neutron/latest/install/concepts.html) · [OpenStack Networking](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html) | network/subnet/port/router/security group 용어. 일반 문서이며 아올다의 현재 구현·권한·기본 정책을 확인한 증거는 아님 |
| P07 | [OpenStack Overlay protocols](https://docs.openstack.org/neutron/latest/admin/intro-overlay-protocols.html) | 캡슐화·VXLAN·오버레이의 선택 개념 설명. 아올다 운영망이 해당 방식이라고 가정하지 않음 |
| P08 | [Wireshark I/O Graphs](https://www.wireshark.org/docs/wsug_html_chunked/ChStatIOGraphs.html) | 캡처 구간의 트래픽을 시간에 따라 비교. 화면의 값과 단위·측정 위치를 함께 읽음 |
| P09 | [Python urllib.request](https://docs.python.org/3/library/urllib.request.html) | 작은 요청·오류 처리 자동화의 공식 API 참고. 1주차 키트의 TypeScript 경로를 계속 사용해도 됨 |

Kurose·Ross 자료를 수업에 사용할 때 출처를 밝힌다. 웹에 수정본을 게시한다면 원저작자·저작권과 수정 여부를 표시한다. 외부 자료의 본문 전체를 자체 교재에 복제하지 않고 필요한 원문 링크와 자체 질문·한국어 설명을 제공한다.

## 주차 준비 때 추가로 확인할 자료

무선·VPN의 실제 구성, OSPF 시뮬레이터 설정, Ansible·Terraform 심화의 구체적인 문서는 아직 필수 자료로 확정하지 않았다. 해당 주차의 학습 수준과 실행 환경이 정해지면 공식 자료의 필요한 절과 재현 절차를 추가한다. 공식 자료를 읽었다는 사실과 실습을 직접 실행해 확인한 결과는 구분한다.

### Linux 환경의 차이

아올다 VM의 배포판·사전 설치·관리자 권한·인터넷 접근·가상망은 참가자 계정에서 확인한다. ip·ss·curl·dig·nc·tcpdump 등의 설치 상태부터 확인하고 필요한 도구만 준비한다. 조회 가능과 주소·경로·정책 변경 가능을 구분한다.

실습 파일과 결과를 VM 밖에도 보관할 수 있는지 확인하고, 진행자와 팀원 계정에서 실제 보존·캡처 조건을 점검한다. VM 내부 루프백 관찰을 개인 PC→아올다 VM 접속이나 보안 그룹 검증으로 기록하지 않는다.

클라우드 VM의 물리 무선 장치와 GUI는 가정하지 않는다. 캡처 권한이 있다면 VM에서 pcap을 수집해 개인 PC의 Wireshark에서 분석하는 경로를 준비하고, 권한이 없으면 제공 캡처를 사용한다.
