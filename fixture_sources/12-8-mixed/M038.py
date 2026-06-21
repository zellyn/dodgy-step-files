"""M038 — AP209 freedom_and_coefficient a != 1, or single_point_constraint b != 0.

Catalog claim: Constraint coefficient values violate the SPC simplifying
assumptions (RP requires a==1, b==0).

Reproducer recipe: freedom_and_coefficient entity with a=2.0, paired with a
single_point_constraint whose b=0.001.

Byte assertions:
  contains(b'FREEDOM_AND_COEFFICIENT')
  contains(b'2.0')
  contains(b'SINGLE_POINT_CONSTRAINT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M038",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 SPC boundary condition with "
        "nonstandard constraint coefficients; "
        "input: AP242/AP209 STEP file where FREEDOM_AND_COEFFICIENT has a=2.0 "
        "(RP requires a==1) and SINGLE_POINT_CONSTRAINT has b=0.001 "
        "(RP requires b==0); "
        "per ISO 10303-104 AP209 the simplifying assumptions for SPC are a==1, b==0; "
        "a nonstandard 'a' scales the constrained DOF; nonzero 'b' shifts it; "
        "kernel must warn and proceed, honoring the actual values rather than "
        "silently clamping them to the assumed defaults; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: AP209 SPC coefficient nonstandard, freedom_and_coefficient a!=1, "
        "single_point_constraint b!=0, BC simplifying assumptions violated"
    ),
)

# ── Constrained node geometry ─────────────────────────────────────────────────
node_pt = f._emit_raw("CARTESIAN_POINT('constrained_node',(1.,2.,3.))")

# ── FREEDOM_AND_COEFFICIENT with a=2.0 (nonstandard; RP requires a==1) ────────
# Byte assertion: contains(b'FREEDOM_AND_COEFFICIENT')
# Byte assertion: contains(b'2.0')
freedom_coeff = f._emit_raw(
    "FREEDOM_AND_COEFFICIENT('constrained_dof_x',.X.,2.0)"
)

# ── SINGLE_POINT_CONSTRAINT with b=0.001 (nonstandard; RP requires b==0) ──────
# Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT')
spc = f._emit_raw(
    f"SINGLE_POINT_CONSTRAINT('spc_nonstandard_b',"
    f"(#{freedom_coeff.eid}),0.001)"
)

# Additional freedom_and_coefficient to show the 'a' field clearly
freedom_coeff2 = f._emit_raw(
    "FREEDOM_AND_COEFFICIENT('constrained_dof_y',.Y.,2.0)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ap209-spc-nonstandard-coefficients',"
    f"(#{freedom_coeff.eid},#{spc.eid},#{freedom_coeff2.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M038.stp")
