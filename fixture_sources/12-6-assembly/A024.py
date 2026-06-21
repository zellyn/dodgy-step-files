"""A024 — MAPPED_ITEM AXIS2_PLACEMENT_3D with left-handed (mirrored, negative-determinant) frame.

Catalog claim: a MAPPED_ITEM's target AXIS2_PLACEMENT_3D uses DIRECTION
axes that form a left-handed frame: Z=(0,0,1) and X=(-1,0,0), giving
implicit Y=Z×X=(0,-1,0) — negative-determinant placement. Keyword
'MIRROR' must appear in the byte stream.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A024",
             defect="MAPPED_ITEM with left-handed AXIS2_PLACEMENT_3D (MIRROR, negative determinant)")

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

# Sub-component representation.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9004,#{sub_pdef.eid},$)"
)

sub_sr = f._emit_raw(f"SHAPE_REPRESENTATION('sub_rep',(#{plc.eid}),#9010)")
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#{sub_sr.eid})")

# Left-handed (MIRROR) frame — X=(-1,0,0), Z=(0,0,1) → det = -1.
mirror_origin = f._emit_raw("CARTESIAN_POINT('MIRROR_ORIGIN',(5.0,0.0,0.0))")
mirror_z = f._emit_raw("DIRECTION('MIRROR_Z',(0.0,0.0,1.0))")
# X=(-1,0,0): forms left-handed frame with Z=(0,0,1).
mirror_x = f._emit_raw("DIRECTION('MIRROR_X',(-1.0,0.0,0.0))")
mirror_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('MIRROR',#{mirror_origin.eid},#{mirror_z.eid},#{mirror_x.eid})"
)

# MAPPED_ITEM referencing the mirrored placement — the defect.
f._emit_raw(f"MAPPED_ITEM('mi_mirror',#{rep_map.eid},#{mirror_plc.eid})")
