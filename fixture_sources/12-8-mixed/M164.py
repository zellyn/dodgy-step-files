"""M164 — Linear pattern of arc-shaped feature emits twisted faces.

Catalog claim: 4 MAPPED_ITEMs referencing the same REPRESENTATION_MAP,
where the 4th's transformation_operator.axis is (0,0,-1) while
instances 1-3 have (0,0,1). LinearPattern of count=4 over arc-shaped
Pad → 4th instance inverted.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a base
ADVANCED_FACE wrapped in REPRESENTATION_MAP, then 4 MAPPED_ITEMs
instantiating it. The 4th has DIRECTION(0,0,-1) for its axis.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="M164",
             defect="4 MAPPED_ITEMs, the 4th with axis (0,0,-1) instead of (0,0,1)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))

# Build the base "arc-pad" face — a quad on the XY plane.
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
base_face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([base_face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Now build a REPRESENTATION_MAP off the base shell and instantiate 4 MAPPED_ITEMs.
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{plc.eid},#9022)"   # the MSSR from add_product_chain
)
# Three normal MAPPED_ITEMs at +X, +Y, -X — with axis (0,0,1).
for k, offset in enumerate([(2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (6.0, 0.0, 0.0)]):
    p_inst = f.cartesian_point(offset)
    zi = f.direction((0.0, 0.0, 1.0))   # correct axis
    xi = f.direction((1.0, 0.0, 0.0))
    plc_inst = f.axis2_placement_3d(p_inst, zi, xi)
    f._emit_raw(
        f"MAPPED_ITEM('instance_{k}',#{rep_map.eid},#{plc_inst.eid})"
    )

# The 4th MAPPED_ITEM — INVERTED axis (0,0,-1). This is the defect.
p_inst4 = f.cartesian_point((8.0, 0.0, 0.0))
z_inverted = f.direction((0.0, 0.0, -1.0))   # the bug
x4 = f.direction((1.0, 0.0, 0.0))
plc_inst4 = f.axis2_placement_3d(p_inst4, z_inverted, x4)
f._emit_raw(
    f"MAPPED_ITEM('instance_3_inverted',#{rep_map.eid},#{plc_inst4.eid})"
)
