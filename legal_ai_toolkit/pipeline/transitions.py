"""
Pipeline step for statutory transitions (IPC→BNS mapping).

REFACTORED (Phase 4):
- Uses improved TransitionExtractor and SectionExtractor
- Cleaner architecture
- Better integration with extraction modules
"""
from .runner import BaseStep
from legal_ai_toolkit.extraction.transitions import TransitionExtractor
from legal_ai_toolkit.extraction.sections import SectionExtractor


class TransitionStep(BaseStep):
    """Pipeline step for extracting and mapping IPC→BNS transitions."""

    def process_item(self, data):
        """
        Process a judgment item to extract statutory transitions.

        Args:
            data: Judgment data dictionary

        Returns:
            Updated data dictionary with sections and transitions
        """
        text = data.get("text", "")

        # Extract all sections using improved SectionExtractor
        all_sections = SectionExtractor.extract(text)
        grouped_sections = SectionExtractor.group_by_act(all_sections)

        # Store extracted sections for all acts
        data["extracted_sections"] = {}
        for act, section_nums in grouped_sections.items():
            act_key = act.lower().replace(" ", "_")
            data["extracted_sections"][act_key] = section_nums

        # Extract IPC→BNS transitions using improved TransitionExtractor
        judgment_date = data.get("metadata", {}).get("decision_date")
        transitions = TransitionExtractor.extract(text, judgment_date=judgment_date)

        # Store transitions
        data["statutory_transitions"] = {
            "total_transitions": len(transitions),
            "transitions": transitions,
            "summary": {
                "total_ipc_found": len(grouped_sections.get("IPC", [])),
                "mapped_count": len([t for t in transitions if t.get("bns")]),
                "unmapped_count": len([t for t in transitions if not t.get("bns")])
            }
        }

        return data
