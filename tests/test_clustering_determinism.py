import json
import tempfile
from pathlib import Path

from legal_ai_toolkit.clustering.centroid import find_clusters_centroid
from legal_ai_toolkit.clustering.refinement import refine_mega_clusters
from legal_ai_toolkit.clustering.similarity import extract_signals


def _judgment(issues, sections):
    return {
        "judgment_id": "J000",
        "annotations": {"issues": {name: 1 for name in issues}, "citations": []},
        "extracted_sections": {"ipc": sections},
        "classification": {"domain": "criminal"},
    }


def _high_edge(source, target, weight=12):
    return {
        "from": source,
        "to": target,
        "weight": weight,
        "strength": "high",
        "signals": {
            "shared_issues": [],
            "shared_sections": [f"IPC {num}" for num in range(300, 300 + weight)],
            "shared_citations": [],
        },
    }


def _write_signals(signal_dir, judgment_ids, issues_for):
    signal_dir.mkdir(parents=True, exist_ok=True)
    for jid in judgment_ids:
        (signal_dir / f"{jid}.json").write_text(
            json.dumps({"judgment_id": jid, "issues": issues_for(jid), "domain": "criminal"}),
            encoding="utf-8",
        )


def test_extract_signals_returns_sorted_lists():
    """Set iteration order varies per process, so signals must be sorted on the way out."""
    signals = extract_signals(
        _judgment(
            ["sentencing", "bail", "quashing", "arbitration"],
            ["376", "302", "498A", "304B"],
        )
    )

    assert signals["issues"] == sorted(signals["issues"])
    assert signals["sections"] == sorted(signals["sections"])
    assert signals["citations"] == sorted(signals["citations"])


def test_centroid_clustering_is_invariant_to_edge_order():
    """imap_unordered can emit edges in any order; clusters must not depend on it."""
    edges = [_high_edge("A", "B"), _high_edge("B", "C"), _high_edge("C", "D")]

    forward, _ = find_clusters_centroid(list(edges))
    reverse, _ = find_clusters_centroid(list(reversed(edges)))

    assert [sorted(cluster) for cluster in forward] == [sorted(cluster) for cluster in reverse]


def test_mega_cluster_refinement_is_invariant_to_issue_order():
    """A judgment's primary issue must not depend on how its issue list was ordered."""
    judgment_ids = [f"J{index:03d}" for index in range(40)]
    cluster = {
        "cluster_id": "CLUSTER-0001",
        "centroid": judgment_ids[0],
        "judgments": judgment_ids,
        "count": len(judgment_ids),
        "basis": {},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _write_signals(tmp_path / "forward", judgment_ids, lambda jid: ["bail", "sentencing"])
        _write_signals(tmp_path / "reverse", judgment_ids, lambda jid: ["sentencing", "bail"])

        forward = refine_mega_clusters([dict(cluster)], tmp_path / "forward")
        reverse = refine_mega_clusters([dict(cluster)], tmp_path / "reverse")

    assert [(c["cluster_id"], c["primary_issue"], c["count"]) for c in forward] == [
        (c["cluster_id"], c["primary_issue"], c["count"]) for c in reverse
    ]
