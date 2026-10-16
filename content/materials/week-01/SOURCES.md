# 1주차 출처와 원문 읽기 안내

요약: roadmap.sh의 용어별 참고 글을 1주차 교재·실습과 함께 읽는다. 필수는 포트·HTTP 원문 지정 부분 10분이며 나머지는 선택이다. 입문 글과 공식 검증 자료, 원문을 읽은 것과 직접 설명·실습한 것을 구분한다.

## 필수 읽기 — 총 10분, 교재 30분 안에서 조절

[한국어 교재](CONCEPTS.md)와 [원문으로 배우기](ARTICLE_LESSON.md)를 함께 사용한다. roadmap.sh 용어 → 연결된 글 → 읽을 부분 → 한국어 설명 → 실습 질문의 대응은 원문 학습 교재가 관리한다. 영어 원문을 모두 번역하거나 외부 과제를 전부 풀 필요는 없다. 원문에서 못 읽은 부분은 짝과 교재의 대응 개념을 확인한다.

| 자료 | 읽을 부분 | 시간·확인 질문 |
| --- | --- | --- |
| [Port → Cloudflare](https://www.cloudflare.com/learning/network-layer/what-is-a-computer-port/) | What is a port?와 What is a port number? | 5분. 같은 IP에서 두 통신 끝점을 어떻게 구별하는가? 기본 80번과 키트의 8080을 구분 |
| [HTTP / HTTPS → AWS](https://aws.amazon.com/compare/the-difference-between-https-and-http/) | How does HTTP protocol work?의 요청·응답·상태 코드 부분 | 5분. 404 응답과 연결 실패의 증거는 어떻게 다른가? 폼 메서드 예·TLS 상세는 제외 |

외부 HTTP 과제의 사이트를 호출하거나 브라우저 설정을 바꾸는 것은 이번 필수 과제가 아니다. 우리 실습은 curl의 HTTP/1.1과 Linux lo를 사용하므로 원문에 있는 브라우저 캐시·VPN·QUIC 관련 준비를 그대로 적용하지 않는다. 메시지를 관찰하는 방법을 읽고 자체 서버에 적용한다.

## 선택 읽기

[CCNA 연계 연습](CCNA_PRACTICE.md)에 공개 샘플의 문항 위치와 기출·연습 사이트별 채택 판단을 정리했다. 외부 문항은 원문 링크에서 풀며, 아래 저작권 안내의 자체 작성 범위는 로컬 문항·설명에 해당한다.

| 자료 | 범위 | 예상 시간·용도 |
| --- | --- | --- |
| [Network Engineer Roadmap](https://roadmap.sh/network-engineer) | 1주차 용어 11개의 참고 글은 [대응표](ARTICLE_LESSON.md#term과-article-대응표) 참고 | 선택 원문은 막힌 개념에 해당하는 부분만 읽기 |
| [Kurose·Ross HTTP v9.0 PDF](https://www-net.cs.umass.edu/wireshark-labs/Wireshark_HTTP_v9.0.pdf) | 1절 The Basic HTTP GET/response interaction, 인쇄 페이지 2~3 | 선택 5분. 요청·응답의 버전·상태 찾기 |
| [Wireshark Follow Stream](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvFollowStreamSection.html) | 7.2 도입과 TCP Stream 화면 설명 | 선택 5분. 같은 흐름의 양방향 메시지 읽기 |
| [Kurose·Ross Getting Started v9.0](https://www-net.cs.umass.edu/wireshark-labs/Wireshark_Intro_v9.0.pdf) | 인쇄 페이지 5~6의 패킷 목록·상세·바이트·필터 설명 | 10분. Wireshark가 처음일 때 화면 읽기 |
| [curl 매뉴얼](https://curl.se/docs/manpage.html) | --verbose, --noproxy, --http1.1, --max-time, Exit codes | 10분. 실습 옵션·상태와 종료 코드 구별 |
| [Python http.server](https://docs.python.org/3/library/http.server.html) | BaseHTTPRequestHandler, protocol_version, send_response, send_header | 10분. 키트 서버의 요청 처리·응답 구성 확인 |
| [Node TypeScript](https://nodejs.org/api/typescript.html) | Type stripping | 5분. 선택 Node 경로. 버전 조건은 실행 전에 확인 |

## 진행자 검증용

- [RFC 9110 §15.3.1, §15.5.5](https://www.rfc-editor.org/rfc/rfc9110.html): 200·404 의미 확인. 일반적인 404 의미와 자체 서버의 단순한 경로 분기를 구분한다. 5분.
- [tcpdump 공식 매뉴얼 원본](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/tcpdump.1.in): -i, -nn, -s, -w 및 종료·필터 동작 확인. 10분. 공식 웹 매뉴얼은 robots 제한으로 본문을 받지 못해 공식 저장소의 원문을 확인했다. 설치 버전의 `man tcpdump`와 실행 권한은 별도 확인한다.
- [Wireshark Flow Graph](https://www.wireshark.org/docs/wsug_html_chunked/ChStatFlowGraph.html): 방향·시간에 따른 흐름 보기. 5분.
- [전체 참고자료 안내](../REFERENCE_GUIDE.md): 16주 자료와 주차별 역할.

## 확인 범위와 저작권

공식 문서와 참고 글의 읽을 범위를 아래 교재에 연결한다. 본문을 확인하지 못한 자료와 대체 자료는 [원문 대응표](ARTICLE_LESSON.md#term과-article-대응표)에 구분했다. 외부 원문은 링크로 안내하며 본문·해답을 길게 복제하지 않는다.

Kurose·Ross Wireshark Labs © 2005–2025 J.F. Kurose, K.W. Ross. [저자 안내](https://gaia.cs.umass.edu/kurose_ross/wireshark.php)에 따라 수업에서 출처를 밝힌다. 원문 각색본을 웹에 게시한다면 원저작권·각색 사실 표시가 필요하다. 이 묶음의 코드·그림·질문·해설은 자체 작성이고 외부 강사용 해답을 사용하지 않았다. 제공 pcap은 기존 자체 Windows 개발 캡처다.

## 핵심 정리와 개발 질문의 근거

[핵심 정리](ESSENTIALS.md)는 기존 교재와 공식 원문을 연결한 자체 설명이며 개발 사례·해설은 스터디 자체 작성이다. [공개 저장소·공식 문서 선정 기록](../INTERVIEW_REFERENCES.md)에 읽은 절·채택 범위·보류 이유를 정리했다. 회사별 실제 면접 출제·빈도는 확인하지 않았다.
