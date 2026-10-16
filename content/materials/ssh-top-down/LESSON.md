# 내 PC에서 내 VM에 접속하기

요약: 프로젝트·망·VM·접속 주소를 준비하고 허용된 계정과 인증 방식으로 SSH 로그인한다. 서버 지문 확인과 사용자 로그인을 구분하고, 성공하면 경로를 설명한 뒤 HTTP 실습으로 이어간다.

## 시작하기 전에

오늘 할 일은 **내 VM을 준비하고, 내 PC에서 접속한 뒤 왜 연결되는지 설명하는 것**이다. 용어를 모두 외운 다음 시작할 필요는 없다. 설정을 하나씩 확인하면서 지금 필요한 개념을 익힌다. 접속에 성공하면 경로를 설명하고 HTTP 실습으로 넘어간다. 오류를 일부러 만들 필요는 없다.

이미 만들어진 망이나 VM을 배정받았다면 설정 확인부터 시작한다. 새 자원이 필요하면 진행자와 프로젝트·사양·할당량을 정한 뒤 만든다. 공유 자원은 변경 권한을 확인한 뒤에만 바꾼다. 참가자별 준비 상황은 [진행자 안내](FACILITATOR.md)에 있다.

[내 기록지](QUESTIONS.md)를 옆에 열어 설정과 실제 출력을 적는다. 아래 주소는 설명용 예시다. 메뉴 이름과 접속 방식은 환경에 따라 다를 수 있다.

<a id="s0"></a>
## S0. 접속에 성공하면 무엇을 할 수 있을까?

내 PC에서 원격 Linux 명령을 실행하려면 무엇이 이어져야 할까?

```text
PC ssh → VPN → 상위 전달 구간 → Floating IP → VM TCP 22
                                            │
                        서버 신원 확인 → 사용자 인증 → 셸
```

PC에서 SSH로 접속한 뒤 입력하는 명령은 원격 Linux에서 실행된다. 화면이 PC에 보인다고 PC의 프로그램을 실행하는 것은 아니다. 셸은 이 명령을 해석하는 프로그램이다.

그림은 이번 테스트망의 논리 경로이며 모든 물리 장비를 관찰한 그림은 아니다. VM Active는 기동, TCP 연결은 포트 도달, SSH 로그인은 계정 인증까지 확인한 결과다. 원격 셸에서 `hostname`·`whoami`를 실행해 대상과 계정을 확인하면 직접 접속의 증거를 남길 수 있다.

> Q0. VM이 Active인 화면과 로그인 후 `hostname`·`whoami` 출력은 각각 무엇을 확인해 줄까?

<figure class="concept"><figcaption>접속할 때 차례로 확인하는 것</figcaption><ol class="diagram"><li><strong>경로와 주소</strong><span>내 PC → VPN → Floating IP → VM</span></li><li><strong>접근 규칙</strong><span>내 VM의 보안 그룹에서 TCP 22 허용</span></li><li><strong>SSH 서버</strong><span>서버 호스트 키 확인 → 내 계정 인증</span></li></ol><p>설정을 이해하기 위한 모형이다. 실제 패킷을 재생하는 화면은 아니다.</p></figure>

<a id="s1"></a>
## S1. 어떤 VM을 쓸지 정하기

이미지·Flavor·네트워크 중 운영체제를 정하는 항목은 무엇일까?

클라우드 화면에서 배정받은 프로젝트를 선택하고 **개요·할당량**을 확인한다. 프로젝트는 누가 어떤 자원을 관리하고 얼마나 쓸 수 있는지 묶는 단위다. IP 주소 범위를 뜻하는 서브넷과는 다르다. 이미지는 운영체제의 바탕, Flavor는 CPU·RAM 사양, 볼륨은 파일을 담을 디스크다. 각각 허용된 항목을 고르고 목록에서 찾기 쉬운 VM 이름을 정한다. 생성 전이라면 기록지에 ‘생성 예정’이라고 적는다.

설명용 구성은 Network-Study 프로젝트의 Ubuntu 26.04, 1 vCPU·2 GiB, 20 GiB VM이다. 본인에게 배정된 사양은 별도로 확인한다. [OpenStack 생성 항목](https://docs.openstack.org/horizon/latest/user/launch-instances.html)

> Q1. 같은 Ubuntu 이미지로 두 VM을 만들면 IP도 같을까? IP는 어느 설정에서 확인해야 할까?

<a id="s2"></a>
## S2. VM이 사용할 네트워크와 주소 범위 정하기

VM에 줄 주소는 어느 범위에 있어야 할까?

Network → Networks에서 사용할 망을 선택한다. 새 망이 필요한 경우 네트워크 생성과 서브넷 설정에서 이름·CIDR·게이트웨이·주소 할당 범위를 정한다. 공동 망이 준비돼 있으면 다시 만들지 않는다. 미사용 여부를 확인하지 않은 주소를 임의로 고르지 않는다.

가상 네트워크는 VM이 연결될 망이고, 서브넷은 주소 범위와 관련 설정이다. IP는 통신에 사용하는 주소다. CIDR은 주소와 접두사 길이로 주소 범위를 나타내는 표기다. IPv4의 /24는 앞 24비트가 같은 범위, /32는 한 주소다. [CIDR 표기](https://www.rfc-editor.org/rfc/rfc4632.html#section-3.1)

설명용 구성의 network-study-lab 서브넷은 `10.0.10.0/24`, 게이트웨이는 `10.0.10.1`이다. 범위는 .0~.255지만 일반 호스트 주소 .1~.254 중에도 게이트웨이·예약·기존 할당 주소는 제외한다. 자신의 설정에서 망·서브넷·범위를 확인한다.

<figure class="concept"><figcaption>주소 한 개와 주소 범위</figcaption><ol class="diagram"><li><strong>내부 IP</strong><span>10.0.10.138 — VM에 할당된 주소</span></li><li><strong>서브넷 /24</strong><span>10.0.10.0 ~ 10.0.10.255</span></li><li><strong>한 주소 /32</strong><span>10.0.10.138 하나만 지정</span></li></ol><p>설명용 주소 표기다. 본인에게 배정된 값은 설정 카드에 따로 적는다.</p></figure>

> Q2. `10.0.10.139`도 포함하는 것은 `10.0.10.138/32`와 위 /24 중 어느 쪽일까?

<a id="s3"></a>
## S3. 다른 망으로 나갈 라우터 연결하기

다른 망으로 보내는 패킷을 VM은 누구에게 넘길까?

Network → Routers에서 사용할 라우터를 선택하거나 허용된 새 라우터를 만든다. 인터페이스 연결에서 실습 서브넷을 연결하고, 외부 게이트웨이 메뉴(Open External Gateway)에서 해당 환경의 provider 네트워크를 선택한다. 설정 항목은 해당 환경의 안내와 대조한다.

라우터 상세 화면에서 실습 서브넷과 외부 네트워크가 연결됐는지 확인한다. 라우터는 망 사이를 연결하고 목적지에 맞는 경로를 고른다. 이 동작이 라우팅이다. VM은 다른 망으로 보낼 패킷을 다음 전달 상대인 게이트웨이로 넘긴다. VM 쪽 게이트웨이와 외부망의 게이트웨이는 서로 다른 위치에 있다.

```text
설명용 구성: VM 10.0.10.138/24 → 실습망 GW 10.0.10.1
              [실습 라우터] → provider망 10.20.0.0/16
              외부 주소 10.20.2.198 / provider GW 10.20.0.1
```

<figure class="concept"><figcaption>같은 라우터의 서로 다른 쪽</figcaption><ol class="diagram"><li><strong>VM 쪽</strong><span>10.0.10.138/24 → GW 10.0.10.1</span></li><li><strong>실습 라우터</strong><span>내부 서브넷과 외부 네트워크 연결</span></li><li><strong>provider 쪽</strong><span>외부 주소 10.20.2.198 → GW 10.20.0.1</span></li></ol><p>설정의 연결 관계를 보여 준다. 라우터 외부 주소는 VM에 연결한 Floating IP와 다르다.</p></figure>

> Q3. 라우터 외부 주소가 곧 VM에 SSH로 접속할 주소일까? VM의 Floating IP는 S5에서 따로 연결한다.

<a id="s4"></a>
## S4. VM을 만들고 콘솔에서 Linux 확인하기

Active가 된 뒤 OS 안에서는 어떤 주소를 볼까?

Compute → Instances에서 허용된 자원·네트워크·보안 그룹을 선택한다. 계정과 인증 방식은 해당 환경의 안내를 따른다. 비밀번호와 개인 키는 기록지에 적지 않는다. 생성 후 상태·실제 IP·연결 망을 대조한다.

기존 VM이라면 생성 단계를 건너뛰고 **Console의 noVNC**에서 Linux에 로그인한다. 아래 명령을 한 줄씩 입력하고 Enter를 누른다. 화면 앞의 `$` 같은 프롬프트는 입력하지 않는다. 클라우드 웹 로그인과 VM 계정 로그인은 별개다.

```bash
hostname
whoami
ip -br addr
ip route
ss -lnt
```

아래 표를 보며 VM과 계정, 내부 주소와 기본 경로, TCP 22의 LISTEN을 찾는다. 본인 기록은 각자 실행한 출력으로 채운다.

| 출력에서 찾을 것 | 확인하는 이유 |
| --- | --- |
| `hostname`의 이름, `whoami`의 계정 | 원하는 VM과 계정인지 접속 대상과 함께 대조한다. |
| `ip -br addr`의 인터페이스와 주소 | 실제 내부 IP를 찾는다. `127.0.0.1`은 VM 자신의 루프백 주소다. |
| `ip route`의 `default via … dev …` | 더 구체적인 경로가 없을 때 사용할 게이트웨이와 인터페이스를 읽는다. |
| `ss -lnt`의 `LISTEN`, `Local Address:Port` | SSH 서버가 TCP 22에서 기다리는지 확인한다. |

`ss`의 `-l`은 대기 중인 소켓, `-n`은 숫자 주소와 포트, `-t`는 TCP를 고른다. TCP 포트는 통신 끝점 번호다. LISTEN은 연결을 기다리는 상태이며 `0.0.0.0:22`는 모든 로컬 IPv4 주소에서 대기한다는 뜻이다. 외부 접근을 허용하는 정책과 다르다. 웹 콘솔은 관리 경로의 화면·키보드를 제공하고 SSH는 VM의 TCP 22에 접속한다. [ss 매뉴얼](https://raw.githubusercontent.com/iproute2/iproute2/main/man/man8/ss.8)

> Q4. 콘솔 로그인과 LISTEN을 확인했어도 PC에서 SSH를 따로 시도해야 하는 이유는 무엇일까?

<a id="s5"></a>
## S5. 접속 주소를 연결하고 PC의 VPN 경로 확인하기

PC에서 쓸 주소와 VM 내부 주소는 같아야 할까?

이번 테스트망에서는 Floating IP를 사용한다. Network → Floating IPs → IP 할당에서 해당 provider 네트워크·서브넷을 선택하고, 발급 주소의 Associate(연결)에서 **자신의 VM과 내부 IP**를 선택한다. 이미 연결됐다면 대상과 상태를 확인한다. 주소 발급과 VM 연결은 별개다.

Floating IP 목록에서 연결된 VM과 내부 IP가 맞는지, 상태가 Active인지 확인한다. 설명용 구성에서는 `10.20.2.88`을 `10.0.10.138`에 연결한다. 둘 다 `10.0.0.0/8` 안의 사설 주소다. Floating IP라는 이름이 공인 인터넷 IP를 뜻하지 않는다. [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html#section-3)

들어온 요청의 목적지를 내부 IP로 바꾸는 것이 DNAT다. 라우팅은 길을 고르고 NAT는 주소를 바꾼다. [OpenStack 설명](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html#self-service-networks)

PC의 본인 VPN을 활성화하고 목적지가 허용된 범위인지 확인한다. Windows PowerShell을 열어 다음 명령을 실행한다. VM 콘솔에 입력하는 명령이 아니다. 아래 `<...>`는 본인 값으로 바꾸는 자리다. 꺾쇠를 그대로 입력하지 않는다.

```powershell
Find-NetRoute -RemoteIPAddress <본인_Floating_IP>
```

출력의 `InterfaceAlias` 또는 인터페이스 번호, 로컬 `IPAddress`, 경로의 `DestinationPrefix`를 기록한다. VPN 인터페이스가 선택됐는지, 내 Floating IP가 그 경로에 포함되는지 확인한다. 설명용 구성의 VPN 인터페이스는 study-vpn, VPN 주소는 10.30.2.4이며 Floating IP로 가는 /32 경로가 있다. 본인 값은 다를 수 있다. [Find-NetRoute](https://learn.microsoft.com/en-us/powershell/module/nettcpip/find-netroute?view=windowsserver2025-ps)

WireGuard의 AllowedIPs는 보낼 패킷의 목적지에 맞는 VPN 상대(peer)를 고르고, 받은 패킷의 출발지를 검사하는 데 쓰인다. OS 경로가 VPN을 선택하는지도 확인한다. 목적지가 빠졌다면 진행자가 확인한 허용 범위에 맞춰 조정한다. PC 설정 추가만으로 상위 전달·허용 정책을 만들지는 않는다. [WireGuard 설명](https://www.wireguard.com/#cryptokey-routing)

<figure class="concept"><figcaption>PC의 경로 선택과 목적지 주소 변환</figcaption><ol class="diagram"><li><strong>내 PC · VPN</strong><span>Floating IP로 갈 경로와 VPN 상대를 선택한다.</span></li><li><strong>Floating IP</strong><span>연결된 VM 내부 IP로 요청의 목적지를 바꾼다.</span></li><li><strong>VM 내부 IP</strong><span>보안 그룹의 허용 조건과 SSH 서비스가 준비돼야 접속할 수 있다.</span></li></ol><p>설정의 역할을 설명하는 모형이다. 라우터와 상위 장비의 실제 배치·NAT 적용 순서를 재현한 그림은 아니다.</p></figure>

> Q5. 내 설정 카드에서 Floating IP, 내부 IP, 게이트웨이를 가리키며 각각의 용도를 설명해 보자.

<a id="s6"></a>
## S6. SSH 접속을 허용하는 규칙 확인하기

어느 출발지의 어떤 접속을 허용해야 할까?

Compute → Instances → VM → Interfaces에서 실제 가상 포트와 연결된 그룹을 확인한다. Network → Security Groups → 해당 그룹 → Rules에서 방향·IP 버전·TCP·목적지 포트·출발지 범위를 대조한다. 필요한 규칙이 없다면 진행자가 확인한 정책에 맞게 준비한다. 이미 맞는 규칙이 있으면 추가하지 않아도 된다. 공유 그룹 수정은 같은 그룹의 다른 VM에도 영향을 줄 수 있다.

| 설정 | 역할 |
| --- | --- |
| Neutron 가상 포트 | VM NIC를 망에 연결하고 IP·MAC·보안 그룹을 연결하는 자원 |
| TCP 목적지 포트 22 | SSH 서버의 통신 끝점 번호 |
| ingress / egress | VM에 들어오는 / 나가는 방향 |
| Remote IP Prefix | 이 ingress 규칙이 적용되는 지점에서 보이는 원격 출발지 주소 범위 |

보안 그룹은 가상 포트의 허용 정책이며 VM 내부 방화벽과 별개다. [Neutron 보안 그룹](https://docs.openstack.org/neutron/latest/admin/intro-os-networking.html#security-groups)

경로에 SNAT가 있으면 정책 적용 지점에서 보이는 출발지 주소가 PC의 주소와 다를 수 있다. 본인 경로의 허용 범위를 확인한다. 공유 NAT의 /32 허용은 주소 하나를 뜻하며 사람 한 명을 인증하지 않는다.

> Q6. 가상 포트 ID, TCP 22, 허용할 출발지 주소는 각각 무엇을 가리킬까?

<a id="s7"></a>
## S7. 서버를 확인하고 내 계정으로 로그인하기

최초 지문 확인은 누구의 신원을 확인하는 과정일까?

PC PowerShell에서 아래 명령의 계정·주소를 본인에게 허용된 값으로 바꿔 실행한다. 환경에 지정된 인증 방식을 사용한다.

```powershell
ssh <본인_계정>@<본인_Floating_IP>
```

처음 접속하는 서버라면 키 종류와 지문을 보여 주며 신뢰할지 묻는다. 호스트 키는 서버의 신원을 확인하는 키다. 화면의 지문을 해당 VM의 웹 콘솔에서 별도로 조회한 공개 키 지문과 대조한다. ED25519 키라면 VM 콘솔에서 다음 명령을 실행한다.

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

두 화면의 키 종류와 `SHA256:…` 지문을 신뢰할 수 있는 경로로 대조한 뒤 최초 등록 여부를 판단한다. 다르면 변경 이유를 먼저 확인한다. 이어 환경에 지정된 비밀번호 또는 키로 사용자 인증을 진행한다. 비밀번호 입력 중 글자나 별표가 보이지 않을 수 있다. 호스트 키는 서버 신원을 확인하고 계정 인증은 사용자 로그인을 확인한다. [OpenSSH](https://man.openbsd.org/ssh) · [지문 조회](https://man.openbsd.org/ssh-keygen)

접속했다면 원격 셸에서 `hostname`, `whoami`, `pwd`를 실행해 실제 결과를 남기고 S8로 간다. 각자 실행한 결과를 기록하고, 진행자나 짝의 결과와 구분한다.

### 접속이 막혔다면

아래에서 현재 증상에 해당하는 항목을 확인한다. 정상 접속한 사람은 진단을 수행하지 않아도 된다.

| 증상 | 다음 확인 | 이 증상만으로 확정하지 않을 것 |
| --- | --- | --- |
| 시간 초과 | 대상 주소·PC 경로·실제 그룹·VM LISTEN, 필요하면 콘솔 캡처 | 모두 NAT 문제라는 결론 |
| Connection refused | 대상·포트·리스너·거부 정책 | 비밀번호 오류라는 결론 |
| 호스트 키 검증 실패 | 기존 등록과 콘솔 키·VM 변경 이력 | TCP가 처음부터 연결되지 않았다는 결론 |
| Permission denied | 허용된 계정·인증 수단·서버 정책·인증 로그 | VPN 재설정이 필요하다는 결론 |

`Permission denied (publickey)`로 끝나면 허용된 계정·키·서버 인증 정책을 확인한다. 비밀번호 방식으로 안내받았는데 프롬프트가 나오지 않는다면 관리자와 설정을 확인한다. 콘솔 로그인 성공만으로 SSH 인증이 허용됐다고 단정하지 않는다.

시간 초과는 경로·정책·서비스를 나누어 확인한다. 패킷이 보이지 않을 때는 캡처 위치·시점·필터의 한계도 고려한다.

<figure class="concept"><figcaption>접속 허용과 인증은 각각 확인한다</figcaption><ol class="diagram"><li><strong>보안 그룹</strong><span>어떤 출발지에서 TCP 22로 들어올 수 있는가?</span></li><li><strong>서버 호스트 키</strong><span>지금 연결한 서버가 내가 접속하려던 서버인가?</span></li><li><strong>사용자 인증</strong><span>이 계정으로 로그인할 자격이 있는가?</span></li></ol><p>주소를 허용하는 규칙만으로 사용자가 인증되지는 않는다.</p></figure>

> Q7. TCP 연결, 서버 호스트 키 확인, 사용자 인증은 각각 무엇을 확인하는 과정일까?

<a id="s8"></a>
## S8. 내가 접속한 경로 설명하기

PC 목적지와 VM 내부 주소가 왜 다를 수 있을까?

질문지의 주소 표를 실제 설정·조회값으로 채운다. src는 보내는 쪽, dst는 받는 쪽이다. TCP에는 양쪽 IP·포트가 있고 응답에서는 방향이 바뀐다. 클라이언트 임시 포트는 실행마다 달라질 수 있다.

```text
본인 PC의 선택 경로·출발지 → VPN → 본인 Floating IP:22
                                       │ 목적지 주소 변환
                                   본인 VM 내부 IP:22
```

이 그림은 설정을 보고 설명한 경로다. 캡처하지 않았다면 VM이 본 src·임시 포트는 미관찰로 남긴다. 성공한 상태에서도 원하면 콘솔에서 새 SSH 연결을 캡처할 수 있지만 오늘 기본 완료 조건은 아니다. SNAT는 [선택 질문 해설](FACILITATOR.md#nat-answers)에서 더 살펴본다.

> Q8. 지금 로그인에 성공했다면 다른 사람의 접속이나 다른 포트의 서비스도 된다고 말할 수 있을까?

<a id="s9"></a>
## S9. 창 두 개를 열고 실습 파일 보내기

PC의 Python 파일은 원격 VM에도 있을까?

HTTP 실습에서는 한 셸에 서버를 켜 두고 다른 셸에서 요청한다. PC에서 PowerShell 창을 하나 더 열어 같은 SSH 명령으로 접속한다. 두 창의 접속 대상과 `hostname`, `whoami`를 대조한다. 같은 VM에 접속해도 현재 폴더는 셸마다 따로 관리된다.

VM에서 먼저 `cd ~`로 홈 폴더로 이동하고 `mkdir -p labs/week-01`로 실습 폴더를 준비한다. 기존 `server.py`가 있다면 덮어쓰기 전에 확인한다.

이제 **SSH에 접속하지 않은 PC PowerShell 창**에서 프로젝트 폴더로 이동한 뒤 파일을 보낸다. 그 폴더 아래에 `labs/week-01/server.py`가 있어야 한다.

```powershell
scp ./labs/week-01/server.py <본인_계정>@<본인_Floating_IP>:labs/week-01/server.py
```

scp에서 앞의 경로는 PC 파일, `계정@주소:` 뒤는 VM 계정의 홈을 기준으로 한 경로다. HTML만 받았다면 [server.py](../../labs/week-01/server.py)를 내려받고, PC에서 파일이 있는 위치에 맞춰 scp의 첫 경로를 바꾼다.

VM에서 `ls -l ~/labs/week-01/server.py`, `python3 --version`, `curl --version`을 확인한다. 두 셸 모두 `cd ~`로 시작 위치를 맞춘다. 파일이 없다는 오류가 나오면 전달 여부와 경로를 확인하고, 도구가 없다면 진행자와 준비한다.

> Q9. 두 창이 같은 VM에 연결됐는지, 보낸 파일이 어디에 있는지 어떤 출력으로 확인했을까?

<a id="s10"></a>
## S10. 같은 VM 안에서 HTTP 네 상태 비교하기

SSH로 들어간 뒤 curl을 실행하면 127.0.0.1은 어디를 가리킬까?

[기존 Linux 안내 1~4단계](../../labs/week-01/LINUX.md#1-서버-시작--셸-a)를 따른다. A에서 Python 서버를 켜 둔 채 B에서 curl을 실행한다. 실행할 명령과 기록 양식은 연결된 자료를 그대로 사용한다.

| 조건 | 코드에 따른 기대 — 실제 수행 후 대조 |
| --- | --- |
| 실행 중 /echo?message=hello | 200·본문·서버 response 로그 |
| 실행 중 /missing | 404·오류 본문·response 로그 |
| 자기 서버 중지 후 같은 요청 | HTTP 응답 없음·연결 오류 |
| 같은 포트로 재시작 | 정상 요청에 다시 200 |

```text
PC SSH 창 ── TCP 22 ──> VM 셸 A / 셸 B
                           │       │
                        Python ← curl
                      VM 내부 lo, TCP 8080
```

서버는 `127.0.0.1:8080`에서 기다린다. 서버와 curl이 모두 VM에서 실행되므로 여기서 `127.0.0.1`은 VM 자신이다. HTTP는 VM 내부에서 오가므로 외부 8080 규칙이 필요하지 않다. PC에 표시되는 글자는 SSH가 전달한다. HTTP 패킷은 VM lo에서 관찰하며 외부 SSH 캡처와 다르다.

> Q10. 404는 서버에 연결하지 못한 결과일까? PC에서 curl을 실행하면 `127.0.0.1`은 어디를 가리킬까?

네 상태의 예상·명령·양쪽 출력과 패킷 근거는 [1주차 개인 실습 기록](../week-01-prestudy.html)에 남기고, 원출력·pcap은 별도 파일로 보관한다. [팀활동](../week-01/WORKSHEET.md)에는 함께 다룬 질문·근거 위치·바뀐 설명을 짧게 적는다. 시간이 부족하면 실제로 끝낸 항목까지만 기록하고 나머지를 보충한다.

## 사이트의 주소 예시

주소와 VM 이름은 설명용 예시다. 본인에게 허용된 주소·계정·인증 방식은 환경 안내에서 확인한다. 비밀번호·개인 키·실제 접속 정보는 공유 답안에 넣지 않는다.
