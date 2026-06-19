"""Pf028 — Rhino joins > 10k face polysurfaces in O(n²).

Catalog claim: very large solids (> 10 000 faces) take O(n²) time to
join in Rhino. The fixture scales-up demo: 100 quad faces packed into
ONE OPEN_SHELL — large enough to demonstrate the pattern, small enough
to keep the fixture file reasonable. Production scaling would replicate
to 10k+ faces.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 100 real
quad faces in ONE OPEN_SHELL.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf028",
             defect="100-face OPEN_SHELL stand-in for Rhino > 10k face O(n²) join")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

N = 10   # 10x10 = 100 quad faces

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
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
        v0 = f.vertex_point(p0)
        v1 = f.vertex_point(p1)
        v2 = f.vertex_point(p2)
        v3 = f.vertex_point(p3)
        e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
        e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
        e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
        e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
        loop = f.edge_loop([
            f.oriented_edge(e0, True),
            f.oriented_edge(e1, True),
            f.oriented_edge(e2, True),
            f.oriented_edge(e3, True),
        ])
        faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

shell = f._emit_raw(
    f"OPEN_SHELL('rhino_o_n2_shell',({','.join(f'#{x.eid}' for x in faces)}))"
)
sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('rhino_sbsm',(#{shell.eid}))"
)
f.add_product_chain(sbsm)
