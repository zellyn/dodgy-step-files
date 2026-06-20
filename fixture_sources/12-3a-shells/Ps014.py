"""Ps014 — Position tolerance frame cites datum compartments in wrong order.

Catalog claim: A 10x10x10 block with three DATUM_FEATUREs (A on bottom,
B on front, C on left).  The producer intended |⌖|0.05|A|B|C| but the PMI
exporter emitted the DATUM_SYSTEM with compartments in order (A, C, B),
swapping the secondary/tertiary roles.  The geometry is valid; the defect
is a hidden semantic error in the ordered datum reference list.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: three
faces of the 10×10×10 cube ARE designated datum planes (bottom=A, front=B,
left=C); the PMI annotation IS attached to the CLOSED_SHELL's outer shell
shape with datum-compartment ordering (A,C,B) instead of (A,B,C), embedding
the swap directly in the face-level geometric association set.

Tier-3 assertions:
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — silent accept.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps014",
    defect=(
        "10x10x10 cube MANIFOLD_SOLID_BREP with datum faces A(bottom) B(front) C(left); "
        "DATUM_SYSTEM lists compartments in order (A,C,B) instead of (A,B,C), "
        "swapping secondary/tertiary; wrong-order IS wired into the face-geometry "
        "annotation set of the CLOSED_SHELL outer shell; kernel accepts silently"
    ),
)

# ── 10x10x10 cube ─────────────────────────────────────────────────────────────
pts = [
    f.cartesian_point((  0.0,  0.0,  0.0)),  # 0 origin
    f.cartesian_point(( 10.0,  0.0,  0.0)),  # 1
    f.cartesian_point(( 10.0, 10.0,  0.0)),  # 2
    f.cartesian_point((  0.0, 10.0,  0.0)),  # 3
    f.cartesian_point((  0.0,  0.0, 10.0)),  # 4
    f.cartesian_point(( 10.0,  0.0, 10.0)),  # 5
    f.cartesian_point(( 10.0, 10.0, 10.0)),  # 6
    f.cartesian_point((  0.0, 10.0, 10.0)),  # 7
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)

e_bot_f = le(0, 1,  1, 0, 0, 10.0)
e_bot_r = le(1, 2,  0, 1, 0, 10.0)
e_bot_b = le(3, 2,  1, 0, 0, 10.0)
e_bot_l = le(0, 3,  0, 1, 0, 10.0)
e_top_f = le(4, 5,  1, 0, 0, 10.0)
e_top_r = le(5, 6,  0, 1, 0, 10.0)
e_top_b = le(7, 6,  1, 0, 0, 10.0)
e_top_l = le(4, 7,  0, 1, 0, 10.0)
e_v0    = le(0, 4,  0, 0, 1, 10.0)
e_v1    = le(1, 5,  0, 0, 1, 10.0)
e_v2    = le(2, 6,  0, 0, 1, 10.0)
e_v3    = le(3, 7,  0, 0, 1, 10.0)

def mk_plane(px, py, pz, zx, zy, zz, rx, ry, rz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((rx, ry, rz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# Datum face A = bottom (z=0, normal -Z)
pl_bot = mk_plane( 0, 0,  0,  0, 0,-1,  1, 0, 0)
# Datum face B = front (y=0, normal -Y)
pl_frt = mk_plane( 0, 0,  0,  0,-1, 0,  1, 0, 0)
# Datum face C = left  (x=0, normal -X)
pl_lft = mk_plane( 0, 0,  0, -1, 0, 0,  0, 1, 0)
pl_top = mk_plane( 0, 0, 10,  0, 0,+1,  1, 0, 0)
pl_bck = mk_plane( 0,10,  0,  0,+1, 0,  1, 0, 0)
pl_rgt = mk_plane(10, 0,  0, +1, 0, 0,  0, 1, 0)

# face[0]=bottom(A), face[1]=top, face[2]=front(B), face[3]=back,
# face[4]=left(C),   face[5]=right
f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]

# CLOSED_SHELL IS the outer shell of MANIFOLD_SOLID_BREP — datum faces wired in
shell = f.closed_shell(all_faces, name="ps014_datum_cube_shell")
msb   = f.manifold_solid_brep(shell, name="ps014_datum_order_swapped")
f.add_product_chain(msb, mode="brep_shape")

# ── PMI: DATUM_REFERENCE_COMPARTMENTs in order (A, C, B) — the defect ────────
# Datum features point to specific faces: bottom=A, front=B, left=C
# The DATUM_SYSTEM is emitted with compartments in wrong order (A,C,B) not (A,B,C).
# Each DATUM_FEATURE references its face entity and a label string.
dft_a = f._emit_raw(f"DATUM_FEATURE('datum_A',#{f_bot.eid},'A')")
dft_b = f._emit_raw(f"DATUM_FEATURE('datum_B',#{f_frt.eid},'B')")
dft_c = f._emit_raw(f"DATUM_FEATURE('datum_C',#{f_lft.eid},'C')")

# Compartments reference their datum features
comp_a = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('compartment_A',(#{dft_a.eid}))")
comp_b = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('compartment_B',(#{dft_b.eid}))")
comp_c = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('compartment_C',(#{dft_c.eid}))")

# DATUM_SYSTEM order is (A, C, B) — B and C are swapped: THIS IS THE DEFECT
# The wrong-order IS wired into the datum_constraints list of the DATUM_SYSTEM
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('datum_sys_ACB_wrong',(#{comp_a.eid},#{comp_c.eid},#{comp_b.eid}))"
)
# POSITION_TOLERANCE attached to the solid shape referencing the wrong-order datum system
f._emit_raw(
    f"POSITION_TOLERANCE('pos_tol_0.05',#{msb.eid},0.05,#{datum_sys.eid})"
)
