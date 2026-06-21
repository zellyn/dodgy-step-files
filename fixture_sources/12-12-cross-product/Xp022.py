"""Xp022 — Time-bomb tolerance × negative-radius torus × cyclic seam edge."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp022",
             defect='Negative torus major_radius x tolerance-boundary tiny seam edge x seam doubled in loop')

# Defect 1: TOROIDAL_SURFACE with negative major_radius
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
torus = f.toroidal_surface(plc, -10.0, 1.0)  # negative major_radius

# Defect 2: seam edge with 3D length = 1e-7 (exactly at Precision::Confusion boundary)
# The two endpoints differ by exactly 1e-7
p_seam0 = f.cartesian_point((9.0, 0.0, 0.0))
p_seam1 = f.cartesian_point((9.0 + 1.0e-7, 0.0, 0.0))  # 1e-7 away — at tolerance boundary
p_other0 = f.cartesian_point((0.0, 9.0, 0.0))
p_other1 = f.cartesian_point((0.0, 9.0, 1.0))

v_s0 = f.vertex_point(p_seam0)
v_s1 = f.vertex_point(p_seam1)
v_o0 = f.vertex_point(p_other0)
v_o1 = f.vertex_point(p_other1)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = max((dx**2 + dy**2 + dz**2) ** 0.5, 1e-15)
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Seam edge: 1e-7 long (at tolerance boundary)
e_seam   = line_edge(p_seam0, p_seam1, v_s0, v_s1)
e_other0 = line_edge(p_seam1, p_other0, v_s1, v_o0)
e_other1 = line_edge(p_other0, p_other1, v_o0, v_o1)
e_back   = line_edge(p_other1, p_seam0, v_o1, v_s0)

# Defect 3: seam edge appears twice in loop (once fwd, once rev) — cyclic seam
loop = f.edge_loop([
    f.oriented_edge(e_seam, True),    # seam forward
    f.oriented_edge(e_other0, True),
    f.oriented_edge(e_seam, False),   # seam reversed — appears twice (cyclic)
    f.oriented_edge(e_other1, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
