"""Tsh221 — context_null_initialize.

Catalog claim: Multiple Perform() calls reuse stale context; accumulated reshape
operations apply twice. Stale context state causes double-fixing of face
orientations.

Mechanism IS the shell structure: TWO ADVANCED_FACEs with MISORIENTED normals
(same_sense=False on both) in an OPEN_SHELL IS the defect trigger. When
Perform() is called twice without re-initializing context, the second call
re-applies FixFaceOrientation on already-fixed faces. The two misoriented faces
ARE the reshape targets; double-application flips them back to wrong orientation.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh221",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs both having same_sense=False IS the context_null_initialize trigger; "
        "face A IS a unit-square at Z=0 with same_sense=False — IS the first misoriented face; "
        "face B IS a unit-square at Z=1 with same_sense=False — IS the second misoriented face; "
        "both faces share vertical edges (A top/B bottom) — IS the connected topology; "
        "first Perform() call: FixFaceOrientation fixes face A to same_sense=True, face B to same_sense=True — IS correct fix; "
        "context accumulates reshape map from first Perform() — IS the stale-context state; "
        "second Perform() call reuses stale context without null-initialize — IS the context_null_initialize defect; "
        "stale reshape map re-applies to already-fixed faces: face A flips back to same_sense=False — IS the double-fix; "
        "face B also re-flipped — IS the double-fixing outcome; "
        "fix: Perform() must null-initialize (clear) context before each call; "
        "emit E_CONTEXT_NULL_INITIALIZE when stale reshape map detected on Perform() re-entry"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Bottom face corners (Z=0)
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

# Top face corners (Z=1)
p00t = cp(0, 0, 1); v00t = f.vertex_point(p00t)
p10t = cp(1, 0, 1); v10t = f.vertex_point(p10t)
p11t = cp(1, 1, 1); v11t = f.vertex_point(p11t)
p01t = cp(0, 1, 1); v01t = f.vertex_point(p01t)

# Bottom face edges (Z=0)
eA_s = led(v00,  v10,  p00,   1,  0, 0)
eA_e = led(v10,  v11,  p10,   0,  1, 0)
eA_n = led(v11,  v01,  p11,  -1,  0, 0)
eA_w = led(v01,  v00,  p01,   0, -1, 0)

# Top face edges (Z=1)
eB_s = led(v00t, v10t, p00t,  1,  0, 0)
eB_e = led(v10t, v11t, p10t,  0,  1, 0)
eB_n = led(v11t, v01t, p11t, -1,  0, 0)
eB_w = led(v01t, v00t, p01t,  0, -1, 0)

# Face A — Z=0 plane, same_sense=False (misoriented) — IS the first reshape target
loop_A = f.edge_loop([
    f.oriented_edge(eA_s, True),
    f.oriented_edge(eA_e, True),
    f.oriented_edge(eA_n, True),
    f.oriented_edge(eA_w, True),
])
plane_A = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, -1), dir3(1, 0, 0)))
face_A = f.advanced_face([f.face_outer_bound(loop_A, orientation=True)], plane_A, same_sense=False)

# Face B — Z=1 plane, same_sense=False (misoriented) — IS the second reshape target
loop_B = f.edge_loop([
    f.oriented_edge(eB_s, True),
    f.oriented_edge(eB_e, True),
    f.oriented_edge(eB_n, True),
    f.oriented_edge(eB_w, True),
])
plane_B = f.plane(f.axis2_placement_3d(p00t, dir3(0, 0, -1), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=False)

# OPEN_SHELL: two misoriented faces — IS the stale-context double-fix mechanism
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
