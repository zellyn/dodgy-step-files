"""Wr038 — Re-emitted file uses entity-numbering pattern that breaks round-trip equivalence.

Catalog claim: a round-trip (read STEP → no-op → write STEP) produces a file that
differs from the input only in the choice of #N numbering; every export uses different
numbers. This breaks regression tests that compare files by hash.
Bug-reporter language: "STEP files differ after no-op round-trip", "file hashes change
every export", "diff is just renumbering".

Reproducer recipe: a file with deliberately non-canonical numbering (#42, #17, #99, #1)
to demonstrate the post-pathology state.

Byte assertions:
  matches(rb'(?s)#42.*#17.*#99.*#1=') or matches(rb'#\\d+=APPLICATION_CONTEXT')
  count(b'#') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr038",
    defect=(
        "re-emitted file uses entity-numbering pattern that breaks round-trip equivalence; "
        "input: a STEP file that on round-trip (read then write) produces different #N entity "
        "numbers each export — entity numbers are chosen non-deterministically; "
        "writer inserts a timestamp or random suffix into entity numbering; "
        "every export differs in entity numbering even though the geometry is unchanged; "
        "breaks regression tests that compare files for equivalence by hash; "
        "produced by writers that iterate an unordered internal representation "
        "and assign ascending IDs in visit order; "
        "expected kernel behavior: heal and accept — normalize / emit canonical deterministic "
        "numbering on write so a no-op round-trip produces byte-identical output "
        "(modulo timestamp-bearing fields like FILE_NAME date); "
        "synonyms: STEP files differ after no-op round-trip, file hashes change every export, "
        "diff is just renumbering, non-deterministic entity IDs"
    ),
)


def _render_wr038() -> str:
    """Render a Part-21 with non-canonical entity numbering (#42, #17, #99, #1)."""
    return (
        "ISO-10303-21;\n"
        "/* Wr038: non-canonical entity numbering breaks round-trip equivalence */\n"
        "/* Entity numbers (#42, #17, #99, #1) are in non-sequential, non-canonical order */\n"
        "/* Writer assigned numbers in internal-representation visit order (unordered set) */\n"
        "/* Every export run produces different numbering — file hashes change with each write */\n"
        "/* A no-op round-trip (read then write) produces a byte-different file */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr038: non-canonical entity numbering'),'2;1');\n"
        "FILE_NAME('Wr038.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: entity numbers skip and reorder: #42, #17, #99, #1 — non-canonical */\n"
        "/* Canonical form would assign #1, #2, #3, #4 sequentially */\n"
        "#42=APPLICATION_CONTEXT('automotive_design');\n"
        "#17=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#99=CARTESIAN_POINT('corner',(1.,1.,1.));\n"
        "#1=GEOMETRIC_CURVE_SET('non-canonical-numbering-shape',(#17,#99));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr038(path) -> None:
    Path(path).write_text(_render_wr038())


f.render = _render_wr038  # type: ignore[method-assign]
f.write = _write_wr038    # type: ignore[method-assign]
