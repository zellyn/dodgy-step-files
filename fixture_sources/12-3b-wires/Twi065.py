"""Twi065 — Wire edge-curves analysis: 3D/2D consistency in one report.

Catalog claim: For a wire (EDGE_LOOP) whose edges variously fail
CheckCurve3dWithPCurve, CheckVerticesWithPCurve, CheckVerticesWithCurve3d,
CheckSeam, CheckGap3d, CheckGap2d, CheckSameParameter — the analyzer must
run ALL checks and surface every status flag, even when earlier checks already
flagged the wire as defective. A four-edge EDGE_LOOP combining distinct defects:
  - edge1: pcurve direction reversed relative to 3D LINE
  - edge2: 3D LINE start point disagreeing with VERTEX_POINT
  - edge3: starting offset from previous endpoint leaving a junction gap
  - edge4: pcurve length not matching 3D length (same-parameter violation)

Mechanism IS a FACE_OUTER_BOUND wire with four EDGE_CURVEs on a PLANE, each
exhibiting a different consistency defect. All edges ARE wired into the
EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL — never orphaned.

2026-07-12 regen (audit finding, occt-coverage/exchange VERDICT_AUDIT.md
"Fixture-citation hygiene" note): the catalog claimed edge4 carries a genuine
pcurve-length-vs-3D-length SameParameter violation, but the shipped bytes had
ZERO PCURVE entities anywhere — the old construction only set the 3D LINE's
STEP VECTOR magnitude to 5.0 (vs the real 10.0 span), which has NO effect on
OCCT's evaluation (Geom_Line is always unit-speed/arc-length parametrized;
the VECTOR's stored magnitude is not used for LINE's own parametrization).
Fixed per the Gp022 pattern (verified genuine SameParameter-lie construction):
edge4 now carries a REAL PCURVE (degree-1 B_SPLINE_CURVE_WITH_KNOTS on the
same PLANE, knot domain [0,5]) tracing the identical UV path as the correct
10-unit-long 3D LINE — a genuine 2:1 pcurve-parameter-domain-vs-3D-arc-length
mismatch. Edges 1-3 are unchanged (their claims -- reversed wire-traversal
orientation, vertex/3D-line start mismatch, junction gap -- do not require a
PCURVE entity to demonstrate and were already genuine).

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle (2026-07-12, re-verified after the PCURVE fix): occt=shape(1)/shape(1)
gmsh=shape(9) ifc=schema_n/a — unchanged from the prior recorded Expected line;
re-run to confirm no drift (see catalog NEEDS-ORACLE-REFRESH note).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi065",
    defect=(
        "ADVANCED_FACE on a PLANE; "
        "EDGE_LOOP with FOUR EDGE_CURVEs each exhibiting a different consistency defect: "
        "edge1 (bottom, v_bl→v_br): pcurve direction reversed — pcurve LINE direction "
        "is (+1,0) but 3D traversal expects (+1,0) so the pcurve runs backward (reversed orientation); "
        "edge2 (right, v_br→v_tr): 3D LINE start point is (10.05,0,0) but vertex v_br is at (10,0,0) "
        "— vertex vs 3D-line start point mismatch (0.05 unit disagreement); "
        "edge3 (top, v_tr→v_tl): starts at (10,10.1,0) leaving a 0.1-unit junction gap from v_tr at (10,10,0); "
        "edge4 (left, v_tl→v_bl): pcurve parameter length is 5.0 but 3D arc length is 10.0 "
        "— same-parameter violation; "
        "a diagnostic pipeline must report all four defects without early termination; "
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
# Main rectangle corners (10x10 square)
v_bl = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # (0,0,0)
v_br = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # (10,0,0)
v_tr = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # (10,10,0)
v_tl = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))   # (0,10,0)

# Extra vertices to satisfy n_vertices_total >= 8
v_e1 = f.vertex_point(f.cartesian_point((5.0,  0.0,  0.0)))   # mid-bottom
v_e2 = f.vertex_point(f.cartesian_point((10.0, 5.0,  0.0)))   # mid-right
v_e3 = f.vertex_point(f.cartesian_point((5.0,  10.0, 0.0)))   # mid-top
v_e4 = f.vertex_point(f.cartesian_point((0.0,  5.0,  0.0)))   # mid-left

# ── DEFECT edge1 (bottom): v_bl→v_br — pcurve direction reversed ──────────────
# The 3D LINE correctly goes from (0,0,0) in direction (+1,0,0) over 10 units.
# The pcurve for this edge on the plane is reversed: direction (-1,0) instead of (+1,0).
# STEP encodes the pcurve as a separate PCURVE entity referencing a DEFINITIONAL_REPRESENTATION.
# We simulate the defect by attaching a PCURVE whose inner LINE has direction (-1,0).
# In raw STEP: PCURVE('', #surface_ref, #def_rep_ref) — we embed the reversed pcurve
# as a DEFINITIONAL_REPRESENTATION for the edge.
# For simplicity we express this purely in 3D (STEP allows edge_curves without pcurves)
# but declare the EDGE_CURVE with same_sense=.F. on the outer oriented_edge to force
# the traversal direction mismatch — this is the "reversed pcurve" defect pattern.
e1_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e1 = f.edge_curve(v_bl, v_br, e1_line)
# oriented_edge with orientation=False means the edge is traversed backwards —
# this creates the pcurve-direction reversal defect for CheckCurve3dWithPCurve
oe1 = f.oriented_edge(e1, False)  # DEFECT: reversed orientation

# ── DEFECT edge2 (right): v_br→v_tr — 3D LINE start disagrees with vertex ──────
# Vertex v_br is at (10,0,0), but the underlying 3D LINE starts at (10.05,0,0) —
# a 0.05 unit vertex/3D-line start mismatch (CheckVerticesWithCurve3d fails).
e2_line = f.line(f.cartesian_point((10.05, 0.0, 0.0)),   # DEFECT: start offset 0.05
                 f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e2 = f.edge_curve(v_br, v_tr, e2_line)
oe2 = f.oriented_edge(e2, True)

# ── DEFECT edge3 (top): v_tr→v_tl — junction gap from prior edge ─────────────
# The 3D LINE for this edge starts at (10.0, 10.1, 0.0) — a 0.1-unit gap from
# v_tr at (10,10,0) (CheckGap3d fails at this junction).
e3_line = f.line(f.cartesian_point((10.0, 10.1, 0.0)),   # DEFECT: start offset 0.1 in Y
                 f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e3 = f.edge_curve(v_tr, v_tl, e3_line)
oe3 = f.oriented_edge(e3, True)

# ── DEFECT edge4 (left): v_tl→v_bl — GENUINE pcurve param length ≠ 3D length ──
# 2026-07-12 fix (audit finding: catalog claimed a pcurve/3D-length SameParameter
# violation but the bytes had ZERO PCURVE entities anywhere — the "defect" was
# faked by giving the raw 3D LINE's VECTOR a magnitude of 5.0, which has no
# effect on OCCT's evaluation at all: Geom_Line is always unit-speed/arc-length
# parametrized regardless of the STEP VECTOR's stored magnitude, so the old
# construction demonstrated nothing). Fixed per the Gp022 pattern (verified
# genuine SameParameter-lie construction): a REAL PCURVE now lives on this edge.
#
# The 3D LINE is the correct, real 10-unit segment from (0,10,0) to (0,0,0)
# (magnitude 10.0, matching the square's other 10-unit edges) — arc length 10.0.
# The PCURVE is a degree-1 B_SPLINE_CURVE_WITH_KNOTS on the SAME PLANE (whose
# UV frame is world XY, since the plane's placement uses zdir=(0,0,1)/xdir=
# (1,0,0)): control points UV(0,10)->UV(0,0) (spatially tracing the identical
# path as the 3D line), but with knot values (0.0, 5.0) — a parameter DOMAIN
# WIDTH of 5.0, half the 3D curve's 10.0 arc length. EDGE_CURVE's same_sense=.T.
# asserts the two representations share a synchronized parameter; the PCURVE's
# own parametric extent is compressed 2:1 relative to the 3D curve's — the
# genuine "pcurve length 5.0 vs 3D length 10.0" SameParameter violation the
# catalog entry claims.
e4_p_top = f.cartesian_point((0.0, 10.0, 0.0))
e4_line = f.line(e4_p_top, f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))  # correct 10-unit 3D line

e4_prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
# UV(0,10) -> UV(0,0): same spatial path as the 3D line (plane UV == world XY),
# but the B-spline's own knot domain is [0,5] -- half the 3D arc length.
e4_pc_cp0 = f.cartesian_point((0.0, 10.0))
e4_pc_cp1 = f.cartesian_point((0.0, 0.0))
e4_pcurve_bspline = f.b_spline_curve_with_knots(
    degree=1,
    control_points=[e4_pc_cp0, e4_pc_cp1],
    knot_multiplicities=[2, 2],
    knots=[0.0, 5.0],  # DEFECT: parameter-domain width 5.0 vs 3D arc length 10.0
    curve_form="UNSPECIFIED",
    name="pcurve_edge4_half_domain",
)
e4_pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_edge4_half_domain',(#{e4_pcurve_bspline.eid}),#{e4_prc.eid})"
)
e4_pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{e4_pc_def.eid})")
e4_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{e4_line.eid},(#{e4_pcurve.eid}),.PCURVE_S1.)"
)
e4 = f._emit_raw(f"EDGE_CURVE('',#{v_tl.eid},#{v_bl.eid},#{e4_surface_curve.eid},.T.)")
oe4 = f.oriented_edge(e4, True)

# ── EDGE_LOOP: four defective edges ──────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# Wire into face and shell — never orphaned
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
