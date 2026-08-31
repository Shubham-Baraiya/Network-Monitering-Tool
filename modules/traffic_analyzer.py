# modules/traffic_analyzer.py

from collections import defaultdict

from scapy.all import (
    sniff,
    IP,
    TCP,
    UDP,
    ICMP,
    ARP,
    DNS,
    Raw
)


PROTOCOLS = [
    "TCP",
    "UDP",
    "ICMP",
    "ARP",
    "DNS",
    "HTTP/HTTPS",
    "Other"
]


def classify_packet(packet):
    """
    Classify a packet into one of the required categories.
    """

    if packet.haslayer(ARP):
        return "ARP"

    if packet.haslayer(DNS):
        return "DNS"

    if packet.haslayer(TCP):

        if packet.haslayer(Raw):

            try:

                payload = bytes(
                    packet[Raw].load
                ).lower()

                if (
                    b"http" in payload
                    or b"get " in payload
                    or b"post " in payload
                ):
                    return "HTTP/HTTPS"

            except Exception:
                pass

        return "TCP"

    if packet.haslayer(UDP):
        return "UDP"

    if packet.haslayer(ICMP):
        return "ICMP"

    return "Other"


def analyze_packets(packets):
    """
    Analyze captured packets.
    """

    protocol_packets = defaultdict(int)
    protocol_bytes = defaultdict(int)

    source_bytes = defaultdict(int)
    destination_bytes = defaultdict(int)

    source_packets = defaultdict(int)
    destination_packets = defaultdict(int)

    for packet in packets:

        protocol = classify_packet(packet)

        size = len(packet)

        protocol_packets[protocol] += 1
        protocol_bytes[protocol] += size

        if packet.haslayer(IP):

            source = packet[IP].src
            destination = packet[IP].dst

            source_bytes[source] += size
            destination_bytes[destination] += size

            source_packets[source] += 1
            destination_packets[destination] += 1

    for protocol in PROTOCOLS:

        protocol_packets.setdefault(
            protocol,
            0
        )

        protocol_bytes.setdefault(
            protocol,
            0
        )

    return {
        "protocol_packets": dict(protocol_packets),
        "protocol_bytes": dict(protocol_bytes),
        "source_bytes": dict(source_bytes),
        "destination_bytes": dict(destination_bytes),
        "source_packets": dict(source_packets),
        "destination_packets": dict(destination_packets)
    }


def capture_traffic(
    interface=None,
    packet_count=100,
    duration=None
):
    """
    Capture packets from an interface.

    Use either packet_count or duration.
    """

    print("\nStarting packet capture...")

    try:

        packets = sniff(
            iface=interface,
            count=packet_count if duration is None else 0,
            timeout=duration,
            store=True
        )

        print(
            f"Captured {len(packets)} packets."
        )

        return packets

    except PermissionError:

        print(
            "Permission denied. Packet capture "
            "may require administrator privileges."
        )

        return []

    except Exception as error:

        print(f"Packet capture error: {error}")

        return []


def get_top_talkers(data, limit=5):
    """
    Return busiest source and destination IPs.
    """

    sources = sorted(
        data["source_bytes"].items(),
        key=lambda item: item[1],
        reverse=True
    )[:limit]

    destinations = sorted(
        data["destination_bytes"].items(),
        key=lambda item: item[1],
        reverse=True
    )[:limit]

    return sources, destinations


def print_traffic_analysis(data):
    """
    Display traffic analysis.
    """

    print("\n============================================")
    print("          TRAFFIC COMPOSITION")
    print("============================================")

    print(
        f"{'Protocol':<15}"
        f"{'Packets':<15}"
        f"{'Bytes':<15}"
    )

    print("-" * 45)

    for protocol in PROTOCOLS:

        packets = data["protocol_packets"].get(
            protocol,
            0
        )

        bytes_count = data["protocol_bytes"].get(
            protocol,
            0
        )

        print(
            f"{protocol:<15}"
            f"{packets:<15}"
            f"{bytes_count:<15}"
        )

    sources, destinations = get_top_talkers(
        data
    )

    print("\n============================================")
    print("              TOP SOURCE IPs")
    print("============================================")

    for ip, bytes_count in sources:

        print(
            f"{ip:<20}"
            f"{bytes_count} bytes"
        )

    print("\n============================================")
    print("           TOP DESTINATION IPs")
    print("============================================")

    for ip, bytes_count in destinations:

        print(
            f"{ip:<20}"
            f"{bytes_count} bytes"
        )


def run_traffic_analyzer(
    interface=None,
    packet_count=100
):
    """
    Capture and analyze traffic.
    """

    packets = capture_traffic(
        interface=interface,
        packet_count=packet_count
    )

    if not packets:
        return {}

    data = analyze_packets(packets)

    print_traffic_analysis(data)

    return data