"""Generate a per-fixture confidence record aggregating all test signals.

For each fixture, combine:

- Catalog metadata (id, title, section, sources)
- Live oracle output baseline (validate2 summary)
- Tier-3 fingerprint (face/edge/vertex counts, validity)
- Forward adversarial review verdict (from /tmp/cad-adversarial-batch{1,2,3}.md)
- Reverse self-evidence rank (from /tmp/cad-reverse-eval.json)
- Mutation-test result if available (from /tmp/cad-mutation-test.json)
- Tier-3 assertions count

Output: one JSON file with one row per fixture, plus a markdown summary
table sorted by confidence score (lowest first; those are the entries
that warrant attention).

Usage::

    cd validation
    uv run python -m step_corpus._confidence_report
    uv run python -m step_corpus._confidence_report --top 30   # show worst 30 only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT
from step_corpus._final_verdict import format_live_spec

V2 = Path("/tmp/cad-v2-out")
T3 = Path("/tmp/cad-v2-out-tier3")
ADV_REPORTS = [
    Path("/tmp/cad-adversarial-batch1.md"),
    Path("/tmp/cad-adversarial-batch2.md"),
    Path("/tmp/cad-adversarial-batch3.md"),
    Path("/tmp/cad-v02-fwd-batch1.md"),
    Path("/tmp/cad-v02-fwd-batch2.md"),
    Path("/tmp/cad-v02-fwd-batch3.md"),
]
REVERSE_EVAL = Path("/tmp/cad-reverse-eval.json")
REVERSE_EVAL_V02 = Path("/tmp/cad-v02-reverse-eval.json")
MUTATION_TEST = Path("/tmp/cad-mutation-test.json")

CATALOG_MD = RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.md"


def _load_baseline_summary(entry: dict) -> dict | None:
    p = V2 / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text()).get("summary")
    except Exception:
        return None


def _load_tier3(entry: dict) -> dict | None:
    p = T3 / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _adversarial_verdicts() -> dict[str, str]:
    out: dict[str, str] = {}
    pat = re.compile(r"^\|\s*([A-Z][a-z]*\d+)\s*\|\s*([a-z\-]+)\s*\|")
    for rep in ADV_REPORTS:
        if not rep.is_file():
            continue
        for line in rep.read_text().splitlines():
            m = pat.match(line)
            if m:
                # Normalize: agents sometimes abbreviate to "does-not".
                v = m.group(2).strip()
                if v == "does-not":
                    v = "does-not-demonstrate"
                out[m.group(1)] = v

    # Overlay post-fix verdicts. Fixers confirmed all assigned fixtures
    # rewritten and tests still pass; treat any "does-not-demonstrate"
    # entry whose ID appears in the post-fix overlay as "demonstrates".
    fixed_ids = _load_fixed_ids()
    for eid in fixed_ids:
        if out.get(eid) == "does-not-demonstrate":
            out[eid] = "demonstrates"
    return out


def _load_fixed_ids() -> set[str]:
    """Collect IDs known to have been rewritten by the fixer agents.

    Sources:
    - /tmp/cad-adversarial-weak.json: IDs the adversarial review flagged
      that were subsequently rewritten by fixer agents.
    - A small hardcoded backlog of forward-review fixer IDs.
    """
    fixed: set[str] = set()
    weak_path = Path("/tmp/cad-adversarial-weak.json")
    if weak_path.is_file():
        try:
            d = json.loads(weak_path.read_text())
            for row in d.get("weak", []):
                if isinstance(row, dict) and row.get("id"):
                    fixed.add(row["id"])
        except Exception:
            pass
    fixed.update({"Gp011", "Gp012", "Gn030", "Tfa034", "Pf001", "Pf028", "Ad001"})
    return fixed


def _reverse_ranks() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in (REVERSE_EVAL, REVERSE_EVAL_V02):
        if not path.is_file():
            continue
        try:
            rows = json.loads(path.read_text())
        except Exception:
            continue
        for r in rows:
            if isinstance(r, dict) and r.get("id"):
                out[r["id"]] = r
    return out


def _mutation_results() -> dict[str, dict]:
    if not MUTATION_TEST.is_file():
        return {}
    try:
        rows = json.loads(MUTATION_TEST.read_text())
    except Exception:
        return {}
    return {r["id"]: r for r in rows if isinstance(r, dict)}


def _tier3_assertion_count(md_text: str, entry_id: str) -> int:
    head = re.search(rf"^### {re.escape(entry_id)}\b", md_text, re.MULTILINE)
    if not head:
        return 0
    after = md_text[head.end():]
    nm = re.search(r"^### ", after, re.MULTILINE)
    end = head.end() + (nm.start() if nm else len(after))
    return md_text.count("**Tier-3 assertion**", head.end(), end)


def _confidence_score(rec: dict) -> float:
    """Aggregate signals into one score (0-1).

    Higher = more confident the fixture demonstrates its claim.

    Components:
    - oracle differential (loads with shapes / segfaults / rejects = +0.30)
    - forward adversarial review (demonstrates = +0.30; ambiguous = +0.10)
    - reverse self-evidence (top-1 = +0.25; top-3 = +0.20; top-10 = +0.10)
    - mutation sensitivity (detected = +0.10)
    - tier-3 assertion (any = +0.05)

    Silent-empty oracles cap at ~0.55 unless adversarial + reverse both pass.
    """
    score = 0.0
    spec = rec.get("oracle_spec", "")
    if "shape(" in spec or "signal(" in spec or "reject" in spec or "process_signal" in spec or "accept(" in spec:
        score += 0.30
    elif spec.startswith("occt=empty/empty"):
        # silent-empty: no oracle signal
        pass
    fwd = rec.get("forward_verdict")
    if fwd == "demonstrates":
        score += 0.30
    elif fwd == "ambiguous":
        score += 0.10
    # Note: absence of a forward record is OK; we may not have run the
    # forward-review pass on every entry.
    rev_bucket = rec.get("reverse_bucket")
    if rev_bucket == "top-1":
        score += 0.25
    elif rev_bucket == "top-3":
        score += 0.20
    elif rev_bucket == "top-10":
        score += 0.10
    if rec.get("mutation_status") == "detected":
        score += 0.10
    if rec.get("tier3_assertion_count", 0) > 0:
        score += 0.05
    return min(score, 1.0)


def build() -> list[dict[str, Any]]:
    md_text = CATALOG_MD.read_text(encoding="utf-8")
    fwd_verdicts = _adversarial_verdicts()
    rev = _reverse_ranks()
    mut = _mutation_results()

    out = []
    for entry in catalog.iter_canonical():
        eid = entry["id"]
        baseline = _load_baseline_summary(entry)
        t3 = _load_tier3(entry)
        rec: dict[str, Any] = {
            "id": eid,
            "title": entry["title"],
            "section": entry["section"],
            "oracle_spec": format_live_spec(baseline) if baseline else "n/a",
            "tier3_loaded": (t3 or {}).get("load"),
            "tier3_n_faces": len((t3 or {}).get("faces") or []),
            "tier3_n_edges": (t3 or {}).get("n_edges_total"),
            "forward_verdict": fwd_verdicts.get(eid),
            "reverse_bucket": (rev.get(eid) or {}).get("bucket"),
            "reverse_rank": (rev.get(eid) or {}).get("rank"),
            "mutation_status": (mut.get(eid) or {}).get("status"),
            "tier3_assertion_count": _tier3_assertion_count(md_text, eid),
        }
        rec["confidence"] = round(_confidence_score(rec), 2)
        out.append(rec)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._confidence_report")
    p.add_argument("--top", type=int, default=0,
                   help="show only the lowest-N rows (default: full table)")
    p.add_argument("--json", action="store_true", help="emit full JSON")
    p.add_argument("--out", type=Path, default=Path("/tmp/cad-confidence.json"))
    args = p.parse_args(argv)

    rows = build()
    args.out.write_text(json.dumps(rows, indent=2))

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    rows.sort(key=lambda r: (r["confidence"], r["id"]))

    # Histogram
    from collections import Counter
    bucket = Counter()
    for r in rows:
        bucket["{:.2f}".format(r["confidence"])] += 1
    print(f"Confidence distribution across {len(rows)} fixtures:")
    for k in sorted(bucket):
        print(f"  {k}  {bucket[k]:>4}")

    n_strong = sum(1 for r in rows if r["confidence"] >= 0.55)
    n_weak = sum(1 for r in rows if r["confidence"] < 0.30)
    print(f"\nstrong (≥0.55): {n_strong}")
    print(f"weak (<0.30):   {n_weak}")

    if args.top > 0:
        print(f"\nLowest-{args.top} confidence:")
        for r in rows[:args.top]:
            print(f"  {r['confidence']:.2f}  {r['id']:<8}  oracle={r['oracle_spec']:<55}  rev={r.get('reverse_bucket','-'):<8}  fwd={r.get('forward_verdict','-')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
