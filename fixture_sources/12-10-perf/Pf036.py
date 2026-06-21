"""Pf036 — STEPCAFControl_Reader hangs in infinite loop on cyclic MAPPED_ITEM reference.

Catalog claim: a MAPPED_ITEM references a REPRESENTATION_MAP whose
mapped_representation ultimately contains the original MAPPED_ITEM. The reader's
resolution recursion does not detect the cycle; it keeps descending until the
call stack overflows or the process hangs indefinitely.

Byte assertion: contains(b'MAPPED_ITEM'), contains(b'REPRESENTATION_MAP')
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf036",
    defect=(
        "Cyclic MAPPED_ITEM reference: MAPPED_ITEM references REPRESENTATION_MAP whose "
        "mapped_representation contains the original MAPPED_ITEM; reader recursion has "
        "no cycle detection; hangs indefinitely or stack overflows; "
        "reject: track in-flight MAPPED_ITEM resolutions in a visited-set; on re-entry "
        "emit E_CYCLIC_MAPPED_ITEM; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal anchor geometry
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Build the cyclic MAPPED_ITEM reference chain:
# #A = REPRESENTATION_MAP(origin, #B_shape_rep)
# #B_shape_rep = SHAPE_REPRESENTATION('', (#C_mapped_item), units)
# #C_mapped_item = MAPPED_ITEM('', #A, origin)
# → #C references #A which contains #B_shape_rep which contains #C: cycle

origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(origin, zdir, xdir)

# Units context for the SHAPE_REPRESENTATION
len_unit = f._emit_raw(
    "( NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) LENGTH_UNIT() )"
)
ang_unit = f._emit_raw(
    "( NAMED_UNIT(*) SI_UNIT($,.RADIAN.) PLANE_ANGLE_UNIT() )"
)
sol_unit = f._emit_raw(
    "( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )"
)
unc = f._emit_raw(
    "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#"
    + str(len_unit.eid)
    + ",'distance_accuracy_value','')"
)
geom_ctx = f._emit_raw(
    f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) "
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid})) "
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{len_unit.eid},#{ang_unit.eid},#{sol_unit.eid})) "
    f"REPRESENTATION_CONTEXT('ctx','3D') )"
)

# We need to create a forward-reference cycle. Use _emit_raw to manually assign
# entity ids that create the cycle. We'll use placeholder pattern:
# Reserve the REPRESENTATION_MAP entity before creating the SHAPE_REPRESENTATION.
# Strategy: emit SHAPE_REPRESENTATION first with a placeholder, then REPRESENTATION_MAP
# referencing it, then MAPPED_ITEM referencing back.

# SHAPE_REPRESENTATION that will contain the MAPPED_ITEM (cyclic back-reference)
# We need to emit the MAPPED_ITEM first then reference it, but that requires forward ref.
# Use two passes: emit the MAPPED_ITEM referencing the REPRESENTATION_MAP id we'll
# assign next. This is an intentional cycle — emit REPRESENTATION_MAP first with
# an as-yet-unused SHAPE_REPRESENTATION id, then emit SHAPE_REPRESENTATION referencing
# a MAPPED_ITEM that references back.

# Emit a dummy CARTESIAN_POINT origin for the mapping
map_orig = f.cartesian_point((0.0, 0.0, 0.0))
map_plc  = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
)

# We emit the entities in dependency order, faking the cycle with
# explicit eid references. The cycle is:
#   rep_map -> shape_rep -> mapped_item -> rep_map
#
# Emit mapped_item placeholder as comment, then emit in cycle-creating order:
# 1. SHAPE_REPRESENTATION (self-referencing via MAPPED_ITEM forward ref)
# We use _emit_raw knowing the next 3 eids, since StepFile assigns sequentially.

# Get the next available eid by emitting a dummy and noting its eid
sentinel = f._emit_raw("CARTESIAN_POINT('sentinel',(9.9,9.9,9.9))")
next_eid = sentinel.eid + 1  # this will be rep_map

# rep_map eid = next_eid
# shape_rep eid = next_eid + 1
# mapped_item eid = next_eid + 2

rep_map_eid    = next_eid
shape_rep_eid  = next_eid + 1
mapped_item_eid = next_eid + 2

# Emit them in order; each references the "next" id in the cycle
rep_map     = f._emit_raw(
    f"REPRESENTATION_MAP(#{map_plc.eid},#{shape_rep_eid})"
)
shape_rep   = f._emit_raw(
    f"SHAPE_REPRESENTATION('',(#{mapped_item_eid}),#{geom_ctx.eid})"
)
mapped_item = f._emit_raw(
    f"MAPPED_ITEM('',#{rep_map.eid},#{map_plc.eid})"
)
