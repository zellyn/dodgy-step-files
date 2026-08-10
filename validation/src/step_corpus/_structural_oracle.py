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

v3 check (added 2026-08-09, adopted from the crash-refusability campaign):
  SLOT_TYPE          — an entity reference sits in a slot whose schema-declared
                       type it is not (e.g. ``LINE.dir`` holding a DIRECTION
                       where a VECTOR is declared, or SURFACE_OF_REVOLUTION's
                       axis holding an AXIS2_PLACEMENT_3D where AXIS1_PLACEMENT
                       is declared). This is the single strongest crash
                       discriminator the corpus has found: wrong-type slots
                       predict OCCT ``signal(11)`` at 96% vs a 3% base rate,
                       because the converters downcast without checking.
                       Validated at zero false positives on 17 clean controls,
                       28 real NIST CAD exports, and an individual read of every
                       corpus hit (2026-08-08). Same scoping as the units-fix
                       era: also scoped in ``make_roadmap.py::crash_refusable``,
                       which imports the table from here — ONE table, two
                       checkers.

v3 also rescopes UNITS_INCONSISTENT (2026-08-09): only units ASSIGNED by a
GLOBAL_UNIT_ASSIGNED_CONTEXT count toward "ambiguous model scale". A length
unit that exists merely as a conversion basis or a self-denominated measure
(PMI tolerance, derived unit) denominates its own value and creates no
ambiguity — counting those flagged 20 of 28 real inch-authored NIST exports.

``lint_text`` / ``lint_file`` return a single most-salient code string, or the
literal ``"ok"`` when no defect is found. Used both as a validate2 oracle
(``summary["structural"]``) and directly by tests (fast, no subprocess).
"""
from __future__ import annotations

import math
import re

# Priority order: structural-graph errors first, then typing errors, then
# semantic defects. SLOT_TYPE sits after DANGLING_REF (an unresolvable ref is
# reported as dangling, never as a type violation) and before the semantic
# checks.
CODES = ("DUPLICATE_ID", "DANGLING_REF", "SLOT_TYPE",
         "UNITS_INCONSISTENT", "AXIS_DEGENERATE")

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


# ---- SLOT_TYPE (v3) — schema-declared types for reference-valued slots -------
# Hand-entered from ISO 10303-42 and checked against the corpus: every "violation"
# reported in a NON-crashing file was read individually, and six legitimate subtypes
# (BEZIER_SURFACE, DEGENERATE_TOROIDAL_SURFACE, BLENDED_EDGE_SURFACE,
# COMPOSITE_CURVE_ON_SURFACE, COMPLEX_TRIANGULATED_FACE, TRIANGULATED_FACE) were missing
# from a first draft. Each expectation is a SET because these attributes are declared
# with SUPERTYPES — EDGE_CURVE.edge_geometry is a CURVE, so LINE/CIRCLE/B_SPLINE all fit.
# This is the CANONICAL copy; occt-coverage/make_roadmap.py imports it.
_SURFACE = {"PLANE", "CYLINDRICAL_SURFACE", "CONICAL_SURFACE", "SPHERICAL_SURFACE",
            "TOROIDAL_SURFACE", "B_SPLINE_SURFACE_WITH_KNOTS", "B_SPLINE_SURFACE",
            "RATIONAL_B_SPLINE_SURFACE", "SURFACE_OF_REVOLUTION", "OFFSET_SURFACE",
            "SURFACE_OF_LINEAR_EXTRUSION", "RECTANGULAR_TRIMMED_SURFACE",
            "CURVE_BOUNDED_SURFACE", "RECTANGULAR_COMPOSITE_SURFACE", "SURFACE_REPLICA",
            "BEZIER_SURFACE", "DEGENERATE_TOROIDAL_SURFACE", "BLENDED_EDGE_SURFACE",
            "UNIFORM_SURFACE", "QUASI_UNIFORM_SURFACE", "SWEPT_SURFACE"}
_CURVE = {"LINE", "CIRCLE", "ELLIPSE", "HYPERBOLA", "PARABOLA", "POLYLINE",
          "B_SPLINE_CURVE_WITH_KNOTS", "B_SPLINE_CURVE", "RATIONAL_B_SPLINE_CURVE",
          "TRIMMED_CURVE", "COMPOSITE_CURVE", "SURFACE_CURVE", "SEAM_CURVE",
          "INTERSECTION_CURVE", "OFFSET_CURVE_3D", "PCURVE", "CURVE_REPLICA",
          "BOUNDED_CURVE", "CONIC", "DEGENERATE_PCURVE", "COMPOSITE_CURVE_ON_SURFACE",
          "BEZIER_CURVE", "UNIFORM_CURVE", "QUASI_UNIFORM_CURVE", "CURVE_ON_SURFACE"}
_POINT = {"CARTESIAN_POINT", "POINT_ON_CURVE", "POINT_ON_SURFACE", "POINT_REPLICA",
          "DEGENERATE_PCURVE"}
_LOOP = {"EDGE_LOOP", "POLY_LOOP", "VERTEX_LOOP"}
_FBOUND = {"FACE_BOUND", "FACE_OUTER_BOUND"}
_SHELL = {"CLOSED_SHELL", "OPEN_SHELL", "ORIENTED_CLOSED_SHELL"}
_FACE = {"ADVANCED_FACE", "FACE_SURFACE", "ORIENTED_FACE", "SUBFACE",
         "TRIANGULATED_FACE", "COMPLEX_TRIANGULATED_FACE", "CURVE_BOUNDED_SURFACE"}

# entity -> {argument index: (legal types, arg_is_a_list)}
SLOT_TYPES = {
    "LINE":                      {1: (_POINT, False), 2: ({"VECTOR"}, False)},
    "VECTOR":                    {1: ({"DIRECTION"}, False)},
    "VERTEX_POINT":              {1: (_POINT, False)},
    "EDGE_CURVE":                {1: ({"VERTEX_POINT"}, False), 2: ({"VERTEX_POINT"}, False),
                                  3: (_CURVE, False)},
    "ORIENTED_EDGE":             {3: ({"EDGE_CURVE"}, False)},
    "EDGE_LOOP":                 {1: ({"ORIENTED_EDGE"}, True)},
    "FACE_BOUND":                {1: (_LOOP, False)},
    "FACE_OUTER_BOUND":          {1: (_LOOP, False)},
    "ADVANCED_FACE":             {1: (_FBOUND, True), 2: (_SURFACE, False)},
    "FACE_SURFACE":              {1: (_FBOUND, True), 2: (_SURFACE, False)},
    "CLOSED_SHELL":              {1: (_FACE, True)},
    "OPEN_SHELL":                {1: (_FACE, True)},
    "MANIFOLD_SOLID_BREP":       {1: (_SHELL, False)},
    "SHELL_BASED_SURFACE_MODEL": {1: (_SHELL, True)},
    # axis_position is declared AXIS1_PLACEMENT; files supplying an
    # AXIS2_PLACEMENT_3D crash the revolution converter (the long-open
    # Twi144 mystery — a repair that fixes every other wrong-type slot
    # still crashes on this one).
    "SURFACE_OF_REVOLUTION":     {2: ({"AXIS1_PLACEMENT"}, False)},
}


def _split_top(args: str) -> list[str]:
    """Split an argument string on top-level commas (paren- and string-aware)."""
    out, depth, cur, i, n = [], 0, [], 0, len(args)
    while i < n:
        c = args[i]
        if c == "'":                      # Part-21 string; '' is an escaped quote
            j = i + 1
            while j < n:
                if args[j] == "'":
                    if j + 1 < n and args[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            cur.append(args[i:j + 1])
            i = j + 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "," and depth == 0:
            out.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append("".join(cur))
    return out


def slot_type_violations(ents: dict[int, tuple[str, str]]) -> list[int]:
    """Entity ids with a reference slot holding an entity of the wrong type.

    FAIL-SAFE by construction: a reference that does not resolve to a simple
    typed entity — undefined ``#N`` (that is DANGLING_REF's job), a complex
    instance like ``#7=(A()B())`` which carries no single type name, or an
    entity the tokenizer missed — is UNKNOWN and is NEVER counted. A missed
    definition can therefore only under-report.
    """
    kind = {eid: typ for eid, (typ, _args) in ents.items() if typ}
    bad: set[int] = set()
    for eid, (typ, args) in ents.items():
        rules = SLOT_TYPES.get(typ)
        if not rules:
            continue
        parts = _split_top(args)
        for idx, (ok, is_list) in rules.items():
            if idx >= len(parts):
                continue
            a = parts[idx].strip()
            refs = (_ID_REF.findall(a) if is_list
                    else ([a[1:]] if a.startswith("#") and a[1:].isdigit() else []))
            if any(kind.get(int(r)) not in ok
                   for r in refs if kind.get(int(r)) is not None):
                bad.add(eid)
                break
    return sorted(bad)


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


_STMT_BODY = re.compile(r"#(\d+)\s*=\s*([^;]*);", re.S)
# The unit list of a GLOBAL_UNIT_ASSIGNED_CONTEXT (simple or inside a complex
# instance): the first argument is an aggregate of unit-entity references.
_GUAC_LIST = re.compile(r"GLOBAL_UNIT_ASSIGNED_CONTEXT\s*\(\s*\(([^)]*)\)", re.S)


def _length_units(data: str) -> set:
    """Distinct LENGTH units ASSIGNED by a GLOBAL_UNIT_ASSIGNED_CONTEXT.

    Only context-assigned units define the model's scale — that is what
    "ambiguous model scale" means. Two populations of length units are
    deliberately NOT counted (2026-08-09, measured on 28 real NIST CAD
    exports where counting them flagged 20 inch-authored files):

      - a conversion-based unit's defining measure (ISO 10303-41 REQUIRES an
        SI basis inside every inch unit — it is the definition of the inch,
        not a second model unit);
      - self-denominated measures (PMI tolerances, derived units): a
        LENGTH_MEASURE_WITH_UNIT that names its own unit is unambiguous by
        construction.

    Only METRE-based SI units and named length CONVERSION_BASED_UNITs count;
    angle / solid-angle units are irrelevant to model scale and are ignored.
    FAIL-SAFE: a context ref that does not resolve, or a unit form the
    regexes do not recognize, is simply not counted — under-report, never a
    false positive. A conversion-based unit that inlines its SI basis in the
    same entity counts once as the conversion (checked first).
    """
    data = _strip_comments(data)
    ents = {int(m.group(1)): m.group(2) for m in _STMT_BODY.finditer(data)}
    units: set = set()
    for m in _GUAC_LIST.finditer(data):
        for r in _ID_REF.findall(m.group(1)):
            body = ents.get(int(r), "")
            cm = _CONV_LENGTH.search(body)
            if cm:
                units.add(("CONV", cm.group(1).upper()))
                continue
            sm = _SI_LENGTH.search(body)
            if sm:
                prefix = (sm.group(1) or "$").strip(".")
                units.add(("SI", prefix or "$"))
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
    if slot_type_violations(ents):
        return "SLOT_TYPE"
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
        "SLOT_TYPE": slot_type_violations(ents),
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
