"""Byte-pattern assertions for catalog entries.

Where ``tier3_assertions`` checks geometric metrics of loaded shapes,
``byte_assertions`` check the *bytes* of the fixture file. Used for
encoding / framing / syntax / adversarial / writer-pathology defects
where the defect IS the bytes; no need to load the file.

Each assertion is one expression evaluated against a fixture's bytes.
The expression vocabulary:

- ``bytes_starts_with(b'\\xef\\xbb\\xbf')``: UTF-8 BOM at offset 0
- ``bytes_ends_with(b'END-ISO-10303-21;')``: close marker
- ``contains(b'\\X2\\03B\\X0\\')``: substring anywhere in the file
- ``not_contains(b'END-ISO-10303-21;')``: substring NOT present
- ``matches(rb'pattern')``: regex match anywhere
- ``count(b'#') >= 100``: substring occurrence count
- ``length > 32768``: file length comparison
- ``max_string_literal_length > 32768``: longest 'apostrophe-delimited' literal
- ``max_paren_depth > 50``: nested () depth in DATA section
- ``count_entity_def(b'CARTESIAN_POINT') == 4``: count of ``#N=TYPE(...)`` definitions
- ``declared_schema == b'AUTOMOTIVE_DESIGN'``: FILE_SCHEMA primary value

Usage::

    cd validation
    uv run python -m step_corpus._byte_assertions
    uv run python -m step_corpus._byte_assertions --json
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


_RE_STRING_LITERAL = re.compile(rb"'((?:[^']|'')*)'")
_RE_INSTANCE_DEF = re.compile(rb"(?:^|;)\s*#\d+\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
_RE_FILE_SCHEMA = re.compile(rb"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'")


def _max_string_literal_length(body: bytes) -> int:
    longest = 0
    for m in _RE_STRING_LITERAL.finditer(body):
        # Resolve doubled-apostrophe escapes for accurate length
        content = m.group(1).replace(b"''", b"'")
        if len(content) > longest:
            longest = len(content)
    return longest


def _max_paren_depth(body: bytes) -> int:
    """Compute max paren nesting in DATA section, ignoring string contents."""
    start = body.find(b"DATA;")
    end = body.find(b"ENDSEC;", start)
    if start < 0 or end < 0:
        start = 0
        end = len(body)
    depth = 0
    max_depth = 0
    in_str = False
    i = start
    while i < end:
        c = body[i]
        if c == ord("'"):
            if in_str and i + 1 < end and body[i + 1] == ord("'"):
                i += 2
                continue
            in_str = not in_str
            i += 1
            continue
        if not in_str:
            if c == ord("("):
                depth += 1
                if depth > max_depth:
                    max_depth = depth
            elif c == ord(")"):
                depth -= 1
        i += 1
    return max_depth


def _count_entity_def(body: bytes, type_name: bytes) -> int:
    n = 0
    target = type_name.upper()
    for m in _RE_INSTANCE_DEF.finditer(body):
        if m.group(1).upper() == target:
            n += 1
    return n


def _declared_schema(body: bytes) -> bytes:
    m = _RE_FILE_SCHEMA.search(body)
    return m.group(1) if m else b""


def _eval_assertion(body: bytes, expr: str) -> tuple[bool, str]:
    """Evaluate one assertion against a fixture body.

    Returns (passed, detail_string).
    """
    # Build a sandboxed eval environment.
    ns: dict[str, Any] = {
        "body": body,
        "length": len(body),
        "max_string_literal_length": _max_string_literal_length(body),
        "max_paren_depth": _max_paren_depth(body),
        "declared_schema": _declared_schema(body),
        # Lambdas
        "bytes_starts_with": lambda prefix: body.startswith(prefix),
        "bytes_ends_with": lambda suffix: body.rstrip().endswith(suffix),
        "contains": lambda sub: sub in body,
        "not_contains": lambda sub: sub not in body,
        "matches": lambda pat: bool(re.search(pat, body)),
        "count": lambda sub: body.count(sub),
        "count_entity_def": lambda tn: _count_entity_def(body, tn),
    }
    try:
        result = eval(expr, {"__builtins__": {}, "re": re}, ns)
        return (bool(result), repr(result))
    except Exception as e:
        return (False, f"eval-error: {type(e).__name__}: {e}")


def check_entry(entry: dict) -> list[dict[str, Any]]:
    asserts = entry.get("byte_assertions") or []
    if not asserts:
        return []
    fixture = RESEARCH_ROOT / entry["fixture_path"]
    if not fixture.is_file():
        return [{"id": entry["id"], "assertion": a, "status": "no-fixture"} for a in asserts]
    body = fixture.read_bytes()
    out = []
    for a in asserts:
        ok, detail = _eval_assertion(body, a)
        out.append({
            "id": entry["id"],
            "assertion": a,
            "status": "pass" if ok else "fail",
            "detail": detail,
        })
    return out


def check_all() -> list[dict[str, Any]]:
    out = []
    for entry in catalog.iter_canonical():
        out.extend(check_entry(entry))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._byte_assertions")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    results = check_all()
    if args.json:
        json.dump(results, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    from collections import Counter
    by_status = Counter(r["status"] for r in results)
    print(f"Byte assertions: {len(results)} total")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<22} {v:>4}")

    fails = [r for r in results if r["status"] != "pass"]
    if fails:
        print(f"\nFirst 20 non-pass:")
        for r in fails[:20]:
            print(f"  {r['id']:<8} [{r['status']:<14}] {r['assertion']}  detail={r['detail']}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
