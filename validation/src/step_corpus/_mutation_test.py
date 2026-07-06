"""Mutation-test fixtures: confirm the bytes actually drive oracle behavior.

For each fixture in the sample:

1. Load the pre-existing validate2 summary from /tmp/cad-v2-out/<sec>/<id>.json
   (the "baseline" oracle output).
2. Identify a defect-bearing byte location in the DATA section. Heuristic:
   pick a digit inside a numeric literal, or a digit inside an entity
   reference (#N), or a coordinate component. Skip whitespace and
   structural punctuation.
3. Mutate that byte (digit -> different digit, letter -> different letter).
4. Write the mutated copy to a temp file.
5. Run validate2 on the mutated copy.
6. Compare the new summary with the baseline.

A fixture is **detected** if any of the four oracles produces a different
spec value (e.g. baseline `occt=shape(1)/shape(1)` becomes `occt=empty/empty`,
or `gmsh=shape(7)` becomes `gmsh=signal(11)`).

A fixture is **undetected** if all four oracle specs are byte-identical to
baseline. Those are flagged for review: either the mutation didn't land in
a defect-relevant region, or the fixture's defect isn't actually being
detected by the oracles.

Usage::

    cd validation
    uv run python -m step_corpus._mutation_test --sample 100
    uv run python -m step_corpus._mutation_test --section 12-3a-shells --sample 20
    uv run python -m step_corpus._mutation_test --all   # ~4 hours, full corpus

The script is parallelized via ProcessPoolExecutor (default: 6 workers).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT
from step_corpus._final_verdict import format_live_spec

V2_BASE = Path("/tmp/cad-v2-out")
TIER3_BASE = Path("/tmp/cad-v2-out-tier3")
EXAMPLES = RESEARCH_ROOT / "step-examples"

# Pattern matches a digit inside a numeric literal or an entity reference.
# We deliberately avoid mutating whitespace, structural punctuation, or
# tokens we don't understand.
_DIGIT_RE = re.compile(rb"[0-9]")


def _baseline_summary(entry: dict) -> dict | None:
    p = V2_BASE / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text()).get("summary")
    except Exception:
        return None


def _baseline_tier3(entry: dict) -> dict | None:
    p = TIER3_BASE / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _tier3_signature(t3: dict | None) -> tuple:
    """Coarse fingerprint of a tier3 output.

    A change in any of these signals "the kernel saw something different":
    - load status
    - face count, edge count, vertex count
    - sum of face areas (rounded)
    - brepcheck.valid flag

    We deliberately don't compare every field; small numerical drift is
    expected. The fingerprint is meant to flag categorical changes only.
    """
    if t3 is None:
        return ("none",)
    faces = t3.get("faces", []) or []
    n_faces = len(faces)
    n_edges = t3.get("n_edges_total", 0)
    n_vertices = t3.get("n_vertices_total", 0)
    # Sum of face areas, but cap at 1e10 so 8e+100 doesn't dominate
    area_sum = 0.0
    for f in faces:
        a = f.get("area", 0.0) or 0.0
        if abs(a) < 1e10:
            area_sum += a
    # Round to 3 sig figs to ignore micro-jitter
    area_round = round(area_sum, 6) if -1e6 < area_sum < 1e6 else round(area_sum, 0)
    valid = (t3.get("brepcheck") or {}).get("valid")
    return (t3.get("load"), n_faces, n_edges, n_vertices, area_round, valid)


def _data_section_range(body: bytes) -> tuple[int, int] | None:
    """Return (start, end) byte offsets of the DATA section body, excluding
    the `DATA;` and `ENDSEC;` markers themselves."""
    start = body.find(b"DATA;")
    if start < 0:
        return None
    start += len(b"DATA;")
    end = body.find(b"ENDSEC;", start)
    if end < 0:
        return None
    return start, end


def _pick_mutation(body: bytes, rng: random.Random) -> int | None:
    """Pick a byte offset to mutate. Returns None if no candidate."""
    rng_data = _data_section_range(body)
    if rng_data is None:
        return None
    start, end = rng_data
    # Find all digit positions inside the DATA section
    candidates = [m.start() for m in _DIGIT_RE.finditer(body, start, end)]
    if not candidates:
        return None
    return rng.choice(candidates)


def _mutate_byte(body: bytes, pos: int, rng: random.Random) -> bytes:
    """Mutate byte at pos: digit -> different digit; letter -> different letter."""
    b = body[pos]
    if 0x30 <= b <= 0x39:
        # digit
        choices = [c for c in range(0x30, 0x3A) if c != b]
        new_b = rng.choice(choices)
    elif 0x41 <= b <= 0x5A or 0x61 <= b <= 0x7A:
        # letter: flip case and shift one
        new_b = b ^ 0x01
    else:
        new_b = b ^ 0x01
    return body[:pos] + bytes([new_b]) + body[pos+1:]


def _run_module(module: str, path: Path) -> dict | None:
    """Run a step_corpus module on a fixture and return its parsed JSON."""
    venv_py = RESEARCH_ROOT / "validation" / ".venv" / "bin" / "python3"
    if not venv_py.is_file():
        venv_py = "python3"
    try:
        proc = subprocess.run(
            [str(venv_py), "-m", module, str(path), "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(RESEARCH_ROOT / "validation"),
        )
    except subprocess.TimeoutExpired:
        return {"timeout": True}
    if proc.returncode != 0:
        return {"_error": f"rc={proc.returncode}", "_stderr": proc.stderr[-300:]}
    try:
        return json.loads(proc.stdout)
    except Exception as exc:
        return {"_error": f"json: {exc}", "_stdout": proc.stdout[:300]}


def _run_validate2(path: Path) -> dict | None:
    parsed = _run_module("step_corpus.validate2", path)
    if parsed is None or "_error" in (parsed or {}) or parsed.get("timeout"):
        return parsed
    return parsed.get("summary")


def _run_tier3(path: Path) -> dict | None:
    return _run_module("step_corpus.tier3_geometric", path)


def _summaries_differ(a: dict | None, b: dict | None) -> bool:
    if a is None or b is None:
        return a is not b
    # Spec-string fields (legacy + part21_strict).
    keys = ("occt_heal_on", "occt_heal_off",
            "gmsh_autofix_on", "gmsh_autofix_off",
            "ifcopenshell", "part21_strict",
            # Non-kernel structural linter: a mutation that changes the
            # structural defect code counts as detected.
            "structural",
            # Diagnostic signatures: distinguish silent-empty fixtures
            # by *why* they came out silent.
            "occt_diag_on", "occt_diag_off", "gmsh_diag")
    for k in keys:
        if a.get(k, "?") != b.get(k, "?"):
            return True
    return False


def _test_one(entry: dict, seed: int, n_mutations: int = 1) -> dict[str, Any]:
    """Mutation-test one fixture. Returns a result dict.

    With ``n_mutations > 1``, runs N independent mutations (different
    seeds, different positions) and reports detected if ANY mutation
    flips the oracle/tier3 signature. Mutation is "undetected" only if
    EVERY mutation leaves both signatures byte-identical to baseline.

    Detection logic compares both the validate2 oracle summary AND the
    tier3 fingerprint. A mutation is "detected" if EITHER changes.
    """
    fixture = EXAMPLES / entry["section_dir"] / f"{entry['id']}.stp"
    if not fixture.is_file():
        return {"id": entry["id"], "status": "no-fixture"}
    body = fixture.read_bytes()
    baseline_v2 = _baseline_summary(entry)
    baseline_t3 = _baseline_tier3(entry)
    baseline_t3_sig = _tier3_signature(baseline_t3)
    if baseline_v2 is None:
        return {"id": entry["id"], "status": "no-baseline"}
    rng_top = random.Random(seed)
    attempts = []
    for k in range(n_mutations):
        attempt_seed = rng_top.randint(0, 1 << 31)
        rng = random.Random(attempt_seed)
        pos = _pick_mutation(body, rng)
        if pos is None:
            continue
        mutated = _mutate_byte(body, pos, rng)
        with tempfile.NamedTemporaryFile(suffix=".stp", delete=False) as tf:
            tf.write(mutated)
            tmp_path = Path(tf.name)
        try:
            new_summary = _run_validate2(tmp_path)
            new_t3 = _run_tier3(tmp_path) if new_summary and "_error" not in new_summary else None
        finally:
            tmp_path.unlink(missing_ok=True)
        if new_summary is None or "_error" in new_summary:
            attempts.append({"pos": pos, "status": "error", "v2_changed": False, "t3_changed": False})
            continue
        if new_summary.get("timeout"):
            attempts.append({"pos": pos, "status": "timeout", "v2_changed": False, "t3_changed": False})
            continue
        v2_changed = _summaries_differ(baseline_v2, new_summary)
        t3_changed = (baseline_t3_sig != _tier3_signature(new_t3))
        attempts.append({
            "pos": pos,
            "status": "detected" if (v2_changed or t3_changed) else "undetected",
            "v2_changed": v2_changed,
            "t3_changed": t3_changed,
            "spec": format_live_spec(new_summary),
        })

    if not attempts:
        return {"id": entry["id"], "status": "no-target-byte"}

    any_detected = any(a["status"] == "detected" for a in attempts)
    return {
        "id": entry["id"],
        "status": "detected" if any_detected else "undetected",
        "n_attempts": len(attempts),
        "attempts": attempts,
        "baseline": format_live_spec(baseline_v2),
    }


def _stratified_sample(entries: list[dict], n: int, seed: int) -> list[dict]:
    """Pick ~n entries proportional to section size, focusing on §12.3."""
    rng = random.Random(seed)
    by_sec: dict[str, list[dict]] = {}
    for e in entries:
        by_sec.setdefault(e["section_dir"], []).append(e)
    # Bias toward §12.3 (where reverse test was weakest)
    weights = {
        "12-3a-shells": 1.5, "12-3b-wires": 1.5, "12-3c-faces": 1.5,
    }
    total_w = sum(len(v) * weights.get(k, 1.0) for k, v in by_sec.items())
    out = []
    for sec, lst in by_sec.items():
        share = round(n * len(lst) * weights.get(sec, 1.0) / total_w)
        share = min(share, len(lst))
        if share > 0:
            out.extend(rng.sample(lst, share))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._mutation_test")
    p.add_argument("--sample", type=int, default=100, help="number of fixtures to test")
    p.add_argument("--all", action="store_true", help="test every fixture")
    p.add_argument("--section", type=str, help="restrict to one section_dir, e.g. 12-3a-shells")
    p.add_argument("--oracle-active", action="store_true",
                   help="restrict to fixtures whose baseline isn't silent-empty (the only ones where mutation has signal)")
    p.add_argument("--mutations", type=int, default=1,
                   help="number of independent mutations per fixture (detect if any flip)")
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=Path("/tmp/cad-mutation-test.json"))
    args = p.parse_args(argv)

    entries = list(catalog.iter_canonical())
    if args.section:
        entries = [e for e in entries if e["section_dir"] == args.section]
    if args.oracle_active:
        SILENT = "occt=empty/empty gmsh=empty ifc=schema_n/a"
        kept = []
        for e in entries:
            s = _baseline_summary(e)
            if s and format_live_spec(s) != SILENT:
                kept.append(e)
        entries = kept
        print(f"oracle-active filter: {len(entries)} fixtures with non-silent baseline", file=sys.stderr)
    if args.all:
        sample = entries
    else:
        sample = _stratified_sample(entries, args.sample, args.seed)
    print(f"Testing {len(sample)} fixtures with {args.workers} workers", file=sys.stderr)

    results: list[dict[str, Any]] = []
    # Per-fixture seed is derived deterministically from (top_seed, fixture_id)
    # so that mutation targets are STABLE across runs regardless of iteration
    # order (--section vs --all, worker count, etc.). Previous versions used
    # `rng.randint(...)` in iteration order, which caused the same fixture to
    # get different seeds depending on how it was invoked and produced
    # non-reproducible detected/undetected verdicts across runs.
    import hashlib
    def _stable_seed(fid: str) -> int:
        h = hashlib.md5(f"{args.seed}:{fid}".encode()).digest()
        return int.from_bytes(h[:4], "big")
    seeds = {e["id"]: _stable_seed(e["id"]) for e in sample}

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_test_one, e, seeds[e["id"]], args.mutations): e for e in sample}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            done += 1
            if done % 10 == 0:
                print(f"  {done}/{len(sample)} done", file=sys.stderr)

    args.out.write_text(json.dumps(results, indent=2))

    from collections import Counter
    by_status = Counter(r["status"] for r in results)
    print(f"\nMutation test results ({len(results)} fixtures):")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<20} {v:>4}")

    detected = by_status.get("detected", 0)
    undetected = by_status.get("undetected", 0)
    if detected + undetected > 0:
        rate = 100 * detected / (detected + undetected)
        print(f"\nDetection rate: {detected}/{detected+undetected} ({rate:.1f}%)")

    undetected_rows = [r for r in results if r["status"] == "undetected"]
    if undetected_rows:
        print(f"\nFirst 15 undetected (all {args.mutations} attempt(s) left baseline unchanged):")
        for r in undetected_rows[:15]:
            print(f"  {r['id']:<8}  baseline={r.get('baseline')}")

    print(f"\nFull results: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
