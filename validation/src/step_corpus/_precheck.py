"""Pre-push audit scoped to git-changed catalog entries.

Runs the byte-assertion, tier-3-assertion, and bytes/tier-3 cross-audit
checks against only the catalog entries that the current working tree
has changed relative to a baseline (default: ``HEAD``). Designed to be
fast enough to run before every push.

Detection: a catalog entry is "changed" if any of these paths appears
in the diff or as untracked:

  - ``step-examples/<section>/<ID>.stp``
  - ``fixture_sources/<section>/<ID>.py``
  - a ``### <ID> —`` heading inside ``STEP_PROBLEM_CATALOG.md`` whose
    block has any added/removed lines (parsed by walking the diff hunks)

If ``STEP_PROBLEM_CATALOG.json`` is the only catalog touch (it's a
generated index), the .md diff is the source of truth.

Usage:
    uv run python -m step_corpus._precheck
    uv run python -m step_corpus._precheck --base main
    uv run python -m step_corpus._precheck --ids Tsh050,Twi005
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from step_corpus import catalog

_FIXTURE_PATH_RE = re.compile(
    r"^(?:step-examples|fixture_sources)/[^/]+/([A-Z][a-z]+\d+)\.(?:stp|py)$"
)
_HEADING_RE = re.compile(r"^### ([A-Z][a-z]+\d+) ")
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATALOG_MD = "STEP_PROBLEM_CATALOG.md"


def _git(args: list[str]) -> str:
    r = subprocess.run(
        ["git", *args], cwd=_REPO_ROOT, capture_output=True, text=True, check=False
    )
    return r.stdout


def _changed_paths(base: str) -> list[str]:
    """Tracked diff vs base + untracked files."""
    tracked = _git(["diff", "--name-only", base]).splitlines()
    untracked = _git(["ls-files", "--others", "--exclude-standard"]).splitlines()
    return [p for p in (*tracked, *untracked) if p]


def _ids_from_paths(paths: list[str]) -> set[str]:
    ids: set[str] = set()
    for p in paths:
        m = _FIXTURE_PATH_RE.match(p)
        if m:
            ids.add(m.group(1))
    return ids


_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _id_line_ranges(md_path: Path) -> list[tuple[int, int, str]]:
    """Return [(start_line, end_line, id), ...] for each ### heading block."""
    text = md_path.read_text()
    ranges: list[tuple[int, int, str]] = []
    current_id: str | None = None
    current_start = 0
    lineno = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        m = _HEADING_RE.match(line)
        if m:
            if current_id is not None:
                ranges.append((current_start, lineno - 1, current_id))
            current_id = m.group(1)
            current_start = lineno
    if current_id is not None and lineno >= current_start:
        ranges.append((current_start, lineno, current_id))
    return ranges


def _ids_from_catalog_diff(base: str) -> set[str]:
    """Parse the .md diff hunk line numbers, map each to its enclosing ### ID."""
    diff = _git(["diff", "-U0", base, "--", _CATALOG_MD])
    if not diff:
        return set()
    ranges = _id_line_ranges(_REPO_ROOT / _CATALOG_MD)
    changed_lines: set[int] = set()
    for line in diff.splitlines():
        m = _HUNK_RE.match(line)
        if m:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) else 1
            for n in range(start, start + max(count, 1)):
                changed_lines.add(n)
    ids: set[str] = set()
    for n in changed_lines:
        for s, e, fid in ranges:
            if s <= n <= e:
                ids.add(fid)
                break
    return ids


def changed_ids(base: str = "HEAD") -> set[str]:
    paths = _changed_paths(base)
    ids = _ids_from_paths(paths)
    if _CATALOG_MD in paths:
        ids |= _ids_from_catalog_diff(base)
    return ids


def _filter_entries(ids: set[str]) -> list[dict]:
    return [e for e in catalog.iter_canonical() if e["id"] in ids]


def precheck(ids: set[str]) -> int:
    """Run the audits scoped to ``ids``. Returns process exit code."""
    if not ids:
        print("No changed catalog entries detected — nothing to check.")
        return 0
    print(f"Pre-checking {len(ids)} changed entries: {', '.join(sorted(ids))}")
    entries = _filter_entries(ids)
    found_ids = {e["id"] for e in entries}
    missing = ids - found_ids
    if missing:
        print(f"  (not in catalog, skipped: {', '.join(sorted(missing))})")
    if not entries:
        return 0

    from step_corpus._byte_assertions import check_all as byte_check_all
    from step_corpus._bytes_tier3_audit import audit_all as bt3_audit_all
    from step_corpus._tier3_assertions import check_all as tier3_check_all
    from step_corpus._schema_oracle import check_all as schema_check_all
    from step_corpus._category_lint import lint_one as category_lint_one
    from step_corpus._fixture_lint import lint_fixture as fixture_lint_one
    from step_corpus._build_catalog_json import RESEARCH_ROOT

    exit_code = 0

    print("\n[1/7] byte_assertions...")
    byte_results = byte_check_all(entries)
    byte_fails = [r for r in byte_results if r["status"] != "pass"]
    if byte_fails:
        exit_code = 1
        for r in byte_fails:
            print(f"  FAIL {r['id']:<8} {r['assertion']}  ({r.get('detail')})")
    else:
        print(f"  ok ({len(byte_results)} assertions across {len(entries)} entries)")

    print("\n[2/7] tier3_assertions...")
    tier3_results = tier3_check_all(entries)
    tier3_fails = [
        r for r in tier3_results
        if r["status"] in {"fail", "parse-error", "eval-error", "lhs-unresolved"}
    ]
    if tier3_fails:
        exit_code = 1
        for r in tier3_fails:
            actual = f"  actual={r['actual']!r}" if "actual" in r else ""
            print(f"  FAIL {r['id']:<8} [{r['status']}] {r['assertion']}{actual}")
    else:
        print(f"  ok ({len(tier3_results)} assertions)")

    print("\n[3/7] bytes/tier-3 cross-audit...")
    bt3_results = bt3_audit_all(entries)
    bt3_fails = [r for r in bt3_results if r["verdict"] == "inconsistent"]
    bt3_documented = [r for r in bt3_results if r["verdict"] == "documented"]
    if bt3_fails:
        exit_code = 1
        for r in bt3_fails:
            print(
                f"  INCONSISTENT {r['id']:<8} byte={r['byte_claim']!r} "
                f"tier3={r['tier3_claim']!r}\n    reason={r['reason']}"
            )
    else:
        suffix = f", {len(bt3_documented)} documented" if bt3_documented else ""
        print(f"  ok ({len(bt3_results)} pairs{suffix})")

    print("\n[4/7] schema-oracle...")
    schema_results = schema_check_all(entries)
    schema_fails = [
        r for r in schema_results
        if r.get("violations") and r.get("schema") not in (None, "AP242")
    ]
    if schema_fails:
        exit_code = 1
        for r in schema_fails:
            print(f"  FAIL {r['id']:<8} {r.get('schema')}  {r['violations']}")
    else:
        print(f"  ok ({len(schema_results)} fixtures)")

    print("\n[5/7] category-lint...")
    cat_fails = []
    for e in entries:
        for msg in category_lint_one(e):
            cat_fails.append((e["id"], msg))
    if cat_fails:
        exit_code = 1
        for fid, msg in cat_fails:
            print(f"  FAIL {fid:<8} {msg}")
    else:
        print(f"  ok ({len(entries)} entries)")

    # [6/7] fixture-lint: per-file structural invariants (END marker,
    # FILE_NAME stem match, etc.). Closes precheck gap that let Ls029 land
    # without an END-ISO-10303-21; close marker (Ls029 was on the exempt
    # list semantically — unterminated comment runs through EOF — but the
    # lint code wasn't told). The lint runs against every changed fixture;
    # if a new fixture has a structural defect that is genuinely the
    # documented bug, add its ID to _fixture_lint.EXEMPT_END_MARKER (or
    # EXEMPT_FILENAME_MATCH / EXEMPT_ID_IN_TEXT).
    print("\n[6/7] fixture-lint (structural invariants)...")
    examples_root = RESEARCH_ROOT / "step-examples"
    fl_fails = []
    fl_checked = 0
    for e in entries:
        fid = e["id"]
        # Find the .stp file for this entry. Catalog entries record a
        # 'category' / 'section' loosely; the fixture lives at
        # step-examples/<section>/<ID>.stp. We discover via glob.
        candidates = list(examples_root.rglob(f"{fid}.stp"))
        # Skip _quarantine
        candidates = [c for c in candidates if "_quarantine" not in c.parts]
        for stp in candidates:
            fl_checked += 1
            result = fixture_lint_one(stp)
            if result.get("errors"):
                for msg in result["errors"]:
                    fl_fails.append((fid, msg))
    if fl_fails:
        exit_code = 1
        for fid, msg in fl_fails:
            print(f"  FAIL {fid:<8} {msg}")
    else:
        print(f"  ok ({fl_checked} fixtures linted)")

    # [7/7] part21-validator pins: spot-check the small set of pinned
    # fixtures whose status (accept/reject) is hard-coded in
    # tests/test_part21_validator.py. Regenerating a fixture can silently
    # shift its validator status (Le028 went accept↔reject when CRLF + NUL
    # positioning changed). Run the pins here so the regen author sees the
    # break locally instead of in CI.
    print("\n[7/7] part21-validator pins...")
    from step_corpus._part21_validator import validate_file as _validate_file
    # Mirror the pin list from tests/test_part21_validator.py exactly.
    # Keep in sync — there is a self-test below that fails CI if these drift.
    PINS = [
        ("12-3a-shells/Tsh007.stp", "accept"),
        ("12-1a-encoding/Le001.stp", "accept_with_warnings"),
        ("12-1b-header/Lh002.stp", "reject"),
        ("12-1a-encoding/Le028.stp", "reject"),
    ]
    # Only re-validate pins whose fixture ID was actually changed.
    changed_pin_fids = {fid for fid in ids}
    pin_fails = []
    pin_checked = 0
    for rel, expected in PINS:
        pin_fid = Path(rel).stem
        if pin_fid not in changed_pin_fids:
            continue
        path = examples_root / rel
        if not path.is_file():
            continue
        pin_checked += 1
        v = _validate_file(path)
        if v.status != expected:
            pin_fails.append((pin_fid, expected, v.status))
    if pin_fails:
        exit_code = 1
        for fid, exp, got in pin_fails:
            print(f"  FAIL {fid:<8} validator pin: expected {exp}, got {got}")
    else:
        print(f"  ok ({pin_checked} pins re-validated)")

    print("\n=== PRECHECK FAILED ===" if exit_code else "\n=== PRECHECK OK ===")
    return exit_code


# Catalog-claim-IS-defect set: entries where schema mismatch is the documented bug.
# Source of truth lives in _schema_oracle.EXEMPT_SCHEMA_DEFECT_ID, but the
# precheck shouldn't fail on those, so we mirror the exemption here.
_SCHEMA_EXEMPT: set[str] = set()
try:
    from step_corpus._schema_oracle import EXEMPT_SCHEMA_DEFECT_ID as _SE  # type: ignore
    _SCHEMA_EXEMPT = set(_SE)
except Exception:
    pass


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._precheck")
    p.add_argument(
        "--base", default="HEAD",
        help="git ref to diff against (default: HEAD = uncommitted changes only). "
             "Use 'main' or 'origin/main' for changes-since-merge-base.",
    )
    p.add_argument(
        "--ids", default="",
        help="comma-separated explicit ID list (overrides git detection)",
    )
    args = p.parse_args(argv)

    if args.ids:
        ids = {x.strip() for x in args.ids.split(",") if x.strip()}
    else:
        ids = changed_ids(args.base)
    return precheck(ids)


if __name__ == "__main__":
    raise SystemExit(main())
