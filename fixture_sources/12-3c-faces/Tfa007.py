"""Tfa007 — Strip face: face one-dimensional within tolerance.

Catalog claim: A face whose UV bounds collapse one parametric direction to
within tolerance. The face is geometrically a thin strip; perpendicular
distance between its two long boundary edges < tolerance.

Mechanism: SHELL_BASED_SURFACE_MODEL containing TWO ADVANCED_FACEs:
  face[0] — the defective STRIP FACE on a PLANE: 4-edge outer wire with two
    100mm long parallel edges separated by only 1e-7 mm and two 1e-7 mm
    connecting short edges. The strip's aspect ratio > 1e3 (100 / 1e-7 = 1e9).
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
    catalog_id="Tfa007",
    defect=(
        "ADVANCED_FACE on PLANE: strip face with two 100mm long parallel edges "
        "separated by 1e-7 mm and two 1e-7 mm connecting short edges; "
        "face width < Precision::Confusion (1e-7 mm); aspect ratio ~1e9 >> 1e3; "
        "FixStripFace must collapse to tolerant_edge and merge incident shells; "
        "defective face IS on live OPEN_SHELL traversal path; "
        "companion valid face gives shape(1) result"
    ),
)

# ── STRIP FACE (face[0]): 100mm × 1e-7mm strip on XY plane ───────────────────
# Reproducer recipe from catalog:
# Two long parallel edges of length 100mm separated by 1e-7 mm
# Two short connecting edges of 1e-7 mm
strip_len  = 100.0    # long dimension in mm
strip_wid  = 1.0e-7   # width: < Precision::Confusion (default 1e-7 mm)
# aspect ratio = strip_len / strip_wid = 100 / 1e-7 = 1e9 >> 1e3 ✓

# Bottom-left origin, strip along +X, width along +Y
st_p0 = f.cartesian_point((0.0,       0.0,      0.0))   # BL
st_p1 = f.cartesian_point((strip_len, 0.0,      0.0))   # BR
st_p2 = f.cartesian_point((strip_len, strip_wid, 0.0))  # TR
st_p3 = f.cartesian_point((0.0,       strip_wid, 0.0))  # TL

st_v0 = f.vertex_point(st_p0)
st_v1 = f.vertex_point(st_p1)
st_v2 = f.vertex_point(st_p2)
st_v3 = f.vertex_point(st_p3)

# Bottom long edge (100mm)
st_ec_b = f.edge_curve(st_v0, st_v1,
    f.line(st_p0, f.vector(f.direction((1.0, 0.0, 0.0)), strip_len)))
# Right short edge (1e-7 mm)
st_ec_r = f.edge_curve(st_v1, st_v2,
    f.line(st_p1, f.vector(f.direction((0.0, 1.0, 0.0)), strip_wid)))
# Top long edge (100mm, reversed)
st_ec_t = f.edge_curve(st_v2, st_v3,
    f.line(st_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), strip_len)))
# Left short edge (1e-7 mm, reversed)
st_ec_l = f.edge_curve(st_v3, st_v0,
    f.line(st_p3, f.vector(f.direction((0.0, -1.0, 0.0)), strip_wid)))

st_loop = f.edge_loop([
    f.oriented_edge(st_ec_b, True),
    f.oriented_edge(st_ec_r, True),
    f.oriented_edge(st_ec_t, True),
    f.oriented_edge(st_ec_l, True),
])

st_orig = f.cartesian_point((0.0, 0.0, 0.0))
st_zdir = f.direction((0.0, 0.0, 1.0))
st_xdir = f.direction((1.0, 0.0, 0.0))
st_plc  = f.axis2_placement_3d(st_orig, st_zdir, st_xdir)
strip_plane = f.plane(st_plc)

strip_fob  = f.face_outer_bound(st_loop)
strip_face = f.advanced_face([strip_fob], strip_plane)

# ── GOOD face (face[1]): valid 1×1 square at (0,5)–(1,6) on XY plane ─────────
g_p0 = f.cartesian_point((0.0, 5.0, 0.0))
g_p1 = f.cartesian_point((1.0, 5.0, 0.0))
g_p2 = f.cartesian_point((1.0, 6.0, 0.0))
g_p3 = f.cartesian_point((0.0, 6.0, 0.0))
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

g_orig = f.cartesian_point((0.0, 5.0, 0.0))
g_zdir = f.direction((0.0, 0.0, 1.0))
g_xdir = f.direction((1.0, 0.0, 0.0))
g_plc  = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
good_plane = f.plane(g_plc)

good_fob  = f.face_outer_bound(g_loop)
good_face = f.advanced_face([good_fob], good_plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([strip_face, good_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa007.stp")
