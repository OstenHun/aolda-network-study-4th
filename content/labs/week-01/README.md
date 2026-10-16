# 1주차 실행 키트

요약: Linux Python 서버와 curl이 기본이며 Node/TypeScript는 선택이다. 단계별 명령은 LINUX.md, 팀 활동은 학습 묶음에서 읽는다. 제공 캡처 분석과 본인 직접 실행을 구분한다.

## 기본 실행 경로

1. [학습 묶음](../../materials/week-01/README.md)에서 읽기 순서를 확인한다.
2. [Linux 실습 정본](LINUX.md)의 준비와 1~6단계를 따른다. 서버·요청은 같은 Linux, 캡처는 lo, pcap 분석은 개인 PC에서도 가능하다.
3. 네 상태의 상세 예상·출력·패킷은 [개인 실습 기록](../../materials/week-01-prestudy.html#start)이나 별도 증거 파일에 보관한다. [팀 활동](../../materials/week-01/WORKSHEET.md)에는 질문·근거 위치·바뀐 설명·남은 질문과 개인 마무리 두 줄을 남긴다.

필수 파일은 [server.py](server.py) 하나이며 Python 표준 라이브러리만 사용한다. 127.0.0.1에 바인딩하고 /echo에 200, 다른 경로에 404를 돌려준다. 디렉터리 파일을 제공하는 서버가 아니다. 이번 키트는 요청마다 연결을 닫도록 구성했다. 모든 HTTP 서비스가 그렇게 동작한다는 뜻은 아니다.

## 처음 코드를 읽는 순서

[코드 읽기 HTML](../../materials/week-01/code-reading.html)에서 Python 문법의 최소 뜻과 실제 파일을 함께 본다. `server.py`의 번호 주석을 따라 요청 읽기 → 경로와 메시지 판정 → JSON 본문 만들기 → HTTP 응답 보내기 → 서버 로그 남기기를 확인한다. 아래 선택 Node 코드는 기본 실습 후에 읽어도 된다.

코드는 한 줄 조건식을 풀고 역할을 드러내는 변수명과 한국어 주석을 사용한다. 설명에 보이는 전체 코드도 실제 키트 파일에서 생성한다. Markdown 설명 정본은 [CODE_READING](../../materials/week-01/CODE_READING.md)이다.

## Node/TypeScript — 선택

이미 준비된 Node 22.18 이상 또는 24.3 이상에서 [client.mts](client.mts)를 실행한다. 타입 제거 실행이며 타입 검사는 별도다. 기본 curl 실습을 위해 Node 설치가 필요하지 않다.

```sh
node --version
node labs/week-01/client.mts 'http://127.0.0.1:8080/echo?message=hello'
echo $?
node labs/week-01/client.mts 'http://127.0.0.1:8080/missing'
echo $?
```

| Node 이벤트 | 읽을 값 |
| --- | --- |
| connected | local·remote 주소/포트 |
| response | HTTP 상태·헤더 |
| body | 본문, elapsed_ms는 앱 경과 시간이며 순수 망 지연 아님 |
| network_error | 연결·시간 제한 등 오류, 원인은 조건과 대조 |

Node 키트 종료 코드는 정상 0, HTTP 400 이상 2, 연결 등 오류 1이다. 기본 curl의 404 전송 완료는 0이므로 혼동하지 않는다. 서버 response 로그의 client·path·status와 대조한다. Node 클라이언트에는 프록시 설정을 구성하지 않았다.

공식 출처는 [SOURCES](../../materials/week-01/SOURCES.md), 예제 패킷은 [제공 캡처 안내](../../materials/week-01/SAMPLE_CAPTURE.md)에서 확인한다.
