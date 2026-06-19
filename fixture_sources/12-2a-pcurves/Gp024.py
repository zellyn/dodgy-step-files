"""Gp024 - Pcurve refit after non-uniform x1000 scale produces large errors.

Catalog claim (14-brlcad-rhino.md K016): When a Rhino user opens a STEP file
with mm tolerance 0.0001, scales the model by x1000, then re-exports with
"export parameter space curves" enabled, the pcurves are not properly refit:
the pcurve parameterisation magnitude is wrong (not rescaled with the geometry),
so the distance from the pcurve end point to the 3D edge endpoint is ~0.05,
far exceeding the (unrescaled) edge tolerance of 0.0001.

Specific error message: "Distance from end of trim to 3D edge is 0.05
(edge tol = 0.0001)".

Fixture: A cylindrical surface, radius 1000 (original radius 1 scaled x1000).
The edge tolerance is 0.0001 (not rescaled). The pcurve LINE for a horizontal
arc edge is parameterised with magnitude (pi - 0.05) instead of the correct
pi, so the pcurve endpoint is 0.05 short in u-parameter. This replicates the
post-scale mismatch. EDGE_CURVE carries SameParameter=.T. despite this,
matching Rhino export behavior.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp024",
    defect=(
        "After x1000 scale: EDGE_CURVE tolerance stays 0.0001 but pcurve LINE "
        "magnitude is (pi-0.05) instead of pi; pcurve end is 0.05 from 3D edge "
        "end; SameParameter=.T. asserted despite mismatch"
    ),
)

# Cylindrical surface: radius 1000 (original radius 1 scaled x1000), axis Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f.cylindrical_surface(plc, 1000.0)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Edge: half-circle arc from (1000,0,500) to (-1000,0,500) at v=500.
# In UV: u from 0 to pi, v=500.
p_start_3d = f.cartesian_point(( 1000.0, 0.0, 500.0))
p_end_3d   = f.cartesian_point((-1000.0, 0.0, 500.0))
v_start    = f.vertex_point(p_start_3d)
v_end      = f.vertex_point(p_end_3d)

# 3D curve: a full circle (vertices define the half-arc trim implicitly).
arc_ctr   = f.cartesian_point((0.0, 0.0, 500.0))
arc_zaxis = f.direction((0.0, 0.0, 1.0))
arc_xaxis = f.direction((1.0, 0.0, 0.0))
arc_axis  = f.axis2_placement_3d(arc_ctr, arc_zaxis, arc_xaxis)
circle_3d = f.circle(arc_axis, 1000.0)

# THE DEFECT: pcurve LINE in UV starts at (0, 500) with direction (1,0) and
# magnitude (pi - 0.05) instead of pi. The correct endpoint would be (pi, 500)
# but the defective pcurve ends at (pi-0.05, 500), a discrepancy of 0.05 in u.
# On the cylinder surface u is the angle parameter, so 0.05 radian corresponds
# to ~50 mm arc length at radius 1000 >> tolerance 0.0001.
pc_start_2d = f.cartesian_point((0.0, 500.0))
pc_dir_2d   = f.direction((1.0, 0.0))
pc_vec_2d   = f.vector(pc_dir_2d, math.pi - 0.05)   # DEFECT: should be math.pi
pc_line_2d  = f.line(pc_start_2d, pc_vec_2d)
pc_def      = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_scale_err',(#{pc_line_2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def.eid})")

sc = f._emit_raw(
    f"SURFACE_CURVE('scaled_arc',#{circle_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# SameParameter=.T. (Rhino export behavior even though parameterisations differ)
edge = f._emit_raw(
    f"EDGE_CURVE('scaled_edge',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
