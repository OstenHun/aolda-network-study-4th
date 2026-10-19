# 실제 BPDU·LACPDU와 링크 전환 관찰하기

요약: 기존 모형으로 경로를 예상한 뒤 격리 컨테이너의 Linux bridge·Open vSwitch에서 실제 STP·LACP와 ICMP를 관찰한다. 링크 하나를 끊고 같은 링크를 복구하며 상태·패킷·응답을 함께 확인한다.

## 모형과 실제 구현을 나란히 보기

[기존 모형](LINUX.md)은 MAC/VLAN·수렴 후 경로를 빠르게 예상하는 도구다. 여기서는 Linux의 STP와 Open vSwitch의 LACP가 실제 프레임을 교환한다. STP는 루트 선출·포트 상태 전환, LACP는 양끝 협상을 관찰한다. 물리 스위치나 학교망을 바꾸는 실습은 아니다. 기존 모형을 지우거나 실제 패킷이라고 이름만 바꾸지 않는다.

진행자가 아래 준비를 마치고 참가자는 준비된 구성을 조회·단절·복구한다. 기존 K2·K3 설명과 비교에 사용하고 새 제출 양식은 만들지 않는다. 이 보완 실습이 준비되지 않았다고 기존 모형의 직접 수행을 취소하지 않는다.

## 준비와 실행 경계

Docker Engine의 **Linux 컨테이너**, Compose v2, 설치/사용 권한이 있는 개인 실습 호스트가 필요하다. Windows는 Docker Desktop의 Linux 엔진을 사용한다. 패킷은 PC의 Wireshark로 읽는다. 처음 이미지 빌드에는 인터넷이 필요하며 설치는 모임 전에 끝낸다.

아래 네 파일을 **같은 새 폴더**에 저장한다. 셸 파일은 LF 줄바꿈을 유지한다. 이 폴더에는 파일을 추가로 넣지 않는다.

- <a download href="../../labs/week-09/real/Dockerfile.txt">Dockerfile.txt</a> · <a download href="../../labs/week-09/real/compose.txt">compose.txt</a>
- <a download href="../../labs/week-09/real/boot.sh">boot.sh</a> · <a download href="../../labs/week-09/real/lab.sh">lab.sh</a>

`lab.sh`는 **컨테이너 안에서만** 실행한다. Compose는 호스트 네트워크·포트·장치·Docker 소켓·호스트 폴더를 연결하지 않는다. NET_ADMIN/NET_RAW는 가상 링크·캡처, SYS_ADMIN은 컨테이너 내부 네트워크 네임스페이스에 필요하다. 이 권한을 사용해도 되는 개인 환경인지 먼저 확인한다. 악성 코드용 보안 샌드박스라는 뜻은 아니다.

`w09me`는 본인 전용 프로젝트 이름이다. `docker compose ls -a`에 같은 이름이 있으면 덮어쓰지 말고 아래 모든 `w09me`를 다른 영숫자 이름으로 맞춘다. 공용 호스트·기존 관리 VM의 네트워크를 변경하지 않는다.

```sh
docker version
docker compose version
docker compose ls -a
docker compose -p w09me -f compose.txt config --quiet
docker compose -p w09me -f compose.txt up -d --build
docker compose -p w09me -f compose.txt logs --tail 10
```

로그의 `READY`를 확인한다. running만으로 준비를 판단하지 않는다. 이후 명령은 모두 **같은 폴더의 호스트 셸**에서 입력한다. `exec -T lab` 뒤 명령이 컨테이너 안에서 실행된다. 배포판 패키지는 갱신될 수 있으므로 사용 버전을 본인 근거에 남긴다.

## A · Linux bridge의 STP

S1–S2–S3 삼각형이며 A는 S2, B는 S3의 access VLAN10에 연결된다. 세 trunk는 VLAN10을 태그한다. 브리지 우선순위는 S1=4096, S2=8192, S3=12288이고 링크 비용은10이다. IP는 격리 끝점 A=192.0.2.10/24, B=192.0.2.20/24이다. 라우터와 기본 경로는 없다.

### A1 · 선출·대기·정상 전달

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp up
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp ping
```

`up`은 생성과 캡처 시작이다. `show`를 몇 초 간격으로 다시 읽어 listening→learning→forwarding과 blocking을 구별한다. 안정 후 S3의 root는 `1000.02:00:09:00:00:01`, root_path_cost=10, s3p1은 forwarding, s3p2는 blocking이 기준이다. A/B access도 forwarding인지 확인한 뒤 ping의 실제 송수신 수를 읽는다. 초기 손실이 있으면 보존하고 안정 후 다시 확인한다.

이 구성은 고전 STP다. 짧은 학습용 설정은 hello1초·max age6초·listening/learning 각각4초이며, 이 iproute2의 입력/출력은 USER_HZ=100 단위라 `100/600/400`으로 보인다. 초와 혼동하지 않는다. 모든 장비의 기본값·수렴 시간을 뜻하지 않으며 RSTP 실험도 아니다.

### A2 · S1–S3 링크 하나 단절·복구

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp link l13 down
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp ping
```

전환 중 응답 손실이 있을 수 있다. show와 ping을 다시 확인한다. 안정 후 s3p1=disabled, s3p2=forwarding, S3 root_path_cost=20과 같은 root, A↔B 응답 복귀를 확인한다. 이는 S2를 경유하는 경로다. 상태 변화와 응답 복귀는 별개 관찰이다.

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp link l13 up
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp ping
```

안정 후 원래 cost10·s3p1 forwarding·s3p2 blocking과 응답으로 돌아오는지 본다. 조회 시각 사이를 정밀 수렴 시간으로 쓰거나, 마지막 ping 성공으로 중간 손실이 없었다고 쓰지 않는다.

### A3 · 캡처를 닫고 PC로 가져오기

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh stp down
docker compose -p w09me -f compose.txt cp lab:/evidence ./stp-evidence
docker compose -p w09me -f compose.txt down
```

기존 폴더를 덮어쓰지 않도록 `stp-evidence`가 없는지 먼저 확인한다. 첫 down은 캡처를 닫고 링크/끝점을 정리한다. 마지막 down은 본인 컨테이너를 지운다. 복사 전에 마지막 down을 실행하면 컨테이너 안의 캡처도 사라진다.

Wireshark에서 `stp-s3p2.pcap`·`stp-s1p3.pcap`을 연다. `stp`로 root/bridge ID·root path cost·포트·타이머를 읽고 양방향 제어 프레임을 짝짓는다. `vlan.id == 10 && (arp || icmp)`로 데이터 프레임과 태그를 읽는다. 차단 링크에서도 BPDU가 보일 수 있으며 데이터 forwarding과 다르다. 단절 전/중/복구 시각과 show를 대응한다. MAC과 패킷 번호는 본인 파일에서 확인한다.

## B · Open vSwitch의 LACP

STP 실습을 정리한 뒤 새 컨테이너에서 시작한다. STP와 LACP를 한 OVS 토폴로지에 섞지 않는다. S1–S2 사이 m1/m2 두 veth가 하나의 bond이며 양끝 access VLAN10의 A/B는 같은 주소를 사용한다. S1은 active, S2는 passive, fast 타이머·fallback 비활성이다. OVS bond는 실제 협상과 데이터 전달을 처리한다.

### B1 · 양끝 협상과 정상 요청

```sh
docker compose -p w09me -f compose.txt up -d
docker compose -p w09me -f compose.txt logs --tail 10
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp up
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp ping
```

READY 뒤 실행한다. 안정 후 po1의 `status: active negotiated`와 po2의 `status: passive negotiated`, 양끝의 두 멤버 `attached`와 bond의 enabled·may_enable, A↔B 응답을 확인한다. 설정에 active/passive가 적혔다는 사실만으로 협상이 끝난 것은 아니다. show의 actor/partner system ID와 멤버를 대응한다.

### B2 · m1만 끊고 같은 멤버 복구

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp link m1 down
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp ping
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp link m1 up
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp ping
```

각 단계에서 필요하면 show/ping을 반복한다. 단절 뒤 양끝 m1 미참여·m2 참여·응답을, 복구 뒤 두 멤버의 재참여·응답을 본다. 하나의 ping 흐름이 두 링크를 동시에 사용하거나 속도가 두 배가 되어야 하는 실험은 아니다. 관찰하지 않은 무손실·처리량을 주장하지 않는다.

### B3 · 선택 비교: carrier와 협상의 차이

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp mode passive
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp ping
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp mode active
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp show
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp ping
```

S1의 모드만 바꾼다. **이미 협상한 뒤 두 passive로 바꾸는 조건은 처음부터 두 passive로 시작하는 조건과 다르다.** 기존 partner 상태와 응답이 유지될 수도 있다. 실패해야 한다고 가정하지 말고 양끝 상태·패킷·응답을 읽는다. 이 비교는 냉기동 협상 실패 실험이 아니다. active/passive로 되돌린 뒤 협상·두 멤버·응답을 재확인한다. 기존 모형에는 이 협상 이력이 없다는 차이도 설명한다.

### B4 · 정리와 패킷 분석

```sh
docker compose -p w09me -f compose.txt exec -T lab sh /lab/lab.sh lacp down
docker compose -p w09me -f compose.txt cp lab:/evidence ./lacp-evidence
docker compose -p w09me -f compose.txt down
docker compose -p w09me -f compose.txt ps -a
```

새 `lacp-evidence` 폴더로 복사한다. Wireshark에서 `lacp-m1a.pcap`·`lacp-m2a.pcap`을 열고 `lacp`로 Actor/Partner System·Port·State의 Synchronization/Collecting/Distributing을 비교한다. `vlan.id == 10 && (arp || icmp)`로 실제 데이터를 찾는다. 제어 프레임의 상태와 show, ping을 같은 단계로 대응한다. B3를 했다면 passive 전환/재협상의 패킷도 찾는다. 마지막 ps가 비어 있는지 확인한다. 이미지·다운로드 원본은 남는다.

## 막혔을 때와 코드 읽기

| 증상 | 확인·복구 |
| --- | --- |
| Docker pipe·permission denied | 본인 Linux 엔진과 사용 권한 확인. 학교/공용 호스트 권한을 풀지 않음 |
| Operation not permitted·datapath 오류 | netns/bridge/OVS와 세 capability 지원 확인. privileged·host network로 우회하지 않고 지원되는 별도 개인 환경에서 보충 |
| READY 없음·파일/셸 오류 | 네 파일·같은 폴더·LF·build 로그 확인. 소유 프로젝트 down 후 원문/빌드부터 재확인 |
| listening/learning 중 ping 실패 | 실제 STP 상태를 다시 읽고 안정 후 확인. STP를 꺼 성공시키지 않음 |
| LACP가 negotiated 아님 | 양끝 actor/partner·모드·carrier·member를 읽음. m1 복구·S1 active 후 재조회 |
| `Evidence exists`·중복 up 거부 | 캡처를 보존하고 해당 mode down→복사→Compose down. 새 컨테이너에서 다시 시작 |

boot.sh는 OVS DB/데몬을 시작한다. lab.sh의 stp_up은 bridge→링크/VLAN→끝점→캡처, lacp_up은 OVS bridge→bond/모드→끝점→캡처 순서다. show는 실제 도구 출력을, ping은 네임스페이스의 실제 ICMP를 사용한다. link는 정해진 링크 하나만, mode는 S1의 LACP 모드만 바꾼다. cleanup은 이 컨테이너의 실습 이름만 지운다. 다른 장비를 관리하는 범용 스크립트가 아니다.

중단 때는 현재 모드의 down으로 캡처를 닫고 필요한 파일을 복사한 뒤 Compose down한다. down이 실패해도 본인 Compose 프로젝트를 지우면 그 컨테이너의 네임스페이스·링크·데몬이 함께 제거된다. 전역 prune이나 다른 컨테이너 종료는 하지 않는다. 본인 상태·패킷·응답·복구와 받은 도움을 기존 개인 기록에 한 번 연결한다. [공식 근거](SOURCES.md#real-l2) · [기존 모형](LINUX.md) · [학습 홈](README.md).
