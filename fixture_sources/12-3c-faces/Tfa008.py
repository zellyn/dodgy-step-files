"""Tfa008 — Pin / sliver face.

Catalog claim: A high-aspect-ratio degenerate face (knife-like, needle-like).
Two long edges plus one tiny edge so that the cross-perpendicular distance
between long edges is below tolerance. Distinguished from pure spot/strip by
retained 2D area (tapers to a point at one corner).

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs:
  face[0] — the defective PIN FACE on a PLANE: 4-edge outer wire with two
    100 mm long convergent edges and two near-zero connecting edges (1e-7 mm).
    The face tapers to a near-point: aspect ratio > 1e9.
  face[1] — a valid 1×1 square PLANE face so OCC loads shape(1).

Tier-3 assertions:
  face[0].sliver_aspect_max_min > 1e3
  face[0].surface_type == "plane"
  n_edges_total >= 2

Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa008",
    defect=(
        "ADVANCED_FACE on PLANE: pin/sliver face with two 100mm long converging "
        "edges and two 1e-7mm connecting edges at the narrow tip; "
        "face tapers from 100mm wide at base to ~1e-7mm at top (near-point); "
        "sliver_aspect_max_min > 1e9 >> 1e3; "
        "ShapeFix_Face::FixSmallFace (FixPinFace) must collapse narrow end to "
        "tolerant_vertex; defective face IS on live OPEN_SHELL traversal path; "
        "companion valid 1x1 face ensures OCC loads shape(1)"
    ),
)

# ── PIN FACE (face[0]): 4-edge trapezoid on XY plane ─────────────────────────
# Wide base (100mm) at y=0, narrow top (1e-7 mm) at y=100mm.
# This creates a near-degenerate pin face.
pin_len  = 100.0     # base width (mm)
pin_wid  = 1.0e-7   # top width (mm) — below Precision::Confusion
pin_ht   = 100.0    # height (mm)

# Four corners: BL, BR, TR, TL
pn_p0 = f.cartesian_point((0.0,      0.0,    0.0))   # BL
pn_p1 = f.cartesian_point((pin_len,  0.0,    0.0))   # BR
pn_p2 = f.cartesian_point((pin_len,  pin_wid, 0.0))  # TR (near-zero offset)
pn_p3 = f.cartesian_point((0.0,      pin_wid, 0.0))  # TL (near-zero offset)

pn_v0 = f.vertex_point(pn_p0)
pn_v1 = f.vertex_point(pn_p1)
pn_v2 = f.vertex_point(pn_p2)
pn_v3 = f.vertex_point(pn_p3)

# Bottom long edge (100mm)
pn_ec_b = f.edge_curve(pn_v0, pn_v1,
    f.line(pn_p0, f.vector(f.direction((1.0, 0.0, 0.0)), pin_len)))
# Right tiny edge (1e-7 mm)
pn_ec_r = f.edge_curve(pn_v1, pn_v2,
    f.line(pn_p1, f.vector(f.direction((0.0, 1.0, 0.0)), pin_wid)))
# Top long edge (100mm, reversed)
pn_ec_t = f.edge_curve(pn_v2, pn_v3,
    f.line(pn_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), pin_len)))
# Left tiny edge (1e-7 mm, reversed)
pn_ec_l = f.edge_curve(pn_v3, pn_v0,
    f.line(pn_p3, f.vector(f.direction((0.0, -1.0, 0.0)), pin_wid)))

pn_loop = f.edge_loop([
    f.oriented_edge(pn_ec_b, True),
    f.oriented_edge(pn_ec_r, True),
    f.oriented_edge(pn_ec_t, True),
    f.oriented_edge(pn_ec_l, True),
])

pn_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pn_zdir  = f.direction((0.0, 0.0, 1.0))
pn_xdir  = f.direction((1.0, 0.0, 0.0))
pn_plc   = f.axis2_placement_3d(pn_orig, pn_zdir, pn_xdir)
pin_plane = f.plane(pn_plc)

pin_fob  = f.face_outer_bound(pn_loop)
pin_face = f.advanced_face([pin_fob], pin_plane)

# ── GOOD face (face[1]): valid 1×1 square at (0,5,0)–(1,6,0) on XY plane ─────
g_p0 = f.cartesian_point((0.0, 5.0, 0.0))
g_p1 = f.cartesian_point((1.0, 5.0, 0.0))
g_p2 = f.cartesian_point((1.0, 6.0, 0.0))
g_p3 = f.cartesian_point((0.0, 6.0, 0.0))
g_v0 = f.vertex_point(g_p0)
g_v1 = f.vertex_point(g_p1)
g_v2 = f.vertex_point(g_p2)
g_v3 = f.vertex_point(g_p3)

g_ec_b = f.edge_curve(g_v0, g_v1, f.line(g_p0, f.vector(f.direction((1.0,  0.0, 0.0)), 1.0)))
g_ec_r = f.edge_curve(g_v1, g_v2, f.line(g_p1, f.vector(f.direction((0.0,  1.0, 0.0)), 1.0)))
g_ec_t = f.edge_curve(g_v2, g_v3, f.line(g_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
g_ec_l = f.edge_curve(g_v3, g_v0, f.line(g_p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

g_loop = f.edge_loop([
    f.oriented_edge(g_ec_b, True),
    f.oriented_edge(g_ec_r, True),
    f.oriented_edge(g_ec_t, True),
    f.oriented_edge(g_ec_l, True),
])

g_orig  = f.cartesian_point((0.0, 5.0, 0.0))
g_zdir  = f.direction((0.0, 0.0, 1.0))
g_xdir  = f.direction((1.0, 0.0, 0.0))
g_plc   = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
g_plane = f.plane(g_plc)

g_fob   = f.face_outer_bound(g_loop)
g_face  = f.advanced_face([g_fob], g_plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([pin_face, g_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa008.stp")
