"""Gn110 — ShapeUpgrade_ConvertSurfaceToBezierBasis bezier-with-trim.

Catalog claim: BEZIER_SURFACE wrapped in RECTANGULAR_TRIMMED_SURFACE via
FACE_BOUND. Conversion logic treats as untrimmed (uses base knot vector
[4,4] on both directions, spans 0.0..1.0) and ignores trim loop
(0.25..0.75 square); produces wrong patches outside trim.

Fixture: A BEZIER_SURFACE (degree 3x3 flat patch 0..1 x 0..1) is the
underlying surface; a RECTANGULAR_TRIMMED_SURFACE clips it to [0.25,0.75]
in both UV. An ADVANCED_FACE uses the trimmed surface; the conversion
pipeline ignores the trim and operates on the full Bezier, producing
extraneous patches.

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn110",
    defect=(
        "BEZIER_SURFACE (degree 3x3, 4x4 control net, flat 10x10 patch) "
        "wrapped in RECTANGULAR_TRIMMED_SURFACE [2.5,7.5]x[2.5,7.5]; "
        "ConvertSurfaceToBezierBasis ignores trim, operates on full surface, "
        "producing patches outside the trim boundary; "
        "ADVANCED_FACE on the trimmed surface loads as shape(1)"
    ),
)

# 4x4 control points for a degree-3 Bezier surface (flat patch 0..10 x 0..10)
pts = []
for i in range(4):
    row = []
    for j in range(4):
        row.append(f.cartesian_point((float(i) * 10.0/3.0, float(j) * 10.0/3.0, 0.0)))
    pts.append(row)

def row_refs(i):
    return "(" + ",".join(f"#{pts[i][j].eid}" for j in range(4)) + ")"

cp_grid = "(" + ",".join(row_refs(i) for i in range(4)) + ")"

# BEZIER_SURFACE: degree 3 in both directions (complex entity)
# Knot vector for degree-3 Bezier: multiplicities (4,4) at [0,1]
bezier_surf = f._emit_raw(
    f"(\n"
    f"  BEZIER_SURFACE()\n"
    f"  BOUNDED_SURFACE()\n"
    f"  B_SPLINE_SURFACE(3,3,{cp_grid},.UNSPECIFIED.,.F.,.F.,.F.)\n"
    f"  B_SPLINE_SURFACE_WITH_KNOTS((4,4),(4,4),(0.0,10.0),(0.0,10.0),.UNSPECIFIED.)\n"
    f"  GEOMETRIC_REPRESENTATION_ITEM()\n"
    f"  REPRESENTATION_ITEM('bezier_base')\n"
    f"  SURFACE()\n"
    f")"
)

# RECTANGULAR_TRIMMED_SURFACE: trim to [2.5, 7.5] x [2.5, 7.5]
# DEFECT: ConvertSurfaceToBezierBasis ignores this trim and uses the full surface
trimmed = f.rectangular_trimmed_surface(
    bezier_surf, 2.5, 7.5, 2.5, 7.5,
    usense=True, vsense=True,
    name="trimmed_bezier"
)

# Build a simple rectangular face on the trimmed surface
# Vertices at the 4 corners of the trim: (2.5,2.5), (7.5,2.5), (7.5,7.5), (2.5,7.5)
p00 = f.cartesian_point(( 2.5,  2.5, 0.0))
p10 = f.cartesian_point(( 7.5,  2.5, 0.0))
p11 = f.cartesian_point(( 7.5,  7.5, 0.0))
p01 = f.cartesian_point(( 2.5,  7.5, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

d_bot = f.direction((1.0, 0.0, 0.0))
vec_bot = f.vector(d_bot, 5.0)
l_bot = f.line(p00, vec_bot)
e_bot = f.edge_curve(v00, v10, l_bot, name="e_bot")

d_rgt = f.direction((0.0, 1.0, 0.0))
vec_rgt = f.vector(d_rgt, 5.0)
l_rgt = f.line(p10, vec_rgt)
e_rgt = f.edge_curve(v10, v11, l_rgt, name="e_rgt")

d_top = f.direction((1.0, 0.0, 0.0))
vec_top = f.vector(d_top, 5.0)
l_top = f.line(p01, vec_top)
e_top = f.edge_curve(v01, v11, l_top, name="e_top")

d_lft = f.direction((0.0, 1.0, 0.0))
vec_lft = f.vector(d_lft, 5.0)
l_lft = f.line(p00, vec_lft)
e_lft = f.edge_curve(v00, v01, l_lft, name="e_lft")

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], trimmed)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
