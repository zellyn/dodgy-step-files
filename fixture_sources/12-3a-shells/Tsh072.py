"""Tsh072 — FreeEdges Detection for Non-Closed Shells.

Catalog claim: OPEN_SHELL containing two faces (quad + triangle) with only
partial edge overlap. Face 2 has three edges: one shared with Face 1 (the
shared edge), and two free edges (#45 and #49) that appear in only Face 2.
ShapeAnalysis_Shell.FreeEdges at line 303 detects these unshared edges,
which violate the closure invariant — every edge in a manifold shell must
be shared by exactly 2 faces.

Mechanism IS the shell structure: OPEN_SHELL contains 2 ADVANCED_FACEs.
Face 1 is a unit quad (4 edges); Face 2 is a right triangle sharing exactly
one EDGE_CURVE entity with Face 1 (the base edge at y=0, x=0..1). The two
remaining edges of Face 2 — the vertical leg and hypotenuse — are single-
incident: each appears in only one face's EDGE_LOOP. These two free EDGE_CURVEs
ARE the free-edge defect wired directly into Face 2's EDGE_LOOP and into no
other face. FreeEdges at line 303 must return compounds containing these two
unshared edges. Shell is non-closed and non-manifold.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh072",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs (unit quad + right triangle); "
        "one EDGE_CURVE IS shared between both faces (base edge x=0..1 at y=0); "
        "Face 2 has two further EDGE_CURVEs (vertical leg and hypotenuse) each in only one face; "
        "two single-incident free edges ARE directly wired into Face 2 EDGE_LOOP; "
        "free edges IS the mechanism violating manifold closure invariant; "
        "ShapeAnalysis_Shell.FreeEdges at line 303 must detect unshared edges; "
        "fix: reject as E_FREE_EDGES or flag shell as non-closed; "
        "every edge in a manifold shell must be shared by exactly 2 faces"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Vertices shared across faces
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)
p0m1= cp(0,-1, 0)   # apex of triangle below seam

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
v0m1= f.vertex_point(p0m1)

# ── Shared edge: (0,0,0)→(1,0,0) — appears in BOTH faces ──────────────────
shared_base = led(v00, v10, p00, 1, 0, 0)

# ── Face 1: unit quad (0,0,0)→(1,0,0)→(1,1,0)→(0,1,0) ────────────────────
pl_quad = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
eQ_right = led(v10, v11, p10,  0, 1, 0)
eQ_top   = led(v11, v01, p11, -1, 0, 0)
eQ_left  = led(v01, v00, p01,  0,-1, 0)
loopQ = f.edge_loop([
    f.oriented_edge(shared_base, True),
    f.oriented_edge(eQ_right,   True),
    f.oriented_edge(eQ_top,     True),
    f.oriented_edge(eQ_left,    True),
])
face_quad = f.advanced_face([f.face_outer_bound(loopQ)], pl_quad, same_sense=True)

# ── Face 2: right triangle (0,0,0)→(1,0,0)→(0,-1,0) ───────────────────────
# Shares shared_base (used reversed), plus two FREE edges
pl_tri = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, -1), dir3(1, 0, 0)))
# FREE edge 1: (1,0,0)→(0,-1,0) — hypotenuse, single-incident
eT_hyp  = led(v10, v0m1, p10, -1,-1, 0)
# FREE edge 2: (0,-1,0)→(0,0,0) — vertical leg, single-incident
eT_vert = led(v0m1, v00, p0m1,  0, 1, 0)
loopT = f.edge_loop([
    f.oriented_edge(shared_base, False),  # shared base traversed reversed
    f.oriented_edge(eT_hyp,     True),    # FREE edge — hypotenuse
    f.oriented_edge(eT_vert,    True),    # FREE edge — vertical leg
])
face_tri = f.advanced_face([f.face_outer_bound(loopT)], pl_tri, same_sense=True)

# OPEN_SHELL: free edges of face_tri ARE wired in, non-closure IS the mechanism
shell = f.open_shell([face_quad, face_tri])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
