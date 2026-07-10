"""
Network Monitoring Module

Collects basic network statistics for the ML model.
"""

import psutil


def get_network_features():
    """
    Returns basic network-related features.

    Output:
    {
        "total_connections": ...,
        "established_connections": ...,
        "listening_ports": ...
    }
    """

    total_connections = 0
    established_connections = 0
    listening_ports = 0

    try:
        connections = psutil.net_connections()

        total_connections = len(connections)

        for conn in connections:

            if conn.status == "ESTABLISHED":
                established_connections += 1

            elif conn.status == "LISTEN":
                listening_ports += 1

    except Exception:
        pass

    return {
        "total_connections": total_connections,
        "established_connections": established_connections,
        "listening_ports": listening_ports
    }


if __name__ == "__main__":

    features = get_network_features()

    print("\nNetwork Features\n")

    for key, value in features.items():
        print(f"{key}: {value}")