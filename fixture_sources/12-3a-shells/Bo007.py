"""Bo007 — A face appears twice in the same shell.

Catalog claim: A CLOSED_SHELL references the same ADVANCED_FACE entity in its
cfs_faces list twice. Shell topology is over-counted.

Mechanism IS the CLOSED_SHELL face-list topology: a single ADVANCED_FACE entity
reference appears twice in the CLOSED_SHELL's cfs_faces IS the defect. The
duplicate reference IS wired directly into the closed-shell entity. BRepCheck
fires SubshapeNotInShape after dedup.

Tier-3 assertions: face[0].surface_type == "plane", n_edges_total >= 4
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo007",
    defect=(
        "CLOSED_SHELL cfs_faces lists the same ADVANCED_FACE entity twice; "
        "duplicate face reference IS wired into closed-shell face-list topology; "
        "BRepCheck fires SubshapeNotInShape"
    ),
)

# ── Build one planar square face ──────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0)); p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def mk_edge(va, vb, p_start, dx, dy, length):
    d = f.direction((dx, dy, 0.0)); v = f.vector(d, length)
    return f.edge_curve(va, vb, f.line(p_start, v))

e0 = mk_edge(v0, v1, p0,  1,  0, 1.0)
e1 = mk_edge(v1, v2, p1,  0,  1, 1.0)
e2 = mk_edge(v2, v3, p2, -1,  0, 1.0)
e3 = mk_edge(v3, v0, p3,  0, -1, 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)

# ── CATALOG MECHANISM: same face entity referenced twice in CLOSED_SHELL ──────
# Byte assertion: contains(b'CLOSED_SHELL')
# Byte assertion: contains(b'ADVANCED_FACE')
# The duplicate reference IS the defect — wired directly into cfs_faces.
shell = f._emit_raw(
    f"CLOSED_SHELL('bo007_duplicate_face',(#{face.eid},#{face.eid}))"
)
msb = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo007_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
