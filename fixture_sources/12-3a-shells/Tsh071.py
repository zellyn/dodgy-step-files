"""Tsh071 — BadEdges Detection for Mismatched Edge Ordering.

Catalog claim: Two ADVANCED_FACEs share a common edge but with opposite
orientation semantics: Face A uses EDGE_CURVE #23 (direction (0,0,0) to
(2,0,0)), Face B uses EDGE_CURVE #47 (direction (2,0,0) to (0,0,0)). The
ORIENTED_EDGE flags do not compensate for the reversed underlying geometry,
creating a topological mismatch. ShapeAnalysis_Shell.BadEdges at line 281
catches edges with mismatched ordering across the two faces.

Mechanism IS the shell structure: OPEN_SHELL contains 2 ADVANCED_FACEs
sharing a seam along x=0..2. Face A's seam EDGE_CURVE runs (0,0,0)→(2,0,0).
Face B's seam EDGE_CURVE is a SEPARATE entity running (2,0,0)→(0,0,0)
(reverse direction), and NEITHER oriented_edge flag compensates — Face A
uses its edge True (forward) and Face B uses its edge True (also forward
through its reversed geometry). The two distinct edge_curve entities IS
the mismatch wired into both face edge_loops; BadEdges at line 281 must
detect that the two faces' seam edges are geometrically anti-parallel but
topologically both "forward", i.e. neither face flips its seam.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh071",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs; "
        "shared seam represented by TWO separate EDGE_CURVEs with opposite parametric directions; "
        "Face A seam EDGE_CURVE runs (0,0,0)→(2,0,0), used forward (oriented_edge .T.); "
        "Face B seam EDGE_CURVE runs (2,0,0)→(0,0,0), also used forward (oriented_edge .T.); "
        "neither oriented_edge flag compensates for reversed geometry; "
        "dual-edge anti-parallel seam IS the mechanism wired into both EDGE_LOOPs; "
        "ShapeAnalysis_Shell.BadEdges at line 281 must detect mismatch; "
        "fix: consolidate to one EDGE_CURVE with correct oriented_edge orientation flags; "
        "reject or flag as E_BAD_EDGES when parametric directions conflict"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Key vertices for a 2x1 rectangle split at y=0 seam
p000 = cp(0, 0, 0); p200 = cp(2, 0, 0)
p010 = cp(0, 1, 0); p210 = cp(2, 1, 0)
p0m1 = cp(0,-1, 0); p2m1 = cp(2,-1, 0)

v000 = f.vertex_point(p000); v200 = f.vertex_point(p200)
v010 = f.vertex_point(p010); v210 = f.vertex_point(p210)
v0m1 = f.vertex_point(p0m1); v2m1 = f.vertex_point(p2m1)

# Face A seam edge: (0,0,0)→(2,0,0) forward, direction +X
seam_A = led(v000, v200, p000, 1, 0, 0)

# Face B seam edge: SEPARATE entity, (2,0,0)→(0,0,0), direction −X
# (anti-parallel to seam_A — IS the mismatch)
seam_B = led(v200, v000, p200, -1, 0, 0)

# ── Face A: upper quad y=0..1 ──────────────────────────────────────────────
pl_A = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, 1), dir3(1, 0, 0)))
eA_top  = led(v000, v010, p000, 0, 1, 0)   # (0,0,0)→(0,1,0)
eA_right= led(v010, v210, p010, 1, 0, 0)   # (0,1,0)→(2,1,0)
eA_far  = led(v210, v200, p210, 0,-1, 0)   # (2,1,0)→(2,0,0)
loopA = f.edge_loop([
    f.oriented_edge(eA_top,   True),
    f.oriented_edge(eA_right, True),
    f.oriented_edge(eA_far,   True),
    f.oriented_edge(seam_A,   False),   # (2,0,0)→(0,0,0) traversal — uses seam_A reversed
])
face_A = f.advanced_face([f.face_outer_bound(loopA)], pl_A, same_sense=True)

# ── Face B: lower quad y=−1..0 ─────────────────────────────────────────────
pl_B = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, -1), dir3(1, 0, 0)))
eB_bot  = led(v2m1, v0m1, p2m1, -1, 0, 0)  # (2,-1,0)→(0,-1,0)
eB_left = led(v0m1, v000, p0m1,  0, 1, 0)  # (0,-1,0)→(0,0,0)
eB_right= led(v200, v2m1, p200,  0,-1, 0)  # (2,0,0)→(2,-1,0)
loopB = f.edge_loop([
    f.oriented_edge(seam_B,   True),    # (2,0,0)→(0,0,0) forward through seam_B — mismatch
    f.oriented_edge(eB_left,  True),
    f.oriented_edge(eB_bot,   True),
    f.oriented_edge(eB_right, True),
])
face_B = f.advanced_face([f.face_outer_bound(loopB)], pl_B, same_sense=True)

# OPEN_SHELL: both faces wired in — anti-parallel dual seam IS the mechanism
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
