"""Ad055 — Stack overflow when meshing TBB pool from STEP import.

Catalog claim: huge faces-per-shell counts overflow the meshing thread
pool's stack. The fixture's job is to look like a "many-faces-per-shell"
producer.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 144 (12×12)
real quad faces in ONE CLOSED_SHELL.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad055",
             defect="144 ADVANCED_FACEs in single CLOSED_SHELL (TBB stack overflow)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

N = 12

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
for i in range(N):
    for j in range(N):
        x = float(i)
        y = float(j)
        p0 = f.cartesian_point((x, y, 0.0))
        p1 = f.cartesian_point((x + 1.0, y, 0.0))
        p2 = f.cartesian_point((x + 1.0, y + 1.0, 0.0))
        p3 = f.cartesian_point((x, y + 1.0, 0.0))
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
        faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

shell = f._emit_raw(
    f"CLOSED_SHELL('tbb_stack_target',({','.join(f'#{x.eid}' for x in faces)}))"
)
brep = f._emit_raw(f"MANIFOLD_SOLID_BREP('huge_brep',#{shell.eid})")
f.add_product_chain(brep)
