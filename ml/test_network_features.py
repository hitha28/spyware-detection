"""
TEMPORARY: manually test extract_network_features against real, currently
active network connections on this machine.
"""

from ml.features.extract_network_features import extract_network_features_for_all_processes

results = extract_network_features_for_all_processes()
results.sort(key=lambda r: r["total_connections"], reverse=True)

print(f"Found {len(results)} processes with active network connections.\n")
for r in results[:10]:
    print(r)