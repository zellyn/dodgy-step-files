"""Tfa172 — ShapeAnalysis_CheckSmallArea non-planar-face

Catalog claim: "Parametrically small face on curved B-spline surface where
geometric area differs significantly from parametric area. CheckSmallArea uses
parametric bounds and misses the actual 3D footprint, triggering false
negatives on near-degenerate curved faces."

Demonstration: construct a small parametric face on a curved B-spline surface
where the 3D area is actually substantial, but the parametric (u,v) domain area
is very small. This tests whether area checking correctly accounts for surface
curvature and stretch.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa172",
             defect="Parametrically small face on curved B-spline with area mismatch")

# Create a curved B-spline surface (hemisphere-like) that expands in 3D
# but is parametrically small.

# We'll build a simple quadratic B-spline surface with 3×3 control points
# arranged to form a dome/hemisphere.

# Control point grid (3×3):
# Bottom row (v=0): three points in x-direction
# Middle row (v=1): three points closer together (curving up)
# Top row (v=2): three points at the apex

import math

# Create the 3×3 control point grid
cpts = []
for v_idx in range(3):
    row = []
    for u_idx in range(3):
        # Scale to create dome shape
        u_norm = u_idx / 2.0  # 0, 0.5, 1.0
        v_norm = v_idx / 2.0  # 0, 0.5, 1.0

        # Dome geometry: center lifts up, edges stay lower
        height = 5.0 * (1.0 - (u_norm - 0.5)**2 - (v_norm - 0.5)**2)
        height = max(0.0, height)

        x = 5.0 * (u_norm - 0.5)  # range -2.5 to 2.5
        y = 5.0 * (v_norm - 0.5)  # range -2.5 to 2.5
        z = height

        row.append(f.cartesian_point((x, y, z)))
    cpts.append(row)

# Flatten grid to list format
def flatten_grid(grid):
    return [pt for row in grid for pt in row]

all_cpts = flatten_grid(cpts)

# Emit B_SPLINE_SURFACE_WITH_KNOTS using raw emit
# For a 3×3 quadratic surface (degree 2 in both directions)
def point_ref_2d(grid):
    rows_str = []
    for row in grid:
        row_str = f"({','.join(str(p.ref()) for p in row)})"
        rows_str.append(row_str)
    return f"({','.join(rows_str)})"

cp_grid_str = point_ref_2d(cpts)

bspline_surface = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('',"
    f"2,2,"  # u_degree, v_degree (quadratic)
    f"{cp_grid_str},"  # control_points (3×3 grid)
    f".UNSPECIFIED.,"  # surface_form
    f".F.,.F.,"  # u_closed, v_closed
    f".F.,"  # self_intersect
    f"(0,0),"  # u_multiplicity_knots
    f"(0.0,0.5,1.0),"  # u_knots
    f"(3,3),"  # u_knot_multiplicity
    f"(0,0),"  # v_multiplicity_knots
    f"(0.0,0.5,1.0),"  # v_knots
    f"(3,3),"  # v_knot_multiplicity
    f".UNIFORM.)"  # knot_spec
)

# Create a small parametric face: u in [0.1, 0.2], v in [0.1, 0.2]
# Parametrically this is 0.1 × 0.1 = 0.01 square units (very small)
# But in 3D, due to the curvature, the actual area is larger

# Four corner points of the parametric face approximated at 3D:
# (u, v) = (0.1, 0.1), (0.2, 0.1), (0.2, 0.2), (0.1, 0.2)

pts_face_3d = []
for u in [0.1, 0.2]:
    for v in [0.1, 0.2]:
        # Approximate surface evaluation at (u, v)
        # Simple bilinear approximation of the 3×3 surface at small parameter values
        height = 5.0 * (1.0 - (u - 0.5)**2 - (v - 0.5)**2)
        height = max(0.0, height)
        x = 5.0 * (u - 0.5)
        y = 5.0 * (v - 0.5)
        z = height
        pts_face_3d.append(f.cartesian_point((x, y, z)))

# Reorder for closed loop: (0.1,0.1), (0.2,0.1), (0.2,0.2), (0.1,0.2)
loop = f.closed_polyline_loop([pts_face_3d[0], pts_face_3d[2], pts_face_3d[3], pts_face_3d[1]])

# Create face on the B-spline surface
face = f.advanced_face([f.face_outer_bound(loop)], bspline_surface)

# Wrap in shell and surface model
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
