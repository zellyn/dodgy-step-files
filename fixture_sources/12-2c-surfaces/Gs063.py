"""Gs063 — Trimmed offset surface Bezier delegation.

Catalog claim: A PLANE trimmed to u∈[0.5, 2.5], v∈[0.5, 2.5] and offset by 2.0 via
OFFSET_SURFACE. ShapeUpgrade_ConvertSurfaceToBezierBasis.Compute() recursively converts
the basis (the RECTANGULAR_TRIMMED_SURFACE) without re-applying the trim domain or
the offset displacement. Result is an untrimmed, un-offset Bezier that must be rejected
or have constraints reapplied.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_SURFACE wrapping RECTANGULAR_TRIMMED_SURFACE (PLANE) IS the
    ADVANCED_FACE.face_geometry; offset=2.0 combined with trim [0.5,2.5]² IS the
    mechanism wired into face topology; Bezier delegation strips both IS the defect.
  - Byte assertions: contains(b'OFFSET_SURFACE'),
                     contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE (offset=2.0) wrapping RECTANGULAR_TRIMMED_SURFACE
    IS the ADVANCED_FACE.face_geometry; trim+offset combination IS the mechanism on face
    surface; Bezier Compute ignores trim and offset IS the defect wired into face topology.
  - shape_null driver: Bezier conversion strips trim and offset; healer must reject or
    reapply; strict kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs063",
    defect=(
        "OFFSET_SURFACE (distance=2.0) wrapping RECTANGULAR_TRIMMED_SURFACE (PLANE) IS "
        "ADVANCED_FACE.face_geometry; trim u∈[0.5,2.5] v∈[0.5,2.5] + offset IS the "
        "mechanism wired into face topology; Bezier delegation strips trim and offset "
        "IS the defect; shape_null"
    ),
)

# ── Underlying PLANE: XY-plane through origin, Z normal ──────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs063_pl_ax',#{pl_orig.eid},#{pl_zdir.eid},#{pl_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs063_plane',#{pl_ax.eid})")

# ── RECTANGULAR_TRIMMED_SURFACE: u∈[0.5, 2.5], v∈[0.5, 2.5] ────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
trimmed = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs063_trim',#{plane.eid},"
    "0.5,2.5,0.5,2.5,.T.,.T.)"
)

# ── OFFSET_SURFACE: offset the trimmed plane by 2.0 along normal ─────────────
# Byte assertion: contains(b'OFFSET_SURFACE')
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('gs063_offset',#{trimmed.eid},2.0,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the offset-trimmed surface ───────────────────────
# 3D corners: plane at z=0 offset by 2.0 → z=2.0; trim domain u,v ∈ [0.5, 2.5]
# (u=x, v=y for XY plane)
p_A = f.cartesian_point((0.5, 0.5, 2.0))
p_B = f.cartesian_point((2.5, 0.5, 2.0))
p_C = f.cartesian_point((2.5, 2.5, 2.0))
p_D = f.cartesian_point((0.5, 2.5, 2.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{offset_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom A→B (v=0.5, u: 0.5→2.5)
e0 = mk_edge_line(v_A, v_B,
                  (0.5, 0.5, 2.0), (1.0, 0.0, 0.0), 2.0,
                  (0.5, 0.5), (1.0, 0.0), 2.0)
# e1: right B→C (u=2.5, v: 0.5→2.5)
e1 = mk_edge_line(v_B, v_C,
                  (2.5, 0.5, 2.0), (0.0, 1.0, 0.0), 2.0,
                  (2.5, 0.5), (0.0, 1.0), 2.0)
# e2: top C→D (v=2.5, u: 2.5→0.5)
e2 = mk_edge_line(v_C, v_D,
                  (2.5, 2.5, 2.0), (-1.0, 0.0, 0.0), 2.0,
                  (2.5, 2.5), (-1.0, 0.0), 2.0)
# e3: left D→A (u=0.5, v: 2.5→0.5)
e3 = mk_edge_line(v_D, v_A,
                  (0.5, 2.5, 2.0), (0.0, -1.0, 0.0), 2.0,
                  (0.5, 2.5), (0.0, -1.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# OFFSET_SURFACE wrapping RECTANGULAR_TRIMMED_SURFACE IS the face_geometry; IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], offset_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
