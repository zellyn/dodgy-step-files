"""Cross-fixture similarity audit (v2).

Compute pairwise BM25 similarity across all canonical catalog entries; flag
pairs whose normalized cross-similarity meets a threshold and classify
each pair into one of three verdicts:

- ``merge``: same category, same taxonomy tags, and substantially
  overlapping byte_assertions; treat as a likely actual duplicate that
  one entry should absorb the other (manual review required, never
  auto-merged).
- ``cross-reference``: same category but the taxonomy / byte_assertion
  fingerprints differ; the two entries describe distinct but related
  defects and should at least cross-link via ``**See also**:``.
- ``keep``: different categories (different defect domains); the BM25
  collision is on shared CAD vocabulary, not on the underlying defect.

The earlier v1 audit (``--threshold`` knob, free-text similarity report)
remains accessible via ``--legacy``. The v2 default writes a structured
JSON report to ``/tmp/cad-dedup-audit.json`` and, with
``--apply-cross-references``, can update the catalog markdown to add
``**See also**:`` links for ``cross-reference`` verdicts.

The signal: if two entries score very high on each other's BM25 query
(treating each entry's ``_build_doc`` token bag as both "document" and
"query"), they are likely describing the same defect.

Usage::

    cd validation
    uv run python -m step_corpus._dedup_audit
    uv run python -m step_corpus._dedup_audit --threshold 0.6
    uv run python -m step_corpus._dedup_audit --apply-cross-references
    uv run python -m step_corpus._dedup_audit --legacy --threshold 0.6 --top 50

Merge suggestions are NEVER applied automatically; they require human
review (a merge changes the canonical surface of the catalog).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._bug_search import BugIndex

# Default threshold honours the spec's "near-duplicate at >= 0.85" target.
# The normalization is symmetric BM25:
#     max(score(A_doc -> B) / self_score(A),
#         score(B_doc -> A) / self_score(B))
# which approaches 1.0 only when the two entries share most of their
# weighted vocabulary.
DEFAULT_THRESHOLD = 0.85

# Where the JSON report lands by default.
DEFAULT_REPORT_PATH = Path("/tmp/cad-dedup-audit.json")

# Where the catalog markdown lives. Resolved lazily so unit tests can patch
# the catalog path without monkey-patching this module.
_RESEARCH_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CATALOG_MD = _RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.md"


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    """Cosine similarity over weighted token bags (the same bags BugIndex
    builds via ``_build_doc``).
    """
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if not (na and nb):
        return 0.0
    return dot / (na * nb)


def _build_pairs(
    idx: BugIndex,
    threshold: float,
    *,
    k: int = 30,
) -> list[dict[str, Any]]:
    """Return all candidate pairs above ``threshold`` with both BM25 and
    cosine similarities.

    The BM25 normalization is the symmetric max of the two directional
    self-normalized BM25 scores; cosine is reported as a corroborating
    signal but not used for thresholding (cosine over weighted bags is
    strictly more permissive than BM25 and would inflate the candidate
    list with shared-vocabulary noise).
    """
    n = len(idx.entries)
    self_scores: list[float] = []
    for i in range(n):
        s = idx._score(idx.docs[i], i)
        self_scores.append(s if s > 0 else 1.0)

    # Build a hit cache: for each entry, the BM25 score against every
    # entry that shows up in its top-k. We need both directions to compute
    # a symmetric similarity, so we do one full pass.
    id_to_idx = {e["id"]: i for i, e in enumerate(idx.entries)}
    hit_cache: list[dict[str, float]] = []
    for i in range(n):
        q = " ".join(idx.docs[i])
        if not q.strip():
            hit_cache.append({})
            continue
        hits = idx.search(q, k=k)
        hit_cache.append({e["id"]: s for s, e in hits})

    bags = [Counter(idx.docs[i]) for i in range(n)]

    pairs: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for i in range(n):
        a_id = idx.entries[i]["id"]
        for tid, sab in hit_cache[i].items():
            if tid == a_id:
                continue
            j = id_to_idx.get(tid)
            if j is None:
                continue
            sba = hit_cache[j].get(a_id, 0.0)
            normalized = max(sab / self_scores[i], sba / self_scores[j])
            if normalized < threshold:
                continue
            key = (a_id, tid) if a_id < tid else (tid, a_id)
            if key in seen:
                continue
            seen.add(key)
            cos = _cosine(bags[i], bags[j])
            pairs.append(
                {
                    "a": key[0],
                    "b": key[1],
                    "bm25_normalized": round(normalized, 4),
                    "cosine": round(cos, 4),
                }
            )
    pairs.sort(key=lambda p: -p["bm25_normalized"])
    return pairs


# ---------------------------------------------------------------------------
# Verdict heuristic
# ---------------------------------------------------------------------------


def _byte_overlap(a: list[str] | None, b: list[str] | None) -> tuple[int, float]:
    """Return ``(shared_count, overlap_ratio)`` over byte_assertions.

    ``overlap_ratio`` is shared / smaller_set_size; 0.0 when either side
    has no byte assertions.
    """
    sa = set(a or [])
    sb = set(b or [])
    if not sa or not sb:
        return 0, 0.0
    shared = len(sa & sb)
    smaller = min(len(sa), len(sb))
    return shared, (shared / smaller) if smaller else 0.0


def classify_pair(ea: dict[str, Any], eb: dict[str, Any]) -> str:
    """Verdict for a candidate near-duplicate pair.

    Heuristic per spec:

    - Same category AND same taxonomy AND substantially-overlapping
      byte_assertions → ``merge``.
    - Different categories → ``keep`` (distinct defect domains).
    - Same category, but the taxonomy or byte fingerprint disagree →
      ``cross-reference``.
    """
    cat_a = (ea.get("category") or "").strip()
    cat_b = (eb.get("category") or "").strip()
    tax_a = tuple(sorted(ea.get("taxonomy") or []))
    tax_b = tuple(sorted(eb.get("taxonomy") or []))
    shared, ratio = _byte_overlap(ea.get("byte_assertions"), eb.get("byte_assertions"))

    if cat_a != cat_b:
        return "keep"
    same_taxonomy = bool(tax_a) and tax_a == tax_b
    substantial_byte_overlap = shared >= 1 and ratio >= 0.5
    if same_taxonomy and substantial_byte_overlap:
        return "merge"
    return "cross-reference"


# ---------------------------------------------------------------------------
# Audit runner
# ---------------------------------------------------------------------------


def run_audit(
    threshold: float = DEFAULT_THRESHOLD,
    *,
    idx: BugIndex | None = None,
) -> dict[str, Any]:
    """Compute pairs above ``threshold``, attach verdicts, return a report.

    The returned dict has::

        {
            "threshold": float,
            "n_entries": int,
            "n_pairs": int,
            "counts": {"merge": ..., "cross-reference": ..., "keep": ...},
            "pairs": [
                {
                    "a": str, "b": str,
                    "bm25_normalized": float, "cosine": float,
                    "verdict": "merge"|"cross-reference"|"keep",
                    "a_category": str, "b_category": str,
                    "a_taxonomy": [...], "b_taxonomy": [...],
                    "byte_overlap": int,
                    "already_linked": bool,
                    "a_title": str, "b_title": str,
                },
                ...
            ],
        }
    """
    idx = idx or BugIndex.load()
    pairs = _build_pairs(idx, threshold)
    by_id = {e["id"]: e for e in idx.entries}

    enriched: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for p in pairs:
        ea = by_id[p["a"]]
        eb = by_id[p["b"]]
        verdict = classify_pair(ea, eb)
        shared, _ratio = _byte_overlap(
            ea.get("byte_assertions"), eb.get("byte_assertions")
        )
        sa = set(ea.get("see_also") or [])
        sb = set(eb.get("see_also") or [])
        already_linked = (eb["id"] in sa) and (ea["id"] in sb)
        enriched.append(
            {
                **p,
                "verdict": verdict,
                "a_category": ea.get("category") or "",
                "b_category": eb.get("category") or "",
                "a_taxonomy": list(ea.get("taxonomy") or []),
                "b_taxonomy": list(eb.get("taxonomy") or []),
                "byte_overlap": shared,
                "already_linked": already_linked,
                "a_title": ea.get("title") or "",
                "b_title": eb.get("title") or "",
            }
        )
        counts[verdict] += 1

    return {
        "threshold": threshold,
        "n_entries": len(idx.entries),
        "n_pairs": len(enriched),
        "counts": dict(counts),
        "pairs": enriched,
    }


# ---------------------------------------------------------------------------
# Markdown patcher: add See also cross-references
# ---------------------------------------------------------------------------


_NOTES_LINE_RE = re.compile(r"^- \*\*Notes\*\*:\s*(?P<rest>.*)$")
_SEE_ALSO_RE = re.compile(
    r"\*\*See also\*\*\s*:\s*(?P<list>[^.]*?)(?P<term>\.|$)"
)
_HEADER_RE = re.compile(r"^### (?P<id>[A-Za-z][A-Za-z0-9]*)\b")


def _format_see_also_list(ids: list[str]) -> str:
    return ", ".join(ids)


def _merge_see_also(existing: list[str], new_id: str) -> list[str]:
    """Return a deduped, alphabetically-sorted list with ``new_id`` added."""
    out = list(existing)
    if new_id not in out:
        out.append(new_id)
    # Stable sort: keep entries that share a prefix together but cleanly
    # ordered (catalog ordering is alphabetic per ID).
    out.sort()
    return out


def _patch_notes_line(line: str, new_id: str) -> tuple[str, bool]:
    """If ``line`` contains a ``**See also**:`` clause, splice ``new_id``
    into that list. Otherwise prepend a fresh ``**See also**: NEW.``
    clause to the Notes content.

    Returns ``(new_line, changed)``.
    """
    notes_match = _NOTES_LINE_RE.match(line)
    if not notes_match:
        return line, False
    rest = notes_match.group("rest")
    sa_match = _SEE_ALSO_RE.search(rest)
    if sa_match:
        chunk = sa_match.group("list")
        ids = re.findall(r"[A-Za-z][A-Za-z0-9]*", chunk)
        if new_id in ids:
            return line, False
        merged = _merge_see_also(ids, new_id)
        replacement = f"**See also**: {_format_see_also_list(merged)}"
        new_rest = (
            rest[: sa_match.start()]
            + replacement
            + sa_match.group("term")
            + rest[sa_match.end():]
        )
        return f"- **Notes**: {new_rest}", True
    # No existing See also; prepend one to the Notes content.
    if rest.strip():
        new_rest = f"**See also**: {new_id}. {rest}"
    else:
        new_rest = f"**See also**: {new_id}."
    return f"- **Notes**: {new_rest}", True


def apply_cross_references(
    pairs: list[dict[str, Any]],
    catalog_md_path: Path | None = None,
) -> dict[str, Any]:
    """For every pair with verdict == ``cross-reference`` AND both
    directions missing, edit the catalog markdown so each entry's first
    Notes line cross-links the other.

    Returns a dict reporting the edits performed.
    """
    catalog_md_path = catalog_md_path or DEFAULT_CATALOG_MD
    text = catalog_md_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Build (entry_id -> [line_indices_of_its_notes_lines]) and
    # (entry_id -> header_line_index)
    header_idx: dict[str, int] = {}
    notes_idx: dict[str, list[int]] = {}
    current_id: str | None = None
    for i, line in enumerate(lines):
        m_header = _HEADER_RE.match(line)
        if m_header:
            current_id = m_header.group("id")
            header_idx[current_id] = i
            continue
        if current_id and _NOTES_LINE_RE.match(line):
            notes_idx.setdefault(current_id, []).append(i)

    edits: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for p in pairs:
        if p["verdict"] != "cross-reference":
            continue
        if p.get("already_linked"):
            continue
        a = p["a"]
        b = p["b"]
        # Skip if entry not parseable (out-of-band header)
        if a not in notes_idx or b not in notes_idx:
            skipped.append({"a": a, "b": b, "reason": "no Notes line"})
            continue

        added_to: list[str] = []
        for src, dst in ((a, b), (b, a)):
            line_indices = notes_idx[src]
            # Try first to update a Notes line that already has See also.
            target_i = None
            for li in line_indices:
                if _SEE_ALSO_RE.search(lines[li]):
                    target_i = li
                    break
            if target_i is None:
                target_i = line_indices[0]
            new_line, changed = _patch_notes_line(lines[target_i], dst)
            if changed:
                lines[target_i] = new_line
                added_to.append(src)
        if added_to:
            edits.append({"a": a, "b": b, "added_to": added_to})

    if edits:
        catalog_md_path.write_text("".join(lines), encoding="utf-8")

    return {
        "catalog_md": str(catalog_md_path),
        "edits": edits,
        "skipped": skipped,
        "n_edits": len(edits),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_summary(report: dict[str, Any], *, top: int = 15) -> None:
    counts = report["counts"]
    print(f"Dedup audit (threshold={report['threshold']}, "
          f"entries={report['n_entries']}):")
    print(f"  total candidate pairs: {report['n_pairs']}")
    print(f"    merge:           {counts.get('merge', 0)}")
    print(f"    cross-reference: {counts.get('cross-reference', 0)}")
    print(f"    keep:            {counts.get('keep', 0)}")
    if not report["pairs"]:
        return
    print(f"\nTop {min(top, len(report['pairs']))} pairs (by BM25):")
    for p in report["pairs"][:top]:
        link = " (linked)" if p["already_linked"] else ""
        print(
            f"  bm25={p['bm25_normalized']:.3f} cos={p['cosine']:.3f} "
            f"{p['verdict']:<16} {p['a']:<8} ↔ {p['b']:<8}{link}"
        )
        print(f"     A: {p['a_title'][:80]}")
        print(f"     B: {p['b_title'][:80]}")


def _legacy_main(argv: list[str] | None) -> int:
    """Original v1 audit kept under ``--legacy`` for backward compatibility."""
    p = argparse.ArgumentParser(prog="step_corpus._dedup_audit --legacy")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    entries = list(catalog.iter_canonical())
    idx = BugIndex.load()
    linked: set[tuple[str, str]] = set()
    for e in entries:
        eid = e["id"]
        for rid in (e.get("see_also") or []):
            linked.add((eid, rid))
            linked.add((rid, eid))

    pairs: list[tuple[float, str, str, bool]] = []
    seen_pair: set[tuple[str, str]] = set()
    for src in entries:
        sid = src["id"]
        q = " ".join([src.get("title") or "", src.get("description") or ""])
        if not q.strip():
            continue
        self_score = next(
            (s for s, e in idx.search(q, k=20) if e["id"] == sid), None
        )
        if self_score is None or self_score <= 0:
            continue
        for hit_score, hit_entry in idx.search(q, k=10):
            tid = hit_entry["id"]
            if tid == sid:
                continue
            ratio = hit_score / self_score
            if ratio < args.threshold:
                continue
            key = tuple(sorted((sid, tid)))
            if key in seen_pair:
                continue
            seen_pair.add(key)
            pairs.append((ratio, sid, tid, (sid, tid) in linked))
    pairs.sort(key=lambda t: -t[0])

    if args.json:
        rows = [{"ratio": r, "a": a, "b": b, "already_linked": al}
                for r, a, b, al in pairs]
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"Cross-fixture similarity audit (threshold={args.threshold}):")
    print(f"  total pairs above threshold: {len(pairs)}")
    print(f"  already linked (see_also): "
          f"{sum(1 for _, _, _, al in pairs if al)}")
    print(f"  unlinked: "
          f"{sum(1 for _, _, _, al in pairs if not al)}\n")
    n = 0
    for ratio, a, b, al in pairs:
        if al:
            continue
        ea = catalog.find(a)
        eb = catalog.find(b)
        ta = (ea.get("title") or "")[:55] if ea else "?"
        tb = (eb.get("title") or "")[:55] if eb else "?"
        print(f"  {ratio:.2f}  {a:<8} ↔ {b:<8}")
        print(f"       {a}: {ta}")
        print(f"       {b}: {tb}")
        n += 1
        if n >= args.top:
            break
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "--legacy":
        return _legacy_main(argv[1:])

    p = argparse.ArgumentParser(prog="step_corpus._dedup_audit")
    p.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="BM25 (max-self-normalized) similarity threshold (default 0.85)",
    )
    p.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Path to write JSON report (default {DEFAULT_REPORT_PATH})",
    )
    p.add_argument(
        "--top",
        type=int,
        default=15,
        help="How many pairs to print to stdout",
    )
    p.add_argument(
        "--apply-cross-references",
        action="store_true",
        help="Edit STEP_PROBLEM_CATALOG.md to add **See also** links for "
             "cross-reference verdicts (does NOT auto-merge)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Print the full report to stdout as JSON instead of pretty-printing.",
    )
    args = p.parse_args(argv)

    report = run_audit(args.threshold)

    # Always write report to disk for downstream consumption (e.g. tests).
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.apply_cross_references:
        patch = apply_cross_references(report["pairs"])
        report["apply_cross_references"] = patch
        # Re-write report with the patch results attached.
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    _print_summary(report, top=args.top)
    if "apply_cross_references" in report:
        patch = report["apply_cross_references"]
        print(f"\nApplied {patch['n_edits']} cross-reference edit(s) to "
              f"{patch['catalog_md']}")
        for e in patch["edits"]:
            print(f"  + See also  {e['a']} <-> {e['b']}  (added to: "
                  f"{', '.join(e['added_to'])})")
        if patch.get("skipped"):
            print(f"  skipped {len(patch['skipped'])} pair(s) with no Notes line")

    print(f"\nReport written to: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
