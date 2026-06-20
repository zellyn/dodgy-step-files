"""Tsh225 — ShapeFix_Shell.FixFaceOrientation multiconnect_edge_loop_unbounded.

Catalog claim: Three triangular faces meeting at shared central edge
(non-manifold, 3+ incident). isAccountMultiConex loop iterates without bound
on pathological mesh; O(n^2) complexity pathological behavior.

Mechanism IS the shell structure: THREE TRIANGULAR ADVANCED_FACEs sharing ONE
COMMON EDGE (non-manifold) in an OPEN_SHELL IS the defect trigger. The shared
central edge IS incident to all three triangular faces simultaneously — IS the
3+ face incidence (non-manifold edge). isAccountMultiConex iterates over all
edge-incident faces to resolve orientation; with 3 incident faces the loop
processes O(n^2) combinations without termination bound — IS the unbounded
iteration defect.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=shape(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh225",
    defect=(
        "OPEN_SHELL with THREE TRIANGULAR ADVANCED_FACEs sharing a central edge IS the multiconnect_edge_loop_unbounded trigger; "
        "shared central edge runs from V_origin(0,0,0) to V_top(0,0,1) — IS the non-manifold edge; "
        "face A IS a triangle: V_origin, V_top, V_right(1,0,0) — IS the first incident face; "
        "face B IS a triangle: V_origin, V_top, V_front(0,1,0) — IS the second incident face; "
        "face C IS a triangle: V_origin, V_top, V_left(-1,0,0) — IS the third incident face; "
        "central edge IS incident to all three faces — IS the 3+ face non-manifold incidence; "
        "isAccountMultiConex detects 3 incident faces on central edge — IS the multi-connect detection; "
        "isAccountMultiConex loop iterates over all (face-pair) combinations — IS the O(n^2) iteration; "
        "loop has no termination bound for 3+ incident faces — IS the unbounded-iteration defect; "
        "pathological mesh with more incident faces causes progressively worse O(n^2) behavior; "
        "fix: isAccountMultiConex must cap iterations or use linear scan; "
        "emit E_MULTICONNECT_EDGE_LOOP_UNBOUNDED when edge has 3+ incident faces during FixFaceOrientation"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared vertices
p_orig  = cp( 0, 0, 0); v_orig  = f.vertex_point(p_orig)
p_top   = cp( 0, 0, 1); v_top   = f.vertex_point(p_top)
p_right = cp( 1, 0, 0); v_right = f.vertex_point(p_right)
p_front = cp( 0, 1, 0); v_front = f.vertex_point(p_front)
p_left  = cp(-1, 0, 0); v_left  = f.vertex_point(p_left)

# Shared central edge (non-manifold — IS shared by all three faces)
e_central = led(v_orig, v_top, p_orig, 0, 0, 1)

# Per-face outer edges (each face IS a triangle sharing the central edge)
# Face A: V_orig -> V_top -> V_right -> V_orig
e_A_tr = led(v_top,   v_right, p_top,   1,  0, -1)
e_A_ro = led(v_right, v_orig,  p_right,-1,  0,  0)

# Face B: V_orig -> V_top -> V_front -> V_orig
e_B_tf = led(v_top,   v_front, p_top,   0,  1, -1)
e_B_fo = led(v_front, v_orig,  p_front, 0, -1,  0)

# Face C: V_orig -> V_top -> V_left -> V_orig
e_C_tl = led(v_top,  v_left,  p_top,  -1,  0, -1)
e_C_lo = led(v_left, v_orig,  p_left,  1,  0,  0)

# Face A — triangle in X-Z plane (Y=0 side)
loop_A = f.edge_loop([
    f.oriented_edge(e_central, True),   # orig -> top
    f.oriented_edge(e_A_tr,    True),   # top  -> right
    f.oriented_edge(e_A_ro,    True),   # right-> orig
])
plane_A = f.plane(f.axis2_placement_3d(p_orig, dir3(0, -1, 0), dir3(1, 0, 0)))
face_A = f.advanced_face([f.face_outer_bound(loop_A, orientation=True)], plane_A, same_sense=True)

# Face B — triangle in Y-Z plane (X=0 side)
loop_B = f.edge_loop([
    f.oriented_edge(e_central, True),   # orig -> top
    f.oriented_edge(e_B_tf,    True),   # top  -> front
    f.oriented_edge(e_B_fo,    True),   # front-> orig
])
plane_B = f.plane(f.axis2_placement_3d(p_orig, dir3(1, 0, 0), dir3(0, 1, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=True)

# Face C — triangle in negative-X/Z plane
loop_C = f.edge_loop([
    f.oriented_edge(e_central, True),   # orig -> top
    f.oriented_edge(e_C_tl,    True),   # top  -> left
    f.oriented_edge(e_C_lo,    True),   # left -> orig
])
plane_C = f.plane(f.axis2_placement_3d(p_orig, dir3(0, 1, 0), dir3(-1, 0, 0)))
face_C = f.advanced_face([f.face_outer_bound(loop_C, orientation=True)], plane_C, same_sense=True)

# OPEN_SHELL: three triangular faces with shared non-manifold central edge
# IS the isAccountMultiConex unbounded-iteration trigger
shell = f.open_shell([face_A, face_B, face_C])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
