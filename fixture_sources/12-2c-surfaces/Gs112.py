"""Gs112 — ShapeUpgrade_ConvertSurfaceToBezierBasis cone-with-trim.

Catalog claim: Trimmed CONICAL_SURFACE conversion to Bezier patch boundaries
doesn't translate cleanly; trim boundaries don't align with Bezier patch
boundaries, causing conversion artifacts.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE (semi-angle 30°, apex at origin) IS the
    ADVANCED_FACE.face_geometry; face boundary loop defines a partial cone
    patch with trim at u=π/4 and u=7π/4 (non-Bezier-boundary aligned)
    IS the mechanism wired into face topology; ConvertSurfaceToBezierBasis
    produces Bezier patches whose boundaries don't align with the partial-cone
    trim, creating conversion artifacts IS the defect.
  - Byte assertions: contains(b'CONICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE (semi_angle=30°, radius=0) IS the
    ADVANCED_FACE.face_geometry; partial-cone trim at non-Bezier-aligned u
    boundaries (u=π/4, u=7π/4) IS the mechanism wired into face topology;
    ConvertSurfaceToBezierBasis produces misaligned patches IS the defect.
  - shape_null driver: Bezier conversion artifacts from non-aligned trim;
    strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

PI      = math.pi
SEMI    = PI / 6.0                   # 30° in radians
U_START = PI / 4.0                   # π/4 (45°) — start trim
U_END   = 7.0 * PI / 4.0            # 7π/4 (315°) — end trim (non-aligned to Bezier)
U_SPAN  = U_END - U_START            # = 6π/4 = 3π/2
TAN30   = math.tan(SEMI)             # tan(30°) ≈ 0.5774
V_BOT   = 1.0                        # v=1 → cone radius at z=1: 1*tan30
V_TOP   = 2.0                        # v=2 → cone radius at z=2: 2*tan30

f = StepFile(
    catalog_id="Gs112",
    defect=(
        f"CONICAL_SURFACE (semi_angle=30deg, apex at origin) IS ADVANCED_FACE.face_geometry; "
        f"partial-cone trim at non-Bezier-aligned u boundaries "
        f"(u={U_START:.6f}, u={U_END:.6f}) IS the mechanism wired into face topology; "
        f"ConvertSurfaceToBezierBasis produces misaligned Bezier patches IS the defect; "
        f"shape_null"
    ),
)

# ── CONICAL_SURFACE: semi-angle 30°, apex at origin, Z axis ──────────────────
# Byte assertion: contains(b'CONICAL_SURFACE')
con_orig = f.cartesian_point((0.0, 0.0, 0.0))
con_zdir = f.direction((0.0, 0.0, 1.0))
con_xdir = f.direction((1.0, 0.0, 0.0))
con_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs112_con_ax',#{con_orig.eid},#{con_zdir.eid},#{con_xdir.eid})"
)
con = f._emit_raw(f"CONICAL_SURFACE('gs112_con',#{con_ax.eid},0.0,{SEMI:.10f})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: partial cone v:[1,2], u:[π/4, 7π/4] ───────────────────────
# Cone surface: point(u,v) = (v*tan30*cos(u), v*tan30*sin(u), v)
# Corners at:
#   A: u=π/4,  v=1: (TAN30/√2, TAN30/√2, 1)
#   B: u=7π/4, v=1: (TAN30/√2, -TAN30/√2, 1)
#   C: u=7π/4, v=2: (2TAN30/√2, -2TAN30/√2, 2)
#   D: u=π/4,  v=2: (2TAN30/√2, 2TAN30/√2, 2)
INV_SQRT2 = 1.0 / math.sqrt(2.0)
r1 = V_BOT * TAN30
r2 = V_TOP * TAN30

p_A = f.cartesian_point((r1 * INV_SQRT2, r1 * INV_SQRT2, V_BOT))
p_B = f.cartesian_point((r1 * INV_SQRT2, -r1 * INV_SQRT2, V_BOT))
p_C = f.cartesian_point((r2 * INV_SQRT2, -r2 * INV_SQRT2, V_TOP))
p_D = f.cartesian_point((r2 * INV_SQRT2, r2 * INV_SQRT2, V_TOP))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{con.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom arc A→B (v=1, u: π/4→7π/4) — partial bottom circle, non-Bezier-aligned
e0 = mk_edge_line(v_A, v_B,
                  (r1 * INV_SQRT2, r1 * INV_SQRT2, V_BOT),
                  (r1 * INV_SQRT2, -r1 * INV_SQRT2 - r1 * INV_SQRT2, 0.0), U_SPAN * r1,
                  (U_START, V_BOT), (1.0, 0.0), U_SPAN)
# e1: right generator B→C (u=7π/4, v: 1→2) — cone generator line at u=7π/4
e1 = mk_edge_line(v_B, v_C,
                  (r1 * INV_SQRT2, -r1 * INV_SQRT2, V_BOT),
                  (r2 * INV_SQRT2 - r1 * INV_SQRT2, -r2 * INV_SQRT2 + r1 * INV_SQRT2, 1.0),
                  V_TOP - V_BOT,
                  (U_END, V_BOT), (0.0, 1.0), V_TOP - V_BOT)
# e2: top arc C→D (v=2, u: 7π/4→π/4) — reversed arc, non-Bezier-aligned
e2 = mk_edge_line(v_C, v_D,
                  (r2 * INV_SQRT2, -r2 * INV_SQRT2, V_TOP),
                  (-r2 * INV_SQRT2, r2 * INV_SQRT2 + r2 * INV_SQRT2, 0.0), U_SPAN * r2,
                  (U_END, V_TOP), (-1.0, 0.0), U_SPAN)
# e3: left generator D→A (u=π/4, v: 2→1) — cone generator line at u=π/4
e3 = mk_edge_line(v_D, v_A,
                  (r2 * INV_SQRT2, r2 * INV_SQRT2, V_TOP),
                  (r1 * INV_SQRT2 - r2 * INV_SQRT2, r1 * INV_SQRT2 - r2 * INV_SQRT2, -1.0),
                  V_TOP - V_BOT,
                  (U_START, V_TOP), (0.0, -1.0), V_TOP - V_BOT)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CONICAL_SURFACE IS the face_geometry;
# partial-cone trim at non-Bezier-aligned u boundaries IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], con)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
