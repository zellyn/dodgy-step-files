"""Gn176 — SolidWorks RECTANGULAR_TRIMMED_SURFACE with negative NURBS pole weight.

Catalog claim: STEP file encoding an ADVANCED_FACE on a RECTANGULAR_TRIMMED_SURFACE
whose underlying B_SPLINE_SURFACE_WITH_KNOTS has at least one negative pole weight
(-0.15 at a specific pole) in its weight vector. OCCT's BRepBuilderAPI_NurbsConvert
raises an exception or returns null shape when it encounters a negative weight, because
negative weights produce geometrically invalid rational B-spline surfaces (weight ≤ 0
is undefined in the homogeneous-coordinate representation).

The defect is the negative weight value itself — it is directly encoded in the STEP
data section as a negative real. This was reported from SolidWorks exports; we
synthesize the pattern from the defect description (LGPL-clean).

Source: https://dev.opencascade.org/content/crash-step-import-solidworks
B4 wave-5 DEF-N. Confidence: HIGH — weight vector is directly specified in STEP.

Byte assertions:
  contains(b'RECTANGULAR_TRIMMED_SURFACE')
  contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
Tier-3: shape_null == True (OCCT rejects negative weight pole)
Expected: verify with live oracle
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn176",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE wraps B_SPLINE_SURFACE_WITH_KNOTS (degree 2,2 "
        "3x3 net) whose weights list contains -0.15 at pole (1,1); "
        "negative weight is geometrically invalid in rational NURBS homogeneous "
        "coordinates; OCCT BRepBuilderAPI_NurbsConvert raises exception or returns "
        "null shape; defect from SolidWorks export pattern (dev.opencascade.org); "
        "RECTANGULAR_TRIMMED_SURFACE IS ADVANCED_FACE.face_geometry — OCC yields "
        "null/empty"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS backing surface (degree 2,2, 3x3 flat grid) ─
# This is a flat bilinear patch over [0,10]×[0,10] in XY.
# We use rational form so we can inject a negative weight.
# Control points: 3×3 grid, flat (z=0)
grid = [
    [f.cartesian_point((0.0,  0.0,  0.0)), f.cartesian_point((0.0,  5.0,  0.0)), f.cartesian_point((0.0,  10.0, 0.0))],
    [f.cartesian_point((5.0,  0.0,  0.0)), f.cartesian_point((5.0,  5.0,  0.0)), f.cartesian_point((5.0,  10.0, 0.0))],
    [f.cartesian_point((10.0, 0.0,  0.0)), f.cartesian_point((10.0, 5.0,  0.0)), f.cartesian_point((10.0, 10.0, 0.0))],
]

# Standard B_SPLINE_SURFACE_WITH_KNOTS (non-rational, degree 2, clamped)
bssurf = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=grid,
    u_multiplicities=[3, 3],
    v_multiplicities=[3, 3],
    u_knots=[0.0, 10.0],
    v_knots=[0.0, 10.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# ── DEFECT: Overlay with RATIONAL_B_SPLINE_SURFACE weights containing -0.15 ─
# We emit a complex instance that combines B_SPLINE_SURFACE_WITH_KNOTS with
# RATIONAL_B_SPLINE_SURFACE to inject the negative weight.
# Per STEP AP214, a rational surface is encoded as a complex instance:
# (B_SPLINE_SURFACE(...) RATIONAL_B_SPLINE_SURFACE(...)) where
# RATIONAL_B_SPLINE_SURFACE carries the weights_data list.
#
# Weight matrix (row-major, 3 rows × 3 cols):
#   row 0: (1.0,  1.0,  1.0)
#   row 1: (1.0, -0.15, 1.0)   ← DEFECT: negative weight at (1,1)
#   row 2: (1.0,  1.0,  1.0)
#
# We emit this as a raw complex STEP entity.
# Extract control point refs:
row_refs = []
for row in grid:
    row_refs.append("(" + ",".join(f"#{cp.eid}" for cp in row) + ")")
cps_list = "(" + ",".join(row_refs) + ")"

# Build the raw complex rational B-spline surface entity.
# Format: (B_SPLINE_SURFACE(...) RATIONAL_B_SPLINE_SURFACE(weights_data))
# B_SPLINE_SURFACE attributes (per STEP EXPRESS):
#   name, u_degree, v_degree, control_points_list, surface_form,
#   u_closed, v_closed, self_intersect
# B_SPLINE_SURFACE_WITH_KNOTS additional attributes:
#   u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec
rat_surf = f._emit_raw(
    "(B_SPLINE_SURFACE(2,2," + cps_list + ",.UNSPECIFIED.,.F.,.F.,.F.)"
    "B_SPLINE_SURFACE_WITH_KNOTS((3,3),(3,3),(0.,10.),(0.,10.),.UNSPECIFIED.)"
    "RATIONAL_B_SPLINE_SURFACE(((1.,1.,1.),(1.,-0.15,1.),(1.,1.,1.))))"
)

# ── RECTANGULAR_TRIMMED_SURFACE wrapping the defect rational surface ─────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
rts = f.rectangular_trimmed_surface(rat_surf, 1.0, 9.0, 1.0, 9.0,
                                    usense=True, vsense=True)

# ── Minimal ADVANCED_FACE on the trimmed surface ──────────────────────────────
# We use a simple rectangular EDGE_LOOP in 3D space matching the RTS bounds:
# corners at (1,1,0), (9,1,0), (9,9,0), (1,9,0)
p0 = f.cartesian_point((1.0, 1.0, 0.0))
p1 = f.cartesian_point((9.0, 1.0, 0.0))
p2 = f.cartesian_point((9.0, 9.0, 0.0))
p3 = f.cartesian_point((1.0, 9.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], rts)

# ── OPEN_SHELL and SHELL_BASED_SURFACE_MODEL ─────────────────────────────────
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
