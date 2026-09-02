import time

from legal_ai_toolkit.extraction.metadata import extract_case_number


def _lines(text):
    return text.splitlines()


def test_writ_petition_number_is_extracted():
    assert extract_case_number(_lines("WP No. 1234 of 2019")) == "WP No. 1234 of 2019"


def test_criminal_misc_number_with_slash_year_is_extracted():
    assert extract_case_number(_lines("MCRC No. 4567/2021")) == "MCRC No. 4567/2021"


def test_multi_number_cause_title_is_still_matched():
    """The comma-separated list form the old pattern spelled out explicitly."""
    assert extract_case_number(_lines("WP Nos. 111, 222, 333 of 2018")) == "WP Nos. 111, 222, 333 of 2018"


def test_case_number_scan_does_not_backtrack_catastrophically():
    """A near-miss cause title must fail fast, not explore every partition of it.

    The header pattern for numbered writ/criminal petitions once carried a
    trailing "(?:sep [class])*" group whose separators were also inside the
    class, so a line that looked like a numbered cause title but did not end in
    a year took exponential time to reject. This line is such a near-miss: it
    has the prefix and the number list but no /YYYY or "of YYYY" ending.
    """
    line = "WP Nos. 1234, 5678, 9012, 3456, 7890, 2345, 6789 AND CONNECTED MATTERS LISTED"

    start = time.perf_counter()
    result = extract_case_number(_lines(line))
    elapsed = time.perf_counter() - start

    assert result in (None, "UNKNOWN") or "1234" in result
    # Sub-millisecond once the ambiguity is gone; was ~40ms for this one line,
    # and grows exponentially with the number of list entries.
    assert elapsed < 1.0, f"case-number scan took {elapsed:.2f}s - backtracking has regressed"


def test_paragraph_case_number_scan_does_not_backtrack_catastrophically():
    """A High-Court-mentioning paragraph with a near-miss tail must fail fast.

    CASE_NO_PATTERNS[7] carried the same "(?:sep [class])*" trailing group as
    the near-miss above, but reached through ordinary paragraph text (not a
    header line): `_extract_high_court_embedded_case_tag` slices off the text
    after a "... High Court" mention and feeds it to this pattern family. Real
    judgment text that mentions a High Court and a "Cr."/"MCRC"/etc token with
    no real case number immediately after took exponential time to reject -
    this hung the ingestion pipeline indefinitely on ordinary prose.
    """
    header = (
        "In the Madras High Court, which was registered as CRLOP No.2943 of 2021, "
        "and was dismissed, which was again challenged in the Supreme Court in "
        "Petition(s) for Special Leave to Appeal (Crl.) No(s).1521-1523 of 2024, "
        "in which the complainant was also directed to deposit a sum, which has "
        "also been deposited, and subsequently the matter has been settled amicably"
    )

    start = time.perf_counter()
    result = extract_case_number(_lines(header))
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"case-number scan took {elapsed:.2f}s - backtracking has regressed"
    assert result is not None


def test_high_court_embedded_fallback_does_not_backtrack_catastrophically():
    """The unbounded fallback regex in `_extract_high_court_embedded_case_tag`
    carried the same vulnerable trailing group as CASE_NO_PATTERNS[7], but as a
    standalone literal rather than a list entry, so fixing the list alone did
    not fix this path. Reached whenever the loop over individual lines finds
    no "... High Court ..." + case-number match and falls through to scan the
    whole (up to 2500-char) header at once.
    """
    from legal_ai_toolkit.extraction.metadata import _extract_high_court_embedded_case_tag

    header = (
        "IN THE HIGH COURT OF MADHYA PRADESH AT INDORE\n"
        "This petition under Section 482 Cr.P.C. has been filed seeking quashment "
        "of the FIR registered at Police Station City Kotwali for offences under "
        "various sections, and the applicant has also sought regular bail in "
        "connection with the same crime number, which remains pending consideration"
    )

    start = time.perf_counter()
    result = _extract_high_court_embedded_case_tag(header)
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f"embedded fallback scan took {elapsed:.2f}s - backtracking has regressed"
