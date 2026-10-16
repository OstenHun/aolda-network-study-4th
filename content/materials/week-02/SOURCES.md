# 2주차 출처와 읽을 범위

요약: 공동 질문은 AWS CIDR·Linux 경로 문서에서 시작하고 RFC·IANA로 개념과 주소 범위를 확인한다. 필요한 절과 선택 읽을거리를 안내하며 문서용 예제·경로 조회·실제 응답의 차이를 구별한다.

## 공동 질문의 출발 자료

[함께 찾아보기](ARTICLE_LESSON.md)의 중심 질문에 필요한 두 자료에서 시작한다. 약 6~8분 동안 지정 부분을 함께 읽고 접두사 계산·경로 조회에 적용한다. 전체 본문을 정독할 필요는 없다.

| 자료 | 지정 부분 | 확인할 주장·한계 |
| --- | --- | --- |
| [AWS — What is CIDR?](https://aws.amazon.com/what-is/cidr/) | “Classless addresses”·“CIDR notation”의 접두사/블록 설명 | 주소 범위 표기. AWS VPC 예시를 실제 아올다 설정으로 채택하지 않음 |
| [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) | `get`·`via`·`dev`·`src` 설명 | 커널의 경로 선택 조회와 실제 패킷 왕복을 구별. 배포판/설정별 출력은 실제 Linux에서 확인 |

낯선 용어는 [개념 교재](CONCEPTS.md)의 그림과 예제로 확인한다. 외부 원문이 열리지 않으면 자체 교재·제공 예제를 사용한다. AWS VPC 예시는 자기 VM의 실제 설정과 구별한다.

## 필요한 부분만 선택해 읽기

| 로드맵 용어 | 연결 글 | 읽을 범위와 주의점 |
| --- | --- | --- |
| IP Address | [Coursera — What Is an IP Address?](https://www.coursera.org/articles/ip-address) | 1주차 IP/port 복습용 선택. 본문의 `224.128.240.8`은 일반 단일 호스트 주소 예로 쓰지 않음. 2주차 접두사·경로 검증의 근거는 아님 |
| IPv4 vs IPv6 | [AWS](https://aws.amazon.com/compare/the-difference-between-ipv4-and-ipv6/), [Kinsta](https://kinsta.com/blog/ipv4-vs-ipv6/) | IPv4 카드 중심이므로 선택·후속. IPv6를 배우는 주차에 비교 |
| Public vs Private Addresses | [Avast — Public vs. Private IP Addresses](https://www.avast.com/c-ip-address-public-vs-private) | **선택:** “Public and private IP address ranges”의 세 범위. 집 공유기·ISP·NAT 전제를 VM에 일반화하지 않음. “사설 외 전부 공인”이라는 문장은 IANA 등록부와 맞지 않아 미채택 |
| Subnet Masks | [Coursera — What Is a Subnet Mask?](https://www.coursera.org/articles/subnet-mask) | **선택:** “What is a subnet mask?” 첫 문단과 “Use of subnet masks in subnetting”의 `/25` 예시. 클래스별 마스크·가정용 기본값은 카드의 근거로 쓰지 않음 |
| CIDR | [AWS — What is CIDR?](https://aws.amazon.com/what-is/cidr/) | **선택:** “Classless addresses”와 “CIDR notation”. AWS VPC 구성·집계는 선택; 주소 블록 표기는 실제 경로·도달 증거가 아님 |
| Subnetting | [Cloudflare — What is a subnet?](https://www.cloudflare.com/en-gb/learning/network-layer/what-is-a-subnet/) | **선택:** “What is a subnet?”과 “What is a subnet mask?”의 첫 문단. 클래스 C 예시와 편지 비유는 실제 전달 순서로 쓰지 않음 |

외부 글·영상은 인터넷이 필요하고 자체 교재·주소 모형은 오프라인으로도 읽을 수 있다. 중심 질문을 해결하는 데 필요한 부분만 선택한다.

## 개념을 확인할 공식 자료

| 공식 원문 | 확인한 범위 | 이번 설명에서 검증한 주장 |
| --- | --- | --- |
| [RFC 1918 §3](https://www.rfc-editor.org/rfc/rfc1918.html#section-3) | Private Address Space | `10/8`, `172.16/12`, `192.168/16`의 정확한 사설 경계 |
| [IANA IPv4 Special-Purpose Address Registry](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml) | Private-Use, Loopback, Documentation | RFC 1918 밖에도 공인이 아닌 특수 목적 범위가 있음 |
| [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1) | Basic Concept and Prefix Notation, 블록 크기 표 | 32비트 접두사 표기, `/26` 64개·`/24` 256개. 주소 수가 곧 할당 가능·통신 가능 수는 아님 |
| [RFC 5737 §3](https://www.rfc-editor.org/rfc/rfc5737.html#section-3) | Documentation Address Blocks | `192.0.2.0/24`는 카드 설명용. 아올다 실측 주소로 해석하지 않음 |
| [RFC 1122 §3.2.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.2.1.3) | loopback address | 1주차 `127.0.0.1`을 VM 자기 자신으로 해석 |
| [iproute2 `ip-route(8)`의 `get`](https://man7.org/linux/man-pages/man8/ip-route.8.html) | route get 명령 설명 | 경로 조회는 커널의 경로 선택을 보여 줌. ping·HTTP의 실제 상대 응답을 증명하지 않음 |

RFC의 주소 정의와 `ip-route`의 경로 선택 설명을 카드 계산·자기 Linux 조회와 대조한다. 계산한 주소 범위와 실제 통신 결과를 구별한다.

## 실습 명령과 계산 도구

[실습 명령의 공식 참고자료](LAB_SOURCES.md)에서 주소·경로 조회, 선택 네임스페이스 실험의 명령을 찾는다. 기본 실습은 Linux의 `ip` 도구와 Python 표준 라이브러리를 사용한다.

[Python ipaddress 공식 문서](https://docs.python.org/3/library/ipaddress.html)는 주소·네트워크·호스트 범위 검산의 근거다. `is_private`는 RFC 1918 세 대역만을 뜻하는 속성이 아니므로 그 값 하나로 사설/공인을 가르지 않는다. 라이브러리가 계산한 결과도 실제 패킷 전송·응답의 증거는 아니다.

## 기출과 문제의 출처

[기출·공개 시험 연계 문제](CCNA_PRACTICE.md)에서 문항마다 원문 위치를 확인한다. [문제 출처 안내](QUESTION_SOURCES.md)에서 대학의 과거 시험·제삼자 사이트·자체 문제의 차이와 풀이 범위를 확인한다. [별도 해설](CCNA_ANSWERS.md)은 스터디가 검산한 설명이며 공식 채점표와 구별한다.

외부 문제의 전문·보기·공식 해설을 묶음에 대량 복제하지 않는다. 위치·짧은 인용·자체 활동 안내로 연결하며, 자체 문제는 실제 출제 문제로 표시하지 않는다.

## 실측과 예제의 경계

- [제공 출력](../../labs/week-02/SAMPLE_OUTPUT.md)은 설명용 자료다. 실제 아올다 VM 캡처로 제출하지 않는다.
- MAC·ARP·ICMP 패킷 분석은 3주차 중심이다. 2주차에서는 주소·경로·계산을 연결하고 준비된 격리 환경에서 마스크 조건만 비교한다.

## 개념과 설명 연습

[핵심 정리](ESSENTIALS.md)에서 CIDR·경로·도달성을 구별하고 [자체 질문](WORKSHEET.md)에 답한다. 개발 사례·해설은 스터디의 개념 확인용 문제다. 특정 기업의 실제 면접 문제나 출제 빈도를 뜻하지 않는다.
