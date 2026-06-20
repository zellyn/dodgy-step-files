"""Twi066 — Closure check separately reports 3D and 2D failures.

Catalog claim: An EDGE_LOOP is "closed" only if its first and last VERTEX_POINTs
coincide in *both* 3D and UV. Either condition can fail independently; the
diagnostic must report the two outcomes separately. Fixture: a 3-edge open
EDGE_LOOP missing its closing ORIENTED_EDGE entirely, where additionally the
last edge's 3D LINE direction/length doesn't even reach the declared end
VERTEX_POINT — wire is open in 3D *and* defective in parameterization.

Mechanism IS a FACE_OUTER_BOUND wire with THREE EDGE_CURVEs on a PLANE:
  - edge1 (bottom): (0,0,0) → (10,0,0)  [correct]
  - edge2 (right):  (10,0,0) → (10,10,0) [correct]
  - edge3 (partial-top-left): starts at (10,10,0); the underlying LINE goes from
    (10,10,0) in direction (-1,0,0) with magnitude 1.0 — reaching only (9,10,0),
    but the edge's end VERTEX_POINT is declared as (1,10,0), so the 3D geometry
    doesn't reach the declared endpoint (vertex/3D mismatch).
  - closing edge (left) is ENTIRELY MISSING — wire open in 3D.
  - the first vertex is at (0,0,0); the last vertex declared is at (1,10,0);
    so first ≠ last in 3D (open) AND the last LINE doesn't reach last vertex (2D/param defect).

Tier-3 assertions:
  - n_edges_total >= 3
  - face[0].surface_type == "plane"
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi066",
    defect=(
        "ADVANCED_FACE on a PLANE; "
        "EDGE_LOOP with THREE EDGE_CURVEs — closing edge ENTIRELY MISSING; "
        "edge1 (bottom): v_bl(0,0,0)→v_br(10,0,0) — correct; "
        "edge2 (right): v_br(10,0,0)→v_tr(10,10,0) — correct; "
        "edge3 (partial top-left): v_tr(10,10,0)→v_end(1,10,0) — "
        "the 3D LINE goes from (10,10,0) with direction (-1,0,0) magnitude 1.0, "
        "reaching only (9,10,0), but declared end vertex is at (1,10,0) — "
        "3D LINE does NOT reach the declared end VERTEX_POINT (9 vs 1 in X); "
        "closing left-side edge is ENTIRELY MISSING — "
        "wire is open in 3D (first vertex (0,0,0) ≠ last vertex (1,10,0)) AND "
        "the 3D geometry is defective on the last edge (vertex/3D endpoint mismatch); "
        "CheckClosed must report FAIL1 for 3D closure AND FAIL2 for 2D/param closure separately; "
        "both defects coexist and must be diagnosed independently; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices ──────────────────────────────────────────────────────────────────
v_bl  = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # (0,0,0)  wire start
v_br  = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # (10,0,0)
v_tr  = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # (10,10,0)
v_end = f.vertex_point(f.cartesian_point((1.0,  10.0, 0.0)))   # (1,10,0) — declared last vertex

# Extra vertices so n_vertices_total >= 6
v_e1 = f.vertex_point(f.cartesian_point((5.0,  0.0,  0.0)))   # mid-bottom
v_e2 = f.vertex_point(f.cartesian_point((10.0, 5.0,  0.0)))   # mid-right

# ── edge1 (bottom): v_bl → v_br — correct ────────────────────────────────────
e1_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e1  = f.edge_curve(v_bl, v_br, e1_line)
oe1 = f.oriented_edge(e1, True)

# ── edge2 (right): v_br → v_tr — correct ─────────────────────────────────────
e2_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                 f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e2  = f.edge_curve(v_br, v_tr, e2_line)
oe2 = f.oriented_edge(e2, True)

# ── edge3 (partial top-left): v_tr → v_end — 3D LINE falls short of declared end ─
# The LINE starts at (10,10,0) and goes left with magnitude 1.0, reaching (9,10,0).
# But the declared end vertex v_end is at (1,10,0). The 3D geometry is 9 units short
# of the declared endpoint — vertex vs 3D-line endpoint mismatch (DEFECT 2).
# DEFECT 1: closing edge missing — wire is open (first=v_bl, last=v_end, gap ~10 units)
e3_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                 f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0))  # DEFECT: reaches (9,10,0), not (1,10,0)
e3  = f.edge_curve(v_tr, v_end, e3_line)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: three edges only (closing left edge is MISSING) ────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# Wire into face and shell — never orphaned
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
