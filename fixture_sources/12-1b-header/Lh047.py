"""Lh047 — Lower-case section keywords (`data;` instead of `DATA;`).

Catalog claim: ISO 10303-21 spells the framing keywords ISO-10303-21, HEADER,
DATA, ENDSEC, and END-ISO-10303-21 exclusively in upper case. A producer that
emits any of these in lower or mixed case (header;, data;, endsec;) violates
the framing grammar. Strict parsers reject at the first mis-cased keyword;
lenient parsers fold case and proceed.
Bug-reporter language: "STEP keywords lower-case", "data; not DATA;",
"lower-case ISO-10303-21".

Reproducer recipe:
  A Part-21 file with header;, data;, endsec; instead of HEADER;, DATA;,
  ENDSEC;.

Byte assertions:
  contains(b'header;') or contains(b'data;') or contains(b'endsec;')
  contains(b'data;')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=reject
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh047",
    defect=(
        "Lower-case section keywords (data; instead of DATA;) in Part-21 file; "
        "input: framing keywords header;, data;, endsec; appear in lower case "
        "instead of the ISO-mandated upper-case HEADER;, DATA;, ENDSEC;; "
        "ISO 10303-21 §6.2: keywords ISO-10303-21, HEADER, DATA, ENDSEC, and "
        "END-ISO-10303-21 are spelled exclusively in upper case; "
        "a producer built from a generic EXPRESS-instance serialiser that lower-cases "
        "all identifiers, or a hand-rolled writer that confuses EXPRESS reserved-word "
        "case-insensitivity with Part-21 framing keyword case, emits mis-cased keywords; "
        "strict parsers reject at the first mis-cased keyword; "
        "lenient parsers fold case and proceed, hiding the producer defect; "
        "expected kernel behavior: reject; framing keywords are case-sensitive in the spec; "
        "a tolerant case-fold may be offered as an opt-in compatibility mode; "
        "distinct from Le027 (8-bit / case-insensitive lexer) which is lexer-side entity-type "
        "keyword tolerance; Lh047 is framing keywords specifically; "
        "synonyms: lowercase data; instead of DATA;, lowercase STEP framing keywords, "
        "header; in STEP file, endsec; lowercase, STEP framing keyword case wrong"
    ),
)


def _render_lh047() -> str:
    """Render a Part-21 with lower-case framing keywords header;, data;, endsec;."""
    return (
        "ISO-10303-21;\n"
        "/* Lh047: lower-case framing keywords — header; data; endsec; instead of upper-case */\n"
        "/* ISO 10303-21 §6.2: framing keywords ISO-10303-21, HEADER, DATA, ENDSEC are upper-case */\n"
        "/* DEFECT: all three section-delimiters below appear in lower case */\n"
        "/* strict parsers reject at first mis-cased keyword; lenient parsers fold case and proceed */\n"
        "header;\n"
        "FILE_DESCRIPTION(('Lh047: lower-case framing keywords'),'2;1');\n"
        "FILE_NAME('Lh047.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "endsec;\n"
        "/* DEFECT: data; and endsec; are lower-case — violate the Part-21 framing grammar */\n"
        "data;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('lowercase-keyword-shape',(#1,#2));\n"
        "endsec;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh047(path) -> None:
    Path(path).write_text(_render_lh047())


f.render = _render_lh047  # type: ignore[method-assign]
f.write = _write_lh047    # type: ignore[method-assign]
