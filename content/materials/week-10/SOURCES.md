# 공식 출처 · 필요한 문단만 찾아 읽기

요약: OSPF의 연결 정보·이웃·경로 계산, DV 갱신식과 BGP 정책을 공식 본문에서 대조한다. 참가자 필수 읽기는 짧은 지정 범위이며 FRR·Docker 명령 근거와 선택 심화를 구별한다.

확인 기준일: 2026-10-17. RFC 원문의 표준 조건과 FRR 10.5 계열 구현 문서를 구별한다. 실습 이미지는10.5.1이다. RFC의 후속 갱신 전체·모든 구현의 동작을 검토했다는 뜻은 아니다. 아래는 이 교재에 적용한 절과 범위다.

<span id="required"></span>
## 참가자 필수 지정 읽기

전체 RFC를 읽을 필요는 없다. 먼저 [교재](CONCEPTS.md)의 용어·그림을 읽고 다음 범위를 함께 찾는다. 합계 약10~15분은 추정이며 영어 읽기 속도에 따라 다르다. 현재 공동학습 시간 안에 배치하고, 어려우면 진행자가 교재와 대조하며 범위를 짚어 준다.

| 자료와 정확한 시작·끝 | 읽는 목적·함께 찾을 것 |
| --- | --- |
| [RFC 2328 §1.1 Protocol overview](https://www.rfc-editor.org/rfc/rfc2328.html#section-1.1)의 `In a link-state routing protocol`로 시작해 `by flooding`으로 끝나는 문단, 이어 `All routers run`으로 시작해 `as leaves`로 끝나는 문단 | 연결 정보를 누가 알리고 누가 계산하는가. 페이지 머리말이 문단 사이에 끼어 있어도 이어 읽는다. 교재 W10-K1·Q4 |
| [RFC 2328 §7.1 The Hello Protocol](https://www.rfc-editor.org/rfc/rfc2328.html#section-7.1)의 첫 문단, [§10.1 Neighbor states](https://www.rfc-editor.org/rfc/rfc2328.html#section-10.1)의 `Full` 항목 | Hello의 양방향 이웃 유지와 Full의 인접 상태. §7.1 첫 문단의 DR 언급은 이번 point-to-point 실습에서 다루지 않음. W10-K2·A1·Q5 |
| [RFC 2453 §3.4 Distance Vector Algorithms](https://www.rfc-editor.org/rfc/rfc2453.html#section-3.4)에서 `Let D(i,j)`로 시작하는 정의·두 식과, `It turns out`으로 시작해 `picks the smallest`로 끝나는 문단 | 이웃의 광고값+이웃까지 비용에서 최소를 고르는 이유. 중간의 간단한 증명 설명은 함께 읽어도 됨. W10-K1·Q3 |

링크가 절 처음으로 이동하지 않으면 문서 안에서 위 영문 시작 구절을 찾는다. 영어 용어 대응은 topology=연결 구조, flooding=정보를 이웃으로 계속 전파, neighbor=이웃, metric=경로 비용, convergence=변화 뒤 안정 과정이다. 식을 읽기 전에 모든 용어를 외우지 않아도 된다.

## 교재와 명령의 근거

| 공식 문서·실제로 적용한 범위 | 이 교재에서 확인하는 주장 |
| --- | --- |
| [RFC 2328 §2.2](https://www.rfc-editor.org/rfc/rfc2328.html#section-2.2) 첫 두 문단, [§16.1](https://www.rfc-editor.org/rfc/rfc2328.html#section-16.1)의 후보 선택·비용 갱신 단계 | 자신을 루트로 경로 계산, 전달에는 다음 홉 사용. 자체 4노드 그림/값은 원문 복제가 아님 |
| [RFC 2328 §1.2](https://www.rfc-editor.org/rfc/rfc2328.html#section-1.2)의 AS·Router ID·area 관련 정의, §1.1·§7.1·§10.1 | AS 내부·영역·이웃/인접/Full·수렴의 역할. LSA 필드 전체는 필수 읽기에서 제외 |
| [RFC 4271 §1.1](https://www.rfc-editor.org/rfc/rfc4271.html#section-1.1)의 AS·EBGP/IBGP·IGP 정의, [§3](https://www.rfc-editor.org/rfc/rfc4271.html#section-3)의 첫 두 문단, [§9.1.1](https://www.rfc-editor.org/rfc/rfc4271.html#section-9.1.1)의 선호도 정책, [§9.1.3](https://www.rfc-editor.org/rfc/rfc4271.html#section-9.1.3)의 외부 광고 정책 | 도달 정보·AS 경로·선택/광고 정책. P/Q와 AS65001은 자체 예시이며 AS 경로 길이만으로 선택한다고 설명하지 않음 |
| [FRR 10.5 OSPFv2](https://docs.frrouting.org/en/stable-10.5/ospfd.html)의 OSPF Configuration·OSPF router·OSPF interface·Showing Information | router-id, area, point-to-point, cost, passive, Hello/Dead, neighbor/interface/database 조회. 명령은 제공10.5.1 이미지에서 확인하는 구성에 적용 |
| [FRR Basic Setup](https://docs.frrouting.org/en/stable-10.5/setup.html#daemons-configuration-file), [VTYSH](https://docs.frrouting.org/en/stable-10.5/vtysh.html), [Zebra Standard Commands](https://docs.frrouting.org/en/stable-10.5/zebra.html#standard-commands) | 데몬·통합 구성·vtysh 실행과 interface shutdown/no shutdown. 새 컨테이너에서만 실행 |
| [Docker Compose services의 networks/interface_name](https://docs.docker.com/reference/compose-file/services/#interface_name), [bridge driver options](https://docs.docker.com/engine/network/drivers/bridge/#options), [Compose down](https://docs.docker.com/reference/cli/docker/compose/down/) | Compose2.36 이상에서 NIC 이름 지정, 브리지 NAT 끄기, 본인 프로젝트 정리. 호스트 전체 네트워크 변경 명령은 제공하지 않음 |
| [FRR 공식 컨테이너 제작 경로](https://github.com/FRRouting/frr/tree/frr-10.5.1/docker/alpine) | 배포 이미지의 시작 방식. 이 교재는 소스 빌드·새 외부 코드를 복사하지 않고 공식 이미지를 사용 |

## 선택 읽기와 범위 지도

- [RFC 2328 §13·§16.1](https://www.rfc-editor.org/rfc/rfc2328.html#section-13): 신뢰성 있는 LSA 전달·계산 상세. 필수는 링크 전환과 출력의 연결이다.
- [RFC 4271 §3·§9](https://www.rfc-editor.org/rfc/rfc4271.html#section-9): BGP 정책·결정 과정. 필수는 AS 내부/간 역할·정책 예의 설명이며 BGP 설정은 선택이다.
- [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer): 학습 범위 지도. 이번에는 Routing Protocols 주제를 연결하며 명령/정답의 표준 근거로 쓰지 않는다.

## 예제와 재사용

4노드 그래프·계산·정책 사례·질문/해설·실습 구성은 자체 학습 자료다. 실제 인터넷 경로·기업 기출·참가자 수행 결과로 제시하지 않는다. 긴 원문·그림·문제집·외부 코드를 복제하지 않고 필요한 절을 연결했다. 원문의 이용 조건은 각 RFC 고지와 공식 문서·FRR 저장소의 라이선스를 따른다. 공식 이미지 실행과 이미지 자체의 재배포는 구별한다.

[학습 홈](README.md) · [진행자 안내](FACILITATOR.md) · [개념 색인](../CONCEPT_INDEX.md).

<a download href="SOURCES.md">출처 안내 원문 내려받기</a>
