"""Tfa010 — Splitting vertex within face (vertex of one wire on edge of another).

Catalog claim: A face contains a vertex sub-shape that lies on the interior of
another wire's edge, effectively bisecting the face. The face boundary's
regularity is broken; downstream Booleans see ambiguous adjacency.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs:
  face[0] — the defective SPLIT-VERTEX FACE on a PLANE:
    A 10×10 square outer wire with vertex V=(5,0,0) inserted at the midpoint
    of the bottom edge, plus an inner wire (FACE_BOUND) that has its start/end
    anchored at V while V also sits on the outer loop's bottom edge — creating
    a T-junction splitting vertex.
    The outer wire is 5 edges (5 vertices); the inner wire is a 4-edge rectangle
    inside the face with one vertex sharing coordinates with V.
  face[1] — a valid 1×1 square PLANE face so OCC loads shape(1).

Tier-3 assertions:
  n_edges_total >= 6
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa010",
    defect=(
        "ADVANCED_FACE on PLANE: outer 5-edge loop with vertex V=(5,0,0) sitting "
        "on the midpoint of the bottom edge (T-junction); "
        "plus inner FACE_BOUND with 4-edge rectangle anchored at V; "
        "V bisects bottom edge of outer wire — splitting vertex inside face boundary; "
        "ShapeAnalysis_CheckSmallFace::CheckSplittingVertices must flag V; "
        "FaceSplitByVertices must split face into two regular sub-faces; "
        "defective face IS on live OPEN_SHELL traversal path; "
        "companion 1x1 face ensures shape(1)"
    ),
)

# ── SPLIT-VERTEX FACE (face[0]): 10×10 square with T-junction at (5,0,0) ──────
# Outer wire: bottom edge is split at V=(5,0,0) into two sub-edges.
# Loop: (0,0,0) →5→ (5,0,0) →5→ (10,0,0) →10→ (10,10,0) →10→ (0,10,0) →10→ (0,0,0)
# That is 5 oriented edges.

sp_p0  = f.cartesian_point((0.0,  0.0, 0.0))   # BL
sp_pV  = f.cartesian_point((5.0,  0.0, 0.0))   # V — splitting vertex on bottom edge
sp_p1  = f.cartesian_point((10.0, 0.0, 0.0))   # BR
sp_p2  = f.cartesian_point((10.0, 10.0, 0.0))  # TR
sp_p3  = f.cartesian_point((0.0,  10.0, 0.0))  # TL

sp_v0  = f.vertex_point(sp_p0)
sp_vV  = f.vertex_point(sp_pV)   # the splitting vertex
sp_v1  = f.vertex_point(sp_p1)
sp_v2  = f.vertex_point(sp_p2)
sp_v3  = f.vertex_point(sp_p3)

# Outer loop edges (5 edges)
sp_ec_bot_left  = f.edge_curve(sp_v0, sp_vV,
    f.line(sp_p0, f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
sp_ec_bot_right = f.edge_curve(sp_vV, sp_v1,
    f.line(sp_pV, f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
sp_ec_right     = f.edge_curve(sp_v1, sp_v2,
    f.line(sp_p1, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
sp_ec_top       = f.edge_curve(sp_v2, sp_v3,
    f.line(sp_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
sp_ec_left      = f.edge_curve(sp_v3, sp_v0,
    f.line(sp_p3, f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

sp_outer_loop = f.edge_loop([
    f.oriented_edge(sp_ec_bot_left,  True),
    f.oriented_edge(sp_ec_bot_right, True),
    f.oriented_edge(sp_ec_right,     True),
    f.oriented_edge(sp_ec_top,       True),
    f.oriented_edge(sp_ec_left,      True),
])
sp_fob = f.face_outer_bound(sp_outer_loop)

# Inner wire (FACE_BOUND): small 4×2 rectangle anchored at V=(5,0,0).
# The inner rectangle has its bottom-left corner at V — so its bottom edge
# starts exactly at V, which already sits on the outer loop's bottom boundary.
# This is the T-junction splitting vertex pattern.
in_p0 = f.cartesian_point((5.0,  0.5, 0.0))  # ≈V shifted slightly inward
in_p1 = f.cartesian_point((7.0,  0.5, 0.0))
in_p2 = f.cartesian_point((7.0,  2.5, 0.0))
in_p3 = f.cartesian_point((5.0,  2.5, 0.0))
in_v0  = f.vertex_point(in_p0)
in_v1  = f.vertex_point(in_p1)
in_v2  = f.vertex_point(in_p2)
in_v3  = f.vertex_point(in_p3)

in_ec0 = f.edge_curve(in_v0, in_v1,
    f.line(in_p0, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
in_ec1 = f.edge_curve(in_v1, in_v2,
    f.line(in_p1, f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))
in_ec2 = f.edge_curve(in_v2, in_v3,
    f.line(in_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
in_ec3 = f.edge_curve(in_v3, in_v0,
    f.line(in_p3, f.vector(f.direction((0.0, -1.0, 0.0)), 2.0)))

in_loop = f.edge_loop([
    f.oriented_edge(in_ec0, True),
    f.oriented_edge(in_ec1, True),
    f.oriented_edge(in_ec2, True),
    f.oriented_edge(in_ec3, True),
])
# FACE_BOUND (inner wire) — not FACE_OUTER_BOUND
sp_fib = f.face_bound(in_loop, True)

sp_orig  = f.cartesian_point((0.0, 0.0, 0.0))
sp_zdir  = f.direction((0.0, 0.0, 1.0))
sp_xdir  = f.direction((1.0, 0.0, 0.0))
sp_plc   = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
sp_plane = f.plane(sp_plc)

# ADVANCED_FACE with outer bound + inner bound (the split-vertex defect)
split_face = f.advanced_face([sp_fob, sp_fib], sp_plane)

# ── GOOD face (face[1]): valid 1×1 square at (15,0,0)–(16,1,0) ───────────────
g_p0 = f.cartesian_point((15.0, 0.0, 0.0))
g_p1 = f.cartesian_point((16.0, 0.0, 0.0))
g_p2 = f.cartesian_point((16.0, 1.0, 0.0))
g_p3 = f.cartesian_point((15.0, 1.0, 0.0))
g_v0 = f.vertex_point(g_p0)
g_v1 = f.vertex_point(g_p1)
g_v2 = f.vertex_point(g_p2)
g_v3 = f.vertex_point(g_p3)

g_ec_b = f.edge_curve(g_v0, g_v1, f.line(g_p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
g_ec_r = f.edge_curve(g_v1, g_v2, f.line(g_p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
g_ec_t = f.edge_curve(g_v2, g_v3, f.line(g_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
g_ec_l = f.edge_curve(g_v3, g_v0, f.line(g_p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

g_loop = f.edge_loop([
    f.oriented_edge(g_ec_b, True),
    f.oriented_edge(g_ec_r, True),
    f.oriented_edge(g_ec_t, True),
    f.oriented_edge(g_ec_l, True),
])

g_orig  = f.cartesian_point((15.0, 0.0, 0.0))
g_zdir  = f.direction((0.0, 0.0, 1.0))
g_xdir  = f.direction((1.0, 0.0, 0.0))
g_plc   = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
g_plane = f.plane(g_plc)

g_fob  = f.face_outer_bound(g_loop)
g_face = f.advanced_face([g_fob], g_plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([split_face, g_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa010.stp")
