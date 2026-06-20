"""Tfa012 — Face area zero / negative after fixshape.

Catalog claim: After healing, BRepGProp::SurfaceProperties returns zero or
negative area for a face. The face outer wire winds clockwise on the natural
surface orientation; healing may reverse the orientation and flip the signed-area
sign.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs:
  face[0] — the defective REVERSED-WINDING FACE on a PLANE:
    A 1×1 square at near-degenerate scale: outer wire wound CW (clockwise)
    relative to the face normal (+Z), so signed area is negative. The face is
    at near-zero scale (1e-7 × 1e-7) making the unsigned area also near-zero.
    sliver_aspect_max_min == 1 but area is ~1e-14 < 0.01.
  face[1] — a valid 1×1 square PLANE face so OCC loads shape(1).

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 4
  n_vertices_total >= 8
  face[0].sliver_aspect_max_min > 1e6

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa012",
    defect=(
        "ADVANCED_FACE on PLANE: outer wire wound clockwise relative to +Z normal; "
        "near-zero-scale square (1e-7 × 1e-7 mm) at origin — area ~1e-14; "
        "clockwise winding means signed area is negative; "
        "sliver_aspect_max_min == 1e7/1e-7 = 1 — but edges are near-zero length; "
        "actual tier-3: sliver_aspect_max_min > 1e6 from max/min edge ratio; "
        "ShapeFix must restore consistent winding; BRepGProp must return positive area; "
        "defective face IS on live OPEN_SHELL traversal path; "
        "companion 1x1 face ensures shape(1)"
    ),
)

# ── REVERSED-WINDING FACE (face[0]): CW winding on a near-degenerate plane ───
# A very thin rectangle: 100mm long × 1e-7mm wide (strip-like).
# Wire wound CW: BL→TL→TR→BR (reverse of CCW standard).
# This produces negative signed area while retaining non-zero unsigned area.
# sliver_aspect_max_min = 100 / 1e-7 = 1e9 > 1e6 ✓

rw_len = 100.0    # long dimension
rw_wid = 1.0e-7  # short dimension (below Precision::Confusion)

# Corners: BL, TL, TR, BR (for CW winding when +Z is normal)
rw_p0 = f.cartesian_point((0.0,    0.0,    0.0))   # BL
rw_p1 = f.cartesian_point((0.0,    rw_wid, 0.0))   # TL
rw_p2 = f.cartesian_point((rw_len, rw_wid, 0.0))   # TR
rw_p3 = f.cartesian_point((rw_len, 0.0,    0.0))   # BR

rw_v0 = f.vertex_point(rw_p0)
rw_v1 = f.vertex_point(rw_p1)
rw_v2 = f.vertex_point(rw_p2)
rw_v3 = f.vertex_point(rw_p3)

# CW winding: BL→TL→TR→BR→BL (clockwise when viewed from +Z)
rw_ec_0 = f.edge_curve(rw_v0, rw_v1,
    f.line(rw_p0, f.vector(f.direction((0.0, 1.0, 0.0)), rw_wid)))   # left edge up
rw_ec_1 = f.edge_curve(rw_v1, rw_v2,
    f.line(rw_p1, f.vector(f.direction((1.0, 0.0, 0.0)), rw_len)))   # top edge right
rw_ec_2 = f.edge_curve(rw_v2, rw_v3,
    f.line(rw_p2, f.vector(f.direction((0.0, -1.0, 0.0)), rw_wid)))  # right edge down
rw_ec_3 = f.edge_curve(rw_v3, rw_v0,
    f.line(rw_p3, f.vector(f.direction((-1.0, 0.0, 0.0)), rw_len)))  # bottom edge left

rw_loop = f.edge_loop([
    f.oriented_edge(rw_ec_0, True),
    f.oriented_edge(rw_ec_1, True),
    f.oriented_edge(rw_ec_2, True),
    f.oriented_edge(rw_ec_3, True),
])

rw_orig  = f.cartesian_point((0.0, 0.0, 0.0))
rw_zdir  = f.direction((0.0, 0.0, 1.0))
rw_xdir  = f.direction((1.0, 0.0, 0.0))
rw_plc   = f.axis2_placement_3d(rw_orig, rw_zdir, rw_xdir)
rw_plane = f.plane(rw_plc)

# same_sense=False: the face orientation is OPPOSITE to the surface normal,
# combined with the CW winding this gives negative signed area.
rw_fob  = f.face_outer_bound(rw_loop)
rw_face = f.advanced_face([rw_fob], rw_plane, same_sense=False)

# ── GOOD face (face[1]): valid 1×1 square at (0,5,0)–(1,6,0) on XY plane ─────
g_p0 = f.cartesian_point((0.0, 5.0, 0.0))
g_p1 = f.cartesian_point((1.0, 5.0, 0.0))
g_p2 = f.cartesian_point((1.0, 6.0, 0.0))
g_p3 = f.cartesian_point((0.0, 6.0, 0.0))
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

g_orig  = f.cartesian_point((0.0, 5.0, 0.0))
g_zdir  = f.direction((0.0, 0.0, 1.0))
g_xdir  = f.direction((1.0, 0.0, 0.0))
g_plc   = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
g_plane = f.plane(g_plc)

g_fob  = f.face_outer_bound(g_loop)
g_face = f.advanced_face([g_fob], g_plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([rw_face, g_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa012.stp")
