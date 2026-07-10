"""
Process Monitoring Module

Collects runtime process information that can be used as
features for the ML classifier.
"""

import psutil


def get_process_features():
    """
    Returns process-related features.

    Output:
    {
        "process_count": ...,
        "high_cpu_processes": ...,
        "high_memory_processes": ...,
        "network_connections": ...
    }
    """

    process_count = 0
    high_cpu_processes = 0
    high_memory_processes = 0
    network_connections = 0

    for process in psutil.process_iter(
        ['pid', 'name', 'cpu_percent', 'memory_percent']
    ):
        try:
            process_count += 1

            cpu = process.info['cpu_percent']
            memory = process.info['memory_percent']

            if cpu > 20:
                high_cpu_processes += 1

            if memory > 10:
                high_memory_processes += 1

        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            continue

    try:
        network_connections = len(psutil.net_connections())
    except Exception:
        network_connections = 0

    return {
        "process_count": process_count,
        "high_cpu_processes": high_cpu_processes,
        "high_memory_processes": high_memory_processes,
        "network_connections": network_connections,
    }


if __name__ == "__main__":
    features = get_process_features()

    print("\nProcess Features\n")

    for key, value in features.items():
        print(f"{key}: {value}")