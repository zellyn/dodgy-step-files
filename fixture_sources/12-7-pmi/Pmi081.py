"""Pmi081 — GD&T saved-views label name silently emptied.

Catalog claim: a document has reserved labels (saved-view labels) that must be
cleared but not deleted. A "clear contents" pass empties their children but also
empties the label name itself, producing nameless reserved labels that downstream
PMI tools cannot find.

Reproducer recipe: Document with two saved-view labels named "front" and "iso".
Run "clear contents". Names become empty.

Byte assertions:
  count_entity_def(b'PRESENTATION_VIEW') == 2
  contains(b'ANNOTATION_PLANE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi081",
    schema="AP242",
    defect=(
        "Two PRESENTATION_VIEWs are present: 'front_view' and 'iso_view'; "
        "a 'clear contents' operation on these saved-view labels also empties "
        "the label name attribute, producing nameless PRESENTATION_VIEW entries "
        "that downstream PMI tools (which look up views by name) cannot locate; "
        "receivers must detect PRESENTATION_VIEW entries with empty names and "
        "warn or reject; a heal-and-proceed path must preserve the label name "
        "while clearing only non-name child attributes; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── ANNOTATION_PLANE anchor (byte assertion: contains(b'ANNOTATION_PLANE')) ───
# Provides a plane for the saved views to annotate.
zdir = f._emit_raw("DIRECTION('z',(0.0,0.0,1.0))")
xdir = f._emit_raw("DIRECTION('x',(1.0,0.0,0.0))")
ap_origin = f._emit_raw("CARTESIAN_POINT('ap_origin',(0.0,0.0,0.0))")
plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('ap_plc',#{ap_origin.eid},#{zdir.eid},#{xdir.eid})"
)
ann_plane = f._emit_raw(
    f"ANNOTATION_PLANE('pmi_annotation_plane',(),#{plc.eid},())"
)

# ── Two PRESENTATION_VIEWs (byte assertion: count == 2) ──────────────────────
# DEFECT: after "clear contents" the 'front' and 'iso' names are emptied to '';
# downstream tools searching for a saved view by name cannot find either entry.
# We model the post-clear state: names are '' (empty) instead of 'front'/'iso'.
pv_front = f._emit_raw(
    f"PRESENTATION_VIEW('','front view name emptied by clear-contents',"
    f"'',(#{ann_plane.eid}),#9000)"
)
f._emit_raw(
    f"PRESENTATION_VIEW('','iso view name emptied by clear-contents',"
    f"'',(#{ann_plane.eid}),#9000)"
)
