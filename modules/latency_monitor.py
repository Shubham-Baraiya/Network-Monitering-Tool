# modules/latency_monitor.py

import platform
import subprocess
import statistics
import time


def ping_target(target, timeout=2):
    """
    Ping a target once.

    Returns:
        RTT in milliseconds if reachable.
        None if unreachable.
    """

    system = platform.system().lower()

    if system == "windows":
        command = [
            "ping",
            "-n",
            "1",
            "-w",
            str(timeout * 1000),
            target
        ]
    else:
        command = [
            "ping",
            "-c",
            "1",
            "-W",
            str(timeout),
            target
        ]

    try:
        start = time.perf_counter()

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 2
        )

        end = time.perf_counter()

        if result.returncode == 0:
            return (end - start) * 1000

    except (
        subprocess.TimeoutExpired,
        FileNotFoundError,
        OSError
    ):
        pass

    return None


def calculate_jitter(values):
    """
    Calculate average difference between
    consecutive successful RTT measurements.
    """

    if len(values) < 2:
        return 0.0

    differences = []

    for i in range(1, len(values)):
        differences.append(
            abs(values[i] - values[i - 1])
        )

    return statistics.mean(differences)


def calculate_latency_statistics(results):
    """
    Calculate min, average, max RTT,
    jitter and packet loss.
    """

    successful = [
        value for value in results
        if value is not None
    ]

    total = len(results)

    if total == 0:
        return {
            "status": "DOWN",
            "min": None,
            "avg": None,
            "max": None,
            "jitter": None,
            "loss": 100.0
        }

    packet_loss = (
        (total - len(successful))
        / total
        * 100
    )

    if not successful:
        return {
            "status": "DOWN",
            "min": None,
            "avg": None,
            "max": None,
            "jitter": None,
            "loss": 100.0
        }

    return {
        "status": "UP",
        "min": min(successful),
        "avg": statistics.mean(successful),
        "max": max(successful),
        "jitter": calculate_jitter(successful),
        "loss": packet_loss
    }


def monitor_target(
    target,
    samples=10,
    interval=1
):
    """
    Perform multiple ping measurements.
    """

    results = []

    for _ in range(samples):

        rtt = ping_target(target)

        results.append(rtt)

        time.sleep(interval)

    return calculate_latency_statistics(
        results
    )


def print_latency_results(results):
    """
    Display latency results.
    """

    print("\n============================================")
    print("        REACHABILITY & LATENCY")
    print("============================================")

    print(
        f"{'Target':<25}"
        f"{'Status':<10}"
        f"{'Min':<12}"
        f"{'Avg':<12}"
        f"{'Max':<12}"
        f"{'Loss':<10}"
    )

    print("-" * 80)

    for target, data in results.items():

        minimum = (
            f"{data['min']:.2f} ms"
            if data["min"] is not None
            else "-"
        )

        average = (
            f"{data['avg']:.2f} ms"
            if data["avg"] is not None
            else "-"
        )

        maximum = (
            f"{data['max']:.2f} ms"
            if data["max"] is not None
            else "-"
        )

        print(
            f"{target:<25}"
            f"{data['status']:<10}"
            f"{minimum:<12}"
            f"{average:<12}"
            f"{maximum:<12}"
            f"{data['loss']:.1f}%"
        )

        if data["jitter"] is not None:
            print(
                f"    Jitter: "
                f"{data['jitter']:.2f} ms"
            )

    print("-" * 80)


def run_latency_monitor(targets):
    """
    Monitor multiple network targets.
    """

    results = {}

    for target in targets:

        print(
            f"\nMonitoring {target}..."
        )

        results[target] = monitor_target(
            target,
            samples=10,
            interval=1
        )

    print_latency_results(results)

    return results