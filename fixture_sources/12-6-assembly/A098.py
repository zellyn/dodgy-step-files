"""A098 — Writer-emitted STEP cannot be re-imported (round-trip refused).

Catalog claim: SHAPE_REPRESENTATION at #10 references entities via forward
references only; a build-N reader has a regression in its forward-reference
resolver and silently imports empty. bytes SHAPE_REPRESENTATION and
regex #10=SHAPE_REPRESENTATION must match.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A098",
             defect="SHAPE_REPRESENTATION at #10 with all-forward refs — build-N reader silently drops on re-import (self-roundtrip regression)")

# We need exactly 9 entities (#1–#9) before SHAPE_REPRESENTATION at #10.
# All references from #10 point to entities emitted after it (#11+) —
# pure forward references that a defective reader cannot resolve.

# Entities #1–#9: dummy cartesian points (fillers).
for i in range(9):
    f._emit_raw(f"CARTESIAN_POINT('filler_{i}',(0.0,0.0,{float(i)}))")
# _next_id is now 10.

# #10: SHAPE_REPRESENTATION — forward-references:
#   #11 = CARTESIAN_POINT (item in the rep's items list)
#   #12 = REPRESENTATION_CONTEXT (the geom context)
sr = f._emit_raw("SHAPE_REPRESENTATION('part',(#11),#12)")
# sr.eid must be 10.

# #11: CARTESIAN_POINT (referenced forward from #10).
fwd_cp = f._emit_raw("CARTESIAN_POINT('fwd_origin',(0.0,0.0,0.0))")

# #12: REPRESENTATION_CONTEXT (referenced forward from #10).
geom_ctx = f._emit_raw("REPRESENTATION_CONTEXT('','3D')")

# Now build the rest of the model for a valid file.
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

# STYLED_ITEM scaffolding for assembly-presence lint.
colour = f._emit_raw("COLOUR_RGB('part_color',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('part_style',(#{psa.eid}),#{face.eid})")
