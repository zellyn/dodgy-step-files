"""A081 — Material attribute overridden by generic colour on round-trip.

Catalog claim: face has both a colour and a richer material record with
reflectance/shininess; on re-import the colour overrides the material.
The bytes SURFACE_STYLE_REFLECTANCE_AMBIENT and COLOUR_RGB must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A081",
             defect="SURFACE_STYLE_REFLECTANCE_AMBIENT + COLOUR_RGB — colour record overrides material on re-import")

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

# Rich material record with reflectance/shininess — the high-fidelity data
# that should be preferred over the plain colour on re-import.
colour = f._emit_raw("COLOUR_RGB('steel_color',0.7,0.7,0.8)")
ambient = f._emit_raw(f"SURFACE_STYLE_REFLECTANCE_AMBIENT(0.3)")
specular = f._emit_raw(f"SURFACE_STYLE_SPECULAR_COLOUR(0.8,#{colour.eid})")
rend = f._emit_raw(
    f"SURFACE_STYLE_RENDERING_WITH_PROPERTIES(.NORMAL_SHADING.,#{colour.eid},(#{ambient.eid},#{specular.eid}))"
)
sss_mat = f._emit_raw(f"SURFACE_SIDE_STYLE('mat_style',(#{rend.eid}))")
ssu_mat = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss_mat.eid})")
psa_mat = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu_mat.eid}))")
f._emit_raw(f"STYLED_ITEM('material_style',(#{psa_mat.eid}),#{face.eid})")

# Plain colour record — the "first wins" reader wrongly picks this over
# the richer material record above.
plain_colour = f._emit_raw("COLOUR_RGB('plain_steel',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{plain_colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss2 = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu2 = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss2.eid})")
psa2 = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu2.eid}))")
f._emit_raw(f"STYLED_ITEM('colour_style',(#{psa2.eid}),#{face.eid})")
