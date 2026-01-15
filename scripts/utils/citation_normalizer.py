class CitationNormalizer:

    @staticmethod
    def normalize(citation):
        if "reporter" in citation:
            return f"{citation['reporter']}-{citation['year']}-{citation['page']}"

        if "case_name" in citation:
            return citation["case_name"].replace(" ", "_").upper()

        return "UNKNOWN"
