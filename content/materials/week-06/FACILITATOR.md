# 6주차 · 진행자 안내

요약: HTTP 분석과 TLS 직접 요청 두 묶음을 기존 시간에 배치한다. 루프백 TLS 대상·공개 CA를 준비하고 정상·잘못된 이름·복구를 재현하며 SSH 설명과 선택 구축·캡처를 구별한다.

## 시작 전 리허설

[학습 홈](README.md)→[공동 질문](WORKSHEET.md)→[교재](CONCEPTS.md)→[실습](LINUX.md)을 따라간다. 기존 Linux 셸 두 개, Python 3.10+·curl HTTPS·ss, 사용하지 않는 비특권 포트, 파일 전달 경로를 확인한다. TLS 서버를 처음부터 만드는 일은 준비자가 맡고 참가자에게 필수 구축 과제로 추가하지 않는다. 같은 VM에서 제공 서버를 켜며 외부 노출·공용망 변경·SSH 인증 변경은 하지 않는다.

<span id="tls-setup"></span>

## TLS 대상 준비 · 진행자 또는 선택 직접 구축

OpenSSL 3을 사용할 수 있는 허가된 Linux 안에서 실행한다. `umask`는 새 개인키를 본인만 읽도록 하고 `mktemp -d`는 충돌하지 않는 임시 폴더를 만든다. 아래 두 개인키는 실습 중 이 폴더에만 생성하며 공개 저장소·다운로드·공유 기록에 넣지 않는다. 개인키를 제외한 **코드와 설정 방법**만 공개 자료다. 시스템 CA 저장소를 변경하지 않는다.

```sh
umask 077
TLS_LAB_DIR=$(mktemp -d)
cd "$TLS_LAB_DIR"
openssl req -x509 -newkey rsa:2048 -noenc -keyout ca-key.pem -out ca.pem -days 2 -subj '/CN=Study Lab CA' -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign'
openssl req -new -newkey rsa:2048 -noenc -keyout server-key.pem -out server.csr -subj '/CN=study.test'
printf '%s\n' 'subjectAltName=DNS:study.test' 'basicConstraints=critical,CA:FALSE' 'keyUsage=critical,digitalSignature,keyEncipherment' 'extendedKeyUsage=serverAuth' > server.ext
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server.pem -days 1 -extfile server.ext
openssl verify -CAfile ca.pem -verify_hostname study.test server.pem
openssl x509 -in server.pem -noout -issuer -subject -dates -ext subjectAltName
```

각 명령의 종료 코드와 오류를 확인하고 실패하면 다음 단계로 넘기지 않는다. 인증서는 짧은 기간만 유효하다. 사용할 날에 다시 생성하고 현재 시각·기간·SAN을 확인한다. 만든 `ca.pem`과 `server.pem`은 공개 인증서이며 참가자가 신뢰 경로와 이름·기간을 확인하는 데 쓴다. CA 개인키와 서버 개인키는 공유하지 않는다. 본인 실습 폴더의 제공 `http_server.py`를 이 임시 폴더로 복사해 실행한다.

```sh
python3 http_server.py --port 8443 --cert server.pem --key server-key.pem
```

서버 셸은 그대로 두고 같은 VM의 다른 셸에서 [B의 세 요청](LINUX.md#tls-lab)을 실행한다. 참가자 셸의 `ca.pem`은 위에서 만든 같은 CA여야 한다. 정상 이름 200→잘못된 이름 검증 실패/HTTP 미수신→정상 이름 200이 준비 기준이다. 이 CA는 학습용이고 외부 서버나 시스템 전체를 신뢰하도록 등록하지 않는다.

TLS 구축이 막히면 허가된 별도 테스트 서버에서 동일한 정상/잘못된 이름 조건·CA를 제공할 수 있는지 확인한다. 검증을 끄거나 불특정 외부 서버의 인증서를 바꿔 대체하지 않는다. 대상이 없으면 교재의 제공 예제로 설명하고 참가자 직접 요청은 미완료로 남겨 보충한다.

종료는 서버 셸의 Ctrl+C 후 해당 listener 부재를 확인한다. 인증서를 정리할 때는 임시 폴더가 본인이 이번에 생성한 경로인지 `pwd`와 목록으로 확인하고, 해당 파일만 삭제한다. 다른 실습·개인 키·SSH 설정을 지우지 않는다.

## 함께 읽는 공식 절

| 역할 | 지정 범위 | 함께 찾을 것 |
| --- | --- | --- |
| 중심 공동 읽기 | curl SSL Certificates의 Verification, RFC 9525 §6.3 | 검증 기본값·요청별 CA·URL 이름과 SAN |
| 재사용 보조 | RFC 9112 §9.3 첫 세 문단 | 지속 연결·본문 끝까지 읽기·닫힘 조건 |
| 캐시/SSH 보충 | RFC 9111 §4.3 첫 흐름, OpenSSH VERIFYING HOST KEYS | 검증자·304, 서버 지문과 사용자 인증의 차이 |

[출처](SOURCES.md)의 나머지 문서는 기술 근거·막힐 때 참조다. 전체 RFC 필독을 요구하지 않는다. 영문이 막히면 교재의 신원 표/시간축과 용어로 돌아간다. 문항·trace·계산은 자체 자료이며 기업 기출로 부르지 않는다.

## 사전 공동학습 60분 제안

| 시간 | 활동 |
| --- | --- |
| 0~5분 | 4주 TCP/처리·5주 DNS/이름 복습, 중심 질문 |
| 5~25분 | TLS 검증 지정 절·교재를 함께 찾고 이름/신뢰/기간 구별 |
| 25~40분 | 한 명 설명·조건 변경, HTTP 메시지·RTT 작은 계산 |
| 40~55분 | 캐시 제공 흐름·TLS 관찰 표·SSH 제공 기록 분석 |
| 55~60분 | W06-K1~K3을 다시 설명하고 실행 환경 확인 |

## 실습 60분 제안

| 시간 | 활동 |
| --- | --- |
| 0~5분 | 준비된 TLS 서버·CA·정상/비교 조건 확인 |
| 5~30분 | 각자 B의 정상→이름 변경→복구·클라이언트/서버 근거 |
| 30~45분 | A1 메시지·RTT와 캐시 분석, 가능하면 A2 재사용 비교 |
| 45~55분 | 짝의 출력 설명·복습에서 막힌 질문 선택 |
| 55~60분 | 서버/선택 캡처 종료·listener 확인·개인 근거 보관 |

초과하면 선택 TLS 초기 구축·패킷 캡처·A2 실행·새 SSH 접속·보조 질문을 먼저 줄인다. 필수 HTTP 분석·TLS 직접 요청은 나눠 보충한다. 참가자별 TLS 직접 수행과 제공 분석을 구별하고, 한 명의 시연을 전원 완료로 쓰지 않는다. 고정 팀 기록·개인 마무리·추가 발표를 요구하지 않는다. 실제 초보자 소요 시간은 진행하며 재점검한다.

## 설명을 과장하지 않기

루프백 시간으로 WAN 성능을 검증하지 않는다. X-Connection-ID·curl 새 연결 수를 함께 읽고, 304를 연결 재사용 증거로 쓰지 않는다. TLS 버전·복호화 여부를 적고 TLS 1.3의 인증서를 중간 캡처에서 평문으로 찾아야 한다고 안내하지 않는다. 서버 인증과 HTTP 사용자 인증을 나누며 `-k`를 복구로 제안하지 않는다. SSH 키 경고를 지우는 실습도 하지 않는다.

다음 주에는 “이름·인증서가 맞는데 연결조차 못 하면 왕복 경로에서 무엇을 볼까?”를 기존 복습 시간에 묻는다. 8주차 전체 통신 흐름과 13주차 서비스 연결로 근거를 이어간다. 이번 자료나 TLS 한 실험을 O02 전체 완료로 표시하지 않는다.
