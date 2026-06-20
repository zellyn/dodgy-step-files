"""Tfa110 — Single-edge circular wire orientation ambiguity.

Catalog claim: Face with a wire that is a single closed curve (circle).
FixOrientation's winding-direction test assumes polygonal vertex sequences and
has no well-defined inside/outside for a single-edge planar loop without
topological context.

Mechanism: MANIFOLD_SOLID_BREP with a cylindrical solid. The top cap is a
planar ADVANCED_FACE whose FACE_OUTER_BOUND carries a single closed CIRCLE
EDGE_CURVE (start==end vertex). BRepClass_FaceClassifier, when called from
ShapeFix_Face::FixOrientation, samples edge midpoints and vertices — for a
single circular edge all sample points lie ON the boundary curve, making
interior/exterior classification undefined. The defect face IS on the live
CLOSED_SHELL traversal path.

Geometry: Cylinder radius=3, height=5, axis along Z. The top circular cap at
z=5 is the defect face with a single circle edge (CIRCLE, radius 3, center
(0,0,5)). The bottom cap and cylindrical wall close the shell.

Byte assertions:
  - contains(b'CIRCLE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa110",
    defect=(
        "CLOSED_SHELL: top cap ADVANCED_FACE (z=5) bounded by single closed CIRCLE "
        "EDGE_CURVE (radius=3, start==end==v_seam_top); "
        "ShapeFix_Face::FixOrientation calls BRepClass_FaceClassifier on edge midpoints "
        "and vertices — all lie on the boundary circle so interior/exterior is undefined; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

R = 3.0
H = 5.0

# Seam vertices
pt_seam_bot = f.cartesian_point((R, 0.0, 0.0))
pt_seam_top = f.cartesian_point((R, 0.0, H))
v_seam_bot  = f.vertex_point(pt_seam_bot)
v_seam_top  = f.vertex_point(pt_seam_top)

# Seam edge (vertical line along cylinder)
seam_edge = f.edge_curve(v_seam_bot, v_seam_top,
    f.line(pt_seam_bot, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# Bottom circle: closed (start==end==v_seam_bot)
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc = f.axis2_placement_3d(bot_ctr, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
bot_circle_edge = f.edge_curve(v_seam_bot, v_seam_bot, f.circle(bot_plc, R))

# Top circle: closed (start==end==v_seam_top) — THE DEFECT EDGE
top_ctr = f.cartesian_point((0.0, 0.0, H))
top_plc = f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
top_circle_edge = f.edge_curve(v_seam_top, v_seam_top, f.circle(top_plc, R))

# Cylindrical surface
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# face[0]: cylindrical wall — seam .T., top_circle .T., seam .F., bot_circle .F.
cyl_loop = f.edge_loop([
    f.oriented_edge(seam_edge,       True),
    f.oriented_edge(top_circle_edge, True),
    f.oriented_edge(seam_edge,       False),
    f.oriented_edge(bot_circle_edge, False),
])
face_cyl = f.advanced_face([f.face_outer_bound(cyl_loop)], cyl_surf)

# face[1]: bottom cap (z=0) — single circle
bot_loop = f.edge_loop([f.oriented_edge(bot_circle_edge, True)])
bot_face = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(
    f.axis2_placement_3d(bot_ctr, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))))

# face[2]: top cap (z=H) — THE DEFECT: single closed circle, FixOrientation ambiguity
top_loop = f.edge_loop([f.oriented_edge(top_circle_edge, True)])
top_face = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(
    f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ──────────────────────────────────────────
closed_sh = f.closed_shell([face_cyl, bot_face, top_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa110.stp")
