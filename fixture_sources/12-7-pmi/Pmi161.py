"""Pmi161 — DATUM_REFERENCE_COMPARTMENT / DATUM_REFERENCE_ELEMENT with per-datum material modifier [VALID-BUT-HARD].

Catalog claim: An AP242 Ed.2 datum-reference frame A|B(Ⓜ)|C encodes the datum
system as ordered `datum_reference_compartment`s, each holding a
`datum_reference_element`; a per-datum modifier (here MMC on secondary datum B)
lives in that element's `modifiers` list. Readers that flatten the datum system
to a legacy flat `datum_reference` list lose both the compartment ORDERING and
the per-datum modifier. The corpus has identical-datum / common-datum entries
(Pmi025/027/028) but none carries compartment + per-datum modifier.

Pattern-mined from the NIST MBE-PMI FTC/CTC AP242 test suite (public-domain /
describe-only — pattern only, no bytes copied).

Byte assertions:
  count_entity_def(b'DATUM_REFERENCE_COMPARTMENT') == 3
  contains(b'DATUM_REFERENCE_ELEMENT')
  contains(b'MAXIMUM_MATERIAL_REQUIREMENT')

Tier-3: shape_null == False (GCS+point loads as one vertex, like Pmi010)
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi161",
    schema="AP242",
    defect=(
        "DATUM_SYSTEM A|B(M)|C: three ordered DATUM_REFERENCE_COMPARTMENTs, the "
        "secondary bearing a DATUM_REFERENCE_ELEMENT whose modifiers list holds "
        ".MAXIMUM_MATERIAL_REQUIREMENT. (MMC on datum B); "
        "flattening to a legacy datum_reference list loses ordering AND modifier; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC loads the point as one vertex"
    ),
)

# Minimal geometry wrapped in GCS (single vertex loads; mirrors Pmi010).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain fixed IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Three datums ─────────────────────────────────────────────────────────────
datum_a = f._emit_raw("DATUM('A','primary datum',#9055,.T.,'A')")
datum_b = f._emit_raw("DATUM('B','secondary datum',#9055,.T.,'B')")
datum_c = f._emit_raw("DATUM('C','tertiary datum',#9055,.T.,'C')")

# ── Datum-reference elements; MMC modifier lives on the secondary (B) ────────
dre_a = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum_a.eid})")
dre_b = f._emit_raw(
    f"DATUM_REFERENCE_ELEMENT('',(.MAXIMUM_MATERIAL_REQUIREMENT.),#{datum_b.eid})"
)
dre_c = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum_c.eid})")

# ── Ordered compartments (primary/secondary/tertiary) ─────────────────────────
comp_a = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('primary',$,#{dre_a.eid})")
comp_b = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('secondary',$,#{dre_b.eid})")
comp_c = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('tertiary',$,#{dre_c.eid})")

datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('A|B(M)|C','',#9055,.T.,"
    f"(#{comp_a.eid},#{comp_b.eid},#{comp_c.eid}))"
)

# ── Position tolerance referencing the compartmented datum system ─────────────
asp = f._emit_raw("SHAPE_ASPECT('hole_axis','toleranced hole',#9055,.T.)")
mag = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.1),#9056)")
f._emit_raw(
    f"POSITION_TOLERANCE('pos','position 0.1 wrt A|B(M)|C',"
    f"#{mag.eid},#{asp.eid},#{datum_sys.eid})"
)
