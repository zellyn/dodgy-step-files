"""N020 — Coordinate-system origin offset: hard-coded BOARD_OFFSET 0.05mm in PCB MCAD pipeline.

KiCad hard-codes BOARD_OFFSET = 0.05 mm on every component's AXIS2_PLACEMENT_3D,
floating components above the board surface to avoid Z-fighting. Downstream MCAD
tools see consistent 0.05 mm misalignment.

Three AXIS2_PLACEMENT_3D instances: board reference (z=0), nominal component
placement (z=0), and board-offset placement (z=0.05). The 0.05 value is
encoded in the third placement's location Z-coordinate.

Byte assertions:
  count_entity_def(b'AXIS2_PLACEMENT_3D') == 3
  matches(rb'0\\.05')
  not_contains(b'EDGE_CURVE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N020",
    defect=(
        "KiCad BOARD_OFFSET: 3×AXIS2_PLACEMENT_3D; board at z=0, component "
        "placement at z=0, hard-coded offset at z=0.05; wireframe-only; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Placement 1: board reference at origin
bp_orig = f.cartesian_point((0.0, 0.0, 0.0), name="board_ref_origin")
bp_zdir = f.direction((0.0, 0.0, 1.0))
bp_xdir = f.direction((1.0, 0.0, 0.0))
plc_board = f.axis2_placement_3d(bp_orig, bp_zdir, bp_xdir, name="board_ref")

# Placement 2: nominal component position (z=0, same as board top)
cp_orig = f.cartesian_point((5.0, 3.0, 0.0), name="comp_nominal_origin")
cp_zdir = f.direction((0.0, 0.0, 1.0))
cp_xdir = f.direction((1.0, 0.0, 0.0))
plc_comp_nominal = f.axis2_placement_3d(cp_orig, cp_zdir, cp_xdir, name="comp_nominal")

# Placement 3: board-offset placement (z=0.05, the hard-coded offset)
bo_orig = f.cartesian_point((5.0, 3.0, 0.05), name="comp_board_offset_origin")
bo_zdir = f.direction((0.0, 0.0, 1.0))
bo_xdir = f.direction((1.0, 0.0, 0.0))
plc_offset = f.axis2_placement_3d(bo_orig, bo_zdir, bo_xdir, name="comp_board_offset")

# Aggregate the three placements; no EDGE_CURVE (as per byte assertion).
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('board_placements',"
    f"(#{plc_board.eid},#{plc_comp_nominal.eid},#{plc_offset.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N020','N020','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','pcb_mcad_precision')"
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
