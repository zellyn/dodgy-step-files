"""Gs092 — ShapeAnalysis_Surface.ComputeBoundIsos extrusion-direction reset.

Catalog claim: Surface of linear extrusion with non-unit direction vector (2.0,0.0,0.0).
Cached BoundIsos reflect pre-normalization range; recomputation fails to invalidate cache.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_LINEAR_EXTRUSION (basis=LINE along X, extrusion VECTOR direction
    (2.0,0.0,0.0) magnitude=1.0 — non-unit extrusion direction) IS the
    ADVANCED_FACE.face_geometry; non-unit extrusion direction vector (2.0,0.0,0.0)
    IS the mechanism wired into face topology; ComputeBoundIsos caches range
    from pre-normalization, cache invalidation fails IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_LINEAR_EXTRUSION'),
                     contains(b'2.0,0.0,0.0').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_LINEAR_EXTRUSION IS the ADVANCED_FACE.face_geometry;
    VECTOR with non-unit DIRECTION (2.0,0.0,0.0) IS the mechanism wired into face
    topology; ComputeBoundIsos caches BoundIsos from pre-normalization parameter
    range and cache invalidation on normalization fails IS the defect.
  - shape_null driver: incorrect cached isoparametric bounds; strict kernels
    reject inconsistent surface bounds; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs092",
    defect=(
        "SURFACE_OF_LINEAR_EXTRUSION IS ADVANCED_FACE.face_geometry; "
        "extrusion VECTOR direction (2.0,0.0,0.0) non-unit IS the mechanism "
        "wired into face topology; ComputeBoundIsos caches pre-normalization "
        "range, cache invalidation fails IS the defect; shape_null"
    ),
)

# ── Basis LINE along Y ─────────────────────────────────────────────────────────
basis_orig = f.cartesian_point((0.0, 0.0, 0.0))
basis_dir  = f.direction((0.0, 1.0, 0.0))
basis_vec  = f.vector(basis_dir, 1.0)
basis_line = f.line(basis_orig, basis_vec)

# ── Extrusion VECTOR: non-unit DIRECTION (2.0,0.0,0.0), magnitude 1.0 ─────────
# Byte assertion: contains(b'2.0,0.0,0.0')
extr_dir = f.direction((2.0, 0.0, 0.0))   # non-unit direction — the mechanism
extr_vec = f.vector(extr_dir, 1.0)

# ── SURFACE_OF_LINEAR_EXTRUSION with non-unit direction ───────────────────────
# Byte assertion: contains(b'SURFACE_OF_LINEAR_EXTRUSION')
sole = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('gs092_sole',#{basis_line.eid},#{extr_vec.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the non-unit-direction extrusion surface ──────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sole.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 1.0, (0.0,0.0), (1.0,0.0), 1.0)
e1 = mk_edge_line(v_B, v_C, (1.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (1.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (1.0,1.0,0.0), (-1.0,0.0,0.0), 1.0, (1.0,1.0), (-1.0,0.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_LINEAR_EXTRUSION IS the face_geometry; non-unit direction (2.0,0.0,0.0) IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sole)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
