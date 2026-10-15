# 2주차 실습 명령의 공식 참고자료

요약: Linux 주소·경로 조회와 Python 주소 계산에 필요한 공식 문서를 연결한다. 선택 격리 실습은 네임스페이스·veth·ping 문서를 참고하며 실제 실행 전 권한·커널 지원·복구 절차를 확인한다.

## 참가자에게 필요한 원문

| 자료 | 읽을 부분과 질문 | 이 키트에서의 역할 |
| --- | --- | --- |
| [ip-address(8)](https://man7.org/linux/man-pages/man8/ip-address.8.html), [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html) | `ip address show`, `-4`, `-brief` 옵션. 인터페이스 주소/접두사를 어디서 보는가? | 실제 Linux 주소 조회 명령의 근거 |
| [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html) | `ip route show`, `ip route get`, `default via` 예제. 경로 조회와 상대 응답이 왜 다른가? | 경로표·선택 경로 판독의 근거 |
| [Python ipaddress](https://docs.python.org/3/library/ipaddress.html) | `IPv4Interface`, `.network`, 네트워크/브로드캐스트/마스크와 멤버십. C1·C2를 검산한다. | 표준 라이브러리 계산. Python의 `is_private`는 RFC 1918 사설망과 뜻이 완전히 같지 않아 키트는 주소 분류에 사용하지 않음 |
| [RFC 1918 §3](https://www.rfc-editor.org/rfc/rfc1918) | `10/8`, `172.16/12`, `192.168/16` 세 사설 범위. 자기 주소가 어느 범위인지 확인한다. | 사설 주소의 정의 |
| [RFC 5737 §3–4](https://www.rfc-editor.org/rfc/rfc5737) | `192.0.2.0/24`의 문서용 지위. 카드 주소를 실제 인터넷 대상으로 해석하지 않는다. | 합성 카드·격리 예제 주소 선택의 근거 |
| [IANA IPv4 특수 용도 등록부](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml) | `127.0.0.0/8`과 문서용 주소의 용도를 확인한다. | 루프백·특수 주소 구분 |

영문 원문을 전부 읽는 과제가 아니다. 2주차에는 주소/접두사·경로 조회·사설/루프백/문서용 주소만 확인한다. 명령 실행 전 자신의 Linux에서 `ip`·Python 사용 가능 여부를 확인한다.

## 선택 격리 실습의 참고자료

| 자료 | 확인한 범위 | 채택 판단 |
| --- | --- | --- |
| [ip-netns(8)](https://man7.org/linux/man-pages/man8/ip-netns.8.html), [network_namespaces(7)](https://man7.org/linux/man-pages/man7/network_namespaces.7.html), [ip-link(8)](https://man7.org/linux/man-pages/man8/ip-link.8.html) | 네임스페이스의 독립 경로표·장치, `ip netns add/exec/del`, veth 링크. | 선택 실습에 직접 사용. Linux 권한과 커널 지원은 현장에서 확인 |
| [iputils ping(8)](https://man7.org/linux/man-pages/man8/ping.8.html) | `-n`, `-c`, `-W`와 종료 상태. | 격리된 두 노드 사이에만 ICMP 한 번씩 보내며 실제 출력은 현장에서 기록 |
| [iproute2 소스 저장소](https://github.com/iproute2/iproute2) | Linux 네트워크 도구의 공식 소스 미러와 GPL-2.0 표시. | 명령 구현을 복제하지 않고 설치된 `ip` 도구를 사용 |

이 실습의 Python·셸 코드, 카드 질문, 합성 출력은 자체 작성했다. 외부 문서·코드의 본문이나 랩 파일을 복제하지 않고 링크와 필요한 읽을 범위만 제공한다. `iproute2`는 GPL-2.0 표시가 있는 별도 도구이며, Python은 [PSF 라이선스](https://docs.python.org/3/license.html)의 별도 표준 라이브러리다. RFC·IANA 원문은 정의와 근거로 인용한 것이지 이 키트의 저작물로 주장하지 않는다.

## 실행 전 확인

[제공 출력](../../labs/week-02/SAMPLE_OUTPUT.md)은 학습용 예시다. 실제 출력은 인터페이스 이름·설정·배포판에 따라 달라질 수 있다. 선택 격리 실습은 허가된 Linux에서 필요한 권한·커널 지원과 생성→변경→복구→정리 절차를 먼저 확인한다. SSH 관리 인터페이스나 기본 경로는 바꾸지 않는다.
