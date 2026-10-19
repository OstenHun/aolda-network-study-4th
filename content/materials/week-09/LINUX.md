# 격리 L2 실습 · 상태를 바꾸고 복구하기

요약: 제공 Python 시뮬레이터에서 MAC/VLAN 전달과 STP 링크 전환, LACP 멤버 전환을 각자 직접 수행한다. 상태·프레임 이벤트·모의 왕복을 비교하며 실제 패킷·성능 측정과 구별한다.

실제 프로토콜과 비교하려면 [Linux bridge·Open vSwitch 실습](REAL_L2.md)을 이어 본다. 이 페이지의 모형은 그대로 사용하며, 실제 BPDU·LACPDU·협상·응답을 여기의 계산 결과와 구별한다. 실제 실습의 설치·권한·복구 조건은 별도 안내를 따른다.

## 실행 위치·준비

본인 PC의 PowerShell 또는 Linux 일반 사용자 셸에서 Python 3.10 이상으로 실행한다. 관리자·sudo·추가 패키지·네트워크 접근은 필요 없다. 세 파일을 **같은 빈 개인 폴더**에 내려받고 그 폴더에서 터미널을 연다.

- <a download href="../../labs/week-09/switch_sim.py">switch_sim.py 내려받기</a>
- <a download href="../../labs/week-09/stp.txt">stp.txt 내려받기</a>
- <a download href="../../labs/week-09/lacp.txt">lacp.txt 내려받기</a>

```sh
python --version
python switch_sim.py stp.txt
```

`python`이 없고 `python3`가 설치된 Linux라면 위 두 명령의 실행 이름만 `python3`로 바꾼다. 이후 `sim>`에서 입력할 명령은 Python 셸이나 운영체제 셸 명령이 아니다. 프롬프트 `sim>` 자체는 입력하지 않는다. 첫 줄에 `SIM v1`이 나오면 `help`, `show`를 입력한다.

### 지원 기능과 관찰 한계

| 지원하는 직접 조작 | 단순화한 조건 |
| --- | --- |
| 출발지 학습·목적지 전달/필터·flood, VLAN10/20 access·trunk 허용 목록 | 프레임은 메모리의 사건이다. IP·ARP·실제 802.1Q 바이트·FCS를 생성하지 않음. MAC 노화 타이머 없음 |
| 동등 비용 STP 루트/포트 재계산·링크 변경·복구 | 제공된 점대점 구성, 모든 비용1·Bridge ID는 숫자 순위. BPDU 교환·상태별 대기·수렴 시간은 구현하지 않음. VLAN들은 같은 트리 사용 |
| LACP 호환 모드·물리 멤버 선택·po1·멤버 단절/복구 | 속도/duplex/상대/키가 이미 맞는 구성. active/passive 호환 규칙의 수렴 후 상태를 계산하며 LACPDU/타이머는 구현하지 않음. min-links=1 고정 |
| 같은 flow의 멤버 고정·여러 flow의 멤버 분산 | flow 정수 `%` 가동 멤버 수라는 교육용 선택. 장비의 해시·실제 TCP 연결·처리량이 아님 |

고정 trace를 재생하지 않는다. 명령마다 현재 구성과 학습 상태로 결과를 계산한다. 상태 변경 때 모델이 FDB 전체를 비우며, 실제 장비의 토폴로지 변경 처리와 동일한 세부 동작이라는 뜻은 아니다. 실제 장비 프로토콜 검증이 필요하면 소유한 격리 환경에서 별도로 수행한다. 기존 학교/공용 스위치·SSH 관리 경로는 변경하지 않는다.

<span id="lab-a"></span>
## 필수 A · MAC/VLAN과 STP 전환

### A1. 정상 기준과 MAC 학습

구성은 [K2의 삼각형](CONCEPTS.md#stp)이다. S1이 루트, A는 S2/VLAN10, B는 S3/VLAN10, C는 S3/VLAN20이다. l12/l13/l23은 VLAN10/20을 허용하는 trunk다. 먼저 다음을 **한 줄씩** 입력하고 바뀐 출력을 읽는다.

```text
show
frame A B
show
frame B A
frame A B
show
```

첫 `show`에는 FDB 줄이 없다. 첫 A→B는 A의 출발지 MAC을 입력 포트와 묶어 학습하고 B를 모르므로 `FLOOD`한다. B→A를 보낸 뒤에는 B 위치도 배우며, 다음 A→B에서 `UNICAST`가 나타난다. `LEARN`의 MAC은 목적지가 아닌 출발지다. `TX`에서 l12→l13 경로, `PORT S3/l23 ... blocked`를 찾아 본다. 데이터가 차단된 포트가 있어도 케이블의 `up=True`일 수 있다.

```text
frame A broadcast
probe A B
probe A C
```

`broadcast`는 이 모형의 예약어다. VLAN10 broadcast의 `DELIVER`에 B는 있고 C는 없어야 한다. `PROBE PASS`는 모형의 L2 요청 프레임과 역방향 응답 프레임이 도달했다는 뜻이다. ping·HTTP·IP 라우팅 성공을 의미하지 않는다. 정상 A↔B는 PASS, 다른 VLAN A↔C는 FAIL이다.

### A2. access VLAN 한 조건 변경과 복구

예상을 먼저 말한 뒤 B의 VLAN만 바꾼다. C의 설정·trunk·링크는 그대로 둔다.

```text
vlan B 20
show
probe A B
probe B C
vlan B 10
probe A B
probe A C
```

변경 후 A↔B FAIL, B↔C PASS, 복구 후 A↔B PASS·A↔C FAIL을 비교한다. `ACCESS`의 VLAN과 `FRAME`의 VLAN을 근거로 쓴다. 이 구성에는 VLAN 간 라우터가 없다. 실제 호스트 IP를 바꾸거나 본인 PC의 NIC를 변경하지 않는다.

### A3. STP 링크 하나 단절과 복구

원래 VLAN으로 돌아온 뒤 `reset`으로 정상 시작점을 확실히 만든다. l13을 끊으면 S3가 어느 경로를 사용할지 [교재](CONCEPTS.md#stp)를 보고 예상한다.

```text
reset
show
probe A B
link l13 down
show
probe A B
link l13 up
show
probe A B
```

기준에서는 S3/l13=root, S3/l23=blocked이다. 단절 후 l13의 양쪽은 disabled, S3/l23=root/forwarding이며 A→B의 `TX`는 l23를 사용한다. S3의 root는 S1 그대로이고 cost는 1→2로 바뀐다. 복구 후 cost1·l13 root·l23 blocked와 PASS를 다시 확인한다. **전환 명령 뒤 이미 수렴한 결과**이므로 중간 손실0이나 즉시 복구라는 실측 주장을 하지 않는다.

정상·VLAN 변경/복구·STP 단절/복구의 본인 명령, MAC/VLAN, 루트/포트와 `TX`, 모의 왕복을 개인 파일에 보관한다. 두 관찰을 하나의 긴 새 양식에 다시 입력할 필요는 없다.

<span id="lab-b"></span>
## 필수 B · LACP 멤버 하나 단절과 복구

A 세션에서 `quit`을 입력하고 운영체제 셸에서 다음 구성으로 새로 시작한다.

```sh
python switch_sim.py lacp.txt
```

이 구성은 S1/S2 사이 po1에 m1/m2 두 멤버, active/passive, min-links1이다. A와 B는 VLAN10이다. STP에서 po1은 논리 포트 하나로 나타난다.

```text
show
probe A B 0
probe A B 1
probe A B 1
link m1 down
show
probe A B 0
probe A B 1
link m1 up
show
probe A B 0
```

정상은 `selected=2`, 두 멤버의 `collecting/distributing=True`와 PASS다. flow0은 m1, flow1은 m2를 선택하며 같은 flow1을 반복해도 같은 멤버다. m1 단절 후 `carrier=False`·참여False, selected1·m2 선택·po1 forwarding·PASS를 확인한다. m1 복구 후 selected2·flow0의 m1·PASS로 돌아오는지 비교한다. 트래픽을 전송해 속도를 잰 것이 아니므로 처리량 수치를 출력에서 만들어 내지 않는다.

### 선택 비교 · 둘 다 끊기거나 협상이 없으면

필수 복구를 확인한 뒤 남는 시간에 한 조건씩 실행하고 각 비교 후 `reset`한다.

```text
link m1 down
link m2 down
show
probe A B
reset
mode S1 passive
show
probe A B
reset
show
probe A B
```

모든 멤버 단절은 selected0·po1 disabled·FAIL이다. 두 모드가 passive이면 carrier가 살아 있어도 선택 멤버0·FAIL이다. 마지막 reset은 active/passive와 두 멤버를 복구하므로 PASS가 된다. 실제 장비의 min-links·키/상대 불일치·LACP 타이머 구성은 이 실습에 추가하지 않는다.

## 오류를 만났을 때와 정리

| 증상 | 다음 확인과 복구 |
| --- | --- |
| 파일 없음·CONFIG ERROR | 현재 폴더와 정확한 세 파일 이름을 확인. JSON을 임의 편집했다면 원본을 다시 내려받아 새 세션으로 실행 |
| `ERROR: invalid command`·unknown link | `help`와 `show`의 이름을 대조. stp에는 l12/l13/l23, lacp에는 po1/m1/m2. 오류 명령은 설정을 바꾸지 않음 |
| 예상과 다른 FAIL | ACCESS VLAN, TRUNK allowed/up, PORT 상태, LACP selected를 차례로 읽는다. 변경을 잊었다면 `reset` 후 정상 기준부터 재현 |
| 출력만 읽고 직접 실행할 수 없음 | 개념/제공 분석으로 표시하고 A/B의 본인 변경·복구를 보충. 다른 사람의 실행을 본인 수행으로 쓰지 않음 |

`reset`은 시작 JSON을 메모리에 다시 복사하고 FDB를 비운다. `quit`·EOF·Ctrl+C는 세션을 끝내고 메모리 변경을 버린다. 파일이나 OS 네트워크를 쓰지 않으므로 NIC·라우트·스위치 정리 명령은 없다. 필요한 개인 출력은 종료 전에 보관한다.

## 코드를 읽는 지도

필수는 `execute`→`frame`의 입력·학습·판단·출력 흐름과 실제 출력의 대응이다. 나머지 계산 구현의 세부 추적은 선택이다.

| 위치 | 이유와 처음 보는 문법 |
| --- | --- |
| <span class="keep-phrase"><code>load_lab</code></span>, `reset` | JSON을 읽고 허용 구성인지 검사. `deepcopy`는 변경이 시작 원본까지 퍼지는 것을 막음 |
| `execute` | `shlex.split`으로 명령을 나누고 검증 후 한 설정만 변경. `int` 실패는 ERROR. 변경 뒤 revision 증가·FDB 초기화 |
| <span class="keep-phrase"><code>spanning_tree</code></span> | `deque` 큐로 같은 비용의 거리를 계산하고 루트/포트 결정. `(switch, port)` 튜플이 양 끝 포트를 따로 식별 |
| `frame` | 큐에서 수신→출발지 FDB 학습→목적지 조회→같은 VLAN/전달 포트로 전송. `seen`은 계산 오류로 루프가 생기면 중단하는 검증이지 STP의 대체가 아님 |
| <span class="keep-phrase"><code>active_members</code></span>, `%` | 가동 멤버와 호환 모드에서 선택 목록 생성. flow 나머지로 그중 한 멤버 선택. 표준 장비 해시의 재구현이 아님 |
| `main` | 명령 반복, quit/EOF/Ctrl+C 종료, 잘못된 명령 복구. 네트워크 소켓·sudo·외부 명령 호출이 없음 |

자기 말로 확인한다. “B로 보내는데 왜 A MAC을 배우는가?”, “l23의 한쪽만 blocked여도 왜 데이터가 못 지나가는가?”, “m1이 빠져도 po1이 남는 조건은 무엇인가?” 답은 [분리 해설](ANSWERS.md)과 실제 본인 출력으로 대조한다.
