#!/usr/bin/env bash
# 선택 실습: 이 실행이 만든 네트워크 네임스페이스와 veth만 사용하고 종료 시 정리한다.
# 읽는 순서: 준비 확인 → 정리 약속 → 관찰 함수 → 맨 아래 세 실험.
# 자세한 문법·명령 설명은 같은 폴더의 CODE_READING.md를 참고한다.
# -e: 처리하지 않은 실패에서 중단, -u: 없는 변수 사용 시 중단, pipefail: 파이프 실패 확인.
set -euo pipefail

# 준비 확인: 실제 네트워크 자원을 만들기 전에 권한과 도구부터 확인한다.
if [[ ${EUID} -ne 0 ]]; then
  echo '관리자 권한이 필요합니다. 허가된 격리 Linux에서 sudo bash로 실행하세요.' >&2
  exit 1
fi
for tool in ip ping; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "필요한 도구가 없습니다: $tool" >&2
    exit 1
  fi
done

# Linux 인터페이스 이름 길이를 고려하고, 실행끼리 이름이 겹칠 가능성을 줄인다.
suffix="${BASHPID}${RANDOM}"
ns_a="aolda-w2-a-${suffix}"
ns_b="aolda-w2-b-${suffix}"
veth_a="w2a${suffix}"
veth_b="w2b${suffix}"
created_ns_a=0
created_ns_b=0
created_veth=0

# 종료 정리: 함수 정의만으로 실행되지 않는다. 아래 trap이 종료 시 호출한다.
cleanup() {
  # 다른 명령이 값을 덮어쓰기 전에 실험의 종료 상태부터 보관한다.
  local original_status=$?
  local cleanup_failed=0
  trap - EXIT
  # 플래그가 세워진 이 실행의 자원만 지운다. 기존 네임스페이스는 건드리지 않는다.
  if [[ ${created_veth} -eq 1 ]]; then
    # 이동 전 실패했다면 veth가 기본 네임스페이스에 남아 있을 수 있다.
    if ip link show dev "$veth_a" >/dev/null 2>&1; then
      if ! ip link del dev "$veth_a"; then
        echo "정리 실패: 호스트 veth $veth_a" >&2
        cleanup_failed=1
      fi
    fi
  fi
  if [[ ${created_ns_a} -eq 1 ]]; then
    if ! ip netns del "$ns_a"; then
      echo "정리 실패: 네임스페이스 $ns_a" >&2
      cleanup_failed=1
    fi
  fi
  if [[ ${created_ns_b} -eq 1 ]]; then
    if ! ip netns del "$ns_b"; then
      echo "정리 실패: 네임스페이스 $ns_b" >&2
      cleanup_failed=1
    fi
  fi
  if [[ ${cleanup_failed} -eq 1 ]]; then
    echo "남은 자원 확인 이름: 네임스페이스 $ns_a, $ns_b; veth $veth_a, $veth_b" >&2
    if [[ ${original_status} -eq 0 ]]; then
      original_status=1
    fi
  fi
  exit "$original_status"
}
# 정상 종료·오류 종료에서 정리한다. INT(Ctrl+C)·TERM도 종료 후 EXIT로 이어진다.
# 강제 종료(SIGKILL) 등 trap이 실행될 수 없는 상황까지 정리를 보장하지는 않는다.
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# 관찰 함수: 실행할 명령을 먼저 보여 주고, 전달받은 인자를 그대로 실행한다.
run_show() {
  printf '$'
  printf ' %q' "$@"
  printf '\n'
  "$@"
}

# 주소 계산과 실제 경로 선택을 비교하기 위해 양쪽 상태를 모두 출력한다.
show_state() {
  echo 'A 주소:'
  run_show ip -n "$ns_a" -br -4 addr
  echo 'A 경로:'
  run_show ip -n "$ns_a" -4 route
  echo 'B 주소:'
  run_show ip -n "$ns_b" -br -4 addr
  echo 'B 경로:'
  run_show ip -n "$ns_b" -4 route
}

# ping 실패도 실험 결과다. if/else로 종료 상태를 잡아 호출한 곳에 돌려준다.
ping_and_report() {
  local status
  if run_show ip netns exec "$ns_a" ping -n -c 1 -W 2 192.0.2.70; then
    status=0
  else
    status=$?  # 실패 직후의 종료 코드. echo보다 먼저 저장해야 한다.
  fi
  echo "ping 종료 상태: $status"
  return "$status"
}

# 실험 환경: 독립된 두 네트워크 공간을 가상 케이블 한 쌍으로 잇는다.
# 기존 VM의 SSH 관리 NIC·기본 경로는 변경하지 않는다.
echo "이번 실행 자원: $ns_a, $ns_b, $veth_a, $veth_b"
run_show ip netns add "$ns_a"
created_ns_a=1
run_show ip netns add "$ns_b"
created_ns_b=1
run_show ip link add "$veth_a" type veth peer name "$veth_b"
created_veth=1
run_show ip link set dev "$veth_a" netns "$ns_a"
run_show ip link set dev "$veth_b" netns "$ns_b"

run_show ip -n "$ns_a" link set dev lo up
run_show ip -n "$ns_b" link set dev lo up
run_show ip -n "$ns_a" link set dev "$veth_a" up
run_show ip -n "$ns_b" link set dev "$veth_b" up
run_show ip -n "$ns_a" address add 192.0.2.10/24 dev "$veth_a"
run_show ip -n "$ns_b" address add 192.0.2.70/24 dev "$veth_b"

# 실험 1: 기준 상태를 먼저 확인한다. 여기서 실패하면 중단하고 종료 정리한다.
echo '1. 양쪽 /24: A의 경로와 B로 향한 ICMP'
show_state
run_show ip -n "$ns_a" -4 route get 192.0.2.70
ping_and_report

# 실험 2: A의 접두사만 바꾼다. B는 /24이며 기본 경로를 추가하지 않는다.
echo '2. A만 /26: 게이트웨이 없이 A의 경로와 ICMP 재확인'
run_show ip -n "$ns_a" address del 192.0.2.10/24 dev "$veth_a"
run_show ip -n "$ns_a" address add 192.0.2.10/26 dev "$veth_a"
show_state
# 이 단계의 조회·ping 실패는 예상 비교 조건이므로 if/else로 처리하고 계속한다.
if run_show ip -n "$ns_a" -4 route get 192.0.2.70; then
  echo '예상과 달리 경로가 있습니다. 실제 경로를 기록하고 원인을 확인하세요.'
else
  echo 'A에서 B로 향한 경로 조회 실패 (예상 조건).'
fi
if ping_and_report; then
  echo '예상과 달리 응답이 있습니다. 실제 출력을 기록하고 원인을 확인하세요.'
else
  echo 'A에서 B로 향한 ping 실패 (예상 조건).'
fi

# 실험 3: 원래 /24로 되돌린 뒤 기준 상태가 돌아오는지 확인한다.
echo '3. A를 /24로 복구하고 다시 확인'
run_show ip -n "$ns_a" address del 192.0.2.10/26 dev "$veth_a"
run_show ip -n "$ns_a" address add 192.0.2.10/24 dev "$veth_a"
show_state
run_show ip -n "$ns_a" -4 route get 192.0.2.70
ping_and_report
echo '종료하면서 이번 실행의 두 네임스페이스와 veth를 정리합니다.'
