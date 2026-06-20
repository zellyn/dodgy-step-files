"""Tfa070 — CURVE_BOUNDED_SURFACE.implicit_outer = .U. (unset BOOLEAN) leaves boundary semantics ambiguous.

Catalog claim: The CURVE_BOUNDED_SURFACE.implicit_outer BOOLEAN slot is set to
.U. (undefined) rather than .T. or .F.. step-g's getBooleanAttribute accepts a
third state BUnset; because LoadONBrep is a stub the face is silently dropped.
The schema-strict reading is to reject.

Mechanism IS a GEOMETRIC_CURVE_SET containing a CURVE_BOUNDED_SURFACE with
implicit_outer = .U.. The surface basis is a PLANE. A single B_SPLINE_CURVE
boundary traces a rectangle. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'CURVE_BOUNDED_SURFACE')
  - contains(b'.U.')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa070",
    defect=(
        "GEOMETRIC_CURVE_SET containing CURVE_BOUNDED_SURFACE with implicit_outer=.U.; "
        "basis surface is a PLANE at z=0; "
        "one boundary curve: a B_SPLINE_CURVE tracing the rectangle [0,10]x[0,10]; "
        "implicit_outer left as .U. (undefined BOOLEAN) — receiver cannot determine "
        "whether natural surface boundary is implicit outer loop; "
        "step-g LoadONBrep is a stub — face silently dropped; "
        "schema-strict receivers must reject with E_AMBIGUOUS_IMPLICIT_OUTER; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane basis surface ───────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Boundary curve: degree-1 B_SPLINE_CURVE tracing rectangle [0,10]x[0,10] ─
# Four corners + closing point (5 control points, closed polyline as B-spline)
c0 = f.cartesian_point(( 0.0,  0.0, 0.0))
c1 = f.cartesian_point((10.0,  0.0, 0.0))
c2 = f.cartesian_point((10.0, 10.0, 0.0))
c3 = f.cartesian_point(( 0.0, 10.0, 0.0))
c4 = f.cartesian_point(( 0.0,  0.0, 0.0))   # closing point = c0

ctrl_pts = f"(#{c0.eid},#{c1.eid},#{c2.eid},#{c3.eid},#{c4.eid})"
# degree-1, 5 poles → 6 knots with multiplicities
bsc = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('rect_boundary',1,"
    f"{ctrl_pts},"
    ".UNSPECIFIED.,.F.,.F.,"
    "(2,1,1,1,2),"
    "(0.0,1.0,2.0,3.0,4.0),"
    ".UNSPECIFIED.)"
)

# ── CURVE_BOUNDED_SURFACE with implicit_outer = .U. ──────────────────────────
cbs = f._emit_raw(
    f"CURVE_BOUNDED_SURFACE('cbs_face',#{plane.eid},(#{bsc.eid}),.U.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{cbs.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa070.stp")
