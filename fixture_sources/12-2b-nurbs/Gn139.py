"""Gn139 — TrimmedCurve Wrapping Periodic B-spline.

Catalog claim: A periodic B-spline surface (U-periodic) whose boundary edges are
modelled as trimmed-curve wrappers around the periodic seam. Kernels that unwrap
TrimmedCurve before checking the periodicity flag may misinterpret the parameter
domain, causing seam-detection failure.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V), 5×2 control net,
    U_CLOSED=.T. (periodic topology). IS the face surface.
  - C-1 DRIVER: periodic flag (.T.) on B_SPLINE_SURFACE_WITH_KNOTS; kernels that
    process TrimmedCurve wrappers before checking periodicity flag miss seam
    continuity, triggering invalid parameter domain on the pcurve.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V);
    5×2 control net; U_CLOSED=.T.; U knots (0.0,0.25,0.5,0.75,1.0)
    mults (3,1,1,1,3) sum=9 → n_u=6 needed; use 6×2 with
    mults (3,1,1,1,1,3) sum=10 → n_u=7? Correct: degree=2, n_u=6,
    n_u+p_u+1=9: mults (3,1,1,1,3) sum=9 with 5 knots but need n_u=6
    → add one interior knot: mults (3,1,1,1,1,3) sum=10, 6 knots → n_u=7.
    Use degree=2, 5×2 net: n_u=5, n_u+p_u+1=8; knots (0.0,0.333,0.667,1.0)
    mults (3,1,1,3) sum=8 ✓; V mults (2,2) knots (0.0,1.0); IS face surface;
    TrimmedCurve-wrapping-periodic seam detection failure.
  - C-1 DRIVER: U_CLOSED=.T. on surface with interior knots → seam pcurve
    wrapping at u=1.0 alias u=0.0 → domain mismatch if TrimmedCurve unwrap
    occurs before periodicity check.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn139",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 1 (V); "
        "5×2 control net; U_CLOSED=.T. (periodic topology); "
        "U knots (0.0,0.333,0.667,1.0) mults (3,1,1,3) sum=8 → n_u=5; "
        "V mults (2,2) knots (0.0,1.0); IS face surface; "
        "TrimmedCurve wrapping of periodic seam → domain mismatch if periodicity "
        "check deferred past TrimmedCurve unwrap"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-1 V, 5×2 control net ──────
# U: n_u=5, p_u=2 → n_u+p_u+1=8. knots (0.0,0.333,0.667,1.0) mults (3,1,1,3) sum=8 ✓.
#    U_CLOSED=.T. signals periodic topology; seam at u=0/u=1.
# V: n_v=2, p_v=1 → n_v+p_v+1=4. mults (2,2) sum=4 ✓. knots (0.0,1.0).
# Control net forms a closed cylinder-like strip (first/last U poles match).
u_row0 = [
    f.cartesian_point((1.0,  0.0, 0.0)),   # u=0  (= u=1 for periodic seam)
    f.cartesian_point((0.0,  1.0, 0.0)),   # u=0.333
    f.cartesian_point((-1.0, 0.0, 0.0)),   # u=0.5 midpoint
    f.cartesian_point((0.0, -1.0, 0.0)),   # u=0.667
    f.cartesian_point((1.0,  0.0, 0.0)),   # u=1 (same as u=0 for closure)
]
u_row1 = [
    f.cartesian_point((1.0,  0.0, 2.0)),
    f.cartesian_point((0.0,  1.0, 2.0)),
    f.cartesian_point((-1.0, 0.0, 2.0)),
    f.cartesian_point((0.0, -1.0, 2.0)),
    f.cartesian_point((1.0,  0.0, 2.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(u_row0)},{row_ids(u_row1)})"

# U_CLOSED=.T. encodes periodic topology
mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn139_periodic_trim',2,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(3,1,1,3),(2,2),"
    f"(0.0,0.333,0.667,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners at the seam: row0[0]=(1,0,0), row1[0]=(1,0,2).
# We model an open face at the seam (u=0 and u=1 are topologically identified).
# Bottom edge: u=0..1, v=0 (z=0 ring). Top edge: u=0..1, v=1 (z=2 ring).
# Left/right edges both lie at the seam (u=0 ≡ u=1).
p_a3 = f.cartesian_point((1.0, 0.0, 0.0))
p_b3 = f.cartesian_point((1.0, 0.0, 2.0))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)

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

# Seam edge at u=0 from v=0 to v=1 (3D: from (1,0,0) to (1,0,2)).
# Bottom and top are degenerate (full loop returns to seam).
# Model as simple rectangle in UV; pcurves at u=0 and u=1 are the seam edges.
e_seam_lo = mk_line_edge(vt_a, vt_b, (1.,0.,0.), (0.,0.,1.), (0.0,0.0), (0.,1.), 1.0)
e_seam_hi = mk_line_edge(vt_a, vt_b, (1.,0.,0.), (0.,0.,1.), (1.0,0.0), (0.,1.), 1.0)

# Bottom edge from seam-lo to seam-hi at v=0.
e_bot = mk_line_edge(vt_a, vt_a, (1.,0.,0.), (0.,0.,0.), (0.0,0.0), (1.,0.), 1.0)
# Top edge from seam-hi back to seam-lo at v=1.
e_top = mk_line_edge(vt_b, vt_b, (1.,0.,2.), (0.,0.,0.), (1.0,1.0), (-1.,0.), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e_seam_lo, True),
    f.oriented_edge(e_top,     True),
    f.oriented_edge(e_seam_hi, False),
    f.oriented_edge(e_bot,     False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], mech_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
