"""M036 — Datum target axes nearly identical.

Catalog claim: Two direction vectors used to define a datum-target or
supplemental-geometry frame have a cross-product norm <= 0.05; orthonormal
frame cannot be reliably constructed.

Reproducer recipe: Datum target axis with two near-parallel direction ratios.

Byte assertions:
  contains(b'0.001')
  contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M036",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing datum-target frame with near-parallel "
        "DIRECTION vectors whose cross-product norm is <= 0.05; "
        "input: AP242 STEP file where two direction vectors used to define a "
        "datum-target or supplemental-geometry AXIS2_PLACEMENT_3D are nearly "
        "identical (angle < 0.05 rad), making the orthonormal frame ill-conditioned; "
        "the z-axis is (0.,0.,1.) and x-axis is (0.001,0.,1.) — norm of cross "
        "product is ~0.001, below the 0.05 threshold; "
        "kernel must warn and heal by substituting a numerically stable frame, "
        "or reject with a diagnostic; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: datum target axes nearly identical, near-collinear DIRECTION pair, "
        "frame cross-product near zero, datum frame ill-conditioned"
    ),
)

# ── Near-parallel direction vectors for the datum-target frame ────────────────
# Byte assertion: contains(b'0.001')
# z-axis and x-axis are nearly parallel — cross product norm ~ 0.001
origin_pt = f._emit_raw("CARTESIAN_POINT('datum_target_origin',(0.,0.,0.))")
z_dir = f._emit_raw("DIRECTION('datum_target_z',(0.,0.,1.))")
# x-axis nearly parallel to z — the cross-product norm is ||(0,0,1) x (0.001,0,1)|| ~ 0.001
x_dir_near_parallel = f._emit_raw("DIRECTION('datum_target_x',(0.001,0.,1.))")

# AXIS2_PLACEMENT_3D using the ill-conditioned pair
bad_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('datum_target_frame',"
    f"#{origin_pt.eid},#{z_dir.eid},#{x_dir_near_parallel.eid})"
)

# Datum target referencing the ill-conditioned frame
datum_target = f._emit_raw(
    f"PLANE('datum_target_plane',#{bad_placement.eid})"
)

# ── CONSTRUCTIVE_GEOMETRY_REPRESENTATION wrapping the datum target ─────────────
# Byte assertion: contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('datum_target_supplemental_geom',"
    f"(#{datum_target.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('datum-target-axes-nearly-identical',"
    f"(#{cgr.eid},#{datum_target.eid},#{bad_placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M036.stp")
