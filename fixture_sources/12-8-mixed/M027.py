"""M027 — Surface-sampling-point validation property failure.

Catalog claim: A finer-grained validation than volume/area: a set of (u,v,XYZ)
sample points is embedded; on retrieval the receiver evaluates the surface at the
same (u,v) and verifies XYZ match. Catches local NURBS reparametrization issues
invisible to a volume checksum.

Reproducer recipe: A B-spline surface re-fit during translation passes the volume
check but fails several surface-sampling-point checks.

Byte assertions:
  contains(b'COMPOUND_REPRESENTATION_ITEM')
  contains(b'SHAPE_ASPECT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M027",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing surface-sampling-point validation property "
        "encoded as COMPOUND_REPRESENTATION_ITEM referencing SHAPE_ASPECT; "
        "input: AP242 STEP file where a B-spline surface re-fit during translation "
        "passes volume/area checks but has embedded (u,v,XYZ) sample points that "
        "do not match the reparametrized surface; "
        "LOTAR Geometric Validation: receiver must evaluate surface at each (u,v) "
        "and verify XYZ within tolerance; archive-reject on failure; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: surface sampling validation fails, validation property fails check, "
        "(u,v,XYZ) sample point mismatch, NURBS reparametrization breaks GVP"
    ),
)

# ── SHAPE_ASPECT to anchor the validation property ────────────────────────────
# Byte assertion: contains(b'SHAPE_ASPECT')
shape_aspect = f._emit_raw(
    "SHAPE_ASPECT('b_spline_face','surface sampling target',$,.F.)"
)

# ── Surface-sampling-point validation property ────────────────────────────────
# Encoded as COMPOUND_REPRESENTATION_ITEM holding a set of (u,v,x,y,z) tuples.
# Each sample: (u, v, X, Y, Z) — the receiver evaluates surf(u,v) and checks XYZ.
# Byte assertion: contains(b'COMPOUND_REPRESENTATION_ITEM')

# Individual sample points as VALUE_REPRESENTATION_ITEM (u,v,x,y,z packed)
samp0 = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('sample_0',MEASURE_VALUE(0.,0.,5.,3.,0.))"
)
samp1 = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('sample_1',MEASURE_VALUE(0.5,0.,5.,3.,2.5))"
)
samp2 = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('sample_2',MEASURE_VALUE(1.,0.,5.,3.,5.))"
)
samp3 = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('sample_3',MEASURE_VALUE(0.,0.5,2.5,1.5,0.))"
)
samp4 = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('sample_4',MEASURE_VALUE(0.5,0.5,2.5,1.5,2.5))"
)
samp5 = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('sample_5',MEASURE_VALUE(1.,0.5,2.5,1.5,5.))"
)

# COMPOUND_REPRESENTATION_ITEM groups the sample points
compound = f._emit_raw(
    f"COMPOUND_REPRESENTATION_ITEM('surface_sampling_points',"
    f"(#{samp0.eid},#{samp1.eid},#{samp2.eid},"
    f"#{samp3.eid},#{samp4.eid},#{samp5.eid}))"
)

# PROPERTY_DEFINITION linking the validation property to the shape aspect
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('surface sampling point set',"
    f"'LOTAR geometric validation property',#{shape_aspect.eid})"
)

# PROPERTY_DEFINITION_REPRESENTATION ties the compound item to the property
prop_rep = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{compound.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('surface-sampling-point-validation-failure',"
    f"(#{shape_aspect.eid},#{compound.eid},#{prop_def.eid},#{prop_rep.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M027.stp")
