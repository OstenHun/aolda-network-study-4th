# 공식 출처 · 읽을 절과 사용할 근거

요약: 공동 탐색은 access/trunk와 STP의 짧은 지정 절부터 읽는다. MAC·LACP·오류 검출의 추가 근거는 필요한 부분만 찾아 실습 판단과 연결한다.

확인일: 2026-10-17. 아래는 제품 문서·교재 저자 자료·RFC의 구분과 지정 범위다. 문서 전체 정독이나 제품 설정 전체를 요구하지 않는다. 시간은 추정이며 기존 공동 탐색/개인 읽기 안에 배치한다.

## 함께 읽는 필수 두 범위

| 공식 자료·실제 읽을 절 | 목적·실습 연결 |
| --- | --- |
| [Cisco, Configuring Access and Trunk Interfaces](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus5000/sw/layer2/503_n1_1/Cisco_n5k_layer2_config_gd_rel_503_N1_1_chapter6.html) · Understanding Access and Trunk Interfaces의 access/trunk 두 항목, Understanding IEEE 802.1Q Encapsulation의 첫 문단 | 약3~5분. 한 포트의 VLAN 소속과 trunk의 VLAN 식별을 찾고 D1/A2를 예상. Nexus5000/NX-OS의 문서이며 제품별 기본값·명령을 본인 장비에 복사하지 않음 |
| [Cisco, Spanning Tree Protocol](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/lan-wan/lan-wan/m_lsw-span-tree-prot.html) · Using the Spanning Tree Protocol with the EtherSwitch Network Module의 루프 설명 문단과 STP defines a tree로 시작하는 문단 | 약3~5분. 루프·차단·장애 때 재계산을 찾고 A3의 경로를 예상. 제품 문서의 VLAN별 인스턴스와 달리 제공 모델은 공통 트리 하나. STP Timers·제품 설정 절은 필수 읽기에서 제외 |

영문을 바로 읽기 어렵다면 [K1/K2](CONCEPTS.md)를 먼저 읽고 해당 용어만 원문에서 찾는다. 답을 찾는 데 필요한 범위이지 긴 영문 읽기 과제가 아니다.

## 기술 근거와 선택 읽기

| 출처·확인한 절 | 지지하는 주장·선택 범위 |
| --- | --- |
| [Kurose/Ross 9판, Chapter6 안내](https://gaia.cs.umass.edu/kurose_ross/videos/6/) · 6.4 Notes의 Switch: self-learning·Switch: frame filtering/forwarding, VLANs | 출발지 학습·목적지 조회·flood·VLAN의 기초. 선택으로 Notes의 해당 제목 슬라이드만 읽고 A1 출력과 대응. 장 전체 읽기는 불필요 |
| 같은 저자 안내의 6.2 Notes · Parity checking·Internet checksum (review)·Cyclic redundancy check | 검출 값·오류 패턴·CRC burst 보장과 한계. 선택으로 세 제목 슬라이드, 필수 분석은 교재의 자체 표와 Q7/Q8로 수행. 원본 슬라이드/그림을 교재에 복제하지 않음 |
| [Cisco STP](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/lan-wan/lan-wan/m_lsw-span-tree-prot.html) · Spanning Tree Port States, Spanning Tree Root Bridge | 역할/상태·루트/경로비용·BPDU·전환 대기. 선택은 첫 상태 목록과 루트 선정 문단. 복잡한 동률·타이머 튜닝 제외 |
| [Cisco, Configuring EtherChannels, IOS XE17.15](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9500/software/release/17-15/configuration_guide/lyr2/b_1715_lyr2_9500_cg/configuring_etherchannels.html) · EtherChannel Overview·Link Aggregation Control Protocol·LACP Modes/Link Redundancy | 논리 링크·호환 모드·구성 제약·min-links. 선택은 active/passive 조합과 min-links 세 항목만 읽고 B의 선택멤버/전환 설명. 제품별 최대멤버 수나 구성 명령은 범위 밖 |
| [Linux kernel, Ethernet Bonding Driver HOWTO](https://docs.kernel.org/networking/bonding.html) · xmit_hash_policy의 layer2/layer2+3/layer3+4, Switch Configuration의 802.3ad | 여러 흐름 분산과 단일 연결의 제한·호환성. 선택은 single connection 제한 문장 주변. 실제 Linux bond를 만드는 실습이 아니며 모델의 flow 나머지가 이 드라이버의 해시라는 뜻은 아님 |
| [RFC1071 §1](https://www.rfc-editor.org/rfc/rfc1071.html#section-1) · checksum 생성/검증과 end-around carry | 16bit 1의 보수 합·보수·수신 FFFF. 선택으로 §1 첫 알고리즘 항목만 읽고 Q7의 작은 계산과 대조. 패킷 전체 checksum 구현 제외 |
| [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer) · Switching/Network Simulators 주제 지도 | 전체 주제 위치를 찾는 선택 색인. 기술 정답·기업 기출의 근거로 사용하지 않음 |

## 예제·코드·인용의 경계

질문·해설·parity/checksum/CRC 작은 값·삼각형과 Python 시뮬레이터는 이 교재의 자체 학습 예제다. 특정 기업 기출이나 실제 운영 측정 결과가 아니다. 코드에는 외부 구현을 복사하지 않았으며 표준 프로토콜의 완전 구현을 주장하지 않는다. 공식 문서의 장문·그림·슬라이드를 재배포하지 않고 링크와 지정 제목으로 찾는다.

모델은 명령마다 현재 구성·학습 상태를 계산한다. 시뮬레이터에서 직접 변경·복구한 근거와 제공 예시를 읽은 근거, 실제 장비 패킷·시간·성능 근거를 구별한다. [실습의 지원 기능/한계](LINUX.md)와 [교재의 조건](CONCEPTS.md)을 함께 읽는다.
