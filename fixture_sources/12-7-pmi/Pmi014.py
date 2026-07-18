"""Pmi014 — annotation_plane: plane vs planar_box ambiguity.

Catalog claim: An annotation_plane may be defined either by an unbounded plane
or by a planar_box (axis placement + sizes). Receivers that support only one
form lose the bounded-rectangle hint or fail to import unbounded annotation
planes.

Reproducer recipe: Two ANNOTATION_PLANEs under the same draughting_model — one
using an unbounded PLANE, one using a PLANAR_BOX.

Byte assertions:
  count_entity_def(b'ANNOTATION_PLANE') == 2
  contains(b'PLANAR_BOX')
  contains(b'PLANE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi014",
    defect=(
        "two ANNOTATION_PLANEs: one unbounded PLANE, one PLANAR_BOX; "
        "receivers supporting only one form lose the bounded hint or fail "
        "to import the unbounded annotation plane; "
        "the defect is a presentation/PMI property the shape-count oracles cannot observe, and here it also sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9060=geom_ctx

# Presentation style (shared).
pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Annotation 1: annotation_plane defined by unbounded PLANE ─────────────────
ap1_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
ap1_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
ap1_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
ap1_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{ap1_origin.eid},#{ap1_normal.eid},#{ap1_xdir.eid})"
)
# Unbounded PLANE — no size information.
plane1 = f._emit_raw(f"PLANE('annotation_plane_1',#{ap1_plc.eid})")
ann_plane1 = f._emit_raw(
    f"ANNOTATION_PLANE('plane_based',(#{pres_style.eid}),#{plane1.eid})"
)

# ── Annotation 2: annotation_plane defined by PLANAR_BOX (bounded) ────────────
ap2_origin = f._emit_raw("CARTESIAN_POINT('',(20.0,0.0,0.0))")
ap2_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
ap2_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
ap2_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{ap2_origin.eid},#{ap2_normal.eid},#{ap2_xdir.eid})"
)
# PLANAR_BOX carries explicit width and height (bounded rectangle).
planar_box = f._emit_raw(
    f"PLANAR_BOX('',50.0,30.0,#{ap2_plc.eid})"
)
ann_plane2 = f._emit_raw(
    f"ANNOTATION_PLANE('planar_box_based',(#{pres_style.eid}),#{planar_box.eid})"
)

# Both annotation planes in one draughting_model — defect is the mixed form.
f._emit_raw(
    f"DRAUGHTING_MODEL('pmi_view',(#{ann_plane1.eid},#{ann_plane2.eid}),#9060)"
)
