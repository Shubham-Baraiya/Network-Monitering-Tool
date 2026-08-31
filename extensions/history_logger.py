# extensions/history_logger.py

import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt

from config import HISTORY_FILE


def ensure_data_directory():
    """
    Create data directory if it doesn't exist.
    """

    directory = os.path.dirname(HISTORY_FILE)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )


def initialize_history_file():
    """
    Create CSV file with headers.
    """

    ensure_data_directory()

    if not os.path.exists(HISTORY_FILE):

        with open(
            HISTORY_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "interface",
                "download_mbps",
                "upload_mbps",
                "average_rtt_ms",
                "packet_loss_percent"
            ])


def save_measurement(
    interface,
    download_mbps,
    upload_mbps,
    average_rtt_ms,
    packet_loss_percent
):
    """
    Save one network measurement.
    """

    initialize_history_file()

    with open(
        HISTORY_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            interface,
            round(download_mbps, 3),
            round(upload_mbps, 3),
            (
                round(average_rtt_ms, 3)
                if average_rtt_ms is not None
                else ""
            ),
            round(packet_loss_percent, 3)
        ])


def read_history():
    """
    Read all stored measurements.
    """

    initialize_history_file()

    with open(
        HISTORY_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        return list(
            csv.DictReader(file)
        )


def generate_throughput_chart(
    output_file="charts/throughput_history.png"
):
    """
    Generate throughput vs time chart.
    """

    rows = read_history()

    if not rows:

        print("No historical data available.")
        return None

    timestamps = []
    downloads = []
    uploads = []

    for row in rows:

        try:

            timestamps.append(
                datetime.strptime(
                    row["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            downloads.append(
                float(row["download_mbps"])
            )

            uploads.append(
                float(row["upload_mbps"])
            )

        except (ValueError, KeyError):
            continue

    if not timestamps:
        return None

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        timestamps,
        downloads,
        label="Download Mbps"
    )

    plt.plot(
        timestamps,
        uploads,
        label="Upload Mbps"
    )

    plt.xlabel("Time")
    plt.ylabel("Speed (Mbps)")
    plt.title("Network Throughput History")

    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(output_file)
    plt.close()

    print(
        f"Chart generated: {output_file}"
    )

    return output_file


def generate_latency_chart(
    output_file="charts/latency_history.png"
):
    """
    Generate average RTT vs time chart.
    """

    rows = read_history()

    timestamps = []
    latency = []

    for row in rows:

        try:

            if not row["average_rtt_ms"]:
                continue

            timestamps.append(
                datetime.strptime(
                    row["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            latency.append(
                float(row["average_rtt_ms"])
            )

        except (ValueError, KeyError):
            continue

    if not timestamps:
        print("No latency history available.")
        return None

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        timestamps,
        latency,
        label="Average RTT"
    )

    plt.xlabel("Time")
    plt.ylabel("RTT (ms)")
    plt.title("Network Latency History")

    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(output_file)
    plt.close()

    print(
        f"Chart generated: {output_file}"
    )

    return output_file