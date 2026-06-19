"""Gp011 — Seam curve with same pcurve referenced twice.

Catalog claim: A SEAM_CURVE must carry two distinct pcurves (one for each
bank of the seam), but the sender wrote the same PCURVE handle in both
slots of associated_geometry. The two banks cannot be disambiguated, and
the wire fails to close around the periodic surface.

Fixture: A cylindrical surface with a seam edge. The SEAM_CURVE's
associated_geometry list contains the same PCURVE reference twice:
  SEAM_CURVE('',#3d,(#pc, #pc),.PCURVE_S1.)
This means the second bank (which should be the period-shifted copy, i.e.
u = 2π) is aliased to the first bank (u = 0), so the wire cannot close.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp011",
             defect="SEAM_CURVE associated_geometry contains same PCURVE twice (both banks aliased)")

# Cylindrical surface: radius 1, axis along Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# 3D circle at z=0 — the seam edge goes all the way around the cylinder
# (start and end coincide: full circle, so v_start = v_end at seam)
circle_orig = f.cartesian_point((0.0, 0.0, 0.5))
circle_zdir = f.direction((0.0, 0.0, 1.0))
circle_xdir = f.direction((1.0, 0.0, 0.0))
circle_plc = f.axis2_placement_3d(circle_orig, circle_zdir, circle_xdir)
circle_3d = f.circle(circle_plc, 1.0)

# The seam vertex (start == end for a full-circle seam)
seam_pt = f.cartesian_point((1.0, 0.0, 0.5))
v_seam = f.vertex_point(seam_pt)

# ONE pcurve for u=0 bank: a vertical line at u=0 in UV space (v goes 0→1)
# On a cylinder u=angle, v=height; seam at u=0 is a vertical line
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# pcurve LINE in UV: from (0,0) going in u-direction (actually seam runs
# along v at u=0, so direction is (0,1) in UV = horizontal seam line)
# For a horizontal circle edge: pcurve goes from (0, 0.5) to (2π, 0.5)
pc_start_2d = f.cartesian_point((0.0, 0.5))
pc_dir_2d = f.direction((1.0, 0.0))
pc_vec_2d = f.vector(pc_dir_2d, 6.283185307)
pc_line_2d = f.line(pc_start_2d, pc_vec_2d)
pc_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bank1',(#{pc_line_2d.eid}),#{prc.eid})"
)
# ONE pcurve — this is the defect: both banks reference this same entity
pcurve = f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_defrep.eid})")

# SEAM_CURVE with SAME pcurve in both slots — the defect
seam_curve = f._emit_raw(
    f"SEAM_CURVE('',#{circle_3d.eid},(#{pcurve.eid},#{pcurve.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_seam.eid},#{v_seam.eid},#{seam_curve.eid},.T.)"
)

# Build a minimal face on the cylinder using the seam edge
loop = f.edge_loop([f.oriented_edge(seam_edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
