"""Defect-TARGETED mutation validator for the ``bytes-only`` provenance tier.

Companion to (and correction of) ``_mutation_test``. That tool flips a *random*
digit anywhere in the DATA section and saturates at high depth (see
BACKLOG DEF-MUT-DEPTH). This one mutates only the bytes that lie **inside a
fixture's own ``Byte assertion`` match region** — the defect-bearing bytes —
and asks: does mutating the defect change what a BRep-load GEOMETRY kernel
(OCCT / gmsh) sees?

A ``bytes-only`` fixture claims its defect is context/metadata that OCC does not
read at BRep-load time. This directly tests that claim:

- **invisible**  -> mutating the defect bytes never changed occt/gmsh -> the
  bytes-only tag is honest.
- **detected**   -> a defect-byte mutation changed occt/gmsh -> the defect IS
  geometry-visible; the tag should be ``bytes-sufficient``.
- **no-target-byte** -> the assertion region has no mutable digit/letter (a
  structural assertion); this method can't probe it (not a failure).

Non-geometry oracles (ifcopenshell schema parser, part21_strict) are reported as
INFO only — they can react to a byte change without the geometry kernel doing
so, which does not contradict a bytes-only (BRep-load) claim.

Run:  cd validation && uv run python -m step_corpus._bytes_only_probe [--max-pos N]
"""
from __future__ import annotations

import argparse
import random
import tempfile
from pathlib import Path

from step_corpus import catalog
from step_corpus._byte_locations import find_all_match_locations
from step_corpus._mutation_test import _mutate_byte, _run_validate2, EXAMPLES

# BRep-load geometry kernels — the oracles a bytes-only claim is about.
GEOM = ("occt_heal_on", "occt_heal_off", "gmsh_autofix_on", "gmsh_autofix_off")
# Reported but NOT used for the verdict (syntax/schema parsers + the non-kernel
# structural linter — a bytes-only defect SHOULD move these, that's expected).
INFO = ("ifcopenshell", "part21_strict", "structural")


def _pick(summary: dict | None, keys) -> dict:
    return {k: (summary or {}).get(k, "?") for k in keys}


def _mutable_positions(body: bytes, ranges) -> list[int]:
    out = []
    for a, b in ranges:
        for i in range(a, min(b, len(body))):
            c = body[i]
            if 0x30 <= c <= 0x39 or 0x41 <= c <= 0x5A or 0x61 <= c <= 0x7A:
                out.append(i)
    return out


def probe_entry(entry: dict, max_pos: int, rng: random.Random) -> dict:
    fid, sec = entry["id"], entry["section_dir"]
    stp = EXAMPLES / sec / f"{fid}.stp"
    if not stp.is_file():
        return {"id": fid, "verdict": "no-stp"}
    body = stp.read_bytes()
    ranges = find_all_match_locations(body, entry.get("byte_assertions") or [])
    positions = _mutable_positions(body, ranges)
    if not positions:
        return {"id": fid, "verdict": "no-target-byte"}
    base = _run_validate2(stp)
    base_geom, base_info = _pick(base, GEOM), _pick(base, INFO)
    if len(positions) > max_pos:
        positions = sorted(rng.sample(positions, max_pos))
    info_flip = None
    for p in positions:
        mut = _mutate_byte(body, p, rng)
        with tempfile.NamedTemporaryFile("wb", suffix=".stp", delete=False) as f:
            f.write(mut)
            tp = Path(f.name)
        try:
            s = _run_validate2(tp)
        finally:
            tp.unlink(missing_ok=True)
        g = _pick(s, GEOM)
        if g != base_geom:
            return {"id": fid, "verdict": "DETECTED", "pos": p,
                    "diff": {k: (base_geom[k], g[k]) for k in GEOM if base_geom[k] != g[k]}}
        if info_flip is None and _pick(s, INFO) != base_info:
            info_flip = {k: v for k, v in _pick(s, INFO).items() if v != base_info.get(k)}
    return {"id": fid, "verdict": "invisible", "info_flip": info_flip}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pos", type=int, default=6,
                    help="max mutable defect-byte positions probed per fixture")
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    results = []
    for e in catalog.iter_canonical():
        if e.get("provenance_tier") == "bytes-only":
            results.append(probe_entry(e, args.max_pos, rng))

    from collections import Counter
    dist = Counter(r["verdict"] for r in results)
    print(f"{'fixture':10} verdict")
    for r in sorted(results, key=lambda r: r["id"]):
        extra = ""
        if r["verdict"] == "DETECTED":
            extra = f"  pos{r['pos']} {r['diff']}"
        elif r.get("info_flip"):
            extra = f"  (info-only flip: {r['info_flip']})"
        print(f"{r['id']:10} {r['verdict']}{extra}")
    print(f"\n{len(results)} bytes-only fixtures: {dict(dist)}")
    detected = [r for r in results if r["verdict"] == "DETECTED"]
    if detected:
        print("\nGEOMETRY-VISIBLE defect bytes (retag -> bytes-sufficient):")
        for r in detected:
            print(f"  {r['id']}: {r['diff']}")
        return 1
    print("\nAll bytes-only tags are geometry-kernel invisible (honest).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
