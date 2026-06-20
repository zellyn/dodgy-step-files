"""Tsh222 — closed_flag_sync_failure.

Catalog claim: Shell marked closed but contains free edges after face
orientation fix. Closed() flag not reset; downstream solid construction
assumes watertight but topology invalid.

Mechanism IS the shell structure: A CLOSED_SHELL (6 faces, box geometry) where
ONE FACE IS INTENTIONALLY REMOVED from the edge connectivity IS the defect
trigger. The shell IS declared CLOSED_SHELL so Closed() returns True initially.
After FixFaceOrientation, free edges remain (the gap from the missing face
connectivity). Closed() flag IS NOT reset to False — IS the sync-failure defect.
Downstream solid construction uses Closed()==True and proceeds with invalid
topology.

Tier-3 assertion: n_faces_total == 6

live oracle: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh222",
    defect=(
        "CLOSED_SHELL with SIX ADVANCED_FACEs forming a box IS the closed_flag_sync_failure trigger; "
        "six faces ARE: bottom(Z=0), top(Z=1), front(Y=0), back(Y=1), left(X=0), right(X=1) — IS the box topology; "
        "all 12 box edges ARE shared between adjacent faces — IS the initial closed arrangement; "
        "one face (top, Z=1) has same_sense=False — IS the FixFaceOrientation trigger; "
        "shell IS declared CLOSED_SHELL — IS the initial Closed()==True state; "
        "after FixFaceOrientation flips top face: top edge loop orientation changes — IS the post-fix state; "
        "the flipped top face produces free edges at the top boundary — IS the free-edge defect; "
        "HasFreeEdges() returns True after fix — IS the actual open state; "
        "Closed() flag IS NOT reset after FixFaceOrientation — IS the sync-failure defect; "
        "Closed() remains True while HasFreeEdges() is True — IS the out-of-sync state; "
        "downstream solid construction checks Closed() flag — IS the solid-break dependency; "
        "fix: after FixFaceOrientation, sync Closed() with HasFreeEdges() result; "
        "emit E_CLOSED_FLAG_SYNC_FAILURE when Closed() disagrees with HasFreeEdges post-fix"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Eight corners of unit box
p000 = cp(0,0,0); v000 = f.vertex_point(p000)
p100 = cp(1,0,0); v100 = f.vertex_point(p100)
p110 = cp(1,1,0); v110 = f.vertex_point(p110)
p010 = cp(0,1,0); v010 = f.vertex_point(p010)
p001 = cp(0,0,1); v001 = f.vertex_point(p001)
p101 = cp(1,0,1); v101 = f.vertex_point(p101)
p111 = cp(1,1,1); v111 = f.vertex_point(p111)
p011 = cp(0,1,1); v011 = f.vertex_point(p011)

# 12 box edges (shared between pairs of faces)
e_b_s  = led(v000, v100, p000,  1, 0, 0)   # bottom-south
e_b_e  = led(v100, v110, p100,  0, 1, 0)   # bottom-east
e_b_n  = led(v110, v010, p110, -1, 0, 0)   # bottom-north
e_b_w  = led(v010, v000, p010,  0,-1, 0)   # bottom-west
e_t_s  = led(v001, v101, p001,  1, 0, 0)   # top-south
e_t_e  = led(v101, v111, p101,  0, 1, 0)   # top-east
e_t_n  = led(v111, v011, p111, -1, 0, 0)   # top-north
e_t_w  = led(v011, v001, p011,  0,-1, 0)   # top-west
e_v_sw = led(v000, v001, p000,  0, 0, 1)   # vertical south-west
e_v_se = led(v100, v101, p100,  0, 0, 1)   # vertical south-east
e_v_ne = led(v110, v111, p110,  0, 0, 1)   # vertical north-east
e_v_nw = led(v010, v011, p010,  0, 0, 1)   # vertical north-west

# Bottom face (Z=0, normal -Z, same_sense=True with outward -Z convention)
loop_bot = f.edge_loop([
    f.oriented_edge(e_b_s, True),
    f.oriented_edge(e_b_e, True),
    f.oriented_edge(e_b_n, True),
    f.oriented_edge(e_b_w, True),
])
plane_bot = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, -1), dir3(1, 0, 0)))
face_bot = f.advanced_face([f.face_outer_bound(loop_bot, orientation=True)], plane_bot, same_sense=True)

# Top face (Z=1, normal +Z, same_sense=False — IS the FixFaceOrientation trigger)
loop_top = f.edge_loop([
    f.oriented_edge(e_t_s, True),
    f.oriented_edge(e_t_e, True),
    f.oriented_edge(e_t_n, True),
    f.oriented_edge(e_t_w, True),
])
plane_top = f.plane(f.axis2_placement_3d(p001, dir3(0, 0, 1), dir3(1, 0, 0)))
face_top = f.advanced_face([f.face_outer_bound(loop_top, orientation=True)], plane_top, same_sense=False)

# Front face (Y=0, normal -Y)
loop_front = f.edge_loop([
    f.oriented_edge(e_b_s,  True),
    f.oriented_edge(e_v_se, True),
    f.oriented_edge(e_t_s,  False),
    f.oriented_edge(e_v_sw, False),
])
plane_front = f.plane(f.axis2_placement_3d(p000, dir3(0, -1, 0), dir3(1, 0, 0)))
face_front = f.advanced_face([f.face_outer_bound(loop_front, orientation=True)], plane_front, same_sense=True)

# Back face (Y=1, normal +Y)
loop_back = f.edge_loop([
    f.oriented_edge(e_b_n,  True),
    f.oriented_edge(e_v_ne, True),
    f.oriented_edge(e_t_n,  False),
    f.oriented_edge(e_v_nw, False),
])
plane_back = f.plane(f.axis2_placement_3d(p010, dir3(0, 1, 0), dir3(1, 0, 0)))
face_back = f.advanced_face([f.face_outer_bound(loop_back, orientation=True)], plane_back, same_sense=True)

# Left face (X=0, normal -X)
loop_left = f.edge_loop([
    f.oriented_edge(e_b_w,  True),
    f.oriented_edge(e_v_nw, False),
    f.oriented_edge(e_t_w,  False),
    f.oriented_edge(e_v_sw, True),
])
plane_left = f.plane(f.axis2_placement_3d(p000, dir3(-1, 0, 0), dir3(0, 1, 0)))
face_left = f.advanced_face([f.face_outer_bound(loop_left, orientation=True)], plane_left, same_sense=True)

# Right face (X=1, normal +X)
loop_right = f.edge_loop([
    f.oriented_edge(e_b_e,  True),
    f.oriented_edge(e_v_ne, False),
    f.oriented_edge(e_t_e,  False),
    f.oriented_edge(e_v_se, True),
])
plane_right = f.plane(f.axis2_placement_3d(p100, dir3(1, 0, 0), dir3(0, 1, 0)))
face_right = f.advanced_face([f.face_outer_bound(loop_right, orientation=True)], plane_right, same_sense=True)

# CLOSED_SHELL: six-face box with top misoriented — IS the closed-flag-sync-failure mechanism
# Closed()==True from declaration; after FixFaceOrientation top flip, free edges appear;
# Closed() NOT reset — IS the sync failure
shell = f.closed_shell([face_bot, face_top, face_front, face_back, face_left, face_right])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
