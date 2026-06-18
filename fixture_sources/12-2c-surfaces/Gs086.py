"""Gs086 — ShapeAnalysis_Surface.Singularity boundary singularity

Catalog claim: "CYLINDRICAL_SURFACE with v_max=0 (degenerate cap).
Singularity detection iterates interior knots only; explicit boundary
singularities undetected. Trimmed cylinder v∈[0,0] case."

Demonstration: A CYLINDRICAL_SURFACE trimmed by RECTANGULAR_TRIMMED_SURFACE
with v_min=0, v_max=0 (collapsed v domain). A cylinder has singularities at
the poles (v=0 and v=2π or equivalently the north/south caps). The defect
is that Singularity detection only checks interior knots, missing boundary
singularities — in this case the collapsed v=0 is itself a degenerate pole.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs086",
             defect="CYLINDRICAL_SURFACE with degenerate v=0 pole; singularity detection misses boundary")

# Place a cylinder at origin, radius 1.0, along z-axis
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)

# Cylinder radius 1.0
cylinder = f.cylindrical_surface(placement, 1.0)

# Trim to v∈[0,0] — collapse v domain, leaving only the pole at v=0
# u ∈ [0, 2π], but for simplicity we use [0,1] in parameter space
# (u=0 → v-axis, u=1 → v-axis, full period expected but we truncate v)
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('degen_pole',{cylinder.ref()},"
    "0.0,1.0,0.0,0.0,.T.,.T.)"
)

# Face boundary: just a line at the pole (degenerate)
p_pole = f.cartesian_point((1.0, 0.0, 0.0))
v_pole = f.vertex_point(p_pole)

# Degenerate loop: same vertex twice
loop = f.edge_loop([
    f.oriented_edge(f.edge_curve(v_pole, v_pole, f.line(p_pole, f.vector(f.direction((0.0, 0.0, 1.0)), 0.0))), True),
])
fob = f.face_outer_bound(loop)

face = f.advanced_face([fob], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
