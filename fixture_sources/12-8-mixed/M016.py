"""M016 — Tessellated curve set missing both coordinates and line_strips.

Catalog claim: tessellated_curve_set is empty; neither coordinates nor
line_strips is populated.

Reproducer recipe: TESSELLATED_CURVE_SET with empty coordinates and empty
line_strips lists.

Byte assertions:
  contains(b'TESSELLATED_CURVE_SET')
  matches(rb'TESSELLATED_CURVE_SET\([^)]*,\(\)\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M016",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_CURVE_SET with empty coordinates "
        "and empty line_strips; "
        "tessellated_curve_set.coordinates is absent ($) and line_strips is empty list (); "
        "kernel must drop entity with a warning; must not crash; "
        "TESSELLATED_CURVE_SET($,()) — neither field is populated; "
        "cross-oracle: OCCT silently accepts (no diagnostic); "
        "kernel-bug: receivers must emit a diagnostic; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: empty tessellated_curve_set, tessellation has no points or strips, "
        "tessellated curve set has no data, empty line_strips and coordinates"
    ),
)

# ── The defect: TESSELLATED_CURVE_SET with no coordinates and no line_strips ──
# TESSELLATED_CURVE_SET(name, coordinates, line_strips)
# Defect: coordinates=$  (absent), line_strips=()  (empty)
# Byte assertion: matches(rb'TESSELLATED_CURVE_SET\([^)]*,\(\)\)')
# The regex matches the trailing ,() which is the empty line_strips.
empty_tcs = f._emit_raw(
    "TESSELLATED_CURVE_SET('empty_tcs',$,())"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('empty-tessellated-curve-set',(#{empty_tcs.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M016.stp")
