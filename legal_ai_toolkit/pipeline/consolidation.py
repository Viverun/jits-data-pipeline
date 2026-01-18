import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from .runner import BaseStep


class ConsolidationStep(BaseStep):
    """Consolidate all extractions into single unified JSON per judgment."""

    def process_item(self, data):
        """
        Create unified JSON with all extractions.

        Takes the pipeline data and creates a clean unified structure
        with citations, sections, and transitions.
        """
        judgment_id = data.get('judgment_id', 'unknown')

        # Build unified structure
        unified = {
            "judgment_id": judgment_id,
            "text": data.get("text", ""),  # ✅ Preserve original text
            "metadata": {
                "processed_date": datetime.now().isoformat(),
                "version": "2.0"
            },
            "extractions": {
                "citations": {},
                "sections": {},
                "transitions": {},
                "landmarks": {},
                "issues": {}
            },
            "provenance": {  # ✅ NEW: Track processing history
                "processed_date": datetime.now().isoformat(),
                "pipeline_version": "2.0",
                "processing_steps": [
                    "ingestion",
                    "metadata_extraction",
                    "issue_extraction",
                    "classification",
                    "statutory_transitions",
                    "citation_extraction",
                    "consolidation"
                ]
            }
        }

        # Preserve any existing metadata
        if 'metadata' in data:
            unified["metadata"].update(data['metadata'])

        # Add citations
        annotations = data.get('annotations', {})
        citations = annotations.get('citations', [])

        citation_counts = defaultdict(int)
        for cite in citations:
            citation_counts[cite.get('type', 'unknown')] += 1

        unified["extractions"]["citations"] = {
            "total": len(citations),
            "by_type": dict(citation_counts),
            "details": citations
        }

        # Add issues
        issues = annotations.get('issues', [])
        unified["extractions"]["issues"] = {
            "total": len(issues),
            "details": issues
        }

        # Add landmarks
        landmarks = annotations.get('matched_landmarks', [])
        landmark_counts = defaultdict(int) 
        for lm in landmarks:
             landmark_counts[lm.get('precedent_id', 'unknown')] += 1

        unified["extractions"]["landmarks"] = {
            "total": len(landmarks),
            "by_id": dict(landmark_counts),
            "details": landmarks
        }

        # Add sections
        extracted_sections = data.get('extracted_sections', {})

        # Convert extracted_sections dict back to grouped format
        sections_by_act = {}
        all_sections = []

        for act_key, section_nums in extracted_sections.items():
            # Convert act_key back to readable name
            act_name = act_key.replace("_", " ").upper()
            if act_name == "IPC":
                act_name = "IPC"
            elif act_name == "CRPC":
                act_name = "CrPC"
            elif act_name == "EVIDENCE ACT":
                act_name = "Evidence Act"
            elif act_name == "DOWRY PROHIBITION ACT":
                act_name = "Dowry Prohibition Act"

            sections_by_act[act_name] = section_nums

            # Create detailed section entries
            for sec_num in section_nums:
                all_sections.append({
                    "section": sec_num,
                    "act": act_name
                })

        unified["extractions"]["sections"] = {
            "total": len(all_sections),
            "by_act": sections_by_act,
            "details": all_sections
        }

        # Add transitions
        statutory_transitions = data.get('statutory_transitions', {})
        transitions = statutory_transitions.get('transitions', [])

        transition_counts = defaultdict(int)
        for trans in transitions:
            transition_counts[trans.get('source', 'unknown')] += 1

        unified["extractions"]["transitions"] = {
            "total": len(transitions),
            "by_source": dict(transition_counts),
            "details": transitions
        }

        # Include classification if available
        if 'classification' in data:
            unified["classification"] = data['classification']

        return unified

    def run(self):
        """Run consolidation to create unified JSON files."""
        print(f"\n[Consolidation] Creating unified JSON files...")
        print(f"  Input: {self.input_dir}")
        print(f"  Output: {self.output_dir}")
        print()

        super().run()

        print(f"[Consolidation] ✅ Created unified JSON files in {self.output_dir}")


