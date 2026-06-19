"""Gp016 — Pcurve in shifted/transformed UV frame relative to host surface.

Catalog claim: A PCURVE expressed in a shifted UV coordinate frame relative
to the host surface's natural UV — the pcurve LINE on a planar face starts at
(u=10, v=5) while the 3D edge runs from (0,0,0) to (1,0,0); the pcurve is
offset into a UV region that does not contain the lift of the 3D curve. Common
output of IGES BRep mode where pcurves arrive in a translated frame relative to
the host surface's natural UV. Without re-baselining, the pcurve evaluates to
wrong UV positions and vertex tolerances bloat.

Fixture: A planar face (z=0 plane) with a single edge from (0,0,0) to (1,0,0)
in 3D. The natural UV of the PLANE places this edge at v=0, u in [0,1]. But
the PCURVE LINE is expressed starting at (u=10, v=5) — offset by 10 units in
u and 5 units in v — displaced into a UV region where the natural surface
coordinate of the 3D edge does not lie. This is the specific IGES BRep mode
defect: pcurve offset into an alien UV frame.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp016",
             defect="PCURVE LINE origin shifted to (u=10,v=5) on PLANE whose 3D edge lies at (u=0,v=0): IGES-style alien UV frame")

# Host surface: a PLANE through origin, normal along Z, x-axis along X.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
host_plane = f.plane(plc)

# 3D edge: from (0,0,0) to (1,0,0) — lies along u-axis of the plane's
# natural UV at v=0. In the plane's natural UV, this is (u=0,v=0)→(u=1,v=0).
p_start_3d = f.cartesian_point((0.0, 0.0, 0.0))
p_end_3d = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start_3d)
v_end = f.vertex_point(p_end_3d)

line_dir_3d = f.direction((1.0, 0.0, 0.0))
line_vec_3d = f.vector(line_dir_3d, 1.0)
line_3d = f.line(p_start_3d, line_vec_3d)

# UV parametric context (2D)
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# THE DEFECT: PCURVE LINE in a shifted UV frame.
# Correct origin would be (0.0, 0.0) in the plane's natural UV.
# IGES BRep mode has written the pcurve origin at (10.0, 5.0) — offset by
# 10 in u and 5 in v — so the pcurve is entirely in the wrong UV region.
# The 3D edge maps to u∈[0,1],v=0 but the pcurve claims u∈[10,11],v=5.
pc_origin_2d = f.cartesian_point((10.0, 5.0))   # WRONG: should be (0.0, 0.0)
pc_dir_2d = f.direction((1.0, 0.0))
pc_vec_2d = f.vector(pc_dir_2d, 1.0)
pc_line_2d = f.line(pc_origin_2d, pc_vec_2d)

pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('shifted_uv',(#{pc_line_2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('',#{host_plane.eid},#{pc_def.eid})")

# SURFACE_CURVE and EDGE_CURVE
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], host_plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
