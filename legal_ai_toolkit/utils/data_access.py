import json
from pathlib import Path

def load_processed_judgments():
    pkg_root = Path(__file__).parent.parent
    data_dir = pkg_root / "data" / "judgments"

    judgments = []
    if data_dir.exists():
        for file in data_dir.glob("*.json"):
            with open(file, encoding="utf-8") as f:
                judgments.append(json.load(f))
    return judgments

def load_clusters(refined=True):
    repo_root = Path(__file__).parent.parent.parent
    if refined:
        cluster_file = repo_root / "annotations" / "similarity" / "clusters_refined.json"
    else:
        cluster_file = repo_root / "annotations" / "similarity" / "clusters.json"

    if cluster_file.exists():
        with open(cluster_file, encoding="utf-8") as f:
            return json.load(f)
    return []

def get_repo_root():
    return Path(__file__).parent.parent.parent
