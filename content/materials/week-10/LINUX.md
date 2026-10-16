# OSPF 실습 · 세 라우터에서 끊고 우회하고 복구하기

요약: 준비된 FRR 세 라우터에서 OSPF 이웃·경로·ping을 조회하고 R2-R3 링크 하나를 직접 끊어 비교한 뒤 복구한다. 실제 라우팅 프로세스와 Linux 커널을 사용하며 공용망·관리 경로는 변경하지 않는다.

## 실행 위치와 진행자의 준비

본인 PC의 PowerShell 또는 소유한 격리 Linux 실습 호스트에서 **Docker Engine의 Linux 컨테이너**와 **Compose 2.36 이상**을 사용한다. Docker 사용 권한이 필요하다. Windows에서는 Docker Desktop의 Linux 엔진을 켠다. 학교·공용 서버나 접속 중인 관리망의 Docker 설정을 바꾸지 않는다. Docker 설치·이용 조건은 사용 환경에서 먼저 확인한다.

진행자가 아래 **일곱 파일을 같은 새 개인 폴더**에 내려받고 정상 기준까지 준비한다. 참가자 필수는 초기 구축이 아니라 준비된 세 라우터의 조회·단절·복구다. 각자 별도 Docker 엔진 또는 별도 프로젝트 이름을 사용한다. 같은 엔진을 공유할 때는 모든 명령의 `-p w10me`를 서로 다른 영숫자 프로젝트 이름으로 일관되게 바꾼다. 같은 프로젝트를 동시에 조작하지 않는다.

- <a download href="../../labs/week-10/compose.txt">compose.txt</a> — YAML 구성, 확장자를 바꾸지 않고 `-f`로 지정한다.
- <a download href="../../labs/week-10/daemons.txt">daemons.txt</a> — FRR 프로세스 활성화.
- <a download href="../../labs/week-10/vtysh.txt">vtysh.txt</a> — vtysh의 통합 구성 방식.
- <a download href="../../labs/week-10/start-router.sh">start-router.sh</a> — 컨테이너 안의 기본 경로를 제거하고 FRR 시작.
- <a download href="../../labs/week-10/r1.txt">r1.txt</a> · <a download href="../../labs/week-10/r2.txt">r2.txt</a> · <a download href="../../labs/week-10/r3.txt">r3.txt</a> — 각 라우터 구성.

`start-router.sh`는 LF 줄바꿈을 유지한다. 파일을 다시 편집해 CRLF가 되면 Linux 셸에서 실행 오류가 날 수 있다. 모든 파일의 내용을 먼저 읽고, 해당 폴더에서 다음을 실행한다.

```sh
docker version
docker compose version
docker compose -p w10me -f compose.txt config --quiet
docker compose -p w10me -f compose.txt up -d
docker compose -p w10me -f compose.txt ps
```

처음에는 공식 FRR 이미지 `quay.io/frrouting/frr:10.5.1`을 받기 위해 인터넷이 필요하다. 컨테이너 세 개가 running인 것만으로 OSPF 준비가 끝난 것은 아니다. 아래 A1의 **두 이웃 Full·경로·ping**까지 확인한다. 대략 1분 간격 안에서 상태를 다시 조회할 수 있으나 일정 시간만 기다렸다는 이유로 정상 처리하지 않는다. 준비되지 않으면 실습 시간을 시작하기 전에 원인을 해결한다.

### 격리와 실제로 동작하는 범위

세 개의 전용 Docker bridge가 R1-R2·R1-R3·R2-R3를 연결한다. 호스트 네트워크와 포트 공개를 사용하지 않고 NAT를 끈다. 시작 스크립트는 **새 컨테이너 안에서만** 기본 경로를 제거한다. 호스트 경로·방화벽·SSH 설정을 변경하지 않는다. 브리지에 호스트 주소는 있으므로 악성 코드까지 격리하는 보안 샌드박스라는 뜻은 아니다. 제공한 실습 파일만 실행한다.

`NET_ADMIN`, `NET_RAW`, `SYS_ADMIN`은 이 FRR 컨테이너가 인터페이스·라우팅·프로세스를 다루기 위한 권한이다. `privileged`나 Docker 소켓 마운트는 없다. 진행자는 자기 Docker 환경에서 이 권한 사용이 허용되는지 확인한다.

FRR `ospfd`가 실제 OSPFv2 메시지를 교환하고 `zebra`가 Linux 커널에 경로를 설치한다. ping은 실제 ICMP 요청이다. 7주 `route_sim.py`나 9주 L2 모형으로 실행하지 않는다. 다만 가상 NIC·브리지의 실습이며 물리 케이블 단절·운영 장비·클라우드 전환·HTTP 응답의 실측은 아니다.

## 구성과 주소를 읽기

| 라우터 | 식별자·목적지 | 이웃용 인터페이스와 주소 | OSPF cost |
| --- | --- | --- | --- |
| R1 | Router ID 1.1.1.1, lo 192.0.2.1/32 | eth12=172.30.12.11/24, eth13=172.30.13.11/24 | eth12=10, eth13=50 |
| R2 | Router ID 2.2.2.2, lo 192.0.2.2/32 | eth12=172.30.12.12/24, eth23=172.30.23.12/24 | eth12=10, eth23=10 |
| R3 | Router ID 3.3.3.3, lo 192.0.2.3/32 | eth13=172.30.13.13/24, eth23=172.30.23.13/24 | eth13=50, eth23=10 |

모든 OSPF 인터페이스는 영역0이다. 연결 구간의 OSPF network type은 point-to-point로 지정해 DR 선출 상세를 생략한다. Docker bridge라는 매체와 OSPF가 그 매체를 다루는 network type을 구별한다. lo는 주소를 광고하되 이웃을 만들지 않는 passive다. 이 FRR 구성의 loopback 광고 cost는0이므로 R1에서 R3 lo까지 정상 비용은20, 우회 비용은50이다. cost는 ms가 아니다.

<span id="lab-a"></span>
## 필수 A · 링크 전환

### A1. 세 가지 정상 기준

모든 명령은 **호스트 셸**에서 입력한다. `exec -T r1`은 이미 준비한 R1 컨테이너에서 뒤의 명령을 실행한다. `vtysh -c` 안의 문자열이 FRR 명령이다. `-c`를 여러 번 쓰면 순서대로 실행한다.

```sh
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip ospf neighbor"
docker compose -p w10me -f compose.txt exec -T r2 vtysh -c "show ip ospf neighbor"
docker compose -p w10me -f compose.txt exec -T r3 vtysh -c "show ip ospf neighbor"
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip route 192.0.2.3/32"
docker compose -p w10me -f compose.txt exec -T r3 vtysh -c "show ip route 192.0.2.1/32"
docker compose -p w10me -f compose.txt exec -T r1 ping -I 192.0.2.1 -c 3 -W 1 192.0.2.3
```

각 라우터에서 두 이웃이 `Full`인지 본다. R1→192.0.2.3/32는 `Known via "ospf"`, distance110·metric20·Installed와 다음 홉172.30.12.12/eth12가 기준이다. R3의 역방향 다음 홉은172.30.23.12/eth23, 비용20이다. ping은 출발 주소를 R1 lo로 고정해 **R3가 R1 lo로 돌아오는 경로까지** 확인한다. 세 요청의 응답을 받는지 확인한다. 첫 ARP 등으로 손실이 있으면 다시 실행하고 최초 결과도 구별한다.

다음으로 경로가 어디서 왔는지 연결한다.

```sh
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip ospf interface eth12"
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip ospf database router"
docker compose -p w10me -f compose.txt exec -T r1 ip -4 route show
docker compose -p w10me -f compose.txt exec -T r1 ip -4 route show default
```

interface의 area·cost·Hello/Dead, database의 Router ID 세 개·LS Seq Number, 커널의 목적지·via·dev를 찾는다. FRR 화면과 커널의 metric 필드는 표시 방식이 다를 수 있으므로 OSPF cost는 FRR 경로/LSA에서 비교한다. 마지막 default 조회는 비어야 한다. 외부 접속을 실험하지 않는다.

### A2. R2의 eth23 하나만 내린다

예상을 말한 뒤 실행한다. R1-R3의 cost50 링크는 그대로 둔다. 명령에서 인터페이스 이름을 임의의 실제 NIC 이름으로 바꾸지 않는다.

```sh
docker compose -p w10me -f compose.txt exec -T r2 vtysh -c "configure terminal" -c "interface eth23" -c "shutdown" -c "end"
docker compose -p w10me -f compose.txt exec -T r2 ip -br link show eth23
docker compose -p w10me -f compose.txt exec -T r2 vtysh -c "show ip ospf neighbor"
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip route 192.0.2.3/32"
docker compose -p w10me -f compose.txt exec -T r3 vtysh -c "show ip route 192.0.2.1/32"
docker compose -p w10me -f compose.txt exec -T r1 ping -I 192.0.2.1 -c 3 -W 1 192.0.2.3
```

R2의 eth23이 DOWN이 되고 R2-R3 인접 관계가 사라지는지 본다. 반대쪽은 Hello 만료까지 옛 상태가 잠시 남을 수 있다. 이후 R1 경로가 **metric50·다음 홉172.30.13.13/eth13**, R3 역방향이 **metric50·172.30.13.11/eth13**으로 바뀌어야 한다. 전환 중 출력도 보관하고 같은 조회/ping을 다시 실행해 안정 후 응답을 확인한다. 준비 구성에서는 단절 후에도 우회로가 있으므로 장기적인 FAIL이 정상은 아니다.

LSDB가 어떻게 달라졌는지 다시 조회한다.

```sh
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip ospf database router"
```

끊긴 인접 연결과 LSA의 sequence·내용을 기준과 비교한다. 화면을 몇 번 조회했는지로 밀리초 수렴 시간을 계산하지 않는다. 시간 비교가 필요하면 단절 명령 시각·경로 관측 시각·ping 응답 시각을 같은 호스트 시계로 남기고 조회 간격의 오차를 적는다. 한 번의 관찰을 고정 성능으로 일반화하지 않는다.

### A3. 같은 인터페이스를 복구한다

```sh
docker compose -p w10me -f compose.txt exec -T r2 vtysh -c "configure terminal" -c "interface eth23" -c "no shutdown" -c "end"
docker compose -p w10me -f compose.txt exec -T r2 ip -br link show eth23
docker compose -p w10me -f compose.txt exec -T r2 vtysh -c "show ip ospf neighbor"
docker compose -p w10me -f compose.txt exec -T r1 vtysh -c "show ip route 192.0.2.3/32"
docker compose -p w10me -f compose.txt exec -T r3 vtysh -c "show ip route 192.0.2.1/32"
docker compose -p w10me -f compose.txt exec -T r1 ping -I 192.0.2.1 -c 3 -W 1 192.0.2.3
```

양 끝 이웃 Full, 비용20·R2 경유의 왕복 경로·ping 응답으로 돌아오는지 본다. no shutdown만 실행하고 끝내지 않는다. 아직 수렴 중이면 다시 조회한다. 각자 정상·단절·우회·복구의 명령, 이웃·경로·ping을 개인 파일에 한 번 보관한다. 다른 사람 화면을 보거나 제공 출력을 읽는 것은 본인 직접 수행을 대신하지 않는다.

## 오류 진단과 정리

| 증상 | 다음 확인과 복구 |
| --- | --- |
| Docker daemon 연결 실패·Linux 이미지 실행 불가 | 로컬 Linux 엔진과 본인 권한 확인. 공용 호스트 설정을 바꾸지 말고 준비 담당에게 환경 보충 요청 |
| interface_name 미지원 | Compose 버전 확인. 2.36 이상을 준비. eth 이름을 추측해 shutdown하지 않음 |
| 파일이 디렉터리로 마운트·셸 오류 | 일곱 파일 이름·같은 폴더·LF 확인. 먼저 아래 down으로 자기 프로젝트만 제거하고 원본을 다시 받아 up |
| address pool overlaps | 같은 엔진의 다른 실습을 임의 삭제하지 않음. 진행자가 충돌 없는 환경을 준비. 프로젝트 이름 변경만으로 서브넷 충돌은 해결되지 않을 수 있음 |
| 이웃이 없음·Full 전 단계 | ps·logs와 `show ip ospf interface eth12`의 주소/area/type/타이머, 다른 라우터의 대응 출력 확인. 정상 기준이 갖춰지기 전 단절 실습을 시작하지 않음 |
| 경로 Installed인데 ping 실패 | R3의 역방향 경로·출발 주소, `ip -4 route show`, 실제 구성/링크 확인. 특히 Docker의 internal 네트워크를 임의 추가하면 라우팅된 트래픽까지 차단할 수 있음 |
| 복구 후 비용50 그대로 | R2 eth23 UP·양 끝 Full부터 확인. `no shutdown` 후 재조회. 필요하면 자기 프로젝트를 down/up해 처음부터 재현 |

```sh
docker compose -p w10me -f compose.txt logs --tail 30
docker compose -p w10me -f compose.txt down
docker compose -p w10me -f compose.txt ps -a
```

`down`은 **이 프로젝트의 세 컨테이너와 세 네트워크**를 제거한다. 마지막 ps가 비면 정리된 것이다. 이미지와 다운로드 원본은 남는다. 전역 `docker system prune`은 사용하지 않는다. 창을 닫거나 Ctrl+C로 조회를 중단해도 컨테이너는 남으므로 마지막에 down을 실행한다. 원래 파일은 읽기 전용 마운트다. FRR의 write 명령으로 변경을 저장하지 않는다.

## 코드·구성 읽기 지도

| 파일·단계 | 이유와 읽을 문법 |
| --- | --- |
| compose.txt의 `x-router`, `&router`, `<<: *router` | YAML 앵커로 같은 이미지·권한·시작 명령을 세 번 복제하지 않음. 각 라우터의 파일과 두 네트워크는 따로 지정 |
| volumes의 `:ro`, networks의 `interface_name` | 원본을 읽기 전용으로 연결하고 NIC 이름을 고정. 호스트 경로와 컨테이너 안의 `/etc/frr/` 경로 구별 |
| start-router.sh의 `set -eu`, `if`, `exec` | 명령 실패·없는 변수를 오류로 취급. default가 있으면 컨테이너 안에서 제거. 이후 FRR 시작 프로세스로 교체. NIC 삭제나 호스트 명령은 없음 |
| daemons.txt·vtysh.txt | ospfd·zebra 활성화와 vtysh의 구성 파일 방식 지정. FRR 버전이 요구하는 관리용 프로세스도 함께 시작될 수 있음. BGP나 정적 경로를 실습에 추가한 뜻은 아님 |
| r1/r2/r3.txt의 `interface`, `ip ospf area/cost/network` | 인터페이스를 영역에 넣고 비용·연결 종류를 지정. lo의 passive는 광고를 유지하면서 Hello를 보내지 않음 |
| `router ospf`, `ospf router-id` | 프로토콜과 고유 식별자. 실제 다음 홉 주소·ping 목적지와 구별 |
| A1→A2→A3 | 조회→한 인터페이스 변경→비교→같은 인터페이스 복구. 이웃표·경로표·요청을 모두 다시 읽음 |

필수는 이 흐름과 본인 출력의 대응을 설명하는 것이다. 파일을 빈 상태에서 독립 작성하는 것은 선택이다. “왜 R1에 R3로 가는 정적 경로가 없는데도 커널 경로가 생길까?”, “왜 출발 주소를 lo로 고정할까?”, “왜 이웃 Full만으로 ping 성공을 결론 내릴 수 없을까?”를 말해 본다. [해설](ANSWERS.md) · [공식 근거](SOURCES.md) · [개념 색인](../CONCEPT_INDEX.md).

<a download href="LINUX.md">실습 안내 원문 내려받기</a>
