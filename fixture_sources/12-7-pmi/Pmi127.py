"""Pmi127 — MARKING with empty inscribed text but non-zero font size.

Catalog claim: AP242 marking implicit invariant: non-zero font_size must pair
with non-empty text. This fixture emits marking_text='' (empty string) with
font_size=5mm. Receivers must reject as malformed; never silently render a
zero-area bounding box.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi127",
    defect=(
        "marking SHAPE_ASPECT with marking_text='' (empty string) but font_size=5mm; "
        "non-zero font size contradicts empty text — receiver must reject"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((30.0, 0.0, 0.0))
p2 = f.cartesian_point((30.0, 30.0, 0.0)); p3 = f.cartesian_point((0.0, 30.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
marking_asp = f._emit_raw("SHAPE_ASPECT('marking','',#9055,.T.)")

# DEFECT: marking_text is empty string but font_size is non-zero
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('marking_text','')"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{marking_asp.eid},'font_size')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('font_size',LENGTH_MEASURE(5.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('marking_on_face','marking on host',"
    f"#{host_asp.eid},#{marking_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('marking_gisu',$,#{marking_asp.eid},#9061,#{face.eid})"
)
