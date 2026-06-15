"""Stage 1 of the adversarial-fixture-review pipeline: format validity.

Scans a fixture's BYTES for Part-21 grammar violations and structural
defects that the v1.0–v1.2 review cycle showed can shadow a fixture's
intended catalog claim (the parser dies on the upstream defect before
ever reaching the claimed defect site).

The checks here are NECESSARY-but-not-sufficient for a healthy fixture.
They catch the v1.0-class problems; they do NOT verify that the bytes
actually demonstrate the catalog claim. That's Stage 2 (claim audit),
implemented separately.

Usage (script):
    uv run python -m step_corpus._format_check <fixture.stp> [...]
    uv run python -m step_corpus._format_check --all          # the whole corpus

Exit code is the count of fixtures with errors (0 = all clean).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from step_corpus import catalog


CHECK_NAMES = [
    "nested-comment-corruption",
    "pipe-delimited-complex-entity",
    "unparenthesised-complex-entity",
    "arithmetic-real-literal",
    "trailing-comma-in-aggregate",
    "edge-curve-same-orientation-pair",
]


@dataclass
class Finding:
    fixture_id: str
    check: str
    severity: str  # "error" | "warning"
    detail: str
    line: int | None = None


# ---- Individual checks ---------------------------------------------------

ENTITY_PROBE = re.compile(
    r"\s*(?:ISO-10303-21|HEADER|DATA|ENDSEC|END-ISO-10303-21|#\d+\s*=)",
)


def _scan_comments_and_strings(raw: str):
    """Yield (kind, start, end) where kind in {comment, string}. Simple
    state machine; ignores nesting (Part-21 forbids it)."""
    n = len(raw)
    state = "NORMAL"
    i = 0
    open_at = 0
    while i < n - 1:
        c, d = raw[i], raw[i+1]
        if state == "NORMAL":
            if c == "/" and d == "*":
                state = "COMMENT"
                open_at = i
                i += 2
                continue
            if c == "'":
                state = "STRING"
                open_at = i
                i += 1
                continue
        elif state == "STRING":
            if c == "'":
                if d == "'":  # escaped quote
                    i += 2
                    continue
                yield ("string", open_at, i + 1)
                state = "NORMAL"
                i += 1
                continue
        elif state == "COMMENT":
            if c == "*" and d == "/":
                yield ("comment", open_at, i + 2)
                state = "NORMAL"
                i += 2
                continue
        i += 1


def check_nested_comments(fixture_id: str, raw: str) -> list[Finding]:
    """Detect author-intended nested /* */ blocks where the inner */
    closes the outer comment prematurely. Pattern: a *not-real-closer*
    `*/` is followed (after whitespace) by more comment-style text
    (a `*` continuation, or alphabetic prose), not by STEP entity code."""
    findings: list[Finding] = []
    n = len(raw)
    state = "NORMAL"
    i = 0
    while i < n - 1:
        c, d = raw[i], raw[i+1]
        if state == "NORMAL":
            if c == "'":
                state = "STRING"; i += 1; continue
            if c == "/" and d == "*":
                state = "COMMENT"; i += 2; continue
            i += 1; continue
        if state == "STRING":
            if c == "'":
                if d == "'":
                    i += 2; continue
                state = "NORMAL"; i += 1; continue
            i += 1; continue
        # COMMENT
        if c == "*" and d == "/":
            after = raw[i+2:i+2+400]
            s = after.lstrip()
            looks_like_step = bool(ENTITY_PROBE.match(s)) or s.startswith("/*") or not s
            if not looks_like_step:
                line = raw[:i].count("\n") + 1
                findings.append(Finding(
                    fixture_id, "nested-comment-corruption", "error",
                    f"`*/` at byte {i} closes a /* comment prematurely "
                    f"(followed by prose: {after[:60]!r})", line,
                ))
                # Still consume — move past this faux closer to detect the next one.
            else:
                state = "NORMAL"
            i += 2
            continue
        i += 1
    return findings


_PIPE_PAT = re.compile(
    r"^#\d+\s*=\s*[A-Z_]+\([^)]*\)\|[A-Z_]+\([^)]*\)\|[A-Z_]+\([^)]*\)\s*;",
    re.MULTILINE,
)


def check_pipe_delimited_complex(fixture_id: str, raw: str) -> list[Finding]:
    """`A()|B()|C()` form is not in Part-21; the correct form is `(A()B()C())`."""
    findings = []
    for m in _PIPE_PAT.finditer(raw):
        line = raw[:m.start()].count("\n") + 1
        findings.append(Finding(
            fixture_id, "pipe-delimited-complex-entity", "error",
            f"`|`-delimited complex entity at byte {m.start()}: {m.group()[:120]}",
            line,
        ))
    return findings


_ARITH_PAT = re.compile(r"\([^)]*\d+(?:\.\d+(?:[eE][+\-]?\d+)?)?\s*[+\-]\s*\d+(?:\.\d+(?:[eE][+\-]?\d+)?)?")


def check_arithmetic_real_literal(fixture_id: str, raw: str) -> list[Finding]:
    """Part-21 REAL literals don't allow `+`/`-` infix. `(1.0+1e-7,0,0)` is
    illegal. Pattern-match: a literal-number followed by `+` or `-` followed
    by another literal-number inside an attribute list.

    Heuristic: skip matches inside string literals (Part-21 strings are
    opaque)."""
    findings = []
    # Mask out strings + comments before matching
    masked = list(raw)
    for kind, s, e in _scan_comments_and_strings(raw):
        for i in range(s, e):
            masked[i] = " "
    masked_str = "".join(masked)
    for m in _ARITH_PAT.finditer(masked_str):
        # filter out clearly-numerical aggregates like (1e+3,1e-3,0) by requiring
        # the SECOND number to start with a digit and not be in scientific notation
        # already consumed by the first.
        token = m.group()
        # If the arithmetic candidate looks like `1.0+1e-7` (no comma between),
        # it's an arithmetic literal (illegal). If it's `(1.0,1e-7,...)` we
        # wouldn't have matched (we required no `)` or `,` between).
        line = raw[:m.start()].count("\n") + 1
        findings.append(Finding(
            fixture_id, "arithmetic-real-literal", "error",
            f"arithmetic-expression REAL literal at byte {m.start()}: {token[:80]}",
            line,
        ))
    return findings


_TRAILING_COMMA_PAT = re.compile(r",\s*\)")


def check_trailing_comma(fixture_id: str, raw: str) -> list[Finding]:
    """`(a,b,)` is not legal Part-21 aggregate syntax. Skip matches inside
    strings."""
    findings = []
    masked = list(raw)
    for kind, s, e in _scan_comments_and_strings(raw):
        for i in range(s, e):
            masked[i] = " "
    masked_str = "".join(masked)
    for m in _TRAILING_COMMA_PAT.finditer(masked_str):
        line = raw[:m.start()].count("\n") + 1
        # Get a small snippet for context
        snippet_start = max(0, m.start() - 40)
        snippet = raw[snippet_start:m.end()].replace("\n", " ")[-80:]
        findings.append(Finding(
            fixture_id, "trailing-comma-in-aggregate", "error",
            f"trailing comma at byte {m.start()}: ...{snippet}", line,
        ))
    return findings


_OE_PAT = re.compile(r"=ORIENTED_EDGE\('[^']*'\s*,\s*\*\s*,\s*\*\s*,\s*#(\d+)\s*,\s*\.([TF])\.")


def check_edge_curve_same_orientation(fixture_id: str, raw: str) -> list[Finding]:
    """For a 2-manifold shell, every EDGE_CURVE should be used exactly once
    with .T. and once with .F.. If a shared edge is used same-sense by two
    faces the build will reject."""
    findings = []
    uses: dict[int, list[str]] = {}
    for m in _OE_PAT.finditer(raw):
        uses.setdefault(int(m.group(1)), []).append(m.group(2))
    for edge_id, senses in uses.items():
        if len(senses) == 2 and senses[0] == senses[1]:
            findings.append(Finding(
                fixture_id, "edge-curve-same-orientation-pair", "warning",
                f"EDGE_CURVE #{edge_id} used twice with same sense .{senses[0]}.; "
                f"2-manifold shells require one .T. + one .F.", None,
            ))
    return findings


ALL_CHECKS = [
    check_nested_comments,
    check_pipe_delimited_complex,
    check_arithmetic_real_literal,
    check_trailing_comma,
    check_edge_curve_same_orientation,
]


def run_all(fixture_id: str, path: Path) -> list[Finding]:
    raw = path.read_text(errors="replace")
    findings: list[Finding] = []
    for fn in ALL_CHECKS:
        findings.extend(fn(fixture_id, raw))
    return findings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._format_check")
    p.add_argument("paths", nargs="*", help="fixture path(s); ignored if --all")
    p.add_argument("--all", action="store_true",
                   help="run against every fixture in the catalog")
    p.add_argument("--errors-only", action="store_true",
                   help="suppress warnings")
    args = p.parse_args(argv)

    if args.all:
        targets = []
        for e in catalog.iter_canonical():
            targets.append((e["id"], Path(e["fixture_path"])))
    else:
        targets = []
        for arg in args.paths:
            path = Path(arg)
            fixture_id = path.stem
            targets.append((fixture_id, path))

    total_findings = 0
    fixtures_with_errors = 0
    for fixture_id, path in targets:
        if not path.exists():
            print(f"{fixture_id}: file not found at {path}", file=sys.stderr)
            continue
        findings = run_all(fixture_id, path)
        if args.errors_only:
            findings = [f for f in findings if f.severity == "error"]
        if findings:
            errors_here = sum(1 for f in findings if f.severity == "error")
            if errors_here:
                fixtures_with_errors += 1
            total_findings += len(findings)
            for f in findings:
                line_str = f" line {f.line}" if f.line else ""
                print(f"{fixture_id} [{f.severity}] [{f.check}]{line_str}: {f.detail}")
    if not args.errors_only and args.all:
        print(f"\n{fixtures_with_errors} fixtures with errors, {total_findings} total findings")
    return fixtures_with_errors


if __name__ == "__main__":
    raise SystemExit(main())
