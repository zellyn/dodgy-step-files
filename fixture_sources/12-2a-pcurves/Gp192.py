"""Gp192 — Pcurve range straddles a U-periodic surface's seam in the wrong
order (w1>w2), forcing ElCLib::AdjustPeriodic re-basing (stp-pcurve-trim-
range-repair, PARTIAL, missing subvariant (b): "a pcurve range that
straddles a U-periodic surface's seam in the wrong order (w1>w2), forcing
ElCLib::AdjustPeriodic re-basing").

Catalog claim: CheckPCurves (StepToTopoDS_TranslateEdgeLoop.cxx:155-163)
detects when a pcurve's declared 2D parameter range has w1>w2 on a
U-periodic surface and re-bases it via ElCLib::AdjustPeriodic, rather than
accepting the range literally (which would describe a backward/negative-
length span). Gp007/Gn019/Gs007/Gp028 present out-of-bounds and periodic-
BAND mismatches but none presents a literal w1>w2 declared-backward range
on a genuinely U-periodic surface.

Mechanism: a CYLINDRICAL_SURFACE (genuinely U-periodic in OCCT
regardless of any STEP-level "closed" declaration -- U naturally wraps
at 2*pi) hosts a quarter-turn arc edge, 'wrong_order_pcurve_edge', whose
declared PCURVE 2D LINE runs from (1.5*pi, 0) to (0.5*pi, 0) -- i.e. its
own u1=4.712 is greater than its own u2=1.571 (backward order), even
though the edge's 3D CIRCLE arc geometry genuinely spans a positive
quarter-turn from angle 1.5*pi to 2.0*pi (going the FORWARD/increasing
direction through the surface's own u=0/u=2*pi seam) -- so the pcurve's
own declared endpoints, read literally, both contradict the 3D traversal
direction AND are in the wrong (w1>w2) order for the healer to trust
without re-basing through AdjustPeriodic. ADVANCED_FACE -> OPEN_SHELL ->
SHELL_BASED_SURFACE_MODEL -> PRODUCT chain; never orphaned.

Byte assertions:
  - contains(b'wrong_order_pcurve_edge')
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1

Tier-3 assertions:
  - face[0].surface_type == "cylinder"

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
(live-verified: reads without crashing, brepcheck.valid=True; edge[0]'s 3D
curve range/length matches the genuine quarter-turn arc -- the wrong-order
pcurve declaration does not corrupt or drop the edge, consistent with
CheckPCurves re-basing the range via AdjustPeriodic rather than either
accepting it literally (which would be non-physical) or rejecting the
edge outright.)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp192",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CYLINDRICAL_SURFACE "
        "(radius 1, axis +Z, genuinely U-periodic in OCCT); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with one EDGE_CURVE "
        "'wrong_order_pcurve_edge': a quarter-turn CIRCLE arc from angle "
        "1.5*pi to 2.0*pi at z=0 (real, positive-length 3D geometry), "
        "wrapped in a SURFACE_CURVE whose SOLE PCURVE is a 2D LINE "
        "declared from (1.5*pi,0) to (0.5*pi,0) -- u1=4.712 > u2=1.571, "
        "the WRONG order for a forward-traversing pcurve on this "
        "U-periodic surface; CheckPCurves' w1>w2 -> ElCLib::AdjustPeriodic "
        "re-basing branch IS the mechanism; EDGE_LOOP IS wired into "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)

R = 1.0

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},{R:.10f})")

ANG0 = 1.5 * math.pi
ANG1 = 2.0 * math.pi

p0 = (R * math.cos(ANG0), R * math.sin(ANG0), 0.0)
p1 = (R * math.cos(ANG1), R * math.sin(ANG1), 0.0)
v0 = f.vertex_point(f.cartesian_point(p0))
v1 = f.vertex_point(f.cartesian_point(p1))

# 3D CIRCLE arc geometry (real, positive quarter-turn, angle 1.5pi -> 2pi)
circ_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), cyl_zdir, cyl_xdir)
circ3d = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},{R:.10f})")

# Wrong-order PCURVE: declared u1=1.5pi > u2=0.5pi (backward order, also
# contradicts the true 3D endpoints angle-wise once periodicity is folded in).
pc_start = f.cartesian_point((ANG0, 0.0))
pc_dir = f.direction((-1.0, 0.0))  # pointing toward decreasing u
pc_vec = f.vector(pc_dir, ANG0 - 0.5 * math.pi)
pc_line = f._emit_raw(f"LINE('',#{pc_start.eid},#{pc_vec.eid})")
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
drep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

surf_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{circ3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('wrong_order_pcurve_edge',#{v0.eid},#{v1.eid},#{surf_curve.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
