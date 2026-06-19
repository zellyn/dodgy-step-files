"""Gp021 — 3D curve and pcurve on same edge disagree about edge location
(skewed/off-unit pcurve LINE).

Catalog claim: For one edge, the 3D-curve evaluation and the pcurve lifted
through the host surface land at different points — the two representations of
the same edge disagree about where the edge actually is, by more than the
edge's tolerance. The specific catalog shape: pcurve LINE whose DIRECTION
ratios are slightly skewed from the canonical axis (e.g. (0.99875, 0.04994)
instead of (1, 0)), so the lifted pcurve diverges from the 3D LINE along the
edge. Senders that recompute pcurve and 3D curve independently introduce
this divergence.

Fixture: A cylindrical surface with one vertical 3D LINE edge at the seam
(u=0), running from (1,0,0) to (1,0,1). The 3D curve is a canonical vertical
line (direction (0,0,1)). The pcurve LINE in UV has direction (0.99875, 0.04994)
instead of (0, 1) — skewed by ~2.9° — so by mid-edge the lifted pcurve has
drifted ~0.025 in u away from the 3D curve's actual position on the surface.
The divergence >> 1e-6 declared tolerance.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp021",
             defect="PCURVE LINE direction (0.99875,0.04994) instead of (0,1): lifted pcurve diverges from 3D LINE by ~0.025 in U at mid-edge, exceeds declared tolerance 1e-6")

# Host: cylindrical surface, radius 1, axis Z, u=angle, v=height.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# 3D edge: vertical line at seam, from (1,0,0) to (1,0,1).
# 3D direction is canonical: (0, 0, 1).
p_start_3d = f.cartesian_point((1.0, 0.0, 0.0))
p_end_3d = f.cartesian_point((1.0, 0.0, 1.0))
v_start = f.vertex_point(p_start_3d)
v_end = f.vertex_point(p_end_3d)
line_dir_3d = f.direction((0.0, 0.0, 1.0))
line_vec_3d = f.vector(line_dir_3d, 1.0)
line_3d = f.line(p_start_3d, line_vec_3d)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# THE DEFECT: pcurve LINE with skewed direction (0.99875, 0.04994) in UV.
# Correct direction would be (0.0, 1.0) — purely in the v direction.
# Instead the u-component is 0.99875 and v-component is 0.04994:
#   at parameter t=0.5, the pcurve is at (u=0+0.5*0.99875, v=0+0.5*0.04994)
#                                       = (u=0.499, v=0.025)
# while the correct position on the lifted 3D line is (u=0, v=0.5).
# Divergence at mid-edge: ΔU≈0.499, ΔV≈0.475 — far beyond 1e-6 tolerance.
# This models the "independently recomputed pcurve with slight skew" defect.
pc_start_2d = f.cartesian_point((0.0, 0.0))
# Skewed direction: (0.99875, 0.04994) ≈ unit vector at ~2.9° from u-axis,
# but should be (0.0, 1.0) for a vertical seam edge.
pc_dir_2d = f.direction((0.99875, 0.04994))
pc_vec_2d = f.vector(pc_dir_2d, 1.0)
pc_line_2d = f.line(pc_start_2d, pc_vec_2d)

pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('skewed_pcurve',(#{pc_line_2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
