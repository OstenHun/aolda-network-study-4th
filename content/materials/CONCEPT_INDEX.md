# 네트워크 핵심 개념 색인

요약: 공개 교재의 핵심 개념과 이후 학습 주제를 찾는 색인이다. 현재 1~16주차를 연결하며 후속 이론·심화 교재의 계획을 구별한다.

- 사용법: 처음에는 해당 주차 교재와 함께 읽고, 복습할 때는 아래에서 막힌 개념을 찾는다. 개념별 설명과 답은 연결된 교재에서 읽는다.

<span id="personal-study"></span>

## 개인 공부에서 질문·혼동·핵심을 정리하기

2~16주차는 혼자 예상→실습·관찰→조건 변경·비교→복구→자기 설명을 먼저 시도한다. 모임에서는 각자 시도한 근거와 막힌 이유를 비교하고 필요한 단계만 다시 확인한다. 고정 파트너나 교대 순서는 필수 조건이 아니다. 설명·질문 역할은 필요할 때 나눈다. 아래 표는 기존 개인 노트에서 사용할 정리 방법이며 새 제출 양식이 아니다. 1주차의 기존 학습·실습 기록은 그대로 둔다.

C08·C16의 정답을 가린 독립 진단은 진행자가 준비한 새 단일 사례로 확인한다. 혼자 원인을 알고 주입한 사례는 연습이며 독립 진단 통과로 쓰지 않는다. 각 실습의 필수/선택과 제공 분석/직접 수행 기준을 따른다.

| 정리의 중심 | 교재에서 찾을 곳 | 자기 설명으로 확인할 것 |
| --- | --- | --- |
| 주요 질문과 내 답 | 각 주차 학습 홈의 확인 질문·공동 질문, 복습과 분리 해설 | 해설을 가리고 이유·성립 조건을 말하고, 조건 하나가 바뀌면 답이 어떻게 달라지는지 설명 |
| 헷갈리는 개념 비교 | 2~3주 핵심 정리, 4~16주 교재의 혼동 구별 | 역할·관찰 위치·성공 범위를 나누고 서로 다른 결과가 나오는 예 제시 |
| 꼭 기억하고 이해할 핵심 개념 | 아래 주차별 K1~K3 색인과 연결 교재 | 용어·역할·동작, 필요한 공식·단위·성립 조건을 떠올리고 새 값이나 출력에 적용 |

모임 전에는 현재 답과 막힌 지점을 남기고 모임 뒤에는 확인한 차이와 보충할 부분을 고친다. 실습의 예상·실제 관찰·수정한 이해는 관련 질문·개념에 연결한다. 제공 분석과 본인 실행을 나누고, 아직 관찰하지 않은 결과는 채우지 않는다. 정해진 개수·분량·별도 발표 자료는 없다. 화면의 답안 입력은 자동 저장되지 않으므로 사용했다면 이동 전에 내려받는다.

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
| 15 · W15-K1~K3 | 소켓 경계·부분 수신·EOF·시간제한·제한된 자동 기록 | 호출과 메시지/세그먼트, timeout과 처리 실패·멱등성 | [교재](week-15/CONCEPTS.md) · [직접 실습/코드 지도](week-15/LINUX.md) · [개발 질문 해설](week-15/ANSWERS.md) |
| 16 · W16-K1~K3 | 정상 기준·경쟁 가설·구별 관찰·최소 변경·복구 | 증상과 원인, 정상 응답과 업무 성공·독립 이해 | [교재](week-16/CONCEPTS.md) · [학습자 실습](week-16/LINUX.md) · [C16](week-16/CHECKPOINT.md) · [개발 질문 해설](week-16/ANSWERS.md#development) |

<span id="operations-progression"></span>

## 현업 핵심을 여러 주차에서 깊게 연결하기

같은 용어를 반복해서 외우기보다 앞 원리가 새 조건에서 어떤 판단에 쓰이는지 설명한다. 해당 주차의 학습 홈에서 개인 공부 범위·실습을 준비하고, 오프라인에서는 중심 질문과 짧은 조건 변경으로 확인한다. 아래 지도는 별도 과제나 새 수료 항목이 아니다.

### 전달과 처리 성공, 경계와 시간제한

- **1→4주:** HTTP 응답과 연결 실패를 나눈 뒤 send/ACK와 앱 처리 성공, TCP 메시지 경계를 구별한다.
- **8→14주:** 손실 시 ACK·버퍼·타이머를 추론하고 미확인 데이터와 RTT가 속도를 제한하는 조건을 계산한다.
- **15→16주:** 부분 수신·EOF·수신 마감을 코드에서 찾고 응답을 못 받은 요청의 처리 여부와 복구 기준을 판단한다.
- 돌아갈 곳: [4주](week-04/CONCEPTS.md) · [8주](week-08/CONCEPTS.md) · [14주](week-14/CONCEPTS.md) · [15주](week-15/CONCEPTS.md) · [16주](week-16/CONCEPTS.md).

### 이름·캐시·연결과 상대 신원

- **5→6주:** DNS TTL과 HTTP 캐시·연결 재사용을 나누고 URL 이름·SAN·신뢰 경로를 확인한다.
- **8→11주:** 캐시/열린 연결에 따라 생략되는 교환을 설명하고 기존 연결과 새 연결의 정책 결과를 구별한다.
- **13→16주:** 같은 서비스의 실제 목적지·정책·TLS 신원을 연결해 실패를 조사한다. 숫자 HTTP 성공만으로 DNS/TLS를 통과했다고 하지 않는다.
- 돌아갈 곳: [5주](week-05/CONCEPTS.md) · [6주](week-06/CONCEPTS.md) · [8주](week-08/CONCEPTS.md) · [11주](week-11/CONCEPTS.md) · [13주](week-13/CONCEPTS.md).

### 링크·왕복 경로·정책·장애 영역

- **2→3→7주:** 주소 범위→첫 이웃→여러 홉의 반환 경로로 넓힌다. 주소 계산·경로 조회·실제 요청을 서로 다른 근거로 읽는다.
- **9→10주:** VLAN/STP/LACP와 OSPF의 계층·전환 대상을 구별한다. 경로표가 바뀐 시점과 서비스 회복 시점을 나눈다.
- **11→12→13주:** 변환 전후 주소/상태·정책, VPN 보호 경계, 실제 클라우드 자원·MTU/PMTUD를 왕복 그림에 표시한다.
- **14→16주:** 한 프로세스의 제외와 한 호스트 상실을 구별하고 실제 요청의 복구를 확인한다.
- 돌아갈 곳: [7주](week-07/CONCEPTS.md) · [9주](week-09/CONCEPTS.md) · [10주](week-10/CONCEPTS.md) · [12주](week-12/CONCEPTS.md) · [13주](week-13/CONCEPTS.md).

### 느림·연결 자원·사용자 영향과 재시도

- **4→6→11주:** 연결 수립 비용·재사용·기존/새 연결의 상태를 익힌다.
- **14주:** 평균/꼬리 지연과 오류·포화의 단서를 읽고 기존 연결과 새 연결의 증상이 다를 때 관찰을 고른다. [제공 사례](week-14/CONCEPTS.md#operational-bridge)를 사용하며 자원 고갈 실험은 하지 않는다.
- **15주:** timeout 뒤 처리 불확실성·멱등성을 바탕으로 계층별 재시도 횟수와 전체 시간 예산을 제한한다. [제공 계산](week-15/CONCEPTS.md#retry-budget)을 사용한다.
- **16주 이후:** 같은 입력의 복구와 사용자 결과를 확인한다. 부하·연결 자원 실험·backoff/jitter·복합 장애·SLO는 후속 심화에서 더 다루며 완성된 실습으로 간주하지 않는다.

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

기억 문장을 가리고 현상을 먼저 설명한다. 다음에는 조건 하나를 바꾸어 결론이 유지되는지 묻는다. 답이 막히면 해당 개념의 원문·그림·분리 해설로 돌아간다. 오프라인 시작에는 바로 앞 주 또는 2~4학습 단위 전의 질문 하나를 새 주소·출력으로 바꾸어 다시 사용한다. 새 복습 양식을 추가하지 않으며 읽기·해설 열람을 독립 이해로 기록하지 않는다.

외부 문제를 찾을 때는 [면접·개발 참고자료 선정](INTERVIEW_REFERENCES.md)을 사용한다. 학습 홈: [1주차](week-01/index.html) · [2주차](week-02/index.html) · [3주차](week-03/index.html) · [4주차](week-04/README.md) · [5주차](week-05/README.md) · [6주차](week-06/README.md) · [7주차](week-07/README.md) · [8주차](week-08/README.md) · [9주차](week-09/README.md) · [10주차](week-10/README.md) · [11주차](week-11/README.md) · [12주차](week-12/README.md) · [13주차](week-13/README.md) · [14주차](week-14/README.md) · [15주차](week-15/README.md) · [16주차](week-16/README.md).
