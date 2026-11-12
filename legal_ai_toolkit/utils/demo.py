import json
import os
import shutil
from pathlib import Path

class ShowcasePreparer:
    def __init__(self, cluster_file, processed_dir, demo_dir):
        self.cluster_file = Path(cluster_file)
        self.processed_dir = Path(processed_dir)
        self.demo_dir = Path(demo_dir)
        os.makedirs(self.demo_dir, exist_ok=True)

    def prepare(self):
        if not self.cluster_file.exists():
            print("Refined cluster file not found.")
            return

        with open(self.cluster_file) as f:
            clusters = json.load(f)

        # Find best clusters for demo
        demo_clusters = {
            'service_promotion': None,
            'bail_498a': None,
            'dowry_death_304b': None,
            'arbitration': None,
            'pension': None
        }

        for cluster in clusters:
            primary = cluster.get('primary_issue', '')

            if 'seniority_promotion' in primary and cluster['count'] >= 10:
                if not demo_clusters['service_promotion']:
                    demo_clusters['service_promotion'] = cluster

            elif 'bail' in primary and cluster['count'] >= 8:
                basis_sections = cluster.get('basis', {}).get('sections', [])
                if any('498' in s for s in basis_sections):
                    if not demo_clusters['bail_498a']:
                        demo_clusters['bail_498a'] = cluster

            elif 'sentencing' in primary and cluster['count'] >= 8:
                basis_sections = cluster.get('basis', {}).get('sections', [])
                if any('304B' in s for s in basis_sections):
                    if not demo_clusters['dowry_death_304b']:
                        demo_clusters['dowry_death_304b'] = cluster

            elif 'pension' in primary and cluster['count'] >= 5:
                if not demo_clusters['pension']:
                    demo_clusters['pension'] = cluster

        # Copy demo cases
        for label, cluster in demo_clusters.items():
            if cluster:
                dest = self.demo_dir / label
                os.makedirs(dest, exist_ok=True)

                # Save cluster summary
                with open(dest / "cluster_summary.json", "w") as f:
                    json.dump(cluster, f, indent=2)

                # Copy judgment files
                for jid in cluster['judgments']:
                    src = self.processed_dir / f"{jid}.json"
                    if src.exists():
                        shutil.copy(src, dest / f"{jid}.json")

                print(f"Prepared showcase for {label} in {dest}")
