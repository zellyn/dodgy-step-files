"""A003 — Empty / phantom assembly nodes (PRODUCT_DEFINITION with no shape).

Catalog claim: a NEXT_ASSEMBLY_USAGE_OCCURRENCE references a
PRODUCT_DEFINITION whose SHAPE_DEFINITION_REPRESENTATION points at an
empty MANIFOLD_SURFACE_SHAPE_REPRESENTATION (no faces, no axes).
The sub-component entity is named 'PHANTOM_INSTANCE'.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A003",
             defect="NAUO -> PD whose MANIFOLD_SURFACE_SHAPE_REPRESENTATION is empty (PHANTOM_INSTANCE)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

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
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")

# Phantom sub-component — its MANIFOLD_SURFACE_SHAPE_REPRESENTATION is empty.
phantom_prod = f._emit_raw(
    f"PRODUCT('PHANTOM_INSTANCE','PHANTOM_INSTANCE','',(#{sub_pdc.eid}))"
)
phantom_pdf = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{phantom_prod.eid})"
)
phantom_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{phantom_pdf.eid},#9003)"
)
phantom_pds = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{phantom_pdef.eid})"
)

# Empty MANIFOLD_SURFACE_SHAPE_REPRESENTATION — no items, no geometry.
empty_mssr = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('phantom_rep',(),#9010)"
)
f._emit_raw(
    f"SHAPE_DEFINITION_REPRESENTATION(#{phantom_pds.eid},#{empty_mssr.eid})"
)

# Single NAUO referencing the phantom product definition.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','phantom_node','',#9004,#{phantom_pdef.eid},$)"
)
