"""Regression test: bytes-only tier must match mutation-test evidence.

Every entry tagged ``provenance_tier: bytes-only`` claims that its
defect is not observable to any wired oracle at BRep-load time. That
claim is directly testable by ``step_corpus._mutation_test`` — if a
random byte-mutation flips the validate2 summary, the fixture is
oracle-active, not bytes-only.

This test locks the tag against text-drift: if someone edits the
Notes wording without re-running the mutation test, or a fixture's
defect mechanism changes such that it becomes detectable, CI fails.

Same shape as ``test_sibling_pair_inputs_present``.

The snapshot at ``tests/data/mutation_snapshot.json`` is refreshed
whenever a full ``_mutation_test --all`` run completes; test enforces
that every current ``bytes-only`` entry is either ``undetected``
or ``no-target-byte`` in the snapshot (both mean "no data-byte
mutation detected the defect").
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from step_corpus import catalog

SNAPSHOT_PATH = Path(__file__).parent / "data" / "mutation_snapshot.json"

# Statuses that are consistent with a bytes-only claim:
#   - undetected: mutation test ran attempts, none flipped the summary
#   - no-target-byte: no mutable digit found in DATA section
#     (structural defect — mutation test can't touch it either way)
_OK_STATUSES = {"undetected", "no-target-byte"}


def test_snapshot_exists() -> None:
    assert SNAPSHOT_PATH.is_file(), (
        f"missing snapshot at {SNAPSHOT_PATH}; refresh via "
        f"`cd validation && uv run python -m step_corpus._mutation_test "
        f"--all --mutations 3 --workers 8 --out /tmp/qmut_full.json` "
        f"then copy to tests/data/mutation_snapshot.json"
    )


def test_bytes_only_are_undetected() -> None:
    """Every bytes-only entry must be undetected/no-target-byte in the
    mutation snapshot. A ``detected`` status would mean the mutation
    test found a byte flip that the oracle noticed, contradicting
    the bytes-only claim."""
    if not SNAPSHOT_PATH.is_file():
        pytest.skip(f"snapshot missing at {SNAPSHOT_PATH}")
    snap = json.loads(SNAPSHOT_PATH.read_text())
    results = snap["results"]

    detected: list[str] = []
    missing: list[str] = []
    for entry in catalog.iter_canonical():
        if entry.get("provenance_tier") != "bytes-only":
            continue
        fid = entry["id"]
        status = results.get(fid)
        if status is None:
            missing.append(fid)
        elif status not in _OK_STATUSES and status != "no-baseline":
            # no-baseline is neutral (baseline hadn't been cached at snapshot
            # time — see the 23 wave-7/8 fixtures added post-snapshot).
            detected.append(f"{fid} → status={status}")

    problems = []
    if detected:
        problems.append(
            f"{len(detected)} bytes-only entries are DETECTED in the mutation "
            f"snapshot (they should be undetected/no-target-byte):\n"
            + "\n".join(f"  {d}" for d in detected[:15])
        )
    if missing:
        problems.append(
            f"{len(missing)} bytes-only entries missing from snapshot "
            f"(refresh the snapshot):\n"
            + "\n".join(f"  {m}" for m in missing[:15])
        )
    if problems:
        pytest.fail("\n\n".join(problems))


def test_snapshot_covers_current_corpus() -> None:
    """Snapshot should cover a large fraction of the corpus. If it drifts
    too far (many new fixtures added since snapshot), refresh it."""
    if not SNAPSHOT_PATH.is_file():
        pytest.skip(f"snapshot missing at {SNAPSHOT_PATH}")
    snap = json.loads(SNAPSHOT_PATH.read_text())
    results = snap["results"]
    corpus_ids = {e["id"] for e in catalog.iter_canonical()}
    covered = corpus_ids & set(results.keys())
    coverage = len(covered) / len(corpus_ids) if corpus_ids else 0.0
    # Allow some drift: floor is 95% coverage.
    assert coverage >= 0.95, (
        f"snapshot covers {coverage:.1%} of corpus ({len(covered)}/{len(corpus_ids)}); "
        f"refresh snapshot (many new fixtures added since {snap.get('run_date')})"
    )
