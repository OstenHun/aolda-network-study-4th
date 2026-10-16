# 5주차 · 공식 출처와 관찰 범위

요약: DNS 역할·레코드·TTL, DHCPv4 초기 임대·옵션과 dig·curl·설정 조회의 공식 근거를 안내한다. 지정 절만 선별해 읽고 자체 예제와 실제 관찰을 구별한다.

## 함께 읽을 공식 절

확인일은 2026-10-16이다. RFC는 이후 갱신이 있는 표준 문서이며 여기서는 아래의 기초 역할·필드·절차만 채택한다. 긴 원문이나 외부 그림·코드를 복제하지 않고 설명·질문·필드 trace를 자체 작성했다.

| 자료 | 읽을 절·채택 범위 |
| --- | --- |
| [RFC 1034](https://www.rfc-editor.org/rfc/rfc1034.html) | §3.6 레코드와 TTL, §4.3.1 질의/응답·재귀, §5.3.2 캐시, §5.3.3 리졸버 알고리즘 |
| [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035.html) | §3.4.1 A, §4.1 메시지 플래그·응답 코드, §4.2 UDP/TCP 전송. 전체 DNS 구현 과제는 제외 |
| [RFC 3596](https://www.rfc-editor.org/rfc/rfc3596.html#section-2) | §2 AAAA의 IPv6 주소. IPv6 경로/자동 설정은 이번 범위 밖 |
| [RFC 2131](https://www.rfc-editor.org/rfc/rfc2131.html) | §3.1 Figure 3 초기 할당, §4.1 포트·전달, §4.4.5 갱신·T1/T2·만료 |
| [RFC 2132](https://www.rfc-editor.org/rfc/rfc2132.html) | §3.3 mask, §3.5 router, §3.8 DNS server, §9.2 lease time. 전체 옵션 암기는 제외 |
| [BIND 9 dig 매뉴얼](https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility) | 기본 질의, 형식 선택, +time/+tries, 응답 섹션·SERVER. 설치된 버전의 도움말도 확인 |
| [curl 매뉴얼](https://curl.se/docs/manpage.html) | --resolve, --noproxy, --ipv4, --connect-timeout, --max-time, --write-out, 종료 코드. 사용 중인 버전에서 지원 여부 확인 |
| [RFC 9110 §7.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-7.2) · [RFC 6066 §3](https://www.rfc-editor.org/rfc/rfc6066.html#section-3) | HTTP Host와 TLS SNI의 이름 조건. 인증서 검증의 세부는 다음 주에 연결 |
| [systemd resolvectl](https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html) · [공식 문서 원문](https://github.com/systemd/systemd/blob/main/man/resolvectl.xml) | status의 링크별 DNS 조회. systemd-resolved 사용 환경에만 적용 |
| [NetworkManager nmcli](https://networkmanager.dev/docs/api/latest/nmcli.html) | device show·필드 선택을 통한 적용 설정 조회. 모든 Linux에 있다고 가정하지 않음 |
| [Python http.server](https://docs.python.org/3/library/http.server.html) · [socketserver](https://docs.python.org/3/library/socketserver.html) | BaseHTTPRequestHandler의 GET·응답·헤더, HTTPServer·handle_request·timeout·컨텍스트 종료. 학습용 루프백 서버에 한정 |
| [roadmap.sh Network Engineer](https://roadmap.sh/network-engineer) | DNS·DHCP·Core Protocols 범위 지도. 상세 기술 판단은 위 공식 문서와 실제 출력 사용 |

## 자체 자료와 실측의 경계

- `api.example`, 192.0.2.0/24, 2001:db8::/32와 TTL 표·DORA trace는 설명용 가공 예제다. 실제 서버 주소·캡처가 아니다.
- `lab.test`·루프백 HTTP 서버는 DNS 조회를 우회해 Host 비교를 하는 자체 실험이다. 외부 라이브러리나 실제 DNS/DHCP 서버 코드를 사용하지 않는다.
- `example.com`의 실제 질의·서비스 응답은 실행할 때 관찰한다. 제공 예제의 값으로 본인 결과를 채우지 않는다. HTTPS 신원 확인의 세부는 다음 주에 다룬다.
- WireSalmon·Wireshark는 선택 분석 도구다. 직접 캡처·제공 파일·본문 가공 trace는 서로 다른 근거다.

[교재](CONCEPTS.md) · [실습](LINUX.md) · [복습](REVIEW.md) · [학습 홈](README.md).
