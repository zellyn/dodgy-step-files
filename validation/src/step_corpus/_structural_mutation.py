"""Structural mutation test for the silent-empty subset.

Random-byte mutation testing only has signal on oracle-active fixtures
(reject / shape-loading / segfault baselines). Silent-empty fixtures
require a *structural* mutation: change one entity reference (`#N`) to
something different, then check whether validate2's
diagnostic-augmented summary changes.

The principle: if a fixture's defect is described as "EDGE_LOOP edges
not head-to-tail", the catalog cites specific `#N` references binding
the edges. Swap one of those `#N`s to a different existing instance.
The mutated fixture should produce a *different* (possibly still
silent-empty, but with a different diagnostic) oracle output. If it
produces *byte-identical* oracle output, the cited entity isn't load-
bearing; the fixture is structurally inert.

Strategy
--------

For each silent-empty candidate:

1. Pick an entity reference `#N` in the DATA section (the catalog's
   reproducer-cited entities are the ideal target, but we operate
   blind; pick any non-trivial reference).
2. Mutate it: replace `#N` with `#M` where `#M` is another defined
   instance of a *different* entity type (so the mutation is structurally
   meaningful).
3. Run validate2. Compare the full augmented summary (including
   diagnostic signatures) to the baseline.
4. Detected = output differs in any field. Undetected = mutated and
   baseline are identical.

The "undetected" set is the set of fixtures whose entity graph is
not actually being walked by OCC, or whose defect is so deep in the
graph that random reference swaps don't surface it. Either way,
worth investigating.

Usage
-----

    cd validation
    uv run python -m step_corpus._structural_mutation --silent-empty --workers 6
    uv run python -m step_corpus._structural_mutation --section 12-3a-shells
"""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT
from step_corpus._final_verdict import format_live_spec
from step_corpus._mutation_test import (
    _baseline_summary,
    _baseline_tier3,
    _summaries_differ,
    _tier3_signature,
    _data_section_range,
    _run_validate2,
    _run_tier3,
)

EXAMPLES = RESEARCH_ROOT / "step-examples"

_RE_INSTANCE_DEF = re.compile(rb"(?:^|;)\s*#(\d+)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
_RE_REF_USAGE = re.compile(rb"#(\d+)")


def _collect_instances(body: bytes, data_start: int, data_end: int) -> dict[int, str]:
    """Return {ref_id: entity_type_name} for all definitions in DATA."""
    out: dict[int, str] = {}
    for m in _RE_INSTANCE_DEF.finditer(body, data_start, data_end):
        try:
            rid = int(m.group(1))
        except ValueError:
            continue
        out[rid] = m.group(2).decode("ascii", errors="replace")
    return out


def _pick_structural_mutation(body: bytes, rng: random.Random) -> tuple[int, int, int] | None:
    """Pick a `#A` reference in body to swap with `#B` of a different type.

    Returns (offset_of_digit_run, len_of_digit_run, new_id) or None.
    """
    rng_data = _data_section_range(body)
    if rng_data is None:
        return None
    start, end = rng_data
    instances = _collect_instances(body, start, end)
    if len(instances) < 2:
        return None
    # Find all reference *usages* (excluding the `#N=` definition line itself)
    candidates: list[tuple[int, int, int, str]] = []
    for m in _RE_REF_USAGE.finditer(body, start, end):
        offset = m.start()
        # Skip if this is a definition (followed by `=`)
        rest = body[m.end():m.end()+10].lstrip()
        if rest.startswith(b"="):
            continue
        try:
            rid = int(m.group(1))
        except ValueError:
            continue
        if rid not in instances:
            continue
        candidates.append((offset + 1, m.end() - m.start() - 1, rid, instances[rid]))
    if not candidates:
        return None
    # Pick a random reference. Try to find a target of a *different* type.
    rng.shuffle(candidates)
    for offset, dlen, src_id, src_type in candidates:
        # Find a different-type target
        diff_targets = [(rid, t) for rid, t in instances.items() if t != src_type and rid != src_id]
        if not diff_targets:
            continue
        target_id, _ = rng.choice(diff_targets)
        return (offset, dlen, target_id)
    return None


def _apply_structural_mutation(body: bytes, offset: int, dlen: int, new_id: int) -> bytes:
    new_str = str(new_id).encode("ascii")
    return body[:offset] + new_str + body[offset + dlen:]


def _test_one(entry: dict, seed: int) -> dict[str, Any]:
    fixture = EXAMPLES / entry["section_dir"] / f"{entry['id']}.stp"
    if not fixture.is_file():
        return {"id": entry["id"], "status": "no-fixture"}
    body = fixture.read_bytes()
    baseline_v2 = _baseline_summary(entry)
    baseline_t3 = _baseline_tier3(entry)
    baseline_t3_sig = _tier3_signature(baseline_t3)
    if baseline_v2 is None:
        return {"id": entry["id"], "status": "no-baseline"}
    rng = random.Random(seed)
    pick = _pick_structural_mutation(body, rng)
    if pick is None:
        return {"id": entry["id"], "status": "no-target"}
    offset, dlen, new_id = pick
    src_id = int(body[offset:offset+dlen])
    mutated = _apply_structural_mutation(body, offset, dlen, new_id)
    with tempfile.NamedTemporaryFile(suffix=".stp", delete=False) as tf:
        tf.write(mutated)
        tmp_path = Path(tf.name)
    try:
        new_summary = _run_validate2(tmp_path)
        new_t3 = _run_tier3(tmp_path) if new_summary and "_error" not in new_summary else None
    finally:
        tmp_path.unlink(missing_ok=True)
    if new_summary is None or "_error" in new_summary:
        return {"id": entry["id"], "status": "validate2-error", "src_id": src_id, "new_id": new_id}
    if new_summary.get("timeout"):
        return {"id": entry["id"], "status": "timeout", "src_id": src_id, "new_id": new_id}
    v2_changed = _summaries_differ(baseline_v2, new_summary)
    t3_changed = (baseline_t3_sig != _tier3_signature(new_t3))
    detected = v2_changed or t3_changed
    return {
        "id": entry["id"],
        "status": "detected" if detected else "undetected",
        "swap": f"#{src_id}→#{new_id}",
        "baseline": format_live_spec(baseline_v2),
        "mutated": format_live_spec(new_summary),
        "v2_changed": v2_changed,
        "t3_changed": t3_changed,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._structural_mutation")
    p.add_argument("--silent-empty", action="store_true",
                   help="restrict to fixtures with silent-empty oracle baseline")
    p.add_argument("--section", type=str, help="restrict to one section_dir")
    p.add_argument("--sample", type=int, default=0,
                   help="sample N fixtures (0 = all matching)")
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("/tmp/cad-structural-mutation.json"))
    args = p.parse_args(argv)

    SILENT = "occt=empty/empty gmsh=empty ifc=schema_n/a"

    entries = list(catalog.iter_canonical())
    if args.section:
        entries = [e for e in entries if e["section_dir"] == args.section]
    if args.silent_empty:
        kept = []
        for e in entries:
            s = _baseline_summary(e)
            if s and format_live_spec(s) == SILENT:
                kept.append(e)
        entries = kept
        print(f"silent-empty filter: {len(entries)} fixtures", file=sys.stderr)

    if args.sample > 0 and len(entries) > args.sample:
        rng = random.Random(args.seed)
        entries = rng.sample(entries, args.sample)

    print(f"Testing {len(entries)} fixtures with {args.workers} workers", file=sys.stderr)
    rng = random.Random(args.seed)
    seeds = {e["id"]: rng.randint(0, 1 << 31) for e in entries}
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_test_one, e, seeds[e["id"]]): e for e in entries}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(entries)} done", file=sys.stderr)

    args.out.write_text(json.dumps(results, indent=2))

    from collections import Counter
    by_status = Counter(r["status"] for r in results)
    print(f"\nStructural mutation results ({len(results)} fixtures):")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<22} {v:>4}")

    detected = by_status.get("detected", 0)
    undetected = by_status.get("undetected", 0)
    if detected + undetected > 0:
        rate = 100 * detected / (detected + undetected)
        print(f"\nDetection rate: {detected}/{detected+undetected} ({rate:.1f}%)")

    print(f"\nFull results: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
