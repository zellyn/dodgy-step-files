"""Gp115 — ShapeAnalysis_Edge.GetEndTangent2d tangent-mid-knot.

Catalog claim: Pcurve B-spline with knot at exact endpoint. GetEndTangent2d
evaluates derivative at knot which produces discontinuous tangent result at
boundary.

STEP mechanism (literal):
  - PLANE Z=0 face. Defect edge via SURFACE_CURVE.
  - 3D curve: clean LINE from (0,0,0) to (5,0,0).
  - PCurve: B_SPLINE_CURVE_WITH_KNOTS degree-2, 5 CPs, knot vector
    (3,2,3) at (0.0, 0.5, 1.0) — interior knot at t=0.5 with multiplicity 2,
    creating a C-0 continuity break (tangent discontinuity) at t=0.5.
  - The pcurve maps the edge from UV (0,0) to UV (5,0) but with a kink: CPs
    create a non-monotone UV path that changes direction at the interior knot.
    Left tangent at t=0.5 and right tangent at t=0.5 are in different directions.
  - THE CATALOG MECHANISM: The interior knot at t=0.5 with mult=2 creates a
    C-0 tangent kink exactly at a "mid-knot" boundary. GetEndTangent2d evaluates
    the derivative of the pcurve at the edge endpoint (t=1.0, clamped end). The
    endpoint tangent is geometrically well-defined, but the pcurve has a
    discontinuous tangent at t=0.5 that influences how OCC evaluates span
    derivatives near that interior knot. GetEndTangent2d still produces a usable
    (non-NaN) tangent at t=1.0, and OCC heals the edge cleanly.
  - NO C-1 break in 3D (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve B-spline degree-2 with interior knot mult=2 at
    t=0.5; C-0 tangent discontinuity at mid-knot; GetEndTangent2d still finds
    usable tangent at actual endpoint t=1.0 and OCC heals silently.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp115",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D LINE (0,0,0)→(5,0,0); "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2 5 CPs knot vector (3,2,3) "
        "at (0.0,0.5,1.0) — interior knot at t=0.5 (mult=2) creates C-0 tangent "
        "discontinuity at mid-knot; left tangent at t=0.5 = direction (1,0.8), "
        "right tangent at t=0.5 = direction (1.5,-0.8) — kink; GetEndTangent2d "
        "at endpoint t=1.0 still returns usable tangent from clamped span; "
        "OCC heals shape(1)/shape(1)"
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

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — bare EDGE_CURVE with LINE
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# 3D curve: clean LINE from (0,0,0) to (5,0,0)
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 5.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: PCurve B-spline degree-2, 5 CPs.
# Knot vector: (3, 2, 3) at (0.0, 0.5, 1.0) — sum=8=5+2+1 correct.
# Interior knot at t=0.5 with multiplicity 2 — for degree-2 this gives C-0
# continuity (tangent discontinuity) at t=0.5. The pcurve has a sharp tangent
# kink exactly at the interior knot t=0.5.
# Segment 1: t in [0.0, 0.5], CPs pp0, pp1, pp2 — going (0,0)→(2.0,0.5)
# Segment 2: t in [0.5, 1.0], CPs pp2, pp3, pp4 — going (2.0,0.5)→(5.0,0)
# Left tangent at t=0.5: direction proportional to pp1→pp2 = (2.0-1.0, 0.5-0.8)=(1.0,-0.3)
# Right tangent at t=0.5: direction proportional to pp2→pp3 = (3.5-2.0,-0.3-0.5)=(1.5,-0.8)
# — a C-0 tangent kink at the interior mid-knot.
# GetEndTangent2d at the edge endpoint t=1.0 (clamped) evaluates the last span
# derivative from pp3→pp4 and returns a usable tangent direction. OCC heals.
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((1.0,  0.8))   # first span: upward-going
pp2 = f.cartesian_point((2.0,  0.5))   # interior knot junction (C-0 only)
pp3 = f.cartesian_point((3.5, -0.3))   # second span: changes direction — tangent kink
pp4 = f.cartesian_point((5.0,  0.0))   # endpoint at t=1.0 (clamped, well-defined)

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('midknot_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('midknot_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('midknot_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('midknot_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('midknot_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
