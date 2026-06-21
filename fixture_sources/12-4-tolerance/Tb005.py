"""Tb005 — Face area sub-tolerance squared (tol*tol threshold defect).

Catalog claim: A planar face with side length 3e-4 mm has area 9e-8 mm².
The file declares tol = 1e-4; a kernel filtering with area < tol*tol = 1e-8
keeps it. If tolerance is bumped to 1e-3, threshold becomes 1e-6, and the
face is silently dropped.

Fixture: A 3e-4 × 3e-4 mm square ADVANCED_FACE on a PLANE, wrapped in a
PRODUCT chain. Declared UNCERTAINTY_MEASURE_WITH_UNIT is 1.0E-4.
Face area = 9e-8 < 1e-6 = (1e-3)^2, but > 1e-8 = (1e-4)^2.

Tier-3: face[0].area < 1e-6, face[0].surface_type == "plane", n_edges_total >= 4
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

SIDE = 3.0e-4  # mm; area = 9e-8 mm²

f = StepFile(
    catalog_id="Tb005",
    defect=(
        f"ADVANCED_FACE {SIDE}x{SIDE} mm square (area={SIDE**2:.1e} mm²) on PLANE; "
        "declared tolerance 1.0E-4 mm; area < (1e-3)^2 = 1e-6 triggers silent drop "
        "under a bumped-tolerance kernel; alive at (1e-4)^2 = 1e-8 threshold; "
        "face-area comparison should use documented tol not tol*tol"
    ),
)

# The tiny square: (0,0,0) to (3e-4, 3e-4, 0)
p00 = f.cartesian_point((0.0,  0.0,  0.0))
p10 = f.cartesian_point((SIDE, 0.0,  0.0))
p11 = f.cartesian_point((SIDE, SIDE, 0.0))
p01 = f.cartesian_point((0.0,  SIDE, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

d_bot = f.direction((1.0, 0.0, 0.0))
vec_bot = f.vector(d_bot, SIDE)
l_bot = f.line(p00, vec_bot)
e_bot = f.edge_curve(v00, v10, l_bot, name="e_bot")

d_rgt = f.direction((0.0, 1.0, 0.0))
vec_rgt = f.vector(d_rgt, SIDE)
l_rgt = f.line(p10, vec_rgt)
e_rgt = f.edge_curve(v10, v11, l_rgt, name="e_rgt")

d_top = f.direction((1.0, 0.0, 0.0))
vec_top = f.vector(d_top, SIDE)
l_top = f.line(p01, vec_top)
e_top = f.edge_curve(v01, v11, l_top, name="e_top")

d_lft = f.direction((0.0, 1.0, 0.0))
vec_lft = f.vector(d_lft, SIDE)
l_lft = f.line(p00, vec_lft)
e_lft = f.edge_curve(v00, v01, l_lft, name="e_lft")

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])

# Plane for the face
orig_pl = f.cartesian_point((0.0, 0.0, 0.0))
zdir_pl = f.direction((0.0, 0.0, 1.0))
xdir_pl = f.direction((1.0, 0.0, 0.0))
plc_pl  = f.axis2_placement_3d(orig_pl, zdir_pl, xdir_pl)
surf    = f.plane(plc_pl)

face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# Custom PRODUCT chain with declared tolerance 1.0E-4
app_ctx  = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product  = f._emit_raw(f"PRODUCT('Tb005','Tb005','',(#{prod_ctx.eid}))")
pdf      = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc      = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd  = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','face_area_tol_squared_threshold')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
shape_rep = f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('',(#{sbsm.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{shape_rep.eid})")
