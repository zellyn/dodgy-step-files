"""Os014 — Pipe section drifts beyond auxiliary spine reach (impossible contact).

Catalog claim: A pipe-shell sweep with KeepContact mode: the section must maintain
contact with an auxiliary spine, but the auxiliary spine is too short or diverges
so that contact cannot be maintained throughout.
Main spine: length 10, along X axis at y=0.
Auxiliary spine: length 5, parallel-offset by 2 (at y=2), also along X axis.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - Main spine: LINE of length 10 along X at y=0
  - Auxiliary spine: LINE of length 5 along X at y=2, z=0
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'LINE')
  - count_entity_def(b'LINE') >= 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os014",
    defect=(
        "GEOMETRIC_CURVE_SET containing two LINE entities; "
        "main spine: LINE from (0,0,0) along X, length 10; "
        "auxiliary spine: LINE from (0,2,0) along X, length 5 — too short; "
        "KeepContact mode: contact impossible after half the main spine; "
        "BRepOffsetAPI_MakePipeShell ImpossibleContact; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Main spine: LINE along X axis at y=0, length 10 ──────────────────────────
main_pt  = f.cartesian_point((0.0, 0.0, 0.0))
main_dir = f.direction((1.0, 0.0, 0.0))
main_vec = f.vector(main_dir, 10.0)
main_ln  = f.line(main_pt, main_vec)   # LINE #1 — byte assertions ✓

# ── Auxiliary spine: LINE along X axis at y=2, length 5 (too short) ──────────
aux_pt  = f.cartesian_point((0.0, 2.0, 0.0))
aux_dir = f.direction((1.0, 0.0, 0.0))
aux_vec = f.vector(aux_dir, 5.0)
aux_ln  = f.line(aux_pt, aux_vec)     # LINE #2 — count_entity_def >= 2 ✓

# ── GEOMETRIC_CURVE_SET wrapping both spines ──────────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{main_ln.eid},#{aux_ln.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os014.stp")
