# 3주차 — IP를 아는데 왜 MAC이 필요할까?

요약: 주소·경로를 복습하고 목적지 IP와 링크의 다음 상대를 함께 탐구한다. 주제별 교재를 찾아 읽고 한 명이 설명한 뒤 조회·제한된 ping·패킷 분석으로 확인한다. 실제 수행과 제공 예제 분석을 구분한다.

## 함께 풀 질문에서 시작하기

**목적지 IP를 아는데 왜 MAC 주소와 ARP가 필요할까?** [함께 찾을 질문](WORKSHEET.md)에서 출발한다. 2주차의 경로 선택과 이번 주의 링크 전달을 연결할 자료를 함께 찾고 한 명이 근거로 설명한다. 다른 사람은 목적지·캐시 조건을 바꾸어 묻고, 설명자는 다음 질문에서 교대한다.

[복습 진단](topics/01-recall.md)에서 같은/다른 서브넷·게이트웨이와 1주차 lo를 짧게 되짚는다. 막히는 항목에 해당하는 교재로 돌아가며 앞선 개념을 이미 숙달했다고 가정하지 않는다.

## 이번 주 읽기와 실습

| 순서 | 자료 | 확인할 것 |
| --- | --- | --- |
| 1 · 질문 | [함께 찾을 질문](WORKSHEET.md) | 중심 질문 하나와 선택 보조 질문 |
| 2 · 공동 탐색 | [LAN·MAC](topics/02-lan-mac.md) → [다음 홉](topics/03-next-hop.md) → [ARP·캐시](topics/04-arp.md) → [ICMP·ping](topics/05-icmp.md) | 질문에 필요한 절과 [공식 출처](SOURCES.md)를 함께 찾아 읽기 |
| 3 · 설명·조건 변경 | [핵심 정리](ESSENTIALS.md) · [함께 찾을 질문](WORKSHEET.md) | 최종 IP 목적지와 링크의 다음 상대를 그림으로 설명하고 같은 링크/게이트웨이 사례 비교 |
| 4 · 직접 확인 | [Linux 실험](LINUX.md) · [실행 절차](../../labs/week-03/LINUX.md) | A 주소·경로·이웃 조회, B 허용 대상 제한된 ping. 프레임·ARP·ICMP는 직접 캡처 또는 제공 trace 분석 |
| 5 · 복습 | [복습 8문항](REVIEW.md) → [분리 해설](ANSWERS.md) | 스스로 답한 뒤 실제 근거·해설과 비교 |

시간과 분량은 [진행자 안내](FACILITATOR.md)를 참고해 조정한다. 함께 찾은 답을 실험으로 확인하며, 선택 활동 때문에 필수 조회·요청을 미루지 않는다.

## 주제 하나만 찾아 읽기

- IP·port, HTTP·SSH, loopback이 헷갈리면 [복습 진단](topics/01-recall.md)과 [1주차](../week-01/index.html)를 읽는다.
- 같은/다른 서브넷 판단이 막히면 [2주차](../week-02/index.html)로 돌아간 뒤 [다음 홉](topics/03-next-hop.md)을 읽는다.
- 프레임의 상대와 최종 서버를 혼동하면 [LAN·MAC](topics/02-lan-mac.md) → [다음 홉](topics/03-next-hop.md)을 읽는다.
- ARP가 안 보이거나 이웃 행이 없으면 [ARP·캐시](topics/04-arp.md)와 [Linux 대안](LINUX.md)을 읽는다.
- ping과 HTTP 결과가 다르면 [ICMP](topics/05-icmp.md)와 [Q7 해설](ANSWERS.md#q7--ping과-http)을 대조한다.

[핵심 정리](ESSENTIALS.md)·[전체 개념 색인](../CONCEPT_INDEX.md)·[외부 참고자료](../INTERVIEW_REFERENCES.md)에서 기억할 개념·혼동·개발 질문을 다시 찾는다. [추가 탐구](EXPLORATIONS.md)는 필수 학습 뒤 선택한다.

## 이번 주 완료 기준과 근거 보관

각자 목적지 IP·선택 인터페이스·다음 홉 IP·알 수 있는 MAC을 표시한 그림을 남긴다. 실제 `ip route get`과 `ip neigh`를 판단 근거로 쓰고, 허용 대상 ping과 ARP/ICMP 직접 관찰 또는 [설명용 trace](../../labs/week-03/sample-trace.txt) 분석을 연결한다. 모르는 MAC은 추정해서 채우지 않는다.

캐시 때문에 새 ARP 요청이 없을 수 있음, ping 실패만으로 HTTP 서버 중지를 단정할 수 없음, loopback은 Ethernet ARP 관찰 대상이 아님을 자기 말로 설명한다. 자신의 경로·이웃을 다시 읽거나 제공 trace를 도움 없이 재분석한다.

명령·출력·패킷은 개인 파일이나 노트에 한 번 보관하고 함께 설명할 때 필요한 근거를 보여 준다. [개인 실습 메모](../../labs/week-03/PERSONAL_RECORD.md)는 필요할 때 참고한다. 직접 실행·시연·제공 분석을 구분하고, 조회·요청을 실행하지 못했다면 직접 수행 보충을 남긴다. 입력 화면을 사용했다면 이동 전에 내려받아 파일을 확인한다.

## 기존 인스턴스를 사용하는 조건

이미 준비된 Linux 인스턴스를 사용한다. 본인의 접속·도구·권한·허용 대상과 통신 조건을 먼저 확인한다. 기본 실험은 NIC·주소·경로·정책·이웃 캐시를 변경하지 않는다. 대상이나 캡처 권한이 없으면 [실행 절차의 대안](../../labs/week-03/LINUX.md)을 따른다.

[실행 키트](../../labs/week-03/README.md) · [진행자 안내](FACILITATOR.md) · [공식 출처](SOURCES.md) · [관찰 범위](VALIDATION.md)를 함께 확인한다. 다음 [4주차](../week-04/index.html)에서는 “IP 패킷이 도착한 뒤 어느 프로그램으로 가는가?”로 이어 간다.
