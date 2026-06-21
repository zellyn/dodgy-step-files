"""Pmi082 — Saved-views and clipping planes lost on STEP read.

Catalog claim: a STEP file containing AP242 saved-view entities
(PRESENTATION_VIEW) and clipping-plane references is imported; saved
views are silently discarded by readers unaware of these AP242 subtypes.

Reproducer recipe: STEP file with one PRESENTATION_VIEW linking three PMI
annotations to a "side view" and one clipping plane.

Byte assertions:
  contains(b'CLIPPING_PLANE')
  count_entity_def(b'DRAUGHTING_CALLOUT') == 3
  contains(b'PRESENTATION_VIEW')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi082",
    schema="AP242",
    defect=(
        "PRESENTATION_VIEW 'side_view' links three DRAUGHTING_CALLOUTs to a "
        "saved-view with one CLIPPING_PLANE reference; readers that do not "
        "recognise the AP242 PRESENTATION_VIEW and CLIPPING_PLANE subtypes "
        "silently discard the entire saved-view record including all clipping-plane "
        "references; receivers must detect and handle PRESENTATION_VIEW entities "
        "and must preserve CLIPPING_PLANE references across round-trip; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── Shared presentation style ────────────────────────────────────────────────
psa = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Three DRAUGHTING_CALLOUTs (byte assertion: count == 3) ───────────────────
# Each callout represents a PMI annotation in the saved view.
pt_a = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
pt_b = f._emit_raw("CARTESIAN_POINT('',(10.0,0.0,0.0))")
poly1 = f._emit_raw(f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))")
aco1 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('ann1',(#{psa.eid}),#{poly1.eid})"
)
dc1 = f._emit_raw(f"DRAUGHTING_CALLOUT('callout_diam',(#{aco1.eid}))")

pt_c = f._emit_raw("CARTESIAN_POINT('',(0.0,10.0,0.0))")
pt_d = f._emit_raw("CARTESIAN_POINT('',(10.0,10.0,0.0))")
poly2 = f._emit_raw(f"POLYLINE('',(#{pt_c.eid},#{pt_d.eid}))")
aco2 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('ann2',(#{psa.eid}),#{poly2.eid})"
)
dc2 = f._emit_raw(f"DRAUGHTING_CALLOUT('callout_pos',(#{aco2.eid}))")

pt_e = f._emit_raw("CARTESIAN_POINT('',(0.0,20.0,0.0))")
pt_f = f._emit_raw("CARTESIAN_POINT('',(10.0,20.0,0.0))")
poly3 = f._emit_raw(f"POLYLINE('',(#{pt_e.eid},#{pt_f.eid}))")
aco3 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('ann3',(#{psa.eid}),#{poly3.eid})"
)
dc3 = f._emit_raw(f"DRAUGHTING_CALLOUT('callout_datum',(#{aco3.eid}))")

# ── CLIPPING_PLANE (byte assertion: contains(b'CLIPPING_PLANE')) ──────────────
# Defines a clipping section plane for the saved view.
clip_origin = f._emit_raw("CARTESIAN_POINT('clip_origin',(0.0,0.0,50.0))")
clip_normal = f._emit_raw("DIRECTION('clip_normal',(0.0,0.0,1.0))")
clip_xdir = f._emit_raw("DIRECTION('clip_xdir',(1.0,0.0,0.0))")
clip_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('clip_plc',#{clip_origin.eid},"
    f"#{clip_normal.eid},#{clip_xdir.eid})"
)
clip_plane = f._emit_raw(
    f"CLIPPING_PLANE('section_cut',#{clip_plc.eid},.T.)"
)

# ── PRESENTATION_VIEW (byte assertion: contains(b'PRESENTATION_VIEW')) ────────
# DEFECT: readers unaware of AP242 PRESENTATION_VIEW silently discard this
# entity together with all three callout references and the clipping plane.
f._emit_raw(
    f"PRESENTATION_VIEW('side_view','side view with section plane',"
    f"(#{dc1.eid},#{dc2.eid},#{dc3.eid}),#{clip_plane.eid})"
)
