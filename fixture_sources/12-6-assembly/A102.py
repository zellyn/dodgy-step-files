"""A102 — Cap part exports as STEP that slicers flag as damaged.

Catalog claim: 7-face shell wrapped as MANIFOLD_SOLID_BREP (should have
8 faces for closure: 4 outer-side, 4 inner-side, 1 outer-bottom, 1
inner-bottom, 1 top-rim — minus one to leave 7).

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 7 real quad
faces wrapped in MANIFOLD_SOLID_BREP — non-closed shell mistakenly
declared solid.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A102",
             defect="7-face shell wrapped as MANIFOLD_SOLID_BREP (missing closure face)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# 7 quad faces of a putative cup.
faces = []
for k in range(7):
    x = k * 1.2
    p0 = f.cartesian_point((x, 0.0, 0.0))
    p1 = f.cartesian_point((x + 1.0, 0.0, 0.0))
    p2 = f.cartesian_point((x + 1.0, 1.0, 0.0))
    p3 = f.cartesian_point((x, 1.0, 0.0))
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

# Wrap in CLOSED_SHELL + MANIFOLD_SOLID_BREP — but 7 faces isn't closed
# (Euler characteristic violation; missing 1 face).
shell = f._emit_raw(
    f"CLOSED_SHELL('non_closed_cap_shell',"
    f"({','.join(f'#{x.eid}' for x in faces)}))"
)
brep = f._emit_raw(f"MANIFOLD_SOLID_BREP('cap_open_as_solid',#{shell.eid})")
f.add_product_chain(brep)
