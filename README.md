# 실습으로 배우는 네트워크

요약: 개념을 읽고 패킷·로그를 관찰하며 직접 실험하는 컴퓨터 네트워크 공개 학습 자료다. 혼자 공부하거나 함께 스터디하며 기초 원리부터 Linux 실습·기본 클라우드 운영까지 익힌다.

**[학습 사이트 바로가기](https://ostenhun.github.io/aolda-network-study-4th/)** · [전체 개념 색인](https://ostenhun.github.io/aolda-network-study-4th/materials/week-01/concept-index.html) · [교재 원본](content/materials/)

아주대학교 클라우드 운영 소학회 [아올다](https://aoldacloud.com/)의 4기 네트워크 스터디에서 시작한 공개 학습 프로젝트다. 소속과 관계없이 개인 학습과 다른 스터디에서도 활용할 수 있다.

IP 주소와 포트를 배웠어도 연결 실패와 HTTP 오류를 구별하기는 쉽지 않다. 서브넷 계산을 할 수 있어도 패킷이 누구에게 먼저 전달되는지 설명하다 보면 막히는 부분이 생긴다. 이 자료에서는 교재를 읽고 코드를 실행하며 관찰한 결과로 그런 질문에 답을 찾는다.

컴퓨터 네트워크 기초를 처음 배우는 학생, 개발 중 만난 통신 문제를 이해하고 싶은 개발자, 함께 질문을 찾고 설명하는 스터디에 맞춰 구성했다. 학부에서 배우는 핵심 원리를 익히고 기본 클라우드 운영과 면접에서의 설명 연습으로 이어 간다.

개념 설명과 Linux 실습 코드, 브라우저에서 조건을 바꾸는 모형, 복습 문제와 분리 해설을 함께 제공한다. 예를 들어 **서브넷 마스크가 경로 판단에 미치는 영향**, **목적지 IP와 다음 홉의 MAC 주소가 다른 이유**, **TCP 전송 성공과 애플리케이션 처리 성공의 차이**를 교재에서 읽고 실습으로 확인할 수 있다. 내용의 근거는 각 교재의 공식 출처에서 확인한다.

## 사이트는 어떻게 구성되어 있나

홈에서 주차를 고르면 왼쪽 학습 메뉴로 교재·실습·복습을 오갈 수 있다. 특정 개념만 다시 찾을 때는 상단 **자료 검색**이나 **전체 개념 색인**을 사용한다. 모바일에서는 **학습 메뉴**를 열어 이동한다.

- **학습 안내·탐구 질문**: 이번 주에 설명할 현상을 정하고, 무엇을 찾아볼지 잡는다.
- **개념 교재·핵심 정리**: 원리와 예시를 읽고 헷갈리기 쉬운 개념을 구별한다.
- **Linux 실습·코드 읽기**: 주소·경로·소켓·로그·패킷을 확인하고, 코드의 동작과 출력을 연결한다.
- **브라우저 실습 모형**: 제공된 모형에서 조건을 바꾸며 결과를 예상한다. 실제 VM 관찰과 구별해서 사용한다.
- **복습 문제·분리 해설**: 먼저 자기 말로 답하고 해설과 비교한다. 답안 입력 화면에서는 기록을 Markdown으로 내려받을 수 있다.
- **공식 출처·참고자료**: 교재의 설명을 원문과 대조하고 더 깊이 읽을 부분을 찾는다.

주차마다 자료의 이름과 구성이 조금씩 다르다. 교재와 복습은 브라우저로 읽을 수 있으며, Linux 직접 실습에는 본인이 사용할 수 있는 환경이 필요하다. 실습에는 본인의 접속 정보를 사용한다. 주소와 가상 출력은 예시이며, 제공 캡처의 측정 조건은 해당 안내에서 확인한다.

## 지금 읽을 수 있는 주제

- **[VM·SSH 준비](https://ostenhun.github.io/aolda-network-study-4th/materials/ssh-top-down/index.html)**: Linux VM, 접속 주소, 서버 신뢰와 SSH 인증을 다룬다. 내 PC에서 어느 서버에 접속한 것일까?
- **[1주차 · 요청과 응답](https://ostenhun.github.io/aolda-network-study-4th/materials/week-01/index.html)**: 클라이언트·서버, IP와 포트, HTTP, 로그와 패킷을 다룬다. 요청 하나는 어디로 가고 어떤 응답을 받을까?
- **[2주차 · IPv4와 서브넷](https://ostenhun.github.io/aolda-network-study-4th/materials/week-02/index.html)**: IPv4, 서브넷 마스크, CIDR, 주소 범위와 경로를 다룬다. IP가 비슷하면 같은 네트워크일까?
- **[3주차 · LAN과 다음 홉](https://ostenhun.github.io/aolda-network-study-4th/materials/week-03/index.html)**: LAN, MAC 주소, 다음 홉, ARP 캐시, ICMP와 ping을 다룬다. 패킷은 누구에게 먼저 갈까?
- **[4주차 · TCP와 UDP](https://ostenhun.github.io/aolda-network-study-4th/materials/week-04/index.html)**: 소켓, RTT, 연결 수립, 바이트 스트림과 데이터그램, SEQ/ACK를 다룬다. TCP가 데이터를 전달하면 프로그램의 처리도 끝난 것일까?
- **[5주차 · DNS와 DHCP](https://ostenhun.github.io/aolda-network-study-4th/materials/week-05/index.html)**: 재귀/권한 DNS, A/AAAA, 캐시·TTL과 DHCP 임대·설정 옵션을 다룬다. 이름에서 IP를 찾았는데 왜 요청은 실패할까?
- **[6주차 · HTTP·TLS·SSH](https://ostenhun.github.io/aolda-network-study-4th/materials/week-06/index.html)**: HTTP 메시지·재사용·캐시, TLS 신원 검증과 SSH 인증을 다룬다. 같은 IP인데 이름이 다르면 왜 HTTPS가 거절될까?
- **[7주차 · 정적 경로](https://ostenhun.github.io/aolda-network-study-4th/materials/week-07/index.html)**: 최장 접두사·다음 홉·왕복 경로·TTL을 다룬다. 가는 경로가 있는데 왜 응답은 돌아오지 않을까?
- **[8주차 · 중간 복습·IPv6](https://ostenhun.github.io/aolda-network-study-4th/materials/week-08/index.html)**: 전체 요청 흐름·RTT·손실 복구 모형·IPv6/NDP를 비교하고 단일 장애를 진단한다. 같은 요청을 다시 보내면 무엇을 생략할까?
- **[9주차 · 링크·VLAN·STP·LACP](https://ostenhun.github.io/aolda-network-study-4th/materials/week-09/index.html)**: MAC 학습·VLAN·STP 경로·LACP 멤버 전환과 오류 검출을 다룬다. 같은 스위치인데 왜 닿지 않을까?
- **[10주차 · 동적 라우팅·OSPF](https://ostenhun.github.io/aolda-network-study-4th/materials/week-10/index.html)**: LS/DV 계산·AS/BGP 정책과 실제 FRR 세 라우터의 이웃·경로·링크 전환을 다룬다. 링크가 끊기면 경로표는 누가 고칠까?

- **[11주차 · NAT·접근 정책](https://ostenhun.github.io/aolda-network-study-4th/materials/week-11/index.html)**: NAT/PAT의 왕복 대응과 접근 규칙의 방향·순서·상태를 배우고, 격리 HTTP 서버의 허용·차단·복구를 직접 비교한다.

- **[12주차 · 무선·망 구성·VPN](https://ostenhun.github.io/aolda-network-study-4th/materials/week-12/index.html)**: 무선 상태·매체 접근·VPN 전후 경로를 제공 자료로 분석하고 작은 망의 분리·허용 경로·보호 경계를 그린다.

- **[13주차 · 클라우드 네트워크](https://ostenhun.github.io/aolda-network-study-4th/materials/week-13/index.html)**: 자기 VM의 자원·양끝 요청·테스트 접근 규칙 변경/복구를 연결하고 MTU·MSS·PMTUD를 제공 사례로 분석한다.

- **[14주차 · 성능·트래픽 분산](https://ostenhun.github.io/aolda-network-study-4th/materials/week-14/index.html)**: 지연·BDP·윈도 상한과 고전 혼잡 그래프를 읽고 정상/서버 대기·프록시 분산/제외/복구를 직접 비교한다.

- **[15주차 · 소켓·작은 자동화](https://ostenhun.github.io/aolda-network-study-4th/materials/week-15/index.html)**: 소켓 경계·부분 수신·EOF·시간제한을 읽고 종료 조건 변경·원복과 HTTP 수동/자동 기록을 대조한다.

- **[16주차 · 종합 장애 진단](https://ostenhun.github.io/aolda-network-study-4th/materials/week-16/index.html)**: 기존 서비스의 두 가설·구별 관찰·최소 변경·복구와 C16·O01~O05의 근거를 연결한다.

공개 자료는 VM·SSH 준비와 1~16주차의 질문·교재·실습·복습으로 구성된다. 후속 SRE·플랫폼·클라우드 심화는 별도 학습 범위다. 자료 열람과 실제 실습·독립 이해는 구별하며, 완료 여부는 각자가 실행하고 설명한 근거로 확인한다.

## 어떻게 공부하면 좋을까

**처음 시작한다면** VM·SSH 준비에서 접속 경로를 이해한 뒤 1주차부터 읽는다. **궁금한 개념이 있다면** 개념 색인에서 해당 교재로 바로 이동한다. **면접이나 설명 연습이 목적이라면** 핵심 정리의 혼동 구별·개발 질문과 복습 문제를 활용한다.

2주차부터 한 주의 자료는 **개인 공부·실습 → 주 1회 오프라인 마무리 → 보충**의 흐름으로 사용한다. 1주차의 기존 학습 기록은 유지한다.

1. **모임 전에 공부하고 실습을 시도한다.** 학습 홈에서 범위를 찾고 질문에 먼저 답한 뒤 교재·공식 지정 절·복습·해설과 대조한다. 실습은 정상 기준·한 조건 변경·비교·복구를 확인한다.
2. **질문·혼동·핵심을 기존 개인 노트에 정리한다.** 주요 질문과 내 답, 헷갈리는 개념 비교, 꼭 기억하고 이해할 핵심 개념을 중심으로 이유·조건·실습 근거를 연결한다. [개념 색인의 정리 방법](https://ostenhun.github.io/aolda-network-study-4th/materials/week-01/concept-index.html#personal-study)과 각 주차 안내에서 시작한다. 새 양식이나 정해진 분량은 없다.
3. **오프라인에서 설명과 새 조건으로 마무리한다.** 설명자를 교대하고 다른 사람은 조건 하나를 바꿔 질문한다. 준비한 근거와 막힌 실습·복구를 각자 확인한다. 이미 마친 정상 실습을 전부 반복할 필요는 없다.
4. **남은 부분을 보충한다.** 처음 헷갈린 이유·고친 설명과 근거를 개인 노트에 보완한다. 제공 자료 분석과 직접 실행을 구별하고 미완료 수행을 다음 보충으로 남긴다.

혼자 공부할 때도 같은 순서로 답을 가리고 설명하고, 새 값이나 출력으로 바꾸어 확인할 수 있다.

예를 들어 2주차에서는 `/24`와 `/26`의 주소 범위를 계산한 다음 VM의 주소와 경로를 확인한다. 계산상 같은 망이라는 판단과 실제 통신 가능 여부가 어떻게 다른지 설명하고, 3주차의 다음 홉·ARP로 이어 갈 수 있다.

## 원문과 출처 활용하기

사이트는 읽기·탐색·실습용 화면이고, 이 저장소의 `content/`에는 교재 Markdown과 실습 코드가 있다. 예를 들어 [2주차 개념 원문](content/materials/week-02/CONCEPTS.md), [4주차 개념 원문](content/materials/week-04/CONCEPTS.md), [4주차 공식 출처](content/materials/week-04/SOURCES.md)를 찾아볼 수 있다.

자료를 공유하거나 설명을 인용할 때는 **해당 교재 URL·절·공식 출처**를 함께 남긴다. 이 자료는 한국어 학습 안내이며 기술 표준의 정본은 각 교재에서 연결한 공식 문서를 따른다. 외부 자료를 재사용할 때도 원래 출처와 이용 조건을 확인한다.

---

아래는 교재를 수정하거나 사이트를 직접 실행하려는 사람을 위한 안내다.

## 소스와 빌드

Python 3.12 이상과 Node.js 22.22 이상을 사용한다. CI는 Node.js 24를 사용하며 Astro 버전은 잠금 파일로 고정한다.

```sh
npm ci --ignore-scripts
npm test
npm run build
python -m http.server 8000 --directory dist
```

브라우저에서 `http://localhost:8000`을 연다. 저장소를 새로 내려받아도 내부 문서·기존 ZIP·ChatGPT Sites 계정 없이 같은 사이트를 만들 수 있다.

| 위치 | 역할 |
| --- | --- |
| `content/` | 공개 교재 Markdown, 페이지 HTML 원본, 실습 코드와 예제 캡처 |
| `config/site.json` | 과정·메뉴·홈 연결과 새 교재의 입력/출력 경로 |
| `astro/` | 새 Markdown 교재의 HTML·목차 생성 |
| `tools/templates/study-home.html` | 학습 홈 원본 |
| `tools/study_site_theme.py` | 공통 탐색·현재 위치·검색 색인 생성 |
| `tools/study-site.css`, `tools/study-site.js` | 공통 디자인과 브라우저 동작 |
| `tools/build-site.py` | 공개 소스 검사·링크/앵커 확인·정적 파일 생성 |
| `.github/workflows/pages.yml` | 변경 검사와 Pages 자동 배포 |
| `dist/` | 생성물. Git에 넣지 않고 Actions에서 생성 |

공개 화면의 정본은 이 저장소다. 기존 주차의 HTML·Markdown은 그대로 유지한다. 다음에 제작하는 교재는 Markdown 한 벌을 Astro로 변환하며 HTML을 따로 작성하지 않는다. 공통 탐색·검색은 빌드할 때 생성하므로 각 교재에 직접 넣지 않는다. Python은 기존 페이지 보존·공통 조립·공개 정보와 링크 검사를 맡는다.

[새 교재 작성 안내](docs/AUTHORING.md)에 Markdown 양식과 과정 등록 예시, 복습 답안·링크·검사 방법을 정리했다. 4주차부터 이 경로로 제작하며 새 주차의 기본으로 사용한다. 기존 1주차 교재와 학습 기능은 보존한다.

## 수정과 게시

작은 수정은 `main`에 반영하고 큰 수정은 브랜치와 PR로 검토한다. PR에서는 공개 정보와 링크를 검사하며, `main` 반영 후 검사에 통과하면 Pages에 배포한다. 화면 변경은 데스크톱·모바일에서 한국어 줄바꿈, 키보드 조작, 검색·실습·답안 다운로드를 확인한다.

[운영·공개 범위](docs/OPERATIONS.md)에서 자료 추가, 게시 확인과 복구 절차를 확인한다. 내용의 기술 근거는 각 교재의 공식 출처를 따른다.

[공식 로고 사용](docs/BRAND.md)에 헤더·푸터·홈·파비콘의 자산 출처와 표시 기준을 정리했다.

[검색·AI 활용 운영 기준](docs/OPERATIONS.md#검색과-ai-학습-활용)에 검색 허용·대표 주소·사이트맵과 실제 색인 확인 방법을 정리했다.
