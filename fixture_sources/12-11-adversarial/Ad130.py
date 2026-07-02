r"""Ad130 — `PRESENTATION_LAYER_ASSIGNMENT` with a null (`$`) item in `assigned_items`.

Catalog claim: STEP AP214 file with a valid cube `MANIFOLD_SOLID_BREP` (six planar
faces) and a `PRESENTATION_LAYER_ASSIGNMENT` whose `assigned_items` list contains
a `$` (null) entry alongside valid `STYLED_ITEM` references. Prior to OCCT commit
96049f2e3d7de177d89f89231e44e9d7d105ae43 (layer-visibility null-item crash fix)
OCCT dereferences the null pointer during layer resolution and segfaults; the
post-fix build handles the null entry gracefully and assigns only the non-null
items to the layer.

Source: https://github.com/Open-Cascade-SAS/OCCT/commit/96049f2e3d7de177d89f89231e44e9d7d105ae43
(referenced by OCCT MANTIS 0032049 layer-visibility + null-item crash). B4 wave-7
DEF-LL. LGPL-clean — pattern only, no upstream bytes copied.

Mechanism: `PRESENTATION_LAYER_ASSIGNMENT('layer_ad130','',(#s1,$,#s2))` — the
middle element of the `assigned_items` set is literally `$` (STEP null). OCCT
pre-fix pipes this through `TCollection_HAsciiString` resolution without a null
check; post-fix skips the null with a diagnostic.

Byte assertions:
  contains(b'PRESENTATION_LAYER_ASSIGNMENT')
  contains(b'STYLED_ITEM')
  matches(rb"PRESENTATION_LAYER_ASSIGNMENT\('[^']*','[^']*',\(#\d+,\$,#\d+\)\)")
Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad130",
    defect=(
        "PRESENTATION_LAYER_ASSIGNMENT('layer_ad130','',(#styled1,$,#styled2)) — "
        "the middle element of assigned_items is literally $ (STEP null) alongside "
        "two valid STYLED_ITEM references; valid cube MANIFOLD_SOLID_BREP as the "
        "carrier geometry; OCCT prior to commit 96049f2e (MANTIS 0032049 layer "
        "null-item fix) dereferences the null pointer during layer resolution and "
        "segfaults; post-fix OCCT skips the null entry gracefully and assigns only "
        "the two non-null STYLED_ITEMs to the layer; DEF-LL; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC (post-fix) yields shape(1)"
    ),
)

# ── Minimal cube MANIFOLD_SOLID_BREP (10×10×10) — carrier geometry ────────────
def make_plane_face(origin, zdir_t, xdir_t, points_ccw):
    plc   = f.axis2_placement_3d(
        f.cartesian_point(origin),
        f.direction(zdir_t),
        f.direction(xdir_t),
    )
    plane = f.plane(plc)
    pts   = [f.cartesian_point(p) for p in points_ccw]
    loop  = f.closed_polyline_loop(pts)
    fob   = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane)

S = 10.0

face_xp = make_plane_face((S,0,0), (1,0,0), (0,0,1),
                           [(S,0,0),(S,0,S),(S,S,S),(S,S,0)])
face_xn = make_plane_face((0,0,0), (-1,0,0), (0,0,-1),
                           [(0,0,0),(0,S,0),(0,S,S),(0,0,S)])
face_yp = make_plane_face((0,S,0), (0,1,0), (S,0,0),
                           [(0,S,0),(S,S,0),(S,S,S),(0,S,S)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,S),(S,0,S),(S,0,0)])
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ad130_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ad130_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── Two valid STYLED_ITEM references + colour + presentation-style chain ──────
# Each STYLED_ITEM references one face of the cube (face_xp and face_yp) so the
# layer would legitimately assign to real geometry — the middle $ is the defect.
colour_red   = f._emit_raw("COLOUR_RGB('red',1.0,0.0,0.0)")
colour_blue  = f._emit_raw("COLOUR_RGB('blue',0.0,0.0,1.0)")

# SURFACE_STYLE_FILL_AREA → FILL_AREA_STYLE → FILL_AREA_STYLE_COLOUR chain
fasc_red     = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour_red.eid})")
fas_red      = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc_red.eid}))")
ssf_red      = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas_red.eid})")
ssu_red      = f._emit_raw(
    f"SURFACE_SIDE_STYLE('',(#{ssf_red.eid}))"
)
ssbc_red     = f._emit_raw(
    f"SURFACE_STYLE_USAGE(.BOTH.,#{ssu_red.eid})"
)
psa_red      = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{ssbc_red.eid}))"
)

fasc_blue    = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour_blue.eid})")
fas_blue     = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc_blue.eid}))")
ssf_blue     = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas_blue.eid})")
ssu_blue     = f._emit_raw(
    f"SURFACE_SIDE_STYLE('',(#{ssf_blue.eid}))"
)
ssbc_blue    = f._emit_raw(
    f"SURFACE_STYLE_USAGE(.BOTH.,#{ssu_blue.eid})"
)
psa_blue     = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{ssbc_blue.eid}))"
)

# STYLED_ITEM entities — the two valid entries for the layer assignment.
# Byte assertion: contains(b'STYLED_ITEM')
styled_1 = f._emit_raw(
    f"STYLED_ITEM('face_xp_style',(#{psa_red.eid}),#{face_xp.eid})"
)
styled_2 = f._emit_raw(
    f"STYLED_ITEM('face_yp_style',(#{psa_blue.eid}),#{face_yp.eid})"
)

# ── DEFECT: PRESENTATION_LAYER_ASSIGNMENT with null ($) in assigned_items ─────
# The middle element of the (STYLED_ITEM,$,STYLED_ITEM) set is the STEP null.
# Byte assertion: contains(b'PRESENTATION_LAYER_ASSIGNMENT')
# Byte assertion: matches(rb"PRESENTATION_LAYER_ASSIGNMENT\('[^']*','[^']*',\(#\d+,\$,#\d+\)\)")
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('layer_ad130',"
    f"'layer with null middle item — OCCT pre-fix 96049f2 segfaults',"
    f"(#{styled_1.eid},$,#{styled_2.eid}))"
)
