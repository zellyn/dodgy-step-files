"""Tfa084 — ShapeAnalysis_FreeBoundsProperties.CheckNotches gap-after-fix.

Catalog claim: Rectangular face with interior notch that, when removed,
leaves 0.1-unit gap between surviving edges. CheckNotches must flag orphaned
gaps as invalid; defect: gap detection skipped.

Mechanism: CLOSED_SHELL box (10×10×1 mm). The top face (z=1) has an outer
wire plus an inner FACE_BOUND that represents a rectangular notch cut into
one side. The notch inner wire is narrow (0.1 mm wide), so when FixNotchedEdges
removes it the surviving outer edges would be 0.1 mm apart. CheckNotches
should flag this residual gap but the gap detection step is skipped.

The inner notch is a thin rectangle: 3.0 wide × 0.1 deep, entering from the
south edge at x=[3.5, 6.5].

Byte assertions:
  - count_entity_def(b'FACE_BOUND') >= 1
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(13) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa084",
    defect=(
        "CLOSED_SHELL 10×10×1 mm box; top face (z=1) outer wire (10×10 rectangle) "
        "plus inner FACE_BOUND: thin notch 3.0×0.1 mm from south edge at x=[3.5,6.5]; "
        "CheckNotches gap-after-fix: 0.1-unit gap between surviving outer edges; "
        "gap detection step skipped — orphaned gap not flagged; "
        "5 companion faces close box shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

W = 10.0
H = 1.0

# Notch dimensions on top face (z=H)
NX0, NX1 = 3.5, 6.5    # notch x range (width = 3.0)
NY0 = 0.0               # notch south edge (flush with outer boundary)
NY1 = 0.1               # notch depth = 0.1 mm

# ── Box corners ───────────────────────────────────────────────────────────────
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
# Top z=H edges
et0=f.edge_curve(v001,v101,f.line(p001,f.vector(f.direction(( 1.0,0.0,0.0)),W)))
et1=f.edge_curve(v101,v111,f.line(p101,f.vector(f.direction(( 0.0,1.0,0.0)),W)))
et2=f.edge_curve(v111,v011,f.line(p111,f.vector(f.direction((-1.0,0.0,0.0)),W)))
et3=f.edge_curve(v011,v001,f.line(p011,f.vector(f.direction(( 0.0,-1.0,0.0)),W)))
# Vertical edges
ev0=f.edge_curve(v000,v001,f.line(p000,f.vector(f.direction((0.0,0.0,1.0)),H)))
ev1=f.edge_curve(v100,v101,f.line(p100,f.vector(f.direction((0.0,0.0,1.0)),H)))
ev2=f.edge_curve(v110,v111,f.line(p110,f.vector(f.direction((0.0,0.0,1.0)),H)))
ev3=f.edge_curve(v010,v011,f.line(p010,f.vector(f.direction((0.0,0.0,1.0)),H)))

# ── Bottom face z=0 ───────────────────────────────────────────────────────────
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

# ── Top face z=H: outer wire + inner notch (FACE_BOUND) ──────────────────────
top_outer_loop=f.edge_loop([f.oriented_edge(et0,True),f.oriented_edge(et1,True),
                             f.oriented_edge(et2,True),f.oriented_edge(et3,True)])
top_outer_fob=f.face_outer_bound(top_outer_loop)

# Inner notch wire: thin rectangle 3.0×0.1 at (3.5-6.5, 0.0-0.1) at z=H
# Vertices
pn00=f.cartesian_point((NX0, NY0, H)); pn10=f.cartesian_point((NX1, NY0, H))
pn11=f.cartesian_point((NX1, NY1, H)); pn01=f.cartesian_point((NX0, NY1, H))
vn00=f.vertex_point(pn00); vn10=f.vertex_point(pn10)
vn11=f.vertex_point(pn11); vn01=f.vertex_point(pn01)

# Notch edges (CW from above = inner hole)
en_s=f.edge_curve(vn00,vn10,f.line(pn00,f.vector(f.direction((1.0,0.0,0.0)),NX1-NX0)))
en_e=f.edge_curve(vn10,vn11,f.line(pn10,f.vector(f.direction((0.0,1.0,0.0)),NY1-NY0)))
en_n=f.edge_curve(vn11,vn01,f.line(pn11,f.vector(f.direction((-1.0,0.0,0.0)),NX1-NX0)))
en_w=f.edge_curve(vn01,vn00,f.line(pn01,f.vector(f.direction((0.0,-1.0,0.0)),NY1-NY0)))

notch_loop=f.edge_loop([f.oriented_edge(en_s,True),f.oriented_edge(en_w,False),
                        f.oriented_edge(en_n,False),f.oriented_edge(en_e,False)])
notch_fb=f.face_bound(notch_loop,orientation=False)

ax_top=f.axis2_placement_3d(p001,f.direction((0.0,0.0,1.0)),f.direction((1.0,0.0,0.0)))
face_top=f.advanced_face([top_outer_fob, notch_fb],f.plane(ax_top))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh=f.closed_shell([face_bot,face_top,face_frt,face_bk,face_lft,face_rgt])
msb=f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb,mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa084.stp")
