# 14주차 · 지연 비교와 프록시 전환 직접 실습

요약: 허가된 Linux의 루프백에서 짧은 GET을 제한 반복한다. 서버 대기 한 조건과 두 서버의 분산·제외·복귀·정지·복구를 비교하고, 클라이언트 시간과 식별자·프록시/서버 로그를 같은 요청에 대응한다.

## 실행 위치·준비와 중단 조건

기존 Linux VM 한 대, 같은 계정의 셸 네 개를 사용한다. Python3·curl·ss가 필요하며 관리자 권한이나 보안 그룹 변경은 필요하지 않다. 현재 허가된 셸·도구·미사용 포트를 먼저 확인한다. 접속 미준비면 [제공 사례](../../labs/week-14/observations.txt)를 분석하고 본인 직접 실험은 보충한다. 실제 서버·관리 SSH·공용망은 변경하지 않는다.

아래 파일을 **같은 새 개인 실습 폴더**에 내려받는다. 기존 파일을 덮어쓰지 않는다. 모든 셸은 이 폴더에서 실행한다. 1주차 `server.py`와 13주차의 HTTP 경로·양끝 로그 개념을 재사용하며, 이번에는 식별자·처리 대기·프록시를 더한다. 13주 원격 서버를 중지하거나 바인딩을 바꾸지 않는다.

- <a download href="../../labs/week-01/server.py">server.py · 기존 Handler</a>
- <a download href="../../labs/week-14/backend.py">backend.py · 서버 실행기</a>
- <a download href="../../labs/week-14/proxy.py">proxy.py · 프록시</a>
- <a download href="../../labs/week-14/enabled.txt">enabled.txt · 사용할 서버 목록</a>
- <a download href="../../labs/week-14/congestion.txt">혼잡 그래프 수치</a> · <a download href="../../labs/week-14/congestion.svg">그래프 SVG</a> · <a download href="../../labs/week-14/observations.txt">가공 제공 사례</a>

enabled.txt와 observations.txt는 JSON, congestion.txt는 CSV 형식의 텍스트다. 확장자는 `.txt`로 유지하고 내용을 해당 형식으로 읽는다.

```bash
python3 --version
curl --version
ss -ltn '( sport = :18080 or sport = :18081 or sport = :18082 )'
python3 -m py_compile server.py backend.py proxy.py
```

세 포트가 이미 LISTEN이면 소유자를 확인한다. 타인의 프로세스를 종료하지 말고 진행자에게 별도 격리 호스트를 요청한다. 이 키트의 백엔드 포트는 18081/18082로 고정되어 있어 실행 인자만 임의로 바꾸면 프록시와 맞지 않는다. 바인딩은 모두 127.0.0.1이다. SSH 연결을 유지한 채 그 안의 셸에서 curl을 실행한다. 개인 PC의 localhost는 VM의 localhost가 아니다.

<span id="delay-lab"></span>

## 실험 A · 계산·그래프와 실제 서버 대기 비교

먼저 [교재의 두 계산 묶음과 그래프](CONCEPTS.md)를 읽고 단위·가정·손실 사건을 설명한다. 제공 그래프는 실제 패킷이 아니다. 직접 측정과 분리해서 보관한다.

### A1 정상 기준 · 셸 1과 셸 4

셸1에서 a를 전경 실행한다. 로그의 `listening`과 delay_s=0을 확인한다.

```bash
python3 -u backend.py --id a --port 18081 --delay 0
```

셸4에서 아래 5회를 실행한다. `phase`는 normal, delayed, recovered 순서로 바꾼다. URL·본문 조건·클라이언트·횟수·단일 순차 요청은 유지하고 phase는 파일·출력 이름에만 쓴다. 각 요청 사이 0.2초 기다리며 부하 시험으로 늘리지 않는다.

```bash
phase=normal
for i in 1 2 3 4 5; do
  curl --noproxy '*' --connect-timeout 1 --max-time 5 -sS \
    -D "$phase-$i.headers" -o "$phase-$i.body" \
    -w "phase=$phase n=$i http=%{http_code} connect_s=%{time_connect} first_s=%{time_starttransfer} total_s=%{time_total}\n" \
    "http://127.0.0.1:18081/echo?message=w14-$i"
  result=$?
  printf 'curl_exit=%s\n' "$result"
  sleep 0.2
done
```

정상 기대는 매번 curl_exit=0·HTTP200·본문의 message·헤더 X-Backend:a다. 셸1의 각 `listening` 이후 구간에서 `response`·`backend_done`의 같은 `w14-i`를 찾는다. 단계별 터미널 출력을 따로 보관하면 같은 요청을 재사용해도 구별할 수 있다. 404는 HTTP 응답이므로 curl 종료값0일 수 있다. 이 명령은 `--fail`을 쓰지 않아 HTTP 상태와 통신 오류를 따로 기록한다. 중간 실패를 성공 표본으로 지우지 않는다.

### A2 처리 대기만 변경 · 복구

셸1에서 Ctrl+C로 **자신의 a만** 종료하고 같은 명령을 `--delay 0.2`로 다시 실행한다. 셸4의 phase를 delayed로 바꿔 같은 5회를 반복한다. 이후 a를 Ctrl+C로 종료하고 원래 `--delay 0`으로 실행, phase=recovered로 5회를 반복한다.

대기는 0.2초를 요청 처리 앞에 넣는다. 실제 대기는 OS 스케줄링 때문에 정확히 0.200000초를 보장하지 않는다. first_s/total_s가 늘어날 것으로 예상하지만 숫자는 직접 관찰한 값만 쓴다. 같은 시점의 `/health`는 지연을 넣지 않아 여전히200이다.

```bash
curl --noproxy '*' --max-time 5 -i http://127.0.0.1:18081/health
curl --noproxy '*' --max-time 5 -i http://127.0.0.1:18081/missing
```

각 단계 요청 수5·HTTP 오류 수·curl 통신 실패 수와 total_s의 범위를 비교한다. 5개로 p99를 추정하거나 일반적인 성능 향상을 주장하지 않는다. `time_connect`는 시작→TCP 연결 완료, `time_starttransfer`는 시작→첫 응답 byte, `time_total`은 전체 작업 시간이며 모두 초다. 새 curl 프로세스와 Connection:close로 요청마다 새 연결을 만든다. 수치에는 로컬 TCP/스케줄링·앱 대기·본문 수신이 들어가고 DNS 질의·TLS는 이 숫자 주소 HTTP 실험에 없다. first_s−connect_s도 순수 서버 처리나 망 RTT는 아니다.

선택으로 기존 4·6주차의 허가된 루프백 캡처·TCP 관찰을 재사용해 요청/첫 응답 시각을 비교한다. 캡처 권한이 없으면 요구하지 않는다. 서버의 `elapsed_ms`는 do_GET 진입→쓰기 뒤, curl의 초와 시작/끝이 다르다. 서로 다른 호스트 시계를 그냥 빼지 않는다.

<span id="proxy-lab"></span>

## 실험 B · 직접 분산·제외·복귀와 정지·복구

### B1 두 서버와 프록시 정상

a가 delay0으로 실행 중인 것을 확인한다. 셸2에서 b, 셸3에서 프록시를 전경 실행한다. enabled.txt의 초기 JSON 내용은 `["a", "b"]`다.

```bash
# 셸 2
python3 -u backend.py --id b --port 18082 --delay 0
# 셸 3
python3 -u proxy.py --config enabled.txt
```

셸4에서 상태와 실제 GET을 따로 본다.

```bash
curl --noproxy '*' --max-time 5 -sS http://127.0.0.1:18080/status
curl --noproxy '*' --max-time 5 -i 'http://127.0.0.1:18080/echo?message=w14-probe'
```

`enabled`는 설정, `health`는 요청 시점에 두 서버로 보낸 `/health` 결과, `eligible`은 둘을 만족하는 현재 후보 목록이다. 첫 probe의 X-Backend와 message를 확인한다. 아래 반복은 단계당 **6회**다. 짝수이므로 후보가 안정되고 다른 요청이 끼지 않으면 각 서버3회가 기대되며, 첫 서버가 a인지 b인지는 앞 요청 수에 따라 달라진다.

```bash
phase=both
for i in 1 2 3 4 5 6; do
  curl --noproxy '*' --connect-timeout 1 --max-time 5 -sS \
    -D "$phase-$i.headers" -o "$phase-$i.body" \
    -w "phase=$phase n=$i http=%{http_code} total_s=%{time_total}\n" \
    "http://127.0.0.1:18080/echo?message=w14-$phase-$i"
  result=$?
  printf 'curl_exit=%s\n' "$result"
  sleep 0.2
done
grep -hi '^X-Backend:' "$phase-"*.headers
```

헤더의 a/b별 수·HTTP 오류·curl 실패·시간을 집계하고 서버의 `/echo?message=w14-both-i` 로그와 프록시 `backend`를 맞춘다. `/health`는 프록시가 추가한 점검이므로 사용자 GET 수와 구별한다. 6회 사용자 GET이면 이 구현은 각 서버에 health6회씩도 보낸다. 상태 조회를 실행하면 점검이 추가된다.

### B2 b를 목록에서 제외 · b는 살아 있는 상태

셸4에서 자신의 설정 파일을 같은 폴더의 임시 파일로 쓰고 교체한다. 원자적 교체로 프록시가 반쯤 쓴 JSON을 읽는 것을 피한다. 실행 중 설정은 매 요청마다 읽는다.

```bash
python3 -c 'from pathlib import Path; import os; p=Path("enabled.next.txt"); p.write_text("[\"a\"]\n", encoding="utf-8"); os.replace(p,"enabled.txt")'
curl --noproxy '*' --max-time 5 -sS http://127.0.0.1:18080/status
curl --noproxy '*' --max-time 5 -i http://127.0.0.1:18082/health
```

enabled/eligible는 a만, health는 a/b 모두 true가 기대된다. b 직접 health200과 a만 선택되는 것은 모순이 아니다. phase=excluded로 위 6회를 반복해 a6회·실제 상태/본문/시간을 확인한다.

### B3 목록 복원 · b 프로세스 정지 · 다시 복구

```bash
python3 -c 'from pathlib import Path; import os; p=Path("enabled.next.txt"); p.write_text("[\"a\",\"b\"]\n", encoding="utf-8"); os.replace(p,"enabled.txt")'
curl --noproxy '*' --max-time 5 -sS http://127.0.0.1:18080/status
```

phase=restored로 6회를 반복해 분산 복귀를 본다. 이어 **셸2의 본인 b만 Ctrl+C**로 멈춘다. 같은 status에서 enabled에는 b가 있지만 health.b=false·eligible는 a만인지 확인하고 phase=stopped로 6회를 반복한다. 이 키트는 매 요청 직전 상태를 확인하므로 안정적으로 정지한 b를 피할 것으로 예상한다. 상태 확인 직후의 정지라면 전달502가 생길 수 있다. 이를 오류 없이 전환했다고 숨기지 않는다.

셸2에서 원래 b 명령을 다시 실행한다. status·phase=recovered-proxy의 6회·b/a 로그를 비교해 정상 분산·오류·시간까지 복구됐는지 확인한다. enabled 복원만으로 복구를 선언하지 않는다. `/status=200`이어도 모든 백엔드가 false면 실제 `/echo`는503이다.

## 코드 읽기 · 입력에서 출력까지

| 파일·단계 | 따라 읽을 것·처음 나오는 문법 | 확인할 출력/오류 |
| --- | --- | --- |
| 기존 server.py의 Handler | URL 경로·message→200/404→UTF8 본문·Content-Length·Connection:close→response 로그 | 기존 `/echo`와 한글 본문을 유지 |
| backend.py의 Backend(Handler) | 상속으로 기존 처리 재사용. super()는 기존 메서드를 호출. end_headers에서 식별자 추가, do_GET에서 health 분기·time.sleep·기존 처리 | X-Backend, backend_done의 처리 구간. delay는0\~0.5초만 |
| proxy.py enabled_backends | Path.read_text→json.loads→a/b 목록·빈 목록/중복 검증 | 잘못된 시작 설정은 종료2, 실행 중 깨진 설정은503 |
| request_backend | 고정 loopback/port→GET→getresponse→본문/식별자. finally는 성공·실패 모두 close | health0.5초/실제요청2초 소켓 대기 제한·본문64KiB 상한 |
| Proxy.do_GET | 설정 읽기→두 health→후보→상태 응답 또는 후보 선택→실제 GET→reply/log | 후보 없음503, 선택 후 실패502, 지원하지 않는 경로404 |
| selection_lock / next_index | with로 잠금을 잡고 선택 번호를 증가. 같은 시점 요청의 번호 충돌 방지 | 순차·안정 후보에서 round robin. 동시 처리 완료 순서 보장 아님 |
| main | argparse로 입력→검증→with로 소유 리스너 열기→serve_forever→Ctrl+C·정리 | 포트 충돌은 종료1. 관리자 권한으로 해결하지 않음 |

두 파일의 LabServer는 표준 ThreadingHTTPServer를 그대로 사용하며 주소 재사용 설정만 OS별로 정한다. Linux에서는 종료 직후 같은 포트로 재시작할 수 있게 하고, Windows에서는 중복 리스너를 막도록 주소 재사용을 끈다. 실행 전 ss 확인과 본인 프로세스 구별은 여전히 필요하다.

표준 http.server/http.client가 HTTP 메시지 경계와 파싱을 맡는다. 범용 프록시·TLS·인증·스트리밍·재시도·운영 보안을 구현한 것이 아니다. GET `/echo`만 전달하며 외부 주소나 사용자 지정 upstream을 받지 않는다. timeout은 소켓 대기 제한이므로 운영용 전체 요청 마감 시간 보장으로 쓰지 않는다. 상태와 본문을 한 번에 받은 뒤 보내므로 프록시 TTFB에는 백엔드 본문 수신까지 포함된다.

자기 말로 “health가200인데 왜 요청이 느릴 수 있나?”, “enabled와 eligible는 언제 다른가?”, “서버 두 포트가 같은 호스트라면 어떤 장애를 못 피하나?”를 설명한다. [K1\~K3](CONCEPTS.md)·[W14-D1\~D3 해설](ANSWERS.md#development)·[공식 API/명령 근거](SOURCES.md)로 돌아갈 수 있다.

## 실패를 구별하고 정리하기

| 증상 | 먼저 볼 것·복구 |
| --- | --- |
| ModuleNotFoundError: server | 같은 실습 폴더에 기존 server.py가 있는지 확인. 전역 Python 경로를 임의 수정하지 않음 |
| Address already in use | ss와 자신이 연 셸의 listening 확인. 다른 프로세스를 죽이지 않고 중단 |
| proxy 시작 설정 오류 | enabled.txt의 JSON·a/b·중복/빈 목록 확인, 원래 파일로 복원 |
| curl 통신 실패/HTTP000 | 각 전경 프로세스·LISTEN·같은 VM에서 실행했는지 확인. 502/503 HTTP 응답과 구별 |
| 502 / 503 | 선택 후 실패/현재 후보 없음/설정 오류를 본문으로 구별. status·직접 health·서버 로그를 비교 |
| health200·echo 지연 | delay 인자·backend_done·클라이언트 시간, 실제 경로·의존성을 따로 비교 |

실습이 끝나면 셸1·2·3에서 **각자 시작한 프로세스**를 Ctrl+C로 종료한다. enabled.txt을 B3의 a/b 목록으로 복원하고 ss로 세 리스너가 닫혔는지 확인한다. `killall python`·공유 서비스 종료·관리SSH 변경은 하지 않는다. 개인 로그·헤더/본문은 필요한 근거만 본인 파일에 한 번 보관하고 실제 접속 정보·개인 경로를 공개 저장소에 넣지 않는다.

직접 완료 근거는 두 계산·그래프 설명과 본인의 정상/지연/복구, 분산/제외/복귀/정지/복구 요청 수·오류·시간·양쪽 로그다. O04는 본인 전환, O05는 정상 기준·다른 원인 가설 두 개·구별할 관찰·최소 변경·복구 설명까지 확인한다. 제공 사례·AI 해설만 읽었다면 직접 수행은 미완료다. [복습](REVIEW.md) · [학습 홈](README.md).
