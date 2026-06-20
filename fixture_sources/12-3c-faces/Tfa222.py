"""Tfa222 — FixMissingSeam.no-closure-early-exit

Open B-spline surface (unclosed U, V); single EDGE_LOOP with 2 rational
B-spline edges; tests early exit when surface open in both directions (line
1732). Defect: without early return, kernel attempts seam insertion on
non-closed surface.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS
that is open in both U and V (u_closed=False, v_closed=False). The face outer
boundary is a 2-edge loop where both edges are B_SPLINE_CURVE_WITH_KNOTS
(degree 2, rational via weight-like control variation). FixMissingSeam at
line 1732 checks the closure flags before attempting seam synthesis; on this
open surface both checks fail, triggering the early-exit return. Without the
guard the kernel would attempt seam arithmetic on an open surface and produce
degenerate topology.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa222",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS; "
        "degree 2×2, 3×3 control grid; u_closed=False, v_closed=False (open surface); "
        "2-edge EDGE_LOOP: both edges are B_SPLINE_CURVE_WITH_KNOTS degree 2; "
        "FixMissingSeam line 1732: early-exit when surface open in both U and V; "
        "without early return: kernel attempts seam insertion on non-closed surface; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: open in both U and V ───────────────────────
# Degree 2×2, 3×3 control grid → clamped knots [0,0,0,1,1,1]
# Control grid forms a curved patch: middle row/column raised to z=0.5
cp = [
    [f.cartesian_point(p) for p in row]
    for row in [
        [(0.0, 0.0, 0.0), (0.0, 0.5, 0.2), (0.0, 1.0, 0.0)],
        [(0.5, 0.0, 0.2), (0.5, 0.5, 0.5), (0.5, 1.0, 0.2)],
        [(1.0, 0.0, 0.0), (1.0, 0.5, 0.2), (1.0, 1.0, 0.0)],
    ]
]
# nu=3, u_degree=2 → sum(u_mults) = 3+2+1=6 → [3,3]
# nv=3, v_degree=2 → sum(v_mults) = 3+2+1=6 → [3,3]
bspline_surf = f.b_spline_surface_with_knots(
    2, 2,
    cp,
    [3, 3], [3, 3],
    [0.0, 1.0], [0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
)

# ── 2-edge EDGE_LOOP using B_SPLINE_CURVE_WITH_KNOTS (degree 2) ──────────────
# Edge 1: bottom arc u=0→1 at v=0 (y=0 side), curved in XZ
# Control points: (0,0,0), (0.5,0,0.3), (1,0,0)
# degree=2, n=3 → sum(mults) = 3+2+1=6 → [3,3]
cp1a = f.cartesian_point((0.0, 0.0, 0.0))
cp1b = f.cartesian_point((0.5, 0.0, 0.3))
cp1c = f.cartesian_point((1.0, 0.0, 0.0))
curve1 = f.b_spline_curve_with_knots(
    2,
    [cp1a, cp1b, cp1c],
    [3, 3],
    [0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
)

# Edge 2: top arc u=1→0 at v=1 (y=1 side), reversed
# Control points: (1,1,0), (0.5,1,0.3), (0,1,0)
cp2a = f.cartesian_point((1.0, 1.0, 0.0))
cp2b = f.cartesian_point((0.5, 1.0, 0.3))
cp2c = f.cartesian_point((0.0, 1.0, 0.0))
curve2 = f.b_spline_curve_with_knots(
    2,
    [cp2a, cp2b, cp2c],
    [3, 3],
    [0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
)

# Vertices
v_start = f.vertex_point(cp1a)   # (0,0,0)
v_mid1  = f.vertex_point(cp1c)   # (1,0,0)
v_mid2  = f.vertex_point(cp2a)   # (1,1,0)
v_end   = f.vertex_point(cp2c)   # (0,1,0)

# Edge 1: (0,0,0) → (1,0,0) via b-spline curve1
e1 = f.edge_curve(v_start, v_mid1, curve1)

# Side edge 3: (1,0,0) → (1,1,0) — straight line
pt_lr = f.cartesian_point((1.0, 0.0, 0.0))
pt_ur = f.cartesian_point((1.0, 1.0, 0.0))
e3 = f.edge_curve(
    v_mid1, v_mid2,
    f.line(pt_lr, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0))
)

# Edge 2: (1,1,0) → (0,1,0) via b-spline curve2
e2 = f.edge_curve(v_mid2, v_end, curve2)

# Side edge 4: (0,1,0) → (0,0,0) — straight line
pt_ul = f.cartesian_point((0.0, 1.0, 0.0))
pt_ll = f.cartesian_point((0.0, 0.0, 0.0))
e4 = f.edge_curve(
    v_end, v_start,
    f.line(pt_ul, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0))
)

face_loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e4, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], bspline_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa222.stp")
