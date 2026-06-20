"""Tfa201 — CheckSpotFace parametric interior singularity

B-spline face with interior peak singularity (pole height 3.5 vs 0.2
boundary). Tests parametric spot classification branch detecting interior
singularities without vertex-like discrete geometry.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS
(degree 2×2, 3×3 control grid). The control grid has a central pole at height
3.5 while the surrounding boundary poles sit at z=0.2. This creates an interior
peak — a parametric spot singularity — whose apex is not represented as a vertex
in the discrete topology. CheckSpotFace case 2: interior singularity detection
path at line 246; the classifier must recognize the interior peak through
parametric sampling rather than vertex proximity analysis.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa201",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS; "
        "degree 2×2, 3×3 control grid; "
        "central pole at z=3.5 (interior peak); boundary poles at z=0.2; "
        "interior peak ratio 3.5/0.2 = 17.5 — far exceeds spot threshold; "
        "no vertex entity at peak location — singularity purely parametric; "
        "CheckSpotFace case 2 at line 246: interior singularity detection; "
        "face boundary: unit square CCW at z≈0.2 perimeter; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B-spline surface: degree 2×2, 3×3 control grid ───────────────────────────
# U and V each run [0,1]. 3 control points per direction, degree=2 → clamped.
# Knot vectors: [0,0,0,1,1,1] multiplicities [3,3] knots [0,1]
# Control grid (u,v):
#   (0,0)=corner, (0,1)=edge, (0,2)=corner  — boundary row at z=0.2
#   (1,0)=edge,   (1,1)=PEAK, (1,2)=edge    — middle row: center at z=3.5
#   (2,0)=corner, (2,1)=edge, (2,2)=corner  — boundary row at z=0.2
z_bnd = 0.2
z_peak = 3.5

cp = [
    [f.cartesian_point(p) for p in row]
    for row in [
        [(0.0, 0.0, z_bnd), (0.0, 0.5, z_bnd), (0.0, 1.0, z_bnd)],
        [(0.5, 0.0, z_bnd), (0.5, 0.5, z_peak), (0.5, 1.0, z_bnd)],
        [(1.0, 0.0, z_bnd), (1.0, 0.5, z_bnd), (1.0, 1.0, z_bnd)],
    ]
]
bsurf = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=cp,
    u_multiplicities=[3, 3],
    v_multiplicities=[3, 3],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
)

# ── Face boundary: rectangular loop at surface perimeter ─────────────────────
# Corners at parametric extremes, 3D positions ≈ control grid corners
p_00 = f.cartesian_point((0.0, 0.0, z_bnd))
p_10 = f.cartesian_point((1.0, 0.0, z_bnd))
p_11 = f.cartesian_point((1.0, 1.0, z_bnd))
p_01 = f.cartesian_point((0.0, 1.0, z_bnd))

v_00 = f.vertex_point(p_00)
v_10 = f.vertex_point(p_10)
v_11 = f.vertex_point(p_11)
v_01 = f.vertex_point(p_01)

e_bot = f.edge_curve(v_00, v_10, f.line(p_00, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
e_rgt = f.edge_curve(v_10, v_11, f.line(p_10, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_top = f.edge_curve(v_11, v_01, f.line(p_11, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_lft = f.edge_curve(v_01, v_00, f.line(p_01, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], bsurf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa201.stp")
