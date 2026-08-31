# modules/host_discovery.py

import socket
import ipaddress
import psutil

from scapy.all import ARP, Ether, srp


def get_local_ipv4_info():
    """
    Detect the computer's active IPv4 address and subnet mask.
    """

    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for interface_name, addresses in interfaces.items():

        if interface_name not in stats:
            continue

        if not stats[interface_name].isup:
            continue

        for address in addresses:

            if address.family == socket.AF_INET:

                ip = address.address
                mask = address.netmask

                if ip.startswith("127."):
                    continue

                if not mask:
                    continue

                network = ipaddress.ip_network(
                    f"{ip}/{mask}",
                    strict=False
                )

                return {
                    "interface": interface_name,
                    "ip": ip,
                    "netmask": mask,
                    "network": str(network),
                    "network_object": network
                }

    return None


def get_hostname(ip_address):
    """
    Try to resolve an IP address to a hostname.
    """

    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname

    except (socket.herror, socket.gaierror, OSError):
        return "Unknown"


def discover_hosts(network):
    """
    Discover live devices using ARP.

    IMPORTANT:
    Only use this on a network you are authorized to monitor.
    """

    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(
        pdst=str(network)
    )

    try:

        answered, _ = srp(
            packet,
            timeout=3,
            verbose=False
        )

    except PermissionError:

        print(
            "Permission denied. Run the program with "
            "administrator privileges for ARP scanning."
        )

        return []

    except Exception as error:

        print(f"Host discovery error: {error}")
        return []

    devices = []

    for _, response in answered:

        ip = response.psrc
        mac = response.hwsrc

        devices.append({
            "ip": ip,
            "mac": mac,
            "hostname": get_hostname(ip)
        })

    devices.sort(
        key=lambda device: ipaddress.ip_address(device["ip"])
    )

    return devices


def print_discovered_hosts(devices):
    """
    Display discovered devices.
    """

    print("\n============================================")
    print("           LOCAL HOST DISCOVERY")
    print("============================================")

    if not devices:

        print("No live hosts found.")
        return

    print(
        f"{'IP Address':<18}"
        f"{'MAC Address':<20}"
        f"{'Hostname'}"
    )

    print("-" * 70)

    for device in devices:

        print(
            f"{device['ip']:<18}"
            f"{device['mac']:<20}"
            f"{device['hostname']}"
        )

    print("-" * 70)
    print(f"Live Hosts: {len(devices)}")


def run_host_discovery():
    """
    Detect local subnet and discover live devices.
    """

    info = get_local_ipv4_info()

    if info is None:

        print(
            "Could not automatically determine "
            "an active IPv4 interface."
        )

        return []

    print("\n============================================")
    print("           NETWORK INFORMATION")
    print("============================================")

    print(f"Interface    : {info['interface']}")
    print(f"IPv4 Address : {info['ip']}")
    print(f"Subnet Mask  : {info['netmask']}")
    print(f"Network      : {info['network']}")

    print("\nScanning local subnet...")

    devices = discover_hosts(
        info["network_object"]
    )

    print_discovered_hosts(devices)

    return devices