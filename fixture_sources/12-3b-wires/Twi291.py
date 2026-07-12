"""Twi291 — Two ADJACENT edges in one wire whose shared corner is encoded as
two distinct VERTEX_POINTs coincident WITHIN TOLERANCE (not bit-identical).
Twi017 covers the single-edge start/end case (one EDGE_CURVE, closed CIRCLE,
two distinct vertices at IDENTICAL coordinates); this fixture is the
multi-edge adjacent-corner case, at a small but nonzero coordinate offset.

Catalog claim: Two distinct STEP vertex entities used within the same wire —
here, the endpoints two adjacent edges are each supposed to share at their
common corner — turn out to be geometrically coincident within tolerance even
though STEP declared them as separate entities. StepToTopoDS_
TranslateEdgeLoop::Init detects that adjacent oriented edges don't reference
a shared vertex entity but their translated points coincide (within
tolerance) -> rebinds one to the other ("Adjacent edges do not have common
vertex; set confused"), keeping the wire connected.

Mechanism IS the pair of VERTEX_POINT entities at the corner between edge 3
and edge 4 of a hexagonal wire: #v3b (end of edge 3) at (2.5,4.330127,0.0)
and #v4a (start of edge 4) at (2.50000001,4.33012701,0.0) — offset by 1e-8 in
each coordinate, well within the file's declared 1e-7 uncertainty, but two
genuinely DISTINCT VERTEX_POINT entities (not the same reference). The rest
of the hexagon uses ordinary single-entity-per-corner vertices. Both
VERTEX_POINTs ARE wired into EDGE_CURVEs inside one EDGE_LOOP ->
FACE_OUTER_BOUND -> ADVANCED_FACE in an OPEN_SHELL; never orphaned.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') >= 7
  - contains(b'1.0E-07')

Tier-3 assertions:
  - n_edges_total >= 6
  - face[0].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi291",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP for a regular hexagon "
        "(radius 5) wire; the corner between edge 3 and edge 4 IS split "
        "across two DISTINCT VERTEX_POINT entities — #v3b (end of edge 3) at "
        "(2.5,4.330127,0.0) and #v4a (start of edge 4) at "
        "(2.50000001,4.33012701,0.0) — offset by 1e-8 in each coordinate, "
        "well within the declared UNCERTAINTY_MEASURE_WITH_UNIT of 1e-7, but "
        "never unified into one entity; "
        "two adjacent edges whose shared corner uses near-coincident-but-"
        "distinct VERTEX_POINTs (within tolerance, not bit-identical) IS the "
        "mechanism; StepToTopoDS_TranslateEdgeLoop::Init must detect the "
        "within-tolerance coincidence between adjacent edges' translated "
        "vertex points and rebind one vertex to the other so the wire stays "
        "connected, or leave the gap as an unresolved connectivity break if "
        "unrepairable; "
        "both VERTEX_POINTs ARE wired into EDGE_CURVE, EDGE_LOOP, "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL — never orphaned"
    ),
)

# ── Global uncertainty context: 1e-7, matching the 1e-8 offset being well
# within tolerance. ───────────────────────────────────────────────────────
unc_entity = f._emit_raw(
    "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-07),#*,"
    "'distance_accuracy_value','')"
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def mk_line_edge(pa, pb, va, vb):
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln  = f.line(f.cartesian_point((pa[0], pa[1], 0.0)), vec)
    return f.edge_curve(va, vb, ln)

# ── Regular hexagon corners (radius 5) ───────────────────────────────────────
N = 6
R = 5.0
hex_pts = [(R * math.cos(2 * math.pi * i / N), R * math.sin(2 * math.pi * i / N))
           for i in range(N)]
hex_v = [f.vertex_point(f.cartesian_point((px, py, 0.0))) for px, py in hex_pts]

# DEFECT: split the corner between edge3 (ends at hex_pts[3]) and edge4
# (starts at hex_pts[3]) into two distinct, near-coincident VERTEX_POINTs.
px3, py3 = hex_pts[3]
v3b = f.vertex_point(f.cartesian_point((px3, py3, 0.0)))                 # end of edge 3
v4a = f.vertex_point(f.cartesian_point((px3 + 1e-8, py3 + 1e-8, 0.0)))   # start of edge 4 — DISTINCT, near-coincident

# Explicit per-edge construction: edges 0,1 ordinary; edge2 ends at v3b;
# edge3 starts at v4a (the DEFECT gap) and continues ordinarily; edges 4,5
# ordinary, edge5 closes back to hex_v[0].
e0 = mk_line_edge(hex_pts[0], hex_pts[1], hex_v[0], hex_v[1])
e1 = mk_line_edge(hex_pts[1], hex_pts[2], hex_v[1], hex_v[2])
e2 = mk_line_edge(hex_pts[2], hex_pts[3], hex_v[2], v3b)
e3 = mk_line_edge(hex_pts[3], hex_pts[4], v4a, hex_v[4])
e4 = mk_line_edge(hex_pts[4], hex_pts[5], hex_v[4], hex_v[5])
e5 = mk_line_edge(hex_pts[5], hex_pts[0], hex_v[5], hex_v[0])

loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    f.oriented_edge(e4, True), f.oriented_edge(e5, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
