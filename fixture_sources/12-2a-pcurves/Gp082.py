"""Gp082 — FixAddCurve3d trim-domain extension.

Catalog claim: Edge on trimmed surface where the natural 3D-from-pcurve curve
extends past the trim boundary; FixAddCurve3d builds the full extent instead
of respecting trim domain.

Fixture: PLANE face. The defect edge's 3D curve is a TRIMMED_CURVE with:
  - BASIS_CURVE: a clean LINE extending from x=-1 to x=+∞.
  - TRIM range: [0.5, 2.5] (PARAMETER_VALUE bounds) that is strictly inside
    the full extent [0.0, ...). The trim U1 < U2 < basis range.
  - PCurve: LINEAR on the PLANE, matching only the trimmed portion.

FixAddCurve3d, when asked to rebuild 3D geometry from the pcurve, samples the
pcurve domain [0.5, 2.5] and tries to recover the basis LINE. Without clipping
to the trim domain it builds the full LINE extent instead of the 2-unit segment.
OCC accepts the trimmed edge cleanly because endpoints match: shape(1).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp082",
             defect="TRIMMED_CURVE basis LINE with U1=0.5 U2=2.5 inside full basis range; "
                    "FixAddCurve3d extends past trim to build full curve extent")

# Host surface: planar XY
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# The defect edge runs from (0.5, 0, 0) to (2.5, 0, 0).
# Basis LINE starts at (-1, 0, 0) pointing in X with magnitude 1; parameterized
# by arc-length so param t corresponds to distance from (-1,0,0).
# At t=0.5: 3D = (-1+0.5, 0, 0) = (-0.5, 0, 0)  -- NO, use simpler:
# Basis LINE at origin pointing X (arc-length). t=0.5 -> (0.5,0,0), t=2.5 -> (2.5,0,0).
# But to make the basis WIDER than the trim, we anchor the basis earlier:
# basis_origin = (-1, 0, 0), dir = (1,0,0), magnitude = 1.
# Parametric: P(t) = (-1,0,0) + t*(1,0,0) = (t-1, 0, 0).
# At t=1.5: (0.5, 0, 0)  [= trim start in 3D]
# At t=3.5: (2.5, 0, 0)  [= trim end in 3D]
# Trim: PARAMETER_VALUE(1.5) to PARAMETER_VALUE(3.5).
# Basis extends from t=0 (P=(−1,0,0)) to t=4+ (P=(3+,0,0)) — wider on both ends.

basis_orig = f.cartesian_point((-1.0, 0.0, 0.0))
basis_dir  = f.direction((1.0, 0.0, 0.0))
basis_vec  = f.vector(basis_dir, 1.0)
basis_line = f.line(basis_orig, basis_vec)

# TRIMMED_CURVE: trim [1.5, 3.5] — strictly inside basis domain.
# trim_start 3D = (0.5, 0, 0); trim_end 3D = (2.5, 0, 0).
trim_3d = f._emit_raw(
    f"TRIMMED_CURVE('trimmed_line_with_room',#{basis_line.eid},"
    f"(PARAMETER_VALUE(1.5)),(PARAMETER_VALUE(3.5)),.T.,.PARAMETER.)"
)

# Face corner vertices (a rectangle from (0.5,0,0) to (2.5,0,0) raised in Y).
p_a = f.cartesian_point((0.5, 0.0, 0.0))
p_b = f.cartesian_point((2.5, 0.0, 0.0))
p_c = f.cartesian_point((2.5, 1.0, 0.0))
p_d = f.cartesian_point((0.5, 1.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Right, top, left clean edges.
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 1.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 2.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 1.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# PCurve: LINEAR in UV from (0.5, 0) to (2.5, 0) — matches the trimmed portion.
pc_start = f.cartesian_point((0.5, 0.0))
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, 2.0)
pc_line  = f.line(pc_start, pc_vec)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bot_trimmed_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{trim_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
