"""
Analyzes timing patterns of repeated contacts to a destination to detect
beaconing behavior — a classic C2 (command-and-control) spyware signal,
where infected devices "phone home" at suspiciously regular intervals.

This works on a list of timestamps (when contact occurred), rather than
raw packets directly — decoupling detection logic from live capture
mechanics (see packet_capture.py), so it can be tested against both
simulated and real timestamp data.
"""

import statistics


def analyze_intervals(timestamps: list[float]) -> dict:
    """
    Analyze the timing pattern of a list of contact timestamps.

    Args:
        timestamps: list of Unix timestamps (seconds), one per contact
            event, in chronological order.

    Returns:
        A dict of features describing the timing pattern, including
        whether it looks like regular beaconing.
    """
    if len(timestamps) < 3:
        return {
            "contact_count": len(timestamps),
            "mean_interval_seconds": 0.0,
            "stdev_interval_seconds": 0.0,
            "coefficient_of_variation": 0.0,
            "is_likely_beaconing": 0,
        }

    intervals = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
    mean_interval = statistics.mean(intervals)
    stdev_interval = statistics.stdev(intervals)

    # Coefficient of variation: stdev / mean. LOW value = very regular
    # timing (suspicious, beaconing-like). HIGH value = irregular timing
    # (normal human-driven browsing behavior).
    coefficient_of_variation = (stdev_interval / mean_interval) if mean_interval > 0 else 0.0

    # Threshold chosen deliberately conservative: real beaconing malware
    # is typically extremely regular (CoV well under 0.1-0.2); normal
    # browsing is highly irregular (CoV often 0.5-2.0+).
    is_likely_beaconing = 1 if coefficient_of_variation < 0.15 and len(timestamps) >= 5 else 0

    return {
        "contact_count": len(timestamps),
        "mean_interval_seconds": round(mean_interval, 2),
        "stdev_interval_seconds": round(stdev_interval, 2),
        "coefficient_of_variation": round(coefficient_of_variation, 3),
        "is_likely_beaconing": is_likely_beaconing,
    }