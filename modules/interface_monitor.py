# modules/interface_monitor.py

import time
import psutil


def get_network_interfaces():
    """
    Return all available network interface names.
    """
    return list(psutil.net_if_addrs().keys())


def get_interface_addresses():
    """
    Return IPv4 information for all interfaces.
    """
    interfaces = psutil.net_if_addrs()
    result = {}

    for name, addresses in interfaces.items():
        result[name] = []

        for address in addresses:
            result[name].append({
                "family": str(address.family),
                "address": address.address,
                "netmask": address.netmask,
                "broadcast": address.broadcast
            })

    return result


def get_interface_stats(interface_name):
    """
    Get traffic counters for a specific interface.
    """
    counters = psutil.net_io_counters(pernic=True)

    return counters.get(interface_name)


def calculate_speed(previous_bytes, current_bytes, elapsed):
    """
    Calculate bits per second using two successive samples.
    """
    if elapsed <= 0:
        return 0.0

    byte_difference = current_bytes - previous_bytes

    return (byte_difference * 8) / elapsed


def format_speed(bits_per_second):
    """
    Convert bits/sec into readable units.
    """

    if bits_per_second >= 1_000_000_000:
        return f"{bits_per_second / 1_000_000_000:.2f} Gbps"

    if bits_per_second >= 1_000_000:
        return f"{bits_per_second / 1_000_000:.2f} Mbps"

    if bits_per_second >= 1_000:
        return f"{bits_per_second / 1_000:.2f} Kbps"

    return f"{bits_per_second:.2f} bps"


def get_interface_snapshot(interface_name):
    """
    Return current interface statistics.
    """

    stats = get_interface_stats(interface_name)

    if stats is None:
        return None

    return {
        "bytes_sent": stats.bytes_sent,
        "bytes_received": stats.bytes_recv,
        "packets_sent": stats.packets_sent,
        "packets_received": stats.packets_recv,
        "total_sent_mb": stats.bytes_sent / (1024 ** 2),
        "total_received_mb": stats.bytes_recv / (1024 ** 2)
    }


def monitor_interface(interface_name, interval=1):
    """
    Continuously monitor one network interface.
    """

    previous = get_interface_stats(interface_name)

    if previous is None:
        print(f"Interface '{interface_name}' not found.")
        return

    print("\n============================================")
    print("        NETWORK INTERFACE MONITOR")
    print("============================================")
    print(f"Interface: {interface_name}")
    print("Press CTRL+C to stop.")
    print("============================================")

    try:

        while True:

            start_time = time.monotonic()

            time.sleep(interval)

            current = get_interface_stats(interface_name)

            if current is None:
                print("\nInterface is no longer available.")
                break

            elapsed = max(
                time.monotonic() - start_time,
                0.001
            )

            upload = calculate_speed(
                previous.bytes_sent,
                current.bytes_sent,
                elapsed
            )

            download = calculate_speed(
                previous.bytes_recv,
                current.bytes_recv,
                elapsed
            )

            print("\033[H\033[J", end="")

            print("============================================")
            print("        NETWORK INTERFACE MONITOR")
            print("============================================")

            print(f"Interface        : {interface_name}")
            print(f"Download Speed   : {format_speed(download)}")
            print(f"Upload Speed     : {format_speed(upload)}")

            print()

            print(f"Packets Received : {current.packets_recv}")
            print(f"Packets Sent     : {current.packets_sent}")

            print()

            print(
                f"Total Received   : "
                f"{current.bytes_recv / (1024 ** 2):.2f} MB"
            )

            print(
                f"Total Sent       : "
                f"{current.bytes_sent / (1024 ** 2):.2f} MB"
            )

            print("============================================")
            print("Press CTRL+C to stop.")

            previous = current

    except KeyboardInterrupt:

        print("\nInterface monitoring stopped.")