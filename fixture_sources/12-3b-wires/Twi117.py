"""Twi117 — ShapeFix_Wire.FixNotchedEdges singular-derivative.

Catalog claim: Wire with edges whose 3D-curve derivatives are parallel at shared
vertex. Notch detector samples tangent angle but tangent is undefined at singular
derivative endpoint. Edge sequence: straight line (tangent: 1,0,0) followed by
cubic Bézier with zero derivative at start. FixNotchedEdges silently fails because
tangent vector is degenerate.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges:
  - e1: LINE from (0,0,0) to (5,0,0) — tangent (1,0,0) at its end
  - e2: B_SPLINE_CURVE_WITH_KNOTS of degree 3 (cubic Bézier); control points
    P0=(5,0,0), P1=(5,0,0), P2=(8,3,0), P3=(10,0,0).
    The first two control points are coincident at the start, giving a zero
    derivative at parameter=0: C'(0) = 3*(P1-P0) = (0,0,0). This is the
    singular derivative that defeats FixNotchedEdges' tangent-angle sampling.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi117",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 2 edges; "
        "e1: LINE (0,0,0)→(5,0,0) tangent (1,0,0) at endpoint; "
        "e2: B_SPLINE_CURVE_WITH_KNOTS degree-3 (cubic Bezier); "
        "control points P0=(5,0,0), P1=(5,0,0), P2=(8,3,0), P3=(10,0,0); "
        "P0==P1 => zero derivative C'(0)=(0,0,0) at start IS singular-derivative defect; "
        "FixNotchedEdges samples tangent angle but encounters degenerate "
        "zero-length tangent vector and silently fails; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ───────────────────────────────────────────────────────────────────
P_e1_start = (0.0,  0.0, 0.0)
P_junction = (5.0,  0.0, 0.0)   # e1 end / e2 start (shared vertex)
P_e2_end   = (10.0, 0.0, 0.0)

v_start    = f.vertex_point(f.cartesian_point(P_e1_start))
v_junction = f.vertex_point(f.cartesian_point(P_junction))
v_end      = f.vertex_point(f.cartesian_point(P_e2_end))

# ── Edge 1: straight line with tangent (1,0,0) ────────────────────────────────
e1 = f.edge_curve(
    v_start, v_junction,
    f.line(
        f.cartesian_point(P_e1_start),
        f.vector(f.direction((1.0, 0.0, 0.0)), 5.0),
    ),
)
oe1 = f.oriented_edge(e1, True)

# ── Edge 2: cubic Bézier with zero derivative at start ────────────────────────
# P0=P1=(5,0,0) => C'(0) = 3*(P1-P0) = (0,0,0) — singular derivative IS defect
bspline = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[
        f.cartesian_point((5.0, 0.0, 0.0)),   # P0
        f.cartesian_point((5.0, 0.0, 0.0)),   # P1 — same as P0 => zero C'(0)
        f.cartesian_point((8.0, 3.0, 0.0)),   # P2
        f.cartesian_point((10.0, 0.0, 0.0)),  # P3
    ],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
e2  = f.edge_curve(v_junction, v_end, bspline)
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP: two edges sharing v_junction ───────────────────────────────────
loop = f.edge_loop([oe1, oe2])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi117.stp")
