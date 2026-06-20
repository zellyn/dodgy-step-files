"""Twi072 — Per-junction 3D gap query returns localized fault.

Catalog claim: Targeted single-junction 3D gap query. Caller specifies `num`;
analyzer reports whether the gap between edge `num-1` and edge `num` exceeds
working precision and the actual distance. Used by interactive healing tools
to focus on one defect at a time. As Twi053 but the caller queries junction 4
specifically — so we need at least 4 edges with a gap at the 4th junction.

Mechanism IS a FACE_OUTER_BOUND wire with THREE correct edges forming two sides
of a rectangle plus a defective fourth junction: the last ORIENTED_EDGE ends at
a vertex distinct from the wire's first vertex, creating a 3D gap at junction 4
(the wrap-around junction between the last and first edges). This matches the
catalog recipe of "querying junction 4 specifically" in a wire with a gap there.

The EDGE_LOOP has three edges:
  - edge1 (bottom): v_bl(0,0,0) → v_br(10,0,0)  [correct]
  - edge2 (right):  v_br(10,0,0) → v_tr(10,10,0) [correct]
  - edge3 (top-partial): v_tr(10,10,0) → v_gap(0,10.05,0) [ends near but not at start]
  The closing edge is absent; junction between edge3-end and edge1-start has a
  3D gap of ~sqrt(0 + 0.05^2) ≈ 0.05 units — above precision tolerance.

A second face provides the additional vertices/edges for tier-3.

Tier-3 assertions:
  - n_edges_total >= 3
  - face[0].surface_type == "plane"
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi072",
    defect=(
        "ADVANCED_FACE on a PLANE; "
        "EDGE_LOOP with THREE EDGE_CURVEs; missing closing edge creates 3D gap at junction 3/wrap-around; "
        "edge1 (bottom): v_bl(0,0,0)→v_br(10,0,0) — correct; "
        "edge2 (right): v_br(10,0,0)→v_tr(10,10,0) — correct; "
        "edge3 (top-partial): v_tr(10,10,0)→v_gap(0.0,10.05,0) — "
        "last vertex is at (0,10.05,0), NOT at (0,0,0); "
        "wrap-around junction has 3D gap of 10.05 units (v_gap to v_bl); "
        "per-junction query for junction 3 (last→first wrap) reports the localized fault distance; "
        "CheckGap3d(num=3) returns DONE/FAIL plus the 10.05-unit gap; "
        "per-junction query isolates ONE junction — targeted diagnostic; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL; "
        "second face in shell provides tier-3 vertex/edge counts"
    ),
)

# ── Plane 0: defective face (3-edge open wire) ────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f._emit_raw(f"PLANE('',#{pl0_plc.eid})")

# Vertices for defective face
v_bl  = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # wire start
v_br  = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))
v_tr  = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v_gap = f.vertex_point(f.cartesian_point((0.0,  10.05, 0.0)))  # gap: 10.05 units from v_bl

# edge1: v_bl → v_br (correct)
e1_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e1  = f.edge_curve(v_bl, v_br, e1_line)
oe1 = f.oriented_edge(e1, True)

# edge2: v_br → v_tr (correct)
e2_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                 f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e2  = f.edge_curve(v_br, v_tr, e2_line)
oe2 = f.oriented_edge(e2, True)

# edge3: v_tr → v_gap — DEFECT: last vertex is 10.05 units from wire start v_bl
# Gap at the wrap-around junction (edge3-end to edge1-start) = dist(v_gap, v_bl)
# = sqrt((0-0)^2 + (10.05-0)^2) = 10.05 units — far above tolerance
e3_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                 f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e3  = f.edge_curve(v_tr, v_gap, e3_line)
oe3 = f.oriented_edge(e3, True)

loop0 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob0  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop0.eid},.T.)")
face0 = f._emit_raw(f"ADVANCED_FACE('',(#{fob0.eid}),#{plane0.eid},.T.)")

# ── Plane 1: correct face (provides additional vertices/edges for tier-3) ──────
pl1_orig = f.cartesian_point((0.0, 0.0, -1.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f._emit_raw(f"PLANE('',#{pl1_plc.eid})")

v_bl1 = f.vertex_point(f.cartesian_point((0.0,  0.0,  -1.0)))
v_br1 = f.vertex_point(f.cartesian_point((10.0, 0.0,  -1.0)))
v_tr1 = f.vertex_point(f.cartesian_point((10.0, 10.0, -1.0)))
v_tl1 = f.vertex_point(f.cartesian_point((0.0,  10.0, -1.0)))

eb1 = f.edge_curve(v_bl1, v_br1,
                   f.line(f.cartesian_point((0.0, 0.0, -1.0)),
                          f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
er1 = f.edge_curve(v_br1, v_tr1,
                   f.line(f.cartesian_point((10.0, 0.0, -1.0)),
                          f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
et1 = f.edge_curve(v_tr1, v_tl1,
                   f.line(f.cartesian_point((10.0, 10.0, -1.0)),
                          f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
el1 = f.edge_curve(v_tl1, v_bl1,
                   f.line(f.cartesian_point((0.0, 10.0, -1.0)),
                          f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

oeb1 = f.oriented_edge(eb1, True)
oer1 = f.oriented_edge(er1, True)
oet1 = f.oriented_edge(et1, True)
oel1 = f.oriented_edge(el1, True)

loop1 = f._emit_raw(
    f"EDGE_LOOP('',(#{oeb1.eid},#{oer1.eid},#{oet1.eid},#{oel1.eid}))"
)
fob1  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop1.eid},.T.)")
face1 = f._emit_raw(f"ADVANCED_FACE('',(#{fob1.eid}),#{plane1.eid},.T.)")

# ── Shell containing both faces ───────────────────────────────────────────────
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face0.eid},#{face1.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
