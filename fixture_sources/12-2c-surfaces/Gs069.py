"""Gs069 — Surface of revolution with near-zero axis magnitude.

Catalog claim: A SURFACE_OF_REVOLUTION whose axis direction vector has magnitude
near zero (1e-11). IsDegenerated() checks absolute values of individual vector
components instead of computing the true Euclidean norm, so the near-zero axis
is missed; the degenerate surface is silently accepted.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION (profile line swept around near-zero axis) IS the
    ADVANCED_FACE.face_geometry; axis direction (1e-11, 0.0, 0.0) IS the near-zero
    magnitude mechanism wired into face topology; IsDegenerated component-check
    misses norm IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION'),
                     contains(b'1.E-11').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION IS the ADVANCED_FACE.face_geometry;
    axis direction vector magnitude 1e-11 (near-zero) IS the mechanism wired into face
    topology; IsDegenerated per-component check, not Euclidean norm IS the defect.
  - shape_null driver: undetected near-zero axis → degenerate revolution surface;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs069",
    defect=(
        "SURFACE_OF_REVOLUTION IS ADVANCED_FACE.face_geometry; "
        "axis direction vector magnitude 1e-11 (near-zero) IS the mechanism wired "
        "into face topology; IsDegenerated per-component check misses zero norm IS "
        "the defect; shape_null"
    ),
)

# ── Profile: a line segment along the Y-axis (the swept generator) ───────────
prof_p0 = f.cartesian_point((1.0, 0.0, 0.0))
prof_p1 = f.cartesian_point((1.0, 1.0, 0.0))
prof_dir = f.direction((0.0, 1.0, 0.0))
prof_vec = f.vector(prof_dir, 1.0)
prof_line = f.line(prof_p0, prof_vec)
v_prof0 = f.vertex_point(prof_p0)
v_prof1 = f.vertex_point(prof_p1)
prof_edge_curve = f.edge_curve(v_prof0, v_prof1, prof_line)

# ── Revolution axis: origin + near-zero direction (1e-11, 0, 0) ──────────────
# Byte assertion: contains(b'1.E-11')
rev_orig = f.cartesian_point((0.0, 0.0, 0.0))
# Near-zero axis direction: magnitude ≈ 1e-11
rev_zdir = f._emit_raw("DIRECTION('gs069_degenaxis',(1.E-11,0.0,0.0))")
rev_xdir = f.direction((1.0, 0.0, 0.0))
rev_ax   = f._emit_raw(
    f"AXIS1_PLACEMENT('gs069_rev_ax',#{rev_orig.eid},#{rev_zdir.eid})"
)

# ── SURFACE_OF_REVOLUTION: sweep profile around near-zero axis ───────────────
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION')
sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs069_sor',#{prof_line.eid},#{rev_ax.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the degenerate revolution surface ────────────────
# Simple rectangular boundary in parameter space u∈[0,1], v∈[0,1]
p_A = f.cartesian_point((1.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))   # degenerate: near-zero axis collapses 3D
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((1.0, 1.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(f.cartesian_point((1.0, 0.0, 1.0)))
v_C = f.vertex_point(f.cartesian_point((1.0, 1.0, 1.0)))
v_D = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sor.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Boundary in approximate 3D (near-zero axis means revolution barely moves)
e0 = mk_edge_line(v_A, v_B,
                  (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 1.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (1.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION IS the face_geometry; near-zero axis IS the mechanism on face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], sor)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
