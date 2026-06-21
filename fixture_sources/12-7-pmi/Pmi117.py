"""Pmi117 — FLAT_PATTERN reference to non-sheet host (host is solid, not surface).

Catalog claim: AP242 flat_pattern requires a sheet-metal surface host, not a
solid. This fixture emits a flat_pattern SHAPE_ASPECT with a descriptive
property host_kind='solid' documenting the host-type contradiction. Receivers
must reject or demote with W_FLAT_PATTERN_HOST_DEMOTED.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi117",
    defect=(
        "flat_pattern SHAPE_ASPECT with host_kind='solid' — flat_pattern "
        "requires a surface-model host, not a solid; "
        "receiver must reject or extract mid-surface with W_FLAT_PATTERN_HOST_DEMOTED"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((50.0, 0.0, 0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0)); p3 = f.cartesian_point((0.0, 50.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
pattern_asp = f._emit_raw("SHAPE_ASPECT('flat_pattern','',#9055,.T.)")
# Defect marker: host is solid, not surface
f._emit_raw("DESCRIPTIVE_REPRESENTATION_ITEM('host_kind','solid')")
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'material_thickness')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('material_thickness',LENGTH_MEASURE(3.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_on_face','flat pattern on host',"
    f"#{host_asp.eid},#{pattern_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('fp_gisu',$,#{pattern_asp.eid},#9061,#{face.eid})"
)
