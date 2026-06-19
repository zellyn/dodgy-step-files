"""A108 — Draft-mirrored body silently dropped on STEP export.

Catalog claim: an assembly with a PRODUCT subassembly containing a Part
Design body and a mirrored copy of that body (via the Draft workbench's
'Mirror' tool) has the mirror dropped during STEP export. The mirrored
body is structurally a NEXT_ASSEMBLY_USAGE_OCCURRENCE referencing the
same source PRODUCT with a transformation that includes a reflected
(negative-determinant) AXIS2_PLACEMENT_3D ref_direction. Some writers'
NAUO-emit path skips entries whose transformation has a negative
determinant.

Source: pattern-mined from FreeCAD/FreeCAD#13581 (LGPL-clean — pattern
only, no bytes copied). User-reported: "Only one of the bodies will be
in the step file."

LGPL-clean: pattern-matched, no bytes copied.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A108",
             defect="NAUO with mirror-reflected AXIS2_PLACEMENT_3D dropped on export")

# Build a tiny "body" shape: 1x1 square at origin, on a plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_body = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc_body)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Now add a mirror placement: AXIS2_PLACEMENT_3D with ref_direction
# negated, giving a mirror reflection on the X axis. This is the
# defect-carrier — the mirrored child placement.
mirror_orig = f.cartesian_point((3.0, 0.0, 0.0))
mirror_xdir = f.direction((-1.0, 0.0, 0.0))   # negated: mirror reflection
mirror_plc = f.axis2_placement_3d(mirror_orig, zdir, mirror_xdir)

# Wrap the body in a REPRESENTATION_MAP + MAPPED_ITEM at the mirrored
# placement. This is the topology pattern Draft's Mirror emits and
# some writers' NAUO path skips.
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{plc_body.eid},#9022)"   # references the MSSR from add_product_chain
)
mapped_item = f._emit_raw(
    f"MAPPED_ITEM('mirrored_body',#{rep_map.eid},#{mirror_plc.eid})"
)

# Emit a second PRODUCT chain for the mirrored child, so the assembly
# has explicit parent + mirrored child products.
mirror_pdc = f._emit_raw(
    f"PRODUCT_CONTEXT('mirror_part',#9000,'mechanical')"
)
mirror_prod = f._emit_raw(
    f"PRODUCT('Body_Mirrored','Body_Mirrored','',(#{mirror_pdc.eid}))"
)
mirror_pdf = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{mirror_prod.eid})"
)
mirror_pdef_ctx = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design')"
)
mirror_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{mirror_pdf.eid},#{mirror_pdef_ctx.eid})"
)
# NEXT_ASSEMBLY_USAGE_OCCURRENCE linking parent → mirrored child.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','BodyMirrored','',"
    f"#9004,#{mirror_pdef.eid},$)"
)
