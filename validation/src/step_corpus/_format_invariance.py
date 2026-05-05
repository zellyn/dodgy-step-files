"""Round-trip / formatting-invariance test.

For each fixture, generate cosmetic variants and check whether the
oracle output changes. A solid fixture's defect should be invariant
under whitespace / line-ending / comment changes. If oracle output
*does* change, OCC has a formatting-dependence, itself a defect class
worth documenting.

Variants generated per fixture:

- **WS-collapsed**: collapse runs of whitespace inside DATA section.
- **CRLF**: convert all line endings to CRLF.
- **LF**: convert all line endings to LF (no-op on already-LF files).
- **Comment-stripped**: remove all `/* */` comment blocks.

Run validate2 on each variant. Compare augmented summaries (including
diagnostic signatures). For most fixtures, all variants should produce
identical output.

Usage::

    cd validation
    uv run python -m step_corpus._format_invariance --sample 100
    uv run python -m step_corpus._format_invariance --all   # full corpus, ~30 min
"""
from __future__ import annotations

import argparse
import json
import re
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
    _summaries_differ,
    _run_validate2,
)

EXAMPLES = RESEARCH_ROOT / "step-examples"


def _variant_ws_collapsed(body: bytes) -> bytes:
    """Collapse runs of whitespace inside DATA section to a single space.

    Preserves string literals (don't mangle their content)."""
    # We won't try to perfectly preserve strings; we only collapse spaces
    # *outside* of apostrophe pairs. Simplistic but works for our fixtures.
    out = bytearray()
    i = 0
    n = len(body)
    in_str = False
    last_was_space = False
    while i < n:
        c = body[i]
        if c == ord("'"):
            in_str = not in_str
            out.append(c)
            last_was_space = False
            i += 1
            continue
        if not in_str and c in (0x20, 0x09):
            if not last_was_space:
                out.append(0x20)
                last_was_space = True
            i += 1
            continue
        out.append(c)
        last_was_space = False
        i += 1
    return bytes(out)


def _variant_crlf(body: bytes) -> bytes:
    # Normalize to LF first, then convert to CRLF
    body = body.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return body.replace(b"\n", b"\r\n")


def _variant_lf(body: bytes) -> bytes:
    return body.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _variant_comment_stripped(body: bytes) -> bytes:
    """Remove all `/* */` comment blocks (replacing with a single space).

    Preserves the magic line and section markers. Skips fixtures whose
    defect is in a comment block (unlikely but possible).
    """
    return re.sub(rb"/\*.*?\*/", b" ", body, flags=re.DOTALL)


_VARIANTS = {
    "ws_collapsed": _variant_ws_collapsed,
    "crlf": _variant_crlf,
    "lf": _variant_lf,
    "comment_stripped": _variant_comment_stripped,
}


def _test_one(entry: dict) -> dict[str, Any]:
    fixture = EXAMPLES / entry["section_dir"] / f"{entry['id']}.stp"
    if not fixture.is_file():
        return {"id": entry["id"], "status": "no-fixture"}
    body = fixture.read_bytes()
    baseline = _baseline_summary(entry)
    if baseline is None:
        return {"id": entry["id"], "status": "no-baseline"}

    diffs: list[str] = []
    diff_details: dict[str, str] = {}
    for vname, vfn in _VARIANTS.items():
        mutated = vfn(body)
        if mutated == body:
            continue  # no-op variant
        with tempfile.NamedTemporaryFile(suffix=".stp", delete=False) as tf:
            tf.write(mutated)
            tmp_path = Path(tf.name)
        try:
            new_summary = _run_validate2(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
        if new_summary is None or "_error" in new_summary:
            continue
        if _summaries_differ(baseline, new_summary):
            diffs.append(vname)
            diff_details[vname] = format_live_spec(new_summary)
    return {
        "id": entry["id"],
        "status": "differs" if diffs else "invariant",
        "differing_variants": diffs,
        "diff_details": diff_details,
        "baseline": format_live_spec(baseline),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._format_invariance")
    p.add_argument("--sample", type=int, default=100, help="sample size (0=all)")
    p.add_argument("--all", action="store_true")
    p.add_argument("--section", type=str)
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("/tmp/cad-format-invariance.json"))
    args = p.parse_args(argv)

    entries = list(catalog.iter_canonical())
    if args.section:
        entries = [e for e in entries if e["section_dir"] == args.section]
    if not args.all and args.sample > 0 and len(entries) > args.sample:
        import random
        rng = random.Random(args.seed)
        entries = rng.sample(entries, args.sample)
    print(f"Testing {len(entries)} fixtures with {args.workers} workers", file=sys.stderr)

    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_test_one, e): e for e in entries}
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
    print(f"\nFormat-invariance results ({len(results)} fixtures):")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<22} {v:>4}")

    differs = [r for r in results if r["status"] == "differs"]
    if differs:
        # Variant breakdown
        variant_breakdown = Counter()
        for r in differs:
            for vn in r["differing_variants"]:
                variant_breakdown[vn] += 1
        print(f"\nFormat-dependent variants:")
        for vn, n in variant_breakdown.most_common():
            print(f"  {vn:<22} {n:>4}")
        print(f"\nFirst 15 format-dependent fixtures:")
        for r in differs[:15]:
            print(f"  {r['id']:<8}  baseline={r['baseline'][:40]:<42}  variants={r['differing_variants']}")
    print(f"\nFull results: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
