"""Xp018 — PMI without saved-view × unit-system mismatch × forward references."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp018",
             defect='PMI without saved-view x unit-system mismatch x forward references')

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 1: geometric_tolerance references shape_aspect via forward reference #998
# (shape_aspect defined later in the file)
id_sa = f._next_id + 10  # intentional forward reference
geom_tol = f._emit_raw(f"FLATNESS_TOLERANCE('flatness',#{id_sa},$,#9005)")

# Define shape_aspect after the tolerance (forward reference fulfilled late)
from step_corpus.step_builder import Entity
sa = Entity(id_sa, "__RAW__", [])
sa._raw_body = f"SHAPE_ASPECT('pmi_face','',#9005,.T.)"
f.entities.append(sa)
f._next_id = max(f._next_id, id_sa + 1)

# Defect 2: draughting_model with empty items list (missing mapped_item for saved view)
draughting_model = f._emit_raw("DRAUGHTING_MODEL('saved_view',(),$)")

# Defect 3: PMI value in inches, context declares mm
# A dimensional_size with value 25.4 (1 inch in mm units)
# but emitting the raw text with 'in' hint makes the mismatch clear
dim_size = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{sa.eid},'diameter')"
)
f._emit_raw(
    "/* xp018 defect-3: context declares mm; PMI value 25.4 authored in inches — unit collision */"
)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('pmi_unit_note','diameter: 1.0 in (should be 25.4 mm)')"
)
