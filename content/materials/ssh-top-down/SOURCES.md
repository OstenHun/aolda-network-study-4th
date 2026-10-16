# SSH 교재의 공식 참고자료

요약: VM·네트워크·SSH 설명을 확인하는 공식 문서다. 사이트의 주소 예시는 실측값과 구분하며 실제 접속 정보는 팀 안내에서 확인한다.

## 공식 기술 자료와 읽을 부분

외부 자료 전체를 참가자의 필수 읽기로 요구하지 않는다. 아래는 진행자가 설명을 확인할 때 사용할 범위다.

| 자료 | 필요한 부분 / 교재 연결 |
| --- | --- |
| [OpenStack Neutron 개념](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html) | Subnets·Ports·Routers·Security groups·Self-service networks. 기본 교재 S2·S5·S6의 연결 자원·정책·Floating IP DNAT |
| [OpenStack 네트워크 생성 안내](https://docs.openstack.org/horizon/latest/user/create-networks.html) | network/subnet/router 선택의 일반 관계. 아올다 Skyline 메뉴와 동일하다고 가정하지 않음 |
| [OpenStack 인스턴스 생성 안내](https://docs.openstack.org/horizon/latest/user/launch-instances.html) | 이미지·Flavor·네트워크·보안 그룹 선택. S1의 자원 역할 |
| [RFC 1918 §3](https://www.rfc-editor.org/rfc/rfc1918.html#section-3) | 10/8 사설 주소 범위. S2·S5의 Floating IP와 공인 IP 구별 |
| [RFC 4632 §3.1](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1) | CIDR의 prefix 길이·/32 한 주소. S2 |
| [iproute2 ss 매뉴얼](https://raw.githubusercontent.com/iproute2/iproute2/main/man/man8/ss.8) | -l·-n·-t와 대기 소켓 조회. S4 |
| [WireGuard 개념·Cryptokey Routing](https://www.wireguard.com/#cryptokey-routing) | UDP 캡슐화, 송신 목적지·수신 출발지와 AllowedIPs. S5 |
| [Microsoft Find-NetRoute](https://learn.microsoft.com/en-us/powershell/module/nettcpip/find-netroute?view=windowsserver2025-ps) | 목적지에 적합한 로컬 주소·경로 조회. S5 |
| [RFC 3022 §2](https://www.rfc-editor.org/rfc/rfc3022.html#section-2) | 주소·포트 변환과 역방향 매핑. 주소 변환·선택 NAT 질문; 아올다 장비 구현 증거는 아님 |
| [RFC 9293 §3.5](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.5) | TCP 연결 수립과 3-way handshake. 주소 변환·선택 NAT 질문 |
| [tcpdump 프로젝트 매뉴얼 소스](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/tcpdump.1.in) | -i·-nn·TCP 출력 형식·flags. 패킷 관찰·선택 NAT 질문. 웹 매뉴얼 페이지 오류로 프로젝트 원본을 확인 |
| [OpenSSH ssh](https://man.openbsd.org/ssh) · [ssh-keygen](https://man.openbsd.org/ssh-keygen) | 호스트 키 검증·사용자 인증, -l 지문 표시. S7 |

## 사이트의 주소 예시

주소와 VM 이름은 설명용 예시다. 본인에게 허용된 주소·계정·인증 방식은 환경 안내에서 확인한다. 비밀번호·개인 키·실제 접속 정보는 공유 답안에 넣지 않는다.
