"""Pf035 — Large assembly STEP: NUC12 design, eager MAPPED_ITEM closure.

Catalog claim: deep nested NEXT_ASSEMBLY_USAGE_OCCURRENCE + MAPPED_ITEM
graph causes eager resolver to materialise every instance up-front.
Byte assertions: ≥5 NAUO, ≥4 MAPPED_ITEM. We synthesize a small but
structurally-representative subset of that graph.

Repair 2026-07-12 (DRIFT audit): the original construction wired every
NAUO as `#9054,#9054` (relating == related == the root PRODUCT_DEFINITION
that also owns the only shape). STEPControl_Reader treats a product
referenced as NAUO.related as "used" (non-root); with all 5 NAUOs
pointing the root at itself, the root stopped being a transferable root
and TransferRoots() produced 0 shapes — silently contradicting this
entry's own "OCC behavior: silently accepts on small fixture" claim.
MAPPED_ITEM args were also swapped (mapping_source `''`, mapping_target
the REPRESENTATION_MAP itself). Fixed by wiring a genuine child
PRODUCT_DEFINITION (like A001/A005's pattern) as NAUO.related, and
correcting MAPPED_ITEM to (name, mapping_source=rep_map,
mapping_target=placement). Root stays free; live-verified shape(1).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf035",
             defect="deeply nested NAUO + MAPPED_ITEM graph (NUC12 closure blowup)")

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

# Genuine child component (distinct PRODUCT_DEFINITION from the root
# #9054) shared by the NAUO/MAPPED_ITEM closure graph.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")

# Dedicated placement for the sub-component's own representation, shared
# by the REPRESENTATION_MAP and used as every MAPPED_ITEM's mapping_target.
sub_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
sub_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
sub_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
sub_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{sub_origin.eid},#{sub_z.eid},#{sub_x.eid})"
)
sub_sr = f._emit_raw(f"SHAPE_REPRESENTATION('sub_rep',(#{sub_plc.eid}),#9060)")

# 1 REPRESENTATION_MAP shared by 4 MAPPED_ITEMs (the eager-closure setup);
# 5 NAUO chain, each relating the root to the (single) child component.
rmap = f._emit_raw(f"REPRESENTATION_MAP(#{sub_plc.eid},#{sub_sr.eid})")
for k in range(4):
    f._emit_raw(f"MAPPED_ITEM('inst_{k}',#{rmap.eid},#{sub_plc.eid})")
# 5 NAUO entries — each maps a sub-assembly relation to the real child.
for k in range(5):
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_{k}','sub_{k}','',#9054,#{sub_pdef.eid},$)"
    )
