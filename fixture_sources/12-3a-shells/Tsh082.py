"""Tsh082 — RemoveLocations stale-location reference during traversal.

Catalog claim: shell has multiple faces with different local placement
transforms; ShapeUpgrade_RemoveLocations removes a transform during
traversal but a downstream face/edge observes stale cached location.

Previous fixture declared `FILE_SCHEMA(('IFC2X3'))` — STEP AP214 parser
rejects on header. Regen with the builder's default AUTOMOTIVE_DESIGN
schema and two faces with distinct AXIS2_PLACEMENT_3D origins.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh082",
             defect="two faces with distinct placements (RemoveLocations target)")

# Common axis directions.
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))

# Face A: 1x1 square at origin.
plc_a = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), zdir, xdir)
plane_a = f.plane(plc_a)
pa = [f.cartesian_point(p) for p in [(0,0,0),(1,0,0),(1,1,0),(0,1,0)]]
va = [f.vertex_point(p) for p in pa]

def line_edge(p, dir_tuple, length, vstart, vend):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(vstart, vend, ln)

ea = [
    line_edge(pa[0], (1.0, 0.0, 0.0), 1.0, va[0], va[1]),
    line_edge(pa[1], (0.0, 1.0, 0.0), 1.0, va[1], va[2]),
    line_edge(pa[2], (-1.0, 0.0, 0.0), 1.0, va[2], va[3]),
    line_edge(pa[3], (0.0, -1.0, 0.0), 1.0, va[3], va[0]),
]
loop_a = f.edge_loop([f.oriented_edge(e, True) for e in ea])
face_a = f.advanced_face([f.face_outer_bound(loop_a)], plane_a)

# Face B: 1x1 square translated to (1, 1, 0) under a non-identity placement.
plc_b = f.axis2_placement_3d(f.cartesian_point((1.0, 1.0, 0.0)), zdir, xdir)
plane_b = f.plane(plc_b)
pb = [f.cartesian_point(p) for p in [(1,1,0),(2,1,0),(2,2,0),(1,2,0)]]
vb = [f.vertex_point(p) for p in pb]
eb = [
    line_edge(pb[0], (1.0, 0.0, 0.0), 1.0, vb[0], vb[1]),
    line_edge(pb[1], (0.0, 1.0, 0.0), 1.0, vb[1], vb[2]),
    line_edge(pb[2], (-1.0, 0.0, 0.0), 1.0, vb[2], vb[3]),
    line_edge(pb[3], (0.0, -1.0, 0.0), 1.0, vb[3], vb[0]),
]
loop_b = f.edge_loop([f.oriented_edge(e, True) for e in eb])
face_b = f.advanced_face([f.face_outer_bound(loop_b)], plane_b)

shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
