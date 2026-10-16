# 1주차 예제 캡처

요약: Windows 루프백에서 수집한 HTTP 예제 패킷이다. 서버 포트 59995의 정상·404·연결 거부·복구를 비교하며 본인 Linux 직접 캡처와 구분한다.

## 캡처 열기

1. [week-01-local.pcapng](week-01-local.pcapng)을 Wireshark로 연다.
2. 표시 필터 tcp.port == 59995를 쓴다. Linux 실습 기본 포트 8080과 다르다.
3. HTTP로 해석되지 않으면 Analyze → Decode As → HTTP를 적용한다.
4. [제공 캡처 분석](../week-01/SAMPLE_CAPTURE.md)의 패킷 번호·방향·HTTP 상태를 비교한다.

주소는 루프백이며 기기·인터페이스 메타데이터를 제거한 예제다. 제공 파일을 읽은 것과 본인이 직접 캡처한 것을 구분한다.
