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
