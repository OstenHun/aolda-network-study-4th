# 링크·VLAN·STP·LACP 교재

요약: 스위치는 출발지 MAC을 배우고 VLAN 안에서 프레임을 전달한다. STP는 루프 없는 경로를, LACP는 여러 멤버의 논리 링크를 만든다. 오류 검출 성공도 무오류·인증을 보장하지 않는다.

[개인 공부 정리](README.md#personal-notes)에서는 이 교재의 핵심·혼동 구별을 주요 질문과 내 답에 연결한다. 먼저 설명하고 해설과 비교한 뒤, 확인한 근거와 고친 이해를 기존 개인 노트에 보완한다.

<span id="mac-vlan"></span>
## W09-K1 · MAC을 배우는 범위와 VLAN

**기억 문장: 스위치는 들어온 프레임의 출발지 MAC과 입력 포트를 배우고, 목적지 MAC으로 출력 포트를 고른다.** MAC 테이블(FDB)은 전달 위치를 기억한다. [3주차](../week-03/arp.html)의 ARP 캐시는 IP→MAC 대응이며 역할이 다르다.

| 수신한 프레임 | 일반적인 학습 스위치의 판단 |
| --- | --- |
| 출발지 A, 목적지 B를 모름 | A의 입력 포트를 학습하고, 같은 VLAN의 전달 가능한 다른 포트로 flood |
| 목적지 B의 위치를 앎 | 그 포트로 unicast. 목적지 포트가 입력 포트와 같으면 다른 포트로 내보내지 않음 |
| 목적지가 broadcast | 같은 VLAN의 전달 가능한 다른 포트로 flood. 출발지 학습은 별도로 일어남 |

flood는 복제 전달이며 모든 망으로 보내는 뜻이 아니다. 차단된 포트·VLAN 허용 목록·입력 포트를 고려한다. MAC 위치는 이동·시간 경과·토폴로지 변화로 바뀔 수 있어 영구 정답이 아니다. 모르는 목적지 unicast와 broadcast는 이번 예제에서 출력 범위가 비슷해도 목적지 주소가 다르다. 근거: [Kurose/Ross 6.4](https://gaia.cs.umass.edu/kurose_ross/videos/6/)의 스위치 학습·전달 부분.

### VLAN과 포트

VLAN은 L2 브로드캐스트 영역을 논리적으로 나눈다. 일반적인 access 포트는 단말의 태그 없는 프레임을 지정 VLAN으로 분류한다. trunk는 여러 VLAN을 한 링크로 운반하며 802.1Q 태그로 소속을 식별한다. 실제 장비에는 native VLAN 등 태그 없는 트래픽의 예외가 있으므로 “trunk는 언제나 모든 프레임에 태그”라고 외우지 않는다. 허용 목록에 없는 VLAN은 그 trunk를 통과하지 못할 수 있다. [Cisco access/trunk](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus5000/sw/layer2/503_n1_1/Cisco_n5k_layer2_config_gd_rel_503_N1_1_chapter6.html)의 지정 절이 근거다.

```text
A -- access VLAN10 -- S2 == trunk 10,20 == S3 -- access VLAN10 -- B
                                            +-- access VLAN20 -- C
```

그림의 A/B는 VLAN10 안에서 L2 전달할 수 있고 C는 VLAN20에 있다. VLAN 간 IP 통신에는 적절한 주소 설계·게이트웨이·L3 라우팅과 허용 정책이 필요하다. trunk만 추가하면 VLAN 간 라우팅도 생긴다는 설명은 틀리다. 같은 `/24`를 분리된 두 VLAN에 넣어도 ARP가 경계를 저절로 넘지 않는다. 같은 VLAN 역시 케이블·STP·정책·종단 설정까지 항상 정상이라는 보장은 아니다. 이번 구성은 라우터가 없으며 VLAN 간 통신을 제공하지 않는다.

<span id="stp"></span>
## W09-K2 · STP는 중복 경로에서 루프를 막는다

**기억 문장: 물리적으로 중복 연결되어 있어도 수렴한 STP의 데이터 전달 경로는 루프가 없도록 제한된다.** Ethernet 데이터 프레임에는 IP TTL처럼 순환 때마다 줄어드는 필드가 없다. 루프가 있으면 broadcast·모르는 목적지 프레임의 복제와 MAC 위치 변동이 망을 방해할 수 있다.

STP는 BPDU라는 제어 메시지의 정보를 비교한다. 기본적으로 가장 작은 Bridge ID가 루트가 된다. Bridge ID에는 우선순위와 MAC 등 식별 정보가 들어간다. 루트가 아닌 스위치는 루트로 가는 최선 경로의 root port를 고르고, 각 세그먼트에는 designated port를 정한다. 동률에는 추가 비교 규칙이 있다. 이번에는 순위 S1<S2<S3, 모든 trunk 비용1인 예만 사용한다. 세부 선출 문제는 선택이다.

```text
             S1 (root)
        l12 /         \ l13
           S2---------S3
                 l23
```

| 스위치/포트 | 기본 수렴 후 역할·데이터 상태 |
| --- | --- |
| S1/l12, S1/l13 | designated / forwarding |
| S2/l12, S3/l13 | root / forwarding |
| S2/l23 | designated / forwarding |
| S3/l23 | 비지정 차단 / blocked |

l23는 케이블 불량이 아니라 한쪽 끝의 데이터 전달이 차단된 중복 경로다. S1–S3의 l13을 끊으면 S3는 S2를 거쳐 루트에 도달하고 S3/l23가 root/forwarding이 될 수 있다. 복구하면 원래 경로를 다시 선택한다. 루트가 모든 데이터 프레임의 필수 경유지라는 뜻은 아니다.

포트 **역할**과 **상태**를 구별한다. 전통 STP에는 blocking/listening/learning/forwarding 등이 있고, RSTP는 역할·상태 표현과 전환 방식이 다르다. 실습의 `blocked`는 수렴 후 데이터 차단을 표현한 이름이며 장비의 모든 상태를 구현하지 않는다. 실제 전환 중 손실과 대기가 생길 수 있다. 근거: [Cisco STP](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/lan-wan/lan-wan/m_lsw-span-tree-prot.html)의 포트 상태·루트 부분.

<span id="lacp"></span>
## W09-K3 · LACP 묶음과 흐름 분산

**기억 문장: 집성은 여러 물리 멤버를 논리 링크 하나로 다루며, 흐름 기반 분산에서 한 연결이 모든 멤버 대역폭을 합쳐 쓰지는 않는다.** LACP는 양 끝이 집성에 참여할 수 있는지 제어 정보를 교환하는 프로토콜이다. static 집성이나 active-backup과 같은 말이 아니다.

```text
                    +-- m1 --+
A -- S1 -- po1 -----+        +----- po1 -- S2 -- B
                    +-- m2 --+
        STP에는 논리 포트 po1, 전송에는 선택된 멤버
```

호환되는 active/active 또는 active/passive는 협상을 시작할 수 있다. passive/passive는 서로 기다려 묶음을 만들지 못한다. 속도·duplex·집성 상대·구성 호환성도 필요하다. 양쪽 설정·선택 멤버·collecting/distributing(수신/송신 참여)을 확인해야 한다. 물리 carrier가 up이라는 사실만으로 집성 참여를 보장하지 않는다. 최소 멤버 수(min-links)에 따라 한 멤버만 남은 묶음도 내려갈 수 있다. [Cisco EtherChannels](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9500/software/release/17-15/configuration_guide/lyr2/b_1715_lyr2_9500_cg/configuring_etherchannels.html)의 LACP 절을 참고한다.

전송 멤버는 구현과 해시 정책에 따라 MAC/IP/포트 등의 값으로 고른다. 여러 흐름이 같은 멤버에 몰릴 수도 있다. 두 1 Gbit/s 멤버의 총 용량이 늘어도 한 연결이 반드시 2 Gbit/s가 되지는 않는다. 멤버 하나를 잃고도 도달할 수 있지만 남은 용량은 줄고, 재선택 중 손실이나 재전송도 가능하다. LACP가 애플리케이션 성공·무손실·동일 처리량을 보장하지 않는다. 근거: [Linux bonding HOWTO](https://docs.kernel.org/networking/bonding.html)의 `xmit_hash_policy`와 802.3ad 선택 설명.

## 혼동 두 가지

| 구별 | 스스로 확인할 반례 |
| --- | --- |
| VLAN과 IP 서브넷 | 같은 접두사여도 VLAN이 갈리면 직접 ARP가 닿지 않는다. L2 소속과 L3의 다음 홉 판단을 따로 확인 |
| STP와 LACP | STP 차단 포트는 루프 방지용이다. LACP의 선택 멤버는 한 논리 링크의 전송에 함께 참여한다. 집성 후에도 전체 토폴로지에 별도 루프가 있으면 STP가 필요 |

<span id="errors"></span>
## 오류 검출 · 맞아 보이는 값도 다시 묻기

송신자는 데이터로 검출 값을 만들고 수신자는 받은 데이터와 비교한다. 검출 값이 다르면 손상을 의심할 수 있지만, 일치한다고 모든 오류가 없었다는 증명은 아니다. 복구·재전송·보안 인증은 별도의 기능이다.

| 방식 | 작은 자체 예제와 한계 |
| --- | --- |
| 짝수 parity | 데이터 `1011`의 1이 3개라 parity bit `1`을 붙여 `10111`로 보낸다. `11111`은 홀수라 검출. 두 비트가 바뀐 `01111`은 다시 짝수라 놓침. 단일 parity는 바뀐 위치를 찾아 고치지 못함 |
| Internet checksum | 16bit 단어 `0001`+`0002`(16진수)의 합은 `0003`, 1의 보수는 `FFFC`. 수신 합이 `FFFF`면 검사 통과. 두 단어가 `0000`과 `0003`으로 바뀌면 같은 합이라 놓침. 올림은 최하위로 더하는 1의 보수 덧셈을 사용 |
| CRC | 비트열을 약속한 생성 다항식으로 검사한다. r비트 CRC는 조건에 맞는 길이 r 이하 burst 오류를 검출하지만 모든 긴 오류를 검출하지는 못함. burst 길이는 첫·마지막 오류 위치를 포함한 구간 길이 |

다음은 Ethernet CRC-32가 아닌 **3비트 CRC의 가공 예**다. 생성 비트열 `1011`에 대해 아래 나머지를 제공한다. 필수는 다항식 나눗셈 대신 표를 읽고 판정하는 것이다.

| 전송 코드에 XOR한 오류 비트열 | 검사 나머지 | 판정할 것 |
| --- | --- | --- |
| `0000000` | `000` | 오류 없는 기준 |
| `0000001` | `001` | 끝 한 비트 변경 |
| `0000011` | `011` | 길이2 burst |
| `0001011` | `000` | 길이4 burst가 검사에 잡히지 않는 반례 |

나머지0을 “전송 중 오류가 절대 없었다”로 읽지 않는다. Ethernet FCS는 CRC를 사용하지만 암호화·송신자 인증을 제공하지 않는다. 공격자가 내용과 CRC를 함께 바꾸는 상황은 우발 손상 검출과 다르다. [Kurose/Ross 6.2](https://gaia.cs.umass.edu/kurose_ross/videos/6/)와 [RFC1071 §1](https://www.rfc-editor.org/rfc/rfc1071.html#section-1)이 근거다.

## 개발 질문과 다음 확인

[W09-D1~D3](WORKSHEET.md#development)의 설명→VLAN 변경→STP/LACP 상태·모의 왕복 근거를 [실습](LINUX.md)에서 모은다. 답은 [분리 해설](ANSWERS.md#development)에 있다. [전체 개념 색인](../CONCEPT_INDEX.md)에서 앞 개념으로 돌아가고, 다음에는 링크의 차단/집성과 IP 라우팅 정보의 갱신을 구별한다.
