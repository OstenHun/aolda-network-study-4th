# 4주차 · 함께 찾고 설명할 질문

요약: 보낸 데이터가 상대 프로그램의 처리 성공을 뜻하는지 함께 탐색한다. 공식 절에서 출발해 한 명이 근거로 설명하고 다른 사람이 조건을 바꾸며 송수신·로그·패킷의 관찰 범위를 확인한다.

## 중심 질문 · 데이터가 도착하면 처리가 끝났을까?

1주차에서 정상 200·404·서버 중지 후 연결 실패를 구별했다. 이번에는 TCP ACK를 봤을 때 무엇까지 알 수 있는지 묻는다. **송신 API 성공, TCP ACK, 애플리케이션 응답은 같은 증거일까?** 답을 먼저 외우지 않고 함께 아래 절에서 근거를 찾는다.

- 검색 출발: [RFC 9293 §2.2](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2)의 전달 서비스, [Python 소켓 HOWTO의 Using a Socket](https://docs.python.org/3.12/howto/sockets.html#using-a-socket)의 send/recv 설명.
- 함께 공부: [소켓과 연결](CONCEPTS.md), [스트림과 데이터그램](CONCEPTS.md#stream), [SEQ/ACK 시간축](CONCEPTS.md#reliability)을 읽고 모르는 용어를 나눈다.
- 한 명 설명: 자신이 고른 근거가 커널 수신·앱 수신·업무 처리 중 어느 단계의 증거인지 말한다.
- 조건 변경: 서버 포트를 잘못 적거나 서버가 데이터를 받고 응답 전에 멈춘다면 어떤 증거가 달라질지 다른 사람이 설명한다. [실습 B](LINUX.md#experiment-b)에서는 포트만 바꾸고 복구한다. 앱 중단은 추가 변경 없이 생각 실험으로 다룬다.
- 비교: 설명 뒤 [중심 질문 해설](ANSWERS.md#inquiry)로 확인한다. 직접 실행·제공 분석·예상을 구별한다.

## 선택 보조 질문 · 두 번 보내면 두 번 받을까?

같은 IP·port로 `hello`와 `network`를 보낼 때 TCP/UDP 수신 코드의 종료 조건은 어떻게 정할까?

함께 [RFC 768의 Introduction·User Interface](https://www.rfc-editor.org/rfc/rfc768.html), [Python HOWTO](https://docs.python.org/3.12/howto/sockets.html#using-a-socket)를 읽는다. [실습 A](LINUX.md#experiment-a)에서 `recv(3)`을 `recv(1)`로 바꾼 경우와 UDP의 `recvfrom(64)`를 비교한다. 한 실행에서 TCP 청크가 두 개였다는 사실을 일반 규칙으로 만들지 않는다. 해설은 [Q2·Q7](ANSWERS.md#q2-메시지-경계)에 있다.

## 선택 보조 질문 · 세 메시지는 몇 RTT일까?

SYN 출발을 0ms로 두고 양방향 편도가 50ms라면 클라이언트와 서버는 언제 연결 수립 상태가 될까? 반대 방향만 70ms로 바뀌면 무엇이 달라질까? [RFC 9293 §3.5 Figure 6](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5)과 [W04-D1~D3](CONCEPTS.md#개발-상황으로-설명하기)에서 시간축을 찾는다. 이 값은 실측이 아닌 계산 조건이다.

## 함께 확인하기

이번 설명자가 아닌 사람은 포트·수신 크기·지연 중 조건 하나를 골라 짧게 다시 설명한다. 다음 질문이나 회차에는 설명자를 바꾼다. 막히면 [교재](CONCEPTS.md)로 돌아가며 긴 발표·팀 기록·개인 마무리 작성은 요구하지 않는다. 필요할 때 자유롭게 메모하고 직접 실행 근거는 개인 파일에 보관한다.
