# 3주차 개념 출처와 검증 범위

요약: LAN·Ethernet·ARP·ICMP의 설명을 원문 절과 연결한다. 주소·출력은 설명용 예시이며 본인 실습의 관찰 근거와 구분한다.

## 확인한 공개 원문

아래 표에서 해당 원문의 절과 페이지를 확인한다. 외부 자료는 근거와 추가 관찰 질문으로 사용했고, 문장·그림·문항은 스터디용으로 새로 작성했다.

| 자료 | 확인 위치 | 이 교재에서 뒷받침하는 내용과 한계 |
| --- | --- | --- |
| [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer) | 공개 로드맵 입구 | 전체 학습 범위의 기준. 웹 텍스트 화면에는 세부 노드가 노출되지 않아 3주차 프로토콜의 직접 근거로 쓰지 않았다. 주차 범위는 [커리큘럼](../../CURRICULUM.md#week-03)이 정한다. |
| [RFC 826](https://www.rfc-editor.org/rfc/rfc826) | “Packet Generation”, “Packet Reception”, “An Example” | 경로가 다음 홉·링크를 정한 뒤 주소 대응을 찾고, 없으면 ARP 요청을 브로드캐스트하며 응답으로 MAC 대응을 얻는 흐름. 원문은 역사적 Ethernet 사례이며 현재 VM 캡처의 증거가 아니다. |
| [RFC 792](https://www.rfc-editor.org/rfc/rfc792) | p.1 “Introduction”, pp.4–5 “Destination Unreachable Message”, pp.14–15 “Echo or Echo Reply Message” | ICMP의 역할·오류·IPv4 Echo Type 8/0. RFC도 전달이나 오류 반환을 보장하지 않는다고 명시한다. |
| [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) | “ip route get” | 목적지 한 건에 대해 커널이 보는 경로를 출력한다는 명령 근거. 본문의 `via`·`dev` 출력은 설명용이다. |
| [ip-neighbour(8)](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html) | DESCRIPTION, “ip neighbour show”, NUD states | IPv4 이웃 표와 링크 주소의 대응 및 `REACHABLE`·`STALE`·`INCOMPLETE`·`FAILED` 상태. 실습에서는 실행 전후의 상태를 비교한다. |
| [ping(8)](https://man7.org/linux/man-pages/man8/ping.8.html) | DESCRIPTION, OPTIONS `-4`, `-c` | Linux `ping`의 ICMP Echo 사용과 IPv4·횟수 제한 명령의 근거.  |
| [Kurose·Ross Wireshark Ethernet and ARP v9](https://www-net.cs.umass.edu/wireshark-labs/Wireshark_Ethernet_ARP_v9.pdf) | pp.1–3 Ethernet 프레임·게이트웨이 MAC 질문, pp.4–7 ARP 캐시·요청·응답 질문 | 프레임의 목적지 MAC과 최종 서버 구분, 캐시 때문에 요청이 새로 보이지 않을 수 있음, 제공된 패킷 예제 대체 경로. 원문 실습의 라이브 캡처를 수행했다는 뜻은 아니다. |
| [Kurose·Ross Wireshark ICMP v8.0](https://www-net.cs.umass.edu/wireshark-labs/Wireshark_ICMP_v8.0.pdf) | pp.1–4 “ICMP and Ping” | Echo 요청·응답의 패킷 관찰과 Type 질문. 원문의 Windows 명령은 Linux 명령으로 그대로 옮기지 않았다. |
| [RFC 5737 §3](https://www.rfc-editor.org/rfc/rfc5737#section-3) | Documentation Address Blocks | `192.0.2.0/24`, `198.51.100.0/24`가 문서 예시용임을 확인. 실제 접속 주소로 쓰지 않는다. |
| [RFC 4861 §7](https://www.rfc-editor.org/rfc/rfc4861#section-7) | Address Resolution | IPv6의 이웃 주소 탐색이 NDP 영역이라는 범위 구분에만 사용. 이번 교재는 IPv4 Ethernet에 한정한다. |

## 자료와 실제 관찰의 경계

개념 교재의 MAC·IP·인터페이스 이름·명령 출력·그림은 설명용 예시다. loopback에서 본 HTTP 패킷은 Ethernet ARP 관찰 결과가 아니다. [관찰 범위와 한계](VALIDATION.md)를 참고한다.

실습에서 근거를 얻을 때는 실제 인터페이스·허용된 목적지와 캡처 위치를 먼저 기록한다. 자기 VM 가상 NIC의 캡처로 물리 호스트 전체 패브릭을 보았다고 해석하지 않는다. 캐시 때문에 새 ARP가 안 보일 수 있고, ICMP 응답 여부만으로 HTTP 서비스 상태를 단정하지 않는다. 직접 캡처가 불가하면 자체 제작한 [설명용 가상 패킷 예제](../../labs/week-03/sample-trace.txt) 분석으로 개념을 확인하되 본인 VM 실행으로 기록하지 않는다. 대학 실습 PDF는 질문·관찰 방식의 참고이며 이 가상 패킷 예제를 캡처한 원본은 아니다.

## 핵심 정리와 개발 질문의 근거

[핵심 정리](ESSENTIALS.md)는 기존 교재와 공식 원문을 연결한 자체 설명이며 개발 사례·해설은 스터디 자체 작성이다. [공개 저장소·공식 문서 선정 기록](../INTERVIEW_REFERENCES.md)에 읽은 절·채택 범위·보류 이유를 정리했다. 회사별 실제 면접 출제·빈도는 확인하지 않았다.
