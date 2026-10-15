# 2주차 함께 찾아보기 — 접두사와 경로에서 근거 찾기

요약: 중심 질문의 답을 AWS CIDR 설명과 Linux 경로 조회 문서에서 함께 찾는다. 검색어·읽을 절·확인할 질문을 안내하고 roadmap 연결 글은 필요한 부분만 선택한다. 원문 읽기는 공동 탐구 시간에 포함한다.

## 중심 질문에서 출발하기

[“IP가 비슷한 두 VM은 같은 망으로 바로 통신할 수 있을까?”](WORKSHEET.md)를 함께 읽는다. 답을 먼저 발표하기보다 접두사·경로·응답 중 모르는 말을 찾아 공부한다. 공동 탐구의 5~25분 안에서 아래 두 자료의 지정 부분을 골라 읽는다. 지정 부분은 합계 약 6~8분의 읽기 시작점이다.

| 찾을 곳 | 검색어와 읽을 절 | 찾아 설명할 것 | 다음 확인 |
| --- | --- | --- | --- |
| [AWS — What is CIDR?](https://aws.amazon.com/what-is/cidr/) | `CIDR prefix notation AWS`, `CIDR /26 주소 수`. “Classless addresses”·“CIDR notation”의 접두사/주소 블록 설명 | `/n`이 어떤 비트 수이고 주소 범위가 어떻게 달라지는가? | [핵심 K1](ESSENTIALS.md#w02-k1--cidr은-주소-범위를-나타낸다)·[교재 4~5절](CONCEPTS.md#4-24와-26은-어디에-선을-긋는가) → C1/C2 손계산 |
| [Linux ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) | `ip route get via dev src man7`. 페이지 안에서 `ip route get` 설명과 `via`·`dev`·`src`를 찾기 | 선택 경로 조회와 실제 상대 응답의 차이, 각 필드의 역할 | [핵심 K2/K3](ESSENTIALS.md#w02-k2--실제-다음-전달-경로는-경로-조회로-확인한다) → [P1 자기 경로](../../labs/week-02/LINUX.md#2-목적지-경로-조회--패킷-전송이-아님) |

검색 결과 요약을 그대로 답으로 삼지 않고 원문에서 해당 조건·문장을 찾는다. 두 문서의 전체 본문을 읽을 필요는 없다. 낯선 영어·비트 계산이 막히면 진행자가 [자체 교재](CONCEPTS.md)의 그림을 함께 읽고 다시 원문과 대조한다. 계정 가입이나 새로운 도구 설치는 요구하지 않는다.

## 찾은 설명을 자기 VM에 적용하기

1. 주소와 접두사가 어떤 계산에 필요한지 말하고 C1/C2를 손으로 푼다. [검산기](../../labs/week-02/subnet_check.py)는 손계산 뒤 사용한다.
2. [P1](../../labs/week-02/LINUX.md)의 실제 조회에서 인터페이스·주소/접두사·선택 경로를 읽는다. 예제의 `192.0.2.*`와 자기 VM 값은 섞지 않는다.
3. 한 명이 답·이유·근거를 설명하고 다른 사람이 조건을 바꾼다. 경로 조회만 했는데 실제 통신 성공까지 확인했다고 말하지 않는다.
4. 자기 설명 뒤 [분리 해설](ANSWERS.md#공동-질문-해설)을 열어 계산·관찰 범위·다음 진단을 대조한다.

읽을 절·개념의 연결은 자체 안내다. 기술 정의는 [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1), 주소 범주는 [IANA 특수 목적 등록부](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)로 대조한다. 출처의 AWS VPC 예시를 현재 아올다 설정으로 취급하지 않는다.

## 더 찾아볼 때

아래 다섯 질문과 연결 글은 **선택 길잡이**다. 중심 질문이 막히는 부분만 골라 읽는다. 공동 탐구의 필수 두 자료에 더해 다섯 질문을 모두 풀거나 발표하지 않는다. 외부 링크가 열리지 않으면 개념 교재·제공 출력으로 공부하고 원문 미열람을 구분한다. 자료별 읽을 범위와 한계는 [출처 안내](SOURCES.md)를 참고한다.

## 1. IP 주소만 보면 어느 프로그램과 어느 범위인지 알 수 있을까?

**필요할 때 선택 참고:** IP Address 노드의 [Coursera — What Is an IP Address?](https://www.coursera.org/articles/ip-address)에서 주소의 뜻과 IPv4 표기 부분만 읽는다. 1주차 [IP·포트 설명](../week-01/ARTICLE_LESSON.md#3-같은-ip에서-두-프로그램을-어떻게-구분할까)을 먼저 자기 말로 복습해도 된다.

지난주 `127.0.0.1:8080`에서 `127.0.0.1`은 curl을 실행한 **그 VM 자신**의 루프백 주소이고 `8080`은 그 VM의 서버 포트였다. 이번 카드의 `.10`과 `.70`은 주소 부분만 보여 준다. 포트는 프로그램을 구분하지만, 주소에 붙은 `/24`나 `/26`은 해당 인터페이스가 어떤 주소 범위를 연결된 망으로 보는지 계산하는 데 쓰인다. `127/8`은 루프백이며 카드의 링크와 섞지 않는다. [RFC 1122 §3.2.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.2.1.3)

**서로 물을 질문:** SSH로 들어간 뒤 `ip -br -4 addr`에 `lo`와 다른 인터페이스가 보이면, 지난주 HTTP 요청은 어느 인터페이스의 주소를 썼는가? 출력의 실제 주소·접두사는 카드의 예시와 같은가? 내 VM과 개인 PC를 같은 호스트로 세지 않고 설명한다.

## 2. 사설 주소가 아니면 공인 주소일까?

**선택 참고:** Public vs Private Addresses 노드의 [Avast — Public vs. Private IP Addresses](https://www.avast.com/c-ip-address-public-vs-private)에서 “Public and private IP address ranges”의 세 범위만 읽는다. 글의 집 공유기·ISP 설명과 제품 안내는 이번 VM의 구조로 가져오지 않는다.

사설 IPv4 범위는 `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` 세 개다. 첫 숫자가 `172` 또는 `192`라고 모두 사설은 아니다. `127.0.0.0/8`은 루프백, `192.0.2.0/24`는 문서용이므로 **RFC 1918 바깥 = 공인**으로 분류할 수 없다. [RFC 1918 §3](https://www.rfc-editor.org/rfc/rfc1918.html#section-3), [IANA IPv4 Special-Purpose Address Registry](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)

이 글은 가정용 공유기를 중심으로 사설 주소를 설명한다. 실제 VM에서는 주소 종류와 외부 도달성을 따로 판단한다. 주소만으로 NAT, 기본 경로, 보안 그룹, 서버 대기 상태를 확인할 수 없다.

**서로 물을 질문:** 자기 VM의 `ip -br -4 addr`에서 한 주소를 고르고 정확히 어느 등록 범위에 드는지 말한다. 그 사실로 알 수 있는 것과 `ip -4 route` 또는 실제 요청을 봐야 알 수 있는 것을 분리한다. 카드 `192.0.2.10`을 공인 VM 주소로 발표하지 않는다.

## 3. `/24`와 `/26`은 어느 비트를 남길까?

**선택 참고:** Subnet Masks 노드의 [Coursera — What Is a Subnet Mask?](https://www.coursera.org/articles/subnet-mask)에서 “What is a subnet mask?” 첫 문단과 “Use of subnet masks in subnetting”의 `/25` 예시만 읽는다. A/B/C 클래스 표와 일반적인 집 마스크 이야기는 이번 카드의 규칙으로 쓰지 않는다.

IPv4는 32비트다. `/24`는 앞 24비트가 1인 `255.255.255.0`, `/26`은 앞 26비트가 1인 `255.255.255.192` 마스크에 해당한다. 주소와 마스크를 비트별 AND하면 해당 접두사로 본 네트워크 주소가 된다. `/26`은 마지막 8비트 중 앞 2비트가 범위를 나누므로 한 블록은 64개 주소다. [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1)

**카드에 적용:** C1은 A=`192.0.2.10/24`, B=`192.0.2.70/24`다. 양쪽에서 `.0/24`를 계산한다. C2는 **A만** `.10/26`으로 바뀌고 B는 `.70/24` 그대로다. A의 `.0/26`은 마지막 묶음 0~63, B의 `/24`는 0~255다. A에서 `.70`은 연결된 `/26` 범위 밖이고, B에서 `.10`은 연결된 `/24` 범위 안이다. 이는 양쪽의 **주소 계산**이며 성공한 ping 기록이 아니다.

**서로 물을 질문:** C2에서 “B는 A를 같은 망으로 보니 왕복 성공한다”라는 주장에 무엇이 빠졌는가? 두 호스트의 판단을 따로 설명하고 [개념 교재 5절](CONCEPTS.md#5-두-예제로-범위-직접-구하기)의 손계산과 검산기를 대조한다.

## 4. CIDR 표기만으로 다음 홉이 정해질까?

**선택 참고:** CIDR 노드의 [AWS — What is CIDR?](https://aws.amazon.com/what-is/cidr/)에서 “Classless addresses”와 “CIDR notation”만 읽는다. AWS VPC 설정, 주소 등록 기관과 과거 클래스별 크기는 이번 실습 범위가 아니다.

`192.0.2.10/26`은 그 주소에 적용할 접두사 길이를 보여 준다. 자기 호스트에 그 주소를 설정했다면 보통 연결된 범위의 경로도 생기지만, **목적지 주소를 보고 실제로 어떤 경로를 고르는지는 현재 경로표와 정책의 문제**다. 더 구체적인 경로가 기본 경로보다 우선할 수 있다. `ip -4 route get <허용된 목적지>`는 커널의 경로 조회를 보여 주며 `via`, `dev`, `src`를 읽는다. 상대가 살아 있거나 애플리케이션이 응답한다는 뜻은 아니다. [ip-route(8), `get`](https://man7.org/linux/man-pages/man8/ip-route.8.html)

**서로 물을 질문:** 자기 VM의 허용된 목적지 하나에 대한 `route get`과 `ip -4 route`에서 선택된 인터페이스·다음 홉·출발지 주소를 찾는다. 해당 경로를 고를 수 있다는 관찰과 패킷 도달·응답을 받았다는 관찰을 나누어 말한다. 문서용 카드 주소로 외부 통신을 시도할 필요는 없다.

## 5. 같은 서브넷이라면 통신도 성공할까?

**선택 참고:** Subnetting 노드의 [Cloudflare — What is a subnet?](https://www.cloudflare.com/en-gb/learning/network-layer/what-is-a-subnet/)에서 “What is a subnet?” 첫 문단과 “What is a subnet mask?”의 첫 문단만 읽는다. 편지 비유와 클래스 C `192.0.2.15` 설명은 카드 계산이나 실제 전달 순서의 근거로 쓰지 않는다.

서브넷 계산은 한 호스트가 주소를 어떤 범위로 묶는지 설명한다. C1에서 양쪽의 `/24`가 일치해도 같은 링크인지, 상대가 동작하는지, 응답 경로와 정책이 허용되는지까지 보장하지 않는다. C2는 A와 B의 판단이 비대칭이다. 기본 경로와 다른 별도 경로가 없는 격리 모형이라면 A→B에는 경로가 없을 것으로 **예상**하지만, 자기 VM의 실제 결과는 양쪽 주소·경로와 허용된 실험의 출력으로만 확인한다. [Linux 안내](../../labs/week-02/LINUX.md)의 격리 실험은 사전 점검이 있을 때만 선택으로 수행한다.

**서로 물을 질문:** “주소 계산 결과”, “`route get`의 선택”, “상대의 응답” 중 우리 팀이 실제로 확인한 것은 각각 무엇인가? C1·C2 카드 설명과 자기 VM 증거를 섞지 않고 근거 위치를 가리킨다. 다음 주에는 같은 링크로 보내기로 한 뒤 상대를 찾는 ARP·ICMP로 이어 간다.

## roadmap 연결 글 — 필요한 부분만 선택

| roadmap.sh term | 연결 글 | 이번 범위 |
| --- | --- | --- |
| IP Address | [Coursera](https://www.coursera.org/articles/ip-address) | 1주차 복습용 선택. 주소·포트·접두사를 구분할 때만 사용 |
| IPv4 vs IPv6 | [AWS](https://aws.amazon.com/compare/the-difference-between-ipv4-and-ipv6/), [Kinsta](https://kinsta.com/blog/ipv4-vs-ipv6/) | 이번 카드는 IPv4만 계산. IPv6 비교는 선택 |
| Subnet Masks | [Coursera](https://www.coursera.org/articles/subnet-mask) | 필요한 두 절만 선택. 클래스별 기본 마스크는 암기 대상 아님 |
| CIDR | [AWS](https://aws.amazon.com/what-is/cidr/) | 필요한 두 절만 선택. VLSM·집계는 선택 |
| Public vs Private Addresses | [Avast](https://www.avast.com/c-ip-address-public-vs-private) | 세 범위를 확인할 때 선택. 공인/사설 이분법과 NAT 일반화 주의 |
| Subnetting | [Cloudflare](https://www.cloudflare.com/en-gb/learning/network-layer/what-is-a-subnet/) | 필요한 두 짧은 문단만 선택. 전달 성공 증거 아님 |

입문 글의 설명이 실제 VM 설정에도 적용되는지는 [공식 근거와 읽을 범위](SOURCES.md)를 대조한다.
