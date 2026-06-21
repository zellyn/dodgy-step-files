"""Lh029 — Schema name in FILE_SCHEMA has whitespace, comments, or vendor extensions.

Catalog claim: Multi-schema FILE_SCHEMA with embedded comments inside the
schema-name list (FILE_SCHEMA(('CONFIG_CONTROL_DESIGN' /* legacy */,
'AUTOMOTIVE_DESIGN'))) or with vendor-specific extensions confuses naive header
parsers. Heal and accept: parse FILE_SCHEMA via the same robust string-literal
tokenizer as DATA; choose the most-capable supported schema; never fall back to
byte-level regex on the raw header.
Bug-reporter language: "comment inside FILE_SCHEMA list", "vendor extension in
schema name list", "whitespace in FILE_SCHEMA element", "FILE_SCHEMA with
embedded comment", "schema-name list malformed".

Reproducer recipe:
  FILE_SCHEMA(('CONFIG_CONTROL_DESIGN' /* legacy */, 'AUTOMOTIVE_DESIGN'));

Byte assertions:
  matches(rb"FILE_SCHEMA\\([^;]*/\\*[^;]*\\*/")
  contains(b'/* legacy */') or contains(b'/* ')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh029",
    defect=(
        "Schema name in FILE_SCHEMA has whitespace, comments, or vendor extensions inside the list; "
        "input: FILE_SCHEMA(('CONFIG_CONTROL_DESIGN' /* legacy */, 'AUTOMOTIVE_DESIGN')); "
        "the embedded comment /* legacy */ appears inside the schema-name list; "
        "naive header parsers that use byte-level regex on the raw header text fail to parse "
        "the schema list correctly when inline comments or vendor extensions are present; "
        "CAD Exchanger v3.24.8 introduced improved parsing of FILE_SCHEMA headers to handle this; "
        "OCC silently accepts (no diagnostic, empty result) — outside catalog allowed set ({heal}); "
        "expected kernel behavior: heal and accept by parsing FILE_SCHEMA via the same robust "
        "string-literal tokenizer as DATA; choose the most-capable supported schema; "
        "synonyms: comment inside FILE_SCHEMA list, vendor extension in schema name list, "
        "whitespace in FILE_SCHEMA element, FILE_SCHEMA with embedded comment, "
        "schema-name list malformed"
    ),
)


def _render_lh029() -> str:
    """Render a Part-21 with an embedded comment inside the FILE_SCHEMA name list."""
    return (
        "ISO-10303-21;\n"
        "/* Lh029: FILE_SCHEMA with embedded comment inside the schema-name list */\n"
        "/* DEFECT: FILE_SCHEMA(('CONFIG_CONTROL_DESIGN' /* legacy */, 'AUTOMOTIVE_DESIGN')) */\n"
        "/* Naive parsers using byte-level regex on the raw header text choke on inline comments */\n"
        "/* OCC silently accepts (no diagnostic, empty result); catalog requires heal and accept */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh029: FILE_SCHEMA with embedded comment in schema-name list'),'2;1');\n"
        "FILE_NAME('Lh029.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: embedded /* legacy */ comment inside the schema name list */\n"
        "FILE_SCHEMA(('CONFIG_CONTROL_DESIGN' /* legacy */, 'AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('comment-in-schema-name-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh029(path) -> None:
    Path(path).write_text(_render_lh029())


f.render = _render_lh029  # type: ignore[method-assign]
f.write = _write_lh029    # type: ignore[method-assign]
