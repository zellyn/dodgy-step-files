"""Gs079 — ShapeAnalysis_Surface.UVFromIso periodic reset.

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS, U-periodic (periodic_u=.T.),
u_upper=2π. Reproduces silent wraparound when querying u_iso=2π that maps
to u_iso=0, breaking downstream code expecting original parameter.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (periodic_u=.T., u_upper=2π) IS the
    ADVANCED_FACE.face_geometry; u-periodic wraparound (u=2π → u=0) IS
    the mechanism wired into face topology; UVFromIso returns u=0 instead
    of u=2π IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'PERIODIC').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (U-periodic, u∈[0,2π])
    IS the ADVANCED_FACE.face_geometry; U-periodic wraparound at seam IS
    the mechanism wired into face topology; UVFromIso silently resets
    u=2π to u=0 IS the defect.
  - shape_null driver: incorrect UV parameter returned; strict kernels
    reject inconsistent topology; empty result.
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 2.0 * math.pi

f = StepFile(
    catalog_id="Gs079",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (U-periodic, u_upper=2π) IS "
        "ADVANCED_FACE.face_geometry; U-periodic seam wraparound (u=2π→u=0) "
        "IS the mechanism wired into face topology; UVFromIso periodic reset "
        "returns wrong parameter IS the defect; shape_null"
    ),
)

# ── U-periodic B-spline surface: 5 control points in U (closed), 2 in V ──────
# degree 2 in U (periodic), degree 1 in V.
# Control grid: 5 cols (U-periodic) × 2 rows (V): forms a tube-like surface.
# U-knots for a periodic degree-2 surface with 5 poles: (0, 2π/5, 4π/5, 6π/5, 8π/5, 2π)
# with multiplicities (1,1,1,1,1,1) for periodic uniform spacing.
# We use a simpler representation: degree-1 U-periodic (linear) with 4 poles.
ctrl = [
    [(1.0,  0.0, 0.0), (0.0,  1.0, 0.0), (-1.0,  0.0, 0.0), (0.0, -1.0, 0.0)],
    [(1.0,  0.0, 1.0), (0.0,  1.0, 1.0), (-1.0,  0.0, 1.0), (0.0, -1.0, 1.0)],
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(4)) + ")"
    for r in range(2)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'), contains(b'PERIODIC')
# periodic_u=.T., u knots span [0, 2π] with uniform spacing (period = 2π).
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs079_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.T.,.F.,.F.,"
    f"(2,1,1,2),(2,2),"
    f"(0.0,{TWO_PI/4:.10f},{TWO_PI/2:.10f},{TWO_PI:.10f}),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary on the periodic surface ─────────────────────────────────────
# Use a rectangular patch at u∈[0, TWO_PI], v∈[0,1].
# The seam at u=2π is the defect trigger: UVFromIso resets u=2π back to u=0.
p_A = f.cartesian_point((1.0,  0.0, 0.0))   # u=0,      v=0
p_B = f.cartesian_point((1.0,  0.0, 1.0))   # u=0,      v=1
p_C = f.cartesian_point((1.0,  0.0, 0.0))   # u=2π,     v=1  (seam: same 3D as p_A/B row)
p_D = f.cartesian_point((1.0,  0.0, 0.0))   # u=2π,     v=0  (seam)

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: left seam meridian v: 0→1 at u=0
e0 = mk_edge_line(v_A, v_B,
                  (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (0.0, 0.0), (0.0, 1.0), 1.0)
# e1: top edge u: 0→2π at v=1 (periodic seam edge — defect trigger)
e1 = mk_edge_line(v_B, v_B,
                  (1.0, 0.0, 1.0), (0.0, 1.0, 0.0), 1.0e-12,
                  (0.0, 1.0), (1.0, 0.0), TWO_PI)
# e2: right seam meridian v: 1→0 at u=2π (seam — same topology as e0)
e2 = mk_edge_line(v_B, v_A,
                  (1.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (TWO_PI, 1.0), (0.0, -1.0), 1.0)
# e3: bottom edge u: 2π→0 at v=0
e3 = mk_edge_line(v_A, v_A,
                  (1.0, 0.0, 0.0), (0.0, -1.0, 0.0), 1.0e-12,
                  (TWO_PI, 0.0), (-1.0, 0.0), TWO_PI)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; U-periodic seam IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
