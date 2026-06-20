"""Twi204 — ShapeFix_Wire.FixIntersectingEdges 3-edges-at-vertex.

Catalog claim: Three edges meeting at a single point (star configuration).
FixIntersectingEdges pairwise comparison reports 3 intersections at the same
point but they're vertex contact, not crossings.

Mechanism: The wire forms a triangle (V0→V1→V2→V0). Three edges meet pairwise
at three distinct vertices — but the DEFECT is that all three vertices are the
same 3D point (0,0,0). V0, V1, V2 are all at the origin. This creates a "star"
where every edge touches every other edge at the shared origin point.
FixIntersectingEdges runs pairwise intersection checks on all edge pairs.
For each pair (E0,E1), (E0,E2), (E1,E2) it finds the common origin point and
reports three intersection events, all at (0,0,0). But these are vertex-contact
events (edges share endpoints), not transverse crossings. The pairwise check
cannot distinguish vertex-shared contact from geometric self-intersection,
resulting in false intersection reports.

Wire topology on PLANE (normal +Z) — star configuration:
  V0 = (0, 0, 0)   ← shared "hub" point (also V1 and V2 are coincident)
  V1 = (0, 0, 0)   ← coincident with V0
  V2 = (0, 0, 0)   ← coincident with V0
  E0: V0 → V1 along X: (0,0,0) → (10,0,0) → back to (0,0,0)  [LINE then return]
  ...

Actually the catalog says "three edges meeting at single point". Let us
encode it as: three edges of a triangle whose three apex-vertices all happen
to be at the same point — i.e., a degenerate triangle collapsed to a star.

Cleaner encoding: three edges each starting and ending at the same point (0,0,0),
going out to (10,0,0), (0,10,0), (-10,0,0) and back — but that's 6 oriented
edges.

Instead: encode as a genuine triangle with distinct geometry but all vertices
at (0,0,0) — creating a "star" where every edge endpoint is the same point.
  E0: (0,0,0) → (10,0,0)
  E1: (10,0,0) → (0,10,0)
  E2: (0,10,0) → (0,0,0)
BUT all vertex CPs at origin:
  V0 = vertex_point at (0,0,0)   [actual loop start/end]
  V1 = vertex_point at (0,0,0)   [coincident]
  V2 = vertex_point at (0,0,0)   [coincident]
All three vertices are at (0,0,0): three edge endpoints collapse to the origin
— the "single shared point" in parameter space. FixIntersectingEdges sees
3 pairwise endpoint-coincidences and misclassifies them as crossings.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile
import math as _math

f = StepFile(
    catalog_id="Twi204",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; 3-edge outer EDGE_LOOP "
        "forming a triangle; all three VERTEX_POINTs are at the same 3D origin "
        "(0,0,0) — star configuration IS the defect; FixIntersectingEdges pairwise "
        "check reports 3 intersections at (0,0,0) but they are vertex-contact "
        "events not transverse crossings — false intersection reports IS the "
        "mechanism; EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE "
        "in CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── DEFECT: All three vertex CPs are at the origin (0,0,0) ──────────────────
# Three separate VERTEX_POINT entities, all with CARTESIAN_POINT at (0,0,0).
# This collapses the "triangle" to a star where every endpoint is the same 3D pt.
hub = (0.0, 0.0, 0.0)
v0 = f.vertex_point(f.cartesian_point(hub))
v1 = f.vertex_point(f.cartesian_point(hub))
v2 = f.vertex_point(f.cartesian_point(hub))

# ── 3D edge geometry: triangle with legs to distinct points ──────────────────
A = (10.0,  0.0,  0.0)
B = (0.0,  10.0,  0.0)

# E0: hub → A (along +X)
ln_e0 = f.line(f.cartesian_point(hub), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e0 = f.edge_curve(v0, v1, ln_e0)

# E1: A → B
dx1, dy1 = B[0] - A[0], B[1] - A[1]
mag1 = _math.sqrt(dx1*dx1 + dy1*dy1)
ln_e1 = f.line(
    f.cartesian_point(A),
    f.vector(f.direction((dx1 / mag1, dy1 / mag1, 0.0)), mag1),
)
e1 = f.edge_curve(v1, v2, ln_e1)

# E2: B → hub (return to origin)
dx2, dy2 = hub[0] - B[0], hub[1] - B[1]
mag2 = _math.sqrt(dx2*dx2 + dy2*dy2)
ln_e2 = f.line(
    f.cartesian_point(B),
    f.vector(f.direction((dx2 / mag2, dy2 / mag2, 0.0)), mag2),
)
e2 = f.edge_curve(v2, v0, ln_e2)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi204.stp")
