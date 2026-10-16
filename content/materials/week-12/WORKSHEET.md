# 12주차 · 함께 찾을 질문

요약: 연결 표시와 서비스 성공을 구별할 근거를 함께 찾고 한 명이 설명한다. 다른 사람은 신호·경로·정책 중 조건 하나를 바꾸어 확인하며 두 제공 분석과 작은 망 구성도로 이어 간다.

## 시작 전에 떠올리기

7주차의 로컬 `ip route get`이 왕복 성공까지 증명하는가? 11주차에서 timeout과 서버 중지를 어떤 근거로 구별했는가? 막히면 [7주 교재](../week-07/CONCEPTS.md)·[11주 교재](../week-11/CONCEPTS.md)로 돌아간다.

## 중심 질문 · 연결됐는데 왜 서버에 닿지 않을까?

`wifi-state.txt` A/C와 `vpn-routes.txt` V1/V2를 먼저 읽는다. Wi-Fi와 VPN 연결 표시가 각각 무엇을 증명하고, 서버 요청 실패의 원인을 좁히려면 어느 위치를 봐야 할까?

함께 [RFC4301 §4.4.1](https://www.rfc-editor.org/rfc/rfc4301.html#section-4.4.1)의 첫 문단과 ‘Processing Choices: DISCARD, BYPASS, PROTECT’ 바로 아래 문단에서 보호·우회·폐기를 찾는다. 이어 [Linux Wireless의 Getting link status](https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html#getting-link-status)의 명령·필드를 짧게 읽는다. 목적은 연결 정보와 접근 판단이 서로 다른 근거라는 점을 찾는 것이다. 영문이 막히면 [K1·K3](CONCEPTS.md)와 [공식 읽기 안내](SOURCES.md)로 돌아간다.

한 사람이 출발지→AP/기존 LAN→경로→VPN GW/정책→서버→응답을 설명한다. 다른 사람은 V3처럼 **경로 한 항목**만 달라진 자료로 설명이 유지되는지 묻는다. 정답은 [분리 해설](ANSWERS.md)에 두며 한 명의 설명을 전원 수행으로 간주하지 않는다.

## 선택 보조 질문

- 신호가 더 강하면 항상 HTTP가 성공할까? A/B/C 중 주장을 구별할 두 사례와 추가 관찰을 고른다.
- CSMA/CA가 있어도 충돌할 수 있을까? `medium-access.txt`의 첫 백오프를 바꿔 보고 현대 전이중 Ethernet과 비교한다.

설명자는 질문이나 회차마다 교대한다. [실습 A/B](LINUX.md)에서 각자 자료를 분석하고 그림을 그린다. 자세한 메모는 선택이며 기존 개인 근거를 한 번 보관한다.

<span id="development"></span>
## W12-D1~D3 · 원격 개발자의 HTTP 접속

자체 개발 사례다. 회사 기출을 재현한 문항이 아니다. `vpn-routes.txt`의 고정 IP·TCP8080·프록시 없음 조건을 사용한다.

- **D1 설명:** V1에서 사내 서버 요청과 외부 서비스 요청의 경로·보호 구간은 어떻게 다른가? VPN 연결 표시 외에 필요한 근거는 무엇인가?
- **D2 조건 하나 변경:** V2처럼 서버 TCP8080 접근 규칙만 DROP이면 연결 표시·서버 LISTEN·새 GET은 각각 어떻게 보일까? 서버를 재시작할 근거가 충분한가?
- **D3 다음 진단:** 실제 환경에서 timeout만 보고 V2인지 V3인지 모른다. 두 가설을 구별할 다음 관찰 두 곳과 복구 후 다시 볼 정상 기준을 고른다.

[해설과 필수 요소](ANSWERS.md#development)는 먼저 설명한 뒤 읽는다. 다음에는 [C12](LINUX.md#c12)에서 기존 본인 STP/LACP·OSPF·정책 변경 근거를 재사용한다.
