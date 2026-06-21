"""N004 — Edge SameParameter flag asserted but 3D curve and pcurve disagree.

An EDGE_CURVE declares SameParameter=.T. but a sampling check shows the maximum
point-wise deviation exceeds the declared edge tolerance (1.0E-6). The 3D LINE
runs from (0,0,0) to (10,0,0); the pcurve LINE on the PLANE runs from (0,0.005)
to (10,0.005) — offset 0.005 mm in v — so parameter-by-parameter evaluation
disagrees with the 3D curve by 5.0E-3 >> 1.0E-6.

The flag was set without re-validation after a geometry edit; the metadata
claims an invariant the data no longer satisfies.

Byte assertions:
  contains(b'PCURVE') and contains(b'SURFACE_CURVE')
  contains(b'PLANE') and count_entity_def(b'EDGE_CURVE') == 1
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N004",
    defect=(
        "EDGE_CURVE SameParameter=.T. but pcurve on PLANE offset by 0.005 mm; "
        "edge tolerance 1.0E-6; 3D curve vs pcurve deviation 5.0E-3 >> tol; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# 3D curve: LINE from (0,0,0) to (10,0,0)
p3d_start = f.cartesian_point((0.0, 0.0, 0.0), name="p3d_start")
p3d_end = f.cartesian_point((10.0, 0.0, 0.0), name="p3d_end")
v_start = f.vertex_point(p3d_start, name="v_start")
v_end = f.vertex_point(p3d_end, name="v_end")

d3d = f.direction((1.0, 0.0, 0.0))
vec3d = f.vector(d3d, 10.0)
line3d = f.line(p3d_start, vec3d, name="line3d")

# Host plane: XZ plane (normal = Y axis)
ax_orig = f.cartesian_point((0.0, 0.0, 0.0), name="plane_orig")
plane_normal = f.direction((0.0, 1.0, 0.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, plane_normal, plane_xdir)
plane = f.plane(plc, name="host_plane")

# 2D pcurve: LINE on plane from (u=0, v=0.005) to (u=10, v=0.005)
# v=0.005 is the offset (0.005 mm above the XZ plane).
uv_ctx = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "GLOBAL_UNIT_ASSIGNED_CONTEXT($)"
    "REPRESENTATION_CONTEXT('uv_ctx','2D'))"
)
pc_start = f.cartesian_point((0.0, 0.005), name="pc_start_offset")
pc_dir = f.direction((1.0, 0.0))
pc_vec = f.vector(pc_dir, 10.0)
pc_line = f.line(pc_start, pc_vec, name="pc_line_offset")
pdef = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pdef',(#{pc_line.eid}),#{uv_ctx.eid})"
)
pcurve = f._emit_raw(f"PCURVE('pc_offset',#{plane.eid},#{pdef.eid})")

# SURFACE_CURVE binding 3D line with the offset pcurve; SameParameter flag on edge = .T.
sc = f._emit_raw(
    f"SURFACE_CURVE('sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# edge_curve: SameParameter=.T. (True) — the lie
edge = f.edge_curve(v_start, v_end, sc, True, name="edge_sameparam_lie")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N004','N004','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tight tolerance 1.0E-6 — byte assertion value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','model_precision')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
