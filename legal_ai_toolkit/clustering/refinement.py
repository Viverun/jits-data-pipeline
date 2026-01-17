import json
import os
from collections import defaultdict
from pathlib import Path

def refine_mega_clusters(clusters, signal_dir, max_cluster_size=30):
    """
    Break mega-clusters into domain-specific sub-clusters
    """
    refined = []
    signal_dir = Path(signal_dir)

    for cluster in clusters:
        if cluster['count'] <= max_cluster_size:
            # Small cluster - keep as is
            refined.append(cluster)
        else:
            # Mega-cluster - split by primary issue
            print(f"[REFINING] {cluster['cluster_id']} has {cluster['count']} cases - splitting...")

            # Load signals for all judgments in cluster
            judgment_issues = {}
            for jid in cluster['judgments']:
                signal_file = signal_dir / f"{jid}.json"
                if signal_file.exists():
                    with open(signal_file) as f:
                        sig = json.load(f)
                        judgment_issues[jid] = sig.get('issues', [])

            # Group by primary issue (most frequent)
            issue_groups = defaultdict(list)
            for jid, issues in judgment_issues.items():
                if issues:
                    primary_issue = issues[0]  # First issue as primary
                    issue_groups[primary_issue].append(jid)
                else:
                    issue_groups['misc'].append(jid)

            # Create sub-clusters
            sub_id = 1
            for issue, jids in issue_groups.items():
                if len(jids) >= 2:  # Only create cluster if 2+ cases
                    sub_cluster = {
                        "cluster_id": f"{cluster['cluster_id']}-SUB{sub_id:02d}",
                        "parent_cluster": cluster['cluster_id'],
                        "centroid": jids[0],
                        "judgments": sorted(jids),
                        "count": len(jids),
                        "primary_issue": issue,
                        "basis": cluster.get('basis', {}),
                        "confidence": "high"
                    }
                    refined.append(sub_cluster)
                    sub_id += 1

    return refined

def filter_by_domain_purity(clusters, signal_dir):
    """
    Ensure clusters are domain-pure (criminal OR civil, not mixed)
    """
    filtered = []
    signal_dir = Path(signal_dir)

    for cluster in clusters:
        # Load domain info from signals
        domains = []
        for jid in cluster['judgments'][:10]:  # Sample first 10
            signal_file = signal_dir / f"{jid}.json"
            if signal_file.exists():
                with open(signal_file) as f:
                    sig = json.load(f)
                    domains.append(sig.get('domain', 'unknown'))

        # Check domain purity
        unique_domains = set(d for d in domains if d != 'unknown')
        if len(unique_domains) == 1 or 'mixed' in unique_domains:
            # Pure domain or explicitly mixed
            cluster['domain_purity'] = "high"
            filtered.append(cluster)
        elif len(unique_domains) <= 2:
            # Mostly pure
            cluster['domain_purity'] = "medium"
            filtered.append(cluster)
        else:
            # Too mixed - skip
            print(f"[FILTERED] {cluster['cluster_id']} - too many domains: {unique_domains}")

    return filtered

class ClusterRefiner:
    def __init__(self, cluster_file, refined_file, signal_dir):
        self.cluster_file = Path(cluster_file)
        self.refined_file = Path(refined_file)
        self.signal_dir = Path(signal_dir)

    def run(self, max_cluster_size=30):
        if not self.cluster_file.exists():
            print(f"[ERROR] Cluster file not found: {self.cluster_file}")
            return

        with open(self.cluster_file) as f:
            clusters = json.load(f)

        print(f"Loaded {len(clusters)} clusters.")

        # Step 1: Break mega-clusters
        refined = refine_mega_clusters(clusters, self.signal_dir, max_cluster_size=max_cluster_size)
        print(f"Refined to {len(refined)} clusters (mega-clusters split).")

        # Step 2: Filter by domain purity
        filtered = filter_by_domain_purity(refined, self.signal_dir)
        print(f"Filtered to {len(filtered)} domain-pure clusters.")

        # Sort by size (descending)
        filtered.sort(key=lambda x: x['count'], reverse=True)

        # Save refined clusters
        os.makedirs(self.refined_file.parent, exist_ok=True)
        with open(self.refined_file, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)

        print(f"Refined clusters saved to {self.refined_file}.")
