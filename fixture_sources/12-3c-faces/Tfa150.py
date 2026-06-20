"""Tfa150 — ShapeFix_Face.FixPeriodicDegenerated B-spline-revolution.

Catalog claim: Surface is B-spline approximating a revolution; FixPeriodicDegenerated's
apex-construction logic assumes analytic revolution not B-spline.

Trigger: Call FixPeriodicDegenerated() on single-wire face with degree-3 B-spline
surface approximating cone (apex at origin, profile curve along u=0 seam).
FixPeriodicDegenerated should construct apex curve and adjust wire orientation
assuming conic geometry. If algorithm assumes analytic properties (e.g., GetCone()),
it fails on B-spline and returns error or applies wrong transformation.

Mechanism: CLOSED_SHELL consisting of:
  face[0]: ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS approximating a cone
    (apex at origin, opens upward, radius 5mm at z=10mm).  The apex row of
    control points all coincide at (0,0,0).  The face wire (single loop) runs
    along the u=0 seam twice (up and down) and uses the top circle to close.
    FixPeriodicDegenerated is expected to detect the degenerate apex row and
    construct a degenerate edge — but the algorithm queries GetCone() which
    returns False for a B-spline, so it bails out early.  Defect IS on live
    CLOSED_SHELL traversal path.
  face[1]: top disc cap (z=10)

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Tfa150",
    defect=(
        "CLOSED_SHELL: face[0] is ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS "
        "approximating a cone (apex at origin, radius 5mm at z=10mm); "
        "apex row of control points all at (0,0,0) — degenerate; "
        "FixPeriodicDegenerated queries GetCone() which returns False for B-spline "
        "surface; algorithm bails out early instead of constructing apex curve; "
        "face wire: seam .T. (apex→top), top_circle .T., seam .F. (top→apex); "
        "face[1] is valid top disc cap; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

R = 5.0   # radius at top
H = 10.0  # height

# ── B-spline cone approximation: degree 3 in U (revolution), degree 1 in V ──
# V runs from 0 (apex) to 1 (base rim).
# U has 4 control cols (degree 3, clamped: mults [4,4], knots [0,1]).
# V has 2 control rows (degree 1, clamped: mults [2,2], knots [0,1]).
# At V=0 all 4 u-cols collapse to apex (0,0,0) — degenerate row.
# At V=1 the 4 u-cols approximate a circle of radius R in the XY plane.
# Approximation: 4-point polygon around circle at z=H.
cp = [
    # u-row 0: apex row (all degenerate at origin)
    [
        f.cartesian_point((0.0,  0.0, 0.0)),
        f.cartesian_point((0.0,  0.0, 0.0)),
        f.cartesian_point((0.0,  0.0, 0.0)),
        f.cartesian_point((0.0,  0.0, 0.0)),
    ],
    # u-row 1: base rim approximation (4-point polygon inscribed in circle)
    [
        f.cartesian_point(( R,   0.0, H)),
        f.cartesian_point(( 0.0,  R,  H)),
        f.cartesian_point((-R,   0.0, H)),
        f.cartesian_point(( 0.0, -R,  H)),
    ],
]
# u_degree=1, nu=2: sum(u_mults)=nu+u_degree+1=4 → [2,2]
# v_degree=3, nv=4: sum(v_mults)=nv+v_degree+1=8 → [4,4]
bsp_cone = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=3,
    control_points_grid=cp,
    u_multiplicities=[2, 2],
    v_multiplicities=[4, 4],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    knot_spec="UNSPECIFIED",
)

# ── Vertices: apex and seam point on top rim ────────────────────────────────
pt_apex     = f.cartesian_point((0.0, 0.0, 0.0))
pt_seam_top = f.cartesian_point((R,   0.0, H))

v_apex     = f.vertex_point(pt_apex)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam edge: vertical line apex → seam_top ────────────────────────────────
seam_line = f.line(pt_apex, f.vector(f.direction((0.0, 0.0, 1.0)), H))
seam_ec   = f.edge_curve(v_apex, v_seam_top, seam_line)

# ── Top circle: closed at v_seam_top ────────────────────────────────────────
top_ctr = f.cartesian_point((0.0, 0.0, H))
top_circ_ec = f.edge_curve(
    v_seam_top, v_seam_top,
    f.circle(
        f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
        R
    )
)

# ── face[0]: B-spline cone face — THE DEFECT ────────────────────────────────
# Wire: seam .T. (apex→seam_top), top_circle .T. (full rev), seam .F. (seam_top→apex)
cone_loop = f.edge_loop([
    f.oriented_edge(seam_ec,      True),   # apex → seam_top (going up)
    f.oriented_edge(top_circ_ec,  True),   # full revolution at top
    f.oriented_edge(seam_ec,      False),  # seam_top → apex (going down)
])
face0 = f.advanced_face([f.face_outer_bound(cone_loop)], bsp_cone)

# ── face[1]: top disc cap ────────────────────────────────────────────────────
top_plane = f.plane(
    f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
)
face1 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(top_circ_ec, True)]))],
    top_plane
)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ──────────────────────────────────────
closed_sh = f.closed_shell([face0, face1])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa150.stp")
