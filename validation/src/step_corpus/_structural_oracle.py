"""Structural-linter oracle — a NON-kernel STEP validator.

Motivation (wave-12 inflection, 2026-07-06): the corpus's kernel oracles
(occt/gmsh shape-counts) are *blind* to a whole class of real defects, because
OCCT silently normalizes or ignores them at BRep-load time — so the defective
file produces the same shape-count signature as a clean solid. This oracle adds
a new discriminating dimension: it asserts on the STEP *structure itself* (spec
conformance / model integrity), independent of any geometry kernel.

Design constraints:
  - Pure Part-21 entity parsing, no OCCT/gmsh (fast, deterministic, no segfaults).
  - LOW false-positive rate on CLEAN files is critical: a linter that flags valid
    input is worse than useless. Every check below flags only genuine defects,
    NOT spec-legal-but-unusual constructs. Notably we do NOT flag non-unit or
    non-perpendicular AXIS2_PLACEMENT_3D ref_directions — ISO 10303 explicitly
    allows those (the kernel derives the x-axis by projection), so flagging them
    would false-positive on the majority of real files.

v1 checks (genuine, oracle-invisible, low-FP), returned in priority order:
  DUPLICATE_ID       — the same ``#N =`` defined more than once (ambiguous graph).
  UNITS_INCONSISTENT — >1 DISTINCT length unit reachable (ambiguous model scale).
  AXIS_DEGENERATE    — an AXIS2_PLACEMENT_3D whose axis and ref_direction are
                       parallel/anti-parallel, or a zero-magnitude DIRECTION
                       (the x-axis projection is undefined; kernel silently
                       defaults or drops it).

These three checks FAIL SAFE: a missed entity definition (from the deliberately
simple ``;``-split tokenizer) makes them *under*-report, never false-positive.

v2 check (added 2026-07-17):
  DANGLING_REF      — a ``#N`` referenced in DATA but never defined (``#N =``
                       absent). v1 deferred this because a ``;``-split tokenizer
                       under-counts definitions and thus *false-positives*. The
                       fix inverts the approach: collect definitions with a
                       PERMISSIVE ``#N =`` scan (never tokenized), so a missed
                       def can only OVER-count (under-report, fail-safe) — never
                       invent a false positive. References are scanned with string
                       literals stripped. Verified zero FP across the full corpus.

``lint_text`` / ``lint_file`` return a single most-salient code string, or the
literal ``"ok"`` when no defect is found. Used both as a validate2 oracle
(``summary["structural"]``) and directly by tests (fast, no subprocess).
"""
from __future__ import annotations

import math
import re

# Priority order: structural-graph errors first, then semantic defects.
CODES = ("DUPLICATE_ID", "DANGLING_REF", "UNITS_INCONSISTENT", "AXIS_DEGENERATE")

_PERP_TOL = 1e-6       # |cos(axis, ref)| >= 1 - tol  =>  parallel  => degenerate
_ZERO_TOL = 1e-12      # a direction whose magnitude^2 is below this is zero

# One Part-21 statement:  #N = TYPE( args )   (TYPE may be empty for complex
# instances like `#1=(A()B()C());` — those carry no simple type but still have
# an id, so we capture the id and leave type possibly empty).
_STMT = re.compile(r"\s*#(\d+)\s*=\s*([A-Z_0-9]*)\s*\((.*)\)\s*$", re.S)
_ID_DEF = re.compile(r"#(\d+)\s*=")
_ID_REF = re.compile(r"#(\d+)")
_FLOAT = re.compile(r"(?<![#\d.])(-?\d+\.\d*(?:[eE][-+]?\d+)?)")
_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_STR_LIT = re.compile(r"'(?:''|[^'])*'", re.S)   # Part-21 string ('' = escaped quote)


def _strip_comments(data: str) -> str:
    """Strip Part-21 ``/* ... */`` comments.

    The ``;``-split statement tokenizer (``_STMT``) anchors on a leading
    ``#N =`` — a comment placed before a definition in the same ``;``-chunk
    (e.g. ``#9063=/* stale */; #9064=FOO(...);`` written as one statement,
    or a trailing ``/* ... */`` glued onto the previous statement) makes
    that chunk fail the regex and the entity becomes invisible to
    ``DUPLICATE_ID`` / ``AXIS_DEGENERATE``. Stripping comments first keeps
    the FAIL SAFE under-report property (never introduces a false positive)
    while fixing this under-report class.
    """
    return _COMMENT.sub("", data)


def _data_section(text: str) -> str:
    """Return only the DATA section body (between ``DATA;`` and its ``ENDSEC;``).

    Falls back to the whole text if the framing tokens aren't found, so partial
    or malformed files still get linted.
    """
    up = text.upper()
    i = up.find("DATA;")
    if i == -1:
        return text
    j = up.find("ENDSEC;", i)
    return text[i + len("DATA;"): j if j != -1 else len(text)]


def parse_entities(data: str) -> dict[int, tuple[str, str]]:
    """Map id -> (type, raw-args) for each ``#N = TYPE(args);`` in DATA.

    On a duplicate id the LAST definition wins here; duplicate detection uses the
    raw definition count (``duplicate_ids``) rather than this map.
    """
    data = _strip_comments(data)
    out: dict[int, tuple[str, str]] = {}
    for stmt in data.split(";"):
        m = _STMT.match(stmt)
        if m:
            out[int(m.group(1))] = (m.group(2), m.group(3))
    return out


def duplicate_ids(data: str) -> list[int]:
    data = _strip_comments(data)
    counts: dict[int, int] = {}
    for stmt in data.split(";"):
        m = _STMT.match(stmt)
        if m:
            i = int(m.group(1))
            counts[i] = counts.get(i, 0) + 1
    return sorted(i for i, c in counts.items() if c > 1)


def dangling_refs(text: str) -> list[int]:
    """IDs referenced but never defined (``#N =`` absent). Takes the FULL text.

    v2, FAIL-SAFE by design (2026-07-17): definitions are collected with a
    *permissive* ``#N =`` scan over the whole comment-stripped file — NOT
    statement-tokenized, and NOT restricted to the first DATA section (a
    multi-DATA-section file like Lh033 defines ids across several ``DATA;``
    blocks). This inverts v1's fatal asymmetry: because a missed definition here
    would OVER-report danglings (a false positive), we must never under-count
    definitions. Over-counting is fine (it under-reports, fail-safe), so a
    malformed string literal, a SCOPE/ENDSCOPE block, ``@``-prefix, nested parens,
    or a second DATA section can only cause a stray ``#N =`` to be counted — never
    a false positive. References are scanned with string literals stripped, so
    ``#N`` inside a quoted string is not miscounted. The Part-21 HEADER carries no
    ``#N`` tokens, so scanning the whole file is safe. Verified zero false
    positives across the full corpus.
    """
    body = _STR_LIT.sub("", _strip_comments(text))
    defined = {int(x) for x in _ID_DEF.findall(_strip_comments(text))}
    referenced = {int(x) for x in _ID_REF.findall(body)}
    return sorted(referenced - defined)


def _floats(args: str) -> list[float]:
    return [float(x) for x in _FLOAT.findall(args)]


# A length SI_UNIT, in either simple form  SI_UNIT(.MILLI.,.METRE.)  or inside a
# complex instance  (LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.)).  The
# prefix group is optional ('$' or empty = base metre). Angle/solid-angle SI
# units end in .RADIAN./.STERADIAN. and never match (we require `.METRE.`).
_SI_LENGTH = re.compile(r"SI_UNIT\s*\(\s*(\$|\.[A-Z]+\.)?\s*,\s*\.METRE\.\s*\)")
# A length CONVERSION_BASED_UNIT names its unit in a leading string literal.
_CONV_LENGTH = re.compile(
    r"CONVERSION_BASED_UNIT\s*\(\s*'([^']*(?:INCH|FOOT|MIL|METRE|MM|YARD)[^']*)'",
    re.IGNORECASE,
)


def _length_units(data: str) -> set:
    """Distinct LENGTH units declared in the model (simple or complex form).

    Only METRE-based SI units and named length CONVERSION_BASED_UNITs count;
    angle / solid-angle units are irrelevant to model scale and are ignored.
    """
    data = _strip_comments(data)
    units: set = set()
    for m in _SI_LENGTH.finditer(data):
        prefix = (m.group(1) or "$").strip(".")
        units.add(("SI", prefix or "$"))
    for m in _CONV_LENGTH.finditer(data):
        units.add(("CONV", m.group(1).upper()))
    return units


def degenerate_axes(ents: dict[int, tuple[str, str]]) -> list[int]:
    """AXIS2_PLACEMENT_3D whose axis and ref_direction are parallel, or which
    reference a zero-magnitude DIRECTION. Both make the x-axis undefined."""
    bad: list[int] = []
    for eid, (typ, args) in ents.items():
        if typ != "AXIS2_PLACEMENT_3D":
            continue
        dir_ids = [i for i in (int(x) for x in _ID_REF.findall(args))
                   if ents.get(i, ("", ""))[0] == "DIRECTION"]
        if len(dir_ids) < 2:
            continue  # only a location, or axis-only placement: nothing to check
        axis = _floats(ents[dir_ids[0]][1])
        refd = _floats(ents[dir_ids[1]][1])
        if len(axis) < 3 or len(refd) < 3:
            continue
        na2 = sum(c * c for c in axis)
        nr2 = sum(c * c for c in refd)
        if na2 < _ZERO_TOL or nr2 < _ZERO_TOL:
            bad.append(eid)          # zero-magnitude direction
            continue
        cos = sum(a * b for a, b in zip(axis, refd)) / math.sqrt(na2 * nr2)
        if abs(cos) >= 1.0 - _PERP_TOL:
            bad.append(eid)          # axis parallel/anti-parallel to ref_direction
    return sorted(bad)


def lint_text(text: str) -> str:
    """Return the most-salient structural defect code, or ``"ok"`` if clean."""
    data = _data_section(text)
    ents = parse_entities(data)
    if duplicate_ids(data):
        return "DUPLICATE_ID"
    if dangling_refs(data):
        return "DANGLING_REF"
    if len(_length_units(data)) > 1:
        return "UNITS_INCONSISTENT"
    if degenerate_axes(ents):
        return "AXIS_DEGENERATE"
    return "ok"


def lint_detail(text: str) -> dict:
    """Full findings (all checks) — for debugging / reporting, not the oracle spec."""
    data = _data_section(text)
    ents = parse_entities(data)
    return {
        "DUPLICATE_ID": duplicate_ids(data),
        "DANGLING_REF": dangling_refs(data),
        "UNITS_INCONSISTENT": sorted(str(u) for u in _length_units(data)) if len(_length_units(data)) > 1 else [],
        "AXIS_DEGENERATE": degenerate_axes(ents),
    }


def lint_file(path) -> str:
    from pathlib import Path
    return lint_text(Path(path).read_text(encoding="latin-1", errors="replace"))


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(f"{p}: {lint_file(p)}")
