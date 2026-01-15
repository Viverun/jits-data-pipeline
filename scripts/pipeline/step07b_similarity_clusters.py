import json
import os
from collections import defaultdict

EDGE_FILE = "annotations/similarity/edges.jsonl"
CLUSTER_FILE = "annotations/similarity/clusters.json"

def find_clusters(edges):
    """Finds connected components using BFS."""
    adj = defaultdict(list)
    edge_data = {}

    for edge in edges:
        u, v = edge["from"], edge["to"]
        adj[u].append(v)
        adj[v].append(u)
        # Store edge signals for basis aggregation
        edge_data[tuple(sorted((u, v)))] = edge["signals"]

    visited = set()
    clusters = []

    for node in list(adj.keys()):
        if node not in visited:
            # New cluster found
            component = []
            queue = [node]
            visited.add(node)
            
            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            clusters.append(component)
            
    return clusters, edge_data

def aggregate_basis(cluster_nodes, edge_data):
    """Aggregates shared signals across all edges in a cluster."""
    basis = {
        "issues": set(),
        "sections": set(),
        "citations": set()
    }
    
    # Look at all pairs in the cluster and collect shared signals if an edge exists
    for i in range(len(cluster_nodes)):
        for j in range(i + 1, len(cluster_nodes)):
            pair = tuple(sorted((cluster_nodes[i], cluster_nodes[j])))
            if pair in edge_data:
                signals = edge_data[pair]
                basis["issues"].update(signals.get("shared_issues", []))
                basis["sections"].update(signals.get("shared_sections", []))
                basis["citations"].update(signals.get("shared_citations", []))
                
    return {
        "issues": sorted(list(basis["issues"])),
        "sections": sorted(list(basis["sections"])),
        "citations": sorted(list(basis["citations"]))
    }

def main():
    if not os.path.exists(EDGE_FILE):
        print(f"❌ EDGE_FILE not found: {EDGE_FILE}")
        return

    edges = []
    with open(EDGE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                edges.append(json.loads(line))

    print(f"✔ Loaded {len(edges)} similarity edges")

    cluster_nodes_list, edge_data = find_clusters(edges)
    
    final_clusters = []
    for i, nodes in enumerate(cluster_nodes_list, start=1):
        basis = aggregate_basis(nodes, edge_data)
        
        final_clusters.append({
            "cluster_id": f"CLUSTER-{i:04d}",
            "judgments": sorted(nodes),
            "basis": basis,
            "confidence": "medium" # Defaulting to medium as per our edge strength
        })

    with open(CLUSTER_FILE, "w", encoding="utf-8") as f:
        json.dump(final_clusters, f, indent=2, ensure_ascii=False)

    print(f"✔ Identified {len(final_clusters)} clusters")
    print(f"✔ {CLUSTER_FILE} written")

if __name__ == "__main__":
    main()
