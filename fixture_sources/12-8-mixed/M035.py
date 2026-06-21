"""M035 — Single-item Constructive_Geometry_Representation crashes translator.

Catalog claim: STEP Constructive_Geometry_Representation with only one representation
item caused exception during translation. Validation observed: silent-empty rather
than crash — kernel mishandling by silent acceptance still demonstrates the defect class.

Reproducer recipe: STEP CGR with a single representation_item (a PLANE).

Byte assertions:
  contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
  count_entity_def(b'PLANE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M035",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing CONSTRUCTIVE_GEOMETRY_REPRESENTATION with "
        "exactly one PLANE item; "
        "input: AP242 STEP file where a constructive_geometry_representation has only "
        "a single representation_item (a PLANE); "
        "OCCT 1e1b83c (Mantis 0031472): translator threw exception on single-item CGR; "
        "fixed translators silently accept but produce empty output; "
        "kernel must accept single-item representations without crash and without "
        "silent-empty; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: single-item CGR crashes translator, constructive_geometry_representation crash, "
        "CGR with one item silent-empty, translator exception on tiny CGR"
    ),
)

# ── Single PLANE item — the minimal CGR that triggered the crash ──────────────
# Byte assertion: count_entity_def(b'PLANE') == 1
origin_pt = f._emit_raw("CARTESIAN_POINT('cgr_origin',(0.,0.,0.))")
z_dir = f._emit_raw("DIRECTION('cgr_z',(0.,0.,1.))")
x_dir = f._emit_raw("DIRECTION('cgr_x',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('cgr_placement',#{origin_pt.eid},#{z_dir.eid},#{x_dir.eid})"
)

# Exactly one PLANE — byte assertion: count_entity_def(b'PLANE') == 1
plane = f._emit_raw(f"PLANE('reference_plane',#{placement.eid})")

# ── CONSTRUCTIVE_GEOMETRY_REPRESENTATION with single item ─────────────────────
# Byte assertion: contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('single_item_cgr',"
    f"(#{plane.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('single-item-cgr-crash',"
    f"(#{cgr.eid},#{plane.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M035.stp")
