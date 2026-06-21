"""A074 — Texture lost when saving binary XBF after STEP import.

Catalog claim: IMAGE_TEXTURE + TEXTURE_MAPPING present in STEP; after
import to XCAF and save as binary XBF, texture bindings are lost. The
bytes IMAGE_TEXTURE and TEXTURE_MAPPING must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A074",
             defect="IMAGE_TEXTURE + TEXTURE_MAPPING present — texture lost on XCAF binary-XBF round-trip")

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

# Texture data — IMAGE_TEXTURE and TEXTURE_MAPPING must appear.
# These are the entities that survive STEP import but are dropped by the
# binary XBF persistence layer on save/reload.
img_tex = f._emit_raw("IMAGE_TEXTURE('face_texture.png')")
tex_coords = f._emit_raw(
    f"TEXTURE_VERTEX_COORDINATE(0.0,0.0)"
)
tex_map = f._emit_raw(
    f"TEXTURE_MAPPING(#{img_tex.eid},$,$)"
)
