"""Os008 — Faces along a shared edge have mixed C0/G1 connectivity
(offset cannot decide regularity).

Catalog claim: Two faces meet along a shared edge that is C0 (a sharp crease)
on part of its length and G1 (smooth) on the rest. Offset must produce
different surface types for each subsection.

Mechanism: Two B-spline ADVANCED_FACEs sharing an edge whose underlying
B-spline curve has a knot of multiplicity = degree at the midpoint (creating
a C0/G1 discontinuity at t=0.5). Wrapped in OPEN_SHELL → SHELL_BASED_SURFACE_MODEL
so OCC loads as shape(1).

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "bspline"
  face[1].surface_type == "bspline"

Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os008",
    defect=(
        "OPEN_SHELL with two B-spline ADVANCED_FACEs sharing an edge whose "
        "underlying B_SPLINE_CURVE_WITH_KNOTS has a knot of multiplicity=degree "
        "at the midpoint (t=0.5), creating C0/G1 mixed connectivity; "
        "offset must split at the discontinuity — BRepOffset_MakeOffset "
        "MixedConnectivity; OCC loads (heals); conservative kernels reject"
    ),
)

# ── Shared edge: B-spline curve with C0 break at midpoint ────────────────────
# Degree 2, 5 control points, internal knot at 0.5 with multiplicity=2 (= degree)
# making a C0 discontinuity there. Knot vector: [0,0,0, 0.5,0.5, 1,1,1] (multiplicities [3,2,3])
cp0 = f.cartesian_point(( 0.0, 0.0, 0.0))
cp1 = f.cartesian_point(( 2.5, 0.0, 0.5))
cp2 = f.cartesian_point(( 5.0, 0.0, 1.0))   # crease point at t=0.5
cp3 = f.cartesian_point(( 7.5, 0.0, 0.5))
cp4 = f.cartesian_point((10.0, 0.0, 0.0))

shared_curve = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp0, cp1, cp2, cp3, cp4],
    knot_multiplicities=[3, 2, 3],
    knots=[0.0, 0.5, 1.0],
    name="shared_c0_edge",
)

v_start = f.vertex_point(cp0)
v_end   = f.vertex_point(cp4)
ec_shared = f.edge_curve(v_start, v_end, shared_curve, True, name="shared_edge")

# ── Face A: B-spline surface above the shared edge (z > 0) ───────────────────
# Simple bilinear B-spline surface: 2x2 control points, degree 1 in both directions
# Surface spans from shared edge (y=0) to y=5
cp_a00 = f.cartesian_point(( 0.0,  0.0, 0.0))
cp_a10 = f.cartesian_point((10.0,  0.0, 0.0))
cp_a01 = f.cartesian_point(( 0.0,  5.0, 0.0))
cp_a11 = f.cartesian_point((10.0,  5.0, 0.0))

surf_a = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=[[cp_a00, cp_a01], [cp_a10, cp_a11]],
    u_multiplicities=[2, 2], v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0], v_knots=[0.0, 1.0],
    name="bspline_surf_a",
)

# Boundary of face A: shared_edge + 3 straight lines closing the rectangle
p_a01 = f.cartesian_point(( 0.0, 5.0, 0.0)); v_a01 = f.vertex_point(p_a01)
p_a11 = f.cartesian_point((10.0, 5.0, 0.0)); v_a11 = f.vertex_point(p_a11)

e_a_left = f.edge_curve(
    v_start, v_a01,
    f.line(cp0, f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)),
    True, name="a_left"
)
e_a_top = f.edge_curve(
    v_a01, v_a11,
    f.line(p_a01, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)),
    True, name="a_top"
)
e_a_right = f.edge_curve(
    v_end, v_a11,
    f.line(cp4, f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)),
    True, name="a_right"
)

loop_a = f.edge_loop([
    f.oriented_edge(ec_shared, True),
    f.oriented_edge(e_a_right, True),
    f.oriented_edge(e_a_top, False),
    f.oriented_edge(e_a_left, False),
])
face_a = f.advanced_face([f.face_outer_bound(loop_a)], surf_a)

# ── Face B: B-spline surface below the shared edge (y < 0) ───────────────────
cp_b00 = f.cartesian_point(( 0.0,   0.0, 0.0))
cp_b10 = f.cartesian_point((10.0,   0.0, 0.0))
cp_b01 = f.cartesian_point(( 0.0,  -5.0, 0.0))
cp_b11 = f.cartesian_point((10.0,  -5.0, 0.0))

surf_b = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=[[cp_b00, cp_b01], [cp_b10, cp_b11]],
    u_multiplicities=[2, 2], v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0], v_knots=[0.0, 1.0],
    name="bspline_surf_b",
)

p_b01 = f.cartesian_point(( 0.0, -5.0, 0.0)); v_b01 = f.vertex_point(p_b01)
p_b11 = f.cartesian_point((10.0, -5.0, 0.0)); v_b11 = f.vertex_point(p_b11)

e_b_left = f.edge_curve(
    v_start, v_b01,
    f.line(cp0, f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)),
    True, name="b_left"
)
e_b_bot = f.edge_curve(
    v_b01, v_b11,
    f.line(p_b01, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)),
    True, name="b_bot"
)
e_b_right = f.edge_curve(
    v_end, v_b11,
    f.line(cp4, f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)),
    True, name="b_right"
)

loop_b = f.edge_loop([
    f.oriented_edge(ec_shared, False),   # shared edge reversed
    f.oriented_edge(e_b_left, True),
    f.oriented_edge(e_b_bot, True),
    f.oriented_edge(e_b_right, False),
])
face_b = f.advanced_face([f.face_outer_bound(loop_b)], surf_b)

# ── OPEN_SHELL wrapping both faces ───────────────────────────────────────────
shell = f._emit_raw(
    f"OPEN_SHELL('os008_mixed_c0g1',(#{face_a.eid},#{face_b.eid}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os008_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os008.stp")
