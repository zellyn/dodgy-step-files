"""P019 — Default-emitted full transparency renders objects invisible.

Catalog claim: STEP files written with
SURFACE_STYLE_RENDERING_WITH_PROPERTIES(.. transparency = 1.0 ..) for every
face — even when the producer treated this as "not specified" — render as
wireframe / invisible in viewers that honor transparency.

The defect: every ADVANCED_FACE carries a STYLED_ITEM whose
SURFACE_STYLE_RENDERING_WITH_PROPERTIES has transparency=1.0. A viewer that
honours transparency renders all objects as invisible. The receiver should
warn when an all-transparent file is improbable and default transparency to 0.

Byte assertions:
  contains(b'SURFACE_STYLE_RENDERING_WITH_PROPERTIES') or contains(b'transparency')
  contains(b'COLOUR_RGB')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P019",
    defect=(
        "Every face styled with SURFACE_STYLE_RENDERING_WITH_PROPERTIES "
        "transparency=1.0 (fully transparent, i.e. invisible); "
        "COLOUR_RGB gives an apparent fill colour but transparency overrides it; "
        "viewer honouring transparency renders all geometry as invisible wireframe; "
        "receiver must warn 'all-transparent file improbable' and default to 0; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Build a small quad face to attach styling to ─────────────────────────────
face_orig = f._emit_raw("CARTESIAN_POINT('face_orig',(0.0,0.0,0.0))")
face_z = f._emit_raw("DIRECTION('face_z',(0.0,0.0,1.0))")
face_x = f._emit_raw("DIRECTION('face_x',(1.0,0.0,0.0))")
face_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('face_plc',#{face_orig.eid},#{face_z.eid},#{face_x.eid})"
)
plane = f._emit_raw(f"PLANE('xy_plane',#{face_plc.eid})")

p0 = f._emit_raw("CARTESIAN_POINT('p0',(0.0,0.0,0.0))")
p1 = f._emit_raw("CARTESIAN_POINT('p1',(1.0,0.0,0.0))")
p2 = f._emit_raw("CARTESIAN_POINT('p2',(1.0,1.0,0.0))")
p3 = f._emit_raw("CARTESIAN_POINT('p3',(0.0,1.0,0.0))")
v0 = f._emit_raw(f"VERTEX_POINT('v0',#{p0.eid})")
v1 = f._emit_raw(f"VERTEX_POINT('v1',#{p1.eid})")
v2 = f._emit_raw(f"VERTEX_POINT('v2',#{p2.eid})")
v3 = f._emit_raw(f"VERTEX_POINT('v3',#{p3.eid})")

d0 = f._emit_raw("DIRECTION('d0',(1.0,0.0,0.0))")
vec0 = f._emit_raw(f"VECTOR('',#{d0.eid},1.0)")
line0 = f._emit_raw(f"LINE('',#{p0.eid},#{vec0.eid})")
e0 = f._emit_raw(
    f"EDGE_CURVE('e0',#{v0.eid},#{v1.eid},#{line0.eid},.T.)"
)

d1 = f._emit_raw("DIRECTION('d1',(0.0,1.0,0.0))")
vec1 = f._emit_raw(f"VECTOR('',#{d1.eid},1.0)")
line1 = f._emit_raw(f"LINE('',#{p1.eid},#{vec1.eid})")
e1 = f._emit_raw(
    f"EDGE_CURVE('e1',#{v1.eid},#{v2.eid},#{line1.eid},.T.)"
)

d2 = f._emit_raw("DIRECTION('d2',(-1.0,0.0,0.0))")
vec2 = f._emit_raw(f"VECTOR('',#{d2.eid},1.0)")
line2 = f._emit_raw(f"LINE('',#{p2.eid},#{vec2.eid})")
e2 = f._emit_raw(
    f"EDGE_CURVE('e2',#{v2.eid},#{v3.eid},#{line2.eid},.T.)"
)

d3 = f._emit_raw("DIRECTION('d3',(0.0,-1.0,0.0))")
vec3 = f._emit_raw(f"VECTOR('',#{d3.eid},1.0)")
line3 = f._emit_raw(f"LINE('',#{p3.eid},#{vec3.eid})")
e3 = f._emit_raw(
    f"EDGE_CURVE('e3',#{v3.eid},#{v0.eid},#{line3.eid},.T.)"
)

oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face = f._emit_raw(
    f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)"
)

# ── Full-transparency styling: SURFACE_STYLE_RENDERING_WITH_PROPERTIES ────────
# COLOUR_RGB satisfies the second byte assertion.
colour = f._emit_raw("COLOUR_RGB('default_colour',0.8,0.8,0.8)")

# SURFACE_STYLE_TRANSPARENT(1.0): fully transparent — the defect value.
# Byte assertion: contains(b'transparency') satisfied by the entity name below
# and/or the field label in SURFACE_STYLE_RENDERING_WITH_PROPERTIES.
full_transp = f._emit_raw("SURFACE_STYLE_TRANSPARENT(1.0)")

# SURFACE_STYLE_RENDERING_WITH_PROPERTIES: wraps colour + transparency=1.0.
# Byte assertion: contains(b'SURFACE_STYLE_RENDERING_WITH_PROPERTIES').
rend = f._emit_raw(
    f"SURFACE_STYLE_RENDERING_WITH_PROPERTIES("
    f".NORMAL_SHADING.,#{colour.eid},(#{full_transp.eid}))"
)

# Wire up the style chain.
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('full_transparent_style',(#{rend.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")

# STYLED_ITEM attaches the fully-transparent style to the face.
f._emit_raw(f"STYLED_ITEM('invisible_face_style',(#{psa.eid}),#{face.eid})")

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('FullTranspComp','FullTranspComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','full_transp_instance','',#9004,#{sub_pdef.eid},$)"
)
