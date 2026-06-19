"""Gp012 — SURFACE_CURVE / seam-curve associated_geometry list contains a null $ entry.

Catalog claim: A SEAM_CURVE on a periodic (cylindrical) surface should carry
two pcurves in its associated_geometry set, but the list contains a PCURVE
followed by a $ (null) entry. The second bank is missing entirely; a
translator must synthesize it by period-shifting the present pcurve, or the
seam fails to register.

Fixture: Cylindrical face with a seam edge whose SEAM_CURVE reads:
  SEAM_CURVE('',#3d,(#pc1, $),.PCURVE_S1.)
The null $ in the second slot is the exact defect.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp012",
             defect="SEAM_CURVE associated_geometry list has null $ for second pcurve slot")

# Cylindrical surface: radius 1, axis along Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# 3D circle at z=0.5 — the seam edge
circle_orig = f.cartesian_point((0.0, 0.0, 0.5))
circle_zdir = f.direction((0.0, 0.0, 1.0))
circle_xdir = f.direction((1.0, 0.0, 0.0))
circle_plc = f.axis2_placement_3d(circle_orig, circle_zdir, circle_xdir)
circle_3d = f.circle(circle_plc, 1.0)

seam_pt = f.cartesian_point((1.0, 0.0, 0.5))
v_seam = f.vertex_point(seam_pt)

# The one valid pcurve (bank 1): horizontal line in UV at v=0.5, u from 0 to 2π
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
pc_start_2d = f.cartesian_point((0.0, 0.5))
pc_dir_2d = f.direction((1.0, 0.0))
pc_vec_2d = f.vector(pc_dir_2d, 6.283185307)
pc_line_2d = f.line(pc_start_2d, pc_vec_2d)
pc_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bank1',(#{pc_line_2d.eid}),#{prc.eid})"
)
pcurve1 = f._emit_raw(f"PCURVE('bank1',#{cyl.eid},#{pc_defrep.eid})")

# DEFECT: second slot is $ (null) — bank 2 is missing
seam_curve = f._emit_raw(
    f"SEAM_CURVE('',#{circle_3d.eid},(#{pcurve1.eid},$),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_seam.eid},#{v_seam.eid},#{seam_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(seam_edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
