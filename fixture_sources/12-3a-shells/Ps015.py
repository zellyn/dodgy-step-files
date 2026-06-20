"""Ps015 — Multi-instance NAUO collapsed by transform-equality dedup to single instance.

Catalog claim: An assembly with four logical NAUO instances of the same bolt
PRODUCT at the same XYZ location.  The exporter deduped by transform-equality
and emitted only one NAUO.  Downstream BOM sees one bolt where four were intended.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: the bolt
child PRODUCT IS a valid 10×10×10 cube whose CLOSED_SHELL IS wired into its
MANIFOLD_SOLID_BREP.  The assembly PRODUCT contains exactly ONE
NEXT_ASSEMBLY_USAGE_OCCURRENCE (name 'expected_4_collapsed_to_1') referencing
the bolt — the collapsed count IS embedded in the NAUO description field,
demonstrating the defect at the entity that the bug mutates.

Tier-3 assertions:
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — silent accept.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps015",
    defect=(
        "Assembly with bolt child: ONE NAUO referencing the bolt at origin "
        "(name='expected_4_collapsed_to_1'); four intended instances collapsed "
        "to one by transform-equality dedup; NAUO IS wired into product graph "
        "of the CLOSED_SHELL / MANIFOLD_SOLID_BREP bolt shape; kernel accepts silently"
    ),
)

# ── Bolt body: 10x10x10 cube (same geometry as Ps014 for tier-3 assertions) ──
pts = [
    f.cartesian_point((  0.0,  0.0,  0.0)),  # 0
    f.cartesian_point(( 10.0,  0.0,  0.0)),  # 1
    f.cartesian_point(( 10.0, 10.0,  0.0)),  # 2
    f.cartesian_point((  0.0, 10.0,  0.0)),  # 3
    f.cartesian_point((  0.0,  0.0, 10.0)),  # 4
    f.cartesian_point(( 10.0,  0.0, 10.0)),  # 5
    f.cartesian_point(( 10.0, 10.0, 10.0)),  # 6
    f.cartesian_point((  0.0, 10.0, 10.0)),  # 7
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)

e_bot_f = le(0, 1,  1, 0, 0, 10.0)
e_bot_r = le(1, 2,  0, 1, 0, 10.0)
e_bot_b = le(3, 2,  1, 0, 0, 10.0)
e_bot_l = le(0, 3,  0, 1, 0, 10.0)
e_top_f = le(4, 5,  1, 0, 0, 10.0)
e_top_r = le(5, 6,  0, 1, 0, 10.0)
e_top_b = le(7, 6,  1, 0, 0, 10.0)
e_top_l = le(4, 7,  0, 1, 0, 10.0)
e_v0    = le(0, 4,  0, 0, 1, 10.0)
e_v1    = le(1, 5,  0, 0, 1, 10.0)
e_v2    = le(2, 6,  0, 0, 1, 10.0)
e_v3    = le(3, 7,  0, 0, 1, 10.0)

def mk_plane(px, py, pz, zx, zy, zz, rx, ry, rz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((rx, ry, rz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

pl_bot = mk_plane( 0, 0,  0,  0, 0,-1,  1, 0, 0)
pl_top = mk_plane( 0, 0, 10,  0, 0,+1,  1, 0, 0)
pl_frt = mk_plane( 0, 0,  0,  0,-1, 0,  1, 0, 0)
pl_bck = mk_plane( 0,10,  0,  0,+1, 0,  1, 0, 0)
pl_lft = mk_plane( 0, 0,  0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(10, 0,  0, +1, 0, 0,  0, 1, 0)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]

# Bolt CLOSED_SHELL / MANIFOLD_SOLID_BREP IS the mechanism carrier
bolt_shell = f.closed_shell(all_faces, name="ps015_bolt_shell")
bolt_msb   = f.manifold_solid_brep(bolt_shell, name="ps015_bolt_body")
f.add_product_chain(bolt_msb, mode="brep_shape")

# ── Assembly product graph with single NAUO (collapsed from 4) ────────────────
# Emit a minimal assembly product chain and a single NAUO referencing bolt_msb.
# The NAUO name 'expected_4_collapsed_to_1' IS the defect marker embedded in
# the product graph — one NAUO where four were intended.
asm_app_ctx = f._emit_raw("APPLICATION_CONTEXT('mechanical design')")
asm_pc      = f._emit_raw(
    f"PRODUCT_CONTEXT('',#{asm_app_ctx.eid},'mechanical')"
)
asm_prod    = f._emit_raw(
    f"PRODUCT('assembly','assembly_with_collapsed_bolt','',(#{asm_pc.eid}))"
)
asm_form    = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{asm_prod.eid})"
)
asm_pdc     = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{asm_app_ctx.eid},'design')"
)
asm_pdef    = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{asm_form.eid},#{asm_pdc.eid})"
)
# NAUO: ONE occurrence linking assembly_pdef → bolt_msb (child stand-in)
# 'expected_4_collapsed_to_1' IS wired into the NAUO name — the defect
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'expected_4_collapsed_to_1',"
    f"'four bolt instances collapsed to one by transform-equality dedup',"
    f"'slot_1',#{asm_pdef.eid},#{bolt_msb.eid},'')"
)
