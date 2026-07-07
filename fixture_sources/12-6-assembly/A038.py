"""A038 — Constructive Geometry Representation Relationship — assembly axis placements.

Catalog claim: AP242 files use inch units for AXIS2_PLACEMENT_3D inside
CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP; the unit is not applied
to the placements, mis-positioning every component.
'CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP' must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A038",
             defect="CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP with inch-unit axis placements (unit not applied)",
             schema="AP242")

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

# Sub-component NAUO for assembly presence.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9054,#{sub_pdef.eid},$)"
)

# Construction geometry context — inch-unit (not applied to placements).
inch_unit = f._emit_raw(
    "(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.INCH.,.METRE.))"
)
cgr_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{inch_unit.eid}))"
    f"REPRESENTATION_CONTEXT('cgr_inch','3D'))"
)

# Axis placement encoded in inch context (value 1.0 inch ≈ 25.4mm, but unit not applied).
cgr_origin = f._emit_raw("CARTESIAN_POINT('cgr_pt',(1.0,0.0,0.0))")
cgr_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
cgr_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
cgr_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('cgr_axis',#{cgr_origin.eid},#{cgr_z.eid},#{cgr_x.eid})"
)

# CONSTRUCTIVE_GEOMETRY_REPRESENTATION with the inch axis.
cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('cgr',(#{cgr_plc.eid}),#{cgr_ctx.eid})"
)

# CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP linking to main shape_rep.
f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP('cgr_rel','cgr',#{cgr.eid},#9060)"
)
