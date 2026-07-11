"""Pmi159 — GEOMETRIC_TOLERANCE_WITH_MODIFIERS carrying MMC / LMC / free-state / tangent-plane [VALID-BUT-HARD].

Catalog claim: Position tolerances often carry material-condition modifiers
(Ⓜ maximum-material, Ⓛ least-material, free-state Ⓕ, tangent-plane Ⓣ) via a
`geometric_tolerance_with_modifiers` whose `modifiers` set holds the enum
values. The modifier changes the tolerance semantics (it enables bonus
tolerance). A reader that silently coerces to RFS (drops the modifier) commits
a correctness bug. The modifier-carrying tolerance and the material-condition
enum vocabulary are absent from the corpus.

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'GEOMETRIC_TOLERANCE_WITH_MODIFIERS')
  contains(b'MAXIMUM_MATERIAL_REQUIREMENT')
  contains(b'LEAST_MATERIAL_REQUIREMENT')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi159",
    schema="AP242",
    defect=(
        "GEOMETRIC_TOLERANCE_WITH_MODIFIERS carrying material-condition modifiers: "
        "position at MAXIMUM_MATERIAL_REQUIREMENT + TANGENT_PLANE on one hole, and "
        "LEAST_MATERIAL_REQUIREMENT + FREE_STATE on a boss; "
        "dropping the modifier silently coerces to RFS and loses bonus tolerance; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

asp_hole = f._emit_raw("SHAPE_ASPECT('hole_axis','toleranced hole',#9055,.T.)")
asp_boss = f._emit_raw("SHAPE_ASPECT('boss_axis','toleranced boss',#9055,.T.)")
mag1 = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)")
mag2 = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.08),#9056)")

# Position tolerance at MMC + tangent-plane on the hole.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_WITH_MODIFIERS('pos_mmc','position 0.05 at MMC',"
    f"#{mag1.eid},#{asp_hole.eid},"
    f"(.MAXIMUM_MATERIAL_REQUIREMENT.,.TANGENT_PLANE.))"
)
# Position tolerance at LMC + free-state on the boss.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_WITH_MODIFIERS('pos_lmc','position 0.08 at LMC free-state',"
    f"#{mag2.eid},#{asp_boss.eid},"
    f"(.LEAST_MATERIAL_REQUIREMENT.,.FREE_STATE.))"
)
