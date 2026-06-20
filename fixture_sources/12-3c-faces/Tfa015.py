"""Tfa015 — DropSmallSolids / debris solids from booleans.

Catalog claim: Compound contains tiny / zero-volume sub-solids (Boolean
fragments, micron-scale residuals). Healer must detect by volume or
width-factor and drop or fuse with neighbor; respect a user "Merge Solids"
flag; preserve XCAF attribute mapping for kept solids.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs:
  face[0] — the defective TINY DEBRIS FACE on a PLANE:
    A micron-scale square face 1e-3 mm × 1e-3 mm at origin.
    Volume (if extruded) would be ~1e-9 mm³ — below DropSmallSolids
    threshold. The face represents a tiny debris fragment from a Boolean.
    brepcheck.valid == False because the tiny face is degenerate.
  face[1] — a valid 10×10 square PLANE face so OCC loads shape(1).

Tier-3 assertions:
  brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa015",
    defect=(
        "ADVANCED_FACE on PLANE: 1e-3 mm × 1e-3 mm square debris fragment at origin; "
        "represents micro-scale Boolean residual (V~1e-9 mm³ < DropSmallSolids threshold); "
        "brepcheck.valid == False on this tiny degenerate face; "
        "healer must detect by volume/width-factor and drop or fuse; "
        "defective face IS on live OPEN_SHELL traversal path; "
        "companion 10x10 face ensures shape(1)"
    ),
)

# ── DEBRIS FACE (face[0]): 1e-3 mm × 1e-3 mm square at origin ────────────────
# area = 1e-6 mm² — micron-scale Boolean fragment; volume of any derived
# solid would be << 1e-9 mm³ (below DropSmallSolids threshold)
s = 1.0e-3  # 1 micrometer side

db_p0 = f.cartesian_point((0.0, 0.0, 0.0))
db_p1 = f.cartesian_point((s,   0.0, 0.0))
db_p2 = f.cartesian_point((s,   s,   0.0))
db_p3 = f.cartesian_point((0.0, s,   0.0))

db_v0 = f.vertex_point(db_p0)
db_v1 = f.vertex_point(db_p1)
db_v2 = f.vertex_point(db_p2)
db_v3 = f.vertex_point(db_p3)

db_ec_b = f.edge_curve(db_v0, db_v1,
    f.line(db_p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), s)))
db_ec_r = f.edge_curve(db_v1, db_v2,
    f.line(db_p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), s)))
db_ec_t = f.edge_curve(db_v2, db_v3,
    f.line(db_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), s)))
db_ec_l = f.edge_curve(db_v3, db_v0,
    f.line(db_p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), s)))

db_loop = f.edge_loop([
    f.oriented_edge(db_ec_b, True),
    f.oriented_edge(db_ec_r, True),
    f.oriented_edge(db_ec_t, True),
    f.oriented_edge(db_ec_l, True),
])

db_orig  = f.cartesian_point((0.0, 0.0, 0.0))
db_zdir  = f.direction((0.0, 0.0, 1.0))
db_xdir  = f.direction((1.0, 0.0, 0.0))
db_plc   = f.axis2_placement_3d(db_orig, db_zdir, db_xdir)
db_plane = f.plane(db_plc)

db_fob  = f.face_outer_bound(db_loop)
# Debris face: degenerate tiny face at sub-micron scale
debris_face = f.advanced_face([db_fob], db_plane)

# ── GOOD face (face[1]): valid 10×10 square at (1,0,0)–(11,10,0) ────────────
g_p0 = f.cartesian_point((1.0,  0.0,  0.0))
g_p1 = f.cartesian_point((11.0, 0.0,  0.0))
g_p2 = f.cartesian_point((11.0, 10.0, 0.0))
g_p3 = f.cartesian_point((1.0,  10.0, 0.0))
g_v0 = f.vertex_point(g_p0)
g_v1 = f.vertex_point(g_p1)
g_v2 = f.vertex_point(g_p2)
g_v3 = f.vertex_point(g_p3)

g_ec_b = f.edge_curve(g_v0, g_v1, f.line(g_p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
g_ec_r = f.edge_curve(g_v1, g_v2, f.line(g_p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
g_ec_t = f.edge_curve(g_v2, g_v3, f.line(g_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
g_ec_l = f.edge_curve(g_v3, g_v0, f.line(g_p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

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
shell = f.open_shell([debris_face, g_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa015.stp")
