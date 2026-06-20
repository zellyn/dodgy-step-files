"""Gs014 — Zero-area / sliver / degenerate ADVANCED_FACE (sliver, spot, strip, pin;
tiny aspect-ratio rectangle).

Catalog claim: A 4-edge ADVANCED_FACE on a PLANE whose two long sides are 100 mm
and two short sides are 1e-7 mm; area = 100 × 1e-7 = 1e-5 mm², far below any
reasonable chord tolerance. The underlying PLANE is well-defined; the degenerate
area comes from the trim boundary collapsing one parametric direction.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: reject (or drop + merge incident edges).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - 4-edge EDGE_LOOP: two long edges (100 mm in X) and two infinitesimal short
    edges (1e-7 mm in Y); face area ≈ 0.
    Vertices: A=(0,0,0), B=(100,0,0), C=(100,1e-7,0), D=(0,1e-7,0).
  - Byte assertions: contains(b'1.0E-7'),
                     contains(b'(100.0,0.0,0.0)'),
                     count_entity_def(b'ORIENTED_EDGE') == 4.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; the four
    EDGE_CURVE 3D LINEs ARE the curve_3d of SURFACE_CURVEs whose PCURVE LINEs
    form a 100×1e-7 sliver rectangle on the plane; near-zero area drives
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs014",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; 4-edge sliver rectangle 100 mm × 1e-7 mm; "
        "long edges (100.0,0.0,0.0), short edges 1.0E-7; area≈0; "
        "count_entity_def(ORIENTED_EDGE)==4; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs014_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs014_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices of 100×1e-7 sliver rectangle in XY plane
SLIVER = 1.0e-7
LONG   = 100.0

p_A = f.cartesian_point((0.0,    0.0,    0.0))   # A
p_B = f.cartesian_point((LONG,   0.0,    0.0))   # B — byte assertion (100.0,0.0,0.0)
p_C = f.cartesian_point((LONG,   SLIVER, 0.0))   # C
p_D = f.cartesian_point((0.0,    SLIVER, 0.0))   # D — byte assertion 1.0E-7

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

# E0: bottom A→B (long, 100 mm in X)
e0 = mk_edge(v_A, v_B,
    (0.0,  0.0,    0.0), (1.0, 0.0, 0.0), LONG,
    (0.0,  0.0),         (1.0, 0.0),       LONG)

# E1: right B→C (short, 1e-7 mm in Y)  — byte assertion 1.0E-7
e1 = mk_edge(v_B, v_C,
    (LONG, 0.0,    0.0), (0.0, 1.0, 0.0), SLIVER,
    (LONG, 0.0),         (0.0, 1.0),       SLIVER)

# E2: top C→D (long, 100 mm in -X)
e2 = mk_edge(v_C, v_D,
    (LONG, SLIVER, 0.0), (-1.0, 0.0, 0.0), LONG,
    (LONG, SLIVER),      (-1.0, 0.0),       LONG)

# E3: left D→A (short, 1e-7 mm in -Y)
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
