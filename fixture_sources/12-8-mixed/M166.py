"""M166 — Heatsink-style fin array crashes export pipeline at faceted sub-shape boundary.

Catalog claim: a fin-array geometry (many parallel thin plates) crashes
the export pipeline when crossing a faceted-to-BRep boundary. The
catalog points at FreeCAD#18524 where the VRML exporter crashes on a
heatsink model.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 20 thin
fin rectangles arranged in parallel, each as an ADVANCED_FACE on the
same plane (or near-parallel planes), demonstrating the fin-array
pattern.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="M166",
             defect="20 thin parallel fin ADVANCED_FACEs (heatsink array)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

NUM_FINS = 20
FIN_WIDTH = 0.5   # thin fin
FIN_HEIGHT = 10.0 # tall fin
FIN_SPACING = 2.0

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
for k in range(NUM_FINS):
    x_start = k * FIN_SPACING
    p0 = f.cartesian_point((x_start, 0.0, 0.0))
    p1 = f.cartesian_point((x_start + FIN_WIDTH, 0.0, 0.0))
    p2 = f.cartesian_point((x_start + FIN_WIDTH, FIN_HEIGHT, 0.0))
    p3 = f.cartesian_point((x_start, FIN_HEIGHT, 0.0))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    e0 = line_edge(p0, (1.0, 0.0, 0.0), FIN_WIDTH, v0, v1)
    e1 = line_edge(p1, (0.0, 1.0, 0.0), FIN_HEIGHT, v1, v2)
    e2 = line_edge(p2, (-1.0, 0.0, 0.0), FIN_WIDTH, v2, v3)
    e3 = line_edge(p3, (0.0, -1.0, 0.0), FIN_HEIGHT, v3, v0)
    loop = f.edge_loop([
        f.oriented_edge(e0, True), f.oriented_edge(e1, True),
        f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    ])
    faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

shell = f.open_shell(faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
