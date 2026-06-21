"""Pmi116 — FLAT_PATTERN with disjoint sub-features (no connecting bend line).

Catalog claim: AP242 flat_pattern bend graph must be connected; every panel
must be reachable from every other via at least one bend. This fixture emits
two panels with no bend_line connecting them. Receivers must reject or split
into N separate flat_pattern groups.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi116",
    defect=(
        "flat_pattern SHAPE_ASPECT with two panels (panel_A, panel_B) linked as "
        "sub-features but no bend_line SHAPE_ASPECT connecting them; "
        "flat_pattern_bend_lines='0'; disconnected panel graph"
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
panel_A     = f._emit_raw("SHAPE_ASPECT('panel_A','flat panel A',#9055,.T.)")
panel_B     = f._emit_raw("SHAPE_ASPECT('panel_B','flat panel B',#9055,.T.)")
f._emit_raw("DESCRIPTIVE_REPRESENTATION_ITEM('flat_pattern_bend_lines','0')")
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_has_A','flat pattern has panel A',"
    f"#{pattern_asp.eid},#{panel_A.eid})"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_has_B','flat pattern has panel B',"
    f"#{pattern_asp.eid},#{panel_B.eid})"
)
# NO bend_line connecting panel_A and panel_B — the defect
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_on_face','flat pattern on host',"
    f"#{host_asp.eid},#{pattern_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('fp_gisu',$,#{pattern_asp.eid},#9061,#{face.eid})"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'material_thickness')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('material_thickness',LENGTH_MEASURE(2.0),#9056)"
)
