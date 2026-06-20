"""Tfa096 — ShapeFix_Face.FixOrientation degenerate-wire bypass.

Catalog claim: Face whose outer wire is composed entirely of zero-length edges
(degenerate). FixOrientation skips degenerate wires without diagnostic, leaving
the face in undefined orientation state.

Mechanism: CLOSED_SHELL with a planar top face whose FACE_OUTER_BOUND contains
four ORIENTED_EDGE entries all sharing identical start/end vertices (collapsed to
a single point). Each edge has a zero-length direction vector. FixOrientation
detects the degenerate outer wire but silently skips it — no diagnostic is
emitted and orientation is left undefined. Companion box faces close the shell.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') >= 1
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa096",
    defect=(
        "CLOSED_SHELL: top face (z=1) FACE_OUTER_BOUND has 4 zero-length EDGE_CURVEs; "
        "all 4 edges share identical start and end vertex at (5,5,1) — collapsed to point; "
        "FixOrientation: degenerate outer wire silently skipped without diagnostic; "
        "orientation left undefined after silent skip; "
        "companion 5 box faces close shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

W = 10.0
H = 1.0

# ── Box corner points ─────────────────────────────────────────────────────────
p000=f.cartesian_point((0.0,0.0,0.0)); p100=f.cartesian_point((W,  0.0,0.0))
p110=f.cartesian_point((W,  W,  0.0)); p010=f.cartesian_point((0.0,W,  0.0))
p001=f.cartesian_point((0.0,0.0,H));   p101=f.cartesian_point((W,  0.0,H))
p111=f.cartesian_point((W,  W,  H));   p011=f.cartesian_point((0.0,W,  H))

v000=f.vertex_point(p000); v100=f.vertex_point(p100)
v110=f.vertex_point(p110); v010=f.vertex_point(p010)
v001=f.vertex_point(p001); v101=f.vertex_point(p101)
v111=f.vertex_point(p111); v011=f.vertex_point(p011)

# Bottom z=0 edges
eb0=f.edge_curve(v000,v100,f.line(p000,f.vector(f.direction(( 1.0,0.0,0.0)),W)))
eb1=f.edge_curve(v100,v110,f.line(p100,f.vector(f.direction(( 0.0,1.0,0.0)),W)))
eb2=f.edge_curve(v110,v010,f.line(p110,f.vector(f.direction((-1.0,0.0,0.0)),W)))
eb3=f.edge_curve(v010,v000,f.line(p010,f.vector(f.direction(( 0.0,-1.0,0.0)),W)))
# Top z=H real edges (for box sides)
et0=f.edge_curve(v001,v101,f.line(p001,f.vector(f.direction(( 1.0,0.0,0.0)),W)))
et1=f.edge_curve(v101,v111,f.line(p101,f.vector(f.direction(( 0.0,1.0,0.0)),W)))
et2=f.edge_curve(v111,v011,f.line(p111,f.vector(f.direction((-1.0,0.0,0.0)),W)))
et3=f.edge_curve(v011,v001,f.line(p011,f.vector(f.direction(( 0.0,-1.0,0.0)),W)))
# Vertical edges
ev0=f.edge_curve(v000,v001,f.line(p000,f.vector(f.direction((0.0,0.0,1.0)),H)))
ev1=f.edge_curve(v100,v101,f.line(p100,f.vector(f.direction((0.0,0.0,1.0)),H)))
ev2=f.edge_curve(v110,v111,f.line(p110,f.vector(f.direction((0.0,0.0,1.0)),H)))
ev3=f.edge_curve(v010,v011,f.line(p010,f.vector(f.direction((0.0,0.0,1.0)),H)))

# ── Bottom face ───────────────────────────────────────────────────────────────
bot_loop=f.edge_loop([f.oriented_edge(eb0,True),f.oriented_edge(eb1,True),
                      f.oriented_edge(eb2,True),f.oriented_edge(eb3,True)])
ax_bot=f.axis2_placement_3d(p000,f.direction((0.0,0.0,-1.0)),f.direction((1.0,0.0,0.0)))
face_bot=f.advanced_face([f.face_outer_bound(bot_loop)],f.plane(ax_bot))

# ── Side faces ────────────────────────────────────────────────────────────────
frt_loop=f.edge_loop([f.oriented_edge(eb0,True),f.oriented_edge(ev1,True),
                      f.oriented_edge(et0,False),f.oriented_edge(ev0,False)])
ax_frt=f.axis2_placement_3d(p000,f.direction((0.0,-1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_frt=f.advanced_face([f.face_outer_bound(frt_loop)],f.plane(ax_frt))

bk_loop=f.edge_loop([f.oriented_edge(ev3,True),f.oriented_edge(et2,False),
                     f.oriented_edge(ev2,False),f.oriented_edge(eb2,False)])
ax_bk=f.axis2_placement_3d(p010,f.direction((0.0,1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_bk=f.advanced_face([f.face_outer_bound(bk_loop)],f.plane(ax_bk))

lft_loop=f.edge_loop([f.oriented_edge(ev0,True),f.oriented_edge(et3,False),
                      f.oriented_edge(ev3,False),f.oriented_edge(eb3,False)])
ax_lft=f.axis2_placement_3d(p000,f.direction((-1.0,0.0,0.0)),f.direction((0.0,1.0,0.0)))
face_lft=f.advanced_face([f.face_outer_bound(lft_loop)],f.plane(ax_lft))

rgt_loop=f.edge_loop([f.oriented_edge(eb1,True),f.oriented_edge(ev2,True),
                      f.oriented_edge(et1,False),f.oriented_edge(ev1,False)])
ax_rgt=f.axis2_placement_3d(p100,f.direction((1.0,0.0,0.0)),f.direction((0.0,1.0,0.0)))
face_rgt=f.advanced_face([f.face_outer_bound(rgt_loop)],f.plane(ax_rgt))

# ── Top face z=H: degenerate outer wire — four zero-length edges at one point ─
# All four edges share the same start == end vertex (collapsed to a single point)
degen_pt = f.cartesian_point((5.0, 5.0, H))
v_degen  = f.vertex_point(degen_pt)
degen_line = f.line(degen_pt, f.vector(f.direction((1.0, 0.0, 0.0)), 0.0))

degen_e0 = f.edge_curve(v_degen, v_degen, degen_line)
degen_e1 = f.edge_curve(v_degen, v_degen, degen_line)
degen_e2 = f.edge_curve(v_degen, v_degen, degen_line)
degen_e3 = f.edge_curve(v_degen, v_degen, degen_line)

degen_loop = f.edge_loop([
    f.oriented_edge(degen_e0, True), f.oriented_edge(degen_e1, True),
    f.oriented_edge(degen_e2, True), f.oriented_edge(degen_e3, True),
])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0,0.0,1.0)), f.direction((1.0,0.0,0.0)))
face_top = f.advanced_face([f.face_outer_bound(degen_loop)], f.plane(ax_top))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh=f.closed_shell([face_bot,face_top,face_frt,face_bk,face_lft,face_rgt])
msb=f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb,mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa096.stp")
