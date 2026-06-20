"""Tfa067 — Top face dropped after STEP import.

Catalog claim: A solid imported from STEP loses one or more faces during
translation. The face's FACE_OUTER_BOUND references an EDGE_LOOP whose edge
translation fails silently — a 3D LINE going one way while the associated
PCURVE is a degree-2 B_SPLINE_CURVE_WITH_KNOTS with control points that dip
in V, producing a 3D-curve / pcurve mismatch beyond tolerance — so the entire
face is dropped. Visible in viewers as a hole in the otherwise-solid part.

Mechanism: CLOSED_SHELL six-face cube (1x1x1) where the top face's EDGE_LOOP
has one edge with:
  - 3D LINE: (0,0,1)→(1,0,1) — straight, correct
  - PCURVE: degree-2 B_SPLINE_CURVE_WITH_KNOTS in UV with control points
    that dip 0.1 in V — the pcurve does not match the 3D LINE

face[0] = bottom (z=0, normal -Z)
face[1] = front  (y=0, normal -Y)
face[2] = right  (x=1, normal +X)
face[3] = back   (y=1, normal +Y)
face[4] = left   (x=0, normal -X)
face[5] = top    (z=1, normal +Z) — THE DEFECT FACE

Tier-3 assertions:
  n_edges_total >= 24
  face[0].surface_type == "plane"
  face[5].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(27) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa067",
    defect=(
        "CLOSED_SHELL: six-face 1x1x1 cube; "
        "top face (face[5], z=1) EDGE_LOOP front edge has "
        "3D LINE (0,0,1)→(1,0,1) but PCURVE is degree-2 B_SPLINE_CURVE_WITH_KNOTS "
        "with control points dipping 0.1 in V — 3D/pcurve mismatch ~0.1mm; "
        "STEP reader silently drops the top face; resulting shell has 5 faces; "
        "face[0].surface_type==plane (bottom), face[5].surface_type==plane (top); "
        "n_edges_total >= 24 (cube has 12 edges, each appearing in 2 faces); "
        "defect IS on live top face traversal path"
    ),
)

# ── Cube vertices ──────────────────────────────────────────────────────────────
p_bbl = f.cartesian_point((0.0, 0.0, 0.0)); p_bbr = f.cartesian_point((1.0, 0.0, 0.0))
p_btr = f.cartesian_point((1.0, 1.0, 0.0)); p_btl = f.cartesian_point((0.0, 1.0, 0.0))
p_tbl = f.cartesian_point((0.0, 0.0, 1.0)); p_tbr = f.cartesian_point((1.0, 0.0, 1.0))
p_ttr = f.cartesian_point((1.0, 1.0, 1.0)); p_ttl = f.cartesian_point((0.0, 1.0, 1.0))

v_bbl = f.vertex_point(p_bbl); v_bbr = f.vertex_point(p_bbr)
v_btr = f.vertex_point(p_btr); v_btl = f.vertex_point(p_btl)
v_tbl = f.vertex_point(p_tbl); v_tbr = f.vertex_point(p_tbr)
v_ttr = f.vertex_point(p_ttr); v_ttl = f.vertex_point(p_ttl)

# ── Bottom edges (z=0) ─────────────────────────────────────────────────────────
e_bot_front = f.edge_curve(v_bbl, v_bbr, f.line(p_bbl, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
e_bot_right = f.edge_curve(v_bbr, v_btr, f.line(p_bbr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_bot_back  = f.edge_curve(v_btr, v_btl, f.line(p_btr, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_bot_left  = f.edge_curve(v_btl, v_bbl, f.line(p_btl, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

# ── Top non-defective edges (z=1) ─────────────────────────────────────────────
e_top_right = f.edge_curve(v_tbr, v_ttr, f.line(p_tbr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_top_back  = f.edge_curve(v_ttr, v_ttl, f.line(p_ttr, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_top_left  = f.edge_curve(v_ttl, v_tbl, f.line(p_ttl, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

# ── Defective top-front edge: 3D LINE + mismatched B_SPLINE pcurve ────────────
# Top face plane: z=1, normal +Z, UV=(U,V)→(U,V,1)
top_plane_ax = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 1.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
)
top_plane = f.plane(top_plane_ax)

# 3D LINE: (0,0,1) → (1,0,1) — straight along X, correct
top_front_3d = f.line(p_tbl, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))

# PCURVE in UV: degree-2 B-spline with control points (0,0),(0.5,-0.1),(1,0)
# This dips 0.1 below V=0 at midpoint — mismatch with 3D LINE which stays at V=0
cp_pc0 = f._emit_raw("CARTESIAN_POINT('',( 0.0, 0.0))")
cp_pc1 = f._emit_raw("CARTESIAN_POINT('',( 0.5,-0.1))")   # dip — DEFECT
cp_pc2 = f._emit_raw("CARTESIAN_POINT('',( 1.0, 0.0))")

# B_SPLINE_CURVE_WITH_KNOTS: degree=2, 3 ctrl pts, knots [0,1] mults [3,3]
bspline_pc = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('',2,"
    f"(#{cp_pc0.eid},#{cp_pc1.eid},#{cp_pc2.eid}),"
    ".UNSPECIFIED.,.F.,.F.,"
    "(3,3),(0.,1.),.UNSPECIFIED.)"
)

# 2D definitional representation
geom_ctx_2d = f._emit_raw("GEOMETRIC_REPRESENTATION_CONTEXT(2)")
pc_defrep   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{bspline_pc.eid}),#{geom_ctx_2d.eid})"
)
top_front_pcurve = f._emit_raw(
    f"PCURVE('',#{top_plane.eid},#{pc_defrep.eid})"
)

# SURFACE_CURVE: 3D LINE (correct) + B_SPLINE pcurve (dipped, mismatch)
top_front_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{top_front_3d.eid},(#{top_front_pcurve.eid}),.PCURVE_S1.)"
)
e_top_front = f._emit_raw(
    f"EDGE_CURVE('top_front_defect',#{v_tbl.eid},#{v_tbr.eid},#{top_front_sc.eid},.T.)"
)

# ── Vertical edges ─────────────────────────────────────────────────────────────
e_vert_bbl = f.edge_curve(v_bbl, v_tbl, f.line(p_bbl, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
e_vert_bbr = f.edge_curve(v_bbr, v_tbr, f.line(p_bbr, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
e_vert_btr = f.edge_curve(v_btr, v_ttr, f.line(p_btr, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
e_vert_btl = f.edge_curve(v_btl, v_ttl, f.line(p_btl, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))

# ── face[0]: bottom (z=0, normal -Z) ──────────────────────────────────────────
loop0 = f.edge_loop([
    f.oriented_edge(e_bot_front, True),
    f.oriented_edge(e_bot_right, True),
    f.oriented_edge(e_bot_back,  True),
    f.oriented_edge(e_bot_left,  True),
])
face0 = f.advanced_face([f.face_outer_bound(loop0)], f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)), f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
)))

# ── face[1]: front (y=0, normal -Y) ───────────────────────────────────────────
# Edges: bot_front fwd, vert_bbr fwd, top_front rev (defect edge), vert_bbl rev
oe_f1_top = f._emit_raw(
    f"ORIENTED_EDGE('',*,*,#{e_top_front.eid},.F.)"
)
loop1 = f.edge_loop([
    f.oriented_edge(e_bot_front,  True),
    f.oriented_edge(e_vert_bbr,   True),
    oe_f1_top,
    f.oriented_edge(e_vert_bbl,   False),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)), f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0))
)))

# ── face[2]: right (x=1, normal +X) ───────────────────────────────────────────
loop2 = f.edge_loop([
    f.oriented_edge(e_bot_right,  True),
    f.oriented_edge(e_vert_btr,   True),
    f.oriented_edge(e_top_right,  False),
    f.oriented_edge(e_vert_bbr,   False),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], f.plane(f.axis2_placement_3d(
    f.cartesian_point((1.0, 0.0, 0.0)), f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0))
)))

# ── face[3]: back (y=1, normal +Y) ────────────────────────────────────────────
loop3 = f.edge_loop([
    f.oriented_edge(e_bot_back,   True),
    f.oriented_edge(e_vert_btl,   True),
    f.oriented_edge(e_top_back,   False),
    f.oriented_edge(e_vert_btr,   False),
])
face3 = f.advanced_face([f.face_outer_bound(loop3)], f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 1.0, 0.0)), f.direction((0.0, 1.0, 0.0)), f.direction((-1.0, 0.0, 0.0))
)))

# ── face[4]: left (x=0, normal -X) ───────────────────────────────────────────
loop4 = f.edge_loop([
    f.oriented_edge(e_bot_left,   True),
    f.oriented_edge(e_vert_bbl,   True),
    f.oriented_edge(e_top_left,   False),
    f.oriented_edge(e_vert_btl,   False),
])
face4 = f.advanced_face([f.face_outer_bound(loop4)], f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)), f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, -1.0, 0.0))
)))

# ── face[5]: top (z=1, normal +Z) — THE DEFECT FACE ──────────────────────────
# Front edge uses the defective SURFACE_CURVE (3D LINE + dipped B-spline pcurve)
oe_top_front_fwd = f._emit_raw(
    f"ORIENTED_EDGE('',*,*,#{e_top_front.eid},.T.)"
)
loop5 = f.edge_loop([
    oe_top_front_fwd,
    f.oriented_edge(e_top_right,  True),
    f.oriented_edge(e_top_back,   True),
    f.oriented_edge(e_top_left,   True),
])
fob5  = f.face_outer_bound(loop5)
face5 = f._emit_raw(
    f"ADVANCED_FACE('top_defect_face',(#{fob5.eid}),#{top_plane.eid},.T.)"
)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
all_faces = [face0.eid, face1.eid, face2.eid, face3.eid, face4.eid, face5.eid]
cs_refs   = ",".join(f"#{eid}" for eid in all_faces)
closed_sh = f._emit_raw(f"CLOSED_SHELL('',({cs_refs}))")
msb       = f._emit_raw(f"MANIFOLD_SOLID_BREP('',#{closed_sh.eid})")
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa067.stp")
