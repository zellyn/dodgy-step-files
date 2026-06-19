"""Pf017 — ShapeFix_Shape multi-pass healing hang on huge single-shell input.

Catalog claim: STEP importer hangs and consumes huge memory during
import-time ShapeFix_Shape::Perform on one big shell — each pass exposes
another defect that requires further iteration, the loop is unbounded
(OCCT #417 / Mantis 32127).

Previous fixture used 16 ADVANCED_FACEs all pointing at the same empty
EDGE_LOOP, which is structurally pathological in a different way (empty
loop, not multi-pass-hang). Regen: a 7×7 grid of small quad faces packed
into ONE CLOSED_SHELL, each face's vertices offset by sub-tolerance
amounts so the healer's gap-close pass uncovers a sliver pass which
uncovers a self-intersect pass, etc.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf017",
             defect="huge single-shell ShapeFix multi-pass divergence")

# Grid carrier plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

N = 7   # 7x7 = 49 faces in ONE shell
EPS = 1e-7   # sub-tolerance gap pattern

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
for i in range(N):
    for j in range(N):
        # 1×1 quad at (i, j); each vertex coord offset by a tiny eps in a
        # pattern that varies with (i, j) so neighbouring quads' shared
        # vertices don't quite line up — the gap-close pass uncovers it.
        delta_x = EPS * ((i + j) % 3)
        delta_y = EPS * ((i * j) % 3)
        x = float(i) + delta_x
        y = float(j) + delta_y
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

# All 49 faces in ONE closed shell — the multi-pass divergence pattern.
shell = f._emit_raw(
    f"CLOSED_SHELL('huge_grid_shell',({','.join(f'#{x.eid}' for x in faces)}))"
)
mssb = f._emit_raw(
    f"MANIFOLD_SOLID_BREP('huge_brep',#{shell.eid})"
)
f.add_product_chain(mssb)
