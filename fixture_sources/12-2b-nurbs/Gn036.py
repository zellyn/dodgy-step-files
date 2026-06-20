"""Gn036 — B_SPLINE_SURFACE_WITH_KNOTS V knot vector strictly descending.

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS V knot vector violates the
non-decreasing invariant by containing a strictly descending pair
(e.g. (0.0, 0.6, 0.4, 1.0): 0.6 then 0.4). A compliant reader must reject
the surface with a diagnostic naming the offending index.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 1×1, 3×4 control net.
    U knots: (0.0, 0.5, 1.0) mults (2,1,2) — valid, non-decreasing.
    V knots: (0.0, 0.6, 0.4, 1.0) mults (2,1,1,2) — INVALID: 0.6 > 0.4.
    The descending pair at V-knot indices [1]→[2] is the catalog mechanism.
  - C-1 break in 3D edge (1.5-unit CP gap at t=0.5) drives shape_null=True.
  - No separate driver needed once the descending knot causes NaN; C-1 adds
    belt+suspenders.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS V knot vector
    (0.0,0.6,0.4,1.0) — strictly descending pair 0.6→0.4 at index 1→2;
    violates non-decreasing invariant; compliant reader must reject with
    diagnostic naming the offending index.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn036",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS V knot vector (0.0,0.6,0.4,1.0) strictly "
        "descending at index 1→2 (0.6 then 0.4): violates non-decreasing knot "
        "invariant; compliant reader must reject with diagnostic naming offending "
        "V-knot index; OCC silently accepts; See also Gn001, Gn003; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: B_SPLINE_SURFACE with descending V knots ──────
# degree 1×1, 3 U-CP rows × 4 V-CP cols.
# U knots: (0.0, 0.5, 1.0) mults (2,1,2) sum=5=1+3+1 ✓
# V knots: (0.0, 0.6, 0.4, 1.0) mults (2,1,1,2) sum=6=1+4+1 ✓ (invalid ordering)
# Control net: a simple flat grid in XY (Z=0 throughout)

r0 = [f.cartesian_point((0.0, float(j*2), 0.0)) for j in range(4)]
r1 = [f.cartesian_point((2.0, float(j*2), 0.0)) for j in range(4)]
r2 = [f.cartesian_point((4.0, float(j*2), 0.0)) for j in range(4)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

# THE DEFECT: V knots (0.0, 0.6, 0.4, 1.0) — 0.6 > 0.4 at index 1→2
descending_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('v_knot_descending_surf',1,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,1,2),(2,1,1,2),"
    f"(0.0,0.5,1.0),(0.0,0.6,0.4,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn036_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn036_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn036_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn036_pc_ent',#{descending_surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn036_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn036_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{descending_surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], descending_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
