"""Tsh070 — FixFaceOrientation Multiconnect-Edge Classification.

Catalog claim: Three ADVANCED_FACEs (xy-plane triangles, xz-plane triangle) share a
single edge (0,0,0)-(1,0,0), creating a multiconnect edge (3+ faces).
ShapeFix_Shell.FixFaceOrientation multiconnect-edge classification at line 1428 fails
to properly propagate orientation fixes when an edge connects more than 2 faces, making
orientation propagation ambiguous.

Mechanism IS the shell structure: OPEN_SHELL contains 3 ADVANCED_FACEs. One
EDGE_CURVE entity — the shared edge from (0,0,0) to (1,0,0) — IS directly wired into
all 3 faces' EDGE_LOOP topologies. Face A (xy-plane triangle) uses the shared edge
forward; Face B (xy-plane triangle, reversed winding) uses it reversed; Face C
(xz-plane triangle) uses it forward again. Triple-incident multiconnect-edge IS the
mechanism: with 3 faces on one edge, orientation propagation from any face leaves the
other two in an ambiguous state — FixFaceOrientation cannot choose a consistent
orientation for all three without additional constraints.

Byte assertions: (none explicit in catalog)

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh070",
    defect=(
        "OPEN_SHELL with 3 ADVANCED_FACEs; "
        "one EDGE_CURVE from (0,0,0) to (1,0,0) IS directly wired into all 3 EDGE_LOOPs; "
        "triple-incident multiconnect edge IS the mechanism; "
        "Face A (xy-plane triangle) uses shared edge forward; "
        "Face B (xy-plane triangle, flipped winding) uses it reversed; "
        "Face C (xz-plane triangle) uses it forward; "
        "3-face multiconnect makes orientation propagation ambiguous; "
        "FixFaceOrientation at line 1428 fails to propagate consistently; "
        "fix: reject non-manifold topology or apply special multiconnect-edge handling; "
        "unambiguous orientation propagation requires additional constraints"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Three key vertices
p000 = cp(0,0,0); p100 = cp(1,0,0)
p010 = cp(0,1,0)   # apex of xy-plane triangle A
p001 = cp(0,0,1)   # apex of xz-plane triangle C

v000 = f.vertex_point(p000)
v100 = f.vertex_point(p100)
v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001)

# Multiconnect shared edge: (0,0,0)→(1,0,0) — IS wired into all 3 face loops
shared_edge = led(v000, v100, p000, 1, 0, 0)   # forward direction

# ── Face A: xy-plane triangle (0,0,0)→(1,0,0)→(0,1,0) ───────────────────────
pl_xy = f.plane(f.axis2_placement_3d(p000, dir3(0,0,1), dir3(1,0,0)))
eA_diag = led(v100, v010, p100, -1, 1, 0)  # (1,0,0)→(0,1,0)
eA_left = led(v010, v000, p010,  0,-1, 0)  # (0,1,0)→(0,0,0)
loopA = f.edge_loop([
    f.oriented_edge(shared_edge, True),   # (0,0,0)→(1,0,0) — multiconnect face 1
    f.oriented_edge(eA_diag,    True),
    f.oriented_edge(eA_left,    True),
])
face_A = f.advanced_face([f.face_outer_bound(loopA)], pl_xy, same_sense=True)

# ── Face B: xy-plane triangle, reversed winding (same domain, opposite normal) ─
eB_left2 = led(v000, v010, p000, 0, 1, 0)  # (0,0,0)→(0,1,0)
eB_diag2 = led(v010, v100, p010, 1,-1, 0)  # (0,1,0)→(1,0,0)
loopB = f.edge_loop([
    f.oriented_edge(eB_left2,   True),
    f.oriented_edge(eB_diag2,   True),
    f.oriented_edge(shared_edge, False),  # (1,0,0)→(0,0,0) reversed — multiconnect face 2
])
face_B = f.advanced_face([f.face_outer_bound(loopB)], pl_xy, same_sense=False)

# ── Face C: xz-plane triangle (0,0,0)→(1,0,0)→(0,0,1) ───────────────────────
pl_xz = f.plane(f.axis2_placement_3d(p000, dir3(0,-1,0), dir3(1,0,0)))
eC_diag = led(v100, v001, p100, -1, 0, 1)  # (1,0,0)→(0,0,1)
eC_up   = led(v001, v000, p001,  0, 0,-1)  # (0,0,1)→(0,0,0)
loopC = f.edge_loop([
    f.oriented_edge(shared_edge, True),   # (0,0,0)→(1,0,0) — multiconnect face 3
    f.oriented_edge(eC_diag,    True),
    f.oriented_edge(eC_up,      True),
])
face_C = f.advanced_face([f.face_outer_bound(loopC)], pl_xz, same_sense=True)

# OPEN_SHELL: triple-incident shared_edge IS wired into all 3 face loops
shell = f.open_shell([face_A, face_B, face_C])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
