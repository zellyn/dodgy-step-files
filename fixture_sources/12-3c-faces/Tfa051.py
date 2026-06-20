"""Tfa051 — Face needs splitting (knot insertion / sub-faces) for downstream tools.

Catalog claim: A face on a surface with internal C0 knots, large parameter
span, or multiple analytic regions. Downstream tools handle smaller pieces
better; meshers produce more uniform elements, Booleans avoid the C0 line,
fillet engines find tangents. The face-divide pipeline produces a shell of
replacement sub-faces.

Reproducer recipe (from catalog): A square face whose underlying surface has
a C0 line at U=0.5; the division must split the face into two sub-faces along
that isoline.

Mechanism: face[0] is a 10×10 ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS
with degree=2 in U, knot vector [0, 0.5, 1] and U-multiplicities [3, 2, 3].
Multiplicity=2=degree at U=0.5 creates a C0 crease (tangent discontinuity).
The surface is geometrically flat (a plane) but parameterically C0-kinked.
Control points form a 5×2 grid mapping [0,1]u × [0,1]v → 10×10 mm square.

The fixture is a closed box 10×10×1 mm:
  face[0]: bottom z=0 on B-spline C0 surface (THE DEFECT)
  face[1]: top z=1 (plane)
  face[2]: front y=0 (plane)
  face[3]: back y=10 (plane)
  face[4]: left x=0 (plane)
  face[5]: right x=10 (plane)

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "bspline"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa051",
    defect=(
        "CLOSED_SHELL: face[0] is 10×10 ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS "
        "(degree=2 in U, knots=[0,0.5,1], U-mults=[3,2,3]); "
        "internal U-multiplicity=2=degree at U=0.5 creates C0 crease (tangent discontinuity); "
        "surface is geometrically flat but parameterically C0-kinked at U=0.5; "
        "ShapeUpgrade_FaceDivide::Perform must split face[0] into two sub-faces at U=0.5; "
        "downstream meshers need smaller pieces; Booleans avoid C0 line; "
        "face[1..5] are plane faces forming closed 10×10×1 box; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Box dimensions
X = 10.0; Y = 10.0; H = 1.0

# Box vertices (z=0 bottom, z=H top)
p000 = f.cartesian_point((0.0, 0.0, 0.0)); p100 = f.cartesian_point((X,   0.0, 0.0))
p110 = f.cartesian_point((X,   Y,   0.0)); p010 = f.cartesian_point((0.0, Y,   0.0))
p001 = f.cartesian_point((0.0, 0.0, H));   p101 = f.cartesian_point((X,   0.0, H))
p111 = f.cartesian_point((X,   Y,   H));   p011 = f.cartesian_point((0.0, Y,   H))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom edges (z=0)
eb0 = f.edge_curve(v000, v100, f.line(p000, f.vector(f.direction(( 1.0, 0.0, 0.0)), X)))
eb1 = f.edge_curve(v100, v110, f.line(p100, f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))
eb2 = f.edge_curve(v110, v010, f.line(p110, f.vector(f.direction((-1.0, 0.0, 0.0)), X)))
eb3 = f.edge_curve(v010, v000, f.line(p010, f.vector(f.direction(( 0.0,-1.0, 0.0)), Y)))

# Top edges (z=H)
et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), X)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), X)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), Y)))

# Vertical edges
ev0 = f.edge_curve(v000, v001, f.line(p000, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev1 = f.edge_curve(v100, v101, f.line(p100, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev2 = f.edge_curve(v110, v111, f.line(p110, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev3 = f.edge_curve(v010, v011, f.line(p010, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# ── face[0]: bottom z=0 on B-SPLINE surface with C0 crease at U=0.5 ──────────
# B-spline surface: degree=2 in U, degree=1 in V
# U knots: [0, 0.5, 1], U-mults: [3, 2, 3] → sum=8
# Control points: nu=8-2-1=5 rows
# V knots: [0, 1], V-mults: [2, 2] → sum=4
# Control points: nv=4-1-1=2 cols
# 5×2 control points: U maps 0→0→5→10 mm (with C0 kink at U=0.5=X/2=5mm)
# V maps 0→0 mm, 1→10 mm
cp = [
    [f.cartesian_point(( 0.0, 0.0, 0.0)), f.cartesian_point(( 0.0, Y, 0.0))],  # u=0
    [f.cartesian_point(( 2.5, 0.0, 0.0)), f.cartesian_point(( 2.5, Y, 0.0))],  # u=0..0.5
    [f.cartesian_point(( 5.0, 0.0, 0.0)), f.cartesian_point(( 5.0, Y, 0.0))],  # u=0.5 (C0)
    [f.cartesian_point(( 7.5, 0.0, 0.0)), f.cartesian_point(( 7.5, Y, 0.0))],  # u=0.5..1
    [f.cartesian_point((10.0, 0.0, 0.0)), f.cartesian_point((10.0, Y, 0.0))],  # u=1
]
bspline_surf = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=cp,
    u_multiplicities=[3, 2, 3],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 0.5, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    knot_spec="UNSPECIFIED",
)

bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
face0 = f.advanced_face([f.face_outer_bound(bot_loop)], bspline_surf)

# ── face[1]: top z=H (plane) ─────────────────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(et1, True),
    f.oriented_edge(et2, True), f.oriented_edge(et3, True),
])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face1 = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── face[2]: front y=0 ───────────────────────────────────────────────────────
frt_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(ev1, True),
    f.oriented_edge(et0, False), f.oriented_edge(ev0, False),
])
ax_frt = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# ── face[3]: back y=Y ────────────────────────────────────────────────────────
bk_loop = f.edge_loop([
    f.oriented_edge(ev3, True), f.oriented_edge(et2, False),
    f.oriented_edge(ev2, False), f.oriented_edge(eb2, False),
])
ax_bk = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# ── face[4]: left x=0 ────────────────────────────────────────────────────────
lft_loop = f.edge_loop([
    f.oriented_edge(ev0, True), f.oriented_edge(et3, False),
    f.oriented_edge(ev3, False), f.oriented_edge(eb3, False),
])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# ── face[5]: right x=X ───────────────────────────────────────────────────────
rgt_loop = f.edge_loop([
    f.oriented_edge(eb1, True), f.oriented_edge(ev2, True),
    f.oriented_edge(et1, False), f.oriented_edge(ev1, False),
])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face5 = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4, face5])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa051.stp")
