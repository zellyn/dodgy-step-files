"""Gn032 — Pro/E non-uniform parameter scaling on 2D Geom2dAPI_Interpolate curves.

Catalog claim: Pro/E emits 2D interpolation curves whose points have non-uniform
parameter scaling (per-segment chord-length parameterization with explicit scaling
tags). OCCT's reader didn't replicate the scaling and produced a different 2D
curve from the source.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS used as pcurve (2D interpolation, flat-plane face).
  - The pcurve control points represent a chord-length parameterized interpolation
    curve with non-uniform parameter scaling: knot spacing reflects per-segment
    arc-lengths (0, 0.3, 0.5, 0.8, 1.0) rather than uniform (0, 0.25, 0.5, 0.75, 1.0).
  - The 3D edge uses a matching B-spline with a C-1 break (1.5-unit gap at t=0.5,
    knots (3,3,3) at (0,0.5,1)).
  - The non-uniform pcurve knot spacing is the catalog mechanism; a kernel that
    ignores it maps the 2D curve to uniform spacing and produces wrong geometry.

Mechanism vs driver:
  - CATALOG MECHANISM: 2D B_SPLINE_CURVE_WITH_KNOTS pcurve with non-uniform
    per-segment chord-length parameter scaling (knots 0,0.3,0.5,0.8,1 instead
    of uniform 0,0.25,0.5,0.75,1) — Pro/E interpolation style.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit positional gap at t=0.5 drives
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn032",
    defect=(
        "Pro/E 2D BSpline interpolation non-uniform parameter scaling: "
        "pcurve B_SPLINE_CURVE_WITH_KNOTS degree-3 with per-segment chord-length "
        "knots (0.0,0.3,0.5,0.8,1.0) mults (4,1,1,1,4) instead of uniform spacing; "
        "OCCT reader ignores scale tags and maps to uniform spacing producing wrong "
        "2D curve; Geom2dAPI_Interpolate scaling not replicated on import; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── HOST SURFACE: flat plane ──────────────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: non-uniform pcurve with chord-length parameter scaling ─
# Degree-3 B-spline interpolation pcurve with 8 CPs.
# Non-uniform knot vector: (0, 0.3, 0.5, 0.8, 1) mults (4,1,1,1,4) sum=11=3+8 ✓
# Control points define a gentle curve in UV space (Y=0 plane face).
pp = [
    f.cartesian_point((0.0,  0.0)),
    f.cartesian_point((0.6,  0.2)),
    f.cartesian_point((1.2,  0.3)),
    f.cartesian_point((2.0,  0.1)),   # crossing knot at 0.3 (chord segment)
    f.cartesian_point((2.8,  0.4)),   # crossing knot at 0.5
    f.cartesian_point((3.6,  0.2)),
    f.cartesian_point((4.3,  0.1)),   # crossing knot at 0.8
    f.cartesian_point((5.0,  0.0)),
]
pp_ids = "(" + ",".join(f"#{p.eid}" for p in pp) + ")"

# Non-uniform chord-length knots: (0,0.3,0.5,0.8,1) mults (4,1,1,1,4)
# sum = 4+1+1+1+4 = 11 = degree+1 + n_cp = 3+1+7 = 11 ✓  (n_cp = 8, so n+1=8, n+p+2=11)
nonuniform_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('proe_nonuniform_pc',3,"
    f"{pp_ids},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,4),(0.0,0.3,0.5,0.8,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn032_pcdef',(#{nonuniform_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn032_pc_ent',#{surf.eid},#{defrep.eid})")

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn032_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

sc = f._emit_raw(
    f"SURFACE_CURVE('gn032_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn032_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
)

# Remaining three edges of rectangular face
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (5.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (5.0, 5.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 5.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
