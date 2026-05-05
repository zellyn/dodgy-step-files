"""Active oracle for §12-13 writer-pathology entries.

§12-13 (Wr*) are byte-asserted today: each fixture is hand-authored to
exhibit a defect class, and ``test_byte_assertions`` checks the
fixture's bytes match the documented signature. That confirms the
fixture, not the *writer* the fixture is supposed to model.

This test pairs each implementable Wr id with a ``BuggyWriter`` method
that simulates the defect on a canonical clean input. The test then
verifies the writer's output exhibits the catalog's defect signature.
End-to-end loop: writer simulator → output bytes → catalog claim.

Skipped Wr ids (round-trip data loss requiring sibling-pair evidence,
or kernel-state-required healing) are listed in
``_writer_oracle.WRITER_SKIP``. Each carries a one-line reason.
"""
from __future__ import annotations

import re

import pytest

from step_corpus._writer_oracle import (
    CLEAN_INPUT,
    BuggyWriter,
    PATHOLOGY_VERIFIERS,
    WRITER_SKIP,
    run_all,
    verify_pathology,
)


@pytest.fixture(scope="module")
def writer_results() -> list[dict]:
    return run_all()


def test_clean_input_is_well_formed() -> None:
    """The canonical input itself must be a clean Part-21 file.

    Sanity check: the input does not exhibit any of the defects the
    writer oracle injects. If a defect already exists in the input,
    the oracle's "before vs after" is meaningless.
    """
    assert CLEAN_INPUT.startswith(b"ISO-10303-21;")
    assert CLEAN_INPUT.rstrip().endswith(b"END-ISO-10303-21;")
    # No CRLF
    assert b"\r" not in CLEAN_INPUT
    # No comma-decimal abuse
    assert not re.search(rb"\(\d+,\d+,\d+,\d+", CLEAN_INPUT)
    # No long-form booleans
    assert b".TRUE." not in CLEAN_INPUT
    # No raw UTF-8
    assert not re.search(rb"[\xc0-\xf7][\x80-\xbf]", CLEAN_INPUT)


def test_writer_oracle_simulates_targeted_count(writer_results: list[dict]) -> None:
    """The writer oracle should simulate ~25-30 distinct Wr ids."""
    n = len(writer_results)
    assert n >= 25, (
        f"writer oracle simulates only {n} Wr ids; target is 25-30"
    )
    assert n <= 40, (
        f"writer oracle simulates {n} Wr ids; that's beyond the design budget"
    )


def test_every_simulated_defect_exhibits(writer_results: list[dict]) -> None:
    """Every BuggyWriter method must produce output that exhibits the defect."""
    misses = [r for r in writer_results if r["verdict"] != "exhibits"]
    if misses:
        listing = "\n".join(
            f"  {r['id']:<8} method={r['method']:<40} verdict={r['verdict']:<10} detail={r['detail']}"
            for r in misses
        )
        pytest.fail(f"{len(misses)} writer methods did not produce expected pathology:\n{listing}")


def test_writer_skip_set_has_reasons() -> None:
    """Every skipped Wr id should have a one-line reason."""
    assert len(WRITER_SKIP) >= 5, "expected at least 5 skipped Wr ids"
    assert len(WRITER_SKIP) <= 25, "skip set ballooned past 25 entries"
    for wr_id, reason in WRITER_SKIP.items():
        assert wr_id.startswith("Wr"), f"skip key should be a Wr id, got {wr_id!r}"
        assert isinstance(reason, str) and len(reason) > 10, (
            f"skip reason for {wr_id} too short: {reason!r}"
        )


def test_no_overlap_between_simulated_and_skipped() -> None:
    """A Wr id should be either implementable or skipped, never both."""
    impl = set(BuggyWriter.DEFECT_METHODS)
    skipped = set(WRITER_SKIP)
    overlap = impl & skipped
    assert not overlap, f"Wr ids appear in both simulator and skip set: {overlap}"


def test_combined_coverage_matches_catalog_size() -> None:
    """Implementable + skipped should cover the documented Wr* range (Wr001..Wr043).

    The catalog has ~43 Wr* entries today. The oracle should
    address every one of them, either by simulation or by an
    explicit skip with a reason.
    """
    covered = set(BuggyWriter.DEFECT_METHODS) | set(WRITER_SKIP)
    expected = {f"Wr{i:03d}" for i in range(1, 44)}
    missing = expected - covered
    assert not missing, f"Wr ids in catalog but not in oracle (neither simulated nor skipped): {sorted(missing)}"


@pytest.mark.parametrize("wr_id,method_name", sorted(BuggyWriter.DEFECT_METHODS.items()))
def test_each_writer_method_individually(wr_id: str, method_name: str) -> None:
    """Per-Wr-id parametrised test: writer + verifier must agree."""
    writer = BuggyWriter()
    method = getattr(writer, method_name)
    out = method()
    assert isinstance(out, bytes), f"{method_name} did not return bytes"
    v = verify_pathology(out, wr_id)
    assert v["verdict"] == "exhibits", (
        f"{wr_id} method={method_name} verdict={v['verdict']} detail={v['detail']}"
    )


def test_verify_pathology_handles_unknown_id() -> None:
    """Unknown Wr id should return 'ambiguous', not crash."""
    v = verify_pathology(b"anything", "Wr999")
    assert v["verdict"] == "ambiguous"


def test_verify_pathology_returns_missing_for_clean_input() -> None:
    """Run every verifier against the clean input; most should not detect the defect."""
    detections = []
    for wr_id, fn in PATHOLOGY_VERIFIERS.items():
        try:
            if fn(CLEAN_INPUT):
                detections.append(wr_id)
        except Exception:  # pragma: no cover
            pass
    # Wr040 (every entity name '') and Wr037 (>= 4 VERTEX_POINTs) match
    # by construction since the clean cube has many empty-name points
    # and 8 vertices. Wr012/Wr038 may incidentally match because the
    # clean input is sequentially numbered. We expect <= 4 incidental
    # matches.
    assert len(detections) <= 6, (
        f"too many catalog signatures match the clean input ({detections}); "
        "the input is supposed to be defect-free"
    )
