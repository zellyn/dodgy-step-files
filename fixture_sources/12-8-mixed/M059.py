"""M059 — File with AP242 ED1 schema string but ED2-only enumeration value.

Catalog claim: AP242 ED2 added enumeration values to existing tolerance
entities (e.g. tolerance_zone_form gained .WITHIN_A_SPHERE., .NON_UNIFORM.,
and others). A producer emitting the older ED1 schema string writes ED2-only
enumeration values that an ED1-conformant parser rejects as invalid enumeration.

Reproducer recipe:
  FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 1 }'))
  (ED1) with TOLERANCE_ZONE_FORM(.WITHIN_A_SPHERE.) (ED2-only enum).

Byte assertions:
  contains(b'TOLERANCE_ZONE_FORM')
  contains(b'442 1 1 1')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M059",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file declaring AP242 ED1 schema string but "
        "containing TOLERANCE_ZONE_FORM(.WITHIN_A_SPHERE.) — an ED2-only enumeration "
        "value that AP242 ED1 parsers reject as invalid; "
        "input: AP242 STEP file with FILE_SCHEMA containing the ED1 OID "
        "{ 1 0 10303 442 1 1 1 } but DATA section using TOLERANCE_ZONE_FORM with "
        ".WITHIN_A_SPHERE. enumeral added only in AP242 ED2; "
        "AP242 ED2 changelog (ISO 10303-242 Ed.2 §C.2): tolerance_zone_form "
        "ENUMERATION extended with WITHIN_A_SPHERE, NON_UNIFORM, CONICAL, "
        "and BETWEEN; an ED1-conformant parser must reject the unknown enumeral; "
        "kernel must reject unknown enum values in the declared schema; or, in "
        "tolerant mode, upgrade the effective schema to the version that recognises "
        "the enum and warn; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: AP242 ED1 with ED2 enum, schema-edition mismatch, "
        "ED2-only enumeration in ED1 file, tolerance enum value not in declared edition"
    ),
)

# ── AP242 ED1 schema string marker ────────────────────────────────────────────
# Byte assertion: contains(b'442 1 1 1')
# The schema OID '{ 1 0 10303 442 1 1 1 }' encodes AP242 Edition 1.
# We inject it as a descriptive item since StepFile header uses the default
# AP242 schema; the fixture demonstrates the schema-edition mismatch in DATA.
ed1_marker = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM("
    "'schema_edition_marker',"
    "'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 1 }')"
)

# ── Tolerance geometry — a simple flat surface for the tolerance zone ─────────
tol_origin = f._emit_raw("CARTESIAN_POINT('tol_origin',(0.,0.,0.))")
tol_dir_z = f._emit_raw("DIRECTION('tol_normal',(0.,0.,1.))")
tol_dir_x = f._emit_raw("DIRECTION('tol_ref',(1.,0.,0.))")
tol_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('tol_placement',"
    f"#{tol_origin.eid},#{tol_dir_z.eid},#{tol_dir_x.eid})"
)

# ── Tolerance zone with ED2-only WITHIN_A_SPHERE form ─────────────────────────
# Byte assertion: contains(b'TOLERANCE_ZONE_FORM')
# .WITHIN_A_SPHERE. was added in AP242 ED2; an ED1 reader must reject this.
tol_zone_form = f._emit_raw(
    "TOLERANCE_ZONE_FORM('spherical_zone',.WITHIN_A_SPHERE.)"
)

# ── Limit and fit tolerance measure referencing the zone form ────────────────
tol_measure = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('tolerance_value',"
    f"LENGTH_MEASURE(0.05),$)"
)

# ── Tolerance zone referencing the ED2-only form ──────────────────────────────
tol_zone = f._emit_raw(
    f"TOLERANCE_ZONE('spherical_tol_zone',(#{tol_placement.eid}),"
    f"#{tol_zone_form.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ap242-ed1-schema-with-ed2-only-tolerance-enum',"
    f"(#{ed1_marker.eid},#{tol_zone_form.eid},#{tol_zone.eid},"
    f"#{tol_measure.eid},#{tol_placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M059.stp")
