"""M033 — Constructive geometry / supplemental geometry not allowed type.

Catalog claim: Supplemental-geometry RP allows only specific entity types (point,
axis, plane, cylinder, etc.). The file uses an unsupported type (B_SPLINE_SURFACE_WITH_KNOTS)
inside CONSTRUCTIVE_GEOMETRY_REPRESENTATION, or omits some items referenced by GISU.

Reproducer recipe: constructive_geometry_representation whose items include a
B_SPLINE_SURFACE_WITH_KNOTS — an unsupported entity type.

Byte assertions:
  contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
  contains(b'B_SPLINE_SURFACE_WITH_KNOTS')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M033",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing CONSTRUCTIVE_GEOMETRY_REPRESENTATION whose "
        "items include B_SPLINE_SURFACE_WITH_KNOTS — an unsupported supplemental entity type; "
        "input: AP242 STEP file where a constructive_geometry_representation contains a "
        "b_spline_surface_with_knots (CAx-IF supplemental-geometry RP allows only point, "
        "axis, plane, cylinder, cone, sphere, torus — not B-spline surfaces); "
        "kernel must reject (drop) or warn-and-accept; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: supplemental geometry wrong type, CGR has unsupported entity, "
        "supplemental items beyond allowed list, GISU references wrong type"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS — forbidden type in supplemental geometry ─────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# A minimal degree-1 × degree-1 bilinear patch (2×2 control points).
# Control points for the B-spline surface
cp11 = f._emit_raw("CARTESIAN_POINT('cp11',(0.,0.,0.))")
cp12 = f._emit_raw("CARTESIAN_POINT('cp12',(10.,0.,0.))")
cp13 = f._emit_raw("CARTESIAN_POINT('cp13',(0.,10.,0.))")
cp14 = f._emit_raw("CARTESIAN_POINT('cp14',(10.,10.,0.))")

# Rebuild with proper control point references now that we have eids
# Re-emit the B-spline surface with actual entity references
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('supp_bspline',1,1,"
    f"((#{cp11.eid},#{cp12.eid}),(#{cp13.eid},#{cp14.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.,1.),(0.,1.),.PIECEWISE_BEZIER_KNOTS.)"
)

# Allowed supplemental geometry types for context (a plane — valid)
origin_pt = f._emit_raw("CARTESIAN_POINT('cgr_origin',(0.,0.,0.))")
z_dir = f._emit_raw("DIRECTION('cgr_z',(0.,0.,1.))")
x_dir = f._emit_raw("DIRECTION('cgr_x',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('cgr_placement',#{origin_pt.eid},#{z_dir.eid},#{x_dir.eid})"
)
plane = f._emit_raw(f"PLANE('supp_ref_plane',#{placement.eid})")

# ── CONSTRUCTIVE_GEOMETRY_REPRESENTATION with forbidden B-spline item ──────────
# Byte assertion: contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('supplemental_geom',"
    f"(#{plane.eid},#{bss.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('supplemental-geometry-unsupported-type',"
    f"(#{cgr.eid},#{plane.eid},#{bss.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M033.stp")
