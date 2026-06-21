"""Wr039 — Re-export re-orders attributes within complex (subtype-stack) records.

Catalog claim: a complex (subtype-stack) record like
(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.)) is re-emitted on round-trip as
(SI_UNIT(.MILLI.,.METRE.) NAMED_UNIT(*) LENGTH_UNIT()); the same complex entity but
with the supertype list reordered. Receivers that build canonical hash strings see the
file as different. Bug-reporter language: "subtype-stack reordered", "complex entity
attribute order changed", "STEP round-trip permutes inheritance order".

Reproducer recipe: #20=(SI_UNIT(.MILLI.,.METRE.) NAMED_UNIT(*) LENGTH_UNIT());
(canonical ordering would be LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(..)).

Byte assertions:
  matches(rb'\\(\\s*SI_UNIT\\([^)]+\\)\\s+NAMED_UNIT\\(\\*\\)\\s+LENGTH_UNIT\\(\\)\\s*\\)')
  matches(rb'\\(\\s*SI_UNIT\\(')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr039",
    defect=(
        "re-export re-orders attributes within complex (subtype-stack) records; "
        "input: complex record (LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.)) "
        "is re-emitted as (SI_UNIT(.MILLI.,.METRE.) NAMED_UNIT(*) LENGTH_UNIT()); "
        "same complex entity but with the supertype list in non-canonical order; "
        "produced by writers that build complex records by iterating an unordered set "
        "of supertype names — visit order determines emission order non-deterministically; "
        "parsers handle either order correctly but file-equivalence hash tests fail; "
        "expected kernel behavior: heal and accept — normalize / emit complex-record "
        "supertype lists in a canonical order (alphabetic or schema-declaration-order) "
        "deterministically on every write; "
        "synonyms: subtype-stack reordered, complex entity attribute order changed, "
        "STEP round-trip permutes inheritance order, supertype list non-deterministic"
    ),
)


def _render_wr039() -> str:
    """Render a Part-21 with non-canonical complex-entity supertype ordering."""
    return (
        "ISO-10303-21;\n"
        "/* Wr039: re-export re-orders attributes within complex (subtype-stack) records */\n"
        "/* Canonical: (LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.)) */\n"
        "/* DEFECT:    (SI_UNIT(.MILLI.,.METRE.) NAMED_UNIT(*) LENGTH_UNIT()) */\n"
        "/* Writer iterated an unordered set of supertype names; SI_UNIT happened first */\n"
        "/* Parsers accept both orders; byte-hash comparators report the file as changed */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr039: non-canonical complex-entity supertype ordering'),'2;1');\n"
        "FILE_NAME('Wr039.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: supertype order is SI_UNIT first, then NAMED_UNIT, then LENGTH_UNIT */\n"
        "/* Canonical schema-declaration order is: LENGTH_UNIT NAMED_UNIT SI_UNIT */\n"
        "#20=(SI_UNIT(.MILLI.,.METRE.) NAMED_UNIT(*) LENGTH_UNIT());\n"
        "#21=GEOMETRIC_CURVE_SET('reordered-complex-entity-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr039(path) -> None:
    Path(path).write_text(_render_wr039())


f.render = _render_wr039  # type: ignore[method-assign]
f.write = _write_wr039    # type: ignore[method-assign]
