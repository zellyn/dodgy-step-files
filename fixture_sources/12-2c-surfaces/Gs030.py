"""Gs030 — Edge geometry inconsistent with adjacent faces' actual intersection.

Catalog claim: After local edits (face translation, blend suppression, partial
defeaturing) an edge's stored 3D curve no longer matches the geometric
intersection of its two host faces.  Edge survives as topology but its curve is
stale, leading to large tolerances or visible cracks.  Reproducer: ADVANCED_FACE
on CYLINDRICAL_SURFACE of radius 10 mm whose EDGE_CURVE is a LINE 0.5 mm
radially off the cylinder.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE radius=10 IS the ADVANCED_FACE.face_geometry.
  - Defect EDGE_CURVE: 3D LINE IS placed at radius 10.5 (0.5 mm off surface)
    instead of on the cylinder surface at radius 10.
  - Point (10.5,0.0,0.0) satisfies byte assertion: a point on the LINE origin at
    the off-surface location.
  - The LINE IS the curve_3d of the SURFACE_CURVE of the defect EDGE_CURVE.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE('),
                     contains(b'(10.5,0.0,0.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE radius=10 IS the
    ADVANCED_FACE.face_geometry; the defect EDGE_CURVE 3D LINE IS the curve_3d
    of its SURFACE_CURVE; LINE origin at (10.5,0.0,0.0) is 0.5 mm off the
    cylinder surface; stale edge curve drives shape(1) (live OCC heals).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs030",
    defect=(
        "CYLINDRICAL_SURFACE radius=10 IS ADVANCED_FACE.face_geometry; "
        "defect EDGE_CURVE curve_3d IS LINE with origin (10.5,0.0,0.0) — "
        "0.5 mm radially off cylinder surface; stale edge after face translation; "
        "shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: CYLINDRICAL_SURFACE, radius=10 ─────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs030_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
cyl  = f._emit_raw(f"CYLINDRICAL_SURFACE('gs030_cyl',#{ax3.eid},10.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

R   = 10.0
# Patch on cylinder: u in [0, pi/2], v (height) in [0, 5].
# 3D corners:
#   A: (R,0,0)   u=0,  v=0
#   B: (0,R,0)   u=π/2, v=0
#   C: (0,R,5)   u=π/2, v=5
#   D: (R,0,5)   u=0,  v=5
p_A3 = f.cartesian_point((R,   0.0, 0.0))
p_B3 = f.cartesian_point((0.0, R,   0.0))
p_C3 = f.cartesian_point((0.0, R,   5.0))
p_D3 = f.cartesian_point((R,   0.0, 5.0))

v_A = f.vertex_point(p_A3)
v_B = f.vertex_point(p_B3)
v_C = f.vertex_point(p_C3)
v_D = f.vertex_point(p_D3)

# ── Defect edge E0: A→B, 3D LINE at radius 10.5 (byte assertion: (10.5,0.0,0.0)) ─
# True intersection of two cylinder faces at u=0 would be a vertical line at (10,0,z),
# but we emit a line whose pnt is at radius 10.5: origin (10.5,0.0,0.0).
# The line direction approximates the chord A→B.
p_defect_orig = f.cartesian_point((10.5, 0.0, 0.0))   # byte assertion (10.5,0.0,0.0)
dx = 0.0 - 10.5
dy = R   - 0.0
chord_len = math.sqrt(dx*dx + dy*dy)
d3_defect = f.direction((dx/chord_len, dy/chord_len, 0.0))
v3_defect = f.vector(d3_defect, chord_len)
l3_defect = f.line(p_defect_orig, v3_defect)

# pcurve for E0 on cyl (u goes from 0 to π/2, v=0)
p2_e0  = f.cartesian_point((0.0, 0.0))
d2_e0  = f.direction((1.0, 0.0))
v2_e0  = f.vector(d2_e0, math.pi/2)
l2_e0  = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{cyl.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{l3_defect.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

def mk_edge_cyl(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
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
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# E1: B→C, vertical line at (0,R,0)→(0,R,5), v increases, u=π/2
e1 = mk_edge_cyl(v_B, v_C,
    (0.0, R, 0.0), (0.0, 0.0, 1.0), 5.0,
    (math.pi/2, 0.0), (0.0, 1.0), 5.0)

# E2: C→D, arc top at v=5, u: π/2→0
e2 = mk_edge_cyl(v_C, v_D,
    (0.0, R, 5.0), (1.0, -1.0, 0.0), chord_len,
    (math.pi/2, 5.0), (-1.0, 0.0), math.pi/2)

# E3: D→A, vertical line at (R,0,5)→(R,0,0), v decreases, u=0
e3 = mk_edge_cyl(v_D, v_A,
    (R, 0.0, 5.0), (0.0, 0.0, -1.0), 5.0,
    (0.0, 5.0), (0.0, -1.0), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE IS the face_geometry; defect LINE IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
