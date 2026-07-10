"""
Extracts numeric behavioral features from network connection data.

This targets the "network monitoring" part of Phase 2's original scope —
catching spyware based on suspicious network behavior (beaconing,
contacting unusual destinations), as a complement to permission-based
features (extract_static_features.py) and process features
(extract_process_features.py).

Note: like extract_process_features.py, there's no readily available
real labeled dataset for "malicious network behavior" the way Drebin
covers permissions. This produces real, genuine features from real
connection data — but training a model on these requires either a real
labeled network dataset or carefully constructed synthetic traffic
patterns (see docs/architecture.md for this caveat).
"""

from collections import Counter

import psutil


def extract_network_features_for_process(pid: int) -> dict:
    """
    Extract network-behavior features for a single process's current
    connections.

    Args:
        pid: process ID to inspect.

    Returns:
        A dict of numeric features describing the process's network activity.
    """
    try:
        proc = psutil.Process(pid)
        connections = proc.net_connections(kind="inet")
    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
        connections = []

    remote_ips = [
        conn.raddr.ip for conn in connections
        if conn.raddr and getattr(conn.raddr, "ip", None)
    ]
    unique_ips = set(remote_ips)

    # A crude "repeat contact" signal: does this process talk to the same
    # small set of IPs repeatedly? (a loose proxy for beaconing behavior,
    # without needing to watch traffic over time)
    ip_counts = Counter(remote_ips)
    max_repeat_count = max(ip_counts.values()) if ip_counts else 0

    established_count = sum(
        1 for conn in connections if conn.status == "ESTABLISHED"
    )

    return {
        "total_connections": len(connections),
        "unique_remote_ips": len(unique_ips),
        "established_connections": established_count,
        "max_repeated_ip_contact": max_repeat_count,
        "low_ip_diversity": 1 if 0 < len(unique_ips) <= 2 and len(connections) > 3 else 0,
    }


def extract_network_features_for_all_processes() -> list[dict]:
    """
    Extract network-behavior features for every currently running
    process that has active connections.

    Returns:
        A list of dicts, each with pid, process name, and network features.
    """
    results = []
    for proc in psutil.process_iter(["pid", "name"]):
        features = extract_network_features_for_process(proc.info["pid"])
        if features["total_connections"] > 0:
            results.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                **features,
            })
    return results