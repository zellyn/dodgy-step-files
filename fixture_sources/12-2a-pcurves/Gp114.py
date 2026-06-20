"""Gp114 — ShapeFix_Edge.FixSameParameter periodic-curve-with-non-periodic-pcurve.

Catalog claim: Closed 3D curve (circle) but pcurve is non-periodic line on plane.
FixSameParameter forces periodicity mismatch between 3D and parametric
representations.

STEP mechanism (literal):
  - PLANE Z=0 face. Defect edge via SURFACE_CURVE.
  - 3D curve: CIRCLE (inherently periodic, period 2*pi) — the closed curve.
    Wrapped in TRIMMED_CURVE to specify the arc used for this edge, with
    trim_1 and trim_2 matching the edge extent.
  - PCurve: a LINE in UV space (explicitly non-periodic). The LINE covers the
    same nominal extent in UV, but a LINE has no periodicity — its domain is
    unbounded/open, in contrast with the CIRCLE's periodic topology.
  - THE CATALOG MECHANISM: FixSameParameter compares the 3D CIRCLE (period 2*pi)
    against the non-periodic LINE pcurve. The periodicity mismatch means
    FixSameParameter cannot cleanly reparameterize the pcurve to match the
    circular parameter — it silently handles the mismatch by ignoring
    periodicity in the pcurve, producing a valid but misrepresented edge.
    OCC heals silently.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: 3D periodic CIRCLE + non-periodic LINE pcurve;
    FixSameParameter handles periodicity mismatch silently.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp114",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D TRIMMED_CURVE(CIRCLE "
        "radius=2.5 center=(2.5,0,0), trim=[pi, 2*pi] rad) — periodic closed "
        "curve; PCurve: LINE from (0,0) direction=(1,0) in UV — non-periodic "
        "open curve; FixSameParameter sees periodicity mismatch between 3D CIRCLE "
        "(period 2pi) and non-periodic LINE pcurve; silently heals mismatch; "
        "shape(1)/shape(1)"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face: a plane rectangle [0,5] x [0,2]
# Bottom edge is the defect arc; context edges are straight lines.
# Circle center at (2.5, 1.0, 0), radius 1.5; the arc at theta=0 gives
# 3D point (2.5+1.5, 1.0, 0) = (4.0, 1.0, 0) and at theta=pi/2 gives
# (2.5, 1.0+1.5, 0) = (2.5, 2.5, 0).
# We'll use a simpler arrangement: circle center (2.5, 0, 0), radius 0.5,
# arc from theta=pi to theta=0 — so start=(2.0,0,0), end=(3.0,0,0).
# This sits cleanly inside the face and gives a sensible bottom edge.
#
# Circle center: (2.5, 0.0, 0.0), radius=0.5
# theta=pi: point=(2.5-0.5, 0, 0)=(2.0, 0, 0)
# theta=0:  point=(2.5+0.5, 0, 0)=(3.0, 0, 0)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
# Arc endpoints and extra corners for a more complex layout.
# Use a simpler approach: straight lines for all 4 edges except defect.
# v_a=(0,0,0), v_b=(5,0,0): defect edge is the arc from v_a to v_b
# But a semicircle from (0,0,0) to (5,0,0) has center (2.5,0,0), radius=2.5.
p_circ_ctr_3d = f.cartesian_point((2.5, 0.0, 0.0))
circ_ax_3d    = f.axis2_placement_3d(p_circ_ctr_3d, zdir, xdir)
circle_3d     = f._emit_raw(f"CIRCLE('periodic_3d_circ',#{circ_ax_3d.eid},2.5)")

# TRIMMED_CURVE: arc from theta=pi (start=(0,0,0)) to theta=0 (end=(5,0,0)).
# trim_1=pi, trim_2=2*pi (or equivalently 0, since CIRCLE is periodic).
# We use trim_1=PARAMETER_VALUE(pi) and trim_2=PARAMETER_VALUE(2.0*pi).
trim_3d = f._emit_raw(
    f"TRIMMED_CURVE('periodic_3d_trim',#{circle_3d.eid},"
    f"(PARAMETER_VALUE({math.pi})),(PARAMETER_VALUE({2.0*math.pi})),"
    f".T.,.PARAMETER.)"
)

v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — clean straight lines
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b): arc from (0,0,0) to (5,0,0) ───────────

# THE CATALOG MECHANISM: PCurve is a non-periodic LINE in UV space.
# The 3D CIRCLE is periodic (period 2*pi). The pcurve LINE has no periodicity.
# UV line: start at (0.0, 0.0) in UV, direction (1,0), length 5.
# This models the u-parameter mapping for the arc on the plane surface.
# FixSameParameter attempts to reconcile the CIRCLE's periodic parameter space
# with the LINE's non-periodic domain — it silently heals rather than failing.
pc_pt  = f.cartesian_point((0.0, 0.0))
pc_dir = f.direction((1.0, 0.0))
pc_vec = f.vector(pc_dir, 5.0)
pc_line = f.line(pc_pt, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('periodic_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('periodic_nonperiodic_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('periodic_sc',#{trim_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('periodic_nonperiodic_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
