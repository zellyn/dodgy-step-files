"""Pmi018 — Identical Graphic PMI duplicated across saved views.

Catalog claim: Two draughting_models for different saved views contain exactly
the same set of annotation occurrences, indicating either a copy-paste bug or
an export that did not differentiate views.

Reproducer recipe: Two saved views written with identical annotation_occurrence
lists.

Byte assertions:
  count_entity_def(b'ANNOTATION_CURVE_OCCURRENCE') == 2
  count_entity_def(b'DRAUGHTING_MODEL') == 2
  count_entity_def(b'POLYLINE') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi018",
    defect=(
        "two DRAUGHTING_MODELs for different saved views share identical "
        "ANNOTATION_CURVE_OCCURRENCE lists (copy-paste or non-differentiating export); "
        "receivers must emit an informational warning about the duplication; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9060=geom_ctx

pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── View-1 annotation: polyline + occurrence ──────────────────────────────────
pt1a = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
pt1b = f._emit_raw("CARTESIAN_POINT('',(10.0,0.0,0.0))")
pt1c = f._emit_raw("CARTESIAN_POINT('',(10.0,5.0,0.0))")
polyline1 = f._emit_raw(
    f"POLYLINE('dim_v1',(#{pt1a.eid},#{pt1b.eid},#{pt1c.eid},#{pt1a.eid}))"
)
aco1 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_occ_v1',(#{pres_style.eid}),#{polyline1.eid})"
)

# ── View-2 annotation: identical geometry and occurrence (defect) ─────────────
# Defect: same leader-line box copied verbatim into a second saved view instead
# of referencing the correct view-2 annotation geometry.
pt2a = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
pt2b = f._emit_raw("CARTESIAN_POINT('',(10.0,0.0,0.0))")
pt2c = f._emit_raw("CARTESIAN_POINT('',(10.0,5.0,0.0))")
polyline2 = f._emit_raw(
    f"POLYLINE('dim_v2',(#{pt2a.eid},#{pt2b.eid},#{pt2c.eid},#{pt2a.eid}))"
)
aco2 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_occ_v2',(#{pres_style.eid}),#{polyline2.eid})"
)

# ── Two draughting_models — each with its own (but identical) occurrence ───────
dm1 = f._emit_raw(
    f"DRAUGHTING_MODEL('saved_view_1',(#{aco1.eid}),#9060)"
)
dm2 = f._emit_raw(
    f"DRAUGHTING_MODEL('saved_view_2',(#{aco2.eid}),#9060)"
)
