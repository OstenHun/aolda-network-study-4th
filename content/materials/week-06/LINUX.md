# 6주차 · Linux 실습과 코드 읽기

요약: HTTP 메시지·재사용·조건부 요청을 비교하고 준비된 TLS 서버에 정상 이름·잘못된 이름·복구 요청을 직접 보낸다. 클라이언트 결과와 패킷의 관찰 범위를 나누고 제공 Python 코드의 흐름을 읽는다.

## 실행 위치와 준비

기존 Linux VM 한 대 안에서 셸 두 개를 사용한다. Python 3.10 이상·curl·ss가 필요하며 TLS 준비자는 OpenSSL 3도 사용한다. `python3 --version`, `curl --version`으로 버전과 HTTPS 지원을 확인한다. 주소·경로·방화벽·SSH 인증 설정은 바꾸지 않는다. 아래 모든 서버는 `127.0.0.1`에만 대기한다. 내 PC에서 명령을 실행하면 그 PC의 루프백이므로 VM 안의 셸인지 먼저 확인한다.

제공 <a download href="../../labs/week-06/http_server.py">http_server.py 내려받기</a>를 본인 실습 폴더에 둔다. 아래 명령은 그 폴더에서 실행한다. `8086`·`8443`이 이미 사용 중이면 소유자를 확인하고 다른 비특권 포트를 골라 서버·URL·`--resolve`의 포트를 모두 맞춘다. 남의 프로세스는 종료하지 않는다.

필수 묶음은 A의 메시지/계산/제공 분석과 B의 TLS 직접 요청이다. A2 재사용 실행과 패킷 캡처는 선택 비교다. TLS 초기 구축은 [진행자 준비](FACILITATOR.md#tls-setup)로 한 번 하고 참가자는 준비된 서버를 사용한다. 같은 VM 안의 참가자만 요청할 수 있으며 외부 바인딩으로 확대하지 않는다.

## A1 · HTTP 메시지와 계산 읽기

셸 1에서 서버를 켠다. 이 서버는 학습용이며 공개 서비스에 사용하지 않는다.

```sh
python3 http_server.py --port 8086
```

셸 2에서 프록시를 거치지 않는 본인 루프백에 요청한다. `-i`는 응답 헤더를 본문과 함께 출력한다. `-v`는 요청/연결 진단을 stderr에 표시한다. 이 예제에는 인증 정보가 없으며 실제 로그인 요청의 진단 출력을 공개하지 않는다.

```sh
curl --noproxy '*' --http1.1 --connect-timeout 3 --max-time 8 -iv http://127.0.0.1:8086/resource
```

GET·경로·Host, 응답의 HTTP/1.1·200·Content-Length·ETag를 짚는다. 서버의 `connection=... path=... status=200`과 대응한다. 메시지의 빈 줄과 본문 길이를 TCP 패킷 하나와 혼동하지 않는다. [교재 RTT 표](CONCEPTS.md#request-cost)의 가정으로 RTT=100ms·객체 4개를 계산한 뒤 RTT=80ms·객체 3개로 바꾼다. 이 루프백의 실행 시간에 WAN RTT 계산값이 나와야 하는 것은 아니다.

<span id="reuse-lab"></span>

## A2 · 실제 새 연결과 재사용 비교

하나의 curl 명령에 같은 origin(스킴·호스트·포트)의 URL 두 개를 준다. 응답을 순서대로 읽은 뒤 다음 요청을 보내므로 파이프라이닝/다중화 실험이 아니다.

```sh
curl --noproxy '*' --http1.1 --connect-timeout 3 --max-time 8 -i -w '\nnew_connections=%{num_connects}\n' http://127.0.0.1:8086/resource http://127.0.0.1:8086/resource
```

정상 기준은 두 응답의 **X-Connection-ID가 같음**, 서버 로그의 같은 ID, `new_connections`가 첫 전송 1·둘째 0인 것이다. curl은 전송마다 통계를 찍는다. 시간만으로 재사용을 확정하지 않는다. 서버·클라이언트가 닫거나 유휴 제한을 넘기면 새 연결이 필요하다.

조건 하나를 바꿔 첫 URL만 `/close`로 요청한다. 이 경로는 같은 표현을 보내되 연결을 닫는다.

```sh
curl --noproxy '*' --http1.1 --connect-timeout 3 --max-time 8 -i -w '\nnew_connections=%{num_connects}\n' http://127.0.0.1:8086/close http://127.0.0.1:8086/resource
```

이번에는 연결 ID가 다르고 두 전송 모두 새 연결 1이어야 한다. 원래 두 `/resource` 명령으로 돌아가 같은 ID/1·0을 재확인한다. 별도 curl 프로세스를 두 번 띄우면 프로세스 사이 연결 풀이 공유되지 않아 비교 조건이 달라진다. 기존 1·5주차 서버를 이 실험의 서버로 바꾸어 사용하지 않는다.

## A3 · 조건부 요청은 연결과 별개다

다음은 저장한 본문과 ETag가 있다고 가정해 **검증자만 수동으로 보내는 요청**이다. curl이 이 명령만으로 브라우저 캐시 전체를 구현하거나 자동으로 저장 본문을 출력하는 것은 아니다.

```sh
curl --noproxy '*' --http1.1 --max-time 8 -i -H 'If-None-Match: "study-v1"' http://127.0.0.1:8086/resource
```

일치하면 304·ETag·본문 없음이 기준이다. 별도 curl 프로세스이므로 이 304를 받으러 새 연결을 맺는다. 검증자를 `"other"`로 바꾸면 200과 본문을 받고, 원래 검증자로 복구하면 304다. 실행이 막혀도 [교재의 가공 흐름](CONCEPTS.md#캐시-재검증은-응답-내용을-다시-받을지-묻는다)에서 요청/304·저장 본문을 분석할 수 있다. 이 분석을 직접 실행으로 기록하지 않는다.

<span id="tls-lab"></span>

## B · TLS 신원 정상→이름 변경→복구

진행자는 같은 Linux 안에 `study.test` SAN 인증서로 대기하는 8443 TLS 서버를 준비한다. 참가자는 별도 신뢰 경로로 확인한 CA **공개** 인증서 `ca.pem`만 실습 폴더에 둔다. 서버/CA 개인키를 참가자에게 전달하지 않는다. `study.test`와 `wrong.test`는 설명용 테스트 이름이며 DNS/hosts 파일에 등록할 필요가 없다.

정상 기준부터 확인한다. `--resolve`는 DNS를 우회해 주소를 정하지만 URL 이름·SNI·검증 이름을 유지한다. `--cacert`는 이 요청에 쓸 신뢰 CA를 지정한다. 시스템 신뢰 설정을 바꾸지 않는다.

```sh
curl --noproxy '*' --http1.1 --connect-timeout 3 --max-time 8 --cacert ca.pem --resolve study.test:8443:127.0.0.1 -iv https://study.test:8443/resource
printf 'exit=%s\n' "$?"
```

정상은 인증서 검증을 켠 채 종료 코드 0·HTTP 200·서버 로그가 나오는 것이다. curl의 TLS 백엔드에 따라 인증서/진단 문구는 다르다. 준비자는 공개 인증서에서 SAN·발급자·기간을 확인해 함께 보여 준다.

```sh
openssl x509 -in server.pem -noout -issuer -subject -dates -ext subjectAltName
openssl verify -CAfile ca.pem -verify_hostname study.test server.pem
```

참가자는 이 공개 정보와 URL 이름·CA 신뢰 근거를 대조한다. 파일 정보 조회만으로 실제 연결을 검증했다고 보지 않는다. 직접 curl 결과와 함께 읽는다.

이제 IP·포트·CA·경로는 유지하고 URL 이름/해당 매핑만 바꾼다.

```sh
curl --noproxy '*' --http1.1 --connect-timeout 3 --max-time 8 --cacert ca.pem --resolve wrong.test:8443:127.0.0.1 -iv https://wrong.test:8443/resource
printf 'exit=%s\n' "$?"
```

예상은 이름 불일치로 인증서 검증 실패(보통 curl 60), HTTP 상태/본문 미수신, 해당 요청의 HTTP 서버 로그 없음이다. TLS 연결 시도 자체는 있었을 수 있다. 마지막에는 **첫 정상 명령을 그대로 다시 실행**해 0·200·로그를 확인한다. `-k`/`--insecure`를 넣거나 CA를 시스템에 추가하는 방법을 복구로 쓰지 않는다.

이 실험은 이름만 틀린 조건이다. 만료·신뢰 CA 누락을 실제 실행했다고 확대하지 않는다. 해당 오류는 신뢰 경로·시간·기간을 나눠 조사한다. 정상 이름도 처음부터 실패하면 아래 오류 표부터 확인한다.

| 결과 | 다음 확인 | 정상 복귀 |
| --- | --- | --- |
| 연결 거부·시간 초과 | 서버 실행·같은 VM·포트·루프백 대기, `ss -ltn` | 준비한 서버/포트로 재요청 |
| ca.pem 읽기 오류 | 현재 폴더·공개 CA 파일·파일 권한 | 올바른 공개 파일 경로 사용 |
| 정상 이름도 인증서 오류 | SAN·CA·서버 인증서 짝·기간·현재 시각 | 준비자가 인증서를 바로잡고 검증 켜서 재요청 |
| HTTP 404 | TLS 이후 요청 경로 | `/resource`로 복구 |
| 재사용 ID가 다름 | 같은 curl 프로세스·URL origin·`/close`·5초 유휴 제한 | A2 정상 명령 반복 |

<span id="packet-view"></span>

## 선택 · 패킷과 클라이언트 결과 대조

캡처 권한이 있을 때 본인 루프백·실습 포트만 대상으로 별도 셸에서 실행한다. 자신의 서버 외 트래픽은 수집하지 않는다. 권한이 없으면 [교재의 TLS 1.3 관찰 표](CONCEPTS.md#암호화되면-무엇을-관찰할까)를 제공 분석한다.

```sh
sudo tcpdump -i lo -nn -s 0 -w week06-loopback.pcap 'tcp port 8086 or tcp port 8443'
```

A1과 B 정상 요청 후 캡처 셸에서 Ctrl+C로 종료한다. Wireshark에서 `http`·`tls`·`tcp.port == 8443`를 나누어 본다. 8443이 TLS로 해석되지 않으면 해당 TCP 포트를 **Decode As → TLS**로 지정한다. 평문 HTTP의 요청/응답과 TLS 레코드를 대조한다. TLS 1.3·ECH 없음·복호화 키 없음이면 ClientHello SNI는 보일 수 있지만 인증서와 HTTP 내용은 평문으로 읽을 수 없다. 실제 협상 버전·관찰 위치를 적고 보이지 않는 필드를 억지로 채우지 않는다. 개인키·세션 키 로그를 공유하지 않는다.

## 코드 읽기 · 입력에서 응답과 정리까지

제공 Python은 참가자가 읽을 코드이며 직접 작성 시험은 아니다. 처음에는 `main()`→`StudyServer.get_request()`→`StudyHandler.setup()`→`do_GET()` 순서로 읽는다. HTTP/TLS 자체를 새로 구현하지 않고 표준 라이브러리를 쓴다.

| 단계 | 코드/문법 | 이유와 출력 |
| --- | --- | --- |
| 입력 | argparse·정수 범위·cert/key 짝 검사 | 잘못된 포트·파일 조건은 서버 실행 전에 거절 |
| TLS 준비 | `SSLContext`·`load_cert_chain` | 인증서와 키를 읽고 HTTP/1.1 ALPN 설정, 평문 모드에는 없음 |
| 대기 | `with StudyServer(...)` | 루프백에만 바인딩, 블록 종료 때 listener 정리 |
| 연결 | `get_request`, `settimeout(5)`·조건부 TLS wrap | 받아들인 연결에 시간 제한, TLS 실패는 HTTP 요청으로 처리하지 않음 |
| 식별 | `setup`·`next(itertools.count(...))` | 소켓 번호를 재사용해도 새 연결은 새 ID, 한 연결의 여러 요청은 같은 ID |
| 판단 | `do_GET`, `self.path`, `self.headers.get` | 경로·ETag 비교, `/close`는 연결 종료 조건 |
| 응답 | `b"..."`·`len(body)`·헤더 후 빈 줄 | 바이트 길이를 보내 재사용의 본문 경계 유지. 304에는 본문을 보내지 않음 |
| 종료 | Ctrl+C·KeyboardInterrupt·`with` | listener 닫기, 스레드 연결은 프로세스 종료 때 끝남 |

`self`는 현재 객체, `super()`는 부모 클래스의 동작 호출이다. `try/except`는 파일·대기·TLS 오류를 다루고 `if __name__ == "__main__"`는 직접 실행 때 main을 부른다. ThreadingHTTPServer는 여러 연결을 처리할 수 있지만 이 실험의 한 curl은 요청을 순서대로 보낸다. 이 코드는 고정 GET 표현·정확히 같은 ETag 하나만 비교한다. 완전한 캐시·인증·HTTP 서버를 구현한 것이 아니다.

자기 말로 설명해 보자. 왜 HTTP/1.1과 Content-Length를 함께 설정할까? 304에 본문을 보내면 왜 문제일까? setup이 요청마다 호출된다면 연결 ID 비교가 왜 잘못될까? [Python 공식 근거](SOURCES.md#도구와-구현의-공식-근거)에서 동작을 확인한다.

## SSH와 정리

SSH는 [제공 기록](CONCEPTS.md#ssh)으로 두 인증 단계를 설명한다. 새 접속은 허가된 경로가 이미 있을 때만 선택하며 기존 [SSH 교재](../ssh-top-down/LESSON.md)의 호스트 확인을 따른다. 인증 방식·서버 키·관리 경로를 바꾸지 않는다. 비밀번호·개인키·인증 토큰을 기록하지 않는다.

HTTP·TLS 서버 각각의 셸에서 Ctrl+C로 종료하고 `Stopped; listener closed`를 확인한다. `ss -ltn '( sport = :8086 or sport = :8443 )'`에 본인 listener가 없는지 확인한다. 임시 인증서는 준비자가 자기 전용 실습 폴더에서 정리한다. 원본 코드·기존 SSH 설정은 지우지 않는다. 명령·출력·필요 캡처를 개인 파일에 한 번 보관하고 직접 수행·제공 분석·미실행을 구별한다.
