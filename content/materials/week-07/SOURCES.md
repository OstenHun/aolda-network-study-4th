# 공식 출처와 읽을 범위 · 정적 경로

요약: 참가자는 경로 일치 두 항목과 ip route get 설명을 함께 읽는다. TTL·traceroute·Python 구현 근거는 필요한 절만 확인한다. 자체 문제·구성·가공 출력은 실제 측정이나 외부 문서의 복제와 구별한다.

## 참가자가 함께 읽을 공식 절

확인 기준은 2026-10-17이다. 링크가 문서 처음을 열면 아래 정확한 소제목을 문서 내 검색으로 찾는다. 전체 RFC나 모든 명령 옵션을 읽을 필요는 없다. 영문이 막히면 [교재](CONCEPTS.md)의 표·그림을 함께 본다.

| 자료·읽을 범위 | 구분·찾을 내용 | 질문/실습에 쓰는 곳 |
| --- | --- | --- |
| [RFC 1812 §5.2.4.3](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.4.3), **(1) Basic Match와 (2) Longest Match** | 중심 필수, 목적지 비트 일치·접두사 길이로 후보 좁히기 | W07-K1, D1, Q1. 뒤의 TOS/metric/policy 전체는 읽지 않음 |
| [ip-route(8) DESCRIPTION](https://man7.org/linux/man-pages/man8/ip-route.8.html#DESCRIPTION), **ip route get**의 get a single route부터 **no packets are actually sent**를 포함한 설명까지 | 중심 필수, 커널 조회와 실제 패킷 전송 구별. 중간 상세 옵션 목록은 필요할 때만 참조 | A, Q2. get과 show 차이·실제 요청 여부 |
| [traceroute(8) DESCRIPTION](https://man7.org/linux/man-pages/man8/traceroute.8.html#DESCRIPTION), TTL을 늘리는 설명부터 **별표 설명**까지 | 보조 선택 읽기, 응답 기다림과 별표 의미. 이 개념은 교재/제공 분석으로도 필수 확인 | K3, D3, Q6. 방식·포트·반환 경로는 교재와 연결 |

RFC 1812는 1995년 IPv4 라우터 요구사항이다. 이번에는 위 두 규칙과 아래 TTL 절만 근거로 쓰고 오래된 문서 전체를 오늘의 모든 라우팅 구현/정책으로 일반화하지 않는다. 접두사 선택은 단일 유효 전달표·동일 접두사 경쟁 없음의 가정이다. 매뉴얼은 Linux 도구 설명이며 플랫폼·설치 버전에 따라 출력/옵션이 달라 실제 버전 도움말도 확인한다.

## 설명·명령의 확인 근거

| 공식/구현 문서 | 확인한 절·채택 범위 |
| --- | --- |
| [RFC 1812 §5.2.1.2](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.1.2), [§5.2.4](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.4), [§5.3.1](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.3.1) | 유니캐스트 전달·다음 홉 판단·TTL 감소/폐기. TTL은 적어도 1 감소하며 모형은 정확히 1로 단순화 |
| [RFC 1812 §4.3.2.7](https://www.rfc-editor.org/rfc/rfc1812.html#section-4.3.2.7), [§4.3.2.8](https://www.rfc-editor.org/rfc/rfc1812.html#section-4.3.2.8) | ICMP 오류 생성 예외·빈도 제한. 항상 응답이 보인다고 보장하지 않음 |
| [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html), [ip-address(8)](https://man7.org/linux/man-pages/man8/ip-address.8.html), [ip-rule(8)](https://man7.org/linux/man-pages/man8/ip-rule.8.html), [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html) | show/get·via/dev/src·table all, 주소 show, rule show, -4/-V. 이번 Linux 실습은 조회만 |
| [traceroute(8)](https://man7.org/linux/man-pages/man8/traceroute.8.html) OPTIONS·NOTES | -n/-m/-q/-w, UDP 기본/다른 방식, 시간/응답 해석의 한계 |
| [Python 3.12 ipaddress](https://docs.python.org/3.12/library/ipaddress.html#ip-network-definitions) | IPv4Address/IPv4Network·포함 검사·prefixlen, 직접 CIDR 비트 연산을 재구현하지 않음 |
| [Python copy](https://docs.python.org/3.12/library/copy.html), [json](https://docs.python.org/3.12/library/json.html), [pathlib](https://docs.python.org/3.12/library/pathlib.html) | deepcopy 원복, JSON 읽기, 코드 옆 파일 찾기. 표준 라이브러리 사용 |
| [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer) | Routing 범주의 학습 지도. 기술 답안·회사 출제 근거로 쓰지 않음 |

## 예제와 재사용 조건

교재의 경로표·A/R1/R2/B 구성·traceroute 숫자·문제·해설·Python 시뮬레이터는 이 스터디의 자체 자료다. 문서용 IPv4 대역을 쓰며 실제 팀 주소/지연·장비 설정을 뜻하지 않는다. 시뮬레이터의 실행 결과는 모형 계산이고 실제 Linux 패킷 출력이 아니다. 미리 제공한 이웃표는 ARP·Ethernet 이벤트를 대신하는 단순화다.

[2주 CIDR](../week-02/CONCEPTS.md)·[3주 다음 홉/ARP](../week-03/topics/03-next-hop.md)·[4주 TCP](../week-04/CONCEPTS.md)·[5주 이름](../week-05/CONCEPTS.md)·[6주 TLS/HTTP](../week-06/CONCEPTS.md)의 정상 자료를 선수 설명으로 재사용한다. 반환 경로 필요성은 각 방향의 다음 홉 선택 원리를 고정 구성에 적용한 자체 추론이다. 제공 예제를 실제 수행 근거로 바꾸지 않는다.

긴 원문·외부 코드·그림을 재배포하지 않고 필요한 공식 절로 연결한다. 다른 자료를 추가 복사할 때는 해당 원문의 이용 조건을 확인한다. 이 자료가 대학 평가·특정 기업 기출·자격증 전체 범위를 대표하지 않는다.
