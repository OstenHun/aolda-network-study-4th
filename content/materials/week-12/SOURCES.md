# 12주차 공식 자료 · 읽을 범위와 목적

요약: 연결 상태·무선 경합·VPN 보호와 정책을 공식 지정 절로 확인한다. 필수 읽기는 공동 탐색 10분 안에 배치하는 추정이며 제품 권고·프로토콜 범위·자체 가공 자료의 한계를 구별한다.

## 공동 탐색에서 읽을 짧은 범위

확인일: 2026-10-17. 아래 **합계 약9분은 추정**이며 기존 공동 탐색10분 안에 포함한다. 전체 문서 읽기나 사전 발표는 요구하지 않는다. 링크가 긴 문서의 위쪽을 열면 지정 제목으로 이동한다.

| 구분·추정 | 실제 읽을 링크·지정 범위 | 찾을 것과 사용할 곳 |
| --- | --- | --- |
| 필수·2분 | [Linux Wireless: Getting link status](https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html#getting-link-status)의 설명·`iw dev wlan0 link`와 바로 다음 출력 한 묶음 | Connected·SSID·freq·signal·tx bitrate. K1/A1의 연결 근거와 서비스 성공을 구별 |
| 필수·4분 | [RFC8325 §6.1](https://www.rfc-editor.org/rfc/rfc8325.html#section-6.1)의 도입과 §6.1.2 DIFS·§6.1.3 CW 첫 세 문단 | 기본 DCF의 고정/무작위 대기·같은 값 선택과 충돌 가능성. K2/A2. SIFS/슬롯 수치 암기는 생략 |
| 필수·3분 | [RFC4301 §4.4.1](https://www.rfc-editor.org/rfc/rfc4301.html#section-4.4.1)의 첫 문단과 같은 절의 ‘Processing Choices: DISCARD, BYPASS, PROTECT’ 제목 바로 아래 첫 문단 | IPsec 경계를 넘는 트래픽의 보호·우회·폐기. 중심 질문/K3에서 터널과 접근 정책 구별. 중간 SPD 선택/순서와 뒤 캐시·관리 상세는 생략 |

`carrier sense`는 매체 사용 감지, `backoff`는 경쟁 시점을 분산하는 대기, `bypass`는 IPsec 보호 없이 통과하는 처리를 뜻한다. 이해가 막히면 [교재 K1~K3](CONCEPTS.md)를 읽고 같은 필드를 다시 찾는다. RFC4301은 IPsec 구조 문서이며 가상 `tun0` 예제를 실제 IPsec 장치 구성으로 제공하는 것은 아니다.

## 교재의 근거와 선택 읽기

여기는 개념을 더 확인할 때 고르는 자료다. 필수9분에 전부 추가하지 않는다.

| 공식 자료 | 확인한 절·주장 | 적용 조건·분량 |
| --- | --- | --- |
| [Cisco AP FAQ](https://www.cisco.com/c/en/us/support/docs/smb/wireless/cisco-small-business-100-series-wireless-access-points/smb5305-wireless-access-points-frequently-asked-questions.html) | 1 What is WAP,3 What is SSID,4 Multiple SSIDs | AP/SSID의 역할과 다중 SSID. 선택3분. 제품별 최대 수·설정 절차는 일반화하지 않음 |
| [Juniper Wi-Fi Mini-PIM](https://www.juniper.net/documentation/us/en/hardware/srx300-srx550-hm/topics/topic-map/srx-series-wifi-mpim.html) | Virtual Access Point Configuration Overview의 첫 문단 | 한 물리 장비/여러 가상 AP·SSID/BSSID 구별의 제품 예. 선택2분, 플랫폼 설치는 제외 |
| [Apple Wi-Fi 권고](https://support.apple.com/en-us/102766) | Security·Hidden network·Bands·Channel·Channel width | WPA3/WPA2-AES·숨김의 한계·2.4/5/6GHz·채널/폭. 선택5분, Apple 제품 운용 권고이며 성능 보장 아님 |
| [Cisco Ethernet collisions](https://www.cisco.com/c/en/us/support/docs/interfaces-modules/port-adapters/12768-eth-collisions.html) | Prerequisites 앞 반이중 주석·What Are Collisions?의 네 단계 | CD·랜덤 대기, 전이중에서 검출 비활성. 선택3분. 오래된 카운터/공유 Ethernet 운용을 현대 전이중 링크에 일반화하지 않음 |
| [Cisco Wireless QoS](https://www.cisco.com/en/US/docs/solutions/Enterprise/Mobility/emob30dg/WANQoS.html) | 802.11 DCF·Random Backoff의 단계·Figure5-4 설명 | 매체가 바쁘면 백오프 중지·재개. 선택4분, 기본 DCF 개요만 채택 |
| [RFC4301 §4.1](https://www.rfc-editor.org/rfc/rfc4301.html#section-4.1) | transport/tunnel mode·안쪽/바깥 IP와 게이트웨이 | 터널 양끝·보호 경계. 선택4분, 실제 VPN 초기 구축은 제외 |
| [RFC4303 §1](https://www.rfc-editor.org/rfc/rfc4303.html#section-1)·[§3.1.2](https://www.rfc-editor.org/rfc/rfc4303.html#section-3.1.2) | §1의 보안 서비스 세 조합·§3.1.2 tunnel mode 헤더/보호 범위 | 터널과 암호화가 동의어가 아님, 구성한 ESP 보호. 선택4분, 협상/암호 상세는 후속 |
| [RFC2784 §2](https://www.rfc-editor.org/rfc/rfc2784.html#section-2) | GRE 캡슐화 구조 | 캡슐화 자체와 암호화 구별의 보조 예. 선택2분, GRE 설치는 하지 않음 |
| [ip-route(8) 매뉴얼](https://man7.org/linux/man-pages/man8/ip-route.8.html) | DESCRIPTION의 ip route get·via·dev·src | 로컬 경로 조회/선택과 실제 송신 구별. 선택3분, 최장 접두사는 7주 교재, 단일 main table 가정은 제공 파일을 따름 |
| [Network Engineer roadmap](https://roadmap.sh/network-engineer) | Wireless·VPN·Network Architectures | 학습 범위 지도, 명령/알고리즘 근거로 쓰지 않음 |

## 제공 자료·문제의 출처와 한계

`wifi-state.txt`·`medium-access.txt`·`vpn-routes.txt`·`design-brief.txt`와 Q1~Q9/D1~D3는 위 개념을 바탕으로 만든 자체 교육 예다. 외부 그림·문항·설정·코드를 복제하지 않았다. 공식 문서의 긴 원문을 재배포하지 않고 필요한 절로 연결한다. RFC는 각각의 발행 시점·업데이트 관계를 가진다. 여기서는 지정 개념을 설명하며 오래된 알고리즘 조합·제품 설정을 보안 기본값으로 권장하지 않는다.

시간·신호·HTTP·DROP/로그는 가공 값이며 실제 학교망·무선 패킷·VPN 측정이 아니다. DCF 모형은 실제 시간·WMM/OFDMA 전체가 아니고 VPN 자료는 특정 제품 설정이 아니다. IPv4 단일 경로표·고정 IP/포트·프록시 없음·암호화/인증의 별도 가정을 유지한다. 실제 Linux/무선·VPN 직접 관찰과 참가자 독립 설명은 각자의 근거로 확인한다.

[실습](LINUX.md) · [복습](REVIEW.md) · [분리 해설](ANSWERS.md)
