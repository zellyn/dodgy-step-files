"""Surface divergences between the pure-Python Part-21 oracle and OCCT.

Reads /tmp/cad-v2-out/<sec>/<id>.json for every fixture and bins each
result by the (part21_strict, occt) pair:

- **agree-accept**: both say the file is well-formed and loads.
- **agree-reject**: both say the file is malformed.
- **purepy-rejects-occt-accepts**: pure-Python validator finds a
  spec-level violation that OCCT silently heals or ignores. Catalog
  should know about these.
- **purepy-accepts-occt-rejects**: OCCT is stricter than spec. Either
  an OCCT bug or undocumented spec interpretation.
- **purepy-warns**: spec-level warning (BOM etc.) that doesn't make
  the file invalid.

Usage::

    cd validation
    uv run python -m step_corpus._oracle_divergence
    uv run python -m step_corpus._oracle_divergence --json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

V2 = Path("/tmp/cad-v2-out")


def _classify(spec: dict) -> tuple[str, str]:
    """Return (purepy, occt): coarse {accept|reject|warn|other}."""
    purepy = spec.get("part21_strict", "?")
    if purepy == "accept":
        purepy_class = "accept"
    elif purepy.startswith("warn"):
        purepy_class = "warn"
    elif purepy.startswith("reject"):
        purepy_class = "reject"
    else:
        purepy_class = "other"

    occt = spec.get("occt_heal_off", "?")
    if "shape(" in occt:
        occt_class = "accept"
    elif occt == "empty":
        occt_class = "accept"  # accepted, just no shapes
    elif "reject" in occt:
        occt_class = "reject"
    elif "signal(" in occt:
        occt_class = "crash"
    else:
        occt_class = "other"

    return purepy_class, occt_class


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._oracle_divergence")
    p.add_argument("--json", action="store_true")
    p.add_argument("--show", default="purepy-rejects-occt-accepts,purepy-accepts-occt-rejects",
                   help="comma-separated divergence buckets to list")
    args = p.parse_args(argv)

    rows: list[dict[str, Any]] = []
    for jp in sorted(V2.rglob("*.json")):
        try:
            d = json.loads(jp.read_text())
        except Exception:
            continue
        s = d.get("summary") or {}
        purepy, occt = _classify(s)
        bucket = f"{purepy}/{occt}"
        rows.append({
            "id": jp.stem,
            "section": jp.parent.name,
            "purepy": s.get("part21_strict"),
            "occt_off": s.get("occt_heal_off"),
            "occt_on":  s.get("occt_heal_on"),
            "ifc": s.get("ifcopenshell"),
            "purepy_class": purepy,
            "occt_class": occt,
            "bucket": bucket,
        })

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    bucket_count = Counter(r["bucket"] for r in rows)
    print(f"Cross-oracle agreement across {len(rows)} fixtures (purepy / occt):\n")
    print(f"{'bucket':<24} count")
    print(f"{'-' * 24} -----")
    for k in sorted(bucket_count, key=lambda x: -bucket_count[x]):
        print(f"{k:<24} {bucket_count[k]:>5}")

    # Headline divergences
    print()
    show = set(args.show.split(","))
    if "purepy-rejects-occt-accepts" in show:
        div = [r for r in rows if r["purepy_class"] == "reject" and r["occt_class"] == "accept"]
        print(f"\n=== purepy-rejects but OCCT-accepts ({len(div)}): OCCT silently heals spec violations")
        for r in div[:30]:
            print(f"  {r['id']:<8}  purepy={r['purepy']:<28}  occt_off={r['occt_off']}")
    if "purepy-accepts-occt-rejects" in show:
        div = [r for r in rows if r["purepy_class"] in ("accept", "warn") and r["occt_class"] == "reject"]
        print(f"\n=== purepy-accepts but OCCT-rejects ({len(div)}): OCCT stricter than spec")
        for r in div[:30]:
            print(f"  {r['id']:<8}  purepy={r['purepy']:<28}  occt_off={r['occt_off']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
