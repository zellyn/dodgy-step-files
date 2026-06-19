"""Gp028 - Wire crosses periodic-surface seam without explicit seam edge
(pcurve trim range vs vertex angular position mismatch).

Catalog claim (08-occt-gitlog.md G111, Mantis 0026708): A wire bounding a
face on a periodic CYLINDRICAL_SURFACE traverses the U=0/U=2pi seam, but no
seam edge is included. The specific signature: a pcurve LINE trim starts at
u=5.5 with length 1.28, corresponding to angular interval [5.5, 6.78 rad]
(wrapping past 2pi=6.283...), but the 3D vertices have angular positions of
approx -0.78 rad and +0.50 rad (i.e. they straddle the seam). The pcurve
end parameter 6.78 > 2pi means the pcurve crosses the seam, but the receiver
gets no seam edge to bridge the gap in UV. Downstream shell composition sees
an open contour in UV even though the wire is closed in 3D.

Fixture: A cylindrical face with two edges forming a closed 3D loop. The main
edge crosses the seam: its pcurve LINE goes from u=5.5 to u=5.5+1.28=6.78,
crossing 2pi. The return edge closes the loop in 3D with a matching pcurve
going from (6.78,1) back to (5.5,0). No seam edge is present at u=2pi/0.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp028",
    defect=(
        "Cylinder face wire crosses U=0/2pi seam without seam edge: pcurve LINE "
        "runs u=5.5 to u=6.78 (crossing 2pi=6.283); vertex angles approx -0.78 "
        "and +0.50 rad; receiver must insert seam edge but none is provided"
    ),
)

# Cylindrical surface: radius 1, axis Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f.cylindrical_surface(plc, 1.0)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertex angles from catalog: start ~= -0.78 rad = 5.50 rad mod 2pi, end ~= +0.50 rad.
# 3D positions on cylinder radius 1:
#   v_start: angle=5.50 rad, z=0 -> (cos(5.5), sin(5.5), 0)
#   v_end:   angle=0.50 rad, z=1 -> (cos(0.5), sin(0.5), 1)
angle_start = 5.50
angle_end   = 0.50
cs = math.cos(angle_start)
ss = math.sin(angle_start)
ce = math.cos(angle_end)
se = math.sin(angle_end)

p_start_3d = f.cartesian_point((cs, ss, 0.0))
p_end_3d   = f.cartesian_point((ce, se, 1.0))
v_start    = f.vertex_point(p_start_3d)
v_end      = f.vertex_point(p_end_3d)

# ---- Main edge: crosses the seam ----
# 3D curve: a straight line from v_start to v_end.
dx = ce - cs
dy = se - ss
dz = 1.0
mag_3d = math.sqrt(dx*dx + dy*dy + dz*dz)
d_fwd   = f.direction((dx / mag_3d, dy / mag_3d, dz / mag_3d))
vec_fwd = f.vector(d_fwd, mag_3d)
line_fwd_3d = f.line(p_start_3d, vec_fwd)

# THE DEFECT: pcurve LINE starts at (5.5, 0.0) with end at (6.78, 1.0).
# Delta-u = 1.28 (= 6.78 - 5.5), delta-v = 1.0.
# 6.78 > 2pi = 6.2831... so this pcurve crosses the seam.
# No seam edge at u=2pi is present to close the UV contour.
delta_u = 1.28   # 5.5 + 1.28 = 6.78, crossing 2pi=6.283
delta_v = 1.0
mag_pc  = math.sqrt(delta_u*delta_u + delta_v*delta_v)
pc_fwd_start = f.cartesian_point((5.5, 0.0))
pc_fwd_dir   = f.direction((delta_u / mag_pc, delta_v / mag_pc))
pc_fwd_vec   = f.vector(pc_fwd_dir, mag_pc)
pc_fwd_line  = f.line(pc_fwd_start, pc_fwd_vec)
pc_fwd_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_seam_cross',(#{pc_fwd_line.eid}),#{prc.eid})"
)
pcurve_fwd = f._emit_raw(f"PCURVE('seam_cross',#{cyl.eid},#{pc_fwd_def.eid})")
sc_fwd = f._emit_raw(
    f"SURFACE_CURVE('seam_crossing',#{line_fwd_3d.eid},(#{pcurve_fwd.eid}),.PCURVE_S1.)"
)
edge_fwd = f._emit_raw(
    f"EDGE_CURVE('seam_cross',#{v_start.eid},#{v_end.eid},#{sc_fwd.eid},.T.)"
)

# ---- Return edge: closes the loop in 3D and UV (no seam edge present) ----
# 3D: straight line back from v_end to v_start.
d_bk    = f.direction((-dx / mag_3d, -dy / mag_3d, -dz / mag_3d))
vec_bk  = f.vector(d_bk, mag_3d)
line_bk_3d = f.line(p_end_3d, vec_bk)
# Pcurve: from (6.78, 1.0) back to (5.5, 0.0).
pc_bk_start = f.cartesian_point((6.78, 1.0))
pc_bk_dir   = f.direction((-delta_u / mag_pc, -delta_v / mag_pc))
pc_bk_vec   = f.vector(pc_bk_dir, mag_pc)
pc_bk_line  = f.line(pc_bk_start, pc_bk_vec)
pc_bk_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_back',(#{pc_bk_line.eid}),#{prc.eid})"
)
pcurve_bk = f._emit_raw(f"PCURVE('back',#{cyl.eid},#{pc_bk_def.eid})")
sc_bk = f._emit_raw(
    f"SURFACE_CURVE('back',#{line_bk_3d.eid},(#{pcurve_bk.eid}),.PCURVE_S1.)"
)
edge_bk = f._emit_raw(
    f"EDGE_CURVE('back',#{v_end.eid},#{v_start.eid},#{sc_bk.eid},.T.)"
)

# Loop: edge_fwd (v_start->v_end) then edge_bk (v_end->v_start).
# Closed in 3D, but the UV contour for edge_fwd crosses 2pi without a seam edge.
loop = f.edge_loop([
    f.oriented_edge(edge_fwd, True),   # pcurve u=5.5->6.78, crosses 2pi
    f.oriented_edge(edge_bk,  True),   # pcurve u=6.78->5.5
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
