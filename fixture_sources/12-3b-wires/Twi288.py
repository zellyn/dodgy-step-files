"""Twi288 — Non-convex "dart" pentagon outer wire / small triangle inner wire
share a common pinch vertex at the face centre (insurance second fixture for
seq-split-common-vertex; Twi009 covers a unit-square outer + small offset-
square inner — this fixture is untouched-Twi009, distinct geometry).

Catalog claim: Two wires of a face (an outer boundary and an inner hole)
share a single common VERTEX_POINT instance — a pinch point. Legal in a
BRep-internal representation, illegal in the STEP schema (each wire must own
distinct vertices), so the shared vertex must be split into per-wire copies
(ShapeFix_SplitCommonVertex, exposed as the `splitcommonvertex` ShapeProcess
operator).

This fixture's outer wire is a simple (non-self-intersecting) non-convex
5-vertex "dart": four vertices on a radius-5 circle, and the fifth pulled all
the way in to the face centre (0,0,0) — no zero-width spur, no duplicate
edges, just an ordinary concave polygon corner that happens to sit at the
same point the inner wire also uses. Geometrically and combinatorially
distinct from Twi009's unit-square / offset-square pair.

Mechanism IS the single VERTEX_POINT at (0,0,0) referenced by BOTH the dart
outer EDGE_LOOP (as one of its five ordinary corners) and the inner
triangle's EDGE_LOOP (as one of its three ordinary corners). The shared
VERTEX_POINT IS wired into EDGE_LOOPs -> FACE_OUTER_BOUND / FACE_BOUND -> one
ADVANCED_FACE in an OPEN_SHELL; never orphaned.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') >= 7
  - contains(b'(0.0,0.0,0.0)')

Tier-3 assertions:
  - n_edges_total >= 7
  - face[0].surface_type == "plane"
  - n_vertices_total >= 7

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi288",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP for a simple non-convex "
        "5-vertex dart: four corners on a radius-5 circle, the fifth pulled "
        "in to the centre (0,0,0); FACE_BOUND references an EDGE_LOOP for a "
        "small inner triangle (hole) with one corner ALSO at (0,0,0); "
        "one VERTEX_POINT entity (#v_shared at (0,0,0)) IS referenced by both "
        "the outer dart wire (as an ordinary concave corner) and the inner "
        "triangle wire (as an ordinary corner); "
        "distinct geometry from Twi009 (unit square outer / offset square "
        "inner, pinch at (0.5,0.5)) — same mechanism, different shape and "
        "pinch location; "
        "STEP requires per-wire distinct VERTEX_POINTs — sharing IS the "
        "defect; kernel must split shared vertex into per-wire copies or "
        "reject as malformed"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Shared vertex at the centre: IS the defect mechanism ─────────────────────
v_shared = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

def mk_line_edge(pa, pb, va, vb):
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln  = f.line(f.cartesian_point((pa[0], pa[1], 0.0)), vec)
    return f.edge_curve(va, vb, ln)

# ── Outer wire: non-convex "dart" — 4 corners on a radius-5 circle, the 5th
# corner (index 2) pulled all the way in to the centre (0,0,0) == v_shared.
# Vertex order keeps the polygon simple (no self-crossing). ──────────────────
ring_angles = [90, 162, None, 306, 18]  # degrees; None == the pulled-in corner
outer_pts = []
for i, ang in enumerate(ring_angles):
    if ang is None:
        outer_pts.append((0.0, 0.0))
    else:
        rad = math.radians(ang)
        outer_pts.append((5.0 * math.cos(rad), 5.0 * math.sin(rad)))

outer_v = []
for pt in outer_pts:
    if pt == (0.0, 0.0):
        outer_v.append(v_shared)
    else:
        outer_v.append(f.vertex_point(f.cartesian_point((pt[0], pt[1], 0.0))))

outer_oedges = []
N = len(outer_pts)
for i in range(N):
    e = mk_line_edge(outer_pts[i], outer_pts[(i + 1) % N],
                      outer_v[i], outer_v[(i + 1) % N])
    outer_oedges.append(f.oriented_edge(e, True))

outer_loop = f.edge_loop(outer_oedges)
fob = f.face_outer_bound(outer_loop)

# ── Inner wire: small triangle (hole) with one corner AT v_shared ────────────
tri_p1 = (-0.6, -0.3)
tri_p2 = (0.6, -0.3)
v_tri1 = f.vertex_point(f.cartesian_point((tri_p1[0], tri_p1[1], 0.0)))
v_tri2 = f.vertex_point(f.cartesian_point((tri_p2[0], tri_p2[1], 0.0)))

e_tri0 = mk_line_edge((0.0, 0.0), tri_p1, v_shared, v_tri1)
e_tri1 = mk_line_edge(tri_p1, tri_p2, v_tri1, v_tri2)
e_tri2 = mk_line_edge(tri_p2, (0.0, 0.0), v_tri2, v_shared)

inner_loop = f.edge_loop([
    f.oriented_edge(e_tri0, True),
    f.oriented_edge(e_tri1, True),
    f.oriented_edge(e_tri2, True),
])
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
