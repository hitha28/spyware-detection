"""
TEMPORARY: tests dns_analyzer.py's beaconing detection against two
simulated timing patterns:
  1. Regular beaconing (like C2 malware "phoning home" every ~30s)
  2. Irregular browsing (like normal human-driven web traffic)

This validates the DETECTION LOGIC using controlled, synthetic timing
data — since we can't ethically generate or capture real malware C2
traffic. See docs/architecture.md for this caveat.
"""

import random
import time

from ml.netwrok.dns_analyzer import analyze_intervals


def simulate_beaconing_timestamps(count: int = 20, interval_seconds: float = 30.0) -> list[float]:
    """Simulate a process contacting a destination at very regular
    intervals, with only tiny natural jitter (like real beaconing malware)."""
    now = time.time()
    timestamps = []
    for i in range(count):
        jitter = random.uniform(-0.5, 0.5)  # +/- half a second, minimal
        timestamps.append(now + i * interval_seconds + jitter)
    return timestamps


def simulate_normal_browsing_timestamps(count: int = 20) -> list[float]:
    """Simulate irregular, human-driven browsing contact — gaps vary
    wildly, like a person clicking around a website."""
    now = time.time()
    timestamps = []
    current = now
    for _ in range(count):
        gap = random.uniform(1, 120)  # anywhere from 1 second to 2 minutes
        current += gap
        timestamps.append(current)
    return timestamps


beaconing_timestamps = simulate_beaconing_timestamps()
browsing_timestamps = simulate_normal_browsing_timestamps()

print("=== Simulated BEACONING pattern (like C2 malware) ===")
print(analyze_intervals(beaconing_timestamps))

print("\n=== Simulated NORMAL BROWSING pattern ===")
print(analyze_intervals(browsing_timestamps))