"""Wr007 — Locale-sensitive decimal separator emitted (comma instead of period).

Catalog claim: Numeric attributes appear with commas as decimal separator
(`1,5` instead of `1.5`) because the writer used a locale-aware formatter.
ISO 10303-21 mandates the period (`.`) as the decimal separator; comma-decimal
output is malformed.  Receivers either fail at the lexer (a `,` mid-number
ends the argument and the next field is mis-counted) or, with bizarre
tolerance, accept the comma and produce wrong geometry.

Reproducer recipe: a CARTESIAN_POINT entry with coordinates `(1,5,2,5,3,5)`
(intended as `(1.5,2.5,3.5)` but parsed as 6 separate integers).

Byte assertions:
  matches(rb"CARTESIAN_POINT\\([^;]*,\\(\\d+,\\d+,\\d+,\\d+")
  count(b',') >= 8

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr007",
    defect=(
        "Locale-sensitive decimal separator emitted (comma instead of period); "
        "numeric attributes appear with commas as decimal separator (1,5 instead of 1.5) "
        "because the writer used a locale-aware formatter without forcing the C locale; "
        "ISO 10303-21 mandates the period (.) as the decimal separator; "
        "comma-decimal output is malformed; "
        "writers that use locale-aware sprintf / std::to_string on Windows builds "
        "running with German, French, or other comma-decimal locales; "
        "receivers either fail at the lexer (a comma mid-number ends the argument "
        "and the next field is mis-counted) or accept the comma and produce wrong geometry; "
        "expected kernel behavior: reject as malformed with a diagnostic naming the "
        "offending attribute and column; "
        "synonyms: commas in numbers, German locale STEP, STEP file from European user "
        "looks corrupt, commas where it should have periods"
    ),
)


def _render_comma_decimal() -> str:
    """Return a Part-21 string where comma is used as decimal separator."""
    return (
        "ISO-10303-21;\n"
        "/* Wr007: comma decimal separator (locale bug) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr007 - locale-sensitive comma decimal separator'),'2;1');\n"
        "FILE_NAME('Wr007.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: comma used as decimal separator (intended 1.5, 2.5, 3.5) */\n"
        "/* Lexer sees (1,5,2,5,3,5) — 6 separate integer tokens, not 3 reals */\n"
        "#1=CARTESIAN_POINT('comma-decimal',(1,5,2,5,3,5));\n"
        "#2=GEOMETRIC_CURVE_SET('locale-bug',(#1));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_comma_decimal(path) -> None:
    Path(path).write_bytes(_render_comma_decimal().encode("utf-8"))


f.render = _render_comma_decimal  # type: ignore[method-assign]
f.write = _write_comma_decimal  # type: ignore[method-assign]
