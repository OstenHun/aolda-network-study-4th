# 6주차 교재 · HTTP·TLS·SSH

요약: HTTP 메시지·연결 재사용·캐시 재검증을 구별하고 RTT 비용을 계산한다. TLS의 보호 범위와 인증서 검증을 읽으며 SSH의 호스트 확인·사용자 인증을 HTTPS와 비교한다.

[개인 공부 정리](README.md#personal-notes)에서는 이 교재의 핵심·혼동 구별을 주요 질문과 내 답에 연결한다. 먼저 설명하고 해설과 비교한 뒤, 확인한 근거와 고친 이해를 기존 개인 노트에 보완한다.

- 선수 개념: [1주차 HTTP 응답](../week-01/ESSENTIALS.md), [4주차 TCP 연결 수립](../week-04/CONCEPTS.md)
- 읽기: HTTP 메시지 → 연결 비용/캐시 → TLS/SSH → 혼동 구별 → 개발 질문 → [분리 해설](ANSWERS.md). [학습 홈](README.md) · [실습](LINUX.md).

## W06-K1 · HTTP 요청과 응답을 연결 위에서 읽기

HTTP 요청은 메서드·대상 경로·헤더·필요한 본문을 담고, 응답은 상태 코드·헤더·필요한 본문으로 표현된다. 1주차의 200·404는 HTTP 응답이고 연결 거부는 그 응답 이전의 실패였다. 여기서는 TCP 위의 HTTP/1.1을 기준으로 연결 수립과 요청·응답을 나누어 본다. HTTPS라면 TLS 과정도 고려해야 한다. [RFC 9110 §6](https://www.rfc-editor.org/rfc/rfc9110.html#section-6).

**기억 문장:** HTTP 요청 하나가 TCP 연결 하나를 항상 뜻하지는 않는다. 이미 열린 연결에서 다음 요청을 보낼 수 있다.

### 메시지의 어느 부분을 읽을까

다음은 작은 HTTP/1.1 설명 예제다. 실제 캡처가 아니며 각 줄 끝은 CRLF다. 빈 줄이 헤더와 본문을 나눈다. TCP의 패킷 경계와 HTTP 메시지 경계는 같지 않다.

```http
GET /resource HTTP/1.1
Host: study.test:8086

HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Length: 24
ETag: "study-v1"

study representation v1
```

요청의 `GET`은 메서드, `/resource`는 요청 대상, `Host`는 서비스의 이름·포트다. 응답의 `200`은 상태 코드다. 위 본문은 마지막 LF를 포함해 UTF-8 24바이트이며 `Content-Length`는 글자 수가 아닌 바이트 수다. 실제 응답에는 Date 등 다른 헤더도 붙는다. 404·401도 HTTP 응답이고 TLS 실패·연결 거부는 이 응답을 받기 전 실패일 수 있다. [RFC 9112 §2.1·§6.3](https://www.rfc-editor.org/rfc/rfc9112.html#section-2.1).

## W06-K2 · 같은 연결로 다음 요청 보내기

**HTTP 지속 연결은 한 연결로 여러 요청과 응답을 주고받는 방식이다.** 경로의 RTT 자체를 짧게 만드는 것과 구별한다. HTTP/1.1은 지속 연결이 기본이지만 서버·클라이언트가 닫거나 유휴 제한에 걸리면 재사용하지 못할 수 있다. [RFC 9112 §9.3·§9.5](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3).

<a id="request-cost"></a>

### 연결 비용과 요청 비용 나누어 계산하기

4주차의 양방향 편도 50ms 모형을 이어 보자. 평문 HTTP 요청을 100ms에 보내면 이 모형에서 150ms에 서버에 도착하고 첫 응답 바이트가 약 200ms에 돌아온다. 그래서 새 연결의 작은 객체 비용을 **연결 준비 1 RTT + 요청/첫 응답 1 RTT**로 나눈다. 전체 본문 완료에는 전송 비용 등이 더해진다. HTTPS는 TCP 수립 뒤 TLS 조건까지 고려해야 한다.

아래 계산은 같은 서버의 작은 객체 N개, 캐시 없음, 병렬 연결 없음, 요청은 응답 뒤 하나씩 시작, HTTP 파이프라이닝·다중화 없음, DNS·TLS·처리·본문 전송·손실 무시를 전제로 한다. 첫 연결도 아직 없는 상태다.

| 방식 | 대기 비용 | N=4, RTT=100ms |
| --- | --- | --- |
| 객체마다 새 TCP 연결 | 2N × RTT | 8 RTT = 800ms |
| 처음 한 번 연결 후 순차 재사용 | (1+N) × RTT | 5 RTT = 500ms |
| 이미 열린 연결을 순차 재사용 | N × RTT | 4 RTT = 400ms |

공식은 이 가정에서 직접 유도한 자체 계산이다. 실측·모든 웹페이지의 로딩 공식이 아니다. HTTP/2 다중화, 브라우저 병렬 연결, TLS, 자원 발견 순서, 서버 처리와 전송량이 바뀌면 별도 시간축을 그린다. HTTP/1.1의 파이프라이닝은 응답 순서를 지키며 HTTP/2 스트림 다중화와 다르다. [MDN 연결 관리](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Connection_management_in_HTTP_1.x).

### 캐시 재검증은 응답 내용을 다시 받을지 묻는다

캐시는 받은 응답을 저장해 재사용한다. 사용할 수 있을 만큼 새 응답(fresh)이면 서버에 가지 않고 쓸 수 있고, 재검증이 필요하면 저장한 응답의 검증자를 보낸다. ETag는 서버가 붙인 표현의 검증자이며 암호화 키나 로그인 토큰이 아니다. 다음은 저장한 본문이 있고 아직 같은 표현이라는 **가공 흐름**이다.

```text
1. GET /resource                 → 200, ETag: "study-v1", 본문 저장
2. GET /resource
   If-None-Match: "study-v1"     → 304 Not Modified, 메시지 본문 없음
3. 캐시는 저장한 본문을 사용하고 응답 메타데이터를 갱신
```

GET의 조건이 맞아 304를 받으면 이 응답에 새 본문은 없다. 변경됐으면 200과 새 표현을 받을 수 있다. 재검증 요청도 네트워크 왕복이 들고 새 연결이나 기존 연결 모두에서 보낼 수 있다. “304이므로 TCP 연결을 안 했다”는 결론은 성립하지 않는다. `Cache-Control: no-cache`는 저장 금지가 아니라 사용 전 검증 요구이며, 저장 금지는 `no-store`다. 실습의 `max-age=0, must-revalidate`는 저장 응답을 다시 쓰기 전 검증하도록 비교하기 위한 설정이다. [RFC 9111 §4.3·§5.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.3), [RFC 9110 §15.4.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.4.5).

<span id="tls-identity"></span>

## W06-K3 · TLS는 내용과 상대 신원을 함께 보호한다

**기억 문장:** TLS의 암호화·무결성·서버 신원 검증과 웹사이트의 사용자 로그인은 서로 다른 확인이다. HTTP를 TLS 위에서 주고받는 것이 HTTPS다. 여기서는 TCP 기반 HTTPS를 읽으며 HTTP/3·QUIC의 전송 구조는 제외한다.

암호화는 중간 관찰자가 내용을 읽기 어렵게 하고, 무결성 보호는 전송 중 변조를 검출한다. 서버 인증은 의도한 상대와 연결했는지 확인한다. 인증서를 받았다는 사실만으로 신원 검증이 끝나지 않는다. [TLS 1.3 RFC 8446 §1·§2](https://www.rfc-editor.org/rfc/rfc8446.html#section-1).

```text
클라이언트가 의도한 URL 이름
          ↓ 이름 비교
서버 인증서의 SAN + 공개키 ← 발급자 서명 ← 신뢰하는 CA
          ↓ 경로·기간·용도 등 검증 + 서버의 키 보유 증명
보호된 HTTP 요청·응답 → 앱이 별도로 사용자 로그인/권한 확인
```

CA는 인증서를 발급·서명하는 인증기관이다. 보통 서버 인증서→중간 CA→클라이언트가 신뢰하는 루트로 경로를 검증한다. 루트는 서버가 보냈기 때문에 신뢰하는 것이 아니다. 실습에서는 직접 확인한 CA 공개 인증서를 `--cacert`로 그 요청에만 지정한다. 시스템 전체 신뢰 저장소에 추가하지 않는다.

| 검증할 조건 | 필요한 이유 | 틀렸을 때의 가설 |
| --- | --- | --- |
| 신뢰 경로·서명·용도 | 신뢰 출발점까지 올바른 발급 경로인지 확인 | 빠진 중간 인증서, 신뢰하지 않은 CA, 서버 인증 용도 불일치 |
| URL 이름과 SAN | 같은 IP에 여러 서비스가 있어도 의도한 상대 확인 | 다른 이름의 인증서, 잘못된 서비스 선택 |
| notBefore·notAfter와 현재 시각 | 인증서가 유효한 기간인지 확인 | 만료, 아직 유효하지 않음, 잘못된 클라이언트 시계 |

SAN(Subject Alternative Name)은 인증서에 적힌 서비스 이름/주소다. DNS 이름은 SAN의 dNSName, IP로 접속하면 SAN의 iPAddress와 대조한다. CN만 보고 이름이 맞다고 판정하지 않는다. 체인·기간·용도 검증과 이름 비교는 함께 필요하다. [RFC 9525 §1.3·§6](https://www.rfc-editor.org/rfc/rfc9525.html#section-6), [RFC 5280 §6.1](https://www.rfc-editor.org/rfc/rfc5280.html#section-6.1).

5주차의 `--resolve`는 연결 주소를 정해도 URL 이름을 유지한다. 이 이름은 TLS의 SNI·검증 기준과 HTTP Host에 쓰인다. SNI는 ClientHello에서 서버에 원하는 이름을 알려 주는 기능이며 인증서 검증의 대체가 아니다. `https://IP`에 `Host` 헤더만 바꿔도 TLS의 기준 이름까지 바뀌지는 않는다. HTTP 헤더는 TLS를 맺은 뒤 보낸다. [RFC 6066 §3](https://www.rfc-editor.org/rfc/rfc6066.html#section-3).

### 암호화되면 무엇을 관찰할까

아래는 **TLS 1.3·ECH 없음·복호화 키 없는 중간 캡처**를 가정한 설명 흐름이다. 실제 측정 trace가 아니다. TLS 버전·기능·관찰 위치를 바꾸면 보이는 필드도 달라진다.

| 단계 | 중간 패킷 관찰 | 연결 당사자 curl/서버 |
| --- | --- | --- |
| TCP SYN/SYN-ACK/ACK | IP·포트·플래그·길이·시점 | 연결 성공/실패 확인 |
| TLS ClientHello/ServerHello | 보통 ClientHello의 SNI·제안 ALPN, ServerHello 등 | 협상한 TLS 버전·암호군 확인 |
| ServerHello 뒤 TLS 1.3 핸드셰이크 | 인증서 등은 암호화돼 평문으로 못 읽음 | 서버 인증서·검증 결과 확인 |
| HTTP 요청·응답 | TLS 레코드 길이·시점, 메서드/경로/본문은 못 읽음 | 복호화한 메서드·상태·헤더·본문 확인 |

평문 HTTP라면 스트림 재조립으로 메시지를 읽을 수 있다. HTTPS의 200을 curl에서 읽어도 중간 캡처에 200 평문이 있어야 하는 것은 아니다. TLS 1.2의 인증서 노출과 TLS 1.3을 혼용하지 않는다. 암호화가 IP·트래픽 양·시점까지 전부 숨기지는 않는다. [RFC 8446 §2·§4.1·§5](https://www.rfc-editor.org/rfc/rfc8446.html#section-2). 직접 캡처는 [실습의 선택 관찰](LINUX.md#packet-view)에서 다룬다.

### 서버 인증과 사용자 인증

일반적인 HTTPS의 인증서는 서버를 확인한다. 사용자는 그 뒤 HTTP 로그인·쿠키/토큰 등 앱의 방식으로 확인할 수 있다. 서버 인증이 성공해도 HTTP 401·403이 나올 수 있고, 인증서가 올바르다고 사이트 내용 전체가 신뢰할 만하다는 뜻도 아니다. 클라이언트 인증서를 쓰는 mTLS는 별도 구성의 선택 심화다.

<span id="ssh"></span>

## SSH · 원격 셸에서 두 확인을 나누기

SSH는 암호화된 통로에서 원격 로그인·명령 실행 등을 제공하는 별도 프로토콜이다. HTTPS처럼 HTTP를 TLS로 감싸는 방식이 아니다. 기본 포트 22와 HTTPS의 443은 관례이며 바꿀 수 있다. SSH 전송 계층에서 서버 호스트 키를 확인한 뒤 사용자 인증을 하고, 그 위에 셸 등의 채널을 연다. [RFC 4251 §1·§4](https://www.rfc-editor.org/rfc/rfc4251.html#section-1), [RFC 4252 §1](https://www.rfc-editor.org/rfc/rfc4252.html#section-1).

다음은 실접속 출력이 아닌 **생략·가공한 안내 순서**다. 실제 지문·계정·주소는 보관하지 않았다.

```text
호스트 키 지문: SHA256:<서버 지문>
이 서버를 신뢰할지 확인 → 별도 신뢰 경로의 지문과 대조
사용자 인증 요청       → 허가된 비밀번호/공개키 등 사용
인증 성공 뒤 원격 셸   → hostname, pwd 등으로 실행 위치 확인
```

호스트 키는 서버의 신원, 사용자 비밀번호/키는 사용자의 신원을 확인한다. 처음 나타난 지문은 신뢰할 별도 경로의 값과 비교하고, 기존 키와 달라지면 재설치/키 교체 여부를 관리자에게 확인한다. 경고를 없애기 위해 `StrictHostKeyChecking=no`를 쓰거나 known_hosts 항목을 바로 지우지 않는다. SSH의 known_hosts 신뢰와 HTTPS의 CA 인증서 경로를 같은 구조라고 설명하지 않는다. [OpenSSH ssh의 VERIFYING HOST KEYS](https://man.openbsd.org/ssh#VERIFYING_HOST_KEYS), [기존 SSH 교재](../ssh-top-down/LESSON.md).

## 헷갈리는 구별 두 가지

연결을 다시 쓰는 것, 여러 요청을 겹쳐 전송하는 것, 로그인 상태를 기억하는 것은 각각 다른 기능이다.

| 혼동 | 구별과 반례 |
| --- | --- |
| 지속 연결이면 캐시·동시 요청·사용자 상태까지 유지한다 | 재사용은 연결 비용, 캐시는 응답 사용, 다중화는 스트림 전송, 로그인은 앱 상태의 문제다. 304도 새 연결에서 받을 수 있다 |
| TLS 인증이 성공하면 사용자 로그인·SSH 접속도 확인했다 | 서버 인증서와 웹 사용자 인증, SSH 호스트 키/사용자 인증은 별개다. HTTPS 401은 TLS 성공 뒤에도 가능하다 |

`keepalive`라는 이름도 문맥을 읽는다. HTTP keep-alive는 요청 사이 재사용, TCP keepalive는 유휴 연결의 반응 확인용 probe, fetch keepalive는 문서를 떠난 뒤에도 요청을 이어갈 수 있게 하는 옵션이다. [RFC 1122 §4.2.3.6](https://www.rfc-editor.org/rfc/rfc1122.html#page-101), [MDN Request.keepalive](https://developer.mozilla.org/en-US/docs/Web/API/Request/keepalive).

## 개발 상황으로 설명하기

**자체 작성 사례:** 같은 서버의 상품·리뷰 API가 각각 상품 ID만 필요하다. 현재 코드는 상품 응답이 끝난 뒤 리뷰 요청을 시작한다. 이 사례는 실제 서비스 측정 결과가 아니다.

1. **W06-D1 · 설명:** 연결이 재사용돼도 왜 두 번째 요청이 기다릴까?
2. **W06-D2 · 조건 변경:** 두 요청을 함께 시작하면 항상 전체 시간이 절반이 될까?
3. **W06-D3 · 진단:** 브라우저 Network에서 무엇을 확인해야 개선을 판단할까?

답을 먼저 설명한 뒤 [분리 해설](ANSWERS.md)을 읽는다. 기존 공통 질문의 추가 질문으로 사용하며 별도 활동지를 추가하지 않는다.

## 연결 재사용을 비교할 때

기존 [1주차 키트](../../labs/week-01/README.md)는 매 요청 연결을 닫는다. 반복 호출만으로 지속 연결을 관찰했다고 기록하지 않는다. [6주차 실습 A2](LINUX.md#reuse-lab)는 HTTP/1.1·본문 길이·같은 프로세스의 curl·서버 연결 ID를 맞춰 비교한다. 계산과 로컬 실행은 실제 브라우저 성능의 측정 결과가 아니다.

다음 복습에서는 “TLS가 성공했는데 HTTP가 실패하면 어느 단계부터 볼까?”를 묻는다. 7주차의 왕복 경로와 8주차의 DNS→TCP→TLS→HTTP 전체 흐름으로 이어 간다. HTTP/2·3·WebSocket·mTLS 상세는 후속 범위다. [전체 개념 색인](../CONCEPT_INDEX.md) · [공식 출처](SOURCES.md).
