# 2주차 공개 문항 출처와 검증

요약: 선택 연습 문제의 대학 시험 원문·풀이 범위·공식 개념 근거를 안내한다. 대학의 과거 시험과 출제 진위가 확인되지 않은 제삼자 사이트를 구분하고 답이 포함된 원문은 풀이 뒤 연다.

## 채택 기준과 사용 범위

2주차 필수 범위는 IPv4 주소 용도, `/24`·`/26`, 네트워크·브로드캐스트·일반 호스트 범위, 게이트웨이와 실제 도달성의 차이다. 공개 자료에서 이 주제와 연결되는 **문항 위치를 직접 확인**했다. [연습 문제](CCNA_PRACTICE.md)에서 소문항 위치와 풀이 범위를 확인한다. 문항에 답과 해설이 함께 인쇄된 PDF는 풀이 후 열도록 안내한다. 온라인에 공개되었다는 사실은 재배포 허가를 뜻하지 않는다.

## 대학의 과거 시험 — CCNA 기출 아님

| 문항 | 출제 이력과 원문 위치 | 직접 확인한 사실 | 채택과 한계 |
| --- | --- | --- | --- |
| C1 | [Brown CSCI 1680 이전 시험 목록](https://cs.brown.edu/courses/csci1680/s22/assignments/)의 **2016 Midterm (Solutions)** → [Q2(d), PDF 4쪽](https://cs.brown.edu/courses/csci1680/s22/content/midterm-f16-sol.pdf#page=4) | H1 `192.168.1.5`, H2 `.180`, GW `.1`, 원래 `/24`, H1 마스크를 `255.255.255.128`로 바꾸는 소문항과 다음 전달 상대 설명을 확인 | `/24`에서 `/25`로 달라진 H1의 판단을 풀게 함. 원문의 스위치 공격·ARP 상세 소문항은 제외 |
| C2 | Duke CS 356 [2014-03-06 중간고사 샘플·해설, Q2(a), PDF 5쪽](https://courses.cs.duke.edu/spring15/compsci356/sample-midterm.pdf#page=5) | `192.168.1.0/24`를 최대 100·50·50호스트인 세 LAN에 나누는 조건과 `/25`, `/26`, `/26` 해설 확인 | 해당 (a)만 선택 확장으로 채택. 이어지는 (b) 해설에는 네트워크 주소를 라우터 인터페이스 주소로 쓴 행이 있어 모범 호스트 배정으로 사용하지 않음 |
| C3 | UC San Diego CSE 123 [2015 중간고사 해설, Q3(b)~(e), PDF 4쪽](https://cseweb.ucsd.edu/classes/fa15/cse123-a/midterm15.pdf#page=4) | `184.86.92.182`, `/16` 크기의 범위를 8등분, 마스크·CIDR·네트워크·브로드캐스트 계산을 확인 | `/19` 확장만 선택. 옛 클래스 기반 주소 체계를 현대 CIDR의 암묵 마스크 규칙으로 가르치지 않음 |

위 문서는 대학 서버의 시험 자료이며 각 과정의 실제 이전 평가 문제로 확인했다. 이것이 **Cisco 200-301 시험의 실제 문항**이라는 뜻은 아니다. C2 PDF는 게시 경로에 `sample-midterm`이지만 문서 본문에 “CS 356 Midterm, March 6, 2014”로 표기되어 있다. C1은 Brown의 “Previous exams” 목록에서 연결된다.

## CCNA 기출을 표방하는 제삼자 사이트

| 문항 | 확인한 공개 내용 | 검증 한계와 채택 |
| --- | --- | --- |
| C4 | [ExamTopics 200-301 Topic 1 Question 94](https://www.examtopics.com/discussions/cisco/view/75248-exam-200-301-topic-1-question-94-discussion/)의 검색 색인에서 RFC 1918 목적 질문과 A~D 보기 확인 | 사이트가 “Actual exam question”이라고 주장한다. **Cisco가 실제 출제·승인한 사실은 확인되지 않았다.** 원문 접근이 제한되어 검색 색인에 드러난 질문·보기만 확인된 자료다. 자체 해설은 [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918#section-3)과 대조 |

시험 덤프의 투표나 제안 답안은 출제 기관의 정답이 아니다. [Cisco 시험 정책](https://www.cisco.com/site/us/en/learn/training-certifications/exams/policies.html)은 실제 시험 내용의 기밀성을 안내한다. 이 자료는 외부 사이트의 **주장과 출처가 불확실한 질문을 비판적으로 검토**하는 선택 활동으로만 쓴다. 현행 시험 문항의 검증된 재현본으로 소개하지 않는다.

## 개념 근거와 독립 검산

| 근거 | 적용한 판단 |
| --- | --- |
| [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632#section-3.1) | `/n`이 왼쪽부터 중요한 접두사 비트 수를 표시. 주소에 과거 클래스만 보고 마스크를 추정하지 않음 |
| [RFC 1918 §3](https://www.rfc-editor.org/rfc/rfc1918#section-3) | 사설 범위 `10/8`, `172.16/12`, `192.168/16`과 공용 고유 주소 수요 절약 |
| [RFC 1122 §3.2.1.3](https://www.rfc-editor.org/rfc/rfc1122#section-3.2.1.3) | `127/8`은 호스트 내부 루프백, 서브넷 브로드캐스트는 일반 호스트 주소가 아님 |
| [IANA IPv4 특수 목적 등록부](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml) | `192.0.2.0/24`는 TEST-NET-1 문서 예시용. 사설/루프백/문서 예시용을 공인 주소와 혼동하지 않음 |

`ipaddress`로 독립 계산을 검산한다. 검산 대상은 복습 Q2·Q3·Q4·Q8과 C1·C2·C3·C5·C6의 주소·접두사·네트워크·브로드캐스트·호스트 경계다. 검산은 주소 범위 계산을 확인하며 실제 패킷 도달·응답을 시험하지 않는다.

## 문제와 해설

- [자체 복습](REVIEW.md) · [해설](ANSWERS.md)
- [공개 문항 연계 연습](CCNA_PRACTICE.md) · [해설](CCNA_ANSWERS.md)

외부 페이지·PDF는 네트워크나 사이트 접근 제한 때문에 열리지 않을 수 있다. C4는 검색 색인에 드러난 질문·보기만 확인된 자료이며 실제 CCNA 출제 여부는 확인되지 않았다. 대학 시험의 해설도 계산·주소 배정 조건을 직접 대조해 읽는다.
