"""Pmi149 — AP242 Ed.3 `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY` dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 assembly file — a parent product P0
that contains a child part P1 (linked by `NEXT_ASSEMBLY_USAGE_OCCURRENCE`)
where P1 has a drilled through-hole encoded in three parallel ways:
  (a) B-rep geometry: a prismatic 20×20×10 mm `MANIFOLD_SOLID_BREP`
      (the carrier part P1) plus a co-present `CYLINDRICAL_SURFACE`
      `ADVANCED_FACE` for the hole wall (radius 3.0, height 10).
  (b) Part-level feature semantic: `BASIC_ROUND_HOLE` with
      `internal_diameter=6.0` mm (as in `Pmi145`).
  (c) Assembly-level feature semantic (Ed.3 new):
      `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY('brh_asm_occ_1',$,$,#nauo,#brh)`
      binding the hole feature to its assembly-context occurrence via
      `NEXT_ASSEMBLY_USAGE_OCCURRENCE`.

The file header declares the AP242 Ed.3 OID
(`{1 0 10303 442 4 1 4}`) with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (block MANIFOLD_SOLID_BREP + hole B-rep).
- Under AP242 Ed.3 readers, the hole is queryable at BOTH the part level
  (`BASIC_ROUND_HOLE`) and the assembly level
  (`BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY`); assembly-aware CAM tools
  can locate the hole per-instance.
- Under AP242 Ed.2 / AP214 readers, the assembly-context occurrence
  entity produces a Void transfer status — the part-level feature is
  still recoverable but the per-assembly-instance binding is silently
  absent; CAM/inspection tools can locate the hole per-part but not
  per-assembly.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY`
§4.5). B4 wave-8 DEF-UU. Confidence: MEDIUM — accept-live-oracle. Entity
signature requires AP242 Ed.3 schema for the `_IN_ASSEMBLY` subclass.

Byte assertions:
  contains(b'BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY')
  contains(b'BASIC_ROUND_HOLE')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi149",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 assembly file: parent product P0 with child part P1 linked "
        "by NEXT_ASSEMBLY_USAGE_OCCURRENCE; P1 has a drilled through-hole with "
        "(a) B-rep MANIFOLD_SOLID_BREP block + CYLINDRICAL_SURFACE hole face, "
        "(b) part-level BASIC_ROUND_HOLE (internal_diameter=6.0), and "
        "(c) assembly-level BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY binding "
        "the hole feature to the assembly-context occurrence (AP242 Ed.3 §4.5, "
        "one of 21 new Ed.3 entities); header OID = {1 0 10303 442 4 1 4}; "
        "Ed.3 readers expose the hole at both part and assembly levels; Ed.2 / "
        "AP214 readers drop the assembly-context occurrence silently — the "
        "part-level feature is recoverable but the per-assembly-instance "
        "binding is absent; edition-boundary drop; steptools notes_ap242e3.html; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Prismatic MANIFOLD_SOLID_BREP (20×20×10 mm) — carrier part P1 ─────────────
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

W = 20.0; H = 10.0

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
shell = f._emit_raw(f"CLOSED_SHELL('pmi149_shell',({block_face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi149_block',#{shell.eid})")
# add_product_chain creates the parent assembly product P0 with the block
# geometry attached (following A001's assembly-fixture pattern). The child
# sub-product P1 is emitted below as a separate PRODUCT chain that the
# NAUO references.
f.add_product_chain(msb, mode="brep_shape", product_id="Pmi149_P0_assembly")

# ── B-rep of the drilled through-hole (co-present, not merged into shell) ─────
R_HOLE = 3.0
CX, CY = W / 2.0, W / 2.0

# CYLINDRICAL_SURFACE for the hole wall
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
cyl_orig = f.cartesian_point((CX, CY, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl      = f.cylindrical_surface(cyl_plc, R_HOLE, name="pmi149_hole_wall")

# Minimal cylinder wall face (placeholder loop; the CYLINDRICAL_SURFACE entity
# and its ADVANCED_FACE presence is what the catalog claim asserts).
p_bot = f.cartesian_point((CX + R_HOLE, CY, 0.0))
p_top = f.cartesian_point((CX + R_HOLE, CY, H))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, H)
seam_line = f.line(p_bot, vec_up)
e_seam    = f.edge_curve(v_bot, v_top, seam_line)

b_axis = f.axis2_placement_3d(
    f.cartesian_point((CX, CY, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
b_circ = f.circle(b_axis, R_HOLE, name="pmi149_bot_edge")
e_bot  = f._emit_raw(
    f"EDGE_CURVE('pmi149_bot_edge',#{v_bot.eid},#{v_bot.eid},#{b_circ.eid},.T.)"
)
t_axis = f.axis2_placement_3d(
    f.cartesian_point((CX, CY, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
t_circ = f.circle(t_axis, R_HOLE, name="pmi149_top_edge")
e_top  = f._emit_raw(
    f"EDGE_CURVE('pmi149_top_edge',#{v_top.eid},#{v_top.eid},#{t_circ.eid},.T.)"
)

cyl_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_seam, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_seam, False),
])
hole_wall_face = f.advanced_face(
    [f.face_outer_bound(cyl_loop)], cyl,
    name="pmi149_hole_wall_face",
)

# ── AP242 Ed.3 part-level BASIC_ROUND_HOLE feature-semantic entity ────────────
# SHAPE_ASPECT anchoring the hole feature to the block's product-def-shape.
hole_shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('through_hole_P1','drilled through hole in P1',#9055,.F.)"
)

# BASIC_ROUND_HOLE (AP242 Ed.3 §4.4).
# Byte assertion: contains(b'BASIC_ROUND_HOLE')
basic_round_hole = f._emit_raw(
    f"BASIC_ROUND_HOLE('brh_P1','through_hole',#{hole_shape_aspect.eid},"
    f"POSITIVE_LENGTH_MEASURE(6.0))"
)

# ── Assembly wrapping: child sub-product P1 referenced by NAUO from P0 ────────
# add_product_chain (above) created P0 (assembly root) with PRODUCT_DEFINITION
# at #9054. We emit a separate P1 sub-product chain that the NAUO references
# as the child instance — mirroring §12-6-assembly/A001's NAUO pattern.

# Parent product-definition is the one add_product_chain emitted at #9054.
# Its APPLICATION_CONTEXT is #9000 (reserved by add_product_chain).
parent_pd_ref = 9054
app_ctx_ref   = 9000

# Child sub-product P1 (a separate PRODUCT that represents the "block with
# hole" instance in the assembly context; no independent geometry — the
# geometry is attached to P0 above, matching A001's pattern where sub-products
# are pure product records referenced only by NAUO/MAPPED_ITEM).
sub_pdc = f._emit_raw(f"PRODUCT_CONTEXT('sub',#{app_ctx_ref},'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('Pmi149_P1_block','Pmi149_P1_block','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})"
)
sub_pd = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)

# NEXT_ASSEMBLY_USAGE_OCCURRENCE: binds parent P0 (#9054) to child P1.
# Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_P0_P1','P0 contains P1',"
    f"'assembly',#{parent_pd_ref},#{sub_pd.eid},$)"
)

# ── AP242 Ed.3 BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY ────────────────────────
# Per AP242 Ed.3 §4.5: binds a BASIC_ROUND_HOLE to its assembly-context
# occurrence via a NEXT_ASSEMBLY_USAGE_OCCURRENCE. Attributes per Ed.3:
#   (name, description, of_shape, feature_definition, assembly_occurrence)
# where feature_definition points at the BASIC_ROUND_HOLE and
# assembly_occurrence points at the NEXT_ASSEMBLY_USAGE_OCCURRENCE.
# Byte assertion: contains(b'BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status and drop the per-assembly-instance
# binding.
brh_asm_occ = f._emit_raw(
    f"BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY('brh_asm_occ_1',$,$,"
    f"#{nauo.eid},#{basic_round_hole.eid})"
)

# ── Tie the assembly-hole chain into the product's PMI representation ─────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('assembly_hole_feature',"
    f"'BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY link',#9055)"
)
feature_rep = f._emit_raw(
    f"REPRESENTATION('assembly_hole_rep',(#{basic_round_hole.eid},"
    f"#{brh_asm_occ.eid},#{nauo.eid},#{hole_wall_face.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{feature_rep.eid})"
)
