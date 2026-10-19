# 5주차 · 함께 찾고 설명할 질문

요약: 이름 해석과 실제 서비스 요청을 서로 다른 증거로 판단한다. 공식 절에서 역할과 조건을 찾고 자기 말로 설명한 뒤 캐시·Host·주소 설정 중 한 조건을 바꾸어 확인한다.

## 중심 질문 · IP를 찾았는데 왜 요청은 실패할까?

DNS 질의에서 주소를 받았는데 웹 요청은 시간 초과가 났다. **DNS 응답, TCP 연결, HTTP 응답 중 무엇을 실제로 확인한 것일까?** 1주차 404·연결 실패와 4주차 전달·처리를 다시 사용한다. 답을 먼저 열지 않고 다음 순서로 찾아본다.

1. [RFC 1034 §4.3.1](https://www.rfc-editor.org/rfc/rfc1034.html#section-4.3.1)에서 재귀 요청과 서버 응답을, [curl의 --resolve](https://curl.se/docs/manpage.html#--resolve)에서 이름을 유지하며 목적 주소만 지정하는 방법을 찾는다.
2. [교재의 DNS 역할](CONCEPTS.md#dns-roles)과 [이름 해석·요청 구별](CONCEPTS.md#distinctions)을 함께 읽고, dig와 curl이 각각 무엇을 보내는지 그린다.
3. 각자 근거와 아직 모르는 부분을 설명한다. “주소는 그대로 두고 URL의 이름만 IP로 바꾸면 같은 요청일까?”라고 묻는다.
4. [실습 A](LINUX.md#experiment-a)의 실제 출력과 비교한 뒤 [중심 질문 해설](ANSWERS.md#inquiry)을 읽는다. HTTPS 인증서 세부는 다음 주에 이어간다.

## 선택 보조 질문 · 바꾼 DNS가 모두에게 바로 보일까?

권한 서버에서 A 주소를 바꿨다. 직전에 받은 응답의 TTL이 300초였고 120초가 지났다. 재귀 리졸버가 예전 주소를 돌려줘도 모순일까? [RFC 1034 §3.6](https://www.rfc-editor.org/rfc/rfc1034.html#section-3.6)과 [교재의 두 응답](CONCEPTS.md#cache)을 읽는다. 설명 뒤 “캐시가 없는 다른 리졸버라면?”으로 조건을 바꾼다. 해설은 [Q3](ANSWERS.md#q3)에서 비교한다.

## 선택 보조 질문 · IP는 있는데 DNS만 잘못 받았다면?

주소·마스크·게이트웨이는 그대로이고 DHCP의 DNS 옵션만 다른 주소가 되었다. 어떤 조회와 요청을 비교하면 될까? [RFC 2131 §3.1](https://www.rfc-editor.org/rfc/rfc2131.html#section-3.1), [RFC 2132 §3.8](https://www.rfc-editor.org/rfc/rfc2132.html#section-3.8), [제공 trace](CONCEPTS.md#dhcp-trace)를 읽는다. 실제 VM 설정은 바꾸지 않고 옵션 필드 하나가 달라진 경우를 분석한다. 답은 [Q6·개발 질문](ANSWERS.md#q6)에 있다.

## 함께 확인하기

각자 출력의 필드 하나를 짚고 조건 변경을 짧게 설명한다. 모임에서는 이미 시도한 근거와 해석을 비교한다. 검색이 막히면 [공식 출처](SOURCES.md)의 지정 절로 바로 돌아간다. 별도 발표 자료나 고정 기록 양식을 작성하지 않는다.
