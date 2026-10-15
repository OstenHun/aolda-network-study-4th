"""두 IPv4 인터페이스의 CIDR 범위를 계산하는 2주차 학습 도구.

주소 계산만 하며 경로 선택이나 실제 통신을 시험하지 않는다.
"""

import argparse
from ipaddress import IPv4Interface


def print_interface_summary(label: str, interface: IPv4Interface) -> None:
    """한 인터페이스의 범위를 구하고 사람이 읽을 수 있는 이름으로 출력한다."""
    network = interface.network
    # /24·/26에서는 첫 주소와 마지막 주소를 일반 호스트에 배정하지 않는다.
    if network.num_addresses > 2:
        first_host = network.network_address + 1
        last_host = network.broadcast_address - 1
    else:
        # /31과 /32는 일반적인 네트워크/브로드캐스트 제외 규칙의 예외다.
        first_host = network.network_address
        last_host = network.broadcast_address

    print(f"{label}: {interface.ip}/{network.prefixlen}")
    print(f"  네트워크: {network.network_address}/{network.prefixlen}")
    print(f"  서브넷 마스크: {network.netmask}")
    print(f"  범위 끝 주소: {network.broadcast_address}")
    print(f"  호스트 주소 범위: {first_host} ~ {last_host}")


def main() -> None:
    # 1. 명령 뒤에 적은 A와 B의 주소/접두사를 읽는다.
    parser = argparse.ArgumentParser(
        description="두 IPv4 인터페이스의 CIDR 범위만 계산합니다. 통신 성공 여부는 알 수 없습니다."
    )
    parser.add_argument("a", type=IPv4Interface, help="A의 주소/접두사 (예: 192.0.2.10/24)")
    parser.add_argument("b", type=IPv4Interface, help="B의 주소/접두사 (예: 192.0.2.70/24)")
    args = parser.parse_args()
    interface_a = args.a
    interface_b = args.b

    # 2. 각 인터페이스의 네트워크·마스크·호스트 범위를 출력한다.
    print_interface_summary("A", interface_a)
    print_interface_summary("B", interface_b)

    # 3. A와 B의 접두사가 다를 수 있으므로 두 방향을 따로 판단한다.
    b_is_in_a_network = interface_b.ip in interface_a.network
    a_is_in_b_network = interface_a.ip in interface_b.network

    # 4. True/False 판단을 한국어 답으로 바꾼 뒤 출력한다.
    if b_is_in_a_network:
        a_answer = "예"
    else:
        a_answer = "아니요"

    if a_is_in_b_network:
        b_answer = "예"
    else:
        b_answer = "아니요"

    print(f"A 기준으로 B 포함: {a_answer}")
    print(f"B 기준으로 A 포함: {b_answer}")
    print("주의: 주소 포함 계산은 경로·링크·방화벽·상대 상태를 확인하지 않습니다.")


if __name__ == "__main__":
    main()
