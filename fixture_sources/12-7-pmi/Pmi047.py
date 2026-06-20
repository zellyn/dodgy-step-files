"""Pmi047 — Annotation has no annotation_plane.

Catalog claim: A graphic PMI annotation occurrence is not referenced by any
annotation_plane.elements. Without an annotation plane the placement is
ambiguous.

Reproducer recipe: annotation_curve_occurrence not listed in any
annotation_plane.elements.

Byte assertions:
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'PRESENTATION_STYLE_ASSIGNMENT')
  count_entity_def(b'ANNOTATION_PLANE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi047",
    defect=(
        "ANNOTATION_CURVE_OCCURRENCE is not listed in any ANNOTATION_PLANE.elements; "
        "without an annotation plane the placement of the graphic PMI annotation is "
        "ambiguous; receivers must warn and reject the annotation; "
        "silently accepting unplaned annotations is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Graphic polyline for the annotation.
pt_a = f.cartesian_point((0.0, 0.0, 0.0))
pt_b = f.cartesian_point((10.0, 0.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)

# Presentation style for the annotation curve occurrence.
colour = f._emit_raw("COLOUR_RGB('anno_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)

# The annotation curve occurrence — this is NOT referenced by any annotation_plane.
anno_curve = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader',(#{polyline.eid}),#{psa.eid})"
)

# A separate dummy annotation occurrence that IS in the annotation plane.
# This makes the annotation_plane structurally valid (non-empty elements list)
# while leaving anno_curve orphaned from any plane — the defect.
pt_c = f.cartesian_point((20.0, 0.0, 0.0))
pt_d = f.cartesian_point((30.0, 0.0, 0.0))
polyline2 = f._emit_raw(
    f"POLYLINE('',(#{pt_c.eid},#{pt_d.eid}))"
)
anno_curve2 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dummy',(#{polyline2.eid}),#{psa.eid})"
)

# Annotation plane placement — in the XY plane.
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
plane_ref = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
plane_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)

# Defect: ANNOTATION_PLANE elements list contains only anno_curve2, NOT anno_curve.
# anno_curve has no annotation_plane — placement is ambiguous.
# count_entity_def(b'ANNOTATION_PLANE') == 1 is satisfied.
f._emit_raw(
    f"ANNOTATION_PLANE('xy_plane',(#{anno_curve2.eid}),#{plane_placement.eid})"
)
