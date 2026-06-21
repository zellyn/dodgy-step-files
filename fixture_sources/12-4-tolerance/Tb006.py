"""Tb006 — Edge length sub-tolerance squared in 2D pcurve length.

Catalog claim: Pcurve domain length is the parameter range; some kernels test
pcurve degeneracy by comparing parameter range to tol*tol_param. A pcurve with
parameter range 1e-4 on a face with declared tol = 1e-3 is alive at
tol_param = sqrt(tol) ≈ 3.16e-2 but degenerate at tol_param = tol*tol = 1e-6.

Fixture: EDGE_CURVE on a CYLINDRICAL_SURFACE (radius 1.0) with a SURFACE_CURVE
whose PCURVE has parameter range 1e-4 in the U direction; declared uncertainty
1.0E-3. The pcurve is a short segment on the cylinder at V=0..1e-4.

Tier-3: face[0].area < 1e-6, face[0].surface_type == "plane", n_edges_total >= 4
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

PCURVE_RANGE = 1.0e-4   # parametric range — the key defect value
FACE_SIDE = 3.0e-4      # face side length for small-face tier-3 assertion

f = StepFile(
    catalog_id="Tb006",
    defect=(
        "EDGE_CURVE with PCURVE whose parameter range is 1e-4 (U-direction); "
        "declared tolerance 1.0E-3; "
        "pcurve degeneracy threshold tol*tol_param = 1e-6 kills the edge under "
        "one policy, while sqrt(tol) ≈ 3.16e-2 keeps it under another; "
        "receiver A keeps edge; receiver B drops it; "
        "small ADVANCED_FACE on a PLANE for tier-3 face[0].area assertion"
    ),
)

# Host plane for the face
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf_plane = f.plane(plc)

# Tiny square face (for tier-3: area < 1e-6)
p00 = f.cartesian_point((0.0,       0.0,       0.0))
p10 = f.cartesian_point((FACE_SIDE, 0.0,       0.0))
p11 = f.cartesian_point((FACE_SIDE, FACE_SIDE, 0.0))
p01 = f.cartesian_point((0.0,       FACE_SIDE, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

d_bot = f.direction((1.0, 0.0, 0.0))
l_bot = f.line(p00, f.vector(d_bot, FACE_SIDE))
e_bot = f.edge_curve(v00, v10, l_bot, name="e_bot")

d_rgt = f.direction((0.0, 1.0, 0.0))
l_rgt = f.line(p10, f.vector(d_rgt, FACE_SIDE))
e_rgt = f.edge_curve(v10, v11, l_rgt, name="e_rgt")

d_top = f.direction((1.0, 0.0, 0.0))
l_top = f.line(p01, f.vector(d_top, FACE_SIDE))
e_top = f.edge_curve(v01, v11, l_top, name="e_top")

d_lft = f.direction((0.0, 1.0, 0.0))
l_lft = f.line(p00, f.vector(d_lft, FACE_SIDE))
e_lft = f.edge_curve(v00, v01, l_lft, name="e_lft")

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf_plane)

# Cylindrical surface for the pcurve edge (embedded separately in file)
cyl_orig = f.cartesian_point((20.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, 1.0)

# The defect PCURVE: parameter range = 1e-4 in U direction
# U=0 to U=1e-4 on a unit cylinder (1 radian = 1 mm arc)
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
uv_start = f.cartesian_point((0.0, 0.0), name="pcurve_uv_start")
uv_dir   = f.direction((1.0, 0.0), name="pcurve_udir")
uv_vec   = f.vector(uv_dir, PCURVE_RANGE, name="pcurve_urange_1e-4")
line2d   = f.line(uv_start, uv_vec, name="pcurve_line")
defrep   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_range_1e-4',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('pcurve_param_range_1e-4',#{cyl_surf.eid},#{defrep.eid})")

# 3D line: tiny arc at v=0 from (1,0,0) to (cos(1e-4), sin(1e-4), 0)
p3d_start = f.cartesian_point((1.0, 0.0, 0.0))
p3d_end   = f.cartesian_point((math.cos(PCURVE_RANGE), math.sin(PCURVE_RANGE), 0.0))
v_3d_start = f.vertex_point(p3d_start)
v_3d_end   = f.vertex_point(p3d_end)
l3d_dir = f.direction((0.0, 1.0, 0.0))
l3d_vec = f.vector(l3d_dir, PCURVE_RANGE)  # ~arc length on unit cylinder
l3d = f.line(p3d_start, l3d_vec)

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{l3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
defect_edge = f._emit_raw(
    f"EDGE_CURVE('pcurve_sub_tol_squared',#{v_3d_start.eid},#{v_3d_end.eid},"
    f"#{surface_curve.eid},.T.)"
)

# Build shell + SBSM from the face only (the defect edge is orphaned for inspection)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])

# Custom PRODUCT chain with declared tolerance 1.0E-3
app_ctx  = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product  = f._emit_raw(f"PRODUCT('Tb006','Tb006','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','pcurve_domain_length_squared_tol_test')"
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
