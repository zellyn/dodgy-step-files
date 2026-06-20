"""Tfa094 — ShapeAnalysis_CheckSmallFace.CheckSplittingVertices boundary T-vertex.

Catalog claim: Outer wire passes through a vertex that is the endpoint of an
inner wire, creating a T-shaped junction at the boundary. T-vertex detector
classifies interior T-vertices but misses the boundary case where outer wire
vertex coincides with inner wire endpoint.

Mechanism: CLOSED_SHELL with a planar top face carrying a hexagonal outer wire
and a rectangular inner wire (FACE_BOUND). One vertex of the inner rectangle
exactly coincides with one vertex of the hexagonal outer wire — forming a
T-vertex at the boundary. CheckSplittingVertices traverses inner wire endpoints
but skips checking against outer wire vertices.

Byte assertions:
  - count_entity_def(b'FACE_BOUND') >= 1
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa094",
    defect=(
        "CLOSED_SHELL: planar top face with hexagonal FACE_OUTER_BOUND + "
        "rectangular inner FACE_BOUND; "
        "inner rectangle NW corner (2.0,4.0) coincides exactly with hex vertex H2; "
        "T-vertex at boundary: outer wire vertex == inner wire endpoint; "
        "CheckSplittingVertices misses boundary T-vertex (only checks interior); "
        "box shell has 6 faces closing CLOSED_SHELL; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# ── Box geometry: 10×10×1 mm base ────────────────────────────────────────────
BW = 10.0
BH = 1.0

# ── Hexagonal outer wire on top face (z=BH) ──────────────────────────────────
# Regular hexagon centered at (5,5), radius 4.0
# Vertex H2 will be at angle=120° → (5+4*cos120, 5+4*sin120) = (3.0, 8.464)
# We simplify: place one vertex at (2.0, 4.0) to match the inner rect NW corner
# Use a non-regular hexagon with vertices:
# H0=(5,1), H1=(9,1), H2=(10,5), H3=(9,9), H4=(5,9), H5=(1,5)
# T-vertex: inner rectangle corner (1,5) coincides with H5=(1,5)
hex_pts = [
    (5.0, 1.0), (9.0, 1.0), (10.0, 5.0),
    (9.0, 9.0), (5.0, 9.0), (1.0, 5.0),
]
z_top = BH

hex_verts = [f.vertex_point(f.cartesian_point((x, y, z_top))) for x, y in hex_pts]

def hex_edge(i, j):
    xa, ya = hex_pts[i]; xb, yb = hex_pts[j]
    dx=xb-xa; dy=yb-ya; mag=math.sqrt(dx*dx+dy*dy)
    d=f.direction((dx/mag, dy/mag, 0.0))
    return f.edge_curve(hex_verts[i], hex_verts[j],
                        f.line(f.cartesian_point((xa,ya,z_top)), f.vector(d, mag)))

he0=hex_edge(0,1); he1=hex_edge(1,2); he2=hex_edge(2,3)
he3=hex_edge(3,4); he4=hex_edge(4,5); he5=hex_edge(5,0)

hex_loop=f.edge_loop([
    f.oriented_edge(he0,True),f.oriented_edge(he1,True),
    f.oriented_edge(he2,True),f.oriented_edge(he3,True),
    f.oriented_edge(he4,True),f.oriented_edge(he5,True),
])
hex_fob=f.face_outer_bound(hex_loop)

# ── Inner rectangular wire (FACE_BOUND) ──────────────────────────────────────
# Rectangle with NW corner at (1,5) — same as H5 = T-vertex
# Rectangle: (1,5) → (3,5) → (3,3) → (1,3) → back to (1,5)
# NW=(1,5) = H5 is the T-vertex contact point
rect_pts = [(1.0,5.0), (3.0,5.0), (3.0,3.0), (1.0,3.0)]
rect_verts = [f.vertex_point(f.cartesian_point((x, y, z_top))) for x, y in rect_pts]
# Override rect_verts[0] to reuse the hex vertex H5 for the T-vertex
rect_verts[0] = hex_verts[5]  # T-vertex: shared with outer hex

def rect_edge(i, j):
    xa, ya = rect_pts[i]; xb, yb = rect_pts[j]
    dx=xb-xa; dy=yb-ya; mag=math.sqrt(dx*dx+dy*dy)
    d=f.direction((dx/mag, dy/mag, 0.0))
    return f.edge_curve(rect_verts[i], rect_verts[j],
                        f.line(f.cartesian_point((xa,ya,z_top)), f.vector(d, mag)))

re0=rect_edge(0,1); re1=rect_edge(1,2); re2=rect_edge(2,3); re3=rect_edge(3,0)

# Inner wire: CW from above (hole inside hex) — orientation=False for inner
rect_loop=f.edge_loop([
    f.oriented_edge(re0,False),f.oriented_edge(re3,False),
    f.oriented_edge(re2,False),f.oriented_edge(re1,False),
])
rect_fb=f.face_bound(rect_loop, orientation=False)

ax_top=f.axis2_placement_3d(
    f.cartesian_point((0.0,0.0,z_top)),
    f.direction((0.0,0.0,1.0)),
    f.direction((1.0,0.0,0.0))
)
face_top=f.advanced_face([hex_fob, rect_fb], f.plane(ax_top))

# ── Simple box shell to host the top face ────────────────────────────────────
p000=f.cartesian_point((0.0, 0.0,  0.0)); p100=f.cartesian_point((BW, 0.0,  0.0))
p110=f.cartesian_point((BW, BW,   0.0)); p010=f.cartesian_point((0.0, BW,   0.0))
p001=f.cartesian_point((0.0, 0.0, BH));   p101=f.cartesian_point((BW, 0.0, BH))
p111=f.cartesian_point((BW, BW,  BH));    p011=f.cartesian_point((0.0, BW, BH))

v000=f.vertex_point(p000); v100=f.vertex_point(p100)
v110=f.vertex_point(p110); v010=f.vertex_point(p010)
v001=f.vertex_point(p001); v101=f.vertex_point(p101)
v111=f.vertex_point(p111); v011=f.vertex_point(p011)

eb0=f.edge_curve(v000,v100,f.line(p000,f.vector(f.direction((1.0,0.0,0.0)),BW)))
eb1=f.edge_curve(v100,v110,f.line(p100,f.vector(f.direction((0.0,1.0,0.0)),BW)))
eb2=f.edge_curve(v110,v010,f.line(p110,f.vector(f.direction((-1.0,0.0,0.0)),BW)))
eb3=f.edge_curve(v010,v000,f.line(p010,f.vector(f.direction((0.0,-1.0,0.0)),BW)))
et0=f.edge_curve(v001,v101,f.line(p001,f.vector(f.direction((1.0,0.0,0.0)),BW)))
et1=f.edge_curve(v101,v111,f.line(p101,f.vector(f.direction((0.0,1.0,0.0)),BW)))
et2=f.edge_curve(v111,v011,f.line(p111,f.vector(f.direction((-1.0,0.0,0.0)),BW)))
et3=f.edge_curve(v011,v001,f.line(p011,f.vector(f.direction((0.0,-1.0,0.0)),BW)))
ev0=f.edge_curve(v000,v001,f.line(p000,f.vector(f.direction((0.0,0.0,1.0)),BH)))
ev1=f.edge_curve(v100,v101,f.line(p100,f.vector(f.direction((0.0,0.0,1.0)),BH)))
ev2=f.edge_curve(v110,v111,f.line(p110,f.vector(f.direction((0.0,0.0,1.0)),BH)))
ev3=f.edge_curve(v010,v011,f.line(p010,f.vector(f.direction((0.0,0.0,1.0)),BH)))

bot_loop=f.edge_loop([f.oriented_edge(eb0,True),f.oriented_edge(eb1,True),
                      f.oriented_edge(eb2,True),f.oriented_edge(eb3,True)])
ax_bot=f.axis2_placement_3d(p000,f.direction((0.0,0.0,-1.0)),f.direction((1.0,0.0,0.0)))
face_bot=f.advanced_face([f.face_outer_bound(bot_loop)],f.plane(ax_bot))

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

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh=f.closed_shell([face_bot,face_top,face_frt,face_bk,face_lft,face_rgt])
msb=f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb,mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa094.stp")
