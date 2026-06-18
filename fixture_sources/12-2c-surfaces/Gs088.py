"""Gs088 — ShapeUpgrade_FaceDivide.SplitSurface periodic

Catalog claim: "CYLINDRICAL_SURFACE split at u=0 (seam). SplitSurface produces
two identical patches instead of preserving wrapped periodicity. Tests line 304+
knot-removal-threshold on periodic geometry."

Demonstration: A CYLINDRICAL_SURFACE trimmed to cover the full [0,2π] period
(u ∈ [0,1] mapped to full circle). Split at the seam u=0 should preserve the
wrapped periodicity and produce compatible neighboring patches. The defect is
that SplitSurface produces two identical patches instead of recognizing the
period wrap.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs088",
             defect="CYLINDRICAL_SURFACE split at seam; periodic wrapping not preserved")

# Cylinder at origin, radius 1.0, along z-axis
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)
cylinder = f.cylindrical_surface(placement, 1.0)

# Trim cylinder to v ∈ [0,1], u ∈ [0,1] (full period wrapped)
# The v parameter extends along the cylinder's axis
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('periodic_cylinder',{cylinder.ref()},"
    "0.0,1.0,0.0,1.0,.T.,.T.)"
)

# Create a face that wraps the seam
# Boundary at v=0 and v=1 (top and bottom circles), split at u≈0.5
# Create a rectangle with rounded seam corners

# Bottom circle (v=0) from u=0 to u=0.5
p_b0 = f.cartesian_point((1.0, 0.0, 0.0))    # u=0, v=0
p_b1 = f.cartesian_point((0.0, 0.0, 0.0))    # u=0.5 (π), v=0 (opposite side)

# Top circle (v=1) from u=0 to u=0.5
p_t0 = f.cartesian_point((1.0, 0.0, 1.0))    # u=0, v=1
p_t1 = f.cartesian_point((0.0, 0.0, 1.0))    # u=0.5, v=1

loop = f.closed_polyline_loop([p_b0, p_b1, p_t1, p_t0])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
