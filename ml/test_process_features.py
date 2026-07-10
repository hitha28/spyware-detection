"""
TEMPORARY: manually test extract_process_features against real, currently
running processes on this machine.
"""

from ml.features.extract_process_features import extract_features_for_all_processes

results = extract_features_for_all_processes()

# Sort by number of connections, descending, to see the "busiest" processes first
results.sort(key=lambda r: r["num_connections"], reverse=True)

print(f"Inspected {len(results)} running processes.\n")
print("Top 10 by network connections:")
for r in results[:10]:
    print(r)