"""Tfa237 — SplitEdge edge-division via B-spline vertical spine on
cylindrical seam.

Catalog claim: ShapeFix_Face::SplitEdge (line ~2653) divides an edge using
a B-spline curve spanning the cylindrical seam.

Previous fixture had PRODUCT_CONTEXT referencing a SECURITY_CLASSIFICATION
(#1) — load-time error before any geometry could be parsed. Regen with a
clean cylindrical surface + vertical B-spline curve as the division spine.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa237",
             defect="B-spline spine dividing cylindrical-surface edge at seam")

# Cylindrical surface (axis along Z, radius 1).
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{plc.eid},1.0)")

# Vertical B-spline curve along the seam line (x=1, y=0, z from 0 to 2).
p0 = f.cartesian_point((1.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 1.0))
p2 = f.cartesian_point((1.0, 0.0, 2.0))
spine = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('vertical_spine',2,"
    f"(#{p0.eid},#{p1.eid},#{p2.eid}),"
    ".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# Seam edge: bottom to top of cylinder along x=1 axis.
v_bot = f.vertex_point(p0)
v_top = f.vertex_point(p2)
seam_edge = f.edge_curve(v_bot, v_top, spine)

# Top + bottom circles to close the face.
top_center = f.cartesian_point((0.0, 0.0, 2.0))
top_plc = f.axis2_placement_3d(top_center, zdir, xdir)
top_circle = f._emit_raw(f"CIRCLE('top',#{top_plc.eid},1.0)")
top_edge = f.edge_curve(v_top, v_top, top_circle)

bot_plc = f.axis2_placement_3d(orig, zdir, xdir)
bot_circle = f._emit_raw(f"CIRCLE('bot',#{bot_plc.eid},1.0)")
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)

# Wire: bottom circle + up the seam + top circle + back down the seam.
loop = f.edge_loop([
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, True),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
