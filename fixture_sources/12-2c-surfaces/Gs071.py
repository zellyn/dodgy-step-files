"""Gs071 — ProjectDegenerated arithmetic-mean redistribution on cone apex.

Catalog claim: A SURFACE_OF_REVOLUTION that forms a cone (generator line from apex
to rim). The apex at v=0 is a singularity (all u values map to the same 3D point).
A degenerate edge loop collapsing onto the apex should redistribute parameter
intervals by arc-length-weighted accumulation, but the implementation uses an
arithmetic mean, producing an incorrect parametric distribution at the apex.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION (conical: generator through apex) IS the
    ADVANCED_FACE.face_geometry; degenerate edge at cone apex (v=0 singularity)
    IS the mechanism wired into face topology; ProjectDegenerated uses arithmetic
    mean redistribution instead of arc-length IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION'),
                     contains(b'gs071').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION (cone) IS the ADVANCED_FACE.face_geometry;
    degenerate edge at v=0 apex (all u collapse to one point) IS the mechanism wired
    into face topology; arithmetic mean redistribution instead of arc-length IS the defect.
  - shape_null driver: incorrect parameter redistribution at apex; strict kernels
    reject degenerate topology; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs071",
    defect=(
        "SURFACE_OF_REVOLUTION (cone, generator through apex) IS ADVANCED_FACE.face_geometry; "
        "degenerate edge at cone apex v=0 (all u→same 3D point) IS the mechanism wired "
        "into face topology; ProjectDegenerated arithmetic-mean redistribution (not arc-length) "
        "IS the defect; shape_null"
    ),
)

# ── Conical generator: a line from the apex (origin) outward ─────────────────
# Apex at (0,0,0); generator goes radially outward in X at Z=0, length 1.
# Revolution around Z-axis → cone with apex at origin.
apex_pt  = f.cartesian_point((0.0, 0.0, 0.0))
rim_pt   = f.cartesian_point((1.0, 0.0, 0.0))
gen_dir  = f.direction((1.0, 0.0, 0.0))
gen_vec  = f.vector(gen_dir, 1.0)
gen_line = f.line(apex_pt, gen_vec)

# ── Revolution axis: Z-axis ───────────────────────────────────────────────────
rev_orig = f.cartesian_point((0.0, 0.0, 0.0))
rev_zdir = f.direction((0.0, 0.0, 1.0))
rev_ax   = f._emit_raw(
    f"AXIS1_PLACEMENT('gs071_rev_ax',#{rev_orig.eid},#{rev_zdir.eid})"
)

# ── SURFACE_OF_REVOLUTION: generator (apex→rim) around Z-axis → cone ─────────
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION'), contains(b'gs071')
sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs071_sor',#{gen_line.eid},#{rev_ax.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face: triangular patch with degenerate apex edge ─────────────────────────
# Cone apex: (0,0,0) — ALL u values at v=0 map here (singularity).
# Rim at v=1: two rim points at u=0 and u=π/2 (quarter turn).
# Face boundary:
#   e0: apex degenerate edge (u: 0→π/2 at v=0, zero-length in 3D)
#   e1: meridian at u=π/2 (v: 0→1), rim_C = (0,1,0)
#   e2: rim arc (u: π/2→0, v=1)
#   e3: meridian at u=0 (v: 1→0), rim_A = (1,0,0)
PI_OVER_2 = math.pi / 2

v_apex  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_rim_A = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))   # u=0, v=1
v_rim_C = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))   # u=π/2, v=1

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

# e0: degenerate apex edge — zero-length 3D, pcurve at v=0 sweeps u: 0→π/2
# This is the collapsed edge whose redistribution uses arithmetic mean.
p3_degen = f.cartesian_point((0.0, 0.0, 0.0))
d3_degen = f.direction((1.0, 0.0, 0.0))
v3_degen = f.vector(d3_degen, 1.0e-12)   # near-zero length
l3_degen = f.line(p3_degen, v3_degen)
p2_degen = f.cartesian_point((0.0, 0.0))
d2_degen = f.direction((1.0, 0.0))
v2_degen = f.vector(d2_degen, PI_OVER_2)
l2_degen = f.line(p2_degen, v2_degen)
pcd_degen= f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_degen',(#{l2_degen.eid}),#{prc.eid})")
pc_degen = f._emit_raw(f"PCURVE('pc_degen',#{sor.eid},#{pcd_degen.eid})")
sc_degen = f._emit_raw(f"SURFACE_CURVE('sc_degen',#{l3_degen.eid},(#{pc_degen.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(
    f"EDGE_CURVE('ec_degen',#{v_apex.eid},#{v_apex.eid},#{sc_degen.eid},.T.)"
)

# e1: meridian at u=π/2: apex → rim_C (v: 0→1)
e1 = mk_edge_line(v_apex, v_rim_C,
                  (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (PI_OVER_2, 0.0), (0.0, 1.0), 1.0)

# e2: rim arc u=π/2→0 at v=1
e2 = mk_edge_line(v_rim_C, v_rim_A,
                  (0.0, 1.0, 0.0), (1.0, -1.0, 0.0), math.sqrt(2),
                  (PI_OVER_2, 1.0), (-1.0, 0.0), PI_OVER_2)

# e3: meridian at u=0: rim_A → apex (v: 1→0)
e3 = mk_edge_line(v_rim_A, v_apex,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION IS the face_geometry; degenerate apex edge IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sor)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
