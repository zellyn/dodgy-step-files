"""Tfa048 — Strip face flagged using caller-supplied tolerance.

Catalog claim: A face that is a strip only at tolerances larger than its own
edge tolerances. The caller supplies a tolerance band; the analyzer determines
whether the face fits the band (its width is less than the supplied tolerance).
Permits queries like "is this face a strip at 1mm tolerance?" independent of
its own tolerance metadata.

Reproducer recipe (from catalog): A 100x0.5 face whose edge tolerances are
1e-7 — only a strip at tolerances >= 0.5.

Mechanism: face[0] is a 100×0.001 mm strip ADVANCED_FACE on a PLANE.
The strip width (0.001mm) is far below the caller-supplied threshold (0.5mm),
satisfying the band check at the caller-supplied tolerance. The face's own
edge tolerances are 1e-7 (default), so it is NOT a strip at the default tol —
only at caller tol >= 0.001.

Sliver aspect ratio = 100/0.001 = 1e5 > 1e3 (strip assertion).

The fixture is a thin rectangular prism (box) 100×0.001×1 mm:
  face[0]: bottom strip, 100×0.001 at z=0   (THE DEFECT — strip face)
  face[1]: top strip,    100×0.001 at z=1
  face[2]: long side A,  100×1    at y=0
  face[3]: long side B,  100×1    at y=0.001
  face[4]: short end A,  0.001×1  at x=0
  face[5]: short end B,  0.001×1  at x=100

The CLOSED_SHELL wraps the prism and places face[0] (the strip) on the
live traversal path.

Tier-3 assertions:
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa048",
    defect=(
        "CLOSED_SHELL: face[0] is 100×0.001 strip ADVANCED_FACE on PLANE at z=0; "
        "strip width = 0.001 mm, aspect ratio = 1e5 > 1e3; "
        "face own edge tolerances = 1e-7 — strip only detectable at caller-supplied tol >= 0.001; "
        "ShapeAnalysis_CheckSmallFace::CheckStripFace accepts caller tolerance parameter; "
        "caller-supplied tol = 0.5 flags this face as strip; default tol does not; "
        "face[1..5] form valid prism sides (100x0.001x1 box) to make closed shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

L = 100.0    # long dimension X
W = 0.001    # short dimension Y (strip width, sub-tolerance)
H = 1.0      # height Z

# Prism vertices: 8 corners of the 100×0.001×1 box
# bottom z=0
p_A = f.cartesian_point((  0.0, 0.0, 0.0))   # A
p_B = f.cartesian_point((  L,   0.0, 0.0))   # B
p_C = f.cartesian_point((  L,   W,   0.0))   # C
p_D = f.cartesian_point((  0.0, W,   0.0))   # D
# top z=H
p_E = f.cartesian_point((  0.0, 0.0, H))     # E
p_F = f.cartesian_point((  L,   0.0, H))     # F
p_G = f.cartesian_point((  L,   W,   H))     # G
p_H = f.cartesian_point((  0.0, W,   H))     # H

vA = f.vertex_point(p_A); vB = f.vertex_point(p_B)
vC = f.vertex_point(p_C); vD = f.vertex_point(p_D)
vE = f.vertex_point(p_E); vF = f.vertex_point(p_F)
vG = f.vertex_point(p_G); vH = f.vertex_point(p_H)

# Bottom edges (z=0): A→B, B→C, C→D, D→A
eAB = f.edge_curve(vA, vB, f.line(p_A, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eBC = f.edge_curve(vB, vC, f.line(p_B, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eCD = f.edge_curve(vC, vD, f.line(p_C, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eDA = f.edge_curve(vD, vA, f.line(p_D, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Top edges (z=H): E→F, F→G, G→H, H→E
eEF = f.edge_curve(vE, vF, f.line(p_E, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eFG = f.edge_curve(vF, vG, f.line(p_F, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eGH = f.edge_curve(vG, vH, f.line(p_G, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eHE = f.edge_curve(vH, vE, f.line(p_H, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Vertical edges: A→E, B→F, C→G, D→H
eAE = f.edge_curve(vA, vE, f.line(p_A, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eBF = f.edge_curve(vB, vF, f.line(p_B, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eCG = f.edge_curve(vC, vG, f.line(p_C, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eDH = f.edge_curve(vD, vH, f.line(p_D, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# ── face[0]: bottom strip at z=0 — THE DEFECT ──────────────────────────────────
bot_loop = f.edge_loop([
    f.oriented_edge(eAB, True),
    f.oriented_edge(eBC, True),
    f.oriented_edge(eCD, True),
    f.oriented_edge(eDA, True),
])
ax_bot = f.axis2_placement_3d(p_A, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face0 = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── face[1]: top strip at z=H ────────────────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(eEF, True),
    f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True),
    f.oriented_edge(eHE, True),
])
ax_top = f.axis2_placement_3d(p_E, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face1 = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── face[2]: long side at y=0 (front, 100×1) ──────────────────────────────────
# Winding: A→B→F→E (outward normal = -Y)
frt_loop = f.edge_loop([
    f.oriented_edge(eAB, True),
    f.oriented_edge(eBF, True),
    f.oriented_edge(eEF, False),
    f.oriented_edge(eAE, False),
])
ax_frt = f.axis2_placement_3d(p_A, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# ── face[3]: long side at y=W (back, 100×1) ───────────────────────────────────
# Winding: D→H→G→C (outward normal = +Y)
bk_loop = f.edge_loop([
    f.oriented_edge(eDH, True),
    f.oriented_edge(eGH, False),
    f.oriented_edge(eCG, False),
    f.oriented_edge(eCD, False),
])
ax_bk = f.axis2_placement_3d(p_D, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# ── face[4]: short end at x=0 (left, 0.001×1) ───────────────────────────────
# Winding: A→E→H→D (outward normal = -X)
lft_loop = f.edge_loop([
    f.oriented_edge(eAE, True),
    f.oriented_edge(eHE, False),
    f.oriented_edge(eDH, False),
    f.oriented_edge(eDA, False),
])
ax_lft = f.axis2_placement_3d(p_A, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# ── face[5]: short end at x=L (right, 0.001×1) ──────────────────────────────
# Winding: B→C→G→F (outward normal = +X)
rgt_loop = f.edge_loop([
    f.oriented_edge(eBC, True),
    f.oriented_edge(eCG, True),
    f.oriented_edge(eFG, False),
    f.oriented_edge(eBF, False),
])
ax_rgt = f.axis2_placement_3d(p_B, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face5 = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4, face5])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa048.stp")
