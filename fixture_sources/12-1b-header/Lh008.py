"""Lh008 — Duplicate FILE_SCHEMA records with conflicting schema names.

Catalog claim: Two separate FILE_SCHEMA lines in HEADER. Last-write-wins vs. first-write-wins
behavior diverges across implementations, leading to silent schema mis-binding.
Bug-reporter language: "duplicate FILE_SCHEMA records", "two FILE_SCHEMA lines in HEADER",
"conflicting schema names in header", "second FILE_SCHEMA overrides first",
"schema declared twice with different names".

Reproducer recipe: HEADER; FILE_DESCRIPTION((''),'2;1'); FILE_NAME(..);
FILE_SCHEMA(('AP203_CONFIG_CONTROL_DESIGN')); FILE_SCHEMA(('AUTOMOTIVE_DESIGN')); ENDSEC;

Byte assertions:
  count(b'FILE_SCHEMA') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh008",
    defect=(
        "Duplicate FILE_SCHEMA records with conflicting schema names; "
        "input: HEADER section contains two FILE_SCHEMA records with different schema names "
        "(AP203_CONFIG_CONTROL_DESIGN and AUTOMOTIVE_DESIGN); "
        "ISO 10303-21 §8 requires exactly one FILE_SCHEMA record in the HEADER section; "
        "last-write-wins vs. first-write-wins behavior diverges across implementations, "
        "leading to silent schema mis-binding; "
        "OCC silently accepts (no diagnostic, empty result); "
        "produced by hand-edited files or merge artifacts where two headers are concatenated; "
        "expected kernel behavior: reject; exactly one FILE_SCHEMA is permitted; "
        "see also: Lh006; "
        "synonyms: duplicate FILE_SCHEMA records, two FILE_SCHEMA lines in HEADER, "
        "conflicting schema names in header, second FILE_SCHEMA overrides first, "
        "schema declared twice with different names"
    ),
)


def _render_lh008() -> str:
    """Render a Part-21 with two conflicting FILE_SCHEMA records in the HEADER."""
    return (
        "ISO-10303-21;\n"
        "/* Lh008: HEADER contains two FILE_SCHEMA records with conflicting schema names */\n"
        "/* ISO 10303-21 §8: exactly one FILE_SCHEMA record is permitted in HEADER */\n"
        "/* DEFECT: two FILE_SCHEMA lines — last-write-wins vs first-write-wins diverges */\n"
        "/* Receivers disagree which schema wins; both are non-deterministic silent mis-bindings */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh008: duplicate FILE_SCHEMA with conflicting names'),'2;1');\n"
        "FILE_NAME('Lh008.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: first FILE_SCHEMA record */\n"
        "FILE_SCHEMA(('AP203_CONFIG_CONTROL_DESIGN'));\n"
        "/* DEFECT: second FILE_SCHEMA record — only one is permitted */\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('duplicate-file-schema-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh008(path) -> None:
    Path(path).write_text(_render_lh008())


f.render = _render_lh008  # type: ignore[method-assign]
f.write = _write_lh008    # type: ignore[method-assign]
