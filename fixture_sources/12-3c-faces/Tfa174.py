"""Tfa174 — ShapeAnalysis_CheckSmallFace.CheckTwisted near-flat-saddle

Catalog claim: "Face on a near-flat saddle surface (Gaussian curvature close
to zero, very mild principal curvatures). CheckTwisted's twist detection
threshold gives indeterminate verdict—saddle orientation cannot be reliably
inferred from coordinate-space tests."

Demonstration: Create a hyperbolic saddle surface with near-zero Gaussian
curvature (principal curvatures opposite sign but equal magnitude). Face
boundary loop on this surface produces indeterminate twist detection.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa174",
             defect="CheckTwisted on near-flat saddle surface with zero Gaussian curvature")

# Hyperbolic paraboloid: z = 0.01 * (x² - y²)
# This is a saddle with opposite curvatures, near-flat behavior
# Control point grid for B-spline approximation (4×4)

cpts = []
u_span = 4  # u from -2 to 2
v_span = 4  # v from -2 to 2

for vi in range(4):
    row = []
    for ui in range(4):
        u = -2.0 + ui
        v = -2.0 + vi
        x = u
        y = v
        z = 0.01 * (u*u - v*v)  # Near-flat saddle
        row.append(f.cartesian_point((x, y, z)))
    cpts.append(row)

# Emit B-spline saddle surface (cubic)
def point_ref_2d(grid):
    rows_str = []
    for row in grid:
        row_str = f"({','.join(str(p.ref()) for p in row)})"
        rows_str.append(row_str)
    return f"({','.join(rows_str)})"

cp_grid_str = point_ref_2d(cpts)

saddle_surface = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('',"
    f"3,3,"  # u_degree, v_degree
    f"{cp_grid_str},"  # control_points
    f".UNSPECIFIED.,"  # surface_form
    f".F.,.F.,"  # u_closed, v_closed
    f".F.,"  # self_intersect
    f"(0,0),"  # u_multiplicity_knots
    f"(0.0,0.333,0.667,1.0),"  # u_knots
    f"(4,4),"  # u_knot_multiplicity
    f"(0,0),"  # v_multiplicity_knots
    f"(0.0,0.333,0.667,1.0),"  # v_knots
    f"(4,4),"  # v_knot_multiplicity
    f".UNIFORM.)"  # knot_spec
)

# Face boundary: square region u∈[-1.5, 1.5], v∈[-1.5, 1.5]
pts_face = []
for u in [-1.5, 1.5]:
    for v in [-1.5, 1.5]:
        z = 0.01 * (u*u - v*v)
        pts_face.append(f.cartesian_point((float(u), float(v), z)))

# Close loop: corner 0 → corner 2 → corner 3 → corner 1
loop = f.closed_polyline_loop([pts_face[0], pts_face[2], pts_face[3], pts_face[1]])

face = f.advanced_face([f.face_outer_bound(loop)], saddle_surface)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
