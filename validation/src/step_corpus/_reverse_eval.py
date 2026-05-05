"""Evaluate the reverse-direction self-evidence test.

Reads JSONL output from the cold-reading agents (one row per fixture: id +
agent-written description). For each row:

1. Run BM25 search using the description.
2. Find the rank of the fixture's canonical catalog id in the results.
3. Bucket: top-1, top-3, top-10, beyond top-10, not-found.

The interpretation:

- **top-1**: the fixture is so self-evident that a cold reader's
  description points directly at the right entry.
- **top-3**: self-evident enough; the cold reader's description ranks
  the right entry near the top among legitimate competitors.
- **top-10**: marginal. The fixture supports the claim, but the catalog
  has multiple entries that match the same description equally well.
  Either the catalog has redundancy or the fixture isn't sharp enough.
- **beyond top-10 / not-found**: the cold reader's description didn't
  surface the canonical entry at all. Either the fixture's defect is
  ambiguous, or the catalog title is too API-shaped, or the reader
  misread the bytes.

A "no discernible defect" description is a separate bucket: a fixture
whose defect is purely runtime / requires geometric reasoning the cold
reader couldn't do from bytes alone. These aren't necessarily broken
fixtures; they're just runtime-only defects.

Usage::

    cd validation
    uv run python -m step_corpus._reverse_eval                  # default: read all 3 batches
    uv run python -m step_corpus._reverse_eval /tmp/foo.jsonl   # custom path
    uv run python -m step_corpus._reverse_eval --json           # machine-readable
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from step_corpus._bug_search import BugIndex


DEFAULT_INPUTS = [
    Path("/tmp/cad-reverse-batch1.jsonl"),
    Path("/tmp/cad-reverse-batch2.jsonl"),
    Path("/tmp/cad-reverse-batch3.jsonl"),
]

# Phrases that mean "the agent couldn't see the defect" (legitimate
# runtime-only signal, not a fixture failure).
_INDISCERNIBLE_MARKERS = (
    "no discernible defect",
    "looks ordinary",
    "structurally sound",
    "no visible defect",
    "appears clean",
    "looks clean",
    "runtime-only",
)


def _is_indiscernible(desc: str) -> bool:
    low = desc.lower()
    return any(m in low for m in _INDISCERNIBLE_MARKERS)


def _bucket(rank: int | None, indiscernible: bool) -> str:
    if indiscernible:
        return "indiscernible"
    if rank is None:
        return "not-found"
    if rank == 1:
        return "top-1"
    if rank <= 3:
        return "top-3"
    if rank <= 10:
        return "top-10"
    return "beyond-10"


def evaluate(inputs: list[Path]) -> list[dict[str, Any]]:
    idx = BugIndex.load()
    results = []
    for src in inputs:
        if not src.is_file():
            continue
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            eid = row.get("id")
            desc = row.get("description", "")
            if not eid or not desc:
                continue
            indisc = _is_indiscernible(desc)
            if indisc:
                rank = None
            else:
                rank = idx.rank_of(desc, eid, k=50)
            results.append({
                "id": eid,
                "description": desc,
                "rank": rank,
                "bucket": _bucket(rank, indisc),
                "source": src.name,
            })
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._reverse_eval")
    p.add_argument("inputs", type=Path, nargs="*", default=DEFAULT_INPUTS,
                   help="JSONL files (default: /tmp/cad-reverse-batch{1,2,3}.jsonl)")
    p.add_argument("--json", action="store_true", help="emit JSON results")
    p.add_argument("--worst", type=int, default=20,
                   help="show this many worst-ranking entries (default 20)")
    args = p.parse_args(argv)

    results = evaluate(list(args.inputs))
    if args.json:
        json.dump(results, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if not results:
        print("No reverse-direction results found.", file=sys.stderr)
        print(f"Looked for: {', '.join(str(p) for p in args.inputs)}", file=sys.stderr)
        return 1

    bk = Counter(r["bucket"] for r in results)
    total = len(results)
    by_source = Counter((r["source"], r["bucket"]) for r in results)

    print(f"Reverse-direction evaluation: {total} fixtures\n")
    print("Bucket               Count    Pct")
    print("-" * 38)
    for bucket in ("top-1", "top-3", "top-10", "beyond-10", "not-found", "indiscernible"):
        n = bk.get(bucket, 0)
        pct = 100 * n / total if total else 0
        print(f"{bucket:<20} {n:>5}   {pct:>5.1f}%")

    # Self-evident threshold = top-1 + top-3
    self_evident = bk.get("top-1", 0) + bk.get("top-3", 0)
    print(f"\nself-evident (top-3 or better): {self_evident} / {total} ({100 * self_evident / total:.1f}%)")
    print(f"runtime-only / can't tell:       {bk.get('indiscernible', 0)} / {total}")
    print(f"weak self-evidence (top-10+/not-found, excluding indiscernible): "
          f"{bk.get('beyond-10', 0) + bk.get('not-found', 0)} / {total}")

    print("\nPer-source breakdown:")
    for src in sorted({s for s, _ in by_source}):
        per = ", ".join(
            f"{b}={by_source[(src, b)]}"
            for b in ("top-1", "top-3", "top-10", "beyond-10", "not-found", "indiscernible")
            if by_source[(src, b)] > 0
        )
        print(f"  {src}: {per}")

    # Worst-ranking entries (excluding indiscernible; those are a legitimate
    # signal, not a fixture problem).
    worst = sorted(
        [r for r in results if r["bucket"] in {"beyond-10", "not-found"}],
        key=lambda r: (r["rank"] if r["rank"] is not None else 9999),
        reverse=True,
    )[: args.worst]
    if worst:
        print(f"\nWorst-ranking {len(worst)} (cold reader's description didn't find canonical entry):")
        for r in worst:
            rk = "not-found" if r["rank"] is None else f"rank={r['rank']}"
            desc = r["description"]
            if len(desc) > 90:
                desc = desc[:87] + "..."
            print(f"  {r['id']:<8}  {rk:<12}  {desc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
