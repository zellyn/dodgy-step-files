"""Mutation tester for the §12.14 mesh sub-corpus.

Analogue of `_mutation_test.py`, adapted for `.mesh.json` fixtures and
the pymeshfix oracle. Per-fixture method:

    1. Run pymeshfix on the untouched fixture → baseline_signature
    2. For each of N mutations (default 3):
       a. Pick a random byte inside the vertices[]/triangles[] arrays
       b. Flip a digit (or letter) at that offset
       c. Re-run pymeshfix on the mutated bytes
       d. Compare mutated_signature vs baseline_signature
    3. Tally per fixture: was at least one mutation detected?

A fixture is "mutation-detected" if any of its mutations produced a
different pymeshfix signature. "Structurally inert" fixtures get the
same signature regardless of single-byte mutations — they're the
analogue of the §12.5 silent-empty STEP fixtures from the Q5 sweep
and tell us where the corpus needs strengthening.

Signature includes: status, n_vertices_in, n_triangles_in,
n_vertices_out, n_triangles_out, n_boundaries.

Usage:
    cd validation && uv run python -m step_corpus._mesh_mutation_test [--limit N]
"""
from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from step_corpus._pymeshfix_oracle import run_pymeshfix, _PYMESHFIX_INSTALLED


ROOT = Path(__file__).resolve().parents[3]
MESH_DIR = ROOT / "mesh-examples" / "12-14-mesh"


# Match any digit byte; the bulk of mesh.json content is integers
# (triangle indices) and floats (vertex coordinates), both digit-rich.
_DIGIT_RE = re.compile(rb"[0-9]")


def _arrays_range(body: bytes) -> tuple[int, int] | None:
    """Return (start, end) byte offset spanning the `vertices` and
    `triangles` arrays — the geometric content. Falls back to the
    full body span if those keys aren't located.
    """
    v_pos = body.find(b'"vertices"')
    t_end = body.rfind(b'"triangles"')
    if v_pos < 0 or t_end < 0:
        return (0, len(body))
    # Extend t_end past the closing bracket of the triangles array.
    end = body.find(b"]", t_end)
    if end < 0:
        end = len(body)
    return (v_pos, end + 1)


def _pick_mutation(body: bytes, rng: random.Random) -> int | None:
    """Pick a random digit offset in vertices/triangles."""
    span = _arrays_range(body)
    if span is None:
        return None
    start, end = span
    cands = [m.start() for m in _DIGIT_RE.finditer(body, start, end)]
    if not cands:
        return None
    return rng.choice(cands)


def _mutate_byte(body: bytes, pos: int, rng: random.Random) -> bytes:
    """Flip the digit at pos to a different digit (0..9)."""
    b = body[pos]
    if 0x30 <= b <= 0x39:
        choices = [c for c in range(0x30, 0x3A) if c != b]
        new_b = rng.choice(choices)
    else:
        new_b = b ^ 0x01
    return body[:pos] + bytes([new_b]) + body[pos+1:]


def _signature(result: dict) -> tuple:
    """Compact per-fixture signature used to detect mutation impact."""
    return (
        result.get("status"),
        result.get("n_vertices_in"),
        result.get("n_triangles_in"),
        result.get("n_vertices_out"),
        result.get("n_triangles_out"),
        result.get("n_boundaries"),
    )


def _run_on_bytes(body: bytes) -> dict:
    """Write body to a temp file and run pymeshfix in a subprocess.

    Subprocess isolation matters because MeshFix's C++ core can SIGSEGV
    on adversarial inputs (negative indices, out-of-bounds refs after
    mutation, etc.). An in-process crash would take down the whole
    mutation runner; subprocess containment turns it into a
    `status: crash` record.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".mesh.json", mode="wb", delete=False
    ) as tmp:
        tmp.write(body)
        tmp_path = Path(tmp.name)
    try:
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "step_corpus._pymeshfix_oracle",
                 str(tmp_path), "--json"],
                capture_output=True, text=True, timeout=15,
            )
        except subprocess.TimeoutExpired:
            return {"status": "timeout"}
        if proc.returncode < 0:
            return {"status": "crash", "stderr_tail": f"signal={-proc.returncode}"}
        if proc.returncode not in (0,):
            # Oracle module returns rc=1 for "rejected", rc=2 for
            # missing-fixture; for our purposes that's still a sane
            # parseable record (or fall through to JSON parse below).
            pass
        try:
            return json.loads(proc.stdout)
        except Exception:
            return {"status": "error", "stderr_tail": proc.stderr[-200:]}
    finally:
        try: tmp_path.unlink()
        except Exception: pass


def _test_one(
    fixture: Path,
    seed: int,
    n_mutations: int = 3,
) -> dict[str, Any]:
    body = fixture.read_bytes()
    baseline = run_pymeshfix(fixture)
    base_sig = _signature(baseline)
    rng = random.Random(seed)

    if baseline["status"] != "loaded":
        # Don't bother mutating fixtures pymeshfix can't load.
        return {
            "fixture": fixture.stem,
            "baseline_status": baseline["status"],
            "mutations": 0,
            "detected": 0,
            "signatures": [],
        }

    detected = 0
    sigs = []
    for _ in range(n_mutations):
        pos = _pick_mutation(body, rng)
        if pos is None:
            continue
        mutated = _mutate_byte(body, pos, rng)
        try:
            result = _run_on_bytes(mutated)
        except Exception as e:
            sigs.append(("error", str(e)[:40]))
            continue
        sig = _signature(result)
        sigs.append(sig)
        if sig != base_sig:
            detected += 1

    return {
        "fixture": fixture.stem,
        "baseline_status": baseline["status"],
        "baseline_signature": base_sig,
        "mutations": n_mutations,
        "detected": detected,
        "signatures": sigs,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._mesh_mutation_test")
    p.add_argument("--limit", type=int, default=0,
                   help="Only test first N fixtures (default: all)")
    p.add_argument("--mutations", type=int, default=3,
                   help="Mutations per fixture (default: 3)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--json-out", type=Path, default=None,
                   help="Write per-fixture results as JSONL to this path")
    args = p.parse_args(argv)

    if not _PYMESHFIX_INSTALLED:
        print("pymeshfix not installed; cannot run mutation tests", file=sys.stderr)
        return 1

    fixtures = sorted(MESH_DIR.glob("Me*.mesh.json"))
    if args.limit:
        fixtures = fixtures[:args.limit]

    print(f"Mutating {len(fixtures)} mesh fixtures "
          f"× {args.mutations} mutations/fixture...")

    results = []
    detect_buckets = Counter()
    baseline_buckets = Counter()
    out_fp = open(args.json_out, "w") if args.json_out else None
    try:
        for i, f in enumerate(fixtures):
            r = _test_one(f, seed=args.seed + i, n_mutations=args.mutations)
            results.append(r)
            baseline_buckets[r["baseline_status"]] += 1
            if r["baseline_status"] == "loaded":
                if r["detected"] > 0:
                    detect_buckets["detected"] += 1
                else:
                    detect_buckets["inert"] += 1
            else:
                detect_buckets["baseline_not_loaded"] += 1
            if out_fp:
                out_fp.write(json.dumps(r) + "\n")
            if (i + 1) % 100 == 0:
                print(f"  ... {i+1}/{len(fixtures)} done")
    finally:
        if out_fp: out_fp.close()

    total = len(fixtures)
    print()
    print("=== Mutation-test summary ===")
    print(f"Total fixtures:       {total}")
    print(f"Baseline status:")
    for s, c in baseline_buckets.most_common():
        print(f"  {s:25} {c:4} ({100.0*c/total:.1f}%)")
    print()
    loaded = baseline_buckets.get("loaded", 0)
    if loaded:
        det = detect_buckets["detected"]
        inert = detect_buckets["inert"]
        print(f"Of {loaded} fixtures with loaded baseline:")
        print(f"  detected by ≥1 mutation: {det:4} ({100.0*det/loaded:.1f}%)")
        print(f"  structurally inert:       {inert:4} ({100.0*inert/loaded:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
