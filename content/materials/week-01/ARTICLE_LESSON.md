# 1주차 원문으로 배우기 — 요청 하나를 설명하는 다섯 질문

요약: roadmap.sh의 1주차 term에 연결된 article을 개념 설명과 Linux HTTP 실습으로 잇는다. 포트·HTTP 지정 부분은 필수 10분, 나머지는 선택 읽기다. 원문 확인과 실제 실습 완료를 구분한다.

## 이 자료를 읽는 방법

[개념 교재](CONCEPTS.md)를 읽으면서 막히는 질문에 해당하는 절을 찾아본다. 각 절은 원문에서 읽을 부분 → 한국어 설명 → 실습에서 확인할 질문 순서다. **필수 원문 읽기는 3절 포트 5분 + 5절 HTTP 5분**이며 기존 개념 학습 30분에 포함한다. 나머지 원문은 모두 읽도록 요구하지 않는다. 영어 읽기가 어렵거나 링크가 열리지 않으면 여기의 설명과 개념 교재로 질문을 함께 풀고, 원문 미열람으로 기록한다.

설명·질문은 자체 작성했다. 원문의 글·그림·해답을 복제하지 않는다. 아래 실습 연결은 기존 키트의 조건을 설명하며 새로 관찰한 결과가 아니다. 명령은 [Linux 실습](../../labs/week-01/LINUX.md), 상세 예상·출력·패킷은 [개인 실습 기록](../week-01-prestudy.html#start)이나 별도 증거 파일에 남긴다. [팀 활동](WORKSHEET.md)에는 함께 확인한 근거 위치와 바뀐 설명·남은 질문을 적는다.

## 1. 네트워크 통신은 꼭 인터넷을 지나갈까?

**원문 선택 읽기, 3분:** What are Networks?의 [IBM — What is computer networking?](https://www.ibm.com/think/topics/networking) 첫 정의, How does the Internet Work?의 [MDN — How does the Internet work?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work) 도입과 Internet and the web 부분을 읽는다. 라우터 배치·DNS·사업자 연결의 상세는 후속 주차로 남긴다.

네트워크를 배우면 먼저 서로 다른 장치의 연결을 떠올리게 된다. 인터넷에서는 여러 네트워크 사이로 데이터가 전달된다. 웹은 그 위에서 사용하는 서비스 중 하나다. 따라서 웹·인터넷·네트워크를 같은 말로 쓰면 어느 범위를 확인했는지 설명하기 어렵다. [IBM](https://www.ibm.com/think/topics/networking), [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work)

이번 키트는 그 큰 경로를 한꺼번에 실험하지 않는다. 원격 Linux 안의 curl과 Python이 루프백으로 통신한다. 개인 PC에서 VM으로 들어가는 SSH 연결과, 접속한 VM 안에서 실행하는 HTTP 요청을 나누어 그려야 한다. 루프백 주소는 호스트 내부에서 쓰는 주소이며 외부 망으로 보내지 않는다. [RFC 1122 §3.2.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-3.2.1.3)

**예측과 확인:** SSH 접속 중 개인 PC의 네트워크가 끊기면 원격 셸 사용도 영향을 받을 수 있다. 이것과 VM 내부 HTTP가 외부 인터넷을 거치는지는 다른 질문이다. 기존 실습에서 명령이 실행되는 호스트를 먼저 표시하고 `lo` 캡처를 확인한다. 네트워크를 실제로 끊는 추가 실험은 하지 않는다.

**자기 설명:** “VM 내부에서 200을 받았다”라는 관찰만으로 외부 인터넷·DNS·공개 웹사이트가 정상이라고 말할 수 있을까? [개념 교재 1절](concepts.html#chapter-1)과 비교한다.

## 2. 호스트·클라이언트·서버는 어떻게 구분할까?

**원문 선택 읽기, 3분:** Server의 [Splunk — What Are Servers?](https://www.splunk.com/en_us/blog/learn/computer-servers.html)에서 What is a computer server?와 How servers work를 읽는다. 하드웨어 부품·AI 서버·구매 안내는 건너뛴다. Client의 TechTarget 링크는 아래 대응표에 보존하되 정의의 검증은 [Python HTTPServer 문서](https://docs.python.org/3/library/http.server.html#http.server.HTTPServer)와 [RFC 9110 §3.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.3)을 기준으로 한다.

호스트는 응용 프로그램을 실행하며 통신에 참여하는 끝 시스템이다. 클라이언트·서버는 특정 통신에서 맡는 역할이다. 서버라는 말이 장비와 소프트웨어를 모두 가리킬 수 있으므로, 이번에는 Linux VM 한 대와 그 안의 두 프로세스를 따로 센다. curl은 요청을 시작하고 Python 서버는 요청을 받아 응답한다. [RFC 1122 §1.1.1](https://www.rfc-editor.org/rfc/rfc1122.html#section-1.1.1), [RFC 9110 §3.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-3.3)

서버가 다른 서비스를 호출할 때는 그 통신에서 클라이언트가 될 수 있다. 역할은 장비에 영구히 붙는 이름이 아니다. 이번에는 추가 서비스를 만들지 않고 기존 두 프로세스의 역할만 설명한다. [Splunk](https://www.splunk.com/en_us/blog/learn/computer-servers.html)

**예측과 확인:** 서버를 중지하면 VM 자체도 사라질까? 기존 중지 단계에서 셸은 계속 사용할 수 있는지, 같은 요청의 HTTP 응답은 있는지 각각 기록한다. 터미널 창 두 개를 호스트 두 대로 세지 않는다.

**자기 설명:** VM·셸·Python 프로세스·curl 프로세스를 나누어 그리고 요청 화살표를 붙인다. [개념 교재 2~3절](concepts.html#chapter-2)과 비교한다.

## 3. 같은 IP에서 두 프로그램을 어떻게 구분할까?

**원문 필수 읽기, 5분:** Port의 [Cloudflare — What is a computer port?](https://www.cloudflare.com/learning/network-layer/what-is-a-computer-port/)에서 What is a port?와 What is a port number?만 읽는다. 포트 목록 암기·방화벽·ping 설명은 이번 읽기 범위에서 제외한다.

IP 주소만으로는 어느 서비스에 요청하는지 다 설명할 수 없다. TCP 통신에서는 주소와 포트를 함께 읽는다. IP 주소는 IP 헤더에서, 출발지·목적지 포트는 TCP 헤더에서 확인한다. [Cloudflare](https://www.cloudflare.com/learning/network-layer/what-is-a-computer-port/)

예를 들어 `127.0.0.1:51000 → 127.0.0.1:8080`은 설명용 요청 방향이다. 양쪽 IP가 같아도 포트가 다르다. 여기서 51000은 임의 예시이고 실제 클라이언트 임시 포트는 로그·캡처에서 찾아야 한다. 서버 대기 포트는 기존 `ss -lnt` 조회와 대조한다. 응답 방향에서는 출발지와 목적지가 뒤집힌다.

**원문을 읽을 때 주의:** 글의 “HTTP는 80번”은 일반적인 기본 포트 설명으로 읽는다. 모든 HTTP 요청이 반드시 80번으로 가는 것은 아니다. URL에 포트를 지정할 수 있고 이 키트는 8080을 사용한다. 포트 번호만 보고 프로토콜이나 암호화 여부를 확정하지 않는다. [RFC 9110 §4.2.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-4.2.1)

**예측과 확인:** URL에서 서버 포트만 틀리면 기존 서버의 `/echo` 처리까지 도달할까? 추가 실행 없이 먼저 예상하고, 기존 네 상태의 로그·캡처에서 실제 목적지 포트를 확인한다.

**자기 설명:** 내 요청의 양쪽 IP·포트 네 값을 적고 각각 클라이언트/서버를 표시한다. [개념 교재 4절](concepts.html#chapter-4)과 비교한다.

## 4. HTTP·TCP·IP는 각각 어떤 일을 할까?

**원문 선택 읽기, 5분:** Protocol의 [Cloudflare — What is a protocol?](https://www.cloudflare.com/en-gb/learning/network-layer/what-is-a-protocol/) 도입 정의와 OSI Model의 [Cloudflare — What is the OSI Model?](https://www.cloudflare.com/en-gb/learning/ddos/glossary/open-systems-interconnection-model-osi/) 응용·전송·네트워크 계층 설명을 읽는다. 7계층 암기와 보안 제품 안내는 필수에서 제외한다.

프로토콜은 통신 상대가 메시지를 만들고 처리할 때 따르는 규칙이다. 계층은 그 일을 나누어 이해하는 틀이다. 요청 경로·상태를 읽는 HTTP와, 연결 양끝의 바이트 전달을 담당하는 TCP, 출발지·목적지 주소를 담는 IP를 구분한다. TCP/IP의 응용·전송·인터넷·링크 구분은 [RFC 1122 §1.1.3](https://www.rfc-editor.org/rfc/rfc1122.html#section-1.1.3)에 대조했다.

| 질문 | 이번에 읽을 근거 | 설명할 역할 |
| --- | --- | --- |
| 어느 경로를 요청하고 무슨 응답을 받았나? | curl의 요청 줄·상태 줄, 서버 path/status | HTTP, 응용 |
| 어느 두 포트가 데이터를 주고받았나? | 캡처의 TCP 출발지·목적지 포트 | TCP, 전송 |
| 어느 주소에서 어느 주소로 보냈나? | 캡처의 IP 출발지·목적지 주소 | IP, 인터넷 |
| 어디서 캡처했나? | 캡처 명령의 인터페이스 `lo` | 이번에는 호스트 내부 전달 경로 |

이 표는 기존 실습을 읽는 안내다. `lo`에서 관찰했다고 외부 Ethernet 링크를 직접 관찰한 것으로 적지 않는다. 이 키트의 HTTP/1.1은 TCP를 사용하며, 모든 HTTP 버전을 같은 전송 방식으로 일반화하지 않는다. [RFC 9110 §2.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-2.5)

**예측과 확인:** 404를 받았을 때 “응용에서 원하는 결과를 못 얻었다”와 “메시지 전달 자체가 실패했다” 중 어느 설명이 맞는지 양쪽 로그로 판단한다.

**자기 설명:** 404 응답이 있으면 확인할 수 있는 것과 아직 확인하지 못한 것을 두 문장으로 나눈다. [개념 교재 5절](concepts.html#chapter-5)과 비교한다.

## 5. 404와 연결 실패는 왜 다를까?

**원문 필수 읽기, 5분:** HTTP / HTTPS의 [AWS — What’s the Difference Between HTTP and HTTPS?](https://aws.amazon.com/compare/the-difference-between-https-and-http/)에서 How does HTTP protocol work?의 요청·응답과 상태 코드 설명만 읽는다. HTTPS 인증서·키 교환·HTTP/2·HTTP/3는 6주차 이후 범위다.

HTTP 클라이언트는 요청을 보내고 서버는 상태 코드와 필요한 데이터를 응답한다. 200은 요청 성공을 나타내고, 404는 요청한 대상의 현재 표현을 찾지 못했거나 그 존재를 공개하지 않는 경우의 상태다. 이 키트에서는 코드의 `/echo` 분기와 그 밖의 경로 분기로 결과를 비교한다. 이 단순 분기를 모든 웹 서비스에 그대로 적용하지 않는다. [RFC 9110 §15.3.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.1), [§15.5.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.5)

404는 서버가 보낸 HTTP 응답이다. 서버를 중지한 뒤 연결이 거부되는 경우에는 그 요청의 HTTP 응답이 없을 수 있다. 상태 코드와 curl 종료 코드를 분리해 적어야 한다. `--fail`을 쓰지 않는 기존 명령에서는 HTTP 404를 받아도 전송을 마쳤다면 curl 종료 코드가 0일 수 있다. [curl 공식 매뉴얼](https://curl.se/docs/manpage.html)

**예측과 확인:** 기존 정상·없는 경로·중지·재시작 네 단계에서 HTTP 상태 줄, 새 서버 response 로그, curl 종료 코드를 각각 기록한다. 값을 예상한 표를 자신의 실제 출력으로 대신하지 않는다.

**자기 설명:** “404이므로 서버가 꺼져 있다”라는 말에 반박할 근거를 내 출력에서 찾는다. [개념 교재 6~7절](concepts.html#chapter-6)과 비교한다.

## term과 article 대응표

아래 표는 Network Engineer 로드맵의 term과 참고 article을 연결한다. 링크와 본문은 바뀔 수 있다. Temok 본문은 확인하지 못했으므로 설명의 근거로 단독 사용하지 않는다.

| term | 로드맵에 연결된 article | 이번 교재에서의 적용 |
| --- | --- | --- |
| What are Networks? | [IBM](https://www.ibm.com/think/topics/networking) | 1절 정의만 선택. 메일 전달·클라우드 상세는 제외 |
| How does the Internet Work? | [roadmap.sh guide](https://roadmap.sh/guides/what-is-internet) · [Cloudflare](https://www.cloudflare.com/en-gb/learning/network-layer/how-does-the-internet-work/) · [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work) | MDN을 1절 선택 원문으로 사용. 나머지는 대체 읽기 |
| Client | [TechTarget](https://www.techtarget.com/searchenterprisedesktop/definition/client) | 정의·동일 기계 설명 확인. /enterprise-software/definition/client로 이동. 선택 참고 |
| Server | [Splunk](https://www.splunk.com/en_us/blog/learn/computer-servers.html) | 2절 정의·요청 처리만 선택 |
| Host | [Temok](https://www.temok.com/blog/what-is-a-host) | 링크 확인, 본문 미확인으로 미채택. RFC 1122로 검증 |
| IP Address | [Coursera](https://www.coursera.org/articles/ip-address) | 개념 4절의 보충 후보. 클래스·서브넷 계산은 2주차로 이월 |
| Port | [Cloudflare](https://www.cloudflare.com/learning/network-layer/what-is-a-computer-port/) | 3절 필수. HTTP 포트의 일반화를 교재에서 보완 |
| Protocol | [Cloudflare](https://www.cloudflare.com/en-gb/learning/network-layer/what-is-a-protocol/) | 4절 정의만 선택 |
| OSI Model | [Cloudflare](https://www.cloudflare.com/en-gb/learning/ddos/glossary/open-systems-interconnection-model-osi/) · [Imperva](https://www.imperva.com/learn/application-security/osi-model/) | Cloudflare의 관련 계층을 선택, Imperva는 대체 읽기 |
| TCP/IP Model | [Wikipedia](https://en.wikipedia.org/wiki/Internet_protocol_suite) · [ThePower](https://thepower.education/en/blog/what-are-the-four-layers-that-make-up-tcp-ip) | 표 확인용 선택 참고. 교재의 역할 구분은 RFC 1122로 검증 |
| HTTP / HTTPS | [AWS](https://aws.amazon.com/compare/the-difference-between-https-and-http/) | 5절 요청·응답 필수. TLS 키 교환·버전 비교는 미채택 |

## 진행자 확인과 적용 한계

입문 article에는 간단한 비유·일반화·오래된 설명이 섞일 수 있다. Port 글의 80번 일반화는 RFC 9110 §4.2.1로 보완했다. AWS 글의 폼 전송을 PUT으로 설명한 예와 TLS 키 교환 절차는 이번 교재로 옮기지 않았다. HTTP 메서드 의미는 RFC 9110, 향후 TLS 1.3은 해당 명세를 기준으로 준비한다. Coursera의 IP 주소 예 `224.128.240.8`은 일반 유니캐스트 호스트 주소 예제로 사용하지 않는다. IP·서브넷의 상세 검증은 2주차 범위다.

RFC 1122는 호스트·루프백·계층의 기초 설명에 사용한다. 최신 모든 프로토콜 구현을 설명하는 자료로 취급하지 않는다. 원문은 [출처 안내](SOURCES.md)에서 확인한다.

