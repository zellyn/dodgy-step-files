"""Gs159 — RectangularTrimmedSurface null-basis unwrap.

Catalog claim: GeomAdaptor_Surface unwraps trimmed surfaces without null-checking
BasisSurface result. Unwrap-null handling in GeomAdaptor_Surface constructor
passes null to downstream classifier, triggering undefined behavior.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE referencing a null basis surface ($) IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing the
    null-basis trimmed surface IS the mechanism wired into face topology;
    GeomAdaptor_Surface BasisSurface null-unwrap without null-check IS the
    defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE with null BasisSurface ($)
    IS ADVANCED_FACE.face_geometry; face boundary edge pcurves on the null-basis
    trimmed surface IS the mechanism wired into face topology;
    GeomAdaptor_Surface unwrap-null-check omission IS the defect.
  - shape_null driver: null passed to downstream classifier from unwrap;
    undefined behavior; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs159",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE with null BasisSurface ($) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves on null-basis "
        "trimmed surface IS the mechanism wired into face topology; "
        "GeomAdaptor_Surface BasisSurface null-unwrap without null-check IS "
        "the defect; shape_null"
    ),
)

# ── RECTANGULAR_TRIMMED_SURFACE with null BasisSurface ───────────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
# The basis surface is $ (null). GeomAdaptor_Surface calls BasisSurface() on the
# trimmed surface during construction and passes the null result to the type
# classifier without checking — this is the defect.
# RECTANGULAR_TRIMMED_SURFACE(name, basis_surface, u1, u2, v1, v2, usense, vsense)
rts = f._emit_raw(
    "RECTANGULAR_TRIMMED_SURFACE('gs159_rts',$,0.,1.,0.,1.,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square, pcurves in [0,1]x[0,1] ───────────────────────
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
    pc  = f._emit_raw(f"PCURVE('pc',#{rts.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom: A→B
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# Right: B→C
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# Top: C→D
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# Left: D→A
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE (null BasisSurface) IS the face_geometry; face
# boundary edge pcurves referencing the null-basis trimmed surface IS the
# mechanism wired into face topology — exercises GeomAdaptor_Surface
# BasisSurface null-unwrap defect.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
