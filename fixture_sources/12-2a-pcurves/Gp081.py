"""Gp081 — CheckSameParameter periodic-shift normalization.

Catalog claim: periodic-surface edge whose 3D and 2D parameters disagree
by exactly 2π (one full period); CheckSameParameter fails to normalize
periodic parameters before comparison, incorrectly reporting mismatch.

Previous fixture used PLANE (non-periodic) — the claim's premise wasn't
even representable. Regen on CYLINDRICAL_SURFACE: a real periodic surface
where U is the cylinder angle and a pcurve LINE in UV-space can be
period-shifted by 2π without changing the 3D geometry.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp081",
             defect="pcurve U-parameter shifted by 2π on periodic cylindrical surface")

# Cylindrical surface: axis along Z, radius 1, periodic in U with period 2π.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cylinder',#{plc.eid},1.0)")

# 3D edge: half-circle in the XY plane (z=0), from (1,0,0) to (-1,0,0).
p_start = f.cartesian_point((1.0, 0.0, 0.0))
p_end = f.cartesian_point((-1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
circ_plc = f.axis2_placement_3d(orig, zdir, xdir)
circle3d = f._emit_raw(f"CIRCLE('arc',#{circ_plc.eid},1.0)")

# 2D pcurve: LINE in UV space starting at U=2π (one full period past 0).
# Natural 3D param: U runs from 0 to π for the half-circle.
# Period-shifted 2D: U runs from 2π to 3π (same shape, +2π shift).
# CheckSameParameter without normalization would see mismatch between
# 3D-param-0 and 2D-param-2π.
uv_start = f.cartesian_point((2.0 * pi, 0.0))   # 2D start at U=2π
udir = f.direction((1.0, 0.0))                  # 2D direction in U
uvec = f.vector(udir, pi)
uline = f.line(uv_start, uvec)
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('uv_ctx','UV'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('shifted_uv',(#{uline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(
    f"PCURVE('pcurve_shifted_2pi',#{cyl.eid},#{defrep.eid})"
)
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('edge_geom',#{circle3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge_arc = f._emit_raw(
    f"EDGE_CURVE('half_circle_edge',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

# Close the wire with a top arc + two seam edges so the fixture is consumable.
# Top circle at z=2.
p_top_start = f.cartesian_point((1.0, 0.0, 2.0))
p_top_end = f.cartesian_point((-1.0, 0.0, 2.0))
v_top_start = f.vertex_point(p_top_start)
v_top_end = f.vertex_point(p_top_end)
top_circ_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 2.0)), zdir, xdir)
top_circle = f._emit_raw(f"CIRCLE('top_arc',#{top_circ_plc.eid},1.0)")
top_edge = f.edge_curve(v_top_start, v_top_end, top_circle)

# Seam edges connecting top and bottom.
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 2.0)
seam1_line = f.line(p_start, seam_vec)
seam1 = f.edge_curve(v_start, v_top_start, seam1_line)
seam2_line = f.line(p_end, seam_vec)
seam2 = f.edge_curve(v_end, v_top_end, seam2_line)

loop = f.edge_loop([
    f.oriented_edge(edge_arc, True),
    f.oriented_edge(seam2, True),
    f.oriented_edge(top_edge, False),
    f.oriented_edge(seam1, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
