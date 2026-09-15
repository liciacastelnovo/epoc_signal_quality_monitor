#!/usr/bin/env python3
"""
Real-time contact quality monitor for the 14 EEG channels of the
Emotiv EPOC 1.0 headset, using the emokit library.

Usage:
    python check_signal_quality.py

Press Ctrl+C to exit.
"""

import os
import time
from emokit.emotiv import Emotiv

# Standard order of the EPOC's 14 EEG channels (International 10-20 system)
CHANNELS = [
    "AF3", "F7", "F3", "FC5", "T7", "P7", "O1",
    "O2", "P8", "T8", "FC6", "F4", "F8", "AF4",
]


# Divisor recommended by emokit's own protocol documentation
# (doc/emotiv_protocol.asciidoc) to turn the raw 14-bit quality reading
# into a more interpretable number, where ~0.8-1.0 indicates good contact.
QUALITY_SCALE = 540.0


def print_table(packet, last_battery):
    os.system("cls" if os.name == "nt" else "clear")
    print("EPOC contact quality — Ctrl+C to exit\n")
    print(f"{'Channel':<8} {'Value':>8} {'Quality (raw)':>14} {'Quality (scaled)':>17}")
    print("-" * 52)

    for ch in CHANNELS:
        sensor_data = packet.sensors.get(ch)
        if sensor_data is None:
            print(f"{ch:<8} {'--':>8} {'--':>14} {'--':>17}")
            continue
        value = sensor_data.get("value", 0)
        quality = sensor_data.get("quality", 0)
        scaled_quality = quality / QUALITY_SCALE
        print(f"{ch:<8} {value:>8} {quality:>14} {scaled_quality:>17.2f}")

    if last_battery is not None:
        print(f"\nBattery: {last_battery}")

    gyro_x = packet.sensors.get("X")
    gyro_y = packet.sensors.get("Y")
    if gyro_x is not None or gyro_y is not None:
        gx = gyro_x.get("value", 0) if gyro_x else "--"
        gy = gyro_y.get("value", 0) if gyro_y else "--"
        print(f"Gyro(x): {gx}   Gyro(y): {gy}")


def main():
    headset = Emotiv()
    time.sleep(1)
    last_battery = None

    try:
        while True:
            packet = headset.dequeue()
            if packet is not None:
                battery = getattr(packet, "battery", None)
                if battery is not None:
                    last_battery = battery
                print_table(packet, last_battery)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        headset.stop()


if __name__ == "__main__":
    main()