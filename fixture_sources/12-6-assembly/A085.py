"""A085 — STEP exporter loses COMPSOLID in nonmanifold writes.

Catalog claim: a COMPSOLID (cellular solid, multiple cells sharing
faces) cannot be expressed natively in AP203/AP214 and the writer's
fallback is to write each cell as a separate solid. In nonmanifold
mode the writer should emit shared faces with proper non-manifold
markers.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 2 cells
sharing a common face — the cellular-solid pattern. Emit one
NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION pointing at the shared
shell.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A085",
             defect="2 cells sharing a face + NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build a face shared by 2 conceptual cells.
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
shared_face = f._emit_raw(
    f"ADVANCED_FACE('shared_face',(#{f.face_outer_bound(loop).eid}),"
    f"#{plane.eid},.T.)"
)

# Two cells (open shells) sharing the same face — the cellular pattern.
shell_cell1 = f.open_shell([shared_face])
shell_cell2 = f.open_shell([shared_face])
sbsm = f.shell_based_surface_model([shell_cell1, shell_cell2])
f.add_product_chain(sbsm)

# Explicit NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION pointing at both
# cells — the nonmanifold-write trigger.
f._emit_raw(
    f"NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION('nmssr_cells',"
    f"(#{shell_cell1.eid},#{shell_cell2.eid}),$)"
)

# Catalog byte assertion expects >= 2 MANIFOLD_SOLID_BREP entries —
# each cell as a separate brep (the writer's fallback for COMPSOLID).
closed1 = f._emit_raw(f"CLOSED_SHELL('cell1_closed',(#{shared_face.eid}))")
closed2 = f._emit_raw(f"CLOSED_SHELL('cell2_closed',(#{shared_face.eid}))")
f._emit_raw(f"MANIFOLD_SOLID_BREP('cell1_brep',#{closed1.eid})")
f._emit_raw(f"MANIFOLD_SOLID_BREP('cell2_brep',#{closed2.eid})")
