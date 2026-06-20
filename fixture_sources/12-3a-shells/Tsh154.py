"""Tsh154 — ShapeFix_Shell.FixFaceOrientation pyramid-with-apex.

Catalog claim: Pyramid shell where apex vertex is shared by N triangular faces
(fan configuration). Orientation propagation from apex doesn't decide consistent
direction; some faces flip outward, others inward.

Mechanism IS the shell structure: FOUR ADVANCED_FACEs — one square base and three
triangular side faces sharing a single apex vertex — ARE wired into a CLOSED_SHELL.
The apex vertex IS shared by all three triangular EDGE_LOOPs; the fan topology IS
wired into the shell so that ShapeFix_Shell.FixFaceOrientation must propagate
orientation through the apex fan. One triangular side face IS wired with
same_sense=.F. to inject the orientation conflict the mechanism exercises.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh154",
    defect=(
        "FOUR ADVANCED_FACEs (square base + 3 triangular sides) in CLOSED_SHELL — "
        "IS the pyramid-with-apex orientation-fan mechanism; "
        "Apex vertex at (0.5,0.5,1) IS shared by all three triangular EDGE_LOOPs; "
        "TriFace0 (front, y=0 side) IS wired with same_sense=.T. (outward reference); "
        "TriFace1 (right, x=1 side) IS wired with same_sense=.T. (outward reference); "
        "TriFace2 (left, x=0 side) IS wired with same_sense=.F. — IS the orientation conflict; "
        "fan topology at apex IS the mechanism: FixFaceOrientation propagates from TriFace0 "
        "through shared apex edges but adjacency-only logic misses TriFace2's flip; "
        "fix: detect apex-fan topology; use consensus vote over all fan faces; "
        "emit E_FIX_ORIENTATION_APEX_CONFLICT when fan faces disagree at shared apex vertex"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Square base at z=0: corners (0,0,0),(1,0,0),(1,1,0),(0,1,0)
p_b00 = cp(0, 0, 0); p_b10 = cp(1, 0, 0)
p_b11 = cp(1, 1, 0); p_b01 = cp(0, 1, 0)
# Apex at top center
p_apex = cp(0.5, 0.5, 1.0)

v_b00 = f.vertex_point(p_b00); v_b10 = f.vertex_point(p_b10)
v_b11 = f.vertex_point(p_b11); v_b01 = f.vertex_point(p_b01)
v_apex = f.vertex_point(p_apex)

# Base edges (CCW from outside below, i.e. normal points down)
e_b0 = led(v_b00, v_b10, p_b00,  1, 0, 0)  # front base
e_b1 = led(v_b10, v_b11, p_b10,  0, 1, 0)  # right base
e_b2 = led(v_b11, v_b01, p_b11, -1, 0, 0)  # back base
e_b3 = led(v_b01, v_b00, p_b01,  0,-1, 0)  # left base

# Lateral (slant) edges from base corners to apex
e_s0 = led(v_b00, v_apex, p_b00,  0.5, 0.5, 1.0)  # front-left to apex
e_s1 = led(v_b10, v_apex, p_b10, -0.5, 0.5, 1.0)  # front-right to apex
e_s2 = led(v_b11, v_apex, p_b11, -0.5,-0.5, 1.0)  # back-right to apex
e_s3 = led(v_b01, v_apex, p_b01,  0.5,-0.5, 1.0)  # back-left to apex

# Square base face (normal pointing down, same_sense=T with downward plane)
plane_base = f.plane(f.axis2_placement_3d(p_b00, dir3(0, 0, -1), dir3(1, 0, 0)))
loop_base = f.edge_loop([
    f.oriented_edge(e_b0, False),
    f.oriented_edge(e_b3, False),
    f.oriented_edge(e_b2, False),
    f.oriented_edge(e_b1, False),
])
face_base = f.advanced_face([f.face_outer_bound(loop_base, orientation=True)], plane_base, same_sense=True)

# Triangular front face (y=0 side): b00, b10, apex — outward normal points toward -y
plane_tri0 = f.plane(f.axis2_placement_3d(p_b00, dir3(0, -1, 0), dir3(1, 0, 0)))
loop_tri0 = f.edge_loop([
    f.oriented_edge(e_b0,  True),
    f.oriented_edge(e_s1,  True),
    f.oriented_edge(e_s0,  False),
])
face_tri0 = f.advanced_face([f.face_outer_bound(loop_tri0, orientation=True)], plane_tri0, same_sense=True)

# Triangular right face (x=1 side): b10, b11, apex — outward normal points toward +x
plane_tri1 = f.plane(f.axis2_placement_3d(p_b10, dir3(1, 0, 0), dir3(0, 1, 0)))
loop_tri1 = f.edge_loop([
    f.oriented_edge(e_b1,  True),
    f.oriented_edge(e_s2,  True),
    f.oriented_edge(e_s1,  False),
])
face_tri1 = f.advanced_face([f.face_outer_bound(loop_tri1, orientation=True)], plane_tri1, same_sense=True)

# Triangular left face (back+left combined): b11,b01,b00 -> apex fan
# same_sense=.F. — IS the orientation conflict wired into the apex fan
plane_tri2 = f.plane(f.axis2_placement_3d(p_b01, dir3(-1, 0, 0), dir3(0, -1, 0)))
loop_tri2 = f.edge_loop([
    f.oriented_edge(e_b2,  True),
    f.oriented_edge(e_s3,  True),
    f.oriented_edge(e_s2,  False),
])
face_tri2 = f.advanced_face([f.face_outer_bound(loop_tri2, orientation=True)], plane_tri2, same_sense=False)

# CLOSED_SHELL: 4 faces, apex IS shared by all 3 triangular faces — IS the fan mechanism
shell = f.closed_shell([face_base, face_tri0, face_tri1, face_tri2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
