"""Gp020 — 2D gap between adjacent edges in wire — pcurves disagree in UV.

Catalog claim: Two consecutive edges of a wire share a VERTEX_POINT in 3D
(so the wire is connected in 3D), but their pcurve evaluations on the host
surface at that shared vertex land at different UV positions by more than
tolerance (ΔUV > 1e-3). This is a parametric-space open wire, not a 3D gap.

Fixture: A cylindrical surface with two edges forming an L-shaped wire. Both
edges share a common VERTEX_POINT at (1,0,0.5) in 3D. Edge1 is a vertical
line from (1,0,0) to (1,0,0.5) with pcurve at u=0, v∈[0,0.5]. Edge2 is a
horizontal arc from (1,0,0.5) going around in 3D. Its pcurve starts at
(u=0.05, v=0.5) — offset by 0.05 in u from where edge1's pcurve ends (u=0,
v=0.5). The 3D endpoints coincide exactly (same VERTEX_POINT), but the pcurve
endpoints at that vertex differ by ΔU=0.05 > 1e-3, creating a UV gap.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(catalog_id="Gp020",
             defect="Two edges share 3D VERTEX_POINT but pcurves disagree at that vertex: edge1 ends at (u=0,v=0.5), edge2 starts at (u=0.05,v=0.5) — UV gap ΔU=0.05")

# Host: cylindrical surface, radius 1, axis Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# Vertices: bottom (1,0,0), shared middle (1,0,0.5), end (−1,0,0.5).
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_mid = f.cartesian_point((1.0, 0.0, 0.5))
p_end = f.cartesian_point((-1.0, 0.0, 0.5))
v_bot = f.vertex_point(p_bot)
v_mid = f.vertex_point(p_mid)    # shared 3D vertex between edge1 and edge2
v_end = f.vertex_point(p_end)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ------- Edge1: vertical line along the cylinder seam (u=0), v from 0 to 0.5 --------
# 3D: line from (1,0,0) to (1,0,0.5)
e1_dir3d = f.direction((0.0, 0.0, 1.0))
e1_vec3d = f.vector(e1_dir3d, 0.5)
e1_line3d = f.line(p_bot, e1_vec3d)

# Pcurve for edge1: 2D line at u=0, v∈[0,0.5] — the endpoint is (u=0, v=0.5).
e1_pc_orig = f.cartesian_point((0.0, 0.0))
e1_pc_dir = f.direction((0.0, 1.0))
e1_pc_vec = f.vector(e1_pc_dir, 0.5)
e1_pc_line = f.line(e1_pc_orig, e1_pc_vec)
e1_pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('e1_pc',(#{e1_pc_line.eid}),#{prc.eid})"
)
e1_pcurve = f._emit_raw(f"PCURVE('e1_seam',#{cyl.eid},#{e1_pc_def.eid})")
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{e1_line3d.eid},(#{e1_pcurve.eid}),.PCURVE_S1.)"
)
e1_edge = f._emit_raw(
    f"EDGE_CURVE('e1',#{v_bot.eid},#{v_mid.eid},#{e1_sc.eid},.T.)"
)

# ------- Edge2: arc from (1,0,0.5) to (-1,0,0.5), half circle at z=0.5 ---------
# 3D: semicircle arc
arc_center = f.cartesian_point((0.0, 0.0, 0.5))
arc_axis = f.axis2_placement_3d(
    arc_center,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
)
arc_circle = f._emit_raw(f"CIRCLE('arc',#{arc_axis.eid},1.0)")

# THE DEFECT: edge2's pcurve at the shared vertex starts at (u=0.05, v=0.5)
# instead of (u=0.0, v=0.5). The 3D endpoint is the same VERTEX_POINT v_mid
# but in UV the pcurve starts 0.05 away from where edge1's pcurve ended (0.0, 0.5).
# This ΔU=0.05 >> tolerance creates the 2D wire gap.
e2_pc_orig = f.cartesian_point((0.05, 0.5))   # DEFECT: should be (0.0, 0.5)
e2_pc_dir = f.direction((1.0, 0.0))
e2_pc_vec = f.vector(e2_pc_dir, math.pi)
e2_pc_line = f.line(e2_pc_orig, e2_pc_vec)
e2_pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('e2_pc_gap',(#{e2_pc_line.eid}),#{prc.eid})"
)
e2_pcurve = f._emit_raw(f"PCURVE('e2_arc',#{cyl.eid},#{e2_pc_def.eid})")
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc_circle.eid},(#{e2_pcurve.eid}),.PCURVE_S1.)"
)
e2_edge = f._emit_raw(
    f"EDGE_CURVE('e2',#{v_mid.eid},#{v_end.eid},#{e2_sc.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e1_edge, True),
    f.oriented_edge(e2_edge, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
