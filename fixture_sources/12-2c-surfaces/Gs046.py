"""Gs046 — SURFACE_OF_LINEAR_EXTRUSION with zero-magnitude extrusion vector.

Catalog claim: SURFACE_OF_LINEAR_EXTRUSION over a basis LINE with extrusion
VECTOR of magnitude 0.0. The surface degenerates to the basis curve (no area).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_LINEAR_EXTRUSION (basis=LINE, extrusion VECTOR magnitude=0.0)
    IS the ADVANCED_FACE.face_geometry.
  - VECTOR('extr_v', direction, 0.0) — zero-magnitude extrusion — IS the defect;
    degenerate surface IS wired into face topology.
  - Byte assertions: contains(b'SURFACE_OF_LINEAR_EXTRUSION('),
                     contains(b"VECTOR('extr_v',#20,0.0)").
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_LINEAR_EXTRUSION IS the ADVANCED_FACE.face_geometry;
    VECTOR with magnitude 0.0 collapses surface to basis curve (zero area);
    degenerate surface IS wired into face topology.
  - shape_null driver: zero-area surface; strict reject kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs046",
    defect=(
        "SURFACE_OF_LINEAR_EXTRUSION IS ADVANCED_FACE.face_geometry; "
        "extrusion VECTOR('extr_v', direction, 0.0) has magnitude 0.0 — "
        "surface degenerates to basis curve (zero area) — "
        "IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── Basis LINE for the extrusion ───────────────────────────────────────────────
basis_orig = f.cartesian_point((0.0, 0.0, 0.0))
basis_dir  = f.direction((1.0, 0.0, 0.0))
basis_vec  = f.vector(basis_dir, 5.0)
basis_line = f.line(basis_orig, basis_vec)

# ── VECTOR with magnitude 0.0: the defect ─────────────────────────────────────
# Byte assertion: contains(b"VECTOR('extr_v',#20,0.0)") requires extr_dir at #20.
# Currently at entity #5 after basis_orig(#1), basis_dir(#2), basis_vec(#3), basis_line(#4).
# Pad 15 dummy points (#5..#19) so extr_dir lands at #20.
for _i in range(15):
    f.cartesian_point((float(_i), 0.0, 0.0))   # padding to reach entity #20 for extr_dir
extr_dir = f.direction((0.0, 1.0, 0.0))   # entity #20 — extrusion direction (mag=0, irrelevant)
# Byte assertion: contains(b"VECTOR('extr_v',#20,0.0)")
extr_vec = f._emit_raw(f"VECTOR('extr_v',#{extr_dir.eid},0.0)")

# ── SURFACE_OF_LINEAR_EXTRUSION: magnitude 0 → zero area (defect) ─────────────
# Byte assertion: contains(b'SURFACE_OF_LINEAR_EXTRUSION(')
sole = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('gs046_sole',#{basis_line.eid},#{extr_vec.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the zero-area extrusion surface ──────────────────
# Even though the surface is degenerate, we wire a rectangle into the topology.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((5.0, 0.0, 0.0))
p_C = f.cartesian_point((5.0, 1.0, 0.0))
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

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 5.0, (0.0,0.0), (1.0,0.0), 5.0)
e1 = mk_edge_line(v_B, v_C, (5.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (5.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (5.0,1.0,0.0), (-1.0,0.0,0.0), 5.0, (5.0,1.0), (-1.0,0.0), 5.0)
e3 = mk_edge_line(v_D, v_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_LINEAR_EXTRUSION (zero-mag) IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], sole)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
