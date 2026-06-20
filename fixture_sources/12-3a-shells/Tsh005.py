"""Tsh005 — Solid demoted by stricter receiver tolerance ("clean in FreeCAD, broken in SolidWorks").

Catalog claim (KiCad StepUp regression): a MANIFOLD_SOLID_BREP/CLOSED_SHELL
cube where one face shares a seam vertex that is offset by 0.0011 — just above
a typical 1.0e-3 receiver sewing tolerance.  Strict receivers (SolidWorks)
demote it to a surface model; lenient receivers (FreeCAD) keep the solid.

Mechanism IS the shell structure: the CLOSED_SHELL contains 6 ADVANCED_FACEs;
one face has a seam vertex displaced 0.0011 away from its nominal position,
creating a geometric micro-gap at that seam.  The gap IS wired into the
vertex coordinates of the face entities inside the shell.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') == 6

Tier-3 assertion: n_faces_total == 6
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh005",
    defect=(
        "MANIFOLD_SOLID_BREP/CLOSED_SHELL with 6 faces; one seam vertex offset "
        "0.0011 (above 1e-3 sewing tolerance); micro-gap IS wired into vertex "
        "coordinates in shell/face topology; strict receivers demote to surface"
    ),
)

# ── Cube with a micro-gap on the top-right seam vertex ───────────────────────
# All faces share a nominal right-top edge at x=1, z=1.
# The 'right' face and 'top' face each build this edge from slightly different
# vertex coordinates: nominal vs. nominal+0.0011 — creating the seam gap.

GAP = 0.0011   # > typical 1e-3 sewing tolerance

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Nominal vertices
p000 = pt(0,0,0); p100 = pt(1,0,0); p110 = pt(1,1,0); p010 = pt(0,1,0)
p001 = pt(0,0,1); p101 = pt(1,0,1); p111 = pt(1,1,1); p011 = pt(0,1,1)

# Slightly offset duplicates for the top-face seam (x=1 side):
# p101_gap and p111_gap are the "top-face's view" of the x=1,z=1 edge,
# offset by GAP in the x direction.
p101_gap = pt(1 + GAP, 0, 1)
p111_gap = pt(1 + GAP, 1, 1)

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001)
# Right face uses nominal v101, v111:
v101 = f.vertex_point(p101); v111 = f.vertex_point(p111)
v011 = f.vertex_point(p011)
# Top face uses gap vertices on the x=1 edge:
v101g = f.vertex_point(p101_gap); v111g = f.vertex_point(p111_gap)

# Bottom z=0, normal (0,0,-1)
e_b0 = line_edge(v000, v010, p000,  0, 1, 0)
e_b1 = line_edge(v010, v110, p010,  1, 0, 0)
e_b2 = line_edge(v110, v100, p110,  0,-1, 0)
e_b3 = line_edge(v100, v000, p100, -1, 0, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

# Top z=1, normal (0,0,1): uses gap vertices on the x=1 side
e_t0 = line_edge(v001, v101g, p001,  1, 0, 0)   # v001→v101g (nominal x=0, gap x=1)
e_t1 = line_edge(v101g, v111g, p101_gap, 0, 1, 0)
e_t2 = line_edge(v111g, v011, p111_gap, -1, 0, 0)
e_t3 = line_edge(v011, v001, p011,  0,-1, 0)
lp_top = f.edge_loop([f.oriented_edge(e_t0,True), f.oriented_edge(e_t1,True),
                      f.oriented_edge(e_t2,True), f.oriented_edge(e_t3,True)])
ax_top = f.axis2_placement_3d(p001, f.direction((0,0,1)), f.direction((1,0,0)))
face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top))

# Front y=0, normal (0,-1,0): uses nominal v101
e_f0 = line_edge(v000, v100, p000,  1, 0, 0)
e_f1 = line_edge(v100, v101, p100,  0, 0, 1)
e_f2 = line_edge(v101, v001, p101, -1, 0, 0)
e_f3 = line_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                      f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# Back y=1, normal (0,1,0): uses nominal v111
e_bk0 = line_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = line_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = line_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = line_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                     f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# Left x=0, normal (-1,0,0)
e_l0 = line_edge(v000, v001, p000,  0, 0, 1)
e_l1 = line_edge(v001, v011, p001,  0, 1, 0)
e_l2 = line_edge(v011, v010, p011,  0, 0,-1)
e_l3 = line_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                      f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# Right x=1, normal (1,0,0): uses nominal v101, v111
e_r0 = line_edge(v100, v110, p100,  0, 1, 0)
e_r1 = line_edge(v110, v111, p110,  0, 0, 1)
e_r2 = line_edge(v111, v101, p111,  0,-1, 0)
e_r3 = line_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                      f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── DEFECT: CLOSED_SHELL + MANIFOLD_SOLID_BREP with micro-gap ────────────────
# The 6 faces go into CLOSED_SHELL (correct container type) but the x=1,z=1
# seam edge is mismatched by GAP=0.0011, defeating strict receiver sewing.
# The micro-gap IS wired into the face vertex coordinates in the shell topology.
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)

f.add_product_chain(msb)
