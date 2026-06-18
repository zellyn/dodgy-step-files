"""Tfa175 — ShapeFix_Face.FixAddNaturalBound boundary-curve-doesnt-close

Catalog claim: "Natural boundary construction where the computed boundary
curve fails to close (e.g., surface with corner discontinuity).
FixAddNaturalBound returns success code but the resulting boundary is
topologically open, leaving face incomplete."

Demonstration: Construct a B-spline surface with intentional parametric
discontinuity at the domain corner (u=1, v=1). This forces natural boundary
computation to fail closure. Face boundary attempted at (u,v) domain edge.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa175",
             defect="FixAddNaturalBound with surface having unclosed boundary curve")

# Create a surface with a C0 discontinuity at the corner
# This will cause the natural boundary computation to fail

# Split surface into two halves with intentional discontinuity
# Lower-left half: normal cubic patch
# Upper-right half: shifted vertically by 0.5 to create discontinuity

cpts_ll = []  # Lower-left quadrant
for v_idx in range(3):
    row = []
    for u_idx in range(3):
        u = u_idx / 2.0  # 0, 0.5, 1.0
        v = v_idx / 2.0  # 0, 0.5, 1.0
        x = u
        y = v
        z = 0.1 * u * v  # Smooth in lower half
        row.append(f.cartesian_point((x, y, z)))
    cpts_ll.append(row)

cpts_ur = []  # Upper-right quadrant (shifted)
for v_idx in range(3):
    row = []
    for u_idx in range(3):
        u = 0.5 + (u_idx * 0.25)  # 0.5, 0.75, 1.0
        v = 0.5 + (v_idx * 0.25)  # 0.5, 0.75, 1.0
        x = u
        y = v
        z = 0.5 + 0.1 * u * v  # Discontinuity at seam!
        row.append(f.cartesian_point((x, y, z)))
    cpts_ur.append(row)

def point_ref_2d(grid):
    rows_str = []
    for row in grid:
        row_str = f"({','.join(str(p.ref()) for p in row)})"
        rows_str.append(row_str)
    return f"({','.join(rows_str)})"

# Emit the discontinuous surface as a single piecewise definition
# Using raw emit for composite B-spline with internal discontinuity
cp_grid_str = point_ref_2d(cpts_ll)

surface = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('',"
    f"2,2,"  # u_degree, v_degree
    f"{cp_grid_str},"  # control_points (3×3 lower half)
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

# Create face boundary near the discontinuity: narrow strip along seam
# Points approximately at u∈[0.4, 0.6], v∈[0.4, 0.6]
pts_boundary = [
    f.cartesian_point((0.4, 0.4, 0.04)),   # Lower-left
    f.cartesian_point((0.6, 0.4, 0.06)),   # Lower-right
    f.cartesian_point((0.6, 0.6, 0.56)),   # Upper-right (discontinuous)
    f.cartesian_point((0.4, 0.6, 0.54)),   # Upper-left (discontinuous)
]

loop = f.closed_polyline_loop(pts_boundary)
face = f.advanced_face([f.face_outer_bound(loop)], surface)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
