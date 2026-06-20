"""Gs007 — Pcurve U coordinate outside canonical [0, 2pi) seam range on
CYLINDRICAL_SURFACE (whole wire off by period).

Catalog claim: Pcurves of an entire wire on a CYLINDRICAL_SURFACE are shifted
by 2×2π in U (i.e. U in [4π, 6π] instead of [0, 2π]). The wire's UV image is
correctly shaped but offset by 4π from the canonical band. A receiver that does
not detect and re-base the period shift leaves the wire un-meshable.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: heal or reject.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry (radius=5).
  - All four wire edges use SURFACE_CURVE whose PCURVE LINE starts at U=4π
    (≈12.5663706144); whole wire is in band [4π, 6π] not [0, 2π].
    Byte assertions: contains(b'CYLINDRICAL_SURFACE('),
                     contains(b'12.5663706144').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    defect EDGE_CURVE 3D curves ARE the curve_3d of SURFACE_CURVEs whose
    PCURVE LINEs start at U=4π=12.5663706144 — whole wire off by 2 periods;
    non-canonical pcurve band drives shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs007",
    defect=(
        "CYLINDRICAL_SURFACE radius=5; all wire pcurve U coords shifted to "
        "[4pi,6pi] band (start U=12.5663706144=4pi); wire correctly shaped but "
        "offset by 2 full periods from canonical [0,2pi); IS "
        "ADVANCED_FACE.face_geometry; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: CYLINDRICAL_SURFACE, radius=5 ─────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs007_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
cyl  = f._emit_raw(f"CYLINDRICAL_SURFACE('gs007_cyl',#{ax3.eid},5.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Period shift: U_start = 4π (the byte assertion value)
four_pi = 4.0 * math.pi          # ≈ 12.5663706144
two_pi  = 2.0 * math.pi          # ≈ 6.2831853072
R = 5.0

# The wire covers a small rectangular patch on the cylinder:
#   canonical UV: u in [0, pi/2], z in [0, 4]  (v = z on cylinder)
# Shifted UV:   u in [4pi, 4pi+pi/2], z in [0, 4]
# 3D corners (same regardless of period shift):
#   (u=0, z=0) → (5,0,0); (u=pi/2, z=0) → (0,5,0)
#   (u=pi/2, z=4) → (0,5,4); (u=0, z=4) → (5,0,4)
p_a = f.cartesian_point((R, 0.0, 0.0))
p_b = f.cartesian_point((0.0, R, 0.0))
p_c = f.cartesian_point((0.0, R, 4.0))
p_d = f.cartesian_point((R, 0.0, 4.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

half_pi = math.pi / 2.0

def mk_cyl_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """Edge on cylinder with pcurve U offset into [4pi, 6pi] band."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    # pcurve start is the shifted-U version
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# Bottom: v_a→v_b  (u: 4pi→4pi+pi/2, z=0)
# 3D: arc on cylinder at z=0; approximate as line from (5,0,0)→(0,5,0)
e0 = mk_cyl_edge(v_a, v_b,
    (R, 0.0, 0.0),   (-1.0, 1.0, 0.0), R,
    (four_pi, 0.0),  (1.0, 0.0),        half_pi)

# Right: v_b→v_c  (z: 0→4, u=4pi+pi/2)
e1 = mk_cyl_edge(v_b, v_c,
    (0.0, R, 0.0),   (0.0, 0.0, 1.0), 4.0,
    (four_pi + half_pi, 0.0), (0.0, 1.0), 4.0)

# Top: v_c→v_d  (u: 4pi+pi/2→4pi, z=4)
e2 = mk_cyl_edge(v_c, v_d,
    (0.0, R, 4.0),   (1.0, -1.0, 0.0), R,
    (four_pi + half_pi, 4.0), (-1.0, 0.0), half_pi)

# Left: v_d→v_a  (z: 4→0, u=4pi)
e3 = mk_cyl_edge(v_d, v_a,
    (R, 0.0, 4.0),   (0.0, 0.0, -1.0), 4.0,
    (four_pi, 4.0),  (0.0, -1.0),       4.0)

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
