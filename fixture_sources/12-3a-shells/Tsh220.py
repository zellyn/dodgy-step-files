"""Tsh220 — multiconnect_edge_loop_unbounded.

Catalog claim: Non-manifold shell with 3+ faces per edge; unbounded iteration
without complexity guard causes O(n²) behavior. Pathological mesh triggers hang.

Mechanism IS the shell structure: THREE ADVANCED_FACEs sharing a SINGLE COMMON
EDGE (3 faces incident on one edge) IS the non-manifold defect trigger.
isAccountMultiConex loop in FixFaceOrientation iterates over all incident faces
per edge without a complexity guard — IS the O(n²) unbounded path. The single
shared edge with 3 incident faces IS the pathological topology.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh220",
    defect=(
        "OPEN_SHELL with THREE ADVANCED_FACEs sharing a SINGLE COMMON EDGE IS the multiconnect_edge_loop_unbounded trigger; "
        "the shared edge IS the central spine along X-axis from (0,0,0) to (1,0,0) — IS the multi-incident edge; "
        "face A IS a triangle in the XY-plane (Z=0, Y>0 side) — IS the first incident face; "
        "face B IS a triangle below the XY-plane (Z<0, Y=0) — IS the second incident face; "
        "face C IS a triangle above the XY-plane (Z>0, Y=0) — IS the third incident face; "
        "all three faces share the same EDGE_CURVE entity — IS the 3+ faces-per-edge topology; "
        "isAccountMultiConex loop iterates without bound over 3 incident faces — IS the O(n²) path; "
        "no complexity guard on iteration count — IS the unbounded-loop defect; "
        "fix: add complexity guard (face count per edge <= 2 manifold check) before isAccountMultiConex loop; "
        "emit E_MULTICONNECT_EDGE_LOOP_UNBOUNDED when edge has 3+ incident faces"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared spine edge along X from (0,0,0) to (1,0,0) — IS the multi-incident edge
p0 = cp(0, 0, 0); v0 = f.vertex_point(p0)
p1 = cp(1, 0, 0); v1 = f.vertex_point(p1)
e_spine = led(v0, v1, p0, 1, 0, 0)   # shared by all 3 faces — IS the 3+ incident edge

# Apex vertices — each face has its own apex (not shared with others)
pA = cp(0.5, 1, 0); vA = f.vertex_point(pA)   # face A apex, Y>0 plane
pB = cp(0.5, 0, -1); vB = f.vertex_point(pB)  # face B apex, Z<0
pC = cp(0.5, 0,  1); vC = f.vertex_point(pC)  # face C apex, Z>0

# Face A edges (triangle in XY plane, Y>0)
eA_left  = led(v0,  vA, p0,  0.5, 1, 0)
eA_right = led(vA,  v1, pA,  0.5,-1, 0)

# Face B edges (triangle below spine, Z<0)
eB_left  = led(v0,  vB, p0,  0.5, 0, -1)
eB_right = led(vB,  v1, pB,  0.5, 0,  1)

# Face C edges (triangle above spine, Z>0)
eC_left  = led(v0,  vC, p0,  0.5, 0, 1)
eC_right = led(vC,  v1, pC,  0.5, 0,-1)

# Face A — triangle using spine forward + own edges
loop_A = f.edge_loop([
    f.oriented_edge(e_spine, True),    # shared spine forward
    f.oriented_edge(eA_right, True),
    f.oriented_edge(eA_left,  False),
])
plane_A = f.plane(f.axis2_placement_3d(p0, dir3(0, 0, 1), dir3(1, 0, 0)))
face_A = f.advanced_face([f.face_outer_bound(loop_A, orientation=True)], plane_A, same_sense=True)

# Face B — triangle using spine forward
loop_B = f.edge_loop([
    f.oriented_edge(e_spine, True),    # same shared spine — IS the 2nd incident face
    f.oriented_edge(eB_right, True),
    f.oriented_edge(eB_left,  False),
])
plane_B = f.plane(f.axis2_placement_3d(p0, dir3(0, -1, 0), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=True)

# Face C — triangle using spine forward
loop_C = f.edge_loop([
    f.oriented_edge(e_spine, True),    # same shared spine — IS the 3rd incident face (non-manifold)
    f.oriented_edge(eC_right, True),
    f.oriented_edge(eC_left,  False),
])
plane_C = f.plane(f.axis2_placement_3d(p0, dir3(0, 1, 0), dir3(1, 0, 0)))
face_C = f.advanced_face([f.face_outer_bound(loop_C, orientation=True)], plane_C, same_sense=True)

# OPEN_SHELL: three faces sharing one edge — IS the non-manifold multiconnect trigger
shell = f.open_shell([face_A, face_B, face_C])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
