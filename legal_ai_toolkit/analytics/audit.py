import json
from pathlib import Path
from collections import Counter

class DataAuditor:
    def __init__(self, processed_dir, cluster_file=None, edge_file=None):
        self.processed_dir = Path(processed_dir)
        self.cluster_file = Path(cluster_file) if cluster_file else None
        self.edge_file = Path(edge_file) if edge_file else None

    def audit_quality(self):
        print("Starting JITS Quality Audit...")

        if not self.processed_dir.exists():
            print(f"Error: {self.processed_dir} not found.")
            return

        files = list(self.processed_dir.glob("*.json"))
        total_cases = len(files)

        if total_cases == 0:
            print("No processed judgments found.")
            return

        empty_metadata = 0
        metadata_accurate_count = 0
        missing_court = 0
        missing_date = 0
        missing_case_no = 0
        empty_annotations = 0
        landmark_coverage = 0
        domain_stats = Counter()
        act_coverage = {
            "crpc": 0,
            "iea": 0,
            "pc_act": 0,
            "ni_act": 0
        }

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

                meta = data.get("metadata", {})
                court = meta.get("court")
                date = meta.get("decision_date")
                case_no = meta.get("case_number")

                # Metadata Accuracy (core fields extracted)
                is_accurate = (court and court != "UNKNOWN") and \
                              (date and date != "UNKNOWN")

                if is_accurate:
                    metadata_accurate_count += 1

                if not court or court == "UNKNOWN":
                    missing_court += 1
                if not date or date == "UNKNOWN":
                    missing_date += 1
                if not case_no or case_no == "UNKNOWN":
                    missing_case_no += 1

                if not court or court == "UNKNOWN":
                    empty_metadata += 1

                anno = data.get("annotations", {})
                if not anno.get("issues") and not anno.get("citations"):
                    empty_annotations += 1

                if anno.get("matched_landmarks"):
                    landmark_coverage += 1

                extracted = data.get("extracted_sections", {})
                for act in act_coverage:
                    if extracted.get(act):
                        act_coverage[act] += 1

                domain = data.get("classification", {}).get("domain", "unknown")
                domain_stats[domain] += 1

        print(f"Total Cases: {total_cases}")
        print(f"Metadata Accuracy: {metadata_accurate_count} ({(metadata_accurate_count/total_cases*100):.1f}%)")
        print(f"  - Missing Court: {missing_court}")
        print(f"  - Missing Date: {missing_date}")
        print(f"  - Missing Case No: {missing_case_no}")
        print(f"Empty Annotations: {empty_annotations}")
        print(f"Landmark Coverage: {landmark_coverage} ({landmark_coverage/total_cases*100:.1f}%)")
        print("Specialized Act Coverage:")
        for act, count in act_coverage.items():
            print(f"  - {act.upper()}: {count} cases ({count/total_cases*100:.1f}%)")
        print(f"Domains: {dict(domain_stats)}")
        return locals()

    def audit_landmarks(self):
        landmark_counts = Counter()
        files = list(self.processed_dir.glob("*.json"))

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                landmarks = data.get("annotations", {}).get("matched_landmarks", [])
                for lm in landmarks:
                    landmark_counts[lm["short_name"]] += 1

        print("\nTop Cited Landmarks:")
        for name, count in landmark_counts.most_common(10):
            print(f"  - {name}: {count} citations")
        return landmark_counts

    def check_unmapped_ipc(self):
        unmapped_counter = Counter()
        files = list(self.processed_dir.glob("*.json"))

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                unmapped = data.get("statutory_transitions", {}).get("unmapped_ipc", [])
                for sec in unmapped:
                    unmapped_counter[sec] += 1

        print("\nTop Unmapped IPC Sections:")
        for sec, count in unmapped_counter.most_common(20):
            print(f"  - {sec}: {count} occurrences")
        return unmapped_counter

    def analyze_edges(self):
        if not self.edge_file or not self.edge_file.exists():
            print("Edge file not found.")
            return

        strengths = Counter()
        weights = []
        with open(self.edge_file, "r", encoding="utf-8") as f:
            for line in f:
                edge = json.loads(line)
                strengths[edge["strength"]] += 1
                weights.append(edge.get("weight", 0))

        print(f"\nTotal Edges: {len(weights)}")
        print(f"Strengths: {dict(strengths)}")
        return strengths

    def audit_classification_samples(self, samples_per_domain=2):
        import random
        files = list(self.processed_dir.glob("*.json"))

        domain_groups = {}
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                domain = data.get("classification", {}).get("domain", "unknown")
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append((file.name, data))

        print("\nClassification Accuracy Audit (Random Samples)")
        print("="*80)

        for domain in sorted(domain_groups.keys()):
            print(f"\nDOMAIN: {domain.upper()}")
            samples = random.sample(domain_groups[domain], min(len(domain_groups[domain]), samples_per_domain))

            for filename, data in samples:
                signals = data.get("classification", {}).get("signals", {})
                confidence = data.get("classification", {}).get("confidence", "low")
                text_snippet = data.get("text", "")[:500].replace("\n", " ")

                print(f"\nFile: {filename}")
                print(f"   Confidence: {confidence}")
                print(f"   Signals Found: {signals}")
                print(f"   Snippet: {text_snippet}...")
                print("-" * 40)

    def summarize_clusters(self):
        if not self.cluster_file or not self.cluster_file.exists():
            print("Cluster file not found.")
            return

        with open(self.cluster_file, "r", encoding="utf-8") as f:
            clusters = json.load(f)

        print(f"\nCluster Summary ({len(clusters)} Clusters)")
        print("="*40)

        for c in clusters:
            print(f"ID: {c['cluster_id']} ({c['count']} judgments)")
            print(f"Centroid: {c['centroid']}")

            basis = c.get('basis', {})
            issues = basis.get('issues', [])
            sections = basis.get('sections', [])

            if issues: print(f"  Themes: {', '.join(issues[:5])}")
            if sections: print(f"  Key Sections: {', '.join(sections[:5])}")
            print("-" * 20)

    def validate_referential_integrity(self):
        """
        Check if all judgment IDs in clusters and edges exist in the processed directory.
        """
        existing_ids = set()
        for file in self.processed_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if "judgment_id" in data:
                        existing_ids.add(data["judgment_id"])
                except Exception:
                    continue

        errors = 0
        if self.edge_file and self.edge_file.exists():
            print(f"Checking edges in {self.edge_file}...")
            with open(self.edge_file, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    if not line.strip(): continue
                    try:
                        edge = json.loads(line)
                        for key in ["from", "to"]:
                            jid = edge.get(key)
                            if jid and jid not in existing_ids:
                                print(f"  [EDGE ERR] Line {line_no}: Missing {key} judgment {jid}")
                                errors += 1
                    except Exception:
                        continue

        if self.cluster_file and self.cluster_file.exists():
            print(f"Checking clusters in {self.cluster_file}...")
            with open(self.cluster_file, "r", encoding="utf-8") as f:
                try:
                    clusters = json.load(f)
                    for cluster in clusters:
                        for jid in cluster.get("judgments", []):
                            if jid not in existing_ids:
                                print(f"  [CLUSTER ERR] {cluster.get('cluster_id')}: Missing judgment {jid}")
                                errors += 1
                except Exception:
                    pass

        print(f"Referential integrity check complete. Total errors: {errors}")
        return errors
