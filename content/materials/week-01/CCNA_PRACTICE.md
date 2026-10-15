# 1주차 CCNA 연계 연습

요약: 출판사 원문 3문항·자체 보충 2문항에 기출 표방 사이트의 짧은 질문 1개를 선택 추가했다. 사이트 문항은 실제 출제 여부 미확인으로 표시하고 자체 해설로 검토한다.

## 사용 순서

[기존 복습](REVIEW.md) 뒤의 선택 보충이다. 개인 풀이 5~10분 → 짝과 오답 이유 설명 5분 → 실습에 연결 5분으로 진행한다. 영어 읽기가 오래 걸리면 외부 1문항과 자체 2문항만 고른다. 기존 실습 완료 기준은 유지한다.

미리 알아둘 말: application은 응용 계층, transport는 전송 계층, adjacent는 인접, encapsulation은 캡슐화다. TCP와 UDP는 전송 계층 프로토콜이다. UDP 상세 비교는 4주차에 다룬다. 캡슐화는 데이터를 전달하며 각 계층의 제어 정보를 덧붙이는 과정이다.

## 외부 원문 3문항

출처: Wendell Odom, *CCENT/CCNA ICND1 640-822 Official Cert Guide*, 3판, Cisco Press, © 2012 Pearson. [출판사 공개 샘플 PDF](https://www.ciscopress.com/content/images/9781587204258/samplepages/1587204258.pdf#page=51).

구판 교재의 학습용 퀴즈다. 실제 출제 기출이나 현재 200-301의 범위·난이도를 대표하는 자료는 아니다. 기초 개념만 선별했다. 문제와 보기는 원문에서 읽고 아래에는 문항 위치와 자체 활동 안내만 둔다.

| ID | 원문 위치 | 개념 | 풀이 후 실습에 연결 |
| --- | --- | --- | --- |
| C1 | Chapter 2, Do I Know This Already? 1번. 인쇄 p.18 / PDF 51쪽 | 전송 계층 프로토콜 | HTTP와 TCP의 역할을 구분한다. 낯선 보기의 세부 기능은 평가에서 제외한다. |
| C2 | 같은 퀴즈 3번. 인쇄 p.18 / PDF 51쪽 | 인접 계층 관계 | HTTP 데이터가 TCP를 통해 전달되는 관계를 그린다. |
| C3 | 같은 퀴즈 5번. 인쇄 p.19 / PDF 52쪽 | 캡슐화 | 패킷 상세에서 IP·TCP·HTTP 정보를 찾는다. 루프백의 링크 계층 표현을 Ethernet으로 단정하지 않는다. |

각자 `문항 ID / 선택한 답 / 근거 / 헷갈린 보기 / 실습과 연결한 한 문장`을 기록한다.

## 바로 풀 자체 보충 2문항

이 스터디의 상황으로 새로 작성했다. 외부 문제의 번역·복제본이나 실제 CCNA 기출이 아니다. 데이터는 문제용 예시이며 실측으로 기록하지 않는다. 정답 하나와 오답의 이유를 적는다.

### C4. 같은 서버의 두 포트

Linux VM의 Python HTTP 서버는 `127.0.0.1:8080`에서 대기 중이다. 같은 VM의 curl이 `http://127.0.0.1:8081/echo`로 요청했고 연결에 실패했다. 다음 행동으로 가장 적절한 것은?

- A. IP가 같으므로 서비스에 도달했다. `/echo` 경로만 바꾼다.
- B. 서버의 대기 포트와 요청의 목적지 포트를 맞춘 뒤 다시 요청한다.
- C. HTTP 상태 8081에 해당하는 오류 설명을 찾는다.
- D. 두 프로그램의 IP가 같으므로 클라이언트·서버 역할을 구별할 수 없다.

### C5. 연결과 자원

키트의 HTTP/1.1 서버에 curl로 요청했다. 상태 줄은 `HTTP/1.1 404 Not Found`이고 서버 로그에도 해당 요청이 남았다. 관찰을 가장 잘 설명하는 것은?

- A. TCP 연결을 맺지 못했으므로 서버가 HTTP 응답을 보내지 못했다.
- B. TCP가 데이터를 전달하면 응용 계층도 언제나 성공하므로 캡처가 잘못됐다.
- C. HTTP 응답은 받았지만 요청한 자원을 찾지 못했다. 연결 실패와 구별한다.
- D. 서버 로그가 있으므로 이후 모든 요청도 성공할 것이다.

풀이 뒤 [해설](CCNA_ANSWERS.md)을 연다.

## 기출·연습 사이트 확인 기록

### C6. 기출 표방 사이트 문항 — 선택 5분

[ExamTopics 200-301, Topic 1, Question 84](https://www.examtopics.com/discussions/cisco/view/72120-exam-200-301-topic-1-question-84-discussion/)의 질문 부분을 짧게 인용한다.

> What is the difference in data transmission delivery and reliability between TCP and UDP?

사이트는 실제 시험 문항이라고 표시하지만 진위는 확인하지 못했다. 아래 활동은 자체 작성이며 객관식 보기 전체는 원문 링크에서 읽는다.

TCP와 UDP의 연결·전달 특성을 두 문장으로 비교해 본다. UDP를 아직 배우지 않았다면 진행자와 함께 읽거나 4주차에 다시 푼다. 1주차 필수 평가에 포함하지 않는다. 원문의 속도 비교가 모든 환경에서 성립하는지도 토론한다. 답은 [C6 해설](CCNA_ANSWERS.md#c6--tcp와-udp의-전달-특성)에서 확인한다.

외부 문항의 재배포 허가는 확보하지 않았다. C6의 짧은 질문 인용 외에 문제·보기·해설 전체는 복제하지 않고 원문 링크로 안내한다.

| 자료 | 확인 사실·한계 | 활용 판단 |
| --- | --- | --- |
| 위 Cisco Press 샘플 | 출판사 공개 PDF·문항 확인. 저작권 페이지는 서면 허가 없는 복제·전송을 제한 | C1~C3 원문 링크·번호 제공. PDF나 문제·보기 번역본은 재배포하지 않음 |
| [CISNET 연습문제](https://www.cisnet.ca/tools/ccna-practice-questions) | 강사 작성·무료·가입 불필요라고 안내. 확인한 첫 문제는 스위치 계층. 전체 동적 퀴즈는 미검증 | LAN·스위칭 주차 후보. 복제 허가는 미확인 |
| [CertSafari 샘플](https://www.certsafari.com/cisco/ccna-associate/practice-questions) | 공개 1번 TCP·UDP 비교 확인. 흐름 제어는 이번 주 범위 밖. 복제 허가 미확인 | 4주차 후보. 실제 기출로 인정하거나 본문을 복제하지 않음 |
| [ExamTopics CCNA](https://www.examtopics.com/exams/cisco/200-301/) | 메인·일부 직접 조회 실패. 검색 결과로 Q84 질문·보기 확인. 실제 출제 진위·Cisco 승인·재배포 권한 미확인 | C6에 짧은 질문 인용·원문 링크·자체 검토 해설 추가. 보기 전체는 원문에서 확인 |
| [Cisco 공식 CCNA 안내](https://www.cisco.com/site/us/en/learn/training-certifications/exams/ccna.html) | Cisco U. 연습시험 연결 확인. 로그인 후 문제·가격·이용 권한은 미확인 | 추가 공식 경로. 필수 구매·가입 조건은 아님 |

[Cisco 시험 정책](https://www.cisco.com/site/us/en/learn/training-certifications/exams/policies.html)은 실제 시험 문제·답·그림을 비공개 자산으로 명시한다. C6은 기출 표방 사이트에 실린 질문의 짧은 인용이며, 공식 공개 기출 또는 자유 재배포가 허가된 문항이라는 뜻은 아니다.

