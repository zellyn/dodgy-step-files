"""Gn142 — Large Pole-Count Surface Sampling Threshold.

Catalog claim: B-spline surface with a very large number of control poles
(e.g., 20+ in U) that exceeds the sampling threshold used in surface-quality
analysis. Kernels with fixed sampling grids fail to adequately sample such
surfaces, causing surface-quality checks to return spurious results.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V), 20×2 control net.
    Many interior U-knots push pole count above sampling thresholds.
    IS the face surface.
  - C-1 DRIVER: 20 U-poles → sampling grid smaller than pole count → surface
    quality check under-samples → incorrect curvature or gap assessment.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V);
    20×2 control net; U knots: 17 interior knots + degree-3 end clamps →
    n_u=20, p_u=3, n_u+p_u+1=24; mults (4, 1×16, 4) sum=4+16+4=24 ✓;
    V mults (2,2) knots (0.0,1.0); IS face surface;
    pole count > sampling threshold → under-sampling → spurious quality check.
  - C-1 DRIVER: fixed sampling grid (e.g., 10×10) fails to capture all
    20-pole surface oscillations → false quality verdict.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn142",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=3 (U) × 1 (V); "
        "20×2 control net; "
        "U: n_u=20, p_u=3 → n_u+p_u+1=24; "
        "mults (4,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4) sum=24; "
        "V mults (2,2) knots (0.0,1.0); IS face surface; "
        "pole count > sampling threshold → under-sampling → spurious surface quality check"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-3 U × degree-1 V, 20×2 control net ──────
# U: n_u=20, p_u=3 → n_u+p_u+1=24.
#    knots: 18 distinct values, mults (4, 1×16, 4) sum=4+16+4=24 ✓.
#    Evenly spaced interior knots at 1/17, 2/17, ..., 16/17.
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) sum=4 ✓. knots (0.0,1.0).
# Control net: 2 V-rows × 20 U-cols.
# Poles oscillate sinusoidally along U to stress the sampling grid.
import math

n_u = 20
u_row0 = []
u_row1 = []
for i in range(n_u):
    t = i / (n_u - 1)
    x = t * 20.0
    y = math.sin(t * 6 * math.pi) * 0.5   # 3 full sine oscillations
    u_row0.append(f.cartesian_point((x, y, 0.0)))
    u_row1.append(f.cartesian_point((x, y, 1.0)))

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(u_row0)},{row_ids(u_row1)})"

# 16 interior knots at evenly-spaced positions + degree-3 clamping.
# Distinct knots: 0.0, 1/17, 2/17, ..., 16/17, 1.0 (18 values).
interior_knots = [round(k / 17, 6) for k in range(1, 17)]
all_knots = [0.0] + interior_knots + [1.0]
all_knots_str = ",".join(str(k) for k in all_knots)
all_mults = [4] + [1] * 16 + [4]
all_mults_str = ",".join(str(m) for m in all_mults)

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn142_large_pole_count',3,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"({all_mults_str}),(2,2),"
    f"({all_knots_str}),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners at t=0 and t=1 (endpoints of the oscillating curve × z extent).
# At t=0: sin(0)=0 → (0,0,0). At t=1: sin(6π)=0 → (20,0,0).
p_a3 = f.cartesian_point((0.0,  0.0, 0.0))
p_b3 = f.cartesian_point((20.0, 0.0, 0.0))
p_c3 = f.cartesian_point((20.0, 0.0, 1.0))
p_d3 = f.cartesian_point((0.0,  0.0, 1.0))
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

# UV domain U∈[0,1] V∈[0,1]; 3D corners above (endpoints happen to have y=0).
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.),   (1.,0.,0.),  (0.0,0.0), (1.,0.),  1.0)
e_right = mk_line_edge(vt_b, vt_c, (20.,0.,0.),  (0.,0.,1.),  (1.0,0.0), (0.,1.),  1.0)
e_top   = mk_line_edge(vt_c, vt_d, (20.,0.,1.),  (-1.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,0.,1.),   (0.,0.,-1.), (0.0,1.0), (0.,-1.), 1.0)

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
