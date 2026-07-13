"""
Extracts numeric behavioral features from a running process, using psutil.

This targets the "process monitoring" part of Phase 2's original scope —
catching spyware based on how it BEHAVES while running, as a complement
to the permission-based static features (see extract_static_features.py).

Note: this is not yet wired into a trained model — there is no real
labeled dataset of "spyware process behavior" readily available the way
Drebin covers permissions. For now, this produces real, usable features;
a model trained specifically on these can be added once real labeled
process-behavior data is available (see docs/architecture.md).
"""

import psutil

# Names of processes/exes that are almost always safe, used to slightly
# reduce false positives for common system/background processes.
COMMON_SAFE_PROCESS_NAMES = {
    "svchost.exe", "explorer.exe", "chrome.exe", "code.exe",
    "python.exe", "systemd", "dockerd",
    "system idle process", "system",
}



def extract_process_features(pid: int) -> dict:
    """
    Extract behavioral features for a single running process.

    Args:
        pid: process ID to inspect.

    Returns:
        A dict of numeric/boolean features describing the process's
        current behavior.

    Raises:
        psutil.NoSuchProcess: if the pid doesn't correspond to a running process.
    """
    proc = psutil.Process(pid)

    with proc.oneshot():  # batches syscalls for efficiency
        name = proc.name()
        cpu_percent = proc.cpu_percent(interval=0.1)
        memory_percent = proc.memory_percent()
        num_threads = proc.num_threads()

        try:
            num_connections = len(proc.net_connections(kind="inet"))
        except (psutil.AccessDenied, AttributeError):
            num_connections = 0

        try:
            num_open_files = len(proc.open_files())
        except psutil.AccessDenied:
            num_open_files = 0

        try:
            create_time = proc.create_time()
        except psutil.AccessDenied:
            create_time = 0

    return {
        "cpu_percent": cpu_percent,
        "memory_percent": round(memory_percent, 2),
        "num_threads": num_threads,
        "num_connections": num_connections,
        "num_open_files": num_open_files,
        "is_common_safe_process": 1 if name.lower() in COMMON_SAFE_PROCESS_NAMES else 0,
        "high_connection_count": 1 if num_connections > 10 else 0,
        "high_thread_count": 1 if num_threads > 20 else 0,
    }


def extract_features_for_all_processes() -> list[dict]:
    """
    Extract features for every currently running process on this machine.

    Returns:
        A list of dicts, each containing the pid, process name, and
        extracted features for one running process.
    """
    results = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            features = extract_process_features(proc.info["pid"])
            results.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                **features,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process ended or we lack permission — skip it, not an error
            continue
    return results