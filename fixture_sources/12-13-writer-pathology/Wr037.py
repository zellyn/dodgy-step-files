"""Wr037 — Loss of seam-edge marking on closed surfaces (cylinder seam emitted as ordinary edge).

Catalog claim: a cylindrical face whose UV-seam edge was marked in the original kernel
is re-emitted with two ordinary edges and duplicate vertices at U=0 and U=2π; the seam
flag is lost. The receiver sees an open shell where the original was closed.
Bug-reporter language: "cylinder seam lost on re-export", "shell became non-watertight
after round-trip", "duplicate vertices at seam".

Reproducer recipe: a cylindrical face whose FACE_OUTER_BOUND is composed of four
ordinary EDGE_CURVE entries (top, bottom, side-A, side-B), where side-A and side-B
share endpoints in 3D but at distinct VERTEX_POINT entities at U=0 and U=2π.

Byte assertions:
  count_entity_def(b'VERTEX_POINT') >= 4
  count(b'VERTEX_POINT') >= 4

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr037",
    defect=(
        "loss of seam-edge marking on closed surfaces (cylinder seam emitted as ordinary edge); "
        "input: CYLINDRICAL_SURFACE face whose UV-seam edge was marked in the original kernel; "
        "writer linearised the seam-edge annotation into two ordinary EDGE_CURVE entries "
        "with duplicate VERTEX_POINT entities at U=0 and U=2pi — no seam flag preserved; "
        "receiver sees an open shell where the original was closed; "
        "produced by writers that serialise a kernel's seam-edge annotation as two separate "
        "ordinary edges with coincident but distinct vertex entities at the seam; "
        "expected kernel behavior: heal and accept — detect duplicate-coincident vertices "
        "at the U-seam of a closed surface; merge and re-mark the edge as a seam; "
        "synonyms: cylinder seam lost on re-export, shell became non-watertight after round-trip, "
        "duplicate vertices at seam, cylinder split at seam"
    ),
)


def _render_wr037() -> str:
    """Render a Part-21 cylindrical face with lost seam-edge marking."""
    return (
        "ISO-10303-21;\n"
        "/* Wr037: loss of seam-edge marking on cylindrical surface */\n"
        "/* Original: cylindrical face with a seam at U=0/U=2pi (writer marked it) */\n"
        "/* Re-emitted: two ordinary EDGE_CURVE entries at U=0 and U=2pi with */\n"
        "/*   distinct VERTEX_POINT entities even though they are coincident in 3D */\n"
        "/* Receiver cannot detect the seam; shell is open where it should be closed */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr037: cylinder seam edge lost on re-export'),'2;1');\n"
        "FILE_NAME('Wr037.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Cylinder axis */\n"
        "#1=CARTESIAN_POINT('axis-origin',(0.,0.,0.));\n"
        "#2=DIRECTION('zdir',(0.,0.,1.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=AXIS2_PLACEMENT_3D('cyl-axis',#1,#2,#3);\n"
        "#5=CYLINDRICAL_SURFACE('cyl-surf',#4,1.0);\n"
        "/* Top circle: at Z=1, radius=1 */\n"
        "#6=CARTESIAN_POINT('top-seam-a',(1.,0.,1.));\n"
        "#7=CARTESIAN_POINT('top-center',(0.,0.,1.));\n"
        "#8=DIRECTION('top-zdir',(0.,0.,1.));\n"
        "#9=DIRECTION('top-xdir',(1.,0.,0.));\n"
        "#10=AXIS2_PLACEMENT_3D('top-circle-ax',#7,#8,#9);\n"
        "#11=CIRCLE('top-circle',#10,1.0);\n"
        "/* Bottom circle: at Z=0, radius=1 */\n"
        "#12=CARTESIAN_POINT('bot-center',(0.,0.,0.));\n"
        "#13=DIRECTION('bot-zdir',(0.,0.,1.));\n"
        "#14=DIRECTION('bot-xdir',(1.,0.,0.));\n"
        "#15=AXIS2_PLACEMENT_3D('bot-circle-ax',#12,#13,#14);\n"
        "#16=CIRCLE('bot-circle',#15,1.0);\n"
        "/* Side seam lines (straight generators at U=0 and U=2pi) */\n"
        "#17=CARTESIAN_POINT('seam-line-pt',(1.,0.,0.));\n"
        "#18=DIRECTION('seam-dir',(0.,0.,1.));\n"
        "#19=VECTOR('seam-vec',#18,1.0);\n"
        "#20=LINE('seam-line-a',#17,#19);\n"
        "#21=LINE('seam-line-b',#17,#19);\n"
        "/* DEFECT: four distinct VERTEX_POINT entities — two pairs coincide in 3D at seam */\n"
        "/* Top vertices at U=0 (seam-A) and U=2pi (seam-B) — same 3D point (1,0,1) */\n"
        "#22=CARTESIAN_POINT('top-pt-seam-a',(1.,0.,1.));\n"
        "#23=CARTESIAN_POINT('top-pt-seam-b',(1.,0.,1.));\n"
        "/* Bottom vertices at U=0 (seam-A) and U=2pi (seam-B) — same 3D point (1,0,0) */\n"
        "#24=CARTESIAN_POINT('bot-pt-seam-a',(1.,0.,0.));\n"
        "#25=CARTESIAN_POINT('bot-pt-seam-b',(1.,0.,0.));\n"
        "#26=VERTEX_POINT('top-v-seam-a',#22);\n"
        "#27=VERTEX_POINT('top-v-seam-b',#23);\n"
        "#28=VERTEX_POINT('bot-v-seam-a',#24);\n"
        "#29=VERTEX_POINT('bot-v-seam-b',#25);\n"
        "/* Edges */\n"
        "/* Top circle edge */\n"
        "#30=EDGE_CURVE('top-edge',#26,#27,#11,.T.);\n"
        "/* Bottom circle edge */\n"
        "#31=EDGE_CURVE('bot-edge',#28,#29,#16,.T.);\n"
        "/* DEFECT: side-A and side-B are ordinary EDGE_CURVE (no seam marking) */\n"
        "/* side-A runs from bot-v-seam-a (#28) to top-v-seam-a (#26) */\n"
        "#32=EDGE_CURVE('seam-side-a',#28,#26,#20,.T.);\n"
        "/* side-B runs from top-v-seam-b (#27) to bot-v-seam-b (#29) */\n"
        "#33=EDGE_CURVE('seam-side-b',#27,#29,#21,.T.);\n"
        "/* Oriented edges and loop */\n"
        "#34=ORIENTED_EDGE('',*,*,#30,.T.);\n"
        "#35=ORIENTED_EDGE('',*,*,#33,.T.);\n"
        "#36=ORIENTED_EDGE('',*,*,#31,.F.);\n"
        "#37=ORIENTED_EDGE('',*,*,#32,.F.);\n"
        "#38=EDGE_LOOP('cyl-loop',(#34,#35,#36,#37));\n"
        "#39=FACE_OUTER_BOUND('',#38,.T.);\n"
        "#40=ADVANCED_FACE('cyl-face',(#39),#5,.T.);\n"
        "#41=OPEN_SHELL('open-shell',(#40));\n"
        "#42=SHELL_BASED_SURFACE_MODEL('cyl-model',(#41));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr037(path) -> None:
    Path(path).write_text(_render_wr037())


f.render = _render_wr037  # type: ignore[method-assign]
f.write = _write_wr037    # type: ignore[method-assign]
