"""Gs167 — RectangularTrimmedSurface null basis detection.

Catalog claim: ShapeUpgrade_ShapeCopy calls BasisSurface() without null
check. If basis is null (malformed), down_cast succeeds but result
overwritten to null; downstream GeomAdaptor_Surface(null) invokes
undefined behavior. Fixture: RECTANGULAR_TRIMMED_SURFACE with basis;
verify null-safety on extraction.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE (trimmed from PLANE_SURFACE, u1=0, u2=1,
    v1=0, v2=1) IS the ADVANCED_FACE.face_geometry; face boundary edge
    pcurves referencing the trimmed surface IS the mechanism wired into
    face topology; ShapeUpgrade_ShapeCopy calling BasisSurface() without
    null check (down_cast result overwritten to null) IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE (PLANE_SURFACE basis,
    u1=0,u2=1,v1=0,v2=1) IS ADVANCED_FACE.face_geometry; face boundary
    edge pcurves on trimmed surface IS the mechanism wired into face
    topology; ShapeUpgrade_ShapeCopy BasisSurface() missing null check
    (down_cast overwrite null → GeomAdaptor_Surface UB) IS the defect.
  - shape_null driver: null basis after down_cast reaches GeomAdaptor_Surface;
    undefined behavior invoked; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs167",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (PLANE_SURFACE basis, u1=0,u2=1,v1=0,v2=1) "
        "IS ADVANCED_FACE.face_geometry; face boundary edge pcurves on trimmed "
        "surface IS the mechanism wired into face topology; "
        "ShapeUpgrade_ShapeCopy BasisSurface() missing null check "
        "(down_cast overwrites to null, GeomAdaptor_Surface UB) IS the defect; shape_null"
    ),
)

# ── PLANE_SURFACE basis ───────────────────────────────────────────────────────
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
#
# ShapeUpgrade_ShapeCopy calls BasisSurface() on the RECTANGULAR_TRIMMED_SURFACE
# to extract the underlying geometry. The call is not null-checked: if the basis
# is null or the down_cast fails, the result is silently overwritten to null.
# Downstream GeomAdaptor_Surface(null) then invokes undefined behavior.

plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_norm = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs167_pl_ax',#{plane_orig.eid},#{plane_norm.eid},#{plane_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs167_plane',#{plane_ax.eid})")

# RECTANGULAR_TRIMMED_SURFACE(name, basis_surface, u1, u2, v1, v2,
#                              usense, vsense)
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs167_rts',#{plane.eid},0.,1.,0.,1.,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square [0,1]x[0,1] in UV, pcurves on trimmed surface ──
# The trimmed surface domain is [0,1]x[0,1] (same as trim parameters).
# All pcurves reference the RECTANGULAR_TRIMMED_SURFACE entity.
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


# Bottom: A→B, u=0→1 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# Right: B→C, v=0→1 at u=1
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# Top: C→D, u=1→0 at v=1
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# Left: D→A, v=1→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_TRIMMED_SURFACE (PLANE_SURFACE basis) IS the face_geometry; face
# boundary edge pcurves on the trimmed surface IS the mechanism wired into face
# topology — exercises ShapeUpgrade_ShapeCopy BasisSurface() missing null check.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
