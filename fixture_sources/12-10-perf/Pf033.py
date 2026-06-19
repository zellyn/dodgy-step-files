"""Pf033 — Long-running mesh on STEP file load (5k faces, auto-mesh quadratic).

Catalog claim: a reader is configured to compute incremental BRep mesh
during STEP load. The mesh step has worst-case quadratic behaviour on
files with many small faces; minutes-long load on shells with thousands
of faces.

Previous fixture used 12 empty-EDGE_LOOP placeholders. Regen: 144 (12×12)
real small quad ADVANCED_FACEs in ONE CLOSED_SHELL. Production-scale is
~5,000, but 144 is enough to demonstrate the pattern without bloating
the corpus.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf033",
             defect="many small ADVANCED_FACEs in single CLOSED_SHELL (auto-mesh O(n²))")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

N = 12   # 12x12 = 144 faces

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
SMALL = 0.1   # small face size — exercises sub-tessellation budget
for i in range(N):
    for j in range(N):
        x = i * SMALL
        y = j * SMALL
        p0 = f.cartesian_point((x, y, 0.0))
        p1 = f.cartesian_point((x + SMALL, y, 0.0))
        p2 = f.cartesian_point((x + SMALL, y + SMALL, 0.0))
        p3 = f.cartesian_point((x, y + SMALL, 0.0))
        v0 = f.vertex_point(p0)
        v1 = f.vertex_point(p1)
        v2 = f.vertex_point(p2)
        v3 = f.vertex_point(p3)
        e0 = line_edge(p0, (1.0, 0.0, 0.0), SMALL, v0, v1)
        e1 = line_edge(p1, (0.0, 1.0, 0.0), SMALL, v1, v2)
        e2 = line_edge(p2, (-1.0, 0.0, 0.0), SMALL, v2, v3)
        e3 = line_edge(p3, (0.0, -1.0, 0.0), SMALL, v3, v0)
        loop = f.edge_loop([
            f.oriented_edge(e0, True), f.oriented_edge(e1, True),
            f.oriented_edge(e2, True), f.oriented_edge(e3, True),
        ])
        faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

shell = f._emit_raw(
    f"CLOSED_SHELL('auto_mesh_target',({','.join(f'#{x.eid}' for x in faces)}))"
)
brep = f._emit_raw(f"MANIFOLD_SOLID_BREP('many_small_faces',#{shell.eid})")
f.add_product_chain(brep)
