"""Gs015 — Sliver face (high aspect ratio, two long edges within tolerance).

Catalog claim: A face whose two long bounding edges lie within tolerance of each
other (1e-5 mm apart in Y) so the face has near-zero area but a non-trivial
perimeter. Produced by surface-surface intersection at grazing angle. Distinguished
from Gs014 in that the perimeter is non-trivial (two full 250 mm edges); the
two short edges are 1e-5 mm.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: heal or reject.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - 4-edge EDGE_LOOP: long edges 250 mm in X, short edges 1e-5 mm in Y.
    Vertices: A=(0,0,0), B=(250,0,0), C=(250,1e-5,0), D=(0,1e-5,0).
  - Byte assertions: contains(b'1.0E-5'),
                     contains(b'(250.0,0.0,0.0)'),
                     count_entity_def(b'EDGE_CURVE') == 4.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; the four
    EDGE_CURVE 3D LINEs ARE the curve_3d of SURFACE_CURVEs whose PCURVE LINEs
    form a 250×1e-5 sliver rectangle; two long edges within tolerance of each
    other drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs015",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; 4-edge sliver rectangle 250 mm × 1e-5 mm; "
        "long edges (250.0,0.0,0.0), short edges 1.0E-5; two long edges within "
        "tolerance; count_entity_def(EDGE_CURVE)==4; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs015_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs015_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices: sliver 250×1e-5 mm
SLIVER = 1.0e-5
LONG   = 250.0

p_A = f.cartesian_point((0.0,  0.0,    0.0))
p_B = f.cartesian_point((LONG, 0.0,    0.0))   # byte assertion (250.0,0.0,0.0)
p_C = f.cartesian_point((LONG, SLIVER, 0.0))   # byte assertion 1.0E-5
p_D = f.cartesian_point((0.0,  SLIVER, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """EDGE_CURVE with SURFACE_CURVE (3D LINE + PCURVE) on the plane."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# E0: bottom A→B (long 250 mm in X)
e0 = mk_edge(v_A, v_B,
    (0.0,  0.0,    0.0), (1.0, 0.0, 0.0), LONG,
    (0.0,  0.0),         (1.0, 0.0),       LONG)

# E1: right B→C (short 1e-5 mm in Y)
e1 = mk_edge(v_B, v_C,
    (LONG, 0.0,    0.0), (0.0, 1.0, 0.0), SLIVER,
    (LONG, 0.0),         (0.0, 1.0),       SLIVER)

# E2: top C→D (long 250 mm in -X) — two long edges within tolerance of each other
e2 = mk_edge(v_C, v_D,
    (LONG, SLIVER, 0.0), (-1.0, 0.0, 0.0), LONG,
    (LONG, SLIVER),      (-1.0, 0.0),       LONG)

# E3: left D→A (short 1e-5 mm in -Y)
e3 = mk_edge(v_D, v_A,
    (0.0,  SLIVER, 0.0), (0.0, -1.0, 0.0), SLIVER,
    (0.0,  SLIVER),      (0.0, -1.0),       SLIVER)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
