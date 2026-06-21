"""P023 — Mixed FACE_OUTER_BOUND orientation flag (negative-volume pocket).

Catalog claim: a MANIFOLD_SOLID_BREP where some FACE_OUTER_BOUND has
orientation .F. (false) on a small subset of faces while surface normals
are otherwise consistent → reader interprets as inverted pocket (negative
volume).

The defect: 2-face shell with MANIFOLD_SOLID_BREP — face 0 has a correct
FACE_OUTER_BOUND (.T.), face 1 has a FACE_OUTER_BOUND with orientation .F.
(inverted).  Mixed .T./.F. orientation flags create a pocket/negative-volume
interpretation.  OCCT heals and loads shape(1).

Byte assertions:
  count_entity_def(b'MANIFOLD_SOLID_BREP') >= 1
  matches(rb'FACE_OUTER_BOUND.*\\.F\\.')

Tier-3 assertion: n_faces_total == 2

Expected: occt=shape(1)/shape(1) gmsh=shape(2) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P023",
    defect=(
        "MANIFOLD_SOLID_BREP with 2 ADVANCED_FACEs: face 0 has FACE_OUTER_BOUND(.T.) "
        "but face 1 has FACE_OUTER_BOUND(.F.) — mixed orientation flags produce "
        "inverted-pocket / negative-volume interpretation; "
        "FreeCAD #10736 mixed outer-loop orientation on pocket; "
        "OCCT heals mixed flags and loads shape(1)"
    ),
)

# Shared planar surface for both faces (XY plane).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def square_loop(x0, y0, size):
    """Return an edge_loop for an axis-aligned square."""
    p0 = f.cartesian_point((x0,          y0,          0.0))
    p1 = f.cartesian_point((x0 + size,   y0,          0.0))
    p2 = f.cartesian_point((x0 + size,   y0 + size,   0.0))
    p3 = f.cartesian_point((x0,          y0 + size,   0.0))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    def le(pa, dv, va, vb):
        d  = f.direction(dv)
        ve = f.vector(d, size)
        li = f.line(pa, ve)
        return f.edge_curve(va, vb, li)
    e0 = le(p0, (1.0,  0.0, 0.0), v0, v1)
    e1 = le(p1, (0.0,  1.0, 0.0), v1, v2)
    e2 = le(p2, (-1.0, 0.0, 0.0), v2, v3)
    e3 = le(p3, (0.0, -1.0, 0.0), v3, v0)
    return f.edge_loop([
        f.oriented_edge(e0, True), f.oriented_edge(e1, True),
        f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    ])

# Face 0: 10×10 mm square at (0,0) — correct orientation (.T.).
loop0 = square_loop(0.0, 0.0, 10.0)
fob0  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop0.eid},.T.)")
face0 = f._emit_raw(f"ADVANCED_FACE('face_correct',(#{fob0.eid}),#{plane.eid},.T.)")

# Face 1: 10×10 mm square at (15,0) — inverted orientation (.F.) — the defect.
loop1 = square_loop(15.0, 0.0, 10.0)
fob1  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop1.eid},.F.)")
face1 = f._emit_raw(f"ADVANCED_FACE('face_inverted',(#{fob1.eid}),#{plane.eid},.T.)")

# Wrap both faces in CLOSED_SHELL + MANIFOLD_SOLID_BREP.
shell = f._emit_raw(f"CLOSED_SHELL('mixed_orient_shell',(#{face0.eid},#{face1.eid}))")
brep  = f._emit_raw(f"MANIFOLD_SOLID_BREP('mixed_orient_solid',#{shell.eid})")
f.add_product_chain(brep, mode="brep_shape")

# Assembly-presence scaffolding (STYLED_ITEM + COLOUR_RGB satisfies §12.6 lint).
colour = f._emit_raw("COLOUR_RGB('pocket_color',0.9,0.5,0.1)")
fasc   = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas    = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa   = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss    = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu    = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa    = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('pocket_style',(#{psa.eid}),#{face0.eid})")
