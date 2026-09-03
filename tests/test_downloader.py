import tempfile
from pathlib import Path
from unittest.mock import patch

import requests
from bs4 import BeautifulSoup

from legal_ai_toolkit.extraction.downloader import IndianKanoonDownloader


def _content(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("div", class_="judgments")


def test_extract_clean_text_keeps_header_and_title_elements():
    """Indian Kanoon renders the court name, case title, author, and bench as
    h2/h3 headings and the opening cause-title block as a bare <pre> - an
    older ["p", "div"] allowlist silently dropped all of them, so a large
    fraction of downloaded judgments came back with no recoverable court
    metadata even though the source page had one.
    """
    html = """
    <div class="judgments">
        <div class="covers">[Cites4, Cited by0]</div>
        <h3 class="docsource_main">Madhya Pradesh High Court</h3>
        <h2 class="doc_title">Smt. Narendar Kaur vs Jasveer Singh on 16 November, 2022</h2>
        <h3 class="doc_author">Author: Deepak Kumar Agarwal</h3>
        <h3 class="doc_bench">Bench: Deepak Kumar Agarwal</h3>
        <pre>IN THE HIGH COURT OF MADHYA PRADESH AT GWALIOR</pre>
        <p>(BY SHRI S.K. SHARMA - ADVOCATE FOR RESPONDENT NO.1)</p>
        <blockquote>JUDGMENT: Aggrieved by the award of the claim petition.</blockquote>
        <p>The appeal sans merit and is hereby dismissed.</p>
    </div>
    """

    text = IndianKanoonDownloader.extract_clean_text(_content(html))

    assert "Madhya Pradesh High Court" in text
    assert "Smt. Narendar Kaur vs Jasveer Singh" in text
    assert "IN THE HIGH COURT OF MADHYA PRADESH" in text
    assert "Aggrieved by the award" in text
    assert "The appeal sans merit" in text


def test_extract_clean_text_strips_cite_tags_and_cite_counts():
    html = """
    <div class="judgments">
        <div class="covers">[Cites 4, Cited by 0]</div>
        <p>Held in <a class="cite_tag">Some Precedent v. State</a> that the appeal fails.</p>
    </div>
    """

    text = IndianKanoonDownloader.extract_clean_text(_content(html))

    assert "Cites" not in text
    assert "Some Precedent" not in text
    assert "the appeal fails" in text


def test_network_failure_does_not_mark_query_completed():
    """A DNS/connection failure during search must leave the query pending,
    not mark it completed with zero results.

    Previously search() swallowed every exception and search_and_download()
    always added the query to completed_queries regardless of outcome. A
    sustained network outage burned through an entire ~3,200-query remaining
    catalog in minutes, recording all of them as "done" with nothing actually
    searched - only discovered by grepping the run log for failure lines and
    manually reconstructing which queries needed retrying.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        downloader = IndianKanoonDownloader(
            output_dir=str(tmp_path / "raw"),
            checkpoint_file=str(tmp_path / "checkpoint.json"),
            manifest_file=str(tmp_path / "manifest.jsonl"),
        )

        with patch(
            "legal_ai_toolkit.extraction.downloader.requests.get",
            side_effect=requests.exceptions.ConnectionError("Failed to resolve indiankanoon.org"),
        ):
            result = downloader.search_and_download("Delhi High Court bail 2020", "test", max_results=10)

        assert result == 0
        assert "Delhi High Court bail 2020" not in downloader.completed_queries
