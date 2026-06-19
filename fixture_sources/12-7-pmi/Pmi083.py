"""Pmi083 — Annotation plane orientation flipped on GD&T import.

Catalog claim: a GD&T annotation plane on a face has its normal vector
pointing into the part. The fixture provides a sliver face with
reversed orientation (.F.) so the orientation-flip-vs-surface scenario
the catalog claims is materialized.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a single
narrow sliver ADVANCED_FACE marked .F. on a PLANE.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi083",
             defect="sliver ADVANCED_FACE marked .F. (high aspect ratio + reversed orientation)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Sliver face: 10.0 wide × 1e-5 tall — aspect ratio 1e6.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 1.0e-5, 0.0))
p3 = f.cartesian_point((0.0, 1.0e-5, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 10.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0e-5, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 10.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0e-5, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

# ADVANCED_FACE marked .F. — reversed orientation relative to surface normal.
# This is the defect carrier.
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face = f._emit_raw(
    f"ADVANCED_FACE('sliver_flipped_face',(#{fob.eid}),#{plane.eid},.F.)"
)

shell = f._emit_raw(f"OPEN_SHELL('shell',(#{face.eid}))")
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)

# Add PMI: catalog narrative is GD&T on the sliver face.
f._emit_raw("DATUM_FEATURE('sliver_datum','sliver face datum','',#9005)")
f._emit_raw("GEOMETRIC_TOLERANCE('gt_sliver','0.05 mm flatness on sliver',#9009,#9005)")
