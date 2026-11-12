import json
import os
from pathlib import Path
from collections import Counter

class ReportGenerator:
    def __init__(self, cluster_file, processed_dir, report_dir):
        self.cluster_file = Path(cluster_file)
        self.processed_dir = Path(processed_dir)
        self.report_dir = Path(report_dir)
        os.makedirs(self.report_dir, exist_ok=True)

    def generate(self):
        """
        Generate comprehensive operational analytics report.
        """
        if not self.cluster_file.exists():
            print(f"[ERROR] Cluster file not found: {self.cluster_file}")
            return

        # Load data
        with open(self.cluster_file, "r", encoding="utf-8") as f:
            clusters = json.load(f)
        if not isinstance(clusters, list):
            print(f"[ERROR] Invalid cluster file format (expected list): {self.cluster_file}")
            return

        judgments = list(self.processed_dir.glob("*.json"))

        # Calculate statistics
        total_cases = len(judgments)
        total_clusters = len(clusters)
        cases_in_clusters = sum(cluster.get("count", 0) for cluster in clusters if isinstance(cluster, dict))

        # Domain distribution
        domain_counts = Counter()
        landmark_count = 0

        for jfile in judgments:
            with open(jfile, "r", encoding="utf-8") as f:
                data = json.load(f)
                domain = data.get('classification', {}).get('domain', 'unknown')
                domain_counts[domain] += 1

                extractions = data.get("extractions", {})
                has_v2_landmarks = extractions.get("landmarks", {}).get("total", 0) > 0
                has_legacy_landmarks = bool(data.get("annotations", {}).get("matched_landmarks"))
                if has_v2_landmarks or has_legacy_landmarks:
                    landmark_count += 1

        # High-Priority Batch Candidates
        top_candidates = []
        for cluster in clusters[:15]:
            if not isinstance(cluster, dict):
                continue

            cluster_size = cluster.get("count", 0)
            individual_time = cluster_size * 2
            batch_time = cluster_size * 0.4
            savings = individual_time - batch_time

            top_candidates.append({
                "cluster_id": cluster.get("cluster_id", "unknown"),
                "size": cluster_size,
                "primary_issue": cluster.get('primary_issue', 'mixed'),
                "estimated_savings_hours": round(savings, 1)
            })

        coverage_pct = 0.0
        if total_cases > 0:
            coverage_pct = round((cases_in_clusters / total_cases) * 100, 1)

        # Final Report Data
        report = {
            "summary": {
                "total_judgments_analyzed": total_cases,
                "total_high_precision_clusters": total_clusters,
                "total_cases_optimized": cases_in_clusters,
                "optimization_coverage": f"{coverage_pct}%",
                "landmark_precedents_matched": landmark_count
            },
            "domain_distribution": dict(domain_counts),
            "top_batch_candidates": top_candidates
        }

        report_path = self.report_dir / "full_operational_report.json"
        with open(report_path, "w", encoding="utf-8") as out:
            json.dump(report, out, indent=2, ensure_ascii=False)

        print(f"Operational report generated at {report_path}")
        return report

class BatchIdentifier:
    def __init__(self, cluster_file):
        self.cluster_file = Path(cluster_file)

    def identify(self):
        if not self.cluster_file.exists():
            print(f"[ERROR] Cluster file not found: {self.cluster_file}")
            return None

        with open(self.cluster_file) as f:
            clusters = json.load(f)

        candidates = {
            'service_seniority': None,
            'criminal_bail_498a': None,
            'criminal_sentencing_304b': None,
            'civil_arbitration': None,
            'service_pension': None
        }

        for cluster in clusters:
            primary = cluster.get('primary_issue', '')

            if 'seniority_promotion' in primary and cluster['count'] >= 10:
                if not candidates['service_seniority']: candidates['service_seniority'] = cluster

            elif 'bail' in primary and cluster['count'] >= 8:
                basis_sections = cluster.get('basis', {}).get('sections', [])
                if any('498' in s for s in basis_sections):
                    if not candidates['criminal_bail_498a']: candidates['criminal_bail_498a'] = cluster

            elif 'sentencing' in primary and cluster['count'] >= 8:
                basis_sections = cluster.get('basis', {}).get('sections', [])
                if any('304B' in s for s in basis_sections):
                    if not candidates['criminal_sentencing_304b']: candidates['criminal_sentencing_304b'] = cluster

            elif 'arbitration' in primary and cluster['count'] >= 5:
                if not candidates['civil_arbitration']: candidates['civil_arbitration'] = cluster

            elif 'pension' in primary and cluster['count'] >= 5:
                if not candidates['service_pension']: candidates['service_pension'] = cluster

        return candidates
