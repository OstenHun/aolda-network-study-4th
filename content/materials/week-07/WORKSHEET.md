# 함께 찾을 질문 · 경로가 있는데 왜 응답이 없을까?

요약: 경로표와 왕복 전달을 중심 질문으로 탐색한다. 공식 절에서 근거를 찾아 설명하고 반환 경로를 바꾼다. 혼자서도 수행하며 함께할 때 각자의 근거를 비교한다. TTL·traceroute 보조 질문은 필요한 경우에 고른다.

## 시작 전 짧은 복습

`192.0.2.10/24`의 주소 범위는 어디까지일까? 다른 망으로 보낼 때 Ethernet 프레임의 목적 MAC은 최종 서버의 것일까? [2주차](../week-02/CONCEPTS.md)와 [3주차](../week-03/topics/03-next-hop.md)에서 필요한 설명만 다시 읽는다. 이름·인증서가 맞다는 근거가 TCP 연결 성공까지 보장하는지도 [6주차](../week-06/CONCEPTS.md)와 연결한다.

## 중심 질문 · W07-D1

**A에서 B로 가는 경로가 보이는데도 응답이 없을 때, 어느 장비의 어떤 방향을 더 확인해야 할까?** [교재의 구성](CONCEPTS.md#round-trip)을 보고 먼저 예상한다. 이 질문은 자체 개발 사례이며 특정 기업의 기출이 아니다.

함께 [RFC 1812 §5.2.4.3](https://www.rfc-editor.org/rfc/rfc1812.html#section-5.2.4.3)의 **(1) Basic Match와 (2) Longest Match 두 항목만** 읽는다. destination은 목적지, prefix length는 접두사 길이, next hop은 다음 전달 대상이다. 어느 주소 비트를 비교하는지 찾아 교재의 작은 경로표에 적용한다. 이어 [ip-route의 `ip route get`](https://man7.org/linux/man-pages/man8/ip-route.8.html#DESCRIPTION) 소제목에서 **get a single route부터 no packets are actually sent를 포함한 설명까지** 찾아, 무엇을 조회하며 무엇은 실험하지 않는지 확인한다. 다른 명령·옵션 전체를 읽지는 않는다.

먼저 공식 절과 선택한 접두사를 근거로 A→B와 B→A를 자기 말로 설명한다. 이어 [필수 B](LINUX.md#simulator)의 반환 경로 한 항목을 삭제하고 정상과 비교한다. 혼자라면 두 단계를 직접 수행하고, 함께라면 각자의 시도 후 설명·질문을 주고받는다. 먼저 해설을 열기보다 **요청 도착·응답 생성·응답 전달** 중 어디에서 막혔는지 출력에서 찾는다. 실행 근거는 개인 파일로 한 번 남긴다. [실제 Linux 비교](REAL_ROUTE.md)에서는 같은 구별을 양끝 패킷으로 확인한다.

## 조건 변경 · W07-D2

R2의 `192.0.2.0/24` 경로만 사라지고 나머지는 같다면 A→B 전달과 왕복 결과가 각각 어떻게 될까? 직접 변경·복구하고 경로표와 결과를 대조한다. 함께할 때도 다른 사람의 출력을 읽기만 했다면 제공 분석으로 구별한다.

## 보조 질문 · W07-D3

traceroute의 중간 홉이 `*`인데 그 뒤 홉은 응답했다면 어떤 단정은 피해야 할까? [traceroute DESCRIPTION](https://man7.org/linux/man-pages/man8/traceroute.8.html#DESCRIPTION)에서 **TTL을 늘리는 설명부터 별표 설명까지** 함께 읽는다. 필요하면 [교재](CONCEPTS.md#ttl)와 [가공 기록](LINUX.md#trace)을 사용한다. 실제 traceroute 실행은 선택이며 허가된 대상에만 보낸다.

## 설명을 마친 뒤

다른 목적지나 TTL 조건에서도 결과를 예상한다. 함께할 때는 다른 사람이 먼저 설명해 볼 수 있다. [핵심 3개·혼동 2개](CONCEPTS.md#essentials)를 확인하고 [복습](REVIEW.md)에 답한 뒤 [분리 해설](ANSWERS.md#development)을 읽는다. 탐색이 막히면 진행자가 지정 두 항목을 같이 찾아 준다. 별도 발표나 고정 기록 양식은 없다.
