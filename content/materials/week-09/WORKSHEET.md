# 함께 찾을 질문 · 같은 대역, 다른 링크

요약: 같은 IP 대역인 두 장치가 통신하지 못하는 현상에서 시작한다. 공식 절과 교재를 함께 읽고, 설명 뒤 VLAN이나 링크 한 조건을 바꿔 직접 확인한다.

## 앞 개념으로 돌아가기

`192.0.2.10/24`와 `192.0.2.20/24`는 같은 접두사에 속한다. 송신자는 목적지 MAC을 어떻게 알까? [3주차 ARP](../week-03/arp.html)를 보고, ARP 요청을 보낼 범위와 응답이 돌아올 조건을 말해 본다. 이 주소는 설명용이며 실습 시뮬레이터가 IP를 구현한다는 뜻은 아니다.

<span id="development"></span>
## 중심 질문 · W09-D1

두 장치가 같은 스위치에 연결되어 있고 IP/마스크도 맞는데 통신하지 못한다. 케이블은 살아 있고 장치가 속한 VLAN은 아직 모른다. 접두사 계산 외에 무엇을 확인해야 하며, 그 판단을 어떤 근거로 설명할까?

모두 [Cisco access/trunk](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus5000/sw/layer2/503_n1_1/Cisco_n5k_layer2_config_gd_rel_503_N1_1_chapter6.html)의 **Understanding Access and Trunk Interfaces** 두 항목과 **Understanding IEEE 802.1Q Encapsulation** 첫 문단을 찾는다. 목적은 포트 소속과 VLAN 식별이 전달 범위를 어떻게 바꾸는지 읽는 것이다. 제품 설정 명령 전체는 읽지 않는다. 영문이 막히면 [K1](CONCEPTS.md#mac-vlan)로 돌아온다.

한 사람이 근거를 설명한 뒤 다른 사람은 [실습 A](LINUX.md#lab-a)에서 `vlan B 20`이라는 한 조건을 고른다. 예상→실행→출력→복구를 연결해 처음 설명이 맞는지 확인한다.

## 선택 보조 질문 · W09-D2

세 스위치를 삼각형으로 연결했다. 평소 쓰지 않는 포트가 있는데 링크 하나를 끊자 전달 경로가 달라졌다. IP 경로를 바꾼 것일까? [Cisco STP](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/lan-wan/lan-wan/m_lsw-span-tree-prot.html)의 **Using the Spanning Tree Protocol with the EtherSwitch Network Module** 첫 두 문단을 함께 읽고, 루프·차단·재계산을 찾는다. 이 절은 필수 개념 읽기이며, 이 보조 발문으로 토론을 늘리는 것은 선택이다. 기본 루트/포트 설명은 [K2](CONCEPTS.md#stp)에서 읽는다.

## 선택 보조 질문 · W09-D3

두 1 Gbit/s 링크를 묶었다. 파일 하나를 받는 연결도 반드시 2 Gbit/s가 될까? 멤버 하나가 끊긴 뒤 모의 왕복이 성공했다면 “성능도 그대로”라고 말할 수 있을까? [K3](CONCEPTS.md#lacp)와 [실습 B](LINUX.md#lab-b)에서 근거와 아직 모르는 것을 나눈다.

## 설명을 확인하기

설명자를 교대하며 조건 하나를 바꿔 묻는다. 긴 발표나 정해진 공동 기록을 만들지 않는다. 상세 명령·출력은 각자의 파일에 한 번 보관하고, [복습](REVIEW.md) 뒤 [개발 질문 해설](ANSWERS.md#development)을 연다.
