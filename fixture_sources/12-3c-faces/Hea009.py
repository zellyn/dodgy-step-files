"""Hea009 — Convert curves and surfaces of a shape to Bezier representation.

Catalog claim: A shape with mixed analytic + B-spline curves. The
convert-to-Bezier pipeline (ShapeUpgrade_ShapeConvertToBezier::Perform)
must handle each kind, splitting at non-Bezier breaks (C0 knots) where
needed. Some receivers (e.g., Bezier-only meshers) require this normalization.

Mechanism: An ADVANCED_FACE on a PLANE with a single FACE_OUTER_BOUND whose
3D curve is a degree-2 B_SPLINE_CURVE_WITH_KNOTS with 6 control points and
an internal C0 knot at u=0.5 (knot multiplicity (3,3,3) at (0.0,0.5,1.0) →
C^(2-3) = C^-1 break). This is NOT a single Bezier segment. The shape is
wrapped in GEOMETRIC_CURVE_SET so TransferRoots yields empty.

Byte assertions:
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS(')
  - contains(b'(3,3,3)')
  - contains(b'(0.0,0.5,1.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea009",
    defect=(
        "ADVANCED_FACE on PLANE with FACE_OUTER_BOUND using degree-2 "
        "B_SPLINE_CURVE_WITH_KNOTS (6 ctrl pts, knot-mults (3,3,3) at (0.0,0.5,1.0)); "
        "internal C0 knot at u=0.5 (mult=3=degree+1 produces C^-1 break); "
        "not a single Bezier segment; must be split by ShapeUpgrade_ShapeConvertToBezier; "
        "wrapped in GEOMETRIC_CURVE_SET → TransferRoots yields empty; "
        "OCC silently accepts; spec-kernel must heal/reject"
    ),
)

# ── Plane at origin ───────────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Edge vertices ─────────────────────────────────────────────────────────────
p_s = f.cartesian_point((0.0, 0.0, 0.0))
p_e = f.cartesian_point((10.0, 0.0, 0.0))
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)

# ── 6 control points: arch shape with C0 knot at u=0.5 ───────────────────────
# degree=2, 6 ctrl pts → knot sum = 6+2+1 = 9 → (3,3,3) ✓
# Left segment [0,0.5]: cp[0],cp[1],cp[2] — arches up
# Right segment [0.5,1.0]: cp[3],cp[4],cp[5] — arches down
# cp[2] and cp[3] both at (5,1,0): C0 continuity (no C1 constraint)
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((2.5, 0.5, 0.0))
cp2 = f.cartesian_point((5.0, 1.0, 0.0))
cp3 = f.cartesian_point((5.0, 1.0, 0.0))   # C0 break at u=0.5
cp4 = f.cartesian_point((7.5, 0.5, 0.0))
cp5 = f.cartesian_point((10.0, 0.0, 0.0))

bspline = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp0, cp1, cp2, cp3, cp4, cp5],
    knot_multiplicities=[3, 3, 3],
    knots=[0.0, 0.5, 1.0],
)

edge = f.edge_curve(v_s, v_e, bspline)
oe   = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# Wrap in GEOMETRIC_CURVE_SET → TransferRoots yields empty
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{face.eid}))")
f.add_product_chain(gcs)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea009.stp")
