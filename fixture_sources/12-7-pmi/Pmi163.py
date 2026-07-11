"""Pmi163 — ANGULAR_SIZE / ANGULAR_LOCATION semantic dimension with plane-angle unit [VALID-BUT-HARD].

Catalog claim: AP242 carries angular dimensions as `angular_size` (with an
`angle_relator` selection) and `angular_location` (angle between two features),
tied to their value through a `dimensional_characteristic_representation` whose
measure is a plane-angle `MEASURE_REPRESENTATION_ITEM` in RADIAN units. A reader
that coerces the angular dimension to a linear `dimensional_size`, or drops the
plane-angle unit, mis-carries the dimension. Angular semantic dimensions are
absent from the corpus (nearest = Pmi072 dimension-pair unit mismatch).

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'ANGULAR_SIZE')
  contains(b'ANGULAR_LOCATION')
  contains(b'PLANE_ANGLE_MEASURE')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi163",
    schema="AP242",
    defect=(
        "ANGULAR_SIZE (30 degrees, angle_relator .EQUAL.) and ANGULAR_LOCATION "
        "between two wedge faces, tied via DIMENSIONAL_CHARACTERISTIC_REPRESENTATION "
        "to a plane-angle MEASURE_REPRESENTATION_ITEM in RADIAN units (#9057); "
        "coercing to a linear size or dropping the plane-angle unit mis-carries it; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT,
# #9057=PLANE_ANGLE_UNIT (RADIAN), #9060=GEOMETRIC_REPRESENTATION_CONTEXT

# ── Two wedge faces forming the angular feature ──────────────────────────────
asp1 = f._emit_raw("SHAPE_ASPECT('wedge_face_1','',#9055,.T.)")
asp2 = f._emit_raw("SHAPE_ASPECT('wedge_face_2','',#9055,.T.)")

# ── Angular size (of the wedge) and angular location (between faces) ──────────
ang_size = f._emit_raw(f"ANGULAR_SIZE(#{asp1.eid},'wedge_angle',.EQUAL.)")
ang_loc = f._emit_raw(
    f"ANGULAR_LOCATION('face_angle','angle between wedge faces',"
    f"#{asp1.eid},#{asp2.eid},.EQUAL.)"
)

# ── 30 degrees = 0.5235987756 rad as a plane-angle MEASURE_REPRESENTATION_ITEM ─
mri = f._emit_raw(
    "(MEASURE_REPRESENTATION_ITEM()"
    "MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.5235987756),#9057)"
    "REPRESENTATION_ITEM('wedge_angle'))"
)
shape_dim_rep = f._emit_raw(
    f"SHAPE_DIMENSION_REPRESENTATION('30deg',(#{mri.eid}),#9060)"
)
# Tie each angular dimension to its represented value.
f._emit_raw(
    f"DIMENSIONAL_CHARACTERISTIC_REPRESENTATION(#{ang_size.eid},#{shape_dim_rep.eid})"
)
f._emit_raw(
    f"DIMENSIONAL_CHARACTERISTIC_REPRESENTATION(#{ang_loc.eid},#{shape_dim_rep.eid})"
)
