"""Tfa187 — ShapeAnalysis_CheckSmallFace.CheckPin pin-with-fillet

Catalog claim: "Pin detection based on convergent poles fails when pin tip
is filleted (poles remain distributed). CheckPin's angle measurement becomes
undefined at non-pointed apex."

Demonstration: B-spline surface (3×4 control point grid) representing a
cone-like surface with smooth fillet at the apex instead of a sharp point.
Face boundary spans full parameter range.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa187",
             defect="CheckPin on cone-like surface with filleted apex")

# Create cone-like surface with filleted apex
# Control grid: 3 rows (u-direction: radial) × 4 columns (v-direction: around axis)
# Apex rows are not degenerate but form a small fillet

cpts = []

# Row 0: Apex region (filleted, not degenerate)
apex_pts = []
for v_idx in range(4):
    angle = v_idx * 1.5708  # 0, π/2, π, 3π/2
    # Small circle at apex
    x = 0.2 * (1.0 - v_idx % 2 * 0.1)
    y = 0.2 * (1.0 - v_idx % 2 * 0.1)
    z = 10.0
    apex_pts.append(f.cartesian_point((x, y, z)))
cpts.append(apex_pts)

# Row 1: Mid-cone (larger radius)
mid_pts = []
for v_idx in range(4):
    angle = v_idx * 1.5708
    import math
    x = 2.0 * math.cos(angle)
    y = 2.0 * math.sin(angle)
    z = 5.0
    mid_pts.append(f.cartesian_point((x, y, z)))
cpts.append(mid_pts)

# Row 2: Base (full radius)
base_pts = []
for v_idx in range(4):
    angle = v_idx * 1.5708
    import math
    x = 5.0 * math.cos(angle)
    y = 5.0 * math.sin(angle)
    z = 0.0
    base_pts.append(f.cartesian_point((x, y, z)))
cpts.append(base_pts)

def point_ref_2d(grid):
    rows_str = []
    for row in grid:
        row_str = f"({','.join(str(p.ref()) for p in row)})"
        rows_str.append(row_str)
    return f"({','.join(rows_str)})"

cp_grid_str = point_ref_2d(cpts)

surface = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('',"
    f"2,3,"  # u_degree=2, v_degree=3 (closed in v via periodic knots)
    f"{cp_grid_str},"  # control_points (3×4 grid)
    f".UNSPECIFIED.,"  # surface_form
    f".F.,.F.,"  # u_closed, v_closed
    f".F.,"  # self_intersect
    f"(0,0),"  # u_multiplicity_knots
    f"(0.0,0.5,1.0),"  # u_knots
    f"(3,3),"  # u_knot_multiplicity
    f"(0,0),"  # v_multiplicity_knots
    f"(0.0,0.333,0.667,1.0),"  # v_knots
    f"(4,4),"  # v_knot_multiplicity
    f".UNIFORM.)"  # knot_spec
)

# Face boundary over full domain: u∈[0,1], v∈[0,1]
pts_boundary = [
    f.cartesian_point((0.2, 0.2, 10.0)),   # Near apex
    f.cartesian_point((5.0, 0.0, 0.0)),    # Base edge
    f.cartesian_point((0.0, 5.0, 0.0)),    # Base edge
    f.cartesian_point((0.2, -0.2, 10.0)),  # Near apex
]

loop = f.closed_polyline_loop(pts_boundary)
face = f.advanced_face([f.face_outer_bound(loop)], surface)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
