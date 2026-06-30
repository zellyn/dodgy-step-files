"""Pmi137 — COMPOUND_REPRESENTATION_ITEM with SET_REPRESENTATION_ITEM null children.

Catalog claim: a STEP AP242 file where a COMPOUND_REPRESENTATION_ITEM's item
list contains a SET_REPRESENTATION_ITEM that wraps DESCRIPTIVE_REPRESENTATION_ITEM
children.  OCCT's reader populates NbItemElement() == 1 (the SET wrapper counts
as one item) but when code calls ItemElementValue(0) to retrieve the SET's
children it returns a null handle, because the entity-resolution pass does not
traverse SET_REPRESENTATION_ITEM sub-elements as compound children.
PMI dimensional-note data is silently missing even though geometry loads.

Source: https://github.com/Open-Cascade-SAS/OCCT/issues/1283
(nist_ctc_05_asme1_ap242-e1.stp test case)

Byte assertions:
  contains(b'COMPOUND_REPRESENTATION_ITEM')
  contains(b'SET_REPRESENTATION_ITEM')
  count_entity_def(b'DESCRIPTIVE_REPRESENTATION_ITEM') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi137",
    schema="AP242",
    defect=(
        "COMPOUND_REPRESENTATION_ITEM item list contains a "
        "SET_REPRESENTATION_ITEM wrapping DESCRIPTIVE_REPRESENTATION_ITEM "
        "children; OCCT NbItemElement()==1 but ItemElementValue(0) returns "
        "null handle — PMI dimensional note silently missing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain reserves #9000+:
#   #9055 = PRODUCT_DEFINITION_SHAPE
#   #9056 = LENGTH_UNIT complex
#   #9060 = GEOMETRIC_REPRESENTATION_CONTEXT complex

# ── PMI structure ─────────────────────────────────────────────────────────────
# DESCRIPTIVE_REPRESENTATION_ITEM carrying the note text — this is the child
# that OCCT cannot dereference when it is wrapped in SET_REPRESENTATION_ITEM.
dri = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('dimensional note','statistical')"
)

# SET_REPRESENTATION_ITEM wraps the DRI.  Per AP242 §4.12, this is a valid
# entity type that can appear in the item list of a COMPOUND_REPRESENTATION_ITEM.
# OCCT bug: the resolver counts the SET wrapper as one item but does not walk
# into it to resolve the DRI children.
sri = f._emit_raw(
    f"SET_REPRESENTATION_ITEM('',(#{dri.eid}))"
)

# COMPOUND_REPRESENTATION_ITEM with the SET as one of its items.
# Correct syntax: (name, (item_list)).
# The defect is that sri's children are opaque to OCCT's compound resolver.
cri = f._emit_raw(
    f"COMPOUND_REPRESENTATION_ITEM('compound_note',(#{sri.eid}))"
)

# Wire the compound item into a REPRESENTATION so OCCT's XCAF reader visits it.
pmi_rep = f._emit_raw(
    f"REPRESENTATION('pmi_rep',(#{cri.eid}),#9060)"
)

# PROPERTY_DEFINITION and PROPERTY_DEFINITION_REPRESENTATION link the PMI
# representation to the model shape.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('note_prop','dimensional note',#9055)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{pmi_rep.eid})"
)
