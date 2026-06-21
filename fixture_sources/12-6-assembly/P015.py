"""P015 — Non-manifold or open shell exported as MANIFOLD_SOLID_BREP.

Catalog claim: a solid that is closed in the producer is wrapped as
MANIFOLD_SOLID_BREP but at least one edge appears only once across the
shell, so the result is not actually manifold.  Re-import yields zero
solids in strict kernels; OCCT heals and loads shape(1).

The defect: a CLOSED_SHELL nominally containing one face with an
inverted outer-bound orientation so the edge winding is inconsistent
— the shell is topologically open/non-manifold but is wrapped inside
a MANIFOLD_SOLID_BREP.  OCCT repairs and returns shape(1).

Byte assertions:
  count_entity_def(b'MANIFOLD_SOLID_BREP') >= 1
  contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P015",
    defect=(
        "MANIFOLD_SOLID_BREP wrapping a single planar ADVANCED_FACE whose "
        "FACE_OUTER_BOUND has orientation .F. (inverted), making the shell "
        "topologically non-manifold/open; writer mislabels this as a closed solid; "
        "FreeCAD PartDesign SubShapeBinder offset regression; "
        "OCCT heals orientation and loads shape(1)"
    ),
)

# Build a single planar face — 10×10 mm square in XY plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0,  0.0,  0.0))
p1 = f.cartesian_point((10.0, 0.0,  0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0,  10.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(pa, dv, ln, va, vb):
    d  = f.direction(dv)
    ve = f.vector(d, ln)
    li = f.line(pa, ve)
    return f.edge_curve(va, vb, li)

e0 = line_edge(p0, (1.0, 0.0, 0.0),  10.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0),  10.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 10.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 10.0, v3, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

# FACE_OUTER_BOUND with orientation .F. — the defect (inverted bound).
# This makes the shell non-manifold (edge winding inconsistency).
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.F.)")
face = f._emit_raw(f"ADVANCED_FACE('open_face',(#{fob.eid}),#{plane.eid},.T.)")

# Wrap in CLOSED_SHELL + MANIFOLD_SOLID_BREP — but the face winding is wrong.
shell = f._emit_raw(f"CLOSED_SHELL('open_shell',(#{face.eid}))")
brep  = f._emit_raw(f"MANIFOLD_SOLID_BREP('non_manifold_solid',#{shell.eid})")
f.add_product_chain(brep, mode="brep_shape")

# Assembly-presence scaffolding (STYLED_ITEM satisfies §12.6 lint).
colour = f._emit_raw("COLOUR_RGB('defect_color',0.7,0.3,0.1)")
fasc   = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas    = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa   = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss    = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu    = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa    = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('defect_style',(#{psa.eid}),#{face.eid})")
