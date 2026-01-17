import json
import os
from collections import defaultdict
from pathlib import Path

# Universal filters
UNIVERSAL_ISSUES = {"jurisdiction", "maintainability", "limitation"}
UNIVERSAL_SECTIONS = {
    "IPC 1", "IPC 2", "IPC 3", "IPC 4", "IPC 5", "IPC 6", "IPC 7", "IPC 8", "IPC 9", "IPC 10",
    "IPC 34", "IPC 120B", "IPC 149", "IPC 1860", "IPC 1973", "IPC 2023", "IPC 2019", "IPC 1959"
}

def find_clusters_centroid(edges):
    adj = defaultdict(dict)
    edge_data = {}

    for edge in edges:
        u, v = edge["from"], edge["to"]

        # Filter signals
        shared_specific_issues = set(edge.get("signals", {}).get("shared_issues", [])) - UNIVERSAL_ISSUES
        shared_sections = set(edge.get("signals", {}).get("shared_sections", [])) - UNIVERSAL_SECTIONS
        shared_citations = set(edge.get("signals", {}).get("shared_citations", []))

        # Calculate clean weight
        weight = len(shared_specific_issues) + len(shared_sections) + len(shared_citations)

        # High threshold (10+) for direct clustering
        if edge.get("strength") == "high" and weight >= 10:
            adj[u][v] = weight
            adj[v][u] = weight
            edge_data[tuple(sorted((u, v)))] = edge.get("signals", {})

    node_degrees = {node: len(neighbors) for node, neighbors in adj.items()}
    sorted_nodes = sorted(node_degrees.keys(), key=lambda x: node_degrees[x], reverse=True)

    clusters = []
    assigned = set()

    for centroid in sorted_nodes:
        if centroid in assigned:
            continue

        current_cluster = [centroid]
        assigned.add(centroid)

        neighbors = adj[centroid]
        sorted_neighbors = sorted(neighbors.keys(), key=lambda x: neighbors[x], reverse=True)

        for n in sorted_neighbors:
            if n not in assigned:
                current_cluster.append(n)
                assigned.add(n)

        if len(current_cluster) > 1:
            clusters.append(current_cluster)

    return clusters, edge_data

def aggregate_basis(cluster_nodes, edge_data):
    """Aggregates shared signals across all edges in a cluster."""
    basis = {"issues": set(), "sections": set(), "citations": set()}

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

class CentroidClusteter:
    def __init__(self, edge_file, cluster_file):
        self.edge_file = Path(edge_file)
        self.cluster_file = Path(cluster_file)
        os.makedirs(self.cluster_file.parent, exist_ok=True)

    def run(self):
        if not self.edge_file.exists():
            print(f"[ERROR] Edge file not found: {self.edge_file}")
            return

        edges = []
        with open(self.edge_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    edges.append(json.loads(line))

        print(f"Loaded {len(edges)} similarity edges.")
        cluster_nodes_list, edge_data = find_clusters_centroid(edges)

        final_clusters = []
        for i, nodes in enumerate(cluster_nodes_list, start=1):
            basis = aggregate_basis(nodes, edge_data)

            final_clusters.append({
                "cluster_id": f"CLUSTER-{i:04d}",
                "centroid": nodes[0],
                "judgments": sorted(nodes),
                "count": len(nodes),
                "basis": basis,
                "confidence": "high"
            })

        with open(self.cluster_file, "w", encoding="utf-8") as f:
            json.dump(final_clusters, f, indent=2, ensure_ascii=False)

        print(f"Identified {len(final_clusters)} clusters. Saved to {self.cluster_file}.")
