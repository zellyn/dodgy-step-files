"""Pmi156 — CIRCULAR_RUNOUT_TOLERANCE + TOTAL_RUNOUT_TOLERANCE with datum axis [VALID-BUT-HARD].

Catalog claim: AP242 semantic GD&T files carry runout tolerances
(`circular_runout_tolerance`, `total_runout_tolerance`) whose zone is defined
relative to a datum axis via a `datum_system`. The whole runout tolerance
family is absent from the corpus (nearest = generic POSITION_TOLERANCE); a
reader that maps unknown subtypes onto a generic tolerance, or that drops the
datum-axis link, silently downgrades runout to circularity or loses the datum.

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'CIRCULAR_RUNOUT_TOLERANCE')
  contains(b'TOTAL_RUNOUT_TOLERANCE')
  contains(b'DATUM_SYSTEM')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi156",
    schema="AP242",
    defect=(
        "CIRCULAR_RUNOUT_TOLERANCE + TOTAL_RUNOUT_TOLERANCE on a cylinder feature, "
        "each referencing a DATUM_SYSTEM built on datum axis A; "
        "semantic runout tolerance family absent from corpus; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Datum axis A ──────────────────────────────────────────────────────────────
datum_a = f._emit_raw("DATUM('A','datum axis A',#9055,.T.,'A')")
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum_a.eid})")
drc = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('',$,#{dre.eid})")
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('datum_system_A','',#9055,.T.,(#{drc.eid}))"
)

# ── Toleranced cylinder feature + magnitudes ─────────────────────────────────
asp = f._emit_raw("SHAPE_ASPECT('cylinder_od','runout feature',#9055,.T.)")
mag_cr = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)")
mag_tr = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.1),#9056)")

# ── Runout FCFs referencing the datum-axis system ─────────────────────────────
f._emit_raw(
    f"CIRCULAR_RUNOUT_TOLERANCE('circular_runout','0.05 circular runout wrt A',"
    f"#{mag_cr.eid},#{asp.eid},#{datum_sys.eid})"
)
f._emit_raw(
    f"TOTAL_RUNOUT_TOLERANCE('total_runout','0.1 total runout wrt A',"
    f"#{mag_tr.eid},#{asp.eid},#{datum_sys.eid})"
)
