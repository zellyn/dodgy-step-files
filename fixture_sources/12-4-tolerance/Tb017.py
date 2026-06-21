"""Tb017 — Two coincident faces at distance equal to declared tolerance.

Catalog claim: Two ADVANCED_FACEs (planar, parallel, same outline) are
separated by exactly 1.0e-6 mm = the declared tolerance. A kernel comparing
strict < keeps them as separate faces (a thin slab). A kernel comparing <=
merges them and the slab disappears.

Reproducer recipe: Two coplanar ADVANCED_FACEs on parallel PLANEs offset by
1.0e-6 mm; declared uncertainty 1.0e-6 mm. Wrap in PRODUCT chain.

Tier-3: n_edges_total >= 8, face[0].surface_type == "plane",
         face[1].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

TOL = 1.0e-6   # declared tolerance AND separation between faces

f = StepFile(
    catalog_id="Tb017",
    defect=(
        f"two parallel ADVANCED_FACEs on PLANEs separated by exactly {TOL:.1e} mm; "
        f"declared uncertainty {TOL:.1e} mm — strict < keeps both faces (thin slab); "
        "<=  comparison merges them (slab disappears); "
        "equality at tolerance boundary creates policy-dependent geometry"
    ),
)

# Face 1: 10x10 square at z = 0
p000 = f.cartesian_point(( 0.0,  0.0, 0.0))
p100 = f.cartesian_point((10.0,  0.0, 0.0))
p110 = f.cartesian_point((10.0, 10.0, 0.0))
p010 = f.cartesian_point(( 0.0, 10.0, 0.0))
v000 = f.vertex_point(p000)
v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110)
v010 = f.vertex_point(p010)

d_x = f.direction((1.0, 0.0, 0.0))
d_y = f.direction((0.0, 1.0, 0.0))
e_b0 = f.edge_curve(v000, v100, f.line(p000, f.vector(d_x, 10.0)), name="f1_bot")
e_b1 = f.edge_curve(v100, v110, f.line(p100, f.vector(d_y, 10.0)), name="f1_rgt")
e_b2 = f.edge_curve(v010, v110, f.line(p010, f.vector(d_x, 10.0)), name="f1_top")
e_b3 = f.edge_curve(v000, v010, f.line(p000, f.vector(d_y, 10.0)), name="f1_lft")

loop1 = f.edge_loop([
    f.oriented_edge(e_b0, True),
    f.oriented_edge(e_b1, True),
    f.oriented_edge(e_b2, False),
    f.oriented_edge(e_b3, False),
])

orig1 = f.cartesian_point((0.0, 0.0, 0.0))
zdir1 = f.direction((0.0, 0.0, 1.0))
xdir1 = f.direction((1.0, 0.0, 0.0))
plc1  = f.axis2_placement_3d(orig1, zdir1, xdir1)
surf1 = f.plane(plc1)
face1 = f.advanced_face([f.face_outer_bound(loop1)], surf1, name="face_z0")

# Face 2: identical 10x10 square at z = TOL (1e-6 mm above face 1)
z2 = TOL
p200 = f.cartesian_point(( 0.0,  0.0, z2))
p210 = f.cartesian_point((10.0,  0.0, z2))
p211 = f.cartesian_point((10.0, 10.0, z2))
p201 = f.cartesian_point(( 0.0, 10.0, z2))
v200 = f.vertex_point(p200)
v210 = f.vertex_point(p210)
v211 = f.vertex_point(p211)
v201 = f.vertex_point(p201)

d_x2 = f.direction((1.0, 0.0, 0.0))
d_y2 = f.direction((0.0, 1.0, 0.0))
e_c0 = f.edge_curve(v200, v210, f.line(p200, f.vector(d_x2, 10.0)), name="f2_bot")
e_c1 = f.edge_curve(v210, v211, f.line(p210, f.vector(d_y2, 10.0)), name="f2_rgt")
e_c2 = f.edge_curve(v201, v211, f.line(p201, f.vector(d_x2, 10.0)), name="f2_top")
e_c3 = f.edge_curve(v200, v201, f.line(p200, f.vector(d_y2, 10.0)), name="f2_lft")

loop2 = f.edge_loop([
    f.oriented_edge(e_c0, True),
    f.oriented_edge(e_c1, True),
    f.oriented_edge(e_c2, False),
    f.oriented_edge(e_c3, False),
])

orig2 = f.cartesian_point((0.0, 0.0, z2))
zdir2 = f.direction((0.0, 0.0, 1.0))
xdir2 = f.direction((1.0, 0.0, 0.0))
plc2  = f.axis2_placement_3d(orig2, zdir2, xdir2)
surf2 = f.plane(plc2)
face2 = f.advanced_face([f.face_outer_bound(loop2)], surf2, name="face_z_tol")

# Shell containing both faces
shell = f.open_shell([face1, face2])
sbsm  = f.shell_based_surface_model([shell])

# Custom PRODUCT chain with declared tolerance == separation == 1.0E-6
app_ctx  = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product  = f._emit_raw(f"PRODUCT('Tb017','Tb017','',(#{prod_ctx.eid}))")
pdf      = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc      = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd  = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu  = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance EQUALS the face separation: 1.0E-6
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','face_separation_equals_tolerance')"
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
