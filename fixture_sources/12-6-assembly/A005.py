"""A005 — Lost assembly hierarchy on round-trip (flatten to single CATPart / single solid).

Catalog claim: a multi-level NAUO graph imports as a single flat part with
N solid bodies, losing PRODUCT_DEFINITION nesting. Key signature: every
leaf body shares one PRODUCT_DEFINITION_FORMATION.
Three NAUO rows + 3 REPRESENTATION_MAP + 3 MAPPED_ITEM all referencing
the same (shared) PRODUCT_DEFINITION_FORMATION.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A005",
             defect="3 NAUO + 3 REPRESENTATION_MAP + 3 MAPPED_ITEM sharing one PDF (flatten trap)")

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

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
# Shared PRODUCT and PDF — the flatten trap: all 3 instances share this.
shared_prod = f._emit_raw(f"PRODUCT('LeafPart','LeafPart','',(#{sub_pdc.eid}))")
# SHARED PRODUCT_DEFINITION_FORMATION — every instance references the same PDF.
shared_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{shared_prod.eid})")

# Shared representation (single shape rep for the leaf geometry).
leaf_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('leaf_rep',(#{plc.eid}),#9060)"
)

# 3 instances: each gets its own PRODUCT_DEFINITION + own NAUO + own
# REPRESENTATION_MAP + own MAPPED_ITEM — but all share the same PDF (flatten trap).
for i in range(1, 4):
    pdef_i = f._emit_raw(
        f"PRODUCT_DEFINITION('design','',#{shared_pdf.eid},#9053)"
    )
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('{i}','leaf{i}','',#9054,#{pdef_i.eid},$)"
    )
    # Each instance gets its own REPRESENTATION_MAP and MAPPED_ITEM.
    rep_map_i = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#{leaf_sr.eid})")
    inst_orig = f._emit_raw(
        f"CARTESIAN_POINT('inst{i}_origin',({float(i-1)*2.0},0.0,0.0))"
    )
    inst_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
    inst_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
    inst_plc = f._emit_raw(
        f"AXIS2_PLACEMENT_3D('inst{i}_plc',#{inst_orig.eid},#{inst_z.eid},#{inst_x.eid})"
    )
    f._emit_raw(f"MAPPED_ITEM('mi{i}',#{rep_map_i.eid},#{inst_plc.eid})")
