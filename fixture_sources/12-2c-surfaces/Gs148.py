"""Gs148 — DegeneratedValues singularity gap classification.

Catalog claim: ShapeAnalysis_Surface::DegeneratedValues() classifies edge
points as degenerate by measuring proximity to singularity loci. When
myNbDeg < 0 (singularities uninitialized or stale) or the tolerance
threshold differs from that used in ComputeSingularities, the gap metric
fails to flag degenerate edges near apex, poles, or seams. The healer then
skips the required edge-collapse or redistribution step.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE (semi-angle pi/4) IS the ADVANCED_FACE.face_geometry;
    face boundary degenerate edge at cone apex (v=0, all u collapse to apex,
    gap metric = 0) IS the mechanism wired into face topology;
    DegeneratedValues singularity-gap classification with stale myNbDeg
    IS the defect.
  - Byte assertions: contains(b'CONICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    degenerate apex edge (gap=0, singularity locus at v=0) IS the mechanism
    wired into face topology; DegeneratedValues stale-myNbDeg tolerance
    mismatch IS the defect.
  - shape_null driver: degenerate edge not classified; healer skips
    edge collapse; strict kernels reject malformed edge; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs148",
    defect=(
        "CONICAL_SURFACE (semi-angle pi/4, apex at origin) "
        "IS ADVANCED_FACE.face_geometry; degenerate apex edge (v=0, all u "
        "collapse to apex, gap metric=0) IS the mechanism wired into face "
        "topology; DegeneratedValues stale myNbDeg singularity-gap "
        "classification miss IS the defect; shape_null"
    ),
)

# ── CONICAL_SURFACE with apex singularity ──────────────────────────────────────
# Byte assertion: contains(b'CONICAL_SURFACE')
# half_angle = pi/4 (45 deg). At v=0: apex (0,0,0).
# DegeneratedValues must recognize the apex edge as degenerate (gap=0),
# but stale myNbDeg causes it to miss the classification.
HALF_ANGLE = math.pi / 4.0
TWO_PI = 2.0 * math.pi

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs148_cone_ax',#{cone_orig.eid},#{cone_zdir.eid},#{cone_xdir.eid})"
)
cone = f._emit_raw(f"CONICAL_SURFACE('gs148_cone',#{cone_ax.eid},0.0,{HALF_ANGLE:.10f})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: partial U sweep including apex singularity ─────────────────
# CONICAL_SURFACE: x = v*cos(u)*cos(ha), y = v*sin(u)*cos(ha), z = v*sin(ha).
# Face: u in [0, pi/2], v in [0, 2.0].
# Bottom edge (v=0): apex — degenerate, zero gap.
# This IS the edge that DegeneratedValues must classify as degenerate.
cos_ha = math.cos(HALF_ANGLE)
sin_ha = math.sin(HALF_ANGLE)
u_right = math.pi / 2.0
v_top = 2.0

def cone_pt(u, v):
    return (v * math.cos(u) * cos_ha, v * math.sin(u) * cos_ha, v * sin_ha)

apex_3d = cone_pt(0.0, 0.0)   # (0, 0, 0)
C3 = cone_pt(0.0, v_top)
D3 = cone_pt(u_right, v_top)

p_apex_L = f.cartesian_point(apex_3d)
p_apex_R = f.cartesian_point(apex_3d)
p_C = f.cartesian_point(C3)
p_D = f.cartesian_point(D3)

v_apex_L = f.vertex_point(p_apex_L)
v_apex_R = f.vertex_point(p_apex_R)
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
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

dv = v_top  # v_top - 0

# Degenerate apex edge: apex_L → apex_R, u=0→pi/2 at v=0 (3D: zero-length)
# Gap = 0 here; this IS the edge DegeneratedValues must classify.
e0 = mk_edge_line(v_apex_L, v_apex_R,
                  apex_3d, (1.0, 0.0, 0.0), 1e-6,
                  (0.0, 0.0), (1.0, 0.0), u_right)
# Right lateral: apex_R → D, u=u_right, v=0→v_top
e1 = mk_edge_line(v_apex_R, v_D,
                  apex_3d, (D3[0], D3[1], D3[2]), dv,
                  (u_right, 0.0), (0.0, 1.0), dv)
# Top: D → C, u=u_right→0 at v=v_top
top_len = v_top * u_right * cos_ha
e2 = mk_edge_line(v_D, v_C,
                  D3, (C3[0]-D3[0], C3[1]-D3[1], 0.0), top_len,
                  (u_right, v_top), (-1.0, 0.0), u_right)
# Left lateral: C → apex_L, u=0, v=v_top→0
e3 = mk_edge_line(v_C, v_apex_L,
                  C3, (-C3[0], -C3[1], -C3[2]), dv,
                  (0.0, v_top), (0.0, -1.0), dv)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CONICAL_SURFACE IS the face_geometry; degenerate apex edge (gap=0, v=0
# singularity locus) IS the mechanism wired into face topology — exercises
# DegeneratedValues stale-myNbDeg gap-classification miss.
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
