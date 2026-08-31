# main.py

from modules.interface_monitor import (
    get_network_interfaces,
    monitor_interface
)

from modules.host_discovery import (
    run_host_discovery
)

from modules.latency_monitor import (
    run_latency_monitor
)

from modules.traffic_analyzer import (
    run_traffic_analyzer
)

from extensions.history_logger import (
    generate_throughput_chart,
    generate_latency_chart
)

from extensions.dashboard import (
    run_dashboard
)


def show_banner():

    print("""
===============================================
        NETWORK MONITORING TOOL
        Computer Networks PBL
===============================================
""")


def select_interface():

    interfaces = get_network_interfaces()

    if not interfaces:

        print(
            "No network interfaces found."
        )

        return None

    print("\nAvailable Interfaces:")

    for index, interface in enumerate(
        interfaces,
        start=1
    ):

        print(
            f"{index}. {interface}"
        )

    try:

        choice = int(
            input(
                "\nSelect interface number: "
            )
        )

        if not 1 <= choice <= len(interfaces):

            print(
                "Invalid interface."
            )

            return None

        return interfaces[
            choice - 1
        ]

    except ValueError:

        print(
            "Please enter a valid number."
        )

        return None


def run_c1():

    interface = select_interface()

    if interface:

        monitor_interface(
            interface,
            interval=1
        )


def run_c2():

    run_host_discovery()


def run_c3():

    print("\nEnter the targets to monitor.")

    print(
        "Example: your gateway, "
        "a public DNS resolver and a website."
    )

    targets = []

    for i in range(3):

        target = input(
            f"Target {i + 1}: "
        ).strip()

        if target:

            targets.append(target)

    if not targets:

        print(
            "No targets entered."
        )

        return

    run_latency_monitor(
        targets
    )


def run_c4():

    interface = select_interface()

    if not interface:
        return

    try:

        count = int(
            input(
                "\nNumber of packets to capture "
                "(default 100): "
            )
        )

    except ValueError:

        count = 100

    run_traffic_analyzer(
        interface=interface,
        packet_count=count
    )


def run_e3():

    print("\n============================================")
    print("       HISTORICAL DATA & CHARTS")
    print("============================================")

    print(
        "\n1. Generate Throughput Chart"
    )

    print(
        "2. Generate Latency Chart"
    )

    choice = input(
        "\nEnter choice: "
    ).strip()

    if choice == "1":

        generate_throughput_chart()

    elif choice == "2":

        generate_latency_chart()

    else:

        print(
            "Invalid choice."
        )


def run_e5():

    run_dashboard(
        host="127.0.0.1",
        port=5000
    )


def show_menu():

    print("""
===============================================
              MAIN MENU
===============================================

1. C1 - Interface Traffic Monitor
2. C2 - Local Subnet Host Discovery
3. C3 - Reachability & Latency Monitor
4. C4 - Traffic Composition Analyzer
5. E3 - Historical Logging & Charts
6. E5 - Auto-refresh Dashboard

0. Exit

===============================================
""")


def main():

    show_banner()

    while True:

        show_menu()

        choice = input(
            "Enter your choice: "
        ).strip()

        try:

            if choice == "1":

                run_c1()

            elif choice == "2":

                run_c2()

            elif choice == "3":

                run_c3()

            elif choice == "4":

                run_c4()

            elif choice == "5":

                run_e3()

            elif choice == "6":

                run_e5()

            elif choice == "0":

                print(
                    "\nThank you for using "
                    "Network Monitoring Tool."
                )

                break

            else:

                print(
                    "\nInvalid choice."
                )

        except KeyboardInterrupt:

            print(
                "\n\nOperation cancelled."
            )

        except Exception as error:

            print(
                f"\nUnexpected error: {error}"
            )


if __name__ == "__main__":
    main()