"""Tfa006 — Spot face: face collapsed to a point.

Catalog claim: A face whose entire boundary lies within Precision::Confusion of
a single point. All vertex coordinates are equal within tolerance; surface
evaluation degenerates.

Mechanism: SHELL_BASED_SURFACE_MODEL containing TWO ADVANCED_FACEs:
  face[0] — the defective SPOT FACE on a PLANE: 4-edge outer wire whose
    vertices are at (0,0,0), (1e-9,0,0), (1e-9,1e-9,0), (0,1e-9,0).
    All coordinates differ by less than Precision::Confusion (1e-7 mm default).
    The face area is ~ (1e-9)^2 = 1e-18 which is < 1e-9 (tier-3 assertion).
  face[1] — a valid 1×1 square PLANE face so OCC loads shape(1).

Tier-3 assertions:
  face[0].area < 1e-9
  face[0].surface_type == "plane"
  n_edges_total >= 4

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa006",
    defect=(
        "ADVANCED_FACE on PLANE: outer wire 4-edge loop with vertices at "
        "(0,0,0), (1e-9,0,0), (1e-9,1e-9,0), (0,1e-9,0); "
        "all vertices within 1e-7 of origin (Precision::Confusion); "
        "face area ~1e-18 < 1e-9; "
        "FixSpotFace must collapse to tolerant_vertex and remove from shell; "
        "defective face IS on live OPEN_SHELL traversal path; "
        "companion valid face gives shape(1) result"
    ),
)

# ── SPOT FACE (face[0]): 4-edge loop all within 1e-9 of origin ───────────────
# Reproducer recipe from catalog:
# vertices at (0,0,0), (1e-9,0,0), (1e-9,1e-9,0), (0,1e-9,0)
sp_p0 = f.cartesian_point((0.0,    0.0,    0.0))
sp_p1 = f.cartesian_point((1.0e-9, 0.0,    0.0))
sp_p2 = f.cartesian_point((1.0e-9, 1.0e-9, 0.0))
sp_p3 = f.cartesian_point((0.0,    1.0e-9, 0.0))

sp_v0 = f.vertex_point(sp_p0)
sp_v1 = f.vertex_point(sp_p1)
sp_v2 = f.vertex_point(sp_p2)
sp_v3 = f.vertex_point(sp_p3)

# 4 edges: bottom, right, top, left
def mini_edge(pa, pb, va, vb, dx, dy, dz, length):
    d   = f.direction((dx, dy, dz))
    vec = f.vector(d, length)
    ln  = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

tiny = 1.0e-9
sp_ec_b = mini_edge(sp_p0, sp_p1, sp_v0, sp_v1,  1.0, 0.0, 0.0, tiny)
sp_ec_r = mini_edge(sp_p1, sp_p2, sp_v1, sp_v2,  0.0, 1.0, 0.0, tiny)
sp_ec_t = mini_edge(sp_p2, sp_p3, sp_v2, sp_v3, -1.0, 0.0, 0.0, tiny)
sp_ec_l = mini_edge(sp_p3, sp_p0, sp_v3, sp_v0,  0.0,-1.0, 0.0, tiny)

sp_loop = f.edge_loop([
    f.oriented_edge(sp_ec_b, True),
    f.oriented_edge(sp_ec_r, True),
    f.oriented_edge(sp_ec_t, True),
    f.oriented_edge(sp_ec_l, True),
])

sp_orig = f.cartesian_point((0.0, 0.0, 0.0))
sp_zdir = f.direction((0.0, 0.0, 1.0))
sp_xdir = f.direction((1.0, 0.0, 0.0))
sp_plc  = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
spot_plane = f.plane(sp_plc)
# RECTANGULAR_TRIMMED_SURFACE bounds the carrier-plane parametric domain so
# BRepGProp can compute the spot face's tiny area; without it, OCC silently
# collapses the sub-tolerance EDGE_LOOP onto the carrier's natural unbounded
# UV domain and BRepGProp reports area ≈ 8e+100. The test
# tests/test_validator_self.py::test_tier3_tfa006_spot_face_realistic_area
# locks this in. Window slightly larger than the spot box ([-1,2]² covers
# the sub-tolerance wire at origin with room for the wire's tolerance ball).
spot_surf = f.rectangular_trimmed_surface(spot_plane, 0.0, 2.0E-9, 0.0, 2.0E-9,
                                          usense=True, vsense=True)

spot_fob  = f.face_outer_bound(sp_loop)
spot_face = f.advanced_face([spot_fob], spot_surf)

# ── GOOD face (face[1]): valid 1×1 square at (5,0)–(6,1) on XY plane ─────────
g_p0 = f.cartesian_point((5.0, 0.0, 0.0))
g_p1 = f.cartesian_point((6.0, 0.0, 0.0))
g_p2 = f.cartesian_point((6.0, 1.0, 0.0))
g_p3 = f.cartesian_point((5.0, 1.0, 0.0))
g_v0 = f.vertex_point(g_p0)
g_v1 = f.vertex_point(g_p1)
g_v2 = f.vertex_point(g_p2)
g_v3 = f.vertex_point(g_p3)

g_ec_b = f.edge_curve(g_v0, g_v1, f.line(g_p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
g_ec_r = f.edge_curve(g_v1, g_v2, f.line(g_p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
g_ec_t = f.edge_curve(g_v2, g_v3, f.line(g_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
g_ec_l = f.edge_curve(g_v3, g_v0, f.line(g_p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

g_loop = f.edge_loop([
    f.oriented_edge(g_ec_b, True),
    f.oriented_edge(g_ec_r, True),
    f.oriented_edge(g_ec_t, True),
    f.oriented_edge(g_ec_l, True),
])
g_orig = f.cartesian_point((5.0, 0.0, 0.0))
g_zdir = f.direction((0.0, 0.0, 1.0))
g_xdir = f.direction((1.0, 0.0, 0.0))
g_plc  = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
good_plane = f.plane(g_plc)

good_fob  = f.face_outer_bound(g_loop)
good_face = f.advanced_face([good_fob], good_plane)

# ── Wire spot face first into OPEN_SHELL so tier3's face[0] is the spot face ─
# (locking down test_tier3_tfa006_spot_face_realistic_area which asserts
#  faces[0].area < 1e-9). good_face is wired but emitted later in the shell
#  list — OCC visits the spot face first via TopExp_Explorer.
shell = f.open_shell([spot_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa006.stp")
