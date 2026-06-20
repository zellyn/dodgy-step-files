"""Tfa013 — Face area exceeds limit (needs split).

Catalog claim: One face dominates the model's area budget (e.g., a single huge
skin face on a long thin part). Downstream meshers produce uneven element sizes;
analyses degrade.

Mechanism: OPEN_SHELL with ONE huge ADVANCED_FACE on a PLANE:
  face[0] — a 1000mm × 2000mm PLANE face (area = 2,000,000 mm² > 1e6 mm²).
    This single face covers 90%+ of a typical model's surface area budget.
    ShapeUpgrade_ShapeDivideArea must subdivide it along iso-curves.

Tier-3 assertions:
  face[0].area > 1e6
  face[0].surface_type == "plane"
  n_edges_total >= 4

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa013",
    defect=(
        "ADVANCED_FACE on PLANE: 1000mm × 2000mm rectangle; "
        "area = 2,000,000 mm² >> 1e6 mm² tier-3 threshold; "
        "single face dominates the model's total surface area; "
        "ShapeUpgrade_ShapeDivideArea must subdivide along iso-curves; "
        "downstream meshers produce uneven element size distribution; "
        "defective face IS on live OPEN_SHELL traversal path"
    ),
)

# ── HUGE FACE (face[0]): 1000mm × 2000mm rectangle on XY plane ───────────────
# area = 1000 * 2000 = 2,000,000 mm² >> 1e6 ✓
huge_w = 1000.0   # mm wide
huge_h = 2000.0   # mm tall

hg_p0 = f.cartesian_point((0.0,   0.0,   0.0))
hg_p1 = f.cartesian_point((huge_w, 0.0,   0.0))
hg_p2 = f.cartesian_point((huge_w, huge_h, 0.0))
hg_p3 = f.cartesian_point((0.0,   huge_h, 0.0))

hg_v0 = f.vertex_point(hg_p0)
hg_v1 = f.vertex_point(hg_p1)
hg_v2 = f.vertex_point(hg_p2)
hg_v3 = f.vertex_point(hg_p3)

hg_ec_b = f.edge_curve(hg_v0, hg_v1,
    f.line(hg_p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), huge_w)))
hg_ec_r = f.edge_curve(hg_v1, hg_v2,
    f.line(hg_p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), huge_h)))
hg_ec_t = f.edge_curve(hg_v2, hg_v3,
    f.line(hg_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), huge_w)))
hg_ec_l = f.edge_curve(hg_v3, hg_v0,
    f.line(hg_p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), huge_h)))

hg_loop = f.edge_loop([
    f.oriented_edge(hg_ec_b, True),
    f.oriented_edge(hg_ec_r, True),
    f.oriented_edge(hg_ec_t, True),
    f.oriented_edge(hg_ec_l, True),
])

hg_orig  = f.cartesian_point((0.0, 0.0, 0.0))
hg_zdir  = f.direction((0.0, 0.0, 1.0))
hg_xdir  = f.direction((1.0, 0.0, 0.0))
hg_plc   = f.axis2_placement_3d(hg_orig, hg_zdir, hg_xdir)
hg_plane = f.plane(hg_plc)

hg_fob  = f.face_outer_bound(hg_loop)
hg_face = f.advanced_face([hg_fob], hg_plane)

# ── Wire into OPEN_SHELL → SBSM → product chain ───────────────────────────────
shell = f.open_shell([hg_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa013.stp")
