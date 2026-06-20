"""Gs111 — ShapeAnalysis_Surface.IsDegenerated SURFACE_OF_LINEAR_EXTRUSION zero-extrusion.

Catalog claim: SURFACE_OF_LINEAR_EXTRUSION with zero-magnitude extrusion vector;
surface collapses to base curve but IsDegenerated's test uses Length() which
returns positive value for zero VECTOR magnitude due to sign bug.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_LINEAR_EXTRUSION with zero-magnitude extrusion VECTOR (0,0,0)
    IS the ADVANCED_FACE.face_geometry; the collapsed (degenerate) surface
    IS the mechanism wired into face topology; IsDegenerated() returns False
    due to sign bug in Length() computation and fails to flag the collapse
    IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_LINEAR_EXTRUSION').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_LINEAR_EXTRUSION (extrusion vector magnitude=0)
    IS the ADVANCED_FACE.face_geometry; zero-magnitude extrusion that collapses
    surface to a curve IS the mechanism wired into face topology;
    IsDegenerated() Length() sign-bug returns False for zero vector IS the defect.
  - shape_null driver: degenerate collapsed surface; strict kernels reject;
    empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs111",
    defect=(
        "SURFACE_OF_LINEAR_EXTRUSION (extrusion vector magnitude=0) "
        "IS ADVANCED_FACE.face_geometry; "
        "zero-magnitude extrusion collapsing surface to base curve IS "
        "the mechanism wired into face topology; "
        "IsDegenerated() Length() sign-bug returns False for zero vector IS the defect; "
        "shape_null"
    ),
)

# ── Base curve: unit-length LINE along X axis ─────────────────────────────────
base_orig = f.cartesian_point((0.0, 0.0, 0.0))
base_dir  = f.direction((1.0, 0.0, 0.0))
base_vec  = f.vector(base_dir, 1.0)
base_line = f.line(base_orig, base_vec)

# ── Zero-magnitude extrusion direction ────────────────────────────────────────
# The defect mechanism: VECTOR with zero magnitude — surface collapses to curve.
zero_dir = f.direction((0.0, 0.0, 1.0))   # direction must be non-zero (STEP requires unit)
zero_vec = f.vector(zero_dir, 0.0)         # but magnitude = 0 → zero extrusion

# ── SURFACE_OF_LINEAR_EXTRUSION with zero-magnitude vector ───────────────────
# Byte assertion: contains(b'SURFACE_OF_LINEAR_EXTRUSION')
sole = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('gs111_sole',#{base_line.eid},#{zero_vec.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in (u,v) parameter space ──────────────────────
# u in [0,1] = along base line; v in [0,1] = along zero-magnitude extrusion.
# All v-values map to same 3D point as v=0 → degenerate collapsed surface.
# 3D corners: surface(u,v) = (u,0,0) + v*(0,0,0) = (u,0,0) for all v.
p_A = f.cartesian_point((0.0, 0.0, 0.0))   # (u=0, v=0)
p_B = f.cartesian_point((1.0, 0.0, 0.0))   # (u=1, v=0)
p_C = f.cartesian_point((1.0, 0.0, 0.0))   # (u=1, v=1) — same 3D as B (collapsed!)
p_D = f.cartesian_point((0.0, 0.0, 0.0))   # (u=0, v=1) — same 3D as A (collapsed!)

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

# e0: bottom A→B (v=0, u: 0→1) — base curve, 3D length=1
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# e1: right B→C (u=1, v: 0→1) — extrusion direction; zero 3D length (collapsed)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.001,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# e2: top C→D (v=1, u: 1→0) — collapsed to same as e0 (zero extrusion)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# e3: left D→A (u=0, v: 1→0) — extrusion direction; zero 3D length (collapsed)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 0.001,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_LINEAR_EXTRUSION (zero-magnitude vector) IS the face_geometry;
# collapsed degenerate surface IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sole)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
