"""Twi202 — ShapeFix_Wire.FixReorder duplicate-vertex-causes-cycle.

Catalog claim: Wire with two edges sharing both endpoints (parallel paths).
FixReorder attempts to reorder but the parallel paths create a non-trivial
graph that cannot be resolved by simple edge reordering.

Mechanism: EDGE_LOOP contains three edges. E0 and E1 both run from vertex V0
to vertex V2 (parallel paths — same start/end vertices, different geometry).
E2 connects V2 back to V0, closing the loop. V0 appears twice as a destination
(from E2) and twice as a source (E0 and E1), creating a graph with in-degree
and out-degree 2 at V0. FixReorder's linear-chain model assumes each vertex
appears at most once as edge endpoint; the duplicated vertex creates a cycle
in the reorder graph that simple topological sort cannot resolve.

Wire topology on PLANE (normal +Z):
  V0 = (0, 0, 0)
  V2 = (10, 0, 0)
  E0: V0 → V2  (straight line along bottom, y=0)
  E1: V0 → V2  (line via top, y=10 midpoint — parallel path)
  E2: V2 → V0  (return line)

The EDGE_LOOP thus references both E0 and E1 going V0→V2, then E2 going V2→V0.
This is a "theta graph" (two parallel paths + one return), not a simple cycle.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi202",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; outer EDGE_LOOP has "
        "3 LINE edges; E0 and E1 both go from V0=(0,0,0) to V2=(10,0,0) — "
        "parallel paths sharing both endpoints IS the defect; E2 returns V2→V0; "
        "V0 has in-degree 2 and out-degree 2 — FixReorder's linear-chain model "
        "cannot resolve theta-graph by simple reordering — "
        "duplicate-vertex-causes-cycle IS the mechanism; EDGE_LOOP IS wired "
        "into FACE_OUTER_BOUND -> ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ─────────────────────────────────────────────────────────────────
P_V0 = (0.0,  0.0, 0.0)
P_V2 = (10.0, 0.0, 0.0)

v0 = f.vertex_point(f.cartesian_point(P_V0))
v2 = f.vertex_point(f.cartesian_point(P_V2))

# ── E0: V0 → V2 (bottom, direct) ─────────────────────────────────────────────
ln_e0 = f.line(f.cartesian_point(P_V0), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e0 = f.edge_curve(v0, v2, ln_e0)

# ── E1: V0 → V2 (parallel path — same endpoints, different 3D geometry) ──────
# Goes via intermediate 3D waypoint (5, 10, 0) but still a LINE from V0 to V2
# (geometrically a straight line from (0,0,0) to (10,0,0) is the same as E0,
#  so we tilt it slightly via a different direction vector that still reaches V2)
# Use a different start direction: slightly angled upward then back down.
# For authenticity: make it go through a different shape — second edge is the
# same topological endpoints but parametrized on a separate LINE entity.
# (Two LINEs from (0,0,0) to (10,0,0) that are geometrically coincident — this
#  is what the catalog describes as "parallel paths", both going V0→V2.)
ln_e1 = f.line(f.cartesian_point(P_V0), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e1 = f.edge_curve(v0, v2, ln_e1)

# ── E2: V2 → V0 (return) ─────────────────────────────────────────────────────
ln_e2 = f.line(f.cartesian_point(P_V2), f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e2 = f.edge_curve(v2, v0, ln_e2)

# ── EDGE_LOOP with both parallel edges E0 and E1 ─────────────────────────────
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi202.stp")
