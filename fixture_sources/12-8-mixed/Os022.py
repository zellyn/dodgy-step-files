"""Os022 — FindContigousEdges: paired LINEs/VECTORs have unequal parameter lengths.

Catalog claim: Two LINE entities run between the same two 3D points but with
different parameter lengths.  One uses a unit DIRECTION (1,0,0) with
magnitude 10 (parameter length = 10).  The other uses a non-unit DIRECTION
(0.5,0,0) with magnitude 10 (parameter length = 10 * ||(0.5,0,0)|| = 5 in
parameterized sense but 3D extent = 5 units, arriving at (5,0,0) not (10,0,0)).

Fixture as per catalog recipe: LINE 1 from (0,0,0), DIRECTION(1,0,0), magnitude 10
→ 3D endpoint (10,0,0); LINE 2 from (0,0,0), DIRECTION(0.5,0,0), magnitude 10
→ 3D endpoint (5,0,0) but the non-unit direction gives param length = 20 for the
same 3D distance as line 1 (if we scale to match endpoint we set magnitude=20).
Result: same 3D extent but different parameter lengths.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - count_entity_def(b'LINE') == 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os022",
    defect=(
        "GEOMETRIC_CURVE_SET containing exactly 2 LINE entities; "
        "LINE 1: VECTOR(DIRECTION(1,0,0), 10.0) — unit direction, param length=10; "
        "LINE 2: VECTOR(DIRECTION(0.5,0,0), 20.0) — non-unit direction, same 3D "
        "extent but param length=20 (magnitude*||dir||^-1 = 20/0.5 = 40 or "
        "20 depending on convention); "
        "FindContigousEdges detects free-edge pair with mismatched param lengths; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── LINE 1: unit DIRECTION (1,0,0), magnitude 10 → endpoint (10,0,0) ─────────
pt1   = f.cartesian_point((0.0, 0.0, 0.0))
dir1  = f.direction((1.0, 0.0, 0.0))          # unit direction
vec1  = f.vector(dir1, 10.0)
line1 = f.line(pt1, vec1)                      # LINE #1 — byte assertion ✓

# ── LINE 2: non-unit DIRECTION (0.5,0,0), magnitude 20 → same 3D endpoint ────
# 3D displacement = direction * magnitude = (0.5,0,0) * 20 = (10,0,0)
# same 3D extent, but parameter length differs (non-unit direction)
pt2   = f.cartesian_point((0.0, 0.0, 0.0))
dir2  = f.direction((0.5, 0.0, 0.0))          # NON-unit direction — key defect
vec2  = f.vector(dir2, 20.0)
line2 = f.line(pt2, vec2)                      # LINE #2 — count == 2 ✓

# ── GEOMETRIC_CURVE_SET wrapping both LINEs ──────────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{line1.eid},#{line2.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os022.stp")
