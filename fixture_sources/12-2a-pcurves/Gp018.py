"""Gp018 — Pcurve gaps / nearly-duplicate pcurves near periodic boundary
after B_SPLINE_SURFACE conversion.

Catalog claim: Converting a periodic surface (cylinder) into an explicit
B_SPLINE_SURFACE_WITH_KNOTS yields a non-periodic NURBS. Pcurves whose
endpoints landed on the period boundary end up with a small gap at wrap-around:
two pcurves on the same 3D edge end up nearly coincident (e.g. one at u=0 and
the other at u=0.999, within 0.001 in U) but not identical — nearly-duplicate
pcurves straddling the converted seam.

Fixture: A non-periodic B-spline surface approximating a cylinder (radius 1,
height 1). The seam EDGE_CURVE carries TWO pcurves: one at u=0.0 (correct
bank) and one at u=0.999 (the defective near-duplicate that should be u=1.0).
These two pcurves are nearly coincident in UV but not equal — a 0.001 gap in U
that the periodic-to-NURBS conversion introduced. The receiver must bridge or
reject this UV gap.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp018",
             defect="Two nearly-duplicate pcurves (u=0.0 and u=0.999) on same non-periodic B-spline surface after periodic-to-NURBS conversion: UV gap 0.001")

# Non-periodic B-spline surface approximating a unit cylinder.
# 9 columns in u (degree 2, clamped with knots [0,1]), 2 rows in v (degree 1).
def xy(angle, z):
    return f.cartesian_point((math.cos(angle), math.sin(angle), z))

angles = [0.0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi,
          5*math.pi/4, 3*math.pi/2, 7*math.pi/4, 2*math.pi]
net = [[xy(a, 0.0), xy(a, 1.0)] for a in angles]

host_surface = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=net,
    u_multiplicities=[3, 1, 1, 1, 1, 1, 1, 3],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
)

# Seam vertices: (1,0,0) bottom and (1,0,1) top — same 3D points at u=0 and u=1.
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# 3D seam line from (1,0,0) to (1,0,1).
d_up = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)
seam_line_3d = f.line(p_bot, vec_up)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Pcurve at u=0.0 — the correct "first bank" seam pcurve.
pc_u0_start = f.cartesian_point((0.0, 0.0))
pc_u0_dir = f.direction((0.0, 1.0))
pc_u0_vec = f.vector(pc_u0_dir, 1.0)
pc_u0_line = f.line(pc_u0_start, pc_u0_vec)
pc_u0_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_u0',(#{pc_u0_line.eid}),#{prc.eid})"
)
pcurve_u0 = f._emit_raw(
    f"PCURVE('bank_u0',#{host_surface.eid},#{pc_u0_def.eid})"
)

# THE DEFECT: second pcurve at u=0.999 instead of u=1.0.
# The periodic-to-NURBS conversion left a 0.001 UV gap:
# the "far bank" pcurve should be at u=1.0 but landed at u=0.999.
# These two pcurves are nearly-duplicate, not at the expected period boundary.
pc_u1_start = f.cartesian_point((0.999, 0.0))   # DEFECT: should be 1.0
pc_u1_dir = f.direction((0.0, 1.0))
pc_u1_vec = f.vector(pc_u1_dir, 1.0)
pc_u1_line = f.line(pc_u1_start, pc_u1_vec)
pc_u1_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_u1_near_dup',(#{pc_u1_line.eid}),#{prc.eid})"
)
pcurve_u1 = f._emit_raw(
    f"PCURVE('bank_u0999',#{host_surface.eid},#{pc_u1_def.eid})"
)

# SURFACE_CURVE carries both nearly-duplicate pcurves — the specific defect.
seam_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('seam_converted',#{seam_line_3d.eid},"
    f"(#{pcurve_u0.eid},#{pcurve_u1.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_bot.eid},#{v_top.eid},#{seam_surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(seam_edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], host_surface)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
