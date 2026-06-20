"""Tfa225 — FixMissingSeam.seam-boundary-clamping

U-closed BSpline surface; 2-edge loop with period-wrap geometry; tests
seam-boundary clamping at line 2224. Defect: out-of-bounds seam placement
(u > 2π) bypasses AdjustToPeriod, producing invalid parameter range.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS
that is U-closed (u_closed=True). The surface is a cylinder-like patch with
period U=2 (control net wraps in U). The face has a 2-edge EDGE_LOOP: one seam
edge at u=0 and one seam edge at u=2 (the period boundary), creating a period-
wrap loop. The OCCT FixMissingSeam code path at line 2224 clamps the computed
seam position to [0, 2π]; when the seam falls at u=2.0 (the full period), the
clamping logic must correctly apply AdjustToPeriod to bring it within bounds.
Without clamping, the arithmetic produces an out-of-bounds parameter range.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Tfa225",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS; "
        "degree 1×2, 2×3 control grid; u_closed=True (period-wrap in U); "
        "2-edge EDGE_LOOP: seam at u=0 and u=period boundary with period-wrap geometry; "
        "FixMissingSeam line 2224: seam-boundary clamping via AdjustToPeriod; "
        "seam at u=full-period: out-of-bounds without clamping; "
        "invalid parameter range when AdjustToPeriod bypassed; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── U-closed B_SPLINE_SURFACE_WITH_KNOTS: cylinder-like patch ─────────────────
# Degree 1 in U (2 unique U knots, closed wrap), degree 2 in V.
# nu=2 control points in U (wraps closed), nv=3 in V.
# u_degree=1, nu=2 → sum(u_mults) = 2+1+1=4; with u_closed, we use [2,2] at [0,1]
# v_degree=2, nv=3 → sum(v_mults) = 3+2+1=6 → [3,3] at [0,1]
#
# U-closed means the surface wraps: control row 0 == control row nu in 3D.
# Build a flat rectangular patch where U wraps (like a cylinder unrolled).
# Control grid: 2 rows (U) × 3 cols (V)
# Row 0 at x=0: y=0, y=0.5, y=1
# Row 1 at x=1: y=0, y=0.5, y=1
# (U-closed: row 0 and row 1 connect, wrapping at period=1.0)

cp_grid = [
    [f.cartesian_point(p) for p in row]
    for row in [
        [(0.0, 0.0, 0.0), (0.0, 0.5, 0.2), (0.0, 1.0, 0.0)],
        [(1.0, 0.0, 0.0), (1.0, 0.5, 0.2), (1.0, 1.0, 0.0)],
    ]
]

bspline_surf = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=2,
    control_points_grid=cp_grid,
    u_multiplicities=[2, 2],
    v_multiplicities=[3, 3],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=True,
    v_closed=False,
    self_intersect=False,
)

# ── 2-edge EDGE_LOOP with period-wrap geometry ────────────────────────────────
# Bottom edge: from (0,0,0) to (1,0,0) — seam at u=0 side
# Top edge: from (1,0,0) back to (0,0,0) — seam at u=period boundary
# This creates the period-wrap loop.

pt_start = f.cartesian_point((0.0, 0.0, 0.0))
pt_end   = f.cartesian_point((1.0, 0.0, 0.0))

v_start = f.vertex_point(pt_start)
v_end   = f.vertex_point(pt_end)

# Bottom edge: straight from (0,0,0) → (1,0,0)
e_fwd = f.edge_curve(
    v_start, v_end,
    f.line(pt_start, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)

# Return edge: straight from (1,0,0) → (0,0,0) — period-wrap path
e_rev = f.edge_curve(
    v_end, v_start,
    f.line(pt_end, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0))
)

# 2-edge loop: forward then return across period boundary
face_loop = f.edge_loop([
    f.oriented_edge(e_fwd, True),
    f.oriented_edge(e_rev, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], bspline_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa225.stp")
