"""Pmi058 — PMI visibility / configuration loss across saved views.

Catalog claim: PMI annotations defined in one configuration become invisible
(or universally visible) when exported, because the configuration-association
is dropped.

Reproducer recipe: STEP file with draughting_pre_defined_colour and
annotation_plane linked to a representation referenced from one of two
configuration_items.

Byte assertions:
  count_entity_def(b'DRAUGHTING_MODEL') == 2
  contains(b'CONFIGURATION_DESIGN')
  count_entity_def(b'CONFIGURATION_ITEM') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi058",
    defect=(
        "PMI annotation is scoped to one CONFIGURATION_ITEM via CONFIGURATION_DESIGN, "
        "but the configuration-association is dropped on export so annotations become "
        "universally visible across all configurations; two DRAUGHTING_MODELs (one per "
        "saved view) are present but the CONFIGURATION_DESIGN linking the annotation "
        "plane to only one configuration is missing the design reference; receivers must "
        "preserve configuration scope and warn when unsupported; silently universalizing "
        "visibility is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9060=geom_ctx

# ── PMI annotation: annotation curve with DRAUGHTING_PRE_DEFINED_COLOUR ──────
pt_a = f.cartesian_point((0.0, 0.0, 0.0))
pt_b = f.cartesian_point((10.0, 0.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)

# Use DRAUGHTING_PRE_DEFINED_COLOUR (byte assertion target for the recipe).
pre_colour = f._emit_raw("DRAUGHTING_PRE_DEFINED_COLOUR('black')")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{pre_colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)
anno_curve = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader',(#{polyline.eid}),#{psa.eid})"
)

# ANNOTATION_PLANE scoping the annotation to a single view.
ap_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
ap_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
ap_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
ap_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{ap_origin.eid},#{ap_normal.eid},#{ap_xdir.eid})"
)
ann_plane = f._emit_raw(
    f"ANNOTATION_PLANE('config_a_plane',(#{anno_curve.eid}),#{ap_plc.eid})"
)

# ── Two saved-view DRAUGHTING_MODELs ─────────────────────────────────────────
# View A contains the annotation plane; View B does not.
dm_a = f._emit_raw(
    f"DRAUGHTING_MODEL('view_config_a',(#{ann_plane.eid}),#9060)"
)

# Second draughting model for the other saved view (no annotation).
pt_c = f.cartesian_point((20.0, 0.0, 0.0))
pt_d = f.cartesian_point((30.0, 0.0, 0.0))
polyline2 = f._emit_raw(
    f"POLYLINE('',(#{pt_c.eid},#{pt_d.eid}))"
)
anno_curve2 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dummy',(#{polyline2.eid}),#{psa.eid})"
)
dm_b = f._emit_raw(
    f"DRAUGHTING_MODEL('view_config_b',(#{anno_curve2.eid}),#9060)"
)

# ── CONFIGURATION_ITEM × 2 (byte assertion target) ───────────────────────────
# Two product configurations that correspond to the two saved views.
config_item_a = f._emit_raw(
    "CONFIGURATION_ITEM('config_A','view configuration A',#9055,$)"
)
config_item_b = f._emit_raw(
    "CONFIGURATION_ITEM('config_B','view configuration B',#9055,$)"
)

# ── CONFIGURATION_DESIGN (byte assertion target) ──────────────────────────────
# Defect: only one CONFIGURATION_DESIGN is emitted and it no longer carries the
# design reference that binds dm_a exclusively to config_item_a. On export the
# configuration-association is dropped, making the annotation universally visible.
f._emit_raw(
    f"CONFIGURATION_DESIGN(#{config_item_a.eid},#9055)"
)
