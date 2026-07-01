"""Ad129 — Negative-determinant CARTESIAN_TRANSFORMATION_OPERATOR_3D in MAPPED_ITEM.

Catalog claim: a STEP AP214 file with a MAPPED_ITEM whose transformation
matrix has a negative determinant (det = -1.0, a reflection). Component B
should appear as the mirror image of component A. Readers that correctly handle
negative-det transformations produce a mirror image; readers that silently force
det to +1 (treating the transformation as orthogonal) produce the wrong
orientation.

The CARTESIAN_TRANSFORMATION_OPERATOR_3D axes form a left-handed coordinate
system: axis1=(1,0,0), axis2=(0,1,0), axis3=(0,0,-1) — det = -1.

OCCT silently treats the transformation as identity (shape(1) still loads),
so the defect is a silent misinterpretation rather than a parse failure.

Source: Fusion 360 community mirror pattern STEP export (DEF-V). LGPL-clean:
synthesised from the defect pattern, no upstream bytes copied.

Byte assertions:
  contains(b'CARTESIAN_TRANSFORMATION_OPERATOR_3D')
  contains(b'MAPPED_ITEM')
Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad129",
    defect=(
        "Negative-determinant CARTESIAN_TRANSFORMATION_OPERATOR_3D (det=-1, reflection) "
        "in MAPPED_ITEM: axis1=(1,0,0) axis2=(0,1,0) axis3=(0,0,-1) form a left-handed "
        "coord system; conforming readers produce a mirror image of component B; "
        "readers that force det=+1 (silently orthogonalize) produce wrong orientation; "
        "OCCT silently treats as identity, yields shape(1); "
        "Fusion 360 mirror pattern STEP export DEF-V"
    ),
)

# ── Valid planar face (1×1 square) — component A via standard product chain ───
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d   = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln  = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0,  0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0,  1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT PAYLOAD: negative-det CARTESIAN_TRANSFORMATION_OPERATOR_3D ─────────
# Left-handed axes: axis1 × axis2 = axis3, but axis3 = (0,0,-1)  → det = -1.
# This is the mirror-reflection matrix: (x,y,z) → (x, y, -z).
#
# CARTESIAN_TRANSFORMATION_OPERATOR_3D(name, axis1, axis2, local_origin,
#                                       scale, axis3)
# Per ISO 10303-42 §4.4.7:
#   axis1 = direction of transformed X axis
#   axis2 = direction of transformed Y axis
#   axis3 = direction of transformed Z axis (det<0 when left-handed)
#   local_origin = translation (origin, here at X+5 to separate from component A)
#   scale = 1.0

cto_axis1  = f._emit_raw("DIRECTION('axis1',(1.0,0.0,0.0))")
cto_axis2  = f._emit_raw("DIRECTION('axis2',(0.0,1.0,0.0))")
cto_axis3  = f._emit_raw("DIRECTION('axis3',(0.0,0.0,-1.0))")   # det = -1
cto_origin = f._emit_raw("CARTESIAN_POINT('mirror_origin',(5.0,0.0,0.0))")
cto = f._emit_raw(
    f"CARTESIAN_TRANSFORMATION_OPERATOR_3D("
    f"'neg_det_mirror',"
    f"#{cto_axis1.eid},"
    f"#{cto_axis2.eid},"
    f"#{cto_origin.eid},"
    f"1.0,"
    f"#{cto_axis3.eid})"
)

# The sub-component shape representation is the same face (share the shell's
# SBSM as the representation item).
# ITEM_DEFINED_TRANSFORMATION links the two representations.
rep_orig = f._emit_raw(
    "CARTESIAN_POINT('rep_origin',(0.0,0.0,0.0))"
)
rep_z    = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
rep_x    = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
rep_plc  = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('rep_plc',#{rep_orig.eid},#{rep_z.eid},#{rep_x.eid})"
)
# Geometry context for component B's shape representation.
lu   = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau  = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau  = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc  = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','')"
)
gctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)
# Component B shape representation (re-uses sbsm as items element).
comp_b_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('comp_b_rep',(#{sbsm.eid}),#{gctx.eid})"
)
# REPRESENTATION_MAP: maps the source shape to the target.
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{rep_plc.eid},#{comp_b_sr.eid})"
)
# ITEM_DEFINED_TRANSFORMATION using the negative-det CTO.
idt = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('mirror_xform','',#{rep_plc.eid},#{cto.eid})"
)
# MAPPED_ITEM places component B via the negative-det transformation.
f._emit_raw(
    f"MAPPED_ITEM('comp_b_mirror',#{rep_map.eid},#{cto.eid})"
)
