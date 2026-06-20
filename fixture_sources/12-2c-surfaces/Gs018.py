"""Gs018 — Mismatched orientation of 3D curve and pcurve.

Catalog claim: An edge's 3D curve runs in the forward parameter direction
(t=0→1) while its pcurve on the surface runs in the reverse direction (t=1→0),
so that evaluating 3D curve and pcurve at the same t lands at opposite ends of
the edge. Projecting between 3D and UV returns wrong-side parameters; downstream
geometry queries are reversed.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: reject.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry (radius=5).
  - The defect edge E1 has its SURFACE_CURVE PCURVE traced from (pi/2, 5.0)
    to (0, 5.0) in UV while the 3D LINE runs from (0,5,5) to (5,0,5) — pcurve
    direction reversed relative to 3D curve.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE('),
                     contains(b'SURFACE_CURVE('),
                     contains(b'(0.0,5.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    the defect EDGE_CURVE 3D LINE IS the curve_3d of its SURFACE_CURVE; the
    PCURVE for that edge runs in the reversed UV direction (pcurve start
    (0.0,5.0) is at the 3D end-point, not start-point); direction mismatch
    drives shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs018",
    defect=(
        "CYLINDRICAL_SURFACE radius=5 IS ADVANCED_FACE.face_geometry; "
        "defect edge E1: 3D LINE runs (0,5,5)→(5,0,5) forward but PCURVE "
        "runs (pi/2,5.0)→(0.0,5.0) reversed; pcurve start (0.0,5.0) matches "
        "3D end-point; direction mismatch; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: CYLINDRICAL_SURFACE, radius=5 ─────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs018_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
cyl  = f._emit_raw(f"CYLINDRICAL_SURFACE('gs018_cyl',#{ax3.eid},5.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

R = 5.0
half_pi = math.pi / 2.0   # ≈ 1.5707963268

# Small rectangular patch on the cylinder:
#   u in [0, pi/2], z in [0, 5]
# 3D corners:
#   A: u=0,     z=0 → (5,0,0)
#   B: u=pi/2,  z=0 → (0,5,0)
#   C: u=pi/2,  z=5 → (0,5,5)
#   D: u=0,     z=5 → (5,0,5)

p_A = f.cartesian_point((R, 0.0, 0.0))
p_B = f.cartesian_point((0.0, R, 0.0))
p_C = f.cartesian_point((0.0, R, R))
p_D = f.cartesian_point((R, 0.0, R))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """EDGE_CURVE with SURFACE_CURVE (3D LINE + PCURVE) on the cylinder."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# E0: bottom A→B (u: 0→pi/2, z=0)  — normal orientation
e0 = mk_edge(v_A, v_B,
    (R, 0.0, 0.0),       (-1.0, 1.0, 0.0),  R,
    (0.0, 0.0),          (1.0, 0.0),          half_pi)

# E1: right B→C (z: 0→5, u=pi/2)  — DEFECT: pcurve reversed vs 3D curve
# 3D LINE goes from B=(0,5,0) → C=(0,5,5); forward in z.
# PCURVE goes from (pi/2, 5.0) → (0.0, 5.0) — REVERSED (starts at pcurve-z=5 end)
# byte assertion: contains(b'(0.0,5.0)') — this is the pcurve start point
e1 = mk_edge(v_B, v_C,
    (0.0, R, 0.0),       (0.0, 0.0, 1.0),   R,      # 3D: forward z=0→5
    (half_pi, R),        (-1.0, 0.0),         half_pi) # pcurve: reversed U pi/2→0 (NOT z)
# The pcurve start (0.0,5.0) is at the 3D end-point side: mismatched direction.

# E2: top C→D (u: pi/2→0, z=5)  — normal (reversed u)
e2 = mk_edge(v_C, v_D,
    (0.0, R, R),         (1.0, -1.0, 0.0),  R,
    (half_pi, R),        (-1.0, 0.0),         half_pi)

# E3: left D→A (z: 5→0, u=0)  — normal
e3 = mk_edge(v_D, v_A,
    (R, 0.0, R),         (0.0, 0.0, -1.0),  R,
    (0.0, R),            (0.0, -1.0),         R)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
