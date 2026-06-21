"""Wr013 — Forward references where sequential numbering was expected.

Catalog claim: The producer emits `#5 = ORIENTED_EDGE(..,#10,..)` before `#10`
has been defined.  Spec-conforming readers must do a two-pass parse (or a
deferred-resolution mechanism), but a class of single-pass kernels reports
"reference to undefined instance #10" and rejects.

Reproducer recipe: `#1 = AXIS2_PLACEMENT_3D('a',#5,$,$);` appears first, with
`#5 = CARTESIAN_POINT('p',(0.,0.,0.));` defined later — so `#1` contains a
forward reference to `#5`.

Byte assertions:
  matches(rb'(?s)#1=AXIS2_PLACEMENT_3D[^;]+#5[^;]+;.*#5=CARTESIAN_POINT')
  matches(rb'(?s)#1=[^;]+#5')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr013",
    defect=(
        "Forward references where sequential numbering was expected; "
        "the producer emits #1 = AXIS2_PLACEMENT_3D referencing #5 before #5 is defined; "
        "writers that emit entities in topological-construction order without a "
        "topological sort; observed in some open-source exporters; "
        "spec-conforming readers must do a two-pass parse or a deferred-resolution "
        "mechanism; but a class of single-pass kernels reports reference to undefined "
        "instance number and rejects; "
        "the spec permits forward references; "
        "expected kernel behavior: implement two-pass parsing or deferred-resolution; "
        "reject only if a reference remains unresolved after the full file is parsed; "
        "synonyms: forward references in STEP, ref before def, "
        "kernel doesn't support out-of-order STEP, ref to undefined instance"
    ),
)


def _render_forward_reference() -> str:
    """Return a Part-21 file where #1 (AXIS2_PLACEMENT_3D) forward-references #5 (CARTESIAN_POINT)."""
    return (
        "ISO-10303-21;\n"
        "/* Wr013: forward reference — #1 references #5 before #5 is defined */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr013 - forward reference to undefined instance'),'2;1');\n"
        "FILE_NAME('Wr013.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: #1 references #5 which has not yet been defined at this point */\n"
        "/* A single-pass parser would see an unresolved reference at #1 parse time */\n"
        "#1=AXIS2_PLACEMENT_3D('placement',#5,#6,#7);\n"
        "#2=PLANE('face-plane',#1);\n"
        "#3=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#4=CARTESIAN_POINT('p2',(1.,1.,0.));\n"
        "/* #5, #6, #7 are defined after #1 — forward references */\n"
        "#5=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#6=DIRECTION('zdir',(0.,0.,1.));\n"
        "#7=DIRECTION('xdir',(1.,0.,0.));\n"
        "#8=GEOMETRIC_CURVE_SET('forward-ref',(#3,#4));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_forward_reference(path) -> None:
    Path(path).write_bytes(_render_forward_reference().encode("utf-8"))


f.render = _render_forward_reference  # type: ignore[method-assign]
f.write = _write_forward_reference  # type: ignore[method-assign]
