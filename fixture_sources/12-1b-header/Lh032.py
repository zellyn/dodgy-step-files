"""Lh032 — Constant reference (#NAME/@NAME) used where instance reference required.

Catalog claim: ISO 10303-21 distinguishes #NAME/@NAME (uppercase identifier,
refers to a schema-defined constant) from #NNN/@NNN (refers to an instance).
Tools occasionally emit #PI thinking it is a literal alias when the schema
defines no such constant, producing an unresolved-reference error.
Bug-reporter language: "#NAME constant reference where #NNN expected", "@NAME
used as instance reference", "schema constant in STEP DATA", "#PI as alias not
resolved", "constant reference unresolved".

Reproducer recipe:
  #1=DIRECTION('',(#PI,0.,0.)); where PI is not a schema-defined constant.

Byte assertions:
  matches(rb'#[A-Z][A-Z_]*\\b')
  matches(rb'#PI\\b')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh032",
    defect=(
        "Constant reference (#NAME/@NAME) used where instance reference (#NNN) required; "
        "input: #1=DIRECTION('',(#PI,0.,0.)); where #PI is used as a literal alias for pi "
        "but PI is not a schema-defined constant in AUTOMOTIVE_DESIGN; "
        "ISO 10303-21 distinguishes #NAME/@NAME (uppercase identifier referring to a "
        "schema-defined constant) from #NNN/@NNN (referring to an instance); "
        "tools emit #PI thinking it is a literal alias; "
        "the schema defines no such constant, producing an unresolved-reference error; "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: reject as undefined constant with a diagnostic that "
        "distinguishes constant not in schema from instance not defined; "
        "synonyms: #NAME constant reference where #NNN expected, @NAME used as instance reference, "
        "schema constant in STEP DATA, #PI as alias not resolved, constant reference unresolved"
    ),
)


def _render_lh032() -> str:
    """Render a Part-21 with #PI used as constant where #NNN instance reference is required."""
    return (
        "ISO-10303-21;\n"
        "/* Lh032: #PI used as schema-defined constant where an instance reference is required */\n"
        "/* ISO 10303-21: #NAME refers to a schema-defined constant; #NNN refers to an instance */\n"
        "/* DEFECT: #PI is not a constant in AUTOMOTIVE_DESIGN; unresolved-reference error */\n"
        "/* OCC silently accepts with diagnostic (empty result); catalog requires reject */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh032: #PI constant reference where #NNN instance expected'),'2;1');\n"
        "FILE_NAME('Lh032.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('pi-point',(#PI,0.,0.));\n"
        "/* DEFECT: #PI used as if it were a schema-defined constant (like math pi = 3.14159) */\n"
        "/* but AUTOMOTIVE_DESIGN defines no constant named PI; this is an unresolved reference */\n"
        "#3=DIRECTION('xdir',(#PI,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('constant-ref-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh032(path) -> None:
    Path(path).write_text(_render_lh032())


f.render = _render_lh032  # type: ignore[method-assign]
f.write = _write_lh032    # type: ignore[method-assign]
