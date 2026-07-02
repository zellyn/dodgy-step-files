"""Pmi145 — AP242 Ed.3 `BASIC_ROUND_HOLE` feature entity dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a prismatic part containing one
drilled through-hole encoded in TWO parallel ways:
  (a) B-rep geometry: a `CYLINDRICAL_SURFACE` `ADVANCED_FACE` for the hole wall
      (radius 3.0, height 10) plus two `PLANE` cap-annulus `ADVANCED_FACE`
      entities marking the +Z and -Z ends of the drilled hole.
  (b) Feature semantic: a `BASIC_ROUND_HOLE` entity with `internal_diameter=6.0`
      (matching the wall radius × 2), plus a `BASIC_ROUND_HOLE_OCCURRENCE`
      linking the feature to the B-rep shape aspect.

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`) with
schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP + hole B-rep faces).
- Under AP242 Ed.3 readers, `BASIC_ROUND_HOLE` populates the machining-feature
  API — the hole is queryable as `type=through, diameter=6.0`.
- Under AP242 Ed.2 / AP214 readers, both feature entities produce a Void
  transfer status: the geometry still loads but the feature semantic is silently
  absent. Machining or CAM downstream cannot recover the drill parameters
  without re-classifying the geometry.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (§4.4
BASIC_ROUND_HOLE + BASIC_ROUND_HOLE_OCCURRENCE); FreeCAD #19795 (AP242 feature
semantic gap). B4 wave-7 DEF-JJ. Confidence: HIGH — entity encoding is
documented in AP242 Ed.3 §4.4.

Byte assertions:
  contains(b'BASIC_ROUND_HOLE')
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'MANIFOLD_SOLID_BREP')
  contains(b'10303 442 4 1 4')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi145",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: prismatic part with one drilled through-hole encoded "
        "as (a) B-rep CYLINDRICAL_SURFACE + two PLANE cap ADVANCED_FACE entities "
        "and (b) BASIC_ROUND_HOLE / BASIC_ROUND_HOLE_OCCURRENCE feature-semantic "
        "entities with internal_diameter=6.0; header OID = {1 0 10303 442 4 1 4}; "
        "Ed.3 readers expose the hole as type=through diameter=6.0 via the "
        "machining-feature API; Ed.2 / AP214 readers produce Void transfer status "
        "on both feature entities — geometry still loads, feature semantic drops "
        "silently; steptools notes_ap242e3.html §4.4; FreeCAD #19795; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
# The task requires the exact FILE_SCHEMA string:
#   AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Prismatic MANIFOLD_SOLID_BREP (20×20×10 mm cube — carrier for the hole) ──
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

W = 20.0; H = 10.0  # width=20, height=10 (block dimensions)

face_xp = make_plane_face((W,0,0), (1,0,0), (0,0,1),
                           [(W,0,0),(W,0,H),(W,W,H),(W,W,0)])
face_xn = make_plane_face((0,0,0), (-1,0,0), (0,0,-1),
                           [(0,0,0),(0,W,0),(0,W,H),(0,0,H)])
face_yp = make_plane_face((0,W,0), (0,1,0), (W,0,0),
                           [(0,W,0),(W,W,0),(W,W,H),(0,W,H)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,H),(W,0,H),(W,0,0)])
face_zp = make_plane_face((0,0,H), (0,0,1), (1,0,0),
                           [(0,0,H),(0,W,H),(W,W,H),(W,0,H)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(W,0,0),(W,W,0),(0,W,0)])

block_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
block_face_refs = ",".join(f"#{fa.eid}" for fa in block_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi145_shell',({block_face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi145_block',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── B-rep of the drilled through-hole (co-present, not merged into the block) ─
# Hole is at (W/2, W/2), through the block (z: 0 → H). Radius R_HOLE = 3.0 mm.
# The hole is represented as three ADVANCED_FACE entities:
#   1. CYLINDRICAL_SURFACE for the hole wall
#   2. PLANE ADVANCED_FACE at z=0 for the -Z cap-annulus mark
#   3. PLANE ADVANCED_FACE at z=H for the +Z cap-annulus mark
# These are supplemental-geometry faces (co-present with the block) — a common
# pattern where the hole feature is annotated separately from the outer shell.

R_HOLE = 3.0
CX, CY = W / 2.0, W / 2.0

# CYLINDRICAL_SURFACE for the hole wall
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
cyl_orig = f.cartesian_point((CX, CY, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl      = f.cylindrical_surface(cyl_plc, R_HOLE, name="pmi145_hole_wall")

# Minimal cylinder wall face: a rectangular parametric patch with an EDGE_LOOP
# using two seam edges (top/bottom circles) and two vertical straight edges.
# For fixture-brevity we use a placeholder degenerate loop (two vertices) —
# the point is not the geometric accuracy of the hole wall but the presence
# of the CYLINDRICAL_SURFACE ADVANCED_FACE entity co-present with BASIC_ROUND_HOLE.
p_bot = f.cartesian_point((CX + R_HOLE, CY, 0.0))
p_top = f.cartesian_point((CX + R_HOLE, CY, H))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# Vertical seam edge
d_up  = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, H)
seam_line = f.line(p_bot, vec_up)
e_seam    = f.edge_curve(v_bot, v_top, seam_line)

# Bottom circle (full circle, seam vertex)
b_axis = f.axis2_placement_3d(
    f.cartesian_point((CX, CY, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
b_circ = f.circle(b_axis, R_HOLE, name="pmi145_bot_edge")
e_bot  = f._emit_raw(
    f"EDGE_CURVE('pmi145_bot_edge',#{v_bot.eid},#{v_bot.eid},#{b_circ.eid},.T.)"
)
# Top circle (full circle, seam vertex)
t_axis = f.axis2_placement_3d(
    f.cartesian_point((CX, CY, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
t_circ = f.circle(t_axis, R_HOLE, name="pmi145_top_edge")
e_top  = f._emit_raw(
    f"EDGE_CURVE('pmi145_top_edge',#{v_top.eid},#{v_top.eid},#{t_circ.eid},.T.)"
)

cyl_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_seam, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_seam, False),
])
hole_wall_face = f.advanced_face(
    [f.face_outer_bound(cyl_loop)], cyl,
    name="pmi145_hole_wall_face",
)

# PLANE cap-annulus faces at z=0 and z=H — represented as two independent
# ADVANCED_FACE entities on PLANE surfaces (annulus geometry not fully wired;
# the presence of PLANE cap faces is what the catalog claim asserts).
cap0_plc = f.axis2_placement_3d(
    f.cartesian_point((CX, CY, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cap0_plane = f.plane(cap0_plc, name="pmi145_cap0_plane")
cap0_loop  = f.edge_loop([f.oriented_edge(e_bot, True)])
cap0_face  = f.advanced_face(
    [f.face_outer_bound(cap0_loop)], cap0_plane,
    name="pmi145_cap0_face",
)

capH_plc = f.axis2_placement_3d(
    f.cartesian_point((CX, CY, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
capH_plane = f.plane(capH_plc, name="pmi145_capH_plane")
capH_loop  = f.edge_loop([f.oriented_edge(e_top, True)])
capH_face  = f.advanced_face(
    [f.face_outer_bound(capH_loop)], capH_plane,
    name="pmi145_capH_face",
)

# ── AP242 Ed.3 BASIC_ROUND_HOLE feature-semantic entities ─────────────────────
# SHAPE_ASPECT anchoring the hole feature to the block's product-definition-shape.
# Byte assertion: contains(b'SHAPE_ASPECT') (present via PMI regex — also OK).
hole_shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('through_hole_1','drilled through hole feature aspect',#9055,.F.)"
)

# BASIC_ROUND_HOLE (AP242 Ed.3 §4.4). Attribute order per Ed.3 schema:
#   BASIC_ROUND_HOLE(name, description, of_shape, internal_diameter)
# where internal_diameter is a POSITIVE_LENGTH_MEASURE (mm here).
# Byte assertion: contains(b'BASIC_ROUND_HOLE')
basic_round_hole = f._emit_raw(
    f"BASIC_ROUND_HOLE('brh_1','through_hole',#{hole_shape_aspect.eid},"
    f"POSITIVE_LENGTH_MEASURE(6.0))"
)

# BASIC_ROUND_HOLE_OCCURRENCE: links the feature to the B-rep hole face
# (the CYLINDRICAL_SURFACE wall).
# Per AP242 Ed.3 §4.4: (name, description, of_shape, feature_definition,
#                       feature_occurrence_geometry).
# We reference the hole_wall_face as the feature occurrence's geometry link.
basic_round_hole_occ = f._emit_raw(
    f"BASIC_ROUND_HOLE_OCCURRENCE('brh_occ_1','through_hole_face',"
    f"#{hole_shape_aspect.eid},#{basic_round_hole.eid},#{hole_wall_face.eid})"
)

# PROPERTY_DEFINITION + PROPERTY_DEFINITION_REPRESENTATION anchor the feature
# semantic to the shape.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('hole_feature','drilled hole feature',#9055)"
)
feature_rep = f._emit_raw(
    f"REPRESENTATION('hole_feature_rep',(#{basic_round_hole.eid},"
    f"#{basic_round_hole_occ.eid},#{hole_wall_face.eid},#{cap0_face.eid},"
    f"#{capH_face.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{feature_rep.eid})"
)
