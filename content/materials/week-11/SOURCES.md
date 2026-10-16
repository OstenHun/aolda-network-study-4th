# 공식 출처 · NAT와 정책에서 읽을 범위

요약: NAPT 대응과 nftables의 방향·순서·상태, 실습 명령의 공식 근거를 연결한다. 참가자는 지정한 짧은 절을 읽고, 클라우드 비교·구현 상세는 교재 또는 선택 참고로 활용한다.

## 필수 공동 읽기

분량·시간은 추정이며 전체 원문 읽기를 요구하지 않는다. 영어가 막히면 먼저 교재의 같은 ID를 읽고 원문에서 용어와 조건만 찾는다. 링크의 제목뿐 아니라 아래 문단·표를 실제로 읽는다.

| 공식 자료·지정 범위 | 찾을 내용·학습에 쓰는 곳 | 추정 |
| --- | --- | --- |
| [RFC3022 §2.2 Overview of NAPT](https://www.rfc-editor.org/rfc/rfc3022.html#section-2.2)의 첫 문단과 Figure3 | local IP/TU port와 registered IP/assigned port의 대응. K1·B/C 제공 표의 왕복 화살표 설명 | 4분 |
| [nft 매뉴얼](https://www.netfilter.org/projects/nftables/manpage.html)의 `IPV4/IPV6/INET ADDRESS FAMILIES` 첫 hook 표 중 input/forward/output, `VERDICT STATEMENTS`의 accept/drop 설명 | 어디서 어떤 패킷을 보는지, accept 이후 다른 chain 가능성·drop 종료를 찾음. 중심 질문·K2 | 5분 |

RFC3022는2001년 Informational 문서로 전통적 NAT의 개념 근거다. 모든 현대 NAT의 필터링·할당 정책을 규정하는 최신 표준으로 읽지 않는다. 실습은 NAT 재현이 아니라 INPUT 필터 실험이다.

## 교재와 명령의 구현 근거

| 자료 | 확인할 절·적용 범위 |
| --- | --- |
| [nft 매뉴얼](https://www.netfilter.org/projects/nftables/manpage.html) | OPTIONS의 --check/--file/--handle, TABLES·CHAINS·CONNTRACK EXPRESSIONS·VERDICT/COUNTER. policy.sh의 특정 표 교체·조건/카운터·검증/적용. 전체 ruleset 삭제는 사용하지 않음 |
| [nftables 상태 메타정보](https://wiki.nftables.org/wiki-nftables/index.php/Matching_connection_tracking_stateful_metainformation)의 `ct state`와 상태 설명 | K3의 new/established/related. 추적 메타정보와 허용 규칙 구별 |
| [Compose networks · internal](https://docs.docker.com/reference/compose-file/networks/#internal), [services · cap_add](https://docs.docker.com/reference/compose-file/services/#cap_add) | 외부와 분리된 네트워크 설정과 서버 NET_ADMIN. 호스트 접근까지 모두 차단하는 보안 샌드박스로 확대하지 않음 |
| [Compose up](https://docs.docker.com/reference/cli/docker/compose/up/), [exec](https://docs.docker.com/reference/cli/docker/compose/exec/), [down](https://docs.docker.com/reference/cli/docker/compose/down/) | --build·-d, exec -T, 소유 프로젝트 컨테이너/망 제거. 이미지·다른 프로젝트 제거는 기본 범위가 아님 |
| [Python3.12 http.server](https://docs.python.org/3.12/library/http.server.html#command-line-interface)의 Command-line interface | --bind·--directory·포트8080·로그. 단순 학습용 서버이며 운영 배포용이 아님 |
| [curl 매뉴얼](https://curl.se/docs/manpage.html)의 --noproxy·--connect-timeout·--max-time·EXIT CODES | 새 프로세스 요청·프록시 제외·시간 제한, 오류7/28과 HTTP 응답을 구별. 오류 번호만으로 원인 확정하지 않음 |
| [Alpine 공식 이미지](https://hub.docker.com/_/alpine), [Alpine apk](https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html) | Alpine3.22와 apk add --no-cache로 도구 설치. 실제 패키지 버전은 빌드 시점에 확인 |

## 클라우드 비교와 선택 참고

| 공식 자료 | 범위와 읽을 목적 |
| --- | --- |
| [AWS Security Group](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)의 Security group basics, [SG rules](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html)의 Rule basics | 연결된 자원·허용 규칙 집합·명시 deny 없음. K3 비교표의 근거, 계정 변경 지시가 아님 |
| [AWS NACL](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)의 Network ACL rules, [NACL rule fields](https://docs.aws.amazon.com/vpc/latest/userguide/nacl-rules.html) | 번호순 첫 일치·서브넷 경계·stateless·반환 허용. 필드의 방향/프로토콜/주소/포트 해석 |
| [AWS 연결 추적](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html) | 기존 연결과 규칙 변경·추적 예외의 선택 읽기. 모든 기존 연결이 즉시 종료된다고 일반화하지 않음 |
| [RFC3022 §3.0~3.3](https://www.rfc-editor.org/rfc/rfc3022.html#section-3.0) | 상태·왕복 경로·세션 처리 상세 선택 읽기. NAT 초기 구축·ALG/IDS/IPS 설정은 다루지 않음 |
| [Network Engineer 로드맵](https://roadmap.sh/network-engineer) | Security·NAT 주제 범위 지도. 명령 정확성의 정본은 위 구현 문서 |

## 예제·재사용 경계

확인 기준일은2026-10-17이다. 대응표·숫자·문항·셸 구성은 이 교재의 자체 학습 예다. RFC 그림을 복제하지 않고 원문으로 연결한다. 외부 문서 전체·외부 코드·이미지를 재배포하지 않으며 원문 이용 조건을 따른다. Dockerfile은 공식 이미지를 기반으로 로컬 빌드하며 새 이미지를 외부에 게시하지 않는다. 실제 명령 출력과 참가자의 독립 설명은 각자의 환경에서 확인한다.
