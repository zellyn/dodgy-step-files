"""Tsh001 — ManifoldSolidBrep.outer references OPEN_SHELL.

Catalog claim: A MANIFOLD_SOLID_BREP whose `outer` field references an
OPEN_SHELL rather than the schema-required CLOSED_SHELL.  Strict receivers
must heal (promote to closed when topology actually closes) or warn-and-proceed.
OCCT silently accepts with no diagnostic.

Mechanism IS the shell structure: a 6-face unit-cube topology is wired as
OPEN_SHELL and that OPEN_SHELL is placed directly inside MANIFOLD_SOLID_BREP.
The schema violation IS the root entity referencing the wrong shell type.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') == 6

Tier-3 assertion: n_faces_total == 6
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh001",
    defect=(
        "MANIFOLD_SOLID_BREP.outer references OPEN_SHELL instead of CLOSED_SHELL; "
        "schema violation IS wired into shell/face topology; OCCT silently accepts; "
        "strict receivers must heal or warn"
    ),
)

# ── Unit-cube: 6 independent ADVANCED_FACEs ────────────────────────────────
# Each face is built with its own edge set (no shared edge objects, keeping
# the topology simple while ensuring exactly 6 ADVANCED_FACE entities).

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Build all faces directly with explicit edge directions:
p000 = pt(0,0,0); p100 = pt(1,0,0); p110 = pt(1,1,0); p010 = pt(0,1,0)
p001 = pt(0,0,1); p101 = pt(1,0,1); p111 = pt(1,1,1); p011 = pt(0,1,1)
v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom z=0, outward normal (0,0,-1): CCW looking from -z → order 000,010,110,100
e_b0 = line_edge(v000, v010, p000,  0, 1, 0)
e_b1 = line_edge(v010, v110, p010,  1, 0, 0)
e_b2 = line_edge(v110, v100, p110,  0,-1, 0)
e_b3 = line_edge(v100, v000, p100, -1, 0, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

# Top z=1, outward normal (0,0,1): CCW looking from +z → order 001,101,111,011
e_t0 = line_edge(v001, v101, p001,  1, 0, 0)
e_t1 = line_edge(v101, v111, p101,  0, 1, 0)
e_t2 = line_edge(v111, v011, p111, -1, 0, 0)
e_t3 = line_edge(v011, v001, p011,  0,-1, 0)
lp_top = f.edge_loop([f.oriented_edge(e_t0,True), f.oriented_edge(e_t1,True),
                      f.oriented_edge(e_t2,True), f.oriented_edge(e_t3,True)])
ax_top = f.axis2_placement_3d(p001, f.direction((0,0,1)), f.direction((1,0,0)))
face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top))

# Front y=0, outward normal (0,-1,0): CCW from -y → 000,100,101,001
e_f0 = line_edge(v000, v100, p000,  1, 0, 0)
e_f1 = line_edge(v100, v101, p100,  0, 0, 1)
e_f2 = line_edge(v101, v001, p101, -1, 0, 0)
e_f3 = line_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                      f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# Back y=1, outward normal (0,1,0): CCW from +y → 010,011,111,110
e_bk0 = line_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = line_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = line_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = line_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                     f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# Left x=0, outward normal (-1,0,0): CCW from -x → 000,001,011,010
e_l0 = line_edge(v000, v001, p000,  0, 0, 1)
e_l1 = line_edge(v001, v011, p001,  0, 1, 0)
e_l2 = line_edge(v011, v010, p011,  0, 0,-1)
e_l3 = line_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                      f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# Right x=1, outward normal (1,0,0): CCW from +x → 100,110,111,101
e_r0 = line_edge(v100, v110, p100,  0, 1, 0)
e_r1 = line_edge(v110, v111, p110,  0, 0, 1)
e_r2 = line_edge(v111, v101, p111,  0,-1, 0)
e_r3 = line_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                      f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── DEFECT: wrap the 6 faces in OPEN_SHELL then reference it from MANIFOLD_SOLID_BREP ──
# Schema requires MANIFOLD_SOLID_BREP.outer to be CLOSED_SHELL.
# Using OPEN_SHELL here IS the mechanism — wired directly into shell/face topology.
open_sh = f.open_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f._emit_raw(f"MANIFOLD_SOLID_BREP('tsh001_msb',#{open_sh.eid})")

f.add_product_chain(msb)
