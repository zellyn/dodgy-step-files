"""A001 — Duplicated component instances collapsed to a single transform on export.

Catalog claim: when the same component appears multiple times under an
assembly with different placements, the writer collapses many MAPPED_ITEM
references of the same product into one, sharing a single
AXIS2_PLACEMENT_3D rather than giving each instance its own. Three
instances of the same PRODUCT_DEFINITION appear via 3 NAUO rows, but all
3 MAPPED_ITEMs share the same AXIS2_PLACEMENT_3D('SHARED_PLACEMENT').
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A001",
             defect="3 NAUO + 3 MAPPED_ITEM sharing one AXIS2_PLACEMENT_3D(SHARED_PLACEMENT)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
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

# Sub-component product shared by 3 instances.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)")

# Shared AXIS2_PLACEMENT_3D — the defect: all 3 instances reuse this one.
shared_origin = f._emit_raw("CARTESIAN_POINT('SHARED_PLACEMENT',(0.0,0.0,0.0))")
shared_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
shared_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
shared_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('SHARED_PLACEMENT',#{shared_origin.eid},#{shared_z.eid},#{shared_x.eid})"
)

# Sub-component representation referencing the shared placement.
sub_sr = f._emit_raw(f"SHAPE_REPRESENTATION('sub_rep',(#{shared_plc.eid}),#9010)")

# Representation map (single) for the sub-component.
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{shared_plc.eid},#{sub_sr.eid})")

# 3 NAUO rows + 3 MAPPED_ITEMs all pointing at the same shared placement.
for i in range(1, 4):
    nauo = f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('{i}','inst{i}','',#9004,#{sub_pdef.eid},$)"
    )
    f._emit_raw(
        f"MAPPED_ITEM('mi{i}',#{rep_map.eid},#{shared_plc.eid})"
    )
