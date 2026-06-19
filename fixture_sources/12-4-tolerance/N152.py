"""N152 — BRepBuilderAPI_Sewing.SameParameterEdge location-transform-in-tolerance-eval.

Catalog claim: SameParameterEdge must transform the surface by its TopLoc_Location
before D0 evaluation in tolerance computation; omitting the transform yields a
false tolerance against an untransformed surface.

Demonstration: provide two planar faces — one at origin, one at AXIS2_PLACEMENT_3D
translated +100 mm in Y — with edges along the shared boundary. The runtime
SameParameterEdge call exercises the asymmetric eval; this fixture's job is to
deliver a clean sewing-pair scaffold the kernel can load.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N152",
             defect="location-transform-in-tolerance-eval (sewing pair)")

# Face A: plane at origin.
orig_a = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_a = f.axis2_placement_3d(orig_a, zdir, xdir)
plane_a = f.plane(plc_a)

# Boundary of face A: 2x2 square in XY at z=0.
pa = [f.cartesian_point(p) for p in [(0,0,0),(2,0,0),(2,2,0),(0,2,0)]]
va = [f.vertex_point(p) for p in pa]
def line_edge(p, dir_tuple, length, v_start, v_end):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(v_start, v_end, ln)
ea = [
    line_edge(pa[0], (1,0,0), 2.0, va[0], va[1]),
    line_edge(pa[1], (0,1,0), 2.0, va[1], va[2]),
    line_edge(pa[2], (-1,0,0), 2.0, va[2], va[3]),
    line_edge(pa[3], (0,-1,0), 2.0, va[3], va[0]),
]
loop_a = f.edge_loop([f.oriented_edge(e, True) for e in ea])
face_a = f.advanced_face([f.face_outer_bound(loop_a)], plane_a)

# Face B: plane on a placement translated +100 mm in Y.
orig_b = f.cartesian_point((0.0, 100.0, 0.0))
plc_b = f.axis2_placement_3d(orig_b, zdir, xdir)
plane_b = f.plane(plc_b)

pb = [f.cartesian_point(p) for p in [(0,100,0),(2,100,0),(2,102,0),(0,102,0)]]
vb = [f.vertex_point(p) for p in pb]
eb = [
    line_edge(pb[0], (1,0,0), 2.0, vb[0], vb[1]),
    line_edge(pb[1], (0,1,0), 2.0, vb[1], vb[2]),
    line_edge(pb[2], (-1,0,0), 2.0, vb[2], vb[3]),
    line_edge(pb[3], (0,-1,0), 2.0, vb[3], vb[0]),
]
loop_b = f.edge_loop([f.oriented_edge(e, True) for e in eb])
face_b = f.advanced_face([f.face_outer_bound(loop_b)], plane_b)

# Both faces in one open shell — the kernel sees this as a sewing-pair candidate.
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
