"""Wr041 — Writer emits .TRUE. / .FALSE. instead of canonical .T. / .F.

Catalog claim: a producer's writer emits boolean attribute values as .TRUE. / .FALSE.
rather than the canonical Part-21 .T. / .F. The output is malformed under strict spec
interpretation; receivers that strictly enforce the lexeme reject, while heuristic
receivers fold the long form. Bug-reporter language: "STEP writer emits .TRUE.",
"long-form boolean", "exporter wrote TRUE/FALSE".

Reproducer recipe: a complete file where every EDGE_CURVE same_sense and every
ORIENTED_EDGE orientation attribute uses .TRUE. / .FALSE. instead of .T. / .F.

Byte assertions:
  contains(b'.TRUE.') and contains(b'.FALSE.')
  count(b'.TRUE.') >= 1 and count(b'.FALSE.') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr041",
    defect=(
        "writer emits .TRUE. / .FALSE. instead of canonical .T. / .F.; "
        "input: file where EDGE_CURVE same_sense and ORIENTED_EDGE orientation attributes "
        "use the long-form spellings .TRUE. / .FALSE. instead of the Part-21 canonical "
        "short forms .T. / .F.; "
        "ISO 10303-21 §6.3.4 specifies boolean lexemes are exactly .T. / .F.; "
        "produced by writers built on a generic EXPRESS-instance serialiser that maps "
        "the EXPRESS BOOLEAN keyword to its long-form spelling, or hand-rolled writers "
        "that confuse EXPRESS reserved-word case-insensitivity with Part-21 lexeme conformance; "
        "strict-spec receivers reject; heuristic receivers fold the long form; "
        "expected kernel behavior: heal and accept — writer normalizes / emits canonical "
        "short-form lexemes per the spec; "
        "producer-side root cause for Le055; "
        "synonyms: STEP writer emits .TRUE., long-form boolean, exporter wrote TRUE/FALSE, "
        "boolean lexeme non-conformant"
    ),
)


def _render_wr041() -> str:
    """Render a Part-21 where boolean attributes use long-form .TRUE. / .FALSE. lexemes."""
    return (
        "ISO-10303-21;\n"
        "/* Wr041: writer emits .TRUE. / .FALSE. instead of canonical .T. / .F. */\n"
        "/* ISO 10303-21 §6.3.4: boolean lexemes must be exactly .T. or .F. */\n"
        "/* DEFECT: same_sense and orientation attributes use long-form .TRUE. / .FALSE. */\n"
        "/* Strict receivers reject; heuristic receivers fold; diff tools see noise */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr041: long-form boolean lexemes .TRUE. / .FALSE.'),'2;1');\n"
        "FILE_NAME('Wr041.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: unit square in XY plane */\n"
        "#1=CARTESIAN_POINT('p0',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('p2',(1.,1.,0.));\n"
        "#4=CARTESIAN_POINT('p3',(0.,1.,0.));\n"
        "#5=DIRECTION('xdir',(1.,0.,0.));\n"
        "#6=DIRECTION('ydir',(0.,1.,0.));\n"
        "#7=DIRECTION('xneg',(-1.,0.,0.));\n"
        "#8=DIRECTION('yneg',(0.,-1.,0.));\n"
        "#9=DIRECTION('zdir',(0.,0.,1.));\n"
        "#10=VECTOR('vx',#5,1.);\n"
        "#11=VECTOR('vy',#6,1.);\n"
        "#12=VECTOR('vxn',#7,1.);\n"
        "#13=VECTOR('vyn',#8,1.);\n"
        "#14=LINE('line-bot',#1,#10);\n"
        "#15=LINE('line-rgt',#2,#11);\n"
        "#16=LINE('line-top',#3,#12);\n"
        "#17=LINE('line-lft',#4,#13);\n"
        "#18=VERTEX_POINT('v0',#1);\n"
        "#19=VERTEX_POINT('v1',#2);\n"
        "#20=VERTEX_POINT('v2',#3);\n"
        "#21=VERTEX_POINT('v3',#4);\n"
        "/* DEFECT: same_sense uses .TRUE. instead of canonical .T. */\n"
        "#22=EDGE_CURVE('e-bot',#18,#19,#14,.TRUE.);\n"
        "#23=EDGE_CURVE('e-rgt',#19,#20,#15,.TRUE.);\n"
        "#24=EDGE_CURVE('e-top',#20,#21,#16,.TRUE.);\n"
        "#25=EDGE_CURVE('e-lft',#21,#18,#17,.TRUE.);\n"
        "/* DEFECT: orientation uses .TRUE. / .FALSE. instead of canonical .T. / .F. */\n"
        "#26=ORIENTED_EDGE('',*,*,#22,.TRUE.);\n"
        "#27=ORIENTED_EDGE('',*,*,#23,.TRUE.);\n"
        "#28=ORIENTED_EDGE('',*,*,#24,.FALSE.);\n"
        "#29=ORIENTED_EDGE('',*,*,#25,.FALSE.);\n"
        "#30=EDGE_LOOP('loop',(#26,#27,#28,#29));\n"
        "#31=FACE_OUTER_BOUND('',#30,.T.);\n"
        "#32=AXIS2_PLACEMENT_3D('ax',#1,#9,#5);\n"
        "#33=PLANE('pln',#32);\n"
        "#34=ADVANCED_FACE('sq-face',(#31),#33,.T.);\n"
        "#35=OPEN_SHELL('shell',(#34));\n"
        "#36=SHELL_BASED_SURFACE_MODEL('model',(#35));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr041(path) -> None:
    Path(path).write_text(_render_wr041())


f.render = _render_wr041  # type: ignore[method-assign]
f.write = _write_wr041    # type: ignore[method-assign]
