"""Tfa197 — ShapeAnalysis_Surface.IsUClosed bspline-periodic-u

A B-spline surface marked periodic in U direction must close geometrically:
start and end isoparametric curves coincide. The closure checker caches results
but may skip revalidation when the surface is trimmed or modified. A face on a
geometrically open but periodically flagged B-spline exhibits incorrect winding
classification if the closure test is bypassed.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS
that approximates a cylindrical patch parameterized over u in [0, 2*pi].
The surface control grid forms a cylinder (radius=1, height=1): 4 columns of
control points in U arranged around the circle plus the repeated first column to
close the periodic loop, and 2 rows in V for bottom/top. The STEP entity uses
U-knot multiplicity indicating closure at u=0/2pi. The face boundary uses
straight-line edges that "close" the patch at the seam. IsUClosed must validate
that the geometry at u=0 and u=2pi coincide; caching may skip this recheck when
the face is modified, leading to incorrect winding classification.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa197",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS; "
        "cylinder approximation: radius=1, height=1; "
        "U-direction: 4-segment (degree 1) periodic loop around cylinder; "
        "V-direction: linear (degree 1) bottom to top; "
        "U-periodic knots close geometry at u=0 ≡ u=8; "
        "IsUClosed cache bypass: revalidation skipped after face modification; "
        "winding classification incorrect on open-but-periodic-flagged surface; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B-spline cylinder approximation: 4-sided (degree 1) in U, degree 1 in V ──
# U direction: 4 segments around the cylinder (5 control points, first=last for closure)
# V direction: 2 rows (bottom at z=0, top at z=1)
# 5 columns × 2 rows
r = 1.0
h = 1.0
angles = [0.0, _math.pi / 2, _math.pi, 3 * _math.pi / 2, 2 * _math.pi]
cp = [
    [f.cartesian_point((r * _math.cos(a), r * _math.sin(a), z)) for z in [0.0, h]]
    for a in angles
]
# U: 5 control points (degree 1), multiplicities [2,1,1,1,2] → open knot vector
# but with first and last points coincident → periodic closure
bsurf = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=cp,
    u_multiplicities=[2, 1, 1, 1, 2],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 2.0, 4.0, 6.0, 8.0],
    v_knots=[0.0, 1.0],
)

# ── 3D corners at u=0 (seam), bottom and top ─────────────────────────────────
# At u=0: seam bottom = (r,0,0), seam top = (r,0,h)
# At u=8 (end knot): same 3D point because last CP == first CP
pt_sb = f.cartesian_point((r,   0.0, 0.0))   # seam bottom
pt_st = f.cartesian_point((r,   0.0, h  ))   # seam top

v_sb = f.vertex_point(pt_sb)
v_st = f.vertex_point(pt_st)

# Seam edge (vertical line at u=0/u=8): bottom→top
seam_edge = f.edge_curve(
    v_sb, v_st,
    f.line(pt_sb, f.vector(f.direction((0.0, 0.0, 1.0)), h)),
)

# Bottom circle edge: closed circle at z=0 (full revolution from seam back to seam)
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_circle = f.circle(bot_plc, r)
bot_edge = f.edge_curve(v_sb, v_sb, bot_circle)

# Top circle edge: closed circle at z=h (full revolution)
top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, h)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, r)
top_edge = f.edge_curve(v_st, v_st, top_circle)

# ── Face loop: seam(T) + top(T) + seam(F) + bottom(F) ───────────────────────
# Winding: outer face of cylinder, normal outward
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge,  True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(bot_edge,  False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], bsurf)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa197.stp")
