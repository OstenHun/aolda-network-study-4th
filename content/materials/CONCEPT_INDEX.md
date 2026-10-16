# 네트워크 핵심 개념 색인

요약: 공개 교재의 핵심 개념과 이후 학습 주제를 찾는 색인이다. 현재 1~14주차를 연결하며 후속 이론·심화 교재의 계획을 구별한다.

- 사용법: 처음에는 해당 주차 교재와 함께 읽고, 복습할 때는 아래에서 막힌 개념을 찾는다. 개념별 설명과 답은 연결된 교재에서 읽는다.

## 지금 읽을 수 있는 개념

| 주차·ID | 기억할 개념 | 구별할 것 | 개발 질문과 해설 |
| --- | --- | --- | --- |
| 1 · W01-K1~K3 | 실행 위치·IP/port·HTTP 응답 | localhost와 원격 VM, 404와 연결 실패 | [핵심 3·혼동 2·개발 사례 1](week-01/ESSENTIALS.md), 같은 URL이 다른 곳을 가리키는 이유 |
| 2 · W02-K1~K3 | CIDR·경로 선택·도달성 | 주소 범위와 실제 통신, 사설 주소와 접근 허용 | [핵심 3·혼동 2·개발 사례 1](week-02/ESSENTIALS.md), 한쪽 마스크만 다를 때 |
| 3 · W03-K1~K3 | 다음 홉·ARP 캐시·프로토콜별 확인 | 최종 IP와 목적 MAC, ping과 HTTP | [핵심 3·혼동 2·개발 사례 1](week-03/ESSENTIALS.md), ping 실패·HTTP 404의 해석 |
| 4 · W04-K1~K3 | 소켓·RTT·TCP 연결 수립, 스트림/데이터그램·SEQ/ACK 연결 | 전달과 처리, 흐름 제어와 혼잡 제어 | [TCP·UDP 교재](week-04/CONCEPTS.md) · [실습](week-04/LINUX.md) · [분리 해설](week-04/ANSWERS.md) |
| 5 · W05-K1~K3 | 재귀/권한 DNS·A/AAAA·캐시/TTL·DHCP 임대/옵션 | 이름 해석과 서비스 성공, 설정 전달과 이름 질의 | [DNS·DHCP 교재](week-05/CONCEPTS.md#dns-roles) · [직접 실습·제공 분석](week-05/LINUX.md) · [W05-D1~D3 해설](week-05/ANSWERS.md#development) |
| 6 · W06-K1~K3 | HTTP 메시지·재사용/캐시·TLS 신원·SSH | 재사용과 캐시, 서버 신원과 사용자 인증 | [HTTP·TLS·SSH 교재](week-06/CONCEPTS.md) · [실습](week-06/LINUX.md) · [개발 질문 해설](week-06/ANSWERS.md#development) |
| 7 · W07-K1~K3 | 최장 접두사·다음 홉·왕복 경로·TTL | 로컬 조회와 왕복 성공, 최종 IP와 링크의 다음 홉 | [정적 경로 교재](week-07/CONCEPTS.md) · [직접 조회·시뮬레이터](week-07/LINUX.md) · [개발 질문 해설](week-07/ANSWERS.md#development) |
| 8 · W08-K1~K3 | 캐시/연결별 전체 흐름·손실 모형·IPv6/NDP | DNS/HTTP 캐시와 연결, 교육 모형과 TCP·ARP와 NDP | [교재](week-08/CONCEPTS.md) · [단일 장애 실습](week-08/LINUX.md) · [개발 질문 해설](week-08/ANSWERS.md#development) |
| 9 · W09-K1~K3 | MAC 학습·VLAN·STP 루프 방지·LACP 논리 링크 | VLAN과 서브넷, STP와 집성·오류 검출과 인증 | [교재](week-09/CONCEPTS.md) · [직접 시뮬레이터 실습](week-09/LINUX.md) · [개발 질문 해설](week-09/ANSWERS.md#development) |
| 10 · W10-K1~K3 | LS/DV 계산·OSPF 이웃/cost/수렴·AS/BGP 정책 | 계산과 정보 교환, 이웃/경로와 요청 성공 | [교재](week-10/CONCEPTS.md) · [OSPF 직접 실습](week-10/LINUX.md) · [개발 질문 해설](week-10/ANSWERS.md#development) |
| 11 · W11-K1~K3 | NAT/PAT 대응·접근 방향/순서·연결 추적 | 변환과 허용, 기존 연결과 새 요청·서버 중지/DROP | [교재](week-11/CONCEPTS.md) · [정책 직접 실습](week-11/LINUX.md) · [개발 질문 해설](week-11/ANSWERS.md#development) |
| 12 · W12-K1~K3 | 무선 연결·공유 매체·작은 망/VPN 경계 | 연결과 도달성, 오류 검출·암호화·정책 | [교재](week-12/CONCEPTS.md) · [제공 분석·설계/C12](week-12/LINUX.md) · [개발 질문 해설](week-12/ANSWERS.md#development) |
| 13 · W13-K1~K3 | 가상 자원·양끝 서비스/정책·MTU/MSS/PMTUD | Neutron port와 TCP port, MTU와 MSS·DNS와 신원/응답 | [교재](week-13/CONCEPTS.md) · [직접 실습/제공 분석](week-13/LINUX.md) · [개발 질문 해설](week-13/ANSWERS.md#development) |
| 14 · W14-K1~K3 | 지연 네 성분·병목·BDP/윈도·고전 혼잡·프록시 | 전체 시간과 망 RTT, 설정/상태와 실제 요청·단일 호스트 전환 | [교재](week-14/CONCEPTS.md) · [직접 실습](week-14/LINUX.md) · [개발 질문 해설](week-14/ANSWERS.md#development) |

## 이후 주차에 이어갈 범위

아래는 주차별 개념을 개발 사례로 이어 보는 학습 지도다. 현재 읽을 수 있는 자료는 위 표에서 찾고 학습 범위는 [커리큘럼](../CURRICULUM.md)에서 확인한다.

| 주차 | 개념을 개발 판단으로 연결하기 |
| --- | --- |
| 4 | [TCP·UDP 교재](week-04/CONCEPTS.md): SEQ/ACK·타이머·stop-and-wait/파이프라이닝, 흐름/혼잡 제어 구별 |
| 5 | [DNS·DHCP 교재](week-05/CONCEPTS.md): 캐시·TTL → 이름 해석 성공과 서비스 정상, 변경 전파 |
| 6 | HTTP/TLS → 연결 재사용과 다중화, 인증서·인증·암호화, 요청 의존성 |
| 7~8 | [7주](../CURRICULUM.md#week-07) 전달·왕복 경로 → [8주](../CURRICULUM.md#week-08) GBN/SR 모형·전체 흐름·IPv6/ARP/NDP |
| 9~10 | [9주](../CURRICULUM.md#week-09) 오류 검출·VLAN/STP/LACP → [10주](../CURRICULUM.md#week-10) LS/DV 계산·AS/BGP 정책·OSPF 직접 장애 전환 |
| 11~13 | [11주](../CURRICULUM.md#week-11) NAT/정책 → [12주](../CURRICULUM.md#week-12) 매체 접근/무선/VPN → [13주](../CURRICULUM.md#week-13) 클라우드·MTU/MSS/PMTUD |
| 14 | [필수 범위](../CURRICULUM.md#week-14): 지연 성분·병목·BDP/윈도 계산·혼잡 그래프·지연 직접 비교·준비된 프록시 분산/서버 제외 직접 확인 |
| 15~16 | [15주](../CURRICULUM.md#week-15) 소켓 경계/부분 수신·시간 제한·재시도/멱등성 → [16주](../CURRICULUM.md#week-16) 계산·코드 이해·독립 진단 |

## 후속 학습

[학부 핵심 이론 지도](../CURRICULUM.md#학부-핵심-이론-지도)와 [공식 자료 안내](REFERENCE_GUIDE.md)에서 다음 주제를 찾는다. SRE·플랫폼·클라우드 심화는 후속 학습 방향이며 이 색인에 완성된 교재로 연결한 범위는 아니다.

## 어떻게 복습할까

기억 문장을 가리고 현상을 먼저 설명한다. 다음에는 조건 하나를 바꾸어 결론이 유지되는지 묻는다. 답이 막히면 해당 개념의 원문·그림·분리 해설로 돌아간다. 다음 주 시작의 기존 복습 시간에 앞 주차 질문 하나를 다시 사용한다. 읽기를 마쳤거나 해설을 보았다는 이유만으로 학습을 통과했다고 기록하지 않는다.

외부 문제를 찾을 때는 [면접·개발 참고자료 선정](INTERVIEW_REFERENCES.md)을 사용한다. 학습 홈: [1주차](week-01/index.html) · [2주차](week-02/index.html) · [3주차](week-03/index.html) · [4주차](week-04/README.md) · [5주차](week-05/README.md) · [6주차](week-06/README.md) · [7주차](week-07/README.md) · [8주차](week-08/README.md) · [9주차](week-09/README.md) · [10주차](week-10/README.md) · [11주차](week-11/README.md) · [12주차](week-12/README.md) · [13주차](week-13/README.md) · [14주차](week-14/README.md).
