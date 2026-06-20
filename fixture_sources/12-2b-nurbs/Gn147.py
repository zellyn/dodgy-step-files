"""Gn147 — Stripe singularity (collapsed pole row).

Catalog claim: All V-poles in the middle U-row are collapsed to a single
point (1.0, *, 0.5) — every V position in the row has the same x and z
coordinate, differing only in y. This creates a stripe singularity where the
entire middle U-iso degenerates to a line. Healing detects via pole-distance
analysis and must handle or reject degenerate topology.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V), 3×4 control net.
    Middle U-row (row index 1) has all V-poles at x=1.0, z=0.5. IS the face
    surface.
  - C-1 DRIVER: middle row x and z coordinates identical across all V-poles
    → stripe singularity (iso-parametric row degenerates to a line segment)
    → pole-distance analysis detects collapsed row → stripe-singularity healing.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V);
    3×4 control net;
    U knots (0.0,1.0) mults (3,3) sum=6 → n_u=3 ✓;
    V knots (0.0,1.0) mults (4,4) sum=8 → n_v=... wait: n_v=4, p_v=2 →
    n_v+p_v+1=7 needed, not 8. Use V knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓.
    Middle U-row all at (1.0, y, 0.5) → stripe; IS face surface.
  - C-1 DRIVER: pole-distance check on middle U-row: max dist(p[1][j], p[1][k])
    in xz = 0 → row degenerates to a segment → stripe-singularity flag.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn147",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree=2 (U) × 2 (V); "
        "3×4 control net; "
        "U knots (0.0,1.0) mults (3,3) sum=6 → n_u=3 ✓; "
        "V knots (0.0,0.5,1.0) mults (3,1,3) sum=7 → n_v=4 ✓; "
        "middle U-row all at x=1.0, z=0.5 (stripe singularity); "
        "IS face surface; pole-distance check → collapsed row → stripe healing"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree-2 U × degree-2 V, 3×4 control net ──────
# U: n_u=3, p_u=2 → n_u+p_u+1=6. knots (0.0,1.0) mults (3,3) sum=6 ✓.
# V: n_v=4, p_v=2 → n_v+p_v+1=7. knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓.
# Control net: 4 V-rows × 3 U-cols.
# Row 0 (u=0): normal spread.
# Row 1 (middle u): stripe singularity — all x=1.0, z=0.5, varying y only.
# Row 2 (u=1): normal spread.
r0 = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((0.0, 2.0, 0.0)),
    f.cartesian_point((0.0, 4.0, 0.0)),
    f.cartesian_point((0.0, 6.0, 0.0)),
]
# Stripe row: x and z identical across all V-poles.
r1 = [
    f.cartesian_point((1.0, 0.0, 0.5)),   # same x=1.0, z=0.5
    f.cartesian_point((1.0, 2.0, 0.5)),
    f.cartesian_point((1.0, 4.0, 0.5)),
    f.cartesian_point((1.0, 6.0, 0.5)),
]
r2 = [
    f.cartesian_point((2.0, 0.0, 0.0)),
    f.cartesian_point((2.0, 2.0, 0.0)),
    f.cartesian_point((2.0, 4.0, 0.0)),
    f.cartesian_point((2.0, 6.0, 0.0)),
]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

mech_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn147_stripe_singularity',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,1,3),"
    f"(0.0,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Boundary edges ─────────────────────────────────────────────────────────────
# 3D corners: r0[0]=(0,0,0), r0[3]=(0,6,0), r2[3]=(2,6,0), r2[0]=(2,0,0).
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((2.0, 0.0, 0.0))
p_c3 = f.cartesian_point((2.0, 6.0, 0.0))
p_d3 = f.cartesian_point((0.0, 6.0, 0.0))
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

# UV domain U∈[0,1] V∈[0,1].
e_bot   = mk_line_edge(vt_a, vt_b, (0.,0.,0.), (1.,0.,0.),   (0.0,0.0), (1.,0.),  1.0)
e_right = mk_line_edge(vt_b, vt_c, (2.,0.,0.), (0.,1.,0.),   (1.0,0.0), (0.,1.),  1.0)
e_top   = mk_line_edge(vt_c, vt_d, (2.,6.,0.), (-1.,0.,0.),  (1.0,1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,6.,0.), (0.,-1.,0.),  (0.0,1.0), (0.,-1.), 1.0)

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
