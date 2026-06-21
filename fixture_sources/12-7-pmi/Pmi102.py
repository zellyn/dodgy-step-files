"""Pmi102 — GROOVE radial depth exceeds cylindrical host radius (depth wraps past axis).

Catalog claim: AP242 GROOVE on a cylindrical host requires groove_radial_depth
< host_cylinder_radius. This fixture has a cylinder of radius=10 mm with a
GROOVE whose radial_depth=15 mm — the groove cuts through the cylinder
centerline. Receivers must reject or clamp with a deterministic warning.

Byte assertions:
  contains(b'GROOVE')
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'depth_DEFECT_exceeds_radius')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(6) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi102",
    defect=(
        "GROOVE on cylinder (radius=10 mm) with groove_radial_depth=15 mm; "
        "depth exceeds host radius — groove cuts through centerline; "
        "receiver must reject or clamp with deterministic warning"
    ),
)

# ── Cylindrical host face: radius=10, height=30 ──────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_top  = f.cartesian_point((0.0, 0.0, 30.0))
cyl_axis = f.direction((0.0, 0.0, 1.0))
cyl_ref  = f.direction((1.0, 0.0, 0.0))
cyl_base_plc = f.axis2_placement_3d(cyl_orig, cyl_axis, cyl_ref)
cyl_top_plc  = f.axis2_placement_3d(cyl_top,  cyl_axis, cyl_ref)
cyl_surf = f.cylindrical_surface(cyl_base_plc, 10.0)

# Seam vertices.
seam_bot = f.cartesian_point((10.0, 0.0, 0.0))
seam_top = f.cartesian_point((10.0, 0.0, 30.0))
v_bot    = f.vertex_point(seam_bot)
v_top    = f.vertex_point(seam_top)

# Two full-circle edges (bottom and top seam circles).
bot_circle = f.circle(cyl_base_plc, 10.0)
top_circle = f.circle(cyl_top_plc,  10.0)
bot_ec = f.edge_curve(v_bot, v_bot, bot_circle)  # full circle: start==end
top_ec = f.edge_curve(v_top, v_top, top_circle)

# Vertical seam edge.
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 30.0)
seam_line = f.line(seam_bot, seam_vec)
seam_ec   = f.edge_curve(v_bot, v_top, seam_line)

# Edge loop: bottom_circle (T) → seam_up (T) → top_circle (F) → seam_down (F)
loop = f.edge_loop([
    f.oriented_edge(bot_ec, True),
    f.oriented_edge(seam_ec, True),
    f.oriented_edge(top_ec, False),
    f.oriented_edge(seam_ec, False),
])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], cyl_surf, name="host_cyl_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: GROOVE with radial_depth (15) exceeding host radius (10) ─────────
host_asp   = f._emit_raw("SHAPE_ASPECT('host_cyl_face','',#9055,.T.)")
groove_asp = f._emit_raw("SHAPE_ASPECT('GROOVE','circumferential groove depth defect',#9055,.T.)")

f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'groove_width')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('groove_width',LENGTH_MEASURE(3.0),#9056)"
)
# radial_depth = 15 mm > host radius 10 mm — DEFECT (wraps past axis)
f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'groove_radial_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('depth_DEFECT_exceeds_radius',LENGTH_MEASURE(15.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'host_cylinder_radius')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('host_cylinder_radius',LENGTH_MEASURE(10.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('groove_on_cyl','groove on cylinder host',"
    f"#{host_asp.eid},#{groove_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('groove_gisu',$,#{groove_asp.eid},#9061,#{face.eid})"
)
