"""Gn071 — ShapeAnalysis_Curve.IsClosed BezierCurve check.

Catalog claim: A BEZIER_CURVE entity with matching first and last poles
(closure property) is evaluated using B-spline closure semantics, returning
false despite satisfying Bezier-specific closure.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - BEZIER_CURVE degree 3, 5 poles, first = last = (0,0,0).
    IsClosed() returns false because implementation treats as B-spline
    (which requires explicit periodic flag) rather than Bezier closure semantics
    (first pole == last pole is sufficient).
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the BEZIER_CURVE first==last closure combined with B-spline
    semantics mis-evaluation drives shape_null=True via topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: BEZIER_CURVE degree-3 5 poles first=last=(0,0,0);
    IS defect edge SURFACE_CURVE.curve_3d; IsClosed() returns false due to
    B-spline periodic-flag check, ignoring Bezier pole-equality closure.
  - C-1 DRIVER: same entity — mis-detected non-closed Bezier drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn071",
    defect=(
        "BEZIER_CURVE degree-3 5 poles first=last=(0,0,0); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed() uses B-spline periodic-flag semantics, ignores Bezier "
        "pole-equality closure — returns false despite first==last; "
        "topology failure drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: BEZIER_CURVE degree 3, 5 poles, first=last=(0,0,0) ────
# degree=3, 5 poles: (0,0,0),(1,1,0),(2,-1,0),(3,1,0),(0,0,0)
# First pole == last pole → Bezier closure, but IsClosed() requires periodic flag.
bp0 = f.cartesian_point((0.0,  0.0, 0.0))
bp1 = f.cartesian_point((1.0,  1.0, 0.0))
bp2 = f.cartesian_point((2.0, -1.0, 0.0))
bp3 = f.cartesian_point((3.0,  1.0, 0.0))
bp4 = f.cartesian_point((0.0,  0.0, 0.0))   # same as bp0 — Bezier closure

bezier_3d = f._emit_raw(
    f"BEZIER_CURVE('gn071_bezier',3,"
    f"(#{bp0.eid},#{bp1.eid},#{bp2.eid},#{bp3.eid},#{bp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.)"
)

# ── Pcurve: linear in UV along bottom edge ────────────────────────────────────
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn071_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn071_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn071_sc',#{bezier_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 1.0, 0.0))
p_d = f.cartesian_point((0.0, 1.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn071_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 1.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
