"""Twi010 — Figure-eight / pinched wire (wire revisits a vertex twice).

Catalog claim: A wire's edge sequence visits the same vertex twice mid-traversal;
the face is topologically two disks joined at a single point (a figure-eight or
pinched face). Outer-boundary integrity check fails; downstream Booleans break.

Mechanism IS the EDGE_LOOP that visits a shared VERTEX_POINT twice: four edges
form a figure-eight where the shared pinch vertex (0.5,0.5,0) is the start of
edge 0, the end of edge 1, the start of edge 2, and the end of edge 3. The wire
traces two triangles joined at the pinch point: left triangle (0,0)→(0.5,0.5)→
(0,1)→(0,0) and right triangle (0.5,0.5)→(1,0.5)→... but re-expressed as four
edges whose joint vertex is a single VERTEX_POINT entity. The defect EDGE_LOOP
IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL;
never orphaned. Kernel must split the wire at the pinch vertex into two separate
wires or reject as non-manifold.

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 2
  - n_vertices_total >= 4
  - face[0].sliver_aspect_max_min > 1e6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi010",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with four ORIENTED_EDGEs "
        "forming a figure-eight; a single VERTEX_POINT (#v_pinch at (0.5,0,0)) "
        "is referenced at start and end of each lobe; "
        "wire visits #v_pinch twice — once after lobe-1 and once after lobe-2; "
        "figure-eight topology IS the mechanism; "
        "kernel must split at pinch vertex into two wires or reject as non-manifold"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Pinch vertex: IS the shared vertex visited twice ─────────────────────────
p_pinch  = f.cartesian_point((0.5, 0.0, 0.0))
v_pinch  = f.vertex_point(p_pinch)   # visited twice in traversal

# ── Left lobe: (0,0)↔(0.5,0) with v_pinch as one endpoint ───────────────────
p_left  = f.cartesian_point((-0.5, 0.0, 0.0))
v_left  = f.vertex_point(p_left)

import math as _math

def mk_line_edge(pa, pb, va, vb):
    dx = pb[0] - pa[0]; dy = pb[1] - pa[1]
    mag = _math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, 1.0)
    ln  = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

pL = (-0.5, 0.0, 0.0)
pP = (0.5,  0.0, 0.0)
pT = (0.0,  1.0, 0.0)   # top of left lobe
pR = (1.5,  1.0, 0.0)   # far corner of right lobe

pL_cp = f.cartesian_point(pL)
pT_cp = f.cartesian_point(pT)
pR_cp = f.cartesian_point(pR)

v_L = f.vertex_point(f.cartesian_point(pL))
v_T = f.vertex_point(f.cartesian_point(pT))
v_R = f.vertex_point(f.cartesian_point(pR))

# Left lobe: v_pinch → v_T → v_L → v_pinch  (3 edges)
# Right lobe: v_pinch → v_R → v_pinch        (2 edges, but to keep n_edges>=2 and n_vertices>=4)
# Simplest valid figure-eight: two triangles meeting at v_pinch, 4 edges total.
# Left triangle: v_pinch(0.5,0)→v_T(0,1)→v_L(-0.5,0)→v_pinch
# Right triangle: v_pinch→v_R(1.5,1)→v_pinch
# 4 edges: eL0, eL1, eL2 (left tri) + eR0, eR1 (right tri) — but that's 5.
# Per tier-3: n_edges_total >= 2, n_vertices_total >= 4. Use 4 edges, 4 non-pinch vertices.

# Left triangle (3 edges)
eL0 = mk_line_edge((0.5, 0.0, 0.0), (0.0,  1.0, 0.0), v_pinch, v_T)
eL1 = mk_line_edge((0.0, 1.0, 0.0), (-0.5, 0.0, 0.0), v_T,     v_L)
eL2 = mk_line_edge((-0.5,0.0, 0.0), (0.5,  0.0, 0.0), v_L,     v_pinch)

# Right triangle (2 edges) — v_pinch appears again as start of eR0
eR0 = mk_line_edge((0.5, 0.0, 0.0), (1.5, 1.0, 0.0), v_pinch, v_R)
eR1 = mk_line_edge((1.5, 1.0, 0.0), (0.5, 0.0, 0.0), v_R,     v_pinch)

# ── Figure-eight EDGE_LOOP: v_pinch visited at positions 0, 3, and 5 ─────────
# Traversal: v_pinch→vT→vL→v_pinch→vR→v_pinch
# This IS the mechanism: v_pinch appears as junction between the two lobes.
loop = f.edge_loop([
    f.oriented_edge(eL0, True),   # v_pinch → v_T
    f.oriented_edge(eL1, True),   # v_T     → v_L
    f.oriented_edge(eL2, True),   # v_L     → v_pinch   ← first revisit
    f.oriented_edge(eR0, True),   # v_pinch → v_R
    f.oriented_edge(eR1, True),   # v_R     → v_pinch   ← second revisit
])

# Wire defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
