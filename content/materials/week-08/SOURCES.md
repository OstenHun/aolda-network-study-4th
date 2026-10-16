# 공식 출처와 읽을 범위 · 중간 복습

요약: TLS 메시지 순서와 HTTP 저장 응답 사용 조건을 필수로 함께 읽는다. 신뢰 전송 저자 노트·IPv6 표준·Linux 매뉴얼은 지정 부분을 대조한다. 자체 시간축·계산·가공 trace는 실측과 구별한다.

## 참가자가 함께 읽을 절

확인 기준은 2026-10-17이다. 앵커가 문서 처음을 열면 정확한 제목/용어로 문서 내 검색한다. 전체 RFC 정독을 요구하지 않는다. 영문이 막히면 [교재](CONCEPTS.md)의 시간축·표를 먼저 대조한다.

| 자료·읽을 부분 | 구분·찾을 것 | 쓰는 곳 |
| --- | --- | --- |
| [RFC 8446 §2](https://www.rfc-editor.org/rfc/rfc8446.html#section-2), 그림 1 **Basic Full TLS Handshake**와 바로 위 도입 | 중심 필수: ClientHello, 서버 메시지 묶음, Finished/응용 데이터의 순서. 암호 수식/전체 필드 제외 | K1·D1·Q1\~Q2 |
| [RFC 9111 §4](https://www.rfc-editor.org/rfc/rfc9111.html#section-4), **Constructing Responses from Caches**의 첫 조건 목록 | 중심 필수: fresh·validation을 포함해 저장 응답을 쓸 조건. 목록 뒤 상세 규칙은 필요 시 참고 | K1·D2·Q3 |
| [RFC 4291 §2.2·§2.3](https://www.rfc-editor.org/rfc/rfc4291.html#section-2.2), 주소/접두사 표기의 첫 예시 | 보조 선택 읽기: 16진수 묶음·::·접두사 길이. IPv6 비교 자체는 교재로 필수 확인 | K3·Q6 |
| [Kurose·Ross 3.4](https://gaia.cs.umass.edu/kurose_ross/videos/3/), **Principles of Reliable Data Transfer**의 [Notes](https://gaia.cs.umass.edu/kurose_ross/videos/3/4/3.4_RDT_video_slides.pptx) 슬라이드 36\~42 중 Go-Back-N/Selective Repeat 송수신·손실 예시 | 보조 선택 읽기: 누적/개별 ACK·순서 밖 보관·timeout. 영상 전체/유한 상태 기계 전체는 요구하지 않음 | K2·Q4\~Q5, 교재 제공 분석은 필수 |

## 개념 주장의 근거

- DNS 캐시: [RFC 1034 §3.6](https://www.rfc-editor.org/rfc/rfc1034.html#section-3.6)의 Resource Record TTL 필드와 캐시 시간 제한. [5주차 출처](../week-05/SOURCES.md)의 이름/주소·TTL 설명을 재사용한다.
- HTTP 재사용/캐시: [RFC 9112 §9.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3), [RFC 9111 §4·§4.3](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.3). [6주차 출처](../week-06/SOURCES.md)를 이어 쓴다. D+3R 등은 교재의 조건으로 유도한 자체 계산이며 표준이 정한 고정 웹 지연이 아니다.
- 실제 TCP와 교육 모형 구별: [RFC 9293 §3.4](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.4)의 바이트 시퀀스/누적 확인. GBN/SR은 위 저자 교육 자료, 네 단위 손실 예시는 자체 작성이다. 저자 노트는 GBN 수신 버퍼를 구현 선택으로도 설명하며, 이 교재는 순서 밖 데이터를 버리는 모형을 명시해 사용한다.
- IPv6 주소·루프백·링크 로컬: [RFC 4291 §2.2·§2.3·§2.5.2·§2.5.3·§2.5.6](https://www.rfc-editor.org/rfc/rfc4291.html#section-2.5.3), 문서 주소는 [RFC 3849 §2](https://www.rfc-editor.org/rfc/rfc3849.html#section-2). RFC 4291의 다른 절/과거 인터페이스 ID 생성 방식을 현재 모든 호스트 규칙으로 확대하지 않는다.
- IPv4 비교: [RFC 1122 §3.2.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#page-30)의 127 루프백, [RFC 3927 §1](https://www.rfc-editor.org/rfc/rfc3927.html#section-1)의 링크 로컬 범위. 외부 접근 성공과 별개다.
- NDP: [RFC 4861 §3·§3.1](https://www.rfc-editor.org/rfc/rfc4861.html#section-3)의 이웃/라우터 발견·NS/NA와 ARP 등과의 비교. §2.3의 solicited-node 주소 용어도 제공 trace 해석에 참고한다. SLAAC/DHCPv6·실제 NDP 구성은 선택이다.
- [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer)는 전체 학습 범주의 지도다. 개별 기술 정답이나 기업 기출의 증거로 쓰지 않는다.

<span id="commands"></span>

## Linux 명령과 기존 코드

[ip-address(8)](https://man7.org/linux/man-pages/man8/ip-address.8.html)의 address show·scope, [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html)의 show/table local/get·패킷 미전송 설명, [ip-neighbour(8)](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html)의 neigh show, [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html)의 -4/-6/-V를 실습 A와 대조한다. [ping(8)](https://man7.org/linux/man-pages/man8/ping.8.html)의 -4/-6/-n/-c/-W·권한 조건은 iputils Linux 기준이다. 다른 OS의 옵션과 섞지 않는다.

실습 B는 [curl 공식 매뉴얼](https://curl.se/docs/manpage.html)의 --noproxy·--http1.1·--connect-timeout·--max-time·-i/-v와 EXIT CODES, [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html)의 -l/-t/-n·sport 필터를 사용한다. 404는 기본 curl의 전송 실패 종료 코드와 별개다. 제공 Python HTTP 서버는 [6주차 코드/공식 API 근거](../week-06/SOURCES.md), 경로 보충 모형은 [7주차 근거](../week-07/SOURCES.md)를 그대로 연결한다.

## 자체 작성과 관찰 범위

교재·질문·해설·시간축·주소 예시·IPv6 사건 기록은 이 스터디의 자체 작성이며 실제 측정/기업 기출이 아니다. RFC/강의의 긴 문장·슬라이드·그림·외부 코드를 복제하지 않고 링크와 필요한 개념을 자체 예제로 설명한다. 저자 강의 자료는 원저작권을 따르며 재배포 파일에 넣지 않는다. 실제 Linux 출력·패킷·수행 결과는 본인이 실행한 환경/관찰 위치에서만 판단한다. 필수 직접 장애 수행을 제공 trace로 완료 처리하지 않는다.
