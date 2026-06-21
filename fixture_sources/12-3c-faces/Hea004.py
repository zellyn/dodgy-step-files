"""Hea004 — Free-bound contour analysis filters EDGE_LOOPs with sub-precision wiggle vertices.

Catalog claim: An OPEN_SHELL where one free-bound EDGE_LOOP has many short
sub-segments along one side with intermediate VERTEX_POINTs wiggling by ±1e-7
(well below typical 1e-6 tolerance). A precision parameter controls which
contours are flagged for downstream healing: those whose defect magnitude
exceeds the precision (1e-7 wiggles only show up when precision < 1e-7).

Mechanism: 10×10 face on a PLANE. The bottom edge is decomposed into 10
short LINE segments (1.0 unit each). The 10 intermediate vertices oscillate
in Y by ±1e-7 (alternating sign). The remaining 3 sides (right, top, left)
are clean. Total: 13 ORIENTED_EDGEs in the outer EDGE_LOOP.

Tier-3 assertions:
  n_edges_total >= 13
  face[0].surface_type == "plane"
  n_vertices_total >= 24

Expected: occt=shape(1)/shape(1) gmsh=shape(27) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea004",
    defect=(
        "OPEN_SHELL with 10x10 face on PLANE; "
        "bottom edge decomposed into 10 sub-segments (1.0 each) with "
        "intermediate vertices wiggling +/-1e-7 in Y (sub-precision noise); "
        "13 total ORIENTED_EDGEs in outer EDGE_LOOP; "
        "ShapeAnalysis_FreeBoundsProperties::CheckContours filters by precision: "
        "wiggle only visible when precision < 1e-7; "
        "defect: sub-precision vertex noise on free-bound contour"
    ),
)

# ── Plane at origin ───────────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── 11 wiggle vertex coordinates along bottom ─────────────────────────────────
EPS = 1.0e-7
wig_coords = []
for i in range(11):
    x = float(i)
    if i == 0 or i == 10:
        y = 0.0
    elif i % 2 == 1:
        y = EPS
    else:
        y = -EPS
    wig_coords.append((x, y))

# Create cartesian points and vertices
wig_pts   = [f.cartesian_point((x, y, 0.0), name=f"w{i}")
             for i, (x, y) in enumerate(wig_coords)]
wig_verts = [f.vertex_point(p) for p in wig_pts]

# Other 2 corners
p_tr = f.cartesian_point((10.0, 10.0, 0.0))
p_tl = f.cartesian_point((0.0, 10.0, 0.0))
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

# ── 10 short wiggle edges along bottom ───────────────────────────────────────
wig_edges = []
for i in range(10):
    x0, y0 = wig_coords[i]
    x1, y1 = wig_coords[i+1]
    dx = x1 - x0
    dy = y1 - y0
    mag = _math.sqrt(dx*dx + dy*dy)
    if mag < 1e-30:
        mag = 1.0
    ln = f.line(wig_pts[i],
                f.vector(f.direction((dx/mag, dy/mag, 0.0)), 1.0))
    ec = f.edge_curve(wig_verts[i], wig_verts[i+1], ln, name=f"wig_{i+1}")
    wig_edges.append(ec)

# Right: wig_verts[10] -> v_tr
ec_right = f.edge_curve(wig_verts[10], v_tr,
                         f.line(wig_pts[10], f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)),
                         name="right")
# Top: v_tr -> v_tl
ec_top = f.edge_curve(v_tr, v_tl,
                       f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)),
                       name="top")
# Left: v_tl -> wig_verts[0]
ec_left = f.edge_curve(v_tl, wig_verts[0],
                        f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)),
                        name="left")

# ── EDGE_LOOP: 10 wiggle + right + top + left = 13 edges ─────────────────────
oe_list = [f.oriented_edge(ec, True) for ec in wig_edges]
oe_list.append(f.oriented_edge(ec_right, True))
oe_list.append(f.oriented_edge(ec_top, True))
oe_list.append(f.oriented_edge(ec_left, True))

loop = f.edge_loop(oe_list, name="wiggly_perimeter")
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="face_with_wiggle_bottom")

shell = f.open_shell([face], name="shell_with_wiggle_contour")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea004.stp")
