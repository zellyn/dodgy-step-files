"""Gn173 — Rational B-spline surface with extreme pole clustering and weight ratio.

Catalog claim: "Rational B-spline surface with poles clustered in 1e-3 region
and weights varying 1:1e6 exhibits numerical instability. ComputeTol and knot-ratio
checks fail to normalize, causing parametric solver convergence loss in
reparametrization and C0-upgrade branches."

Demonstration: A 3×3 control point grid for a rational B-spline surface where:
- Most poles occupy [0, 0.001] in Y (tight clustering)
- Weights range from 1.0 to 1e5 (extreme ratio)
- Interior poles have weight 1e5, creating singularity near [0.5, 0.0005]

This combination triggers EvalTol-based fallback in ShapeAnalysis_Curve, but
the knot-ratio heuristic (10% of min pole distance) computes Tol2d ≈ 1e-5,
which may over-escalate and cause adaptive tolerance loop divergence.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn173",
             defect="rational B-spline surface with extreme pole clustering (1e-3) and weight ratio (1:1e6)")

# 3×3 control point grid with tight Y clustering
# Row 0 (u=0)
grid = [
    [f.cartesian_point((0.0, 0.0, 0.0)),
     f.cartesian_point((0.0, 0.0005, 0.0)),
     f.cartesian_point((0.0, 0.001, 0.0))],
    # Row 1 (u=0.5) - interior poles with high weights
    [f.cartesian_point((0.5, 0.0, 0.1)),
     f.cartesian_point((0.5, 0.0005, 0.1)),
     f.cartesian_point((0.5, 0.001, 0.1))],
    # Row 2 (u=1)
    [f.cartesian_point((1.0, 0.0, 0.0)),
     f.cartesian_point((1.0, 0.0005, 0.0)),
     f.cartesian_point((1.0, 0.001, 0.0))]
]

# Weights: high on interior poles (row 1) to create singularity
weights_grid = [
    [1.0, 1.0, 1.0],        # Row 0: normal weights
    [1e5, 1e5, 1e5],        # Row 1: extreme weights
    [1.0, 1.0, 1.0]         # Row 2: normal weights
]

# Degree 2 in both U and V
# 3 U-poles + degree 2 + 1 = 6; 3 V-poles + degree 2 + 1 = 6
u_knots = [0.0, 0.5, 1.0]
u_mults = [3, 1, 3]  # sum = 7
v_knots = [0.0, 0.5, 1.0]
v_mults = [3, 1, 3]  # sum = 7

# But we have 3×3 = 9 poles, and 3 + 2 + 1 = 6 for each direction
# Adjust: use 2×2 grid for simpler case
# Degree 1, 2 poles each direction → 2 + 1 + 1 = 4
grid_2x2 = [
    [f.cartesian_point((0.0, 0.0, 0.0)),
     f.cartesian_point((0.0, 0.001, 0.0))],
    [f.cartesian_point((1.0, 0.0, 0.0)),
     f.cartesian_point((1.0, 0.001, 0.0))]
]

weights_2x2 = [
    [1.0, 1e6],
    [1.0, 1e6]
]

u_knots = [0.0, 1.0]
u_mults = [2, 2]  # 2 + 2 = 4 = 2 + 1 + 1 ✓
v_knots = [0.0, 1.0]
v_mults = [2, 2]  # 2 + 2 = 4 = 2 + 1 + 1 ✓

# Build rational surface with weights via _emit_raw (builder method doesn't expose weights directly)
# First create the B-spline surface structure
grid_refs = [[grid_2x2[i][j] for j in range(2)] for i in range(2)]

bspl_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('bspl_rational_surf',1,1,"
    f"(({grid_2x2[0][0].ref()},{grid_2x2[0][1].ref()}),"
    f"({grid_2x2[1][0].ref()},{grid_2x2[1][1].ref()})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.,"
    f"((1.0,1.E+06),(1.0,1.E+06)))"
)

# Wrap in trimmed surface
trimmed = f.rectangular_trimmed_surface(bspl_surf, 0.0, 1.0, 0.0, 1.0)

# Create a face
loop = f.closed_polyline_loop([
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.001, 0.0)),
    f.cartesian_point((0.0, 0.001, 0.0))
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], trimmed)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
