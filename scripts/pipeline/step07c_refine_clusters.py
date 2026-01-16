import json
import os
from collections import defaultdict

CLUSTER_FILE = "annotations/similarity/clusters.json"
REFINED_CLUSTER_FILE = "annotations/similarity/clusters_refined.json"
SIGNAL_DIR = "annotations/similarity/signals"

def refine_mega_clusters(clusters, max_cluster_size=30):
    """
    Break mega-clusters into domain-specific sub-clusters
    """
    refined = []
    
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
                signal_file = os.path.join(SIGNAL_DIR, f"{jid}.json")
                if os.path.exists(signal_file):
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

def filter_by_domain_purity(clusters):
    """
    Ensure clusters are domain-pure (criminal OR civil, not mixed)
    """
    filtered = []
    
    for cluster in clusters:
        # Load domain info from signals
        domains = []
        for jid in cluster['judgments'][:10]:  # Sample first 10
            signal_file = os.path.join(SIGNAL_DIR, f"{jid}.json")
            if os.path.exists(signal_file):
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

def main():
    if not os.path.exists(CLUSTER_FILE):
        print(f"[ERROR] Cluster file not found: {CLUSTER_FILE}")
        return
    
    with open(CLUSTER_FILE) as f:
        clusters = json.load(f)
    
    print(f"[OK] Loaded {len(clusters)} clusters")
    
    # Step 1: Break mega-clusters
    refined = refine_mega_clusters(clusters, max_cluster_size=30)
    print(f"[OK] Refined to {len(refined)} clusters (mega-clusters split)")
    
    # Step 2: Filter by domain purity
    filtered = filter_by_domain_purity(refined)
    print(f"[OK] Filtered to {len(filtered)} domain-pure clusters")
    
    # Sort by size (descending)
    filtered.sort(key=lambda x: x['count'], reverse=True)
    
    # Save refined clusters
    with open(REFINED_CLUSTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Refined clusters saved to {REFINED_CLUSTER_FILE}")
    
    # Summary
    print("\n📊 Refined Cluster Summary:")
    for c in filtered[:10]:  # Show top 10
        print(f"  {c['cluster_id']}: {c['count']} cases - {c.get('primary_issue', 'mixed')}")

if __name__ == "__main__":
    main()
