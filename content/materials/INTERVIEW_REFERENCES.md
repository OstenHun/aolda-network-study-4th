# 면접·개발 질문 참고자료

요약: 공개 저장소는 질문과 연결 순서를 찾는 데 쓰고, 기술 설명은 RFC·공식 문서와 대조한다. 공식 채용 범위·공개 학습 자료·스터디 자체 문항을 구별하며 회사별 실제 출제 빈도는 주장하지 않는다.

- 이 문서에서는 자료를 고른 이유와 읽을 범위를 확인한다. 기술 해설은 해당 주차 교재에서 읽는다. RTT·연결 수립은 [4주차 TCP](week-04/CONCEPTS.md), 연결 재사용은 [6주차 HTTP](week-06/CONCEPTS.md)에서 읽는다.

## 공개 저장소에서 참고할 것

| 자료·작성자 | 확인한 범위와 활용 | 이번에 옮기지 않은 것 |
| --- | --- | --- |
| [System Design Primer — Donne Martin](https://github.com/donnemartin/system-design-primer#latency-vs-throughput) | Latency vs throughput, DNS·CDN·load balancer 목차. 지연과 처리량을 구별하고 설계 이유를 묻는 질문 구성에 참고. 4~6·14주차 선택 읽기 | 긴 본문·그림·문항을 복사하지 않음. 회사 공식 문제집으로 취급하지 않음 |
| [What happens when — alex와 기여자](https://github.com/alex/what-happens-when#the-g-key-is-pressed) | URL 입력을 DNS·ARP·소켓·TLS·HTTP로 연결하는 질문의 분해 방식. 3주차는 ARP/다음 홉, 5~6주차는 전체 흐름의 선택 길잡이 | 원문의 ARP 요청 전달·스위치 설명과 구현별 브라우저 동작을 정답으로 채택하지 않음. Ethernet 브로드캐스트 처리와 경로 선택은 공식 근거로 재확인 |

[How the web works — vasanthk](https://github.com/vasanthk/how-web-works)는 비교 검토했으나 필수 읽기로 채택하지 않았다. 오래된 TLS 키 교환·SPDY·브라우저 설명이 섞여 있어 현재 HTTP/TLS 설명의 정본으로 삼기 어렵다.

위 저장소는 커뮤니티 학습 자료다. 이번 질문·해설·숫자 예제는 스터디가 새로 작성했다. System Design Primer는 저장소가 밝힌 작성자와 CC BY 4.0을 확인했다. 원문 재사용 시 해당 리비전·라이선스·출처·변경 사항을 별도 확인한다. 별도 라이선스를 확인하지 않은 자료의 본문·그림은 복제하지 않는다. 별 개수나 저자의 근무 이력은 기술 정확성·실제 출제의 근거가 아니다.

## 공식 문서로 설명 대조하기

| 근거 | 읽을 범위 | 연결 |
| --- | --- | --- |
| [RFC 9110 §15.5.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.5) | 404의 의미 | 1주차 HTTP 응답과 연결 실패 |
| [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1) | 접두사 표기와 블록 크기 | 2주차 CIDR |
| [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) | get, via, dev, src | 2~3주차 실제 경로 판단 |
| [RFC 826](https://www.rfc-editor.org/rfc/rfc826.html) · [ip-neighbour(8)](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html) | ARP 생성·수신, 이웃 상태 | 3주차 링크 전달·캐시 |
| [ping(8)](https://man7.org/linux/man-pages/man8/ping.8.html) | DESCRIPTION, RTT 통계 | 3주차 ICMP 왕복과 앱 지연 구별 |
| [RFC 9293 §3.5](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5) · [RFC 9112 §9.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3) | TCP 상태 전이, HTTP/1.1 지속 연결 | 공통 RTT 해설·4~6주차 |
| [MDN 연결 관리](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Connection_management_in_HTTP_1.x) | 지속 연결·파이프라이닝·다중화 구별 | 6주차 연결 재사용 |
| [AWS timeout·재시도·backoff](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | timeout과 부수 효과, 재시도 부하·멱등성 | 14주차 개발 사례 후보 |

## 면접 질문에 붙일 출처 표시

- **공식 채용 안내:** 예를 들어 [Amazon 소프트웨어 개발 준비 범위](https://amazon.jobs/content/en-gb/how-we-hire/interview-prep/software-development-topics)는 Internet topics를 포함한다. 특정 질문의 실제 출제·빈도까지 확인한 것은 아니다.
- **공개 학습 자료:** 저장소·작성자·읽은 절·확인일을 남긴다. 버전에 따라 달라지거나 단순화된 설명은 공식 자료와 대조한다.
- **스터디 자체 문항:** 어떤 개념을 평가하려고 만들었는지, 조건·답에 포함할 내용·흔한 오답·확인 근거를 붙인다. 이번 1~3주차 개발 질문은 여기에 해당한다.
- **후기:** 실제 회사·직무·시점의 개인 경험이라는 한계를 붙인다. 사실 확인 없는 ‘빅테크 공통 필수·빈출’ 표시는 사용하지 않는다.

## 학습에 배치하는 방법

필수 외부 읽기를 추가하지 않는다. 해당 주차 핵심 정리와 기존 공통 질문에서 개발 사례 하나를 사용한다. 공개 저장소는 필수 학습 뒤 필요한 절만 선택한다. 개념을 설명하지 못한 상태에서 전체 시스템 설계 문제로 확장하지 않는다.

[개념 색인](CONCEPT_INDEX.md) · [1주차 핵심](week-01/ESSENTIALS.md) · [2주차 핵심](week-02/ESSENTIALS.md) · [3주차 핵심](week-03/ESSENTIALS.md)

## SRE 후속 학습과 평가 연결

[공식 자료 색인](REFERENCE_GUIDE.md#심화-공식-자료)에서 필요한 절을 찾아 읽는다. Google SRE·AWS 문서는 운영 원리와 문제 분해의 근거이며 기업 공식 면접 문항이나 출제 빈도를 뜻하지 않는다. Kubernetes의 학습 깊이는 지원 역할에 맞춰 정한다.

장애 진단 문제는 증상·조건·관측 자료를 먼저 읽고 원인 가설과 확인 방법을 설명한다. 지원 공고의 OS·코딩·분산 시스템 요구도 함께 대조한다.

## 공통 과정에서 연습할 것

중심 질문에서 원리와 이유를 설명하고, 조건이 바뀌었을 때의 동작과 장애 확인 방법을 연습한다. 후속 학습에서는 부하가 크거나 장애 원인이 겹친 상황을 다루고 설계를 더 자세히 살펴본다.
