"""Gs062 — Trimmed cylinder ValueOfUV dispatch.

Catalog claim: A CYLINDRICAL_SURFACE (r=5.0) trimmed to u∈[π/4, 3π/4], v∈[1.0, 5.0]
via RECTANGULAR_TRIMMED_SURFACE. ValueOfUV checks basis type (CYLINDER) but ignores
trim bounds, so inversion of a 3D point outside the trim domain produces (u,v)
parameters that lie outside [π/4, 3π/4] × [1.0, 5.0]. Out-of-bounds parameters are
not clamped or re-projected; strict kernels reject or return empty.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE (trimming CYLINDRICAL_SURFACE) IS the
    ADVANCED_FACE.face_geometry; trim domain u∈[π/4, 3π/4], v∈[1, 5] IS the
    mechanism wired into face topology; ValueOfUV ignores trim bounds IS the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE'),
                     contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE IS the ADVANCED_FACE.face_geometry;
    trim bounds [π/4, 3π/4] × [1, 5] restrict cylinder IS the mechanism on face surface;
    ValueOfUV ignores trim domain, produces out-of-bounds (u,v) IS the defect.
  - shape_null driver: out-of-bounds UV not clamped; strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs062",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (trimming CYLINDRICAL_SURFACE r=5.0) IS "
        "ADVANCED_FACE.face_geometry; trim u∈[π/4,3π/4] v∈[1,5] IS the mechanism "
        "wired into face topology; ValueOfUV ignores trim bounds, out-of-bounds "
        "UV produced IS the defect; shape_null"
    ),
)

PI = math.pi

# ── CYLINDRICAL_SURFACE radius 5.0, Z-axis ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs062_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs062_cyl',#{cyl_ax.eid},5.0)")

# ── RECTANGULAR_TRIMMED_SURFACE: u∈[π/4, 3π/4], v∈[1.0, 5.0] ───────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
U1 = PI / 4       # 0.7853981633974483
U2 = 3 * PI / 4   # 2.356194490192345
V1 = 1.0
V2 = 5.0
trimmed = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs062_trim',#{cyl.eid},"
    f"{U1},{U2},{V1},{V2},.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the trimmed cylindrical surface ──────────────────
# 3D corners corresponding to the trim domain corners:
#   u=π/4,  v=1: (5 cos π/4, 5 sin π/4, 1) = (3.536, 3.536, 1)
#   u=3π/4, v=1: (5 cos 3π/4, 5 sin 3π/4, 1) = (-3.536, 3.536, 1)
#   u=3π/4, v=5: (-3.536, 3.536, 5)
#   u=π/4,  v=5: (3.536, 3.536, 5)
C = 5.0 * math.cos(PI / 4)   # ≈ 3.5355339059327378

p_A = f.cartesian_point(( C,  C, V1))
p_B = f.cartesian_point((-C,  C, V1))
p_C = f.cartesian_point((-C,  C, V2))
p_D = f.cartesian_point(( C,  C, V2))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{trimmed.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

du = U2 - U1  # π/2
dv = V2 - V1  # 4.0

# e0: bottom edge A→B (v=1, u: π/4 → 3π/4)
e0 = mk_edge_line(v_A, v_B,
                  ( C,  C, V1), (-2*C, 0.0, 0.0), 2*C,
                  (U1, V1), (1.0, 0.0), du)
# e1: right edge B→C (u=3π/4, v: 1 → 5)
e1 = mk_edge_line(v_B, v_C,
                  (-C,  C, V1), (0.0, 0.0, 1.0), dv,
                  (U2, V1), (0.0, 1.0), dv)
# e2: top edge C→D (v=5, u: 3π/4 → π/4)
e2 = mk_edge_line(v_C, v_D,
                  (-C,  C, V2), (2*C, 0.0, 0.0), 2*C,
                  (U2, V2), (-1.0, 0.0), du)
# e3: left edge D→A (u=π/4, v: 5 → 1)
e3 = mk_edge_line(v_D, v_A,
                  ( C,  C, V2), (0.0, 0.0, -1.0), dv,
                  (U1, V2), (0.0, -1.0), dv)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE IS the face_geometry; trim bounds IS the mechanism on face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], trimmed)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
