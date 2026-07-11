"""Lint pass over the fixture corpus.

Checks that every .stp fixture honors the corpus conventions:
- Filename's stem matches the FILE_NAME first argument.
- Top of file has a `/* ... */` Part-21 comment block (allowed before or after
  the ISO-10303-21; magic; most §12.11 adversarial fixtures put the comment
  before the magic line).
- The comment names the entry ID (matches the filename stem).
- File ends with `END-ISO-10303-21;` *unless* the entry's catalog claim
  explicitly involves missing/truncated end markers (Lh002 etc.); those
  are exempted by ID list.
- File schema declared via FILE_SCHEMA.

Run: cd validation && uv run python -m step_corpus._fixture_lint [--strict]
Exits 0 when all fixtures pass; 1 when any defect found (strict mode prints
per-fixture diagnoses).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[3] / "step-examples"

# IDs whose catalog claim is "missing close marker" or other framing defect.
EXEMPT_END_MARKER = {
    "Lh002",         # missing END marker
    "Le001",         # UTF-8 BOM: file framing intentionally malformed
    "Le015",         # unterminated string: file truncates intentionally
    "Le027",         # lower-case iso-10303-21 magic line: framing malformed
    "Le031",         # UTF-16 LE BOM: entire body is UTF-16
    "Ls029",         # unterminated /* */ comment runs through EOF — no close marker by design
    "Ls055",         # unterminated /* */ comment swallows the file tail incl. END marker — by design
    # §12.11 adversarial: many intentionally have framing issues
    "Ad001", "Ad002", "Ad003", "Ad004", "Ad005",
    "Ad014", "Ad015", "Ad026", "Ad027", "Ad030",
    "Ad090",         # lower-case end marker is the defect
}

# Entries whose .stp uses a different filename in FILE_NAME slot 1
# (e.g., .ifc extension for IFC schema mismatch test).
EXEMPT_FILENAME_MATCH = {
    "Lh019",  # IFC4 schema declared with .ifc filename
    "Wr020",  # label-loss defect: writer renamed product to 'BREP_001'
}

# Entries whose body is not latin-1 / ASCII (UTF-16 etc.); skip ID-in-text check.
EXEMPT_ID_IN_TEXT = {
    "Le031",  # UTF-16 LE encoded
}

# Entries whose .stp may legitimately have empty/different schema.
EXEMPT_SCHEMA = set()


def lint_fixture(path: Path) -> dict:
    """Return a dict with 'errors' (list of strings) and 'warnings' (list of strings)."""
    errors: list[str] = []
    warnings: list[str] = []

    fid = path.stem  # e.g. "Le001"

    try:
        text = path.read_text(encoding="latin-1", errors="replace")
    except Exception as e:
        return {"file": str(path), "errors": [f"read_failed: {e}"], "warnings": []}

    # 1. Header comment names the entry ID (within first 5KB), unless exempt
    head = text[:5000]
    if fid not in EXEMPT_ID_IN_TEXT and not re.search(rf"\b{re.escape(fid)}\b", head):
        errors.append(f"entry ID '{fid}' not found in first 5KB")

    # 2. Header has a /* */ Part-21 comment somewhere near the top
    if "/*" not in head:
        warnings.append("no `/* ... */` Part-21 comment block in first 5KB")

    # 3. FILE_NAME first arg matches filename stem (skip on framing-malformed fixtures)
    if (fid not in EXEMPT_END_MARKER
        and fid not in EXEMPT_FILENAME_MATCH
        and "ISO-10303-21" in head):
        m = re.search(r"FILE_NAME\s*\(\s*'([^']+)'", text)
        if m:
            declared = m.group(1)
            # Strip recognized extensions: accept .stp, .step, .ifc.
            declared_stem = re.sub(r"\.(stp|step|ifc|p21|stpx|stpz)$", "", declared, flags=re.I)
            if declared_stem != fid:
                errors.append(f"FILE_NAME first arg = '{declared}'; filename stem = '{fid}'")
        else:
            warnings.append("FILE_NAME entity not found in body")

    # 4. End marker present unless exempted
    if fid not in EXEMPT_END_MARKER and "END-ISO-10303-21;" not in text:
        errors.append("missing END-ISO-10303-21; close marker (and not on exempt list)")

    # 5. FILE_SCHEMA declared (skip on framing-malformed fixtures)
    if fid not in EXEMPT_END_MARKER and "ISO-10303-21" in head and "FILE_SCHEMA" not in text:
        warnings.append("FILE_SCHEMA entity not found")

    return {"file": str(path), "id": fid, "errors": errors, "warnings": warnings}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="Print per-fixture diagnoses, not just summary")
    ap.add_argument("--examples", default=str(EXAMPLES))
    args = ap.parse_args()

    examples = Path(args.examples)
    # Skip _quarantine/ — those fixtures are preserved as historical
    # evidence of broken regens; their lint state is by definition
    # outside the active-corpus invariants this lint enforces.
    fixtures = sorted(
        p for p in examples.rglob("*.stp")
        if "_quarantine" not in p.parts
    )

    error_count = 0
    warning_count = 0
    fixtures_with_errors = []
    fixtures_with_warnings = []

    for stp in fixtures:
        result = lint_fixture(stp)
        if result["errors"]:
            error_count += len(result["errors"])
            fixtures_with_errors.append(result)
        if result["warnings"]:
            warning_count += len(result["warnings"])
            fixtures_with_warnings.append(result)

    print(f"Linted {len(fixtures)} fixtures")
    print(f"  fixtures with errors:   {len(fixtures_with_errors)}  (total {error_count} errors)")
    print(f"  fixtures with warnings: {len(fixtures_with_warnings)}  (total {warning_count} warnings)")

    if args.strict or fixtures_with_errors:
        if fixtures_with_errors:
            print("\nFixtures with errors:")
            for r in fixtures_with_errors:
                print(f"  {r['id']}:")
                for e in r["errors"]:
                    print(f"    - {e}")
        if args.strict and fixtures_with_warnings:
            print("\nFixtures with warnings:")
            for r in fixtures_with_warnings[:30]:  # cap for output size
                print(f"  {r['id']}: {'; '.join(r['warnings'])}")
            if len(fixtures_with_warnings) > 30:
                print(f"  ... and {len(fixtures_with_warnings) - 30} more")

    return 1 if fixtures_with_errors else 0


if __name__ == "__main__":
    sys.exit(main())
