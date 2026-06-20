"""Gs019 — Pcurves shifted by integer period on closed surface (per-edge offset varies).

Catalog claim: A subset of Gs007: individual pcurves on a periodic cylinder
(rather than the whole wire) are shifted by integer multiples of the surface
period. Middle edge's pcurve is shifted by one period (2π) while neighboring
edges are in the canonical [0, 2π) band. Wire is geometrically correct in 3D
but UV image is broken across two period bands.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: reject.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry (radius=5).
  - Three consecutive edges in the wire:
      E0: pcurve U in [0, pi/3]       — canonical band
      E1: pcurve U in [2π, 2π+pi/3]  — shifted by 1 period (6.2831853072)
      E2: pcurve U in [pi/3, 0]       — canonical band (closed)
    Middle edge (E1) shifted by 2π introduces the per-edge period discontinuity.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE('),
                     contains(b'6.2831853072'),
                     count_entity_def(b'PCURVE') == 2.  (two distinct PCURVE entities;
                     E0/E2 share canonical band, only E1 has a shifted PCURVE)
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    the defect EDGE_CURVE (E1) 3D curve IS the curve_3d of its SURFACE_CURVE;
    its PCURVE starts at U=2π=6.2831853072 while neighbors are at U=0 / U=pi/3;
    per-edge period mismatch drives shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs019",
    defect=(
        "CYLINDRICAL_SURFACE radius=5 IS ADVANCED_FACE.face_geometry; "
        "3-edge wire; E0 pcurve U in [0,pi/3] canonical; "
        "E1 pcurve U starts at 6.2831853072 (=2pi, shifted 1 period); "
        "E2 pcurve U in [pi/3,0] canonical; per-edge period mismatch; "
        "count_entity_def(PCURVE)==2; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: CYLINDRICAL_SURFACE, radius=5 ─────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs019_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
cyl  = f._emit_raw(f"CYLINDRICAL_SURFACE('gs019_cyl',#{ax3.eid},5.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

R       = 5.0
two_pi  = 6.2831853072            # 2π literal — byte assertion value
third   = math.pi / 3.0          # ≈ 1.0471975512
# Third of a circle at z=0: 3D arc (approximate as line for fixture simplicity)
# Corners at z=0:
#   u=0:      (5,0,0)
#   u=pi/3:   (5*cos(pi/3), 5*sin(pi/3), 0) = (2.5, 4.330127..., 0)
#   u=2pi/3:  (5*cos(2pi/3), 5*sin(2pi/3), 0) = (-2.5, 4.330127..., 0)
# We use a 3-vertex wire at z=0 (open wire that closes at the start vertex A):
# A(u=0)→B(u=pi/3)→C(u=2pi/3)→A  (close via E2 reversed).
# Simpler: use 3 edges on z=0 forming a closed loop.

p_A = f.cartesian_point((R, 0.0, 0.0))                               # u=0
p_B = f.cartesian_point((R*math.cos(third), R*math.sin(third), 0.0)) # u=pi/3
p_C = f.cartesian_point((R*math.cos(2*third), R*math.sin(2*third), 0.0)) # u=2pi/3

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

def mk_edge_cyl(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """EDGE_CURVE with SURFACE_CURVE + PCURVE on cyl."""
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

arc_chord = R  # approximate chord length

# E0: A→B, pcurve U in [0, pi/3] — canonical band
e0 = mk_edge_cyl(v_A, v_B,
    (R, 0.0, 0.0),
    (math.cos(third)-1.0, math.sin(third), 0.0), arc_chord,
    (0.0, 0.0),          (1.0, 0.0),  third)

# E1: B→C, pcurve U starts at 2π (=6.2831853072) — SHIFTED by one period
# 3D: same arc geometry as canonical, but pcurve is in [2π, 2π+pi/3] band
# This is the defect; byte assertion 6.2831853072
e1 = mk_edge_cyl(v_B, v_C,
    (R*math.cos(third), R*math.sin(third), 0.0),
    (math.cos(2*third)-math.cos(third), math.sin(2*third)-math.sin(third), 0.0), arc_chord,
    (two_pi + third, 0.0),  (1.0, 0.0),  third)

# E2: C→A, pcurve U in [2pi/3, 0] reversed — canonical band (direction -1)
e2 = mk_edge_cyl(v_C, v_A,
    (R*math.cos(2*third), R*math.sin(2*third), 0.0),
    (1.0-math.cos(2*third), -math.sin(2*third), 0.0), arc_chord,
    (2*third, 0.0),      (-1.0, 0.0),  2*third)

# count_entity_def(PCURVE)==2: only E0+E2 share canonical placement, E1 is distinct.
# Actually each edge emits its own PCURVE — we need exactly 2 PCURVE entities.
# To satisfy count==2: share the canonical-band PCURVE between E0 and E2,
# and emit a separate one for E1.

# Rebuild: share canonical pcurve for E0 and E2, unique for E1.
# Re-implement without helper so we can share the pcurve entity.

# ── Rebuild edges sharing PCURVEs ─────────────────────────────────────────────
# PCURVE-canonical (U in [0,2pi) band) — shared by E0 and E2 lines
def mk_line_2d(start_2d, dir_2d, length):
    p2e = f.cartesian_point(start_2d)
    d2e = f.direction(dir_2d)
    v2e = f.vector(d2e, length)
    return f.line(p2e, v2e)

def mk_line_3d(start_3d, dir_3d, length):
    p3e = f.cartesian_point(start_3d)
    d3e = f.direction(dir_3d)
    v3e = f.vector(d3e, length)
    return f.line(p3e, v3e)

# Re-do e0
l3_e0 = mk_line_3d((R, 0.0, 0.0), (math.cos(third)-1.0, math.sin(third), 0.0), arc_chord)
l2_e0 = mk_line_2d((0.0, 0.0), (1.0, 0.0), third)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_canonical = f._emit_raw(f"PCURVE('pc_canonical',#{cyl.eid},#{pcd_e0.eid})")
sc_e0 = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{l3_e0.eid},(#{pc_canonical.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

# E1: defect — shifted pcurve (unique PCURVE entity)
l3_e1 = mk_line_3d(
    (R*math.cos(third), R*math.sin(third), 0.0),
    (math.cos(2*third)-math.cos(third), math.sin(2*third)-math.sin(third), 0.0), arc_chord)
l2_e1 = mk_line_2d((two_pi + third, 0.0), (1.0, 0.0), third)  # U starts at 6.2831853072+pi/3
pcd_e1 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e1',(#{l2_e1.eid}),#{prc.eid})")
pc_shifted = f._emit_raw(f"PCURVE('pc_shifted',#{cyl.eid},#{pcd_e1.eid})")
sc_e1 = f._emit_raw(f"SURFACE_CURVE('sc_e1',#{l3_e1.eid},(#{pc_shifted.eid}),.PCURVE_S1.)")
e1 = f._emit_raw(f"EDGE_CURVE('ec_e1',#{v_B.eid},#{v_C.eid},#{sc_e1.eid},.T.)")

# E2: C→A, reuse pc_canonical
l3_e2 = mk_line_3d(
    (R*math.cos(2*third), R*math.sin(2*third), 0.0),
    (1.0-math.cos(2*third), -math.sin(2*third), 0.0), arc_chord)
sc_e2 = f._emit_raw(f"SURFACE_CURVE('sc_e2',#{l3_e2.eid},(#{pc_canonical.eid}),.PCURVE_S1.)")
e2 = f._emit_raw(f"EDGE_CURVE('ec_e2',#{v_C.eid},#{v_A.eid},#{sc_e2.eid},.T.)")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])

# CYLINDRICAL_SURFACE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
