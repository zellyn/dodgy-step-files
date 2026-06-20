"""Tfa014 — Small ADVANCED_FACE below area threshold (FixFaceSize).

Catalog claim: An ADVANCED_FACE whose total area is below a user-configured
small-face threshold but is not strictly a spot/strip/pin/sliver. Typical
shape: a square face on a PLANE of size 0.05 × 0.05 mm (≈2.5e-3 mm²); small
enough for downstream meshers/healers to drop.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs:
  face[0] — the defective TINY FACE on a PLANE: a 0.05 × 0.05 mm square
    at origin (area = 2.5e-3 mm² < 0.01). Not a spot face (area > 1e-9) and
    not a strip face (aspect ratio = 1). A below-threshold "fingernail" face.
  face[1] — a valid 1×1 square PLANE face so OCC loads shape(1).

Tier-3 assertions:
  face[0].area < 0.01
  face[0].surface_type == "plane"
  n_edges_total >= 4

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa014",
    defect=(
        "ADVANCED_FACE on PLANE: 0.05mm × 0.05mm square at origin; "
        "area = 2.5e-3 mm² < 0.01 (below FixFaceSize threshold); "
        "aspect ratio = 1.0 (square, not a strip/sliver/spot); "
        "a fingernail-sized residual face from boolean fragment; "
        "ShapeFix must eliminate the face and merge surrounding wires onto neighbors; "
        "defective face IS on live OPEN_SHELL traversal path; "
        "companion 1x1 face ensures shape(1)"
    ),
)

# ── TINY FACE (face[0]): 0.05mm × 0.05mm square at origin ────────────────────
# area = 0.05 * 0.05 = 0.0025 mm² < 0.01 ✓
# aspect_ratio = 0.05 / 0.05 = 1.0 (not a strip/sliver)
tiny_s = 0.05  # 0.05 mm side length

tn_p0 = f.cartesian_point((0.0,   0.0,   0.0))
tn_p1 = f.cartesian_point((tiny_s, 0.0,   0.0))
tn_p2 = f.cartesian_point((tiny_s, tiny_s, 0.0))
tn_p3 = f.cartesian_point((0.0,   tiny_s, 0.0))

tn_v0 = f.vertex_point(tn_p0)
tn_v1 = f.vertex_point(tn_p1)
tn_v2 = f.vertex_point(tn_p2)
tn_v3 = f.vertex_point(tn_p3)

tn_ec_b = f.edge_curve(tn_v0, tn_v1,
    f.line(tn_p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), tiny_s)))
tn_ec_r = f.edge_curve(tn_v1, tn_v2,
    f.line(tn_p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), tiny_s)))
tn_ec_t = f.edge_curve(tn_v2, tn_v3,
    f.line(tn_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), tiny_s)))
tn_ec_l = f.edge_curve(tn_v3, tn_v0,
    f.line(tn_p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), tiny_s)))

tn_loop = f.edge_loop([
    f.oriented_edge(tn_ec_b, True),
    f.oriented_edge(tn_ec_r, True),
    f.oriented_edge(tn_ec_t, True),
    f.oriented_edge(tn_ec_l, True),
])

tn_orig  = f.cartesian_point((0.0, 0.0, 0.0))
tn_zdir  = f.direction((0.0, 0.0, 1.0))
tn_xdir  = f.direction((1.0, 0.0, 0.0))
tn_plc   = f.axis2_placement_3d(tn_orig, tn_zdir, tn_xdir)
tn_plane = f.plane(tn_plc)

tn_fob  = f.face_outer_bound(tn_loop)
tn_face = f.advanced_face([tn_fob], tn_plane)

# ── GOOD face (face[1]): valid 1×1 square at (1,0,0)–(2,1,0) on XY plane ─────
g_p0 = f.cartesian_point((1.0, 0.0, 0.0))
g_p1 = f.cartesian_point((2.0, 0.0, 0.0))
g_p2 = f.cartesian_point((2.0, 1.0, 0.0))
g_p3 = f.cartesian_point((1.0, 1.0, 0.0))
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

g_orig  = f.cartesian_point((1.0, 0.0, 0.0))
g_zdir  = f.direction((0.0, 0.0, 1.0))
g_xdir  = f.direction((1.0, 0.0, 0.0))
g_plc   = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
g_plane = f.plane(g_plc)

g_fob  = f.face_outer_bound(g_loop)
g_face = f.advanced_face([g_fob], g_plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([tn_face, g_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa014.stp")
