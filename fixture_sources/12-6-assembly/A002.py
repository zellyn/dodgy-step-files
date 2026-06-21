"""A002 — Hidden / suppressed bodies leak into export, or are dropped silently.

Catalog claim: writer emits a NEXT_ASSEMBLY_USAGE_OCCURRENCE whose target
PRODUCT_DEFINITION has no SHAPE_DEFINITION_REPRESENTATION (the body was
hidden / suppressed and the writer dropped it), leaving a dangling NAUO.
The HIDDEN keyword appears in the byte stream to signal the suppression
intent; a second NAUO references a valid (visible) body.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A002",
             defect="2 NAUO — one targeting empty hidden body (HIDDEN flag in byte stream)")

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

# Visible sub-component (NAUO 1).
vis_prod = f._emit_raw(f"PRODUCT('Visible','Visible','',(#{sub_pdc.eid}))")
vis_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{vis_prod.eid})")
vis_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{vis_pdf.eid},#9003)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','visible_body','',#9004,#{vis_pdef.eid},$)"
)

# Hidden sub-component — body was suppressed so NO SDR is emitted (NAUO 2
# is dangling). The HIDDEN keyword records the suppression intent.
hid_prod = f._emit_raw(f"PRODUCT('HIDDEN_Body','HIDDEN_Body','',(#{sub_pdc.eid}))")
hid_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{hid_prod.eid})")
hid_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','HIDDEN',#{hid_pdf.eid},#9003)"
)
# No SHAPE_DEFINITION_REPRESENTATION for the hidden body — the dropped-body defect.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','hidden_body','',#9004,#{hid_pdef.eid},$)"
)
