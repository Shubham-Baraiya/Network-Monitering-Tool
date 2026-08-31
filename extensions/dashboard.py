# extensions/dashboard.py

import socket
import psutil

from flask import (
    Flask,
    jsonify,
    render_template
)

from modules.interface_monitor import (
    get_network_interfaces,
    get_interface_stats
)

from modules.host_discovery import (
    get_local_ipv4_info,
    discover_hosts
)

from modules.latency_monitor import (
    ping_target
)


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)


def get_active_interface():
    """
    Determine a usable active interface.
    """

    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for name, addresses in interfaces.items():

        if name not in stats:
            continue

        if not stats[name].isup:
            continue

        for address in addresses:

            if (
                address.family == socket.AF_INET
                and not address.address.startswith("127.")
            ):
                return name

    return None


def get_dashboard_data():
    """
    Collect data displayed on dashboard.
    """

    interface = get_active_interface()

    data = {
        "interface": interface,
        "download_mbps": 0,
        "upload_mbps": 0,
        "hosts": 0,
        "targets": []
    }

    if interface:

        stats = get_interface_stats(
            interface
        )

        if stats:

            data["total_received_mb"] = (
                stats.bytes_recv / (1024 ** 2)
            )

            data["total_sent_mb"] = (
                stats.bytes_sent / (1024 ** 2)
            )

            data["packets_received"] = (
                stats.packets_recv
            )

            data["packets_sent"] = (
                stats.packets_sent
            )

    network_info = get_local_ipv4_info()

    if network_info:

        try:

            hosts = discover_hosts(
                network_info["network_object"]
            )

            data["hosts"] = len(hosts)

        except Exception:
            data["hosts"] = 0

        data["ip"] = network_info["ip"]
        data["netmask"] = network_info["netmask"]
        data["network"] = network_info["network"]

    # These are intentionally configurable.
    # Replace with targets appropriate for your authorized network.
    targets = [
        "8.8.8.8",
        "1.1.1.1"
    ]

    for target in targets:

        rtt = ping_target(target)

        data["targets"].append({
            "target": target,
            "status": "UP" if rtt is not None else "DOWN",
            "rtt": (
                round(rtt, 2)
                if rtt is not None
                else None
            )
        })

    return data


@app.route("/")
def dashboard():
    """
    Render dashboard page.
    """

    return render_template(
        "dashboard.html"
    )


@app.route("/api/status")
def status():
    """
    Return current dashboard data as JSON.
    """

    return jsonify(
        get_dashboard_data()
    )


def run_dashboard(
    host="127.0.0.1",
    port=5000
):
    """
    Start Flask dashboard.
    """

    print(
        f"\nDashboard running at "
        f"http://{host}:{port}"
    )

    app.run(
        host=host,
        port=port,
        debug=False
    )


if __name__ == "__main__":
    run_dashboard()