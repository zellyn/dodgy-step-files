"""Pmi004 — Non-coplanar leader collapsed onto annotation plane loses attachment.

Catalog claim: NX permits an annotation whose leader is not in the same plane
as the text. Writers project the leader onto the annotation plane, but the
projected leader no longer touches the geometry it was attached to.  The fix
is to split into coplanar subsets under one DRAUGHTING_CALLOUT.

Reproducer: text in plane Z=10; leader endpoints (0,0,5) and (0,0,0).  Two
ANNOTATION_CURVE_OCCURRENCEs (leader subset + text subset) gathered under one
DRAUGHTING_CALLOUT, but the leader polyline is projected flat onto Z=0 so
attachment is lost.

Byte assertions:
  count_entity_def(b'ANNOTATION_CURVE_OCCURRENCE') == 2
  contains(b'DRAUGHTING_CALLOUT')
  count_entity_def(b'POLYLINE') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi004",
    defect=(
        "non-coplanar leader projected onto annotation plane; "
        "two ANNOTATION_CURVE_OCCURRENCEs under one DRAUGHTING_CALLOUT; "
        "leader POLYLINE projected to Z=0 — attachment to geometry at Z=5 lost; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# Presentation style (shared by both occurrences).
pres_style = f._emit_raw(
    "PRESENTATION_STYLE_ASSIGNMENT($)"
)

# Leader polyline: projected to Z=0 — the defect; original was at Z=5..0.
ldr_p1 = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
ldr_p2 = f._emit_raw("CARTESIAN_POINT('',(5.0,0.0,0.0))")
ldr_poly = f._emit_raw(
    f"POLYLINE('leader',(#{ldr_p1.eid},#{ldr_p2.eid}))"
)
ldr_occ = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader_occ',(#{pres_style.eid}),#{ldr_poly.eid})"
)

# Text box polyline: in the annotation plane Z=0.
txt_p1 = f._emit_raw("CARTESIAN_POINT('',(5.0,-1.0,0.0))")
txt_p2 = f._emit_raw("CARTESIAN_POINT('',(15.0,1.0,0.0))")
txt_poly = f._emit_raw(
    f"POLYLINE('text_box',(#{txt_p1.eid},#{txt_p2.eid}))"
)
txt_occ = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('text_occ',(#{pres_style.eid}),#{txt_poly.eid})"
)

# Defect: both subsets gathered under one DRAUGHTING_CALLOUT, but the leader
# subset's geometry is projected (no longer touches Z=5 attachment point).
f._emit_raw(
    f"DRAUGHTING_CALLOUT('callout',(#{ldr_occ.eid},#{txt_occ.eid}))"
)
