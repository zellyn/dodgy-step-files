"""Gp054 — ShapeFix_Edge.FixReversed2d non-B-spline pcurve.

Catalog claim: FixReversed2d special-cases B-spline reversal but doesn't
handle TRIMMED_CURVE wrapping a LINE. Reversal of trimmed-line pcurves leaves
parameter range unflipped, creating inconsistent direction vs. range mapping.

Mechanism: The defect IS in the pcurve — a TRIMMED_CURVE wrapping a LINE
with parameter range [0, 5]. When the edge orientation is reversed, FixReversed2d
correctly flips the underlying LINE direction but fails to invert the trim
parameter range from (0, 5) to (5, 0), leaving inconsistent orientation.
The face loads cleanly (shape(1)) because OCC heals the range mismatch;
the bug is exposed during the FixReversed2d path for non-B-spline pcurves.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp054",
    defect=(
        "PLANE Z=0; defect edge uses TRIMMED_CURVE(LINE, trim=[0,5]) as pcurve; "
        "edge is oriented reversed (.F.); FixReversed2d flips LINE direction but "
        "leaves TRIMMED_CURVE parameter range as (0,5) instead of inverting to (5,0); "
        "inconsistent direction vs. range mapping on TRIMMED_CURVE pcurve; "
        "FixReversed2d non-B-spline path IS the defect mechanism"
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

# Face corners: rectangle [0,5] x [0,3]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build a normal EDGE_CURVE with SURFACE_CURVE + linear PCURVE."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 3.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 3.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 3.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, (0.0, 3.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_b -> v_a, reversed) ────────────────────────────
# CATALOG MECHANISM: TRIMMED_CURVE wrapping LINE as pcurve.
# Edge runs from v_b=(5,0,0) to v_a=(0,0,0) (reversed direction, orient=.F.)
# 3D curve: LINE from (0,0,0) in +X direction, length 5
line_3d_p = f.cartesian_point((0.0, 0.0, 0.0))
line_3d_d = f.direction((1.0, 0.0, 0.0))
line_3d_v = f.vector(line_3d_d, 5.0)
line_3d   = f.line(line_3d_p, line_3d_v)

# Pcurve: TRIMMED_CURVE wrapping a LINE in UV space
# Base line in UV from u=0 in +U direction
uv_base_p = f.cartesian_point((0.0, 0.0))
uv_base_d = f.direction((1.0, 0.0))
uv_base_v = f.vector(uv_base_d, 1.0)   # unit vec; trim controls extent
uv_base_l = f.line(uv_base_p, uv_base_v)

# TRIMMED_CURVE: LINE trimmed to parameter range [0, 5]
# FixReversed2d flips LINE direction but doesn't invert the (0,5) range to (5,0)
trim_pcurve = f._emit_raw(
    f"TRIMMED_CURVE('gp054_trimmed_pcurve',#{uv_base_l.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp054_def',(#{trim_pcurve.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp054_uv',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp054_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# Edge from v_b to v_a (REVERSED sense), oriented .F. in loop to restore bottom direction
e_bot_edge = f._emit_raw(
    f"EDGE_CURVE('gp054_bot_edge',#{v_b.eid},#{v_a.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot_edge, False),   # .F. = reversed; goes v_a→v_b in loop
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
