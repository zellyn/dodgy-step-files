"""Gn141 — High V-Multiplicity Continuity Gap.

Catalog claim: B-spline surface with a full-multiplicity interior V-knot
(multiplicity = degree + 1 = degree at that point creates a C(-1) break,
i.e., a geometric discontinuity). Healers that only check C0 continuity miss
the gap; full-multiplicity knot exposes the continuity-gap detection path.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 4×6 control net.
    Interior V-knot at 0.5 with multiplicity=3 (= degree+1 = full multiplicity)
    creates a geometric gap in V. IS the face surface.
  - C-1 DRIVER: full-multiplicity interior V-knot (mult=3 = p_v+1) → C(-1)
    discontinuity → continuity-gap healing path triggered.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    4×6 control net;
    U knots (0.0,0.5,1.0) mults (3,1,3) sum=7 → n_u=4 ✓;
    V knots (0.0,0.5,1.0) mults (3,3,3) sum=9 → n_v=6 ✓;
    interior V-knot mult=3 = p_v+1 (full multiplicity) → geometric gap;
    IS face surface; continuity-gap healing path.
  - C-1 DRIVER: full-multiplicity interior V knot → upper and lower patch
    share only a point at v=0.5 but not tangent → C(-1) in V.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn141",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "4×6 control net; "
        "U knots (0.0,0.5,1.0) mults (3,1,3) sum=7 → n_u=4; "
        "V knots (0.0,0.5,1.0) mults (3,3,3) sum=9 → n_v=6; "
        "interior V-knot mult=3=p_v+1 (full mult, geometric gap); "
        "IS face surface; continuity-gap detection → healing path"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 4×6 control net ──────
# U: n_u=4, p_u=2 → n_u+p_u+1=7. knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓.
#    One interior U-knot at 0.5 (mult=1 < p_u+1=3): C1 continuity in U.
# V: n_v=6, p_v=2 → n_v+p_v+1=9. knots (0.0,0.5,1.0) mults (3,3,3) sum=9 ✓.
#    Interior V-knot at 0.5 (mult=3 = p_v+1 = full mult): C(-1) gap in V.
#    Lower half (v∈[0,0.5]) and upper half (v∈[0.5,1]) are disconnected patches.
# Control net: 6 V-rows × 4 U-cols.
# Lower half poles (v-rows 0,1,2): forms a ramp z=0..1.
# Upper half poles (v-rows 3,4,5): starts offset from lower end to create gap.
r0 = [f.cartesian_point((float(u)*3, 0.0, 0.0)) for u in range(4)]   # v=0
r1 = [f.cartesian_point((float(u)*3, 1.0, 0.5)) for u in range(4)]   # v∈[0,0.5] interior
r2 = [f.cartesian_point((float(u)*3, 2.0, 1.0)) for u in range(4)]   # v=0.5 (lower endpoint)
# Gap: upper half starts at z=1.5 (not z=1.0), producing a geometric gap in V.
r3 = [f.cartesian_point((float(u)*3, 2.0, 1.5)) for u in range(4)]   # v=0.5 (upper startpoint)
r4 = [f.cartesian_point((float(u)*3, 3.0, 2.0)) for u in range(4)]   # v∈[0.5,1] interior
r5 = [f.cartesian_point((float(u)*3, 4.0, 2.5)) for u in range(4)]   # v=1

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)},{row_ids(r3)},{row_ids(r4)},{row_ids(r5)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn141_v_mult_gap',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,3),(3,3,3),"
    f"(0.0,0.5,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[3]=(9,0,0), r5[3]=(9,4,2.5), r5[0]=(0,4,2.5).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((9.0, 0.0, 0.0))
p_c3 = f.cartesian_point((9.0, 4.0, 2.5))
p_d3 = f.cartesian_point((0.0, 4.0, 2.5))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)
vt_c = f.vertex_point(p_c3)
vt_d = f.vertex_point(p_d3)

def mk_line_edge(vs_, ve_, p3c, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3c)
    d3e = f.direction(d3t)
    v3_ = f.vector(d3e, length)
    l3  = f.line(p3e, v3_)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{mech_surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

# UV domain U∈[0,1] V∈[0,1]; 3D corners above.
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),   (1.,0.,0.),   (0.0,0.0), (1.,0.),  1.0)
e_right = mk_line_edge(vt_b, vt_c, (9.,0.,0.),   (0.,1.,0.),   (1.0,0.0), (0.,1.),  1.0)
e_top   = mk_line_edge(vt_c, vt_d, (9.,4.,2.5),  (-1.,0.,0.),  (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,4.,2.5),  (0.,-1.,0.),  (0.0,1.0), (0.,-1.), 1.0)

loop  = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], mech_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
