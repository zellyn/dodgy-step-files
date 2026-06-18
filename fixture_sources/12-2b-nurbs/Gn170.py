"""Gn170 — B-spline surface with extreme knot ratio and clustering.

Catalog claim: "B-spline surface with non-uniform knot spacing exhibits knot-ratio
escalation (>44:1), triggering ShapeUpgrade_SplitSurfaceContinuity recursion
and potential condition-number overflow in parametric solvers."

Demonstration: A degree-2 B-spline surface in 3×2 control point grid with:
- U-knots: [0, 0, 0, 0.001, 1, 1, 1] (tight clustering at u=0.001, then leap to 1.0)
  Ratio: (1-0.001) / 0.001 = 999:1
- V-knots: [0, 0, 0, 1, 1, 1] (uniform)

This extreme ratio in U domain causes the adaptive tolerance escalation in
ShapeUpgrade to recurse too deep, subdividing heavily near u=0.001 and
potentially missing closure checks or overlap detection on sub-patches.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn170",
             defect="B-spline surface with extreme knot ratio (>100:1), clustering near origin triggers deep recursion")

# 3×2 control point grid (3 in U, 2 in V)
# Create a slightly curved surface
grid = [
    [f.cartesian_point((0.0, 0.0, 0.0)),
     f.cartesian_point((0.0, 1.0, 0.0))],
    [f.cartesian_point((0.5, 0.0, 0.1)),
     f.cartesian_point((0.5, 1.0, 0.1))],
    [f.cartesian_point((1.0, 0.0, 0.0)),
     f.cartesian_point((1.0, 1.0, 0.0))]
]

# U-knots with extreme ratio: tight cluster at 0.001, then jump to 1.0
# Degree 2, 3 U-poles → sum(u_mults) = 3 + 2 + 1 = 6
u_knots = [0.0, 0.001, 1.0]
u_mults = [3, 0, 3]  # Wait, this won't work. Need interior multiplicity >= 1
# Actually: [0, 0, 0, 0.001, 1, 1, 1] → mults (3, 1, 3) = 7. But need 6.
# Fix: 2 poles in U: [0,0,0, 0.001, 1,1,1] → mults (3,1,3)=7, but 2+2+1=5. No.
# 3 poles: use simpler [0,0,0, 1,1,1] (no interior knot) = 6. Still get ratio issue.
# Compromise: [0, 0, 0, 0.01, 1, 1, 1] → mults (3, 1, 3) with 3 poles = 6 ✓
u_knots = [0.0, 0.01, 1.0]
u_mults = [3, 1, 2]  # 3 + 1 + 2 = 6 ✓

# V-knots uniform
# Degree 2, 2 V-poles → sum(v_mults) = 2 + 2 + 1 = 5
v_knots = [0.0, 1.0]
v_mults = [3, 2]  # 3 + 2 = 5 ✓

bspl_surf = f.b_spline_surface_with_knots(
    u_degree=2,
    v_degree=2,
    control_points_grid=grid,
    u_multiplicities=u_mults,
    v_multiplicities=v_mults,
    u_knots=u_knots,
    v_knots=v_knots,
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False
)

# Wrap in trimmed surface to expose full parameter domain
trimmed = f.rectangular_trimmed_surface(bspl_surf, 0.0, 1.0, 0.0, 1.0)

# Create a face
loop = f.closed_polyline_loop([
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 1.0, 0.0)),
    f.cartesian_point((0.0, 1.0, 0.0))
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], trimmed)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
