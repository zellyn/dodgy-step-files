"""A018 — STYLED_ITEM at wrong scope: assembly-level color override lost.

Catalog claim: STYLED_ITEM attached to top-level SHAPE_REPRESENTATION
instead of per-MAPPED_ITEM instances → all instances colored alike.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: one base
face wrapped in REPRESENTATION_MAP, 2 MAPPED_ITEM instances, with one
STYLED_ITEM attached to the TOP-LEVEL shape-representation (the wrong
scope) rather than each MAPPED_ITEM (the right scope).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A018",
             defect="STYLED_ITEM attached at top-level shape-rep instead of per MAPPED_ITEM")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build base 1x1 face.
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
base_face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([base_face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# REPRESENTATION_MAP off the base shape, 2 MAPPED_ITEM instances.
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#9022)")
for k, offset in enumerate([(2.0, 0.0, 0.0), (4.0, 0.0, 0.0)]):
    p_inst = f.cartesian_point(offset)
    plc_inst = f.axis2_placement_3d(p_inst, zdir, xdir)
    f._emit_raw(
        f"MAPPED_ITEM('instance_{k}',#{rep_map.eid},#{plc_inst.eid})"
    )

# STYLED_ITEM attached to top-level SHAPE_REPRESENTATION (#9022) —
# WRONG SCOPE: should be attached to each MAPPED_ITEM.
colour = f._emit_raw("COLOUR_RGB('wrong_scope_red',0.8,0.0,0.0)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
# WRONG SCOPE: attaches to #9022 (the MSSR) instead of to each MAPPED_ITEM.
f._emit_raw(f"STYLED_ITEM('wrong_scope',(#{psa.eid}),#9022)")
