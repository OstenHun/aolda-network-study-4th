# 6주차 · 공식 출처와 읽기 범위

요약: HTTP·TLS·SSH의 공식 근거와 함께 읽을 짧은 범위를 구분한다. 원문 전체 필독을 요구하지 않으며 교재의 계산·흐름·문항은 자체 자료다. 도구 명령은 실제 버전과 조건을 함께 확인한다.

## 참가자가 함께 읽을 범위

| 우선순위 | 공식 자료·지정 범위 | 읽는 목적·돌아갈 교재 |
| --- | --- | --- |
| 중심 | [curl SSL Certificates](https://curl.se/docs/sslcerts.html)의 Verification, [RFC 9525 §6.3](https://www.rfc-editor.org/rfc/rfc9525.html#section-6.3) | 기본 검증·CA 지정과 이름 비교. 영문이 막히면 [W06-K3](CONCEPTS.md#tls-identity)의 세 조건 표 |
| 선택 보조 | [RFC 9112 §9.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3) 첫 세 문단 | 지속 연결·본문 경계. [RTT 계산](CONCEPTS.md#request-cost)과 실습 ID 비교 |
| 필요할 때 | [RFC 9111 §4.3](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.3) 도입부, [OpenSSH 호스트 키 확인](https://man.openbsd.org/ssh#VERIFYING_HOST_KEYS) | 검증자·304, 호스트 신뢰. 캐시 흐름·SSH 제공 기록으로 돌아가기 |

중심 두 짧은 범위는 공동 탐색 시간에 나눠 읽는다. 선택 문서를 모두 사전 과제로 쌓지 않는다. 문서에서 필요한 문장/필드를 찾은 뒤 한국어 교재와 실제 요청으로 연결하며 읽기 소요 시간은 참가자에 따라 조정한다.

## 기술 주장의 공식 근거

| 자료·확인한 절 | 교재에 채택한 범위 |
| --- | --- |
| [RFC 9110 §6·§13.1.2·§15.4.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-6) | HTTP 메시지 의미·If-None-Match·304, HTTP 사용자 인증과 TLS의 구별 |
| [RFC 9112 §2.1·§6.3·§9.3·§9.5](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3) | HTTP/1.1 메시지 경계·본문·지속 연결·유휴/닫힘 |
| [RFC 9111 §4.3·§5.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.3) | 캐시 재검증·no-cache/no-store·must-revalidate |
| [RFC 8446 §1·§2·§4.1·§5](https://www.rfc-editor.org/rfc/rfc8446.html#section-2) | TLS 1.3의 보호 목표·흐름·ServerHello 뒤 암호화·레코드 |
| [RFC 9525 §1.3·§6](https://www.rfc-editor.org/rfc/rfc9525.html#section-6), [RFC 5280 §6.1](https://www.rfc-editor.org/rfc/rfc5280.html#section-6.1) | SAN/기준 이름과 인증서 경로·기간·용도. RFC 9525는 6125를 대체 |
| [RFC 6066 §3](https://www.rfc-editor.org/rfc/rfc6066.html#section-3) | SNI가 알려 주는 서버 이름과 검증 이름의 역할 구별 |
| [RFC 4251 §1·§4](https://www.rfc-editor.org/rfc/rfc4251.html#section-1), [RFC 4252 §1](https://www.rfc-editor.org/rfc/rfc4252.html#section-1) | SSH 전송·사용자 인증·연결 프로토콜의 분업 |
| [RFC 1122 §4.2.3.6](https://www.rfc-editor.org/rfc/rfc1122.html#page-101), [MDN Request.keepalive](https://developer.mozilla.org/en-US/docs/Web/API/Request/keepalive) | TCP keepalive·fetch keepalive와 HTTP 재사용 구별 |
| [MDN HTTP/1.x 연결 관리](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Connection_management_in_HTTP_1.x) | 지속 연결·파이프라이닝·병렬 연결 설명. 일반 문서이며 모든 로딩의 계산 공식으로 사용하지 않음 |

## 도구와 구현의 공식 근거

| 공식 문서 | 명령·코드에서 확인할 부분 |
| --- | --- |
| [curl manpage](https://curl.se/docs/manpage.html) | --resolve·--cacert·--noproxy·--http1.1·--write-out의 num_connects·시간 제한·오류 코드. 같은 명령 내 연결 재사용 |
| [Python http.server](https://docs.python.org/3.10/library/http.server.html), [socketserver](https://docs.python.org/3.10/library/socketserver.html) | protocol_version·Content-Length·setup의 연결 단위·ThreadingHTTPServer·with 정리. 공개 서비스용 아님 |
| [Python ssl](https://docs.python.org/3.10/library/ssl.html) | SSLContext·load_cert_chain·wrap_socket·ALPN·TLS 최소 버전 |
| [OpenSSL req](https://docs.openssl.org/3.0/man1/openssl-req/), [x509](https://docs.openssl.org/3.0/man1/openssl-x509/), [verify](https://docs.openssl.org/3.0/man1/openssl-verify/) | 테스트 CA·CSR·서명·확장 SAN/용도·기간·verify_hostname. 설정 방법만 제공하고 개인키는 배포하지 않음 |
| [ss](https://man7.org/linux/man-pages/man8/ss.8.html), [tcpdump](https://www.tcpdump.org/manpages/tcpdump.1.html), [Wireshark Decode As](https://www.wireshark.org/docs/wsug_html/#ChAdvDecodeAs) | listener 조회·허가된 루프백 한정 캡처·포트 해석. 캡처는 선택 |

## 자료의 종류와 한계

[roadmap.sh Network Engineer](https://roadmap.sh/network-engineer)는 범위 지도다. [기존 SSH 교재](../ssh-top-down/LESSON.md)·4/5주차의 원리·코드를 선수 자료로 쓴다. RTT 식·가공 HTTP/TLS/SSH 흐름·질문·해설·Python 예제는 스터디 자체 작성이며 공식 기출·외부 서비스 실측이 아니다.

공식 문서는 필요한 절을 참고했고 원문·그림·외부 코드를 길게 복제하지 않았다. RFC의 IETF Trust 안내, 각 문서의 저작권/라이선스를 따른다. 이 페이지는 확인한 절의 채택 범위이며 모든 확장·보안 표준·최신 구현의 전체 감사는 아니다. 확인일: 2026-10-17.
