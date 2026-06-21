"""M021 — Tessellated GD&T (annotation) entities not imported.

Catalog claim: TESSELLATED_ANNOTATION_OCCURRENCE entities for GD&T were
unrecognized by the reader.

Reproducer recipe: AP242 file with tessellated PMI annotations.

Byte assertions:
  contains(b'TESSELLATED_ANNOTATION_OCCURRENCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M021",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_ANNOTATION_OCCURRENCE for GD&T PMI; "
        "input: AP242 STEP file where tessellated PMI annotation is encoded as "
        "TESSELLATED_ANNOTATION_OCCURRENCE with a TESSELLATED_GEOMETRIC_SET presentation; "
        "OCCT b78ccf1 (Mantis 0033661): TESSELLATED_ANNOTATION_OCCURRENCE was unrecognized "
        "by the reader — annotation entities silently skipped, PMI lost on import; "
        "kernel must heal: translate TESSELLATED_ANNOTATION_OCCURRENCE as PMI carrier "
        "with mesh presentation; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellated GD&T not imported, TESSELLATED_ANNOTATION_OCCURRENCE skipped, "
        "PMI tessellation entities unrecognized, tessellated annotation lost on read"
    ),
)

# ── Tessellated PMI annotation geometry ───────────────────────────────────────
# A simple leader line + tolerance box outline as tessellated curves
leader_coords = f._emit_raw(
    "COORDINATES_LIST('leader_pts',3,"
    "((0.,0.,0.),(5.,5.,0.),(5.,8.,0.),(15.,8.,0.),(15.,11.,0.)))"
)

leader_curve = f._emit_raw(
    f"TESSELLATED_CURVE_SET('leader_line',#{leader_coords.eid},(0,1,2,3,4))"
)

box_coords = f._emit_raw(
    "COORDINATES_LIST('tol_box_pts',3,"
    "((5.,8.,0.),(15.,8.,0.),(15.,11.,0.),(5.,11.,0.)))"
)

box_curve = f._emit_raw(
    f"TESSELLATED_CURVE_SET('tolerance_box',#{box_coords.eid},(0,1,2,3,0))"
)

# TESSELLATED_GEOMETRIC_SET wraps the annotation curves
tgs = f._emit_raw(
    f"TESSELLATED_GEOMETRIC_SET('annot_tgs',(#{leader_curve.eid},#{box_curve.eid}))"
)

# TESSELLATED_ANNOTATION_OCCURRENCE — the unrecognized entity.
# Byte assertion: contains(b'TESSELLATED_ANNOTATION_OCCURRENCE')
tao = f._emit_raw(
    f"TESSELLATED_ANNOTATION_OCCURRENCE('diameter_tolerance',(#{tgs.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('tessellated-annotation-occurrence-unrecognized',"
    f"(#{tao.eid},#{tgs.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M021.stp")
