# 4주차 · 공식 출처와 읽을 범위

요약: TCP·UDP와 소켓 예제를 확인할 공식 절을 연결한다. 긴 원문을 복제하지 않고 자체 질문·가상 시간축으로 설명하며 표준의 역할과 실제 운영체제 출력의 차이를 구별한다.

## 함께 읽을 출발점

공동 탐색은 아래 두 항목의 지정 절에서 시작한다. 문서 전체를 추가 필독으로 요구하지 않는다.

| 출처 | 읽을 절과 이번에 쓸 내용 |
| --- | --- |
| [IETF RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html) | §2.2 서비스, §3.3.2 상태, §3.4 SEQ, §3.5 Figure 6 연결, §3.6 종료. 소켓·연결·스트림·ACK의 근거 |
| [Python 3.12 Socket Programming HOWTO](https://docs.python.org/3.12/howto/sockets.html#using-a-socket) | Using a Socket. send/recv와 메시지 길이·EOF·앱 경계의 관계 |

## 필요한 부분을 더 확인하기

- [RFC 768](https://www.rfc-editor.org/rfc/rfc768.html): Introduction·User Interface. UDP의 데이터그램과 전달/중복 보호를 보장하지 않는 범위. 정상 실험에서 반드시 손실이 난다는 뜻은 아니다.
- [RFC 6298 §2·§5](https://www.rfc-editor.org/rfc/rfc6298.html#section-2): RTT 표본과 재전송 타이머. 본문의 타이머 시간축은 실제 RTO 계산·실측을 재현하지 않는다.
- [RFC 5681 §2·§3](https://www.rfc-editor.org/rfc/rfc5681.html#section-2): 수신 윈도와 혼잡 윈도의 역할. 이번에는 흐름/혼잡 제어의 대상을 구별하며 알고리즘·성능 계산은 후속으로 둔다.
- [Python 3.12 socket API](https://docs.python.org/3.12/library/socket.html): `accept`, `recv`, `recvfrom`, `sendall`, `sendto`, `settimeout`, 컨텍스트 관리자. 반환값·시간 제한·예외 처리를 확인한다.
- [iproute2 ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html): `-t`, `-u`, `-l`, `-a`, `-n`과 포트 필터. 배포판 버전별 출력 차이는 현장 도움말과 대조한다.
- [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer): Core Protocols의 TCP/UDP 학습 위치. 기술 내용을 확인할 때는 위 RFC·API 원문과 직접 관찰한 결과를 대조한다.

## 자체 자료의 성격

W04-D1~D3·복습 아홉 문항·공동 질문·SEQ/ACK 시간축·소켓 코드는 이 스터디의 자체 자료다. 기업 기출이나 공식 채용 범위로 표시하지 않는다. 패킷 표는 실제 캡처가 아니며 예제 포트·루프백 주소는 실제 서비스 접속 값이 아니다.

[교재](CONCEPTS.md) · [실습 코드 읽기](LINUX.md#code-reading) · [학습 홈](README.md)
