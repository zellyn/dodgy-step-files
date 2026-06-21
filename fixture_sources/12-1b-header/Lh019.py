"""Lh019 — FILE_SCHEMA names a schema that disagrees with entity types in DATA.

Catalog claim: HEADER claims one schema (e.g. IFC4) but DATA uses entity names
that exist only in another schema or another edition (e.g. IFC2X3_PROJECT in an
IFC4 file; ROUND_HOLE in an AP214 file; post-Ed.3 hole-feature entities under
an Ed.2 header). Kernel must reject with a diagnostic naming the offending
entity-name vs. claimed schema; offer a schema-name override flag; parse based
on entity-name availability, not header schema name; warn on mismatch.
Bug-reporter language: "FILE_SCHEMA disagrees with DATA entities", "AP214 entity
in IFC4 file", "schema name mismatches entity types", "entity not in declared
schema", "STEP DATA uses entities from another schema".

Reproducer recipe:
  FILE_SCHEMA(('IFC4')); with body #1=IFC2X3_PROJECT(..);

Byte assertions:
  contains(b'IFC2X3_PROJECT')
  matches(rb"FILE_SCHEMA\\(\\('IFC4'\\)\\)")
  contains(b'IFC2X3') and contains(b'IFC4')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=accept(12)
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh019",
    defect=(
        "FILE_SCHEMA names a schema that disagrees with entity types in DATA; "
        "input: FILE_SCHEMA(('IFC4')) declares IFC4 schema but DATA section contains "
        "IFC2X3_PROJECT which exists only in IFC2X3, not in IFC4; "
        "a conforming kernel must reject with a diagnostic naming the offending entity-name "
        "vs. the claimed schema and offer a schema-name override flag; "
        "parse based on entity-name availability, not header schema name; warn on mismatch; "
        "OCC silently accepts (no diagnostic, empty result) — outside the catalog allowed set ({reject}); "
        "see also: Le027, Lh031; "
        "synonyms: FILE_SCHEMA disagrees with DATA entities, AP214 entity in IFC4 file, "
        "schema name mismatches entity types, entity not in declared schema, "
        "STEP DATA uses entities from another schema"
    ),
)


def _render_lh019() -> str:
    """Render a Part-21 with FILE_SCHEMA(('IFC4')) but IFC2X3_PROJECT entity in DATA."""
    return (
        "ISO-10303-21;\n"
        "/* Lh019: FILE_SCHEMA claims IFC4 but DATA contains IFC2X3_PROJECT from IFC2X3 */\n"
        "/* DEFECT: schema mismatch — FILE_SCHEMA declares IFC4, entity belongs to IFC2X3 */\n"
        "/* Conforming kernel must reject with diagnostic naming offending entity vs schema */\n"
        "/* OCC silently accepts (no diagnostic, empty result) — catalog forbids silent acceptance */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh019: FILE_SCHEMA IFC4 but DATA uses IFC2X3_PROJECT'),'2;1');\n"
        "FILE_NAME('Lh019.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: declares IFC4 but DATA below uses IFC2X3 entity types */\n"
        "FILE_SCHEMA(('IFC4'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: IFC2X3_PROJECT belongs to IFC2X3, not IFC4 as declared in FILE_SCHEMA */\n"
        "#1=IFC2X3_PROJECT('2TH4j2P0X0JvdGnNH$MHRS',$,'Lh019 schema mismatch project',$,$,(#2),$);\n"
        "#2=GEOMETRIC_CURVE_SET('schema-mismatch-shape',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh019(path) -> None:
    Path(path).write_text(_render_lh019())


f.render = _render_lh019  # type: ignore[method-assign]
f.write = _write_lh019    # type: ignore[method-assign]
