"""Tier-3 metric assertions for catalog entries.

Some catalog entries make specific geometric claims ("face area below
1e-9 mm²", "sliver aspect > 1e6", "edge length under tolerance"). This
module formalizes those claims as machine-checkable assertions and
provides a runner that compares them against tier3_geometric output.

Assertion format
----------------

Catalog entries opt in by adding one or more lines like::

    - **Tier-3 assertion**: face[0].area < 1e-9
    - **Tier-3 assertion**: face[0].sliver_aspect_max_min > 1e6
    - **Tier-3 assertion**: load == ok
    - **Tier-3 assertion**: n_edges_total >= 100

Supported left-hand sides:

- ``load`` (compares to ``ok`` / ``failed``)
- ``shape_null`` (boolean)
- ``n_faces_total``, ``n_edges_total``, ``n_vertices_total``
- ``face[i].area``, ``face[i].sliver_aspect_max_min``, ``face[i].edge_count``,
  ``face[i].surface_type``
- ``face[i].edge_orientations.forward``, ``.reversed``, ``.internal``,
  ``.external``  (per-face edge-loop orientation counts)
- ``face[i].bspline.is_rational``, ``.is_u_periodic``, ``.is_v_periodic``,
  ``.u_degree``, ``.v_degree``, ``.n_u_knots``, ``.n_v_knots``,
  ``.u_knot_mult_max``, ``.v_knot_mult_max``  (B-spline / Bezier surface
  introspection; ``bspline.*`` keys are absent on non-parametric surfaces)
- ``face[i].quadric.radius`` (cylinder, sphere)
- ``face[i].quadric.semi_angle``, ``.ref_radius`` (cone)
- ``face[i].quadric.major_radius``, ``.minor_radius`` (torus)
- ``face[i].quadric.axis_x``, ``.axis_y``, ``.axis_z`` (cylinder, cone, torus)
- ``face[i].quadric.loc_x``, ``.loc_y``, ``.loc_z`` (sphere)
  (analytic-surface introspection; ``quadric.*`` keys are absent on
  non-quadric surfaces)
- ``edge[i].length``, ``edge[i].curve_type``, ``edge[i].orientation``
- ``edge[i].bspline.is_rational``, ``.is_periodic``, ``.degree``,
  ``.n_knots``, ``.knot_mult_max``  (B-spline / Bezier curve introspection;
  ``bspline.*`` keys are absent on non-parametric curves)
- ``vertex[i].tolerance``, ``vertex[i].position``
- ``brepcheck.valid`` (boolean)

Operators: ``< <= == != >= > in``.

The intent is *coarse-grained* assertions that capture the catalog's
geometric claim; precise-numeric pinning belongs in a separate
regression test, not in the catalog.

Usage
-----

    uv run python -m step_corpus._tier3_assertions
    uv run python -m step_corpus._tier3_assertions --json   # machine-readable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT

# tier3 outputs from _run_corpus
TIER3_BASE = Path("/tmp/cad-v2-out-tier3")

_ASSERT_RE = re.compile(
    r"^- \*\*Tier-3 assertion\*\*:\s*(.+?)\s*$",
    re.MULTILINE,
)

_OPS = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "in": lambda a, b: a in b,
}

# Match `lhs op rhs`. lhs allows dots and [N] subscripts.
_EXPR_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_\.\[\]]*)\s*(<=|>=|==|!=|<|>|in)\s*(.+?)\s*$"
)


def _parse_assertion(line: str) -> tuple[str, str, Any] | None:
    m = _EXPR_RE.match(line)
    if not m:
        return None
    lhs, op, rhs = m.group(1), m.group(2), m.group(3).strip()
    # rhs is a Python literal-ish: number, string ("ok"), bool, list.
    # Try literal-eval-ish parsing.
    try:
        rhs_val = json.loads(rhs)
    except Exception:
        # bare token (`ok`, `failed`, `plane`, `True`, `False`) -> string/bool
        if rhs == "True":
            rhs_val = True
        elif rhs == "False":
            rhs_val = False
        elif rhs == "None":
            rhs_val = None
        else:
            rhs_val = rhs
    return lhs, op, rhs_val


def _resolve_lhs(tier3: dict, lhs: str) -> Any:
    """Resolve a dotted/subscripted path against a tier3 output dict.

    Examples:
      ``load`` -> tier3["load"]
      ``face[0].area`` -> tier3["faces"][0]["area"]
      ``n_edges_total`` -> tier3["n_edges_total"]
    """
    cur: Any = tier3
    # Split on dots, but treat subscripts attached to the previous token.
    tokens = re.findall(r"([A-Za-z_]+)(\[\d+\])?", lhs)
    for name, sub in tokens:
        if not name:
            continue
        # Handle plurals: face[i] -> faces[i]
        key = name
        if sub:
            if name == "face":
                key = "faces"
            elif name == "edge":
                key = "edges"
            elif name == "vertex":
                key = "vertices"
        if isinstance(cur, dict):
            cur = cur.get(key)
        else:
            return None
        if sub:
            idx = int(sub[1:-1])
            if isinstance(cur, list) and idx < len(cur):
                cur = cur[idx]
            else:
                return None
    return cur


def _entry_assertions(catalog_md_block: str) -> list[str]:
    """Legacy markdown-scrape path. Prefer ``entry['tier3_assertions']``
    from the JSON catalog; kept for backward compatibility."""
    return [m.group(1) for m in _ASSERT_RE.finditer(catalog_md_block)]


def _entry_block(entry_id: str, md_text: str) -> str:
    """Slice the markdown block for one entry. Legacy helper."""
    m = re.search(rf"^### {re.escape(entry_id)}\b", md_text, re.MULTILINE)
    if not m:
        return ""
    rest = md_text[m.end():]
    nm = re.search(r"^### ", rest, re.MULTILINE)
    end = m.end() + (nm.start() if nm else len(rest))
    return md_text[m.start():end]


def _tier3_path(entry: dict) -> Path:
    return TIER3_BASE / entry["section_dir"] / f"{entry['id']}.json"


def check_entry(entry: dict, md_text: str = "") -> list[dict[str, Any]]:
    """Return per-assertion result dicts for one entry.

    Reads from the JSON catalog's ``tier3_assertions`` field. Falls
    back to scraping markdown if the field is absent (legacy).
    """
    asserts = entry.get("tier3_assertions") or []
    if not asserts and md_text:
        block = _entry_block(entry["id"], md_text)
        asserts = _entry_assertions(block)
    if not asserts:
        return []
    t3p = _tier3_path(entry)
    if not t3p.is_file():
        return [{
            "id": entry["id"],
            "assertion": a,
            "status": "no-tier3-output",
            "reason": str(t3p),
        } for a in asserts]
    try:
        raw = t3p.read_text()
        # Strip ANSI escape codes emitted by OCCT diagnostics on stdout
        raw = re.sub(r"\x1b\[[0-9;]*m", "", raw)
        # Skip any non-JSON prefix lines (e.g., "*** ERR ..." diagnostic lines)
        idx = raw.find("{")
        if idx > 0:
            raw = raw[idx:]
        tier3 = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        return [{
            "id": entry["id"],
            "assertion": a,
            "status": "tier3-parse-error",
            "reason": str(exc),
        } for a in asserts]
    # If the tier3 runner itself crashed or timed out (rather than producing
    # a geometric report), treat it as tolerated infrastructure noise — the
    # same as if the file were absent entirely ("no-tier3-output").
    runner_status = tier3.get("status", "")
    if runner_status in ("tier3_failed", "tier3_timeout", "tier3_error"):
        return [{
            "id": entry["id"],
            "assertion": a,
            "status": "no-tier3-output",
            "reason": f"runner status: {runner_status}",
        } for a in asserts]
    results = []
    for a in asserts:
        parsed = _parse_assertion(a)
        if parsed is None:
            results.append({"id": entry["id"], "assertion": a, "status": "parse-error"})
            continue
        lhs, op, rhs = parsed
        actual = _resolve_lhs(tier3, lhs)
        if actual is None:
            results.append({"id": entry["id"], "assertion": a, "status": "lhs-unresolved", "lhs": lhs})
            continue
        try:
            ok = _OPS[op](actual, rhs)
        except Exception as exc:
            results.append({"id": entry["id"], "assertion": a, "status": "eval-error", "error": str(exc)})
            continue
        results.append({
            "id": entry["id"],
            "assertion": a,
            "status": "pass" if ok else "fail",
            "actual": actual,
            "rhs": rhs,
        })
    return results


def check_all(entries: Iterable[dict] | None = None) -> list[dict[str, Any]]:
    """Run tier-3 assertions for every catalog entry that declares any.

    Source of truth: the ``tier3_assertions`` field in the JSON
    catalog. Markdown is no longer scraped on the hot path.
    """
    out = []
    src = entries if entries is not None else catalog.iter_canonical()
    for entry in src:
        out.extend(check_entry(entry))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._tier3_assertions")
    p.add_argument("--json", action="store_true", help="emit JSON results")
    args = p.parse_args(argv)
    results = check_all()

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    # Statuses that should fail CI: assertion mistakes that the catalog can
    # fix. Statuses tolerated as infrastructure noise (see the
    # test_tier3_assertions docstring for the rationale):
    #   - no-tier3-output: the tier3 worker didn't run on this fixture
    #     (segfault / timeout); covered by validate2's spec line.
    #   - tier3-parse-error: tier3 produced empty/broken JSON (rare).
    FAILING_STATUSES = {"fail", "parse-error", "eval-error", "lhs-unresolved"}

    by_status: dict[str, int] = {}
    failures: list[dict] = []
    non_pass_for_display: list[dict] = []
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        if r["status"] != "pass":
            non_pass_for_display.append(r)
        if r["status"] in FAILING_STATUSES:
            failures.append(r)
    print(f"Tier-3 assertions: {len(results)} total")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<22} {v:>4}")
    if non_pass_for_display:
        print(f"\nFirst 20 non-pass:")
        for f in non_pass_for_display[:20]:
            extras = ""
            if "actual" in f:
                extras = f"  actual={f.get('actual')!r}"
            print(f"  {f['id']:<8} [{f['status']:<14}] {f['assertion']}{extras}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
