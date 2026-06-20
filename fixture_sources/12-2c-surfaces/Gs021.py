"""Gs021 — Line displaced from true position (FPX Expert PCB).

Catalog claim: EDGE_CURVE based on a LINE whose direction is correct but whose
pnt (origin) is parallel-displaced from the line that actually passes through
both vertex points. Vertex points are approximately equidistant off the line.
Translator must shift the line to pass through the vertices.

Reproducer: VERTEX_POINT(A=(0,0,0)), VERTEX_POINT(B=(10,0,0)),
EDGE_CURVE referring to LINE(pnt=(0,0,0.5), dir=(1,0,0)) — line is parallel
to AB but offset 0.5 in Z.

OCC behavior: silently accepts (no diagnostic, empty result).
Expected: occt=empty. Closure intent: heal (shift line to vertices).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry (small rectangular face in XY,
    giving the edge a surface context so the defect is wired into face topology).
  - Defect EDGE_CURVE: 3D LINE(pnt=(0,0,0.5), dir=(1,0,0)) — direction correct,
    pnt offset 0.5 in Z from both endpoint vertex positions which lie at Z=0.
    The LINE IS the curve_3d of the SURFACE_CURVE of the defect EDGE_CURVE.
  - Byte assertions: contains(b'(0.0,0.0,0.5)'),
                     contains(b'(10.0,0.0,0.0)'),
                     contains(b'LINE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: the defect EDGE_CURVE 3D LINE IS the curve_3d of its
    SURFACE_CURVE; LINE pnt=(0.0,0.0,0.5) is displaced 0.5 from both vertex
    endpoints at Z=0; PLANE IS the ADVANCED_FACE.face_geometry; displaced line
    drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs021",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; defect EDGE_CURVE IS LINE with "
        "pnt=(0.0,0.0,0.5) displaced 0.5 in Z from vertices at Z=0; "
        "direction=(1,0,0) correct; vertex B=(10.0,0.0,0.0); "
        "LINE pnt parallel-displaced from edge; shape_null=True"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs021_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs021_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices at Z=0
WIDTH = 10.0
HEIGHT = 5.0

p_A  = f.cartesian_point((0.0,   0.0,    0.0))   # A = (0,0,0)
p_B  = f.cartesian_point((WIDTH, 0.0,    0.0))   # B = (10,0,0) — byte assertion
p_C  = f.cartesian_point((WIDTH, HEIGHT, 0.0))
p_D  = f.cartesian_point((0.0,   HEIGHT, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_normal(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """Normal EDGE_CURVE — line passes through endpoints."""
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

# ── Defect edge E0: A→B, 3D LINE displaced +0.5 in Z ─────────────────────────
# byte assertion: contains(b'(0.0,0.0,0.5)') — the displaced pnt
# byte assertion: contains(b'(10.0,0.0,0.0)') — vertex B
# byte assertion: contains(b'LINE(')
p_line_pnt = f.cartesian_point((0.0, 0.0, 0.5))   # displaced pnt — NOT at Z=0
d_line     = f.direction((1.0, 0.0, 0.0))          # direction correct
v_line     = f.vector(d_line, WIDTH)
l3_defect  = f.line(p_line_pnt, v_line)             # IS the defect 3D curve_3d

# Pcurve for E0 on plane (UV coordinates)
p2_e0 = f.cartesian_point((0.0, 0.0))
d2_e0 = f.direction((1.0, 0.0))
v2_e0 = f.vector(d2_e0, WIDTH)
l2_e0 = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{plane.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{l3_defect.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

# E1: B→C (right side, normal)
e1 = mk_edge_normal(v_B, v_C,
    (WIDTH, 0.0,    0.0), (0.0, 1.0, 0.0), HEIGHT,
    (WIDTH, 0.0),         (0.0, 1.0),       HEIGHT)

# E2: C→D (top, normal)
e2 = mk_edge_normal(v_C, v_D,
    (WIDTH, HEIGHT, 0.0), (-1.0, 0.0, 0.0), WIDTH,
    (WIDTH, HEIGHT),      (-1.0, 0.0),       WIDTH)

# E3: D→A (left side, normal)
e3 = mk_edge_normal(v_D, v_A,
    (0.0, HEIGHT, 0.0), (0.0, -1.0, 0.0), HEIGHT,
    (0.0, HEIGHT),      (0.0, -1.0),       HEIGHT)

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
