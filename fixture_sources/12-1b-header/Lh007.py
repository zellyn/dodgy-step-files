"""Lh007 — Multiple schema names listed inside a single FILE_SCHEMA.

Catalog claim: FILE_SCHEMA carries ('AP203_CONFIG_CONTROL_DESIGN','AUTOMOTIVE_DESIGN').
Most receivers consume only the first; some pick the most-capable; behavior is
implementation-defined and divergent. Bug-reporter language: "multiple schemas in FILE_SCHEMA",
"FILE_SCHEMA lists AP203 and AP214 together", "two schema names in one FILE_SCHEMA",
"STEP picks wrong schema from multi-list", "compound FILE_SCHEMA confuses receiver".

Reproducer recipe: FILE_SCHEMA(('AP203_CONFIG_CONTROL_DESIGN','AUTOMOTIVE_DESIGN'));

Byte assertions:
  matches(rb"FILE_SCHEMA\\(\\(\\s*'[^']+' \\s*,\\s*'[^']+'\\s*\\)\\)")
  count(b"','") >= 2 or matches(rb"FILE_SCHEMA\\(\\(\\s*'[^']+',\\s*'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh007",
    defect=(
        "Multiple schema names listed inside a single FILE_SCHEMA; "
        "input: FILE_SCHEMA list contains two schema names (AP203_CONFIG_CONTROL_DESIGN and "
        "AUTOMOTIVE_DESIGN) in a single FILE_SCHEMA record; "
        "ISO 10303-21 §8 specifies FILE_SCHEMA as a LIST OF STRING but does not define "
        "deterministic behavior when multiple schemas are listed; "
        "most receivers consume only the first schema entry; some pick the most-capable; "
        "behavior is implementation-defined and divergent across tools; "
        "produced by exporters targeting multiple AP versions simultaneously (e.g. AP203 + AP214); "
        "expected kernel behavior: warn; pick the most-capable supported schema deterministically; "
        "do not crash; document which schema was chosen; "
        "see also: Lh006; "
        "synonyms: multiple schemas in FILE_SCHEMA, FILE_SCHEMA lists AP203 and AP214 together, "
        "two schema names in one FILE_SCHEMA, STEP picks wrong schema from multi-list, "
        "compound FILE_SCHEMA confuses receiver"
    ),
)


def _render_lh007() -> str:
    """Render a Part-21 where FILE_SCHEMA lists two schema names in a single record."""
    return (
        "ISO-10303-21;\n"
        "/* Lh007: FILE_SCHEMA lists two schema names — implementation-defined behavior */\n"
        "/* ISO 10303-21 §8: behavior is undefined when FILE_SCHEMA contains multiple names */\n"
        "/* DEFECT: FILE_SCHEMA(('AP203_CONFIG_CONTROL_DESIGN','AUTOMOTIVE_DESIGN')); */\n"
        "/* Receivers diverge: first-wins vs most-capable-wins; both are non-deterministic */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh007: FILE_SCHEMA with multiple schema names'),'2;1');\n"
        "FILE_NAME('Lh007.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: two schema names in one FILE_SCHEMA — divergent receiver behavior */\n"
        "FILE_SCHEMA(('AP203_CONFIG_CONTROL_DESIGN','AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('multi-schema-file-schema-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh007(path) -> None:
    Path(path).write_text(_render_lh007())


f.render = _render_lh007  # type: ignore[method-assign]
f.write = _write_lh007    # type: ignore[method-assign]
