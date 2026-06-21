"""Wr011 — Empty parameter list `()` where the schema requires at least one element.

Catalog claim: A `CLOSED_SHELL` entity with an empty face-list `()` appears in
the file because the producer pruned all faces but left the shell wrapper.
Schema requires the face-list to be non-empty.  Some readers reject; some
accept and produce a vacuous shell that flows through the rest of the import
as an empty solid.

Reproducer recipe: `CLOSED_SHELL('hollow',())` referenced by a
`MANIFOLD_SOLID_BREP`.

Byte assertions:
  contains(b'CLOSED_SHELL') and matches(rb"CLOSED_SHELL\('[^']*',\(\)\)")
  matches(rb'CLOSED_SHELL\([^;]*\(\)\)') or matches(rb',\(\)\s*\)')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr011",
    defect=(
        "Empty parameter list where the schema requires at least one element; "
        "a CLOSED_SHELL entity with an empty face-list () appears in the file "
        "because the producer pruned all faces but left the shell wrapper; "
        "schema requires the face-list to be non-empty; "
        "writers that prune the model and forget to suppress now-empty container entities; "
        "some readers reject; some accept and produce a vacuous shell that flows through "
        "the rest of the import as an empty solid; "
        "strongly related to Wr020 (empty SHAPE_DEFINITION_REPRESENTATION chains); "
        "expected kernel behavior: reject the empty-shell case as schema-violating; "
        "do not silently accept the placeholder; "
        "synonyms: empty shell, STEP closed_shell with no faces, writer left a stub entity, "
        "empty face list, STEP shell has no faces"
    ),
)


def _render_empty_closed_shell() -> str:
    """Return a Part-21 with CLOSED_SHELL('hollow',()) referencing a MANIFOLD_SOLID_BREP."""
    return (
        "ISO-10303-21;\n"
        "/* Wr011: CLOSED_SHELL with empty face-list () violates schema */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr011 - empty face list in CLOSED_SHELL'),'2;1');\n"
        "FILE_NAME('Wr011.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: CLOSED_SHELL has an empty face-set (); schema requires >= 1 face */\n"
        "/* Producer pruned all faces but did not suppress the shell entity */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=DIRECTION('zdir',(0.,0.,1.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=AXIS2_PLACEMENT_3D('placement',#1,#2,#3);\n"
        "/* Empty face-list — the defect */\n"
        "#5=CLOSED_SHELL('hollow',());\n"
        "#6=MANIFOLD_SOLID_BREP('empty-body',#5);\n"
        "#7=GEOMETRIC_CURVE_SET('placeholder',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_empty_closed_shell(path) -> None:
    Path(path).write_bytes(_render_empty_closed_shell().encode("utf-8"))


f.render = _render_empty_closed_shell  # type: ignore[method-assign]
f.write = _write_empty_closed_shell  # type: ignore[method-assign]
