"""Tfa104 — ShapeAnalysis_CheckSmallFace.CheckSplittingVertices NM-vertex.

Catalog claim: Face with a non-manifold vertex (used by 3+ edges);
CheckSplittingVertices' splitting plan only handles 2-edge incidence.

Mechanism: MANIFOLD_SOLID_BREP with a planar face where a central vertex is
shared by 3 edges (non-manifold, 3-edge incidence). The face is topologically
a "star" — three triangular sub-regions meeting at the central vertex. Each
triangle is a triangle edge, and all three triangles share the same central
vertex entity. CheckSplittingVertices only handles 2-edge incidence, so the
3-edge non-manifold central vertex is not properly split.

A second valid flat face is included to give OCC enough topology to load
shape(1).

Tier-3 assertion: n_faces_total == 2

Expected: occt=shape(1)/shape(1) gmsh=shape(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa104",
    defect=(
        "CLOSED_SHELL: planar ADVANCED_FACE with non-manifold central vertex shared by "
        "3 edges (three triangular sub-regions meeting at one vertex point); "
        "ShapeAnalysis_CheckSmallFace::CheckSplittingVertices splitting plan only "
        "handles 2-edge incidence — 3-edge non-manifold vertex is not handled; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Central non-manifold vertex shared by 3 triangle edges
p_center = f.cartesian_point((0.0, 0.0, 0.0))
v_center = f.vertex_point(p_center)

# Three outer vertices forming the triangular "star"
p_A = f.cartesian_point(( 2.0,  0.0, 0.0))
p_B = f.cartesian_point((-1.0,  1.732, 0.0))   # approx (-1, sqrt(3), 0)
p_C = f.cartesian_point((-1.0, -1.732, 0.0))   # approx (-1, -sqrt(3), 0)

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

# Three edges from center to each outer vertex
e_cA = f.edge_curve(v_center, v_A, f.line(p_center, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
e_cB = f.edge_curve(v_center, v_B, f.line(p_center, f.vector(f.direction((-0.5, 0.866, 0.0)), 2.0)))
e_cC = f.edge_curve(v_center, v_C, f.line(p_center, f.vector(f.direction((-0.5, -0.866, 0.0)), 2.0)))

# Two outer edges needed in the star loop: A→B and C→A
e_AB = f.edge_curve(v_A, v_B, f.line(p_A, f.vector(f.direction((-0.75, 0.433, 0.0)), 3.0)))
e_CA = f.edge_curve(v_C, v_A, f.line(p_C, f.vector(f.direction(( 0.75, 0.433, 0.0)), 3.0)))

# Star loop: center→A→B→center→C→A→center — visits center 3 times.
# Non-manifold: center vertex has 3-edge incidence (e_cA, e_cB, e_cC all touch it).
nm_loop = f.edge_loop([
    f.oriented_edge(e_cA, True),   # center → A      (e_cA: center→A, fwd)
    f.oriented_edge(e_AB, True),   # A → B            (e_AB: A→B, fwd)
    f.oriented_edge(e_cB, False),  # B → center       (e_cB: center→B, rev → B→center)
    f.oriented_edge(e_cC, True),   # center → C       (e_cC: center→C, fwd)
    f.oriented_edge(e_CA, True),   # C → A            (e_CA: C→A, fwd)
    f.oriented_edge(e_cA, False),  # A → center       (e_cA: center→A, rev → A→center)
])

# The above loop: center→A→B→center→C→A→center — VISITS CENTER 3 TIMES
# Non-manifold: center vertex has 3 distinct outgoing/incoming edge traversals

pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

nm_face = f.advanced_face([f.face_outer_bound(nm_loop)], plane)

# ── Companion face: valid flat rectangle at z=1 ───────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 1.0)); p1 = f.cartesian_point((1.0, 0.0, 1.0))
p2 = f.cartesian_point((1.0, 1.0, 1.0)); p3 = f.cartesian_point((0.0, 1.0, 1.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
comp_loop = f.edge_loop([f.oriented_edge(e0, True), f.oriented_edge(e1, True),
                          f.oriented_edge(e2, True), f.oriented_edge(e3, True)])
comp_plc  = f.axis2_placement_3d(p0, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
comp_face = f.advanced_face([f.face_outer_bound(comp_loop)], f.plane(comp_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([nm_face, comp_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa104.stp")
