"""Wr009 — Spurious `$` for required parameter (writer omits required value).

Catalog claim: The producer emits `$` (omitted) where the EXPRESS schema
declares the attribute as required (non-OPTIONAL).
Example: `AXIS2_PLACEMENT_3D('placement',#10,$,$)` where the schema specifies
`axis` and `ref_direction` as effectively required when both are present.
Some kernels invent a default direction; others reject.

Reproducer recipe: `AXIS2_PLACEMENT_3D('p',#10,$,$)` paired with a
`MANIFOLD_SOLID_BREP` that depends on the placement.

Byte assertions:
  matches(rb'AXIS2_PLACEMENT_3D\\([^;]*,#\\d+,\\$,\\$\\)')
  contains(b'$,$)') or matches(rb',\\$\\s*,\\$\\s*\\)')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr009",
    defect=(
        "Spurious dollar-sign for required parameter (writer omits required value); "
        "the producer emits $ (omitted) where the EXPRESS schema declares the attribute "
        "as required (non-OPTIONAL); "
        "AXIS2_PLACEMENT_3D('p',#10,$,$) where the schema specifies axis and ref_direction "
        "as effectively required when both are present; "
        "older Pro/E and some lightweight web-CAD STEP exporters; "
        "some kernels invent a default direction; others reject; "
        "AP242 marks axis and ref_direction as OPTIONAL in the EXPRESS; "
        "but most receivers expect both populated when the placement is referenced "
        "from a non-trivial geometry context; "
        "expected kernel behavior: reject as malformed when a required attribute is $; "
        "do not silently substitute Z+X defaults because the producer's intent is unrecoverable; "
        "synonyms: STEP file has dollar signs for required fields, missing axis direction, "
        "writer skipped required attribute, writer omitted required attribute"
    ),
)


def _render_missing_required_param() -> str:
    """Return a Part-21 string with AXIS2_PLACEMENT_3D omitting required axis attrs."""
    return (
        "ISO-10303-21;\n"
        "/* Wr009: spurious $ for required parameter in AXIS2_PLACEMENT_3D */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr009 - spurious dollar for required attribute'),'2;1');\n"
        "FILE_NAME('Wr009.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: AXIS2_PLACEMENT_3D has $,$ for axis and ref_direction */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "/* axis and ref_direction are $ (omitted) but are required for non-trivial use */\n"
        "#2=AXIS2_PLACEMENT_3D('placement',#1,$,$);\n"
        "#3=PLANE('face-plane',#2);\n"
        "#4=CARTESIAN_POINT('p0',(0.,0.,0.));\n"
        "#5=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#6=CARTESIAN_POINT('p2',(1.,1.,0.));\n"
        "#7=CARTESIAN_POINT('p3',(0.,1.,0.));\n"
        "#8=VERTEX_POINT('v0',#4);\n"
        "#9=VERTEX_POINT('v1',#5);\n"
        "#10=VERTEX_POINT('v2',#6);\n"
        "#11=VERTEX_POINT('v3',#7);\n"
        "#12=DIRECTION('xdir',(1.,0.,0.));\n"
        "#13=VECTOR('xvec',#12,1.);\n"
        "#14=LINE('edge-line',#4,#13);\n"
        "#15=DIRECTION('ydir',(0.,1.,0.));\n"
        "#16=VECTOR('yvec',#15,1.);\n"
        "#17=LINE('edge-line2',#5,#16);\n"
        "#18=DIRECTION('nxdir',(-1.,0.,0.));\n"
        "#19=VECTOR('nxvec',#18,1.);\n"
        "#20=LINE('edge-line3',#6,#19);\n"
        "#21=DIRECTION('nydir',(0.,-1.,0.));\n"
        "#22=VECTOR('nyvec',#21,1.);\n"
        "#23=LINE('edge-line4',#7,#22);\n"
        "#24=EDGE_CURVE('e0',#8,#9,#14,.T.);\n"
        "#25=EDGE_CURVE('e1',#9,#10,#17,.T.);\n"
        "#26=EDGE_CURVE('e2',#10,#11,#20,.T.);\n"
        "#27=EDGE_CURVE('e3',#11,#8,#23,.T.);\n"
        "#28=ORIENTED_EDGE('',*,*,#24,.T.);\n"
        "#29=ORIENTED_EDGE('',*,*,#25,.T.);\n"
        "#30=ORIENTED_EDGE('',*,*,#26,.T.);\n"
        "#31=ORIENTED_EDGE('',*,*,#27,.T.);\n"
        "#32=EDGE_LOOP('loop',(#28,#29,#30,#31));\n"
        "#33=FACE_OUTER_BOUND('fob',#32,.T.);\n"
        "#34=ADVANCED_FACE('face',(#33),#3,.T.);\n"
        "#35=CLOSED_SHELL('shell',(#34));\n"
        "#36=MANIFOLD_SOLID_BREP('body',#35);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_missing_required_param(path) -> None:
    Path(path).write_bytes(_render_missing_required_param().encode("utf-8"))


f.render = _render_missing_required_param  # type: ignore[method-assign]
f.write = _write_missing_required_param  # type: ignore[method-assign]
