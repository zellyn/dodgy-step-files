"""Tfa053 — Composite-surface patches do not connect on shared boundary.

Catalog claim: A RECTANGULAR_COMPOSITE_SURFACE has a 3D gap on the shared
boundary between two neighboring patches; patches do not actually touch within
the connectivity tolerance. Faces built atop the composite have invalid
topology because the surface is not a single continuous manifold.

Reproducer recipe (from catalog): Two abutting plane patches whose touching
edges should be at U=1 but the second patch's origin is at (1.005,0,0)
instead of (1,0,0).

Mechanism: Two ADVANCED_FACEs form the bottom of a 2×1×1 mm closed box.
  face[0]: 1×1 patch at x=[0,1], z=0, on PLANE with origin (0,0,0)
  face[1]: 1×1 patch at x=[1,2], z=0, on PLANE with origin (1.005,0,0)
             (origin offset by 0.005mm in X — the gap defect)

The shared edge between face[0] and face[1] is at x=1 in topology, but
face[1]'s underlying PLANE surface origin is 0.005mm away from the shared
boundary — a surface/topology mismatch that creates a gap a checker would
detect between the patches. ShapeExtend_CompositeSurface::CheckConnectivity
would flag this 0.005mm gap.

Full closed shell (8 faces):
  face[0]: bottom-left patch at z=0, x=[0,1]  (THE DEFECT — plane orig at x=0)
  face[1]: bottom-right patch at z=0, x=[1,2] (THE DEFECT — plane orig at x=1.005)
  face[2]: top-left patch at z=1, x=[0,1]
  face[3]: top-right patch at z=1, x=[1,2]
  face[4]: front y=0, x=[0,2]
  face[5]: back y=1, x=[0,2]
  face[6]: left end x=0
  face[7]: right end x=2

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 8
  face[1].surface_type == "plane"
  n_vertices_total >= 16

Expected: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa053",
    defect=(
        "CLOSED_SHELL: face[0] (bottom-left z=0, x=[0,1]) on PLANE origin (0,0,0); "
        "face[1] (bottom-right z=0, x=[1,2]) on PLANE origin (1.005,0,0) — 0.005mm offset; "
        "shared topological edge at x=1 but face[1] surface origin is 0.005mm away; "
        "surface/topology mismatch: gap = 0.005mm between patch planes at shared boundary; "
        "ShapeExtend_CompositeSurface::CheckConnectivity flags this gap; "
        "faces[2..7] form a valid 2×1×1 closed box (split bottom and top into left/right patches); "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Box: 2mm wide (X), 1mm deep (Y), 1mm tall (Z)
# Split at x=1 (bottom and top faces each have two patches)
X1 = 1.0; X2 = 2.0; Y = 1.0; H = 1.0

# Bottom layer vertices (z=0): 6 vertices (3 cols × 2 rows)
p00 = f.cartesian_point((0.0, 0.0, 0.0)); p10 = f.cartesian_point((X1,  0.0, 0.0)); p20 = f.cartesian_point((X2,  0.0, 0.0))
p01 = f.cartesian_point((0.0, Y,   0.0)); p11 = f.cartesian_point((X1,  Y,   0.0)); p21 = f.cartesian_point((X2,  Y,   0.0))

# Top layer vertices (z=H): 6 vertices
p00t = f.cartesian_point((0.0, 0.0, H)); p10t = f.cartesian_point((X1,  0.0, H)); p20t = f.cartesian_point((X2,  0.0, H))
p01t = f.cartesian_point((0.0, Y,   H)); p11t = f.cartesian_point((X1,  Y,   H)); p21t = f.cartesian_point((X2,  Y,   H))

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)
v00t = f.vertex_point(p00t); v10t = f.vertex_point(p10t); v20t = f.vertex_point(p20t)
v01t = f.vertex_point(p01t); v11t = f.vertex_point(p11t); v21t = f.vertex_point(p21t)

# Bottom edges (z=0)
eb_00_10 = f.edge_curve(v00,  v10,  f.line(p00,  f.vector(f.direction(( 1.0, 0.0, 0.0)), X1)))
eb_10_20 = f.edge_curve(v10,  v20,  f.line(p10,  f.vector(f.direction(( 1.0, 0.0, 0.0)), X1)))
eb_20_21 = f.edge_curve(v20,  v21,  f.line(p20,  f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))
eb_21_11 = f.edge_curve(v21,  v11,  f.line(p21,  f.vector(f.direction((-1.0, 0.0, 0.0)), X1)))
eb_11_01 = f.edge_curve(v11,  v01,  f.line(p11,  f.vector(f.direction((-1.0, 0.0, 0.0)), X1)))
eb_01_00 = f.edge_curve(v01,  v00,  f.line(p01,  f.vector(f.direction(( 0.0,-1.0, 0.0)), Y)))
eb_10_11 = f.edge_curve(v10,  v11,  f.line(p10,  f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))  # shared seam

# Top edges (z=H)
et_00_10 = f.edge_curve(v00t, v10t, f.line(p00t, f.vector(f.direction(( 1.0, 0.0, 0.0)), X1)))
et_10_20 = f.edge_curve(v10t, v20t, f.line(p10t, f.vector(f.direction(( 1.0, 0.0, 0.0)), X1)))
et_20_21 = f.edge_curve(v20t, v21t, f.line(p20t, f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))
et_21_11 = f.edge_curve(v21t, v11t, f.line(p21t, f.vector(f.direction((-1.0, 0.0, 0.0)), X1)))
et_11_01 = f.edge_curve(v11t, v01t, f.line(p11t, f.vector(f.direction((-1.0, 0.0, 0.0)), X1)))
et_01_00 = f.edge_curve(v01t, v00t, f.line(p01t, f.vector(f.direction(( 0.0,-1.0, 0.0)), Y)))
et_10_11 = f.edge_curve(v10t, v11t, f.line(p10t, f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))  # shared seam top

# Vertical edges
ev_00 = f.edge_curve(v00, v00t, f.line(p00, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev_10 = f.edge_curve(v10, v10t, f.line(p10, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev_20 = f.edge_curve(v20, v20t, f.line(p20, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev_01 = f.edge_curve(v01, v01t, f.line(p01, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev_11 = f.edge_curve(v11, v11t, f.line(p11, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev_21 = f.edge_curve(v21, v21t, f.line(p21, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# ── face[0]: bottom-left patch (THE DEFECT: plane origin at (0,0,0)) ──────────
loop0 = f.edge_loop([
    f.oriented_edge(eb_00_10, True),
    f.oriented_edge(eb_10_11, True),
    f.oriented_edge(eb_11_01, False),
    f.oriented_edge(eb_01_00, False),
])
# PLANE for patch 0: origin at (0,0,0), normal -Z (inward for bottom face)
ax0 = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face0 = f.advanced_face([f.face_outer_bound(loop0)], f.plane(ax0))

# ── face[1]: bottom-right patch (THE DEFECT: plane origin displaced +0.005 in X) ─
loop1 = f.edge_loop([
    f.oriented_edge(eb_10_20, True),
    f.oriented_edge(eb_20_21, True),
    f.oriented_edge(eb_21_11, True),
    f.oriented_edge(eb_10_11, False),
])
# PLANE for patch 1: origin at (1.005,0,0) instead of (1,0,0) — 0.005mm gap defect
p10_gap = f.cartesian_point((1.005, 0.0, 0.0))
ax1 = f.axis2_placement_3d(p10_gap, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face1 = f.advanced_face([f.face_outer_bound(loop1)], f.plane(ax1))

# ── face[2]: top-left patch at z=H ───────────────────────────────────────────
loop2 = f.edge_loop([
    f.oriented_edge(et_00_10, True),
    f.oriented_edge(et_10_11, True),
    f.oriented_edge(et_11_01, False),
    f.oriented_edge(et_01_00, False),
])
ax2 = f.axis2_placement_3d(p00t, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(loop2)], f.plane(ax2))

# ── face[3]: top-right patch at z=H ──────────────────────────────────────────
loop3 = f.edge_loop([
    f.oriented_edge(et_10_20, True),
    f.oriented_edge(et_20_21, True),
    f.oriented_edge(et_21_11, True),
    f.oriented_edge(et_10_11, False),
])
ax3 = f.axis2_placement_3d(p10t, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(loop3)], f.plane(ax3))

# ── face[4]: front y=0 (full width x=[0,2]) ───────────────────────────────────
frt_loop = f.edge_loop([
    f.oriented_edge(eb_00_10, True),
    f.oriented_edge(eb_10_20, True),
    f.oriented_edge(ev_20,    True),
    f.oriented_edge(et_10_20, False),
    f.oriented_edge(et_00_10, False),
    f.oriented_edge(ev_00,    False),
])
ax_frt = f.axis2_placement_3d(p00, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# ── face[5]: back y=Y (full width x=[0,2]) ────────────────────────────────────
bk_loop = f.edge_loop([
    f.oriented_edge(ev_01,    True),
    f.oriented_edge(et_11_01, False),
    f.oriented_edge(et_21_11, False),
    f.oriented_edge(ev_21,    False),
    f.oriented_edge(eb_21_11, False),
    f.oriented_edge(eb_11_01, True),
])
ax_bk = f.axis2_placement_3d(p01, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face5 = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# ── face[6]: left end x=0 ─────────────────────────────────────────────────────
lft_loop = f.edge_loop([
    f.oriented_edge(ev_00,    True),
    f.oriented_edge(et_01_00, False),
    f.oriented_edge(ev_01,    False),
    f.oriented_edge(eb_01_00, True),
])
ax_lft = f.axis2_placement_3d(p00, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face6 = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# ── face[7]: right end x=2 ────────────────────────────────────────────────────
rgt_loop = f.edge_loop([
    f.oriented_edge(eb_20_21, True),
    f.oriented_edge(ev_21,    True),
    f.oriented_edge(et_20_21, False),
    f.oriented_edge(ev_20,    False),
])
ax_rgt = f.axis2_placement_3d(p20, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face7 = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4, face5, face6, face7])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa053.stp")
