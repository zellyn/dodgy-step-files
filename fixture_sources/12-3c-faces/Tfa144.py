"""Tfa144 — ShapeAnalysis_CheckSmallFace.CheckPinFace 3D-vs-parametric-pin

Catalog claim: "B_SPLINE_SURFACE_WITH_KNOTS stretched non-uniformly (control
points in y-direction span 0 to 40.0) creates severe parametric-vs-3D
aspect-ratio mismatch. Face bounds parametrically narrow (u: [0.1, 0.15],
v: [0.2, 0.9]) with parametric aspect 0.071, but 3D geometry expands to
width ~0.5 and length ~20 (aspect 0.025). CheckPinFace applies parametric
ratio test, missing the actual 3D pin condition. Defect exposes surface-stretch
blindness in pin detection."

Demonstration: construct a B-spline surface that is extremely stretched in
the y-direction (control points span 0 to 40.0) but parametrically narrow.
The face bounds parametrically to [0.1, 0.15] × [0.2, 0.9], which looks like
a thin pin in parametric space, but in 3D the surface expands to a long
rectangular band (pin in 3D but not in parametric).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa144",
             defect="B-spline surface with parametric-vs-3D pin mismatch")

# Create a highly stretched B-spline surface using raw emit.
# The surface has control points in a 2×4 grid where:
# - u-direction (2 control points): short span in x
# - v-direction (4 control points): long span in y (0 to 40)

# We'll emit the B_SPLINE_SURFACE_WITH_KNOTS directly.
# For simplicity, we approximate with a simpler approach:
# Create 4 rectangular vertices and build a bilinear B-spline-like surface.

# However, since the builder doesn't have B_SPLINE_SURFACE_WITH_KNOTS,
# we'll use the escape hatch to emit raw entities.

# Build the control-point grid (2×4):
# Row 1 (v=0 direction): 4 points at y-spacing
# Row 2 (v=1 direction): 4 points at y-spacing, slightly displaced in x
pts_row1 = []
pts_row2 = []
for i in range(4):
    y_val = i * (40.0 / 3.0)  # y: 0, 13.33, 26.67, 40
    # Row 1: x=0, y varies, z=0
    pts_row1.append(f.cartesian_point((0.0, y_val, 0.0)))
    # Row 2: x=0.5, y varies, z=0 (slight offset in x)
    pts_row2.append(f.cartesian_point((0.5, y_val, 0.0)))

# Emit a B_SPLINE_SURFACE_WITH_KNOTS with:
# - Degree 1 in u, degree 1 in v (bilinear)
# - 2 control points in u-direction, 4 in v-direction
# - Knots: [0, 0, 1, 1] for u; [0, 0, 0, 0.33, 0.67, 1, 1, 1, 1] for v (or simplified)

# For this escape, we construct the raw entity manually:
cp_u_list = f._emit_raw("(0.0,13.333,26.667,40.0)")  # placeholder for control points
# Actually, let's build it step by step:

# Convert points to list format for the control grid
def point_ref_list(pts):
    return f"({','.join(str(p.ref()) for p in pts)})"

cp_row1_refs = point_ref_list(pts_row1)
cp_row2_refs = point_ref_list(pts_row2)
cp_grid = f"(({cp_row1_refs}),({cp_row2_refs}))"

# Emit the B_SPLINE_SURFACE_WITH_KNOTS
# B_SPLINE_SURFACE_WITH_KNOTS(
#   name,
#   u_degree, v_degree,
#   control_points_list (list of (row)),
#   surface_form (UNSPECIFIED, PLANE, CYLINDRICAL, CONICAL, SPHERICAL, TOROIDAL, SURF_OF_REVOLUTION, SURF_OF_LINEAR_EXTRUSION, RULED_SURF, GENERALISED_CONE),
#   u_closed, v_closed,
#   self_intersect,
#   u_multiplicity_knots (list), u_knots (list), u_knot_mult (list),
#   v_multiplicity_knots (list), v_knots (list), v_knot_mult (list),
#   knot_spec (UNSPECIFIED, QUASI_UNIFORM, UNIFORM, PIECEWISE_BEZIER)
# )

# Simplified: emit a raw B_SPLINE_SURFACE_WITH_KNOTS string
bspline_raw = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('',"
    f"1,1,"  # u_degree, v_degree
    f"{cp_grid},"  # control_points (2x4 grid)
    f".UNSPECIFIED.,"  # surface_form
    f".F.,.F.,"  # u_closed, v_closed
    f".F.,"  # self_intersect
    f"(0,0),"  # u_multiplicity_knots: not used in this simplified form
    f"(0.0,1.0),"  # u_knots
    f"(2,2),"  # u_knot_multiplicity
    f"(0,0,0,0),"  # v_multiplicity_knots
    f"(0.0,0.333,0.667,1.0),"  # v_knots (roughly)
    f"(2,1,1,2),"  # v_knot_multiplicity
    f".PIECEWISE_BEZIER.)"  # knot_spec
)

# Now create a face on this B-spline surface.
# The face bounds parametrically to u: [0.1, 0.15], v: [0.2, 0.9]

# Create a 4-point rectangular wire in parametric space (mapping to 3D via the surface).
# Approximate 3D corners:
# (u=0.1, v=0.2) -> interpolate on surface
# (u=0.15, v=0.2) -> interpolate on surface
# (u=0.15, v=0.9) -> interpolate on surface
# (u=0.1, v=0.9) -> interpolate on surface

# On a bilinear surface with the control grid above:
# S(u, v) = (1-u)(1-v)*CP[0,0] + u(1-v)*CP[1,0] + (1-u)v*CP[0,1] + uv*CP[1,1]
# where CP[i,j] is indexed by (u-row, v-row)

# Approximate 3D coordinates (simplified):
pts_face = []
for u in [0.1, 0.15]:
    for v in [0.2, 0.9]:
        # Interpolate x, y, z on the bilinear surface
        x = (1-u)*0.0 + u*0.5  # x ranges 0 to 0.5
        y = (1-u)*(1-v)*0.0 + (1-u)*v*40.0 + u*(1-v)*0.0 + u*v*40.0
        y = y  # y ranges 0 to 40 depending on v
        z = 0.0
        pts_face.append(f.cartesian_point((x, y, z)))

# Reorder to form a closed loop: (0.1, 0.2), (0.15, 0.2), (0.15, 0.9), (0.1, 0.9)
# pts are already in this order from the nested loop above
loop = f.closed_polyline_loop([pts_face[0], pts_face[2], pts_face[3], pts_face[1]])

# Create the face on the B-spline surface
face = f.advanced_face([f.face_outer_bound(loop)], bspline_raw)

# Wrap in shell and surface model
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
