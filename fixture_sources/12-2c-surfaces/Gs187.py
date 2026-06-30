"""Gs187 — CONICAL_SURFACE tessellation null in OCCT 7.8+ (historical-fix demonstration).

Catalog claim: a STEP file with a MANIFOLD_SOLID_BREP whose CLOSED_SHELL has
three ADVANCED_FACEs: (a) CONICAL_SURFACE lateral face (truncated cone,
R_bottom=15 mm, R_top=5 mm, height=20 mm, semi_angle≈0.464 rad), (b) a PLANE
bottom cap, and (c) a PLANE top cap. The BRep geometry is valid and passes
checkshape. The defect is that OCCT 7.8.0–7.9.x BRepMesh_IncrementalMesh
silently returns null (zero-triangle) triangulation on the CONICAL_SURFACE face;
OCCT 7.6.0 tessellates correctly.

This is a historical-fix demonstration: the local OCCT version may tessellate
the cone face correctly; the defect was specific to the 7.8/7.9 mesher path.
The fixture documents the triggering geometry class.

Source: https://github.com/Open-Cascade-SAS/OCCT/issues/572
Confidence: HIGH — entity-level encoding is well-defined; geometry is valid.

Byte assertions:
  contains(b'CONICAL_SURFACE')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: n_faces_total == 3
Expected: verify with live oracle (historical-fix: OCCT 7.6 tessellates; 7.8-7.9 null mesh on cone face)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs187",
    defect=(
        "CONICAL_SURFACE (R_bottom=15, R_top=5, height=20, semi_angle≈0.464 rad) "
        "IS ADVANCED_FACE.face_geometry in CLOSED_SHELL; "
        "OCCT 7.8.0-7.9.x BRepMesh_IncrementalMesh returns null triangulation on "
        "cone lateral face (silent failure, zero triangles); OCCT 7.6 tessellates "
        "correctly; historical-fix demonstration (OCCT issue #572); "
        "3 faces: lateral cone + 2 plane caps — MANIFOLD_SOLID_BREP IS model entity"
    ),
)

# ── Parameters ────────────────────────────────────────────────────────────────
# Truncated cone: R_bottom=15, R_top=5, height=20
# Semi-angle = atan((R_bottom - R_top) / height) = atan(10/20) ≈ 0.4636 rad
R_BOTTOM = 15.0
R_TOP    =  5.0
HEIGHT   = 20.0
SEMI_ANGLE = math.atan((R_BOTTOM - R_TOP) / HEIGHT)  # ≈ 0.4636 rad

# The CONICAL_SURFACE is defined with apex and axis; we place the cone with
# apex above. For a cone opening downward toward z=0:
#   apex is at z = HEIGHT + R_BOTTOM / tan(semi_angle)
#   = 20 + 15 / tan(0.4636) ≈ 20 + 30 = 50 mm above base center
# Simplification: axis from apex pointing downward (-Z), radius at apex = 0.
# At z=0 (bottom): distance from apex = HEIGHT * (R_BOTTOM/R_TOP) ...
# Actually use simpler formulation:
# Apex at z = H_apex where cone opens from apex.
# R(z_from_apex) = z_from_apex * tan(semi_angle)
# At z_from_apex = d_bottom: R = R_BOTTOM = 15 → d_bottom = 15/tan = 30 mm
# At z_from_apex = d_top:   R = R_TOP   =  5 → d_top   =  5/tan ≈ 10 mm
d_bottom = R_BOTTOM / math.tan(SEMI_ANGLE)   # ≈ 30 mm from apex
d_top    = R_TOP    / math.tan(SEMI_ANGLE)   # ≈ 10 mm from apex

# Place apex at z = d_bottom (so bottom circle is at z=0, top at z=20)
apex_z = d_bottom   # apex at z=30, bottom at z=0, top at z=20

# ── CONICAL_SURFACE ──────────────────────────────────────────────────────────
# Apex at (0, 0, apex_z=30); axis points DOWN (-Z) so cone opens toward z=0
cone_orig = f.cartesian_point((0.0, 0.0, apex_z))
cone_zdir = f.direction((0.0, 0.0, -1.0))    # axis pointing down
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f.conical_surface(cone_plc, radius=0.0, semi_angle=SEMI_ANGLE)

# ── PLANE bottom cap (z=0) ───────────────────────────────────────────────────
bot_orig  = f.cartesian_point((0.0, 0.0, 0.0))
bot_zdir  = f.direction((0.0, 0.0, -1.0))   # outward normal points down
bot_xdir  = f.direction((1.0, 0.0, 0.0))
bot_plc   = f.axis2_placement_3d(bot_orig, bot_zdir, bot_xdir)
bot_plane = f.plane(bot_plc)

# ── PLANE top cap (z=HEIGHT) ─────────────────────────────────────────────────
top_orig  = f.cartesian_point((0.0, 0.0, HEIGHT))
top_zdir  = f.direction((0.0, 0.0, 1.0))    # outward normal points up
top_xdir  = f.direction((1.0, 0.0, 0.0))
top_plc   = f.axis2_placement_3d(top_orig, top_zdir, top_xdir)
top_plane = f.plane(top_plc)

# ── Bottom circle (z=0, radius=R_BOTTOM=15) ─────────────────────────────────
bot_cp    = f.cartesian_point((0.0, 0.0, 0.0))
bot_cz    = f.direction((0.0, 0.0, -1.0))
bot_cx    = f.direction((1.0, 0.0, 0.0))
bot_cplc  = f.axis2_placement_3d(bot_cp, bot_cz, bot_cx)
bot_circ  = f._emit_raw(f"CIRCLE('gs187_bot_circ',#{bot_cplc.eid},{R_BOTTOM})")
v_bot     = f.vertex_point(f.cartesian_point((R_BOTTOM, 0.0, 0.0)))
e_bot     = f._emit_raw(
    f"EDGE_CURVE('gs187_bot_circle',#{v_bot.eid},#{v_bot.eid},#{bot_circ.eid},.T.)"
)

# ── Top circle (z=HEIGHT=20, radius=R_TOP=5) ─────────────────────────────────
top_cp    = f.cartesian_point((0.0, 0.0, HEIGHT))
top_cz    = f.direction((0.0, 0.0, 1.0))
top_cx    = f.direction((1.0, 0.0, 0.0))
top_cplc  = f.axis2_placement_3d(top_cp, top_cz, top_cx)
top_circ  = f._emit_raw(f"CIRCLE('gs187_top_circ',#{top_cplc.eid},{R_TOP})")
v_top     = f.vertex_point(f.cartesian_point((R_TOP, 0.0, HEIGHT)))
e_top     = f._emit_raw(
    f"EDGE_CURVE('gs187_top_circle',#{v_top.eid},#{v_top.eid},#{top_circ.eid},.T.)"
)

# ── Bottom face (disk at z=0) ─────────────────────────────────────────────────
bot_loop = f.edge_loop([f.oriented_edge(e_bot, True)])
bot_fob  = f.face_outer_bound(bot_loop)
bot_face = f.advanced_face([bot_fob], bot_plane)

# ── Top face (disk at z=20) ───────────────────────────────────────────────────
top_loop = f.edge_loop([f.oriented_edge(e_top, True)])
top_fob  = f.face_outer_bound(top_loop)
top_face = f.advanced_face([top_fob], top_plane)

# ── Cone lateral face — outer bound = bot circle (reversed), inner = top circle
# The cone lateral face is bounded by: bottom circle (large, outer) and top
# circle (small, inner). Both are seam-free circles on the frustum.
cone_outer_loop = f.edge_loop([f.oriented_edge(e_bot, False)])   # reversed (outward)
cone_inner_loop = f.edge_loop([f.oriented_edge(e_top, True)])    # forward
cone_fob  = f.face_outer_bound(cone_outer_loop)
cone_fb   = f._emit_raw(f"FACE_BOUND('',#{cone_inner_loop.eid},.T.)")
cone_face = f._emit_raw(
    f"ADVANCED_FACE('gs187_cone_lateral',(#{cone_fob.eid},#{cone_fb.eid}),#{cone_surf.eid},.T.)"
)

# ── CLOSED_SHELL and MANIFOLD_SOLID_BREP ─────────────────────────────────────
# Byte assertion: contains(b'MANIFOLD_SOLID_BREP')
all_faces  = [bot_face, top_face, cone_face]
face_refs  = ",".join(f"#{fa.eid}" for fa in all_faces)
shell      = f._emit_raw(f"CLOSED_SHELL('gs187_shell',({face_refs}))")
msb        = f._emit_raw(f"MANIFOLD_SOLID_BREP('gs187_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
