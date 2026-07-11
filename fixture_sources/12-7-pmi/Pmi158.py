"""Pmi158 — SURFACE_PROFILE_TOLERANCE + LINE_PROFILE_TOLERANCE with ALL_AROUND_SHAPE_ASPECT [VALID-BUT-HARD].

Catalog claim: Profile tolerances scoped "all-around" target an
`all_around_shape_aspect` so the profile zone wraps every bounded segment of
the profile, not just the first face. The profile tolerance family
(`surface_profile_tolerance`, `line_profile_tolerance`) and the all-around
scope entity are absent from the corpus. A reader that ignores the all-around
scope applies the zone to only one face; one that drops the profile subtype
loses the symbol semantics.

Pattern-mined from the NIST MBE-PMI CTC/FTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  contains(b'SURFACE_PROFILE_TOLERANCE')
  contains(b'LINE_PROFILE_TOLERANCE')
  contains(b'ALL_AROUND_SHAPE_ASPECT')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi158",
    schema="AP242",
    defect=(
        "SURFACE_PROFILE_TOLERANCE + LINE_PROFILE_TOLERANCE targeting an "
        "ALL_AROUND_SHAPE_ASPECT so the zone wraps the whole profile; "
        "profile-tolerance family + all-around scope absent from corpus; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Base profiled feature + the all-around scope wrapping it ──────────────────
base = f._emit_raw("SHAPE_ASPECT('profiled_edge','profile feature',#9055,.T.)")
all_around = f._emit_raw(
    "ALL_AROUND_SHAPE_ASPECT('all_around','profile zone wraps all around',#9055,.T.)"
)
# Tie the all-around scope to the base feature it wraps.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('all_around_of','',#{all_around.eid},#{base.eid})"
)

mag_surf = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.2),#9056)")
mag_line = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.1),#9056)")

# ── Profile FCFs whose toleranced aspect is the all-around scope ──────────────
f._emit_raw(
    f"SURFACE_PROFILE_TOLERANCE('surf_profile','0.2 all-around surface profile',"
    f"#{mag_surf.eid},#{all_around.eid})"
)
f._emit_raw(
    f"LINE_PROFILE_TOLERANCE('line_profile','0.1 all-around line profile',"
    f"#{mag_line.eid},#{all_around.eid})"
)
