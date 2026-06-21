"""Tb012 — Sphere seam matching across pole singularity.

SPHERICAL_SURFACE has parametric singularity at V = +/- pi/2. A wire pcurve
at V = pi/2 - 1.0e-9 is just below the north pole. A receiver with pole-snap
tolerance 1.0e-7 rad does not snap (1.0e-9 < 1.0e-7). A receiver with
pole-snap tolerance 1.0e-3 rad snaps the wire onto the pole, collapsing the
upper face into a degenerate point. Same wire, different surface extents.

Byte assertions:
  contains(b'SPHERICAL_SURFACE') and contains(b'CIRCLE')
  count_entity_def(b'VERTEX_POINT') == 1
  contains(b'1.0E-7')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb012",
    defect=(
        "SPHERICAL_SURFACE R=1; wire pcurve at V=pi/2-1.0E-9 (just below pole); "
        "pole-snap at 1.0E-7 rad does not snap; at 1.0E-3 rad snaps and collapses face; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Sphere placement.
origin = f.cartesian_point((0.0, 0.0, 0.0), name="o")
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(origin, zdir, xdir, name="plc")
sph = f._emit_raw(f"SPHERICAL_SURFACE('sph',#{plc.eid},1.0)")

# Near-pole point: V = pi/2 - 1e-9, U = 0.
# x = R*cos(V)*cos(U) = 1 * cos(pi/2 - 1e-9) * 1 = sin(1e-9) ≈ 1e-9
# z = R*sin(V) = cos(1e-9) ≈ 1.0
near_pole_x = math.sin(1.0e-9)
near_pole_z = math.cos(1.0e-9)
p_near = f.cartesian_point((near_pole_x, 0.0, near_pole_z), name="p_near_pole")
# One VERTEX_POINT (closed circle edge uses same vertex start=end).
v_near = f.vertex_point(p_near, name="v_near_pole_seam")

# UV context (2D) for pcurve.
uv_ctx = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "GLOBAL_UNIT_ASSIGNED_CONTEXT($)"
    "REPRESENTATION_CONTEXT('uv','2D'))"
)

# Pcurve: V constant at pi/2 - 1e-9, U from 0 to 2*pi.
v_param = math.pi / 2.0 - 1.0e-9
uv0 = f.cartesian_point((0.0, v_param), name="uv0")
uv_dir = f.direction((1.0, 0.0))
uv_vec = f.vector(uv_dir, 2.0 * math.pi)
uv_line = f.line(uv0, uv_vec, name="pcurve_near_pole")
pdef = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pdef',(#{uv_line.eid}),#{uv_ctx.eid})"
)
pc = f._emit_raw(f"PCURVE('pc',#{sph.eid},#{pdef.eid})")

# 3D circle at radius ~1e-9 (near-pole circle).
circ_orig = f.cartesian_point((near_pole_x, 0.0, near_pole_z), name="circ_orig")
circ_plc = f.axis2_placement_3d(circ_orig, zdir, xdir, name="circ_axis")
circ = f._emit_raw(f"CIRCLE('circ_near_pole',#{circ_plc.eid},1.0E-9)")

sc = f._emit_raw(f"SURFACE_CURVE('sc',#{circ.eid},(#{pc.eid}),.PCURVE_S1.)")
# Closed edge: same vertex for start and end.
edge = f.edge_curve(v_near, v_near, sc, name="e_at_pole_minus_1e-9")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid},#{sph.eid}))"
)

# Manual PRODUCT chain with declared tolerance 1.0E-7 (byte assertion).
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb012','Tb012','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','strict_tolerance_no_pole_snap')"
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
