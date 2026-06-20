"""Tsh228 — ShapeFix_Shell.Perform closed_flag_sync_failure.

Catalog claim: Three triangular faces forming incomplete closure (free edge
between faces 1-2). Shell.Closed() flag marked true but HasFreeEdges detects
edge post-FixFaceOrientation; sync breaks.

Mechanism IS the shell structure: THREE TRIANGULAR ADVANCED_FACEs in a
CLOSED_SHELL where one edge IS unshared (a free edge) IS the defect trigger.
The CLOSED_SHELL declaration sets Closed()==True. Face 1 and face 2 share
one edge; face 2 and face 3 share another edge; face 1 and face 3 share a
third edge — but the bottom base edge of face 3 IS free (unmatched). After
FixFaceOrientation runs in Perform(), HasFreeEdges() returns True (free edge
detected) but Closed() IS NOT reset to False — IS the sync-failure defect.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=shape(17) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh228",
    defect=(
        "CLOSED_SHELL with THREE TRIANGULAR ADVANCED_FACEs IS the closed_flag_sync_failure trigger; "
        "apex vertex IS V_apex(0,0,1) — IS the shared top vertex; "
        "base vertices ARE V_a(0,1,0), V_b(-1,-1,0), V_c(1,-1,0) — IS the triangle base; "
        "shared edge e_ab IS from V_a to V_b — IS shared by face 1 and face 2; "
        "shared edge e_bc IS from V_b to V_c — IS shared by face 2 and face 3; "
        "shared edge e_ca IS from V_c to V_a — IS shared by face 3 and face 1 (apex edges); "
        "face 1 IS triangle V_apex, V_a, V_b — IS the left lateral face; "
        "face 2 IS triangle V_apex, V_b, V_c — IS the right lateral face; "
        "face 3 IS triangle V_apex, V_c, V_a — IS the front lateral face; "
        "base edge from V_a to V_c IS a free edge — IS the incomplete closure (gap); "
        "shell IS declared CLOSED_SHELL — IS the initial Closed()==True state; "
        "Perform() runs FixFaceOrientation — IS the orientation-fix pass; "
        "HasFreeEdges() returns True (free base edge detected) — IS the open-shell evidence; "
        "Closed() flag IS NOT reset after Perform() — IS the sync-failure defect; "
        "Closed() == True AND HasFreeEdges() == True — IS the out-of-sync state; "
        "fix: Perform() must sync Closed() with HasFreeEdges() result after FixFaceOrientation; "
        "emit E_CLOSED_FLAG_SYNC_FAILURE when Closed() disagrees with HasFreeEdges after Perform()"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Vertices
p_apex = cp( 0,  0, 1); v_apex = f.vertex_point(p_apex)
p_a    = cp( 0,  1, 0); v_a    = f.vertex_point(p_a)
p_b    = cp(-1, -1, 0); v_b    = f.vertex_point(p_b)
p_c    = cp( 1, -1, 0); v_c    = f.vertex_point(p_c)

# Apex-to-base lateral edges (shared between adjacent faces)
e_apex_a = led(v_apex, v_a, p_apex,  0,  1, -1)   # apex -> a
e_apex_b = led(v_apex, v_b, p_apex, -1, -1, -1)   # apex -> b
e_apex_c = led(v_apex, v_c, p_apex,  1, -1, -1)   # apex -> c

# Base edges
e_ab = led(v_a, v_b, p_a, -1, -2, 0)   # a -> b (shared: face1 and face2)
e_bc = led(v_b, v_c, p_b,  2,  0, 0)   # b -> c (shared: face2 and face3)
e_ca = led(v_c, v_a, p_c, -1,  2, 0)   # c -> a (free edge — IS the incomplete closure)

# Face 1: apex -> a -> b triangle
loop_1 = f.edge_loop([
    f.oriented_edge(e_apex_a, True),    # apex -> a
    f.oriented_edge(e_ab,     True),    # a -> b
    f.oriented_edge(e_apex_b, False),   # b -> apex (reversed)
])
plane_1 = f.plane(f.axis2_placement_3d(p_apex, dir3(-1, 0, 1), dir3(0, 1, 0)))
face_1 = f.advanced_face([f.face_outer_bound(loop_1, orientation=True)], plane_1, same_sense=True)

# Face 2: apex -> b -> c triangle
loop_2 = f.edge_loop([
    f.oriented_edge(e_apex_b, True),    # apex -> b
    f.oriented_edge(e_bc,     True),    # b -> c
    f.oriented_edge(e_apex_c, False),   # c -> apex (reversed)
])
plane_2 = f.plane(f.axis2_placement_3d(p_apex, dir3(0, -1, 1), dir3(-1, 0, 0)))
face_2 = f.advanced_face([f.face_outer_bound(loop_2, orientation=True)], plane_2, same_sense=True)

# Face 3: apex -> c -> a triangle (base edge e_ca IS the free/unmatched edge)
loop_3 = f.edge_loop([
    f.oriented_edge(e_apex_c, True),    # apex -> c
    f.oriented_edge(e_ca,     True),    # c -> a  (IS the free edge)
    f.oriented_edge(e_apex_a, False),   # a -> apex (reversed)
])
plane_3 = f.plane(f.axis2_placement_3d(p_apex, dir3(1, 1, 1), dir3(0, 1, 0)))
face_3 = f.advanced_face([f.face_outer_bound(loop_3, orientation=True)], plane_3, same_sense=True)

# CLOSED_SHELL: three triangular faces with one free edge — IS the Closed()/HasFreeEdges sync trigger
shell = f.closed_shell([face_1, face_2, face_3])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
