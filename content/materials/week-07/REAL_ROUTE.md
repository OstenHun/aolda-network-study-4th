# 실제 Linux에서 반환 경로와 링크 장애 관찰하기

요약: 기존 모형과 같은 A–R1–R2–B를 격리 Linux 네임스페이스로 만든다. 반환 경로 삭제와 링크 단절을 따로 실험하고 경로표·실제 ICMP·양끝 패킷을 대조한 뒤 같은 조건으로 복구한다. 혼자서도 전 과정을 수행할 수 있다.

## 먼저 예상하고 직접 확인하기

[기존 모형](LINUX.md#simulator)은 그대로 사용한다. 여기서는 Linux 커널이 실제 패킷을 전달한다. 모형의 `ROUND_TRIP OK`와 실제 ping·pcap을 구별한다. 기존 필수 A/B와 평가 기준을 바꾸지 않으며 준비된 실제 구성으로 같은 원리를 비교한다. 설치·초기 구축은 진행자가 미리 준비하고 새 제출물은 만들지 않는다.

**파트너는 실행 조건이 아니다.** 혼자라면 각 단계에서 예상→직접 실행→출력/패킷 대조→복구→자기 설명으로 진행한다. 함께라면 각자 먼저 예상과 실행을 한 뒤 막힌 근거를 비교한다. 원하면 설명자·질문자를 바꾸지만 한 사람의 실행이나 정답을 서로의 수행으로 쓰지 않는다. 두 호스트·두 라우터는 프로그램 안의 장치 역할이며 사람 두 명을 뜻하지 않는다.

## 실행 환경과 네 파일

Docker Engine의 Linux 컨테이너, Compose v2 이상과 설치/사용 권한이 있는 개인 호스트가 필요하다. Windows에서는 Docker Desktop의 Linux 엔진을 쓴다. 패킷 파일은 PC의 Wireshark로 읽는다. 이미지 빌드에는 인터넷이 필요하다.

아래 네 파일을 **같은 새 폴더**에 저장하고 그 폴더의 호스트 셸에서 명령을 입력한다. 셸 파일은 LF 줄바꿈을 유지한다. 코드의 명령을 호스트에서 직접 실행하지 않는다.

- <a download href="../../labs/week-07/real/Dockerfile.txt">Dockerfile.txt</a> · <a download href="../../labs/week-07/real/compose.txt">compose.txt</a>
- <a download href="../../labs/week-07/real/boot.sh">boot.sh</a> · <a download href="../../labs/week-07/real/lab.sh">lab.sh</a>

Compose는 호스트 폴더·네트워크·포트·장치·Docker 소켓을 연결하지 않는다. NET_ADMIN/NET_RAW는 내부 링크·경로·캡처, SYS_ADMIN은 내부 네임스페이스와 임시 마운트에 필요하다. 이 권한이 허용되는 개인 환경에서만 실행한다. 악성 코드용 보안 샌드박스를 뜻하지 않는다. 기존 관리 VM·공용망·SSH 기본 경로를 바꾸지 않는다.

```sh
docker version
docker compose version
docker compose ls -a
docker compose -p w07me -f compose.txt config --quiet
docker compose -p w07me -f compose.txt up -d --build
docker compose -p w07me -f compose.txt logs --tail 10
```

`w07me`가 이미 쓰이는 이름이면 모든 명령에서 본인 전용의 다른 영숫자 이름으로 바꾼다. running만 보지 말고 로그의 `READY` 뒤 다음을 실행한다. 설치 패키지는 갱신될 수 있으므로 Docker·`ip -V`·`ping -V`·`tcpdump --version`을 본인 근거에 남긴다. 도구 버전은 `docker compose ... exec -T lab` 뒤에서 조회한다.

## A · 정상 경로와 양끝 관찰 위치

구성은 기존 교재와 같다. 네 장치 각각 별도 네트워크 스택·경로표를 사용한다. R1/R2는 IPv4 forwarding을 켜고, 이번에는 반환 경로 삭제만 분리해 보도록 reverse-path filter(rp_filter)를 끈다. rp_filter는 들어온 패킷 출발지의 역방향 경로를 검사하는 별도 조건이다. 이 설정을 운영망의 권장값으로 복사하지 않는다. NAT·동적 라우팅·대체 링크는 없다.

| 장치/인터페이스 | 주소 | 필요한 정적 경로 |
| --- | --- | --- |
| A eth0 / R1 lan0 | 192.0.2.10/24 / 192.0.2.1/24 | A 기본 경로는 R1 |
| R1 transit0 / R2 transit0 | 198.51.100.1/30 / 198.51.100.2/30 | R1의203.0.113.0/24는 R2 경유, R2의192.0.2.0/24는 R1 경유 |
| R2 lan0 / B eth0 | 203.0.113.1/24 / 203.0.113.20/24 | B 기본 경로는 R2 |

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh up
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh show
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh lookup
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh ping 701
```

show의 네 주소/표, R1/R2 forwarding=1·rp_filter=0을 확인한다. lookup은 R1의 요청 전달과 R2의 응답 전달을 **조회만** 한다. 실제 통신은 별도 ping으로 확인한다. `701`은 ICMP Identifier이며 나중에 패킷을 단계별로 찾기 위한 표식이다. 경로·포트 번호가 아니며 생략하면700을 쓴다. 정상 ping의 실제 송수신 수를 읽고 초기 손실이 있으면 남긴 뒤 재확인한다.

캡처 `a-edge.pcap`은 R1의 A쪽 lan0, `b-edge.pcap`은 R2의 B쪽 lan0이다. 같은 시각·같은 ICMP ID/Sequence의 요청과 응답을 양쪽 파일에서 대응한다. 연결 상태·경로 선택·왕복 성공은 서로 다른 근거다.

## B · 요청은 도착하지만 응답은 못 돌아오는가?

다음 명령은 **R2의192.0.2.0/24 정적 경로 하나만** 지운다. A의 기본 경로나 링크는 바꾸지 않는다.

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh return down
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh show
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh lookup
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh ping 702
```

R1의 B 목적지 조회는 남아 있고 R2의 A 목적지 조회는 경로 없음이 기준이다. ping 실패의 종료코드1은 이 조건에서 예상한 관찰이며 설치 실패라는 뜻은 아니다. 캡처에서 B쪽에 요청과 B가 만든 응답이 있지만 A쪽에는 그 응답이 없는지 확인한다. 이것이 “요청 도착”과 “왕복 성공”을 나누는 근거다. ICMP 오류가 생기는지도 읽되 항상 같은 오류가 생성·반환된다고 보장하지 않는다.

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh return up
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh lookup
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh ping 703
```

R2의 경로와 양끝 응답이 복구됐는지 확인한다. 반환 경로를 지운 채 다음 링크 실험을 시작하면 두 조건이 섞인다.

## C · R1–R2 링크 하나 단절·복구

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh link down
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh show
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh lookup
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh ping 704
```

R1 transit0의 admin down과 R2측 carrier 변화를 읽는다. Linux는 admin down 때 그 인터페이스의 경로를 제거할 수 있다. 반대편에는 정적 항목이 남아 `linkdown`으로 보일 수도 있다. 실제 표를 읽고 어느 쪽도 자동 우회로 단정하지 않는다. B쪽 캡처에704 요청이 도착하지 않는지 B와 비교한다. 대체 경로가 없으므로 OSPF 수렴을 기대하지 않는다.

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh link up
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh show
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh lookup
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh ping 705
```

**링크 up만으로 정적 경로가 다시 생기는 것은 아니다.** R1의 B 경로가 사라졌다면705도 실패할 수 있다. R1의 직접 연결 경로·정적 B 경로와 R2의 반환 경로를 따로 읽는다. 다음 명령은 R1의 B 경로를 명시적으로 다시 설치한다. 이미 존재하면 같은 값으로 맞춘다.

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh forward-restore
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh lookup
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh ping 706
```

링크·양방향 경로·실제 응답이 모두 정상인지 확인한다. 마지막 성공이 중간 무손실이나 일정 복구 시간을 증명하지 않는다. B와 C의 실패를 각각 한 문장으로 설명한다. 반환 경로 삭제와 링크 단절, 링크 복구 뒤 남은 정적 경로 부재는 어떻게 구별했는가?

## D · 캡처 보존과 정리

```sh
docker compose -p w07me -f compose.txt exec -T lab sh /lab/lab.sh down
docker compose -p w07me -f compose.txt cp lab:/evidence ./route-evidence
docker compose -p w07me -f compose.txt down
docker compose -p w07me -f compose.txt ps -a
```

새 `route-evidence` 폴더로 복사한다. 첫 down은 캡처를 닫고 내부 자원을 지우며, 마지막 Compose down은 컨테이너를 제거한다. 복사 전에 컨테이너를 지우면 캡처가 사라진다. actions.log의 UTC 시각·ID와 두 pcap을 함께 보관한다.

Wireshark에서 `icmp.ident == 702`로 반환 경로 삭제 단계의 관련 패킷을 찾는다. Identifier는 오류 패킷에 인용된 원래 ICMP에도 있을 수 있으므로 **바깥 ICMP Type과 안에 인용된 패킷을 구별**한다. Echo request는 type8, Echo reply는 type0이다. 같은 필터의 Identifier를701·703·704·705·706으로 바꿔 각 단계를 비교한다. ARP는 다음 홉 MAC 해석이며 반환 경로 자체를 만들어 주지 않는다. 파일 두 개를 받았다는 사실만으로 분석을 완료 처리하지 않는다.

## 막힌 지점과 코드 지도

| 증상 | 확인·복구 |
| --- | --- |
| Docker 접근·권한·netns/proc mount 오류 | 본인 Linux 엔진과 capability 지원을 확인한다. 공용 호스트 권한 해제·privileged/host network 전환으로 우회하지 않는다. 지원되는 개인 환경에서 보충한다. |
| 파일/셸 오류·READY 없음 | 네 파일·같은 폴더·LF·build 로그를 확인한다. 소유 프로젝트만 정리하고 재시작한다. |
| 정상에서도 ping 실패 | show의 주소·양쪽 경로·forwarding/rp_filter·링크, lookup과 두 캡처를 비교한다. 설정을 무작정 추가하지 않는다. |
| 중복 up·Evidence exists | 현재 down→캡처 복사→Compose down 후 새 컨테이너에서 시작한다. 기존 캡처를 덮어쓰지 않는다. |

boot.sh는 소유 표식과 준비 로그를 만든다. lab.sh의 up은 네임스페이스→veth·주소→라우터 전달 설정→경로→캡처 순서다. 전달 설정은 `ip netns exec`가 만든 별도 mount namespace의 임시 proc에서 적용하며 명령 종료 때 그 마운트도 사라진다. 네트워크 설정은 해당 라우터 netns에 남는다. return은 R2의 고정 경로 하나, link는 R1 transit0 하나, forward-restore는 R1의 B 경로 하나만 바꾼다. 임의 주소·인터페이스를 관리하는 스크립트가 아니다.

중단 시 down→필요 파일 복사→Compose down한다. 실습 down이 실패해도 소유 Compose 프로젝트 제거로 그 컨테이너의 네임스페이스·프로세스·링크를 정리할 수 있다. 전역 prune·다른 컨테이너 종료는 하지 않는다. [공식 근거](SOURCES.md#real-route) · [기존 모형](LINUX.md) · [학습 홈](README.md).
