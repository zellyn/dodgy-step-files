"""Pmi017 — Saved-view supplemental geometry split via "supplemental geometry subset".

Catalog claim: A part may have many supplemental elements but only some belong
in a particular Saved View. The recommended pattern is one global CGR with all
elements, plus additional shape_representation instances tagged with
description_attribute = 'supplemental geometry subset'.

Reproducer recipe: Two saved views; ten supplemental planes total; views 1 and 2
each show a different subset of three planes via two shape_representations tagged
with the magic description.

Byte assertions:
  count_entity_def(b'DRAUGHTING_MODEL') == 2
  count_entity_def(b'DESCRIPTION_ATTRIBUTE') == 2
  count_entity_def(b'PLANE') == 5

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi017",
    defect=(
        "supplemental-geometry split via description_attribute='supplemental geometry subset'; "
        "two DRAUGHTING_MODELs each reference a SHAPE_REPRESENTATION subset tagged with "
        "that magic description — normalising receivers must recognise the tag; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9060=geom_ctx

# Presentation style (shared).
pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Helper: build a PLANE at a given z offset ─────────────────────────────────
def make_plane(z: float):
    pt = f._emit_raw(f"CARTESIAN_POINT('',(0.0,0.0,{z:.1f}))")
    nrm = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
    xd = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
    plc = f._emit_raw(f"AXIS2_PLACEMENT_3D('',#{pt.eid},#{nrm.eid},#{xd.eid})")
    return f._emit_raw(f"PLANE('supp_plane_{z:.0f}',#{plc.eid})")

# Five supplemental planes (two subsets of three = 5 unique planes, two shared
# in two subsets each or totally distinct; we use five distinct planes, with
# views picking 3 each: view-1 gets planes 0,1,2; view-2 gets planes 2,3,4).
planes = [make_plane(float(i * 10)) for i in range(5)]

# ── Global shape_representation listing all five planes ───────────────────────
all_plane_refs = ",".join(f"#{p.eid}" for p in planes)
global_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('all_supplemental',({all_plane_refs}),#9060)"
)

# ── Subset SR for view-1 (planes 0,1,2) ──────────────────────────────────────
v1_refs = ",".join(f"#{planes[i].eid}" for i in range(3))
sr_v1 = f._emit_raw(
    f"SHAPE_REPRESENTATION('view1_subset',({v1_refs}),#9060)"
)
da_v1 = f._emit_raw(
    f"DESCRIPTION_ATTRIBUTE('supplemental geometry subset',#{sr_v1.eid})"
)

# ── Subset SR for view-2 (planes 2,3,4) ──────────────────────────────────────
v2_refs = ",".join(f"#{planes[i].eid}" for i in range(2, 5))
sr_v2 = f._emit_raw(
    f"SHAPE_REPRESENTATION('view2_subset',({v2_refs}),#9060)"
)
da_v2 = f._emit_raw(
    f"DESCRIPTION_ATTRIBUTE('supplemental geometry subset',#{sr_v2.eid})"
)

# ── Two draughting_models (saved views) ───────────────────────────────────────
# Each saved view references its subset SR as an item.
dm1 = f._emit_raw(
    f"DRAUGHTING_MODEL('saved_view_1',(#{sr_v1.eid}),#9060)"
)
dm2 = f._emit_raw(
    f"DRAUGHTING_MODEL('saved_view_2',(#{sr_v2.eid}),#9060)"
)
