"""Lh022 — Duplicate instance ID (#N=.. defined twice within one DATA section).

Catalog claim: Within one DATA section each #N may appear on the LHS at most
once. Concatenating two STEP files with overlapping IDs, or merging sub-files
without renumbering, produces duplicates. Silent overwrite causes semantic
divergence; in C++ implementations, freeing the first instance while references
still point at it transitions to use-after-free. Kernel must reject with
E_DUPLICATE_INSTANCE_ID before constructing the second instance; never
silently overwrite or free-then-reuse.
Bug-reporter language: "duplicate instance ID in DATA", "#42 defined twice in
STEP", "concatenated STEP files have ID collision", "two definitions of same
#N", "instance ID overwrites previous".

Reproducer recipe:
  DATA; #10=PRODUCT('a','a','',(#11)); #10=PRODUCT('b','b','',(#12)); ENDSEC;
  or #19=IFCPROJECT(..); #19=IFCSITE(..);

Byte assertions:
  count_entity_def(b'PRODUCT') >= 2 or matches(rb'(?s)#4=PRODUCT.*#4=PRODUCT')
  matches(rb'(?s)#4=PRODUCT.*#4=PRODUCT')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh022",
    defect=(
        "Duplicate instance ID (#N=.. defined twice within one DATA section); "
        "input: DATA section defines #4=PRODUCT('widget-a',..) and then again "
        "#4=PRODUCT('widget-b',..) — the same instance ID appears on the LHS twice; "
        "within one DATA section each #N may appear at most once per ISO 10303-21; "
        "concatenating two STEP files with overlapping IDs or merging sub-files "
        "without renumbering produces this defect; "
        "silent overwrite causes semantic divergence; in C++ implementations, freeing "
        "the first instance while references still point at it transitions to use-after-free; "
        "OCC silently accepts duplicate instance IDs (last-write-wins) without diagnostic; "
        "expected kernel behavior: reject with E_DUPLICATE_INSTANCE_ID before constructing "
        "the second instance; never silently overwrite or free-then-reuse; "
        "see also: Ad038, Lh024; "
        "synonyms: duplicate instance ID in DATA, #42 defined twice in STEP, "
        "concatenated STEP files have ID collision, two definitions of same #N, "
        "instance ID overwrites previous"
    ),
)


def _render_lh022() -> str:
    """Render a Part-21 with the same instance ID #4 defined twice in one DATA section."""
    return (
        "ISO-10303-21;\n"
        "/* Lh022: duplicate instance ID — #4=PRODUCT defined twice in one DATA section */\n"
        "/* DEFECT: ISO 10303-21 requires each #N to appear at most once as LHS in DATA */\n"
        "/* Produced by concatenating two STEP files without renumbering IDs */\n"
        "/* OCC: silently accepts (last-write-wins); catalog forbids silent overwrite */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh022: duplicate instance ID #4 defined twice in DATA'),'2;1');\n"
        "FILE_NAME('Lh022.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=PRODUCT_DEFINITION_CONTEXT('part definition',#5,'design');\n"
        "/* DEFECT: first definition of #4 */\n"
        "#4=PRODUCT('widget-a','Widget A','',(#3));\n"
        "#5=APPLICATION_CONTEXT('automotive design');\n"
        "/* DEFECT: second definition of #4 — same ID reused, violates ISO 10303-21 */\n"
        "#4=PRODUCT('widget-b','Widget B','',(#3));\n"
        "#6=GEOMETRIC_CURVE_SET('duplicate-id-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh022(path) -> None:
    Path(path).write_text(_render_lh022())


f.render = _render_lh022  # type: ignore[method-assign]
f.write = _write_lh022    # type: ignore[method-assign]
