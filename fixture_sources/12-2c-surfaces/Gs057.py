"""Gs057 — RECTANGULAR_COMPOSITE_SURFACE LoadONBrep stub (BRL-CAD step-g).

Catalog claim: A RECTANGULAR_COMPOSITE_SURFACE whose LoadONBrep is a stub
(prints "not implemented" and returns false).  Faces referencing the quilt
are dropped without further diagnostic.  step-g's Load parses the segment
grid into SurfacePatch objects, but LoadONBrep never converts the entity to
BRep geometry.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_COMPOSITE_SURFACE(segments=((SURFACE_PATCH,...))) IS the
    ADVANCED_FACE.face_geometry; unimplemented LoadONBrep dispatch IS the
    defect wired into face topology.
  - Byte assertions: contains(b'RECTANGULAR_COMPOSITE_SURFACE'),
                     contains(b'SURFACE_PATCH').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_COMPOSITE_SURFACE IS the ADVANCED_FACE.face_geometry;
    SURFACE_PATCH grid IS the segment list; unimplemented LoadONBrep stub IS
    the defect wired into face topology; face is dropped without diagnostic.
  - shape_null driver: LoadONBrep returns false; face geometry never materialises;
    strict reject or unimplemented dispatch kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs057",
    defect=(
        "RECTANGULAR_COMPOSITE_SURFACE IS ADVANCED_FACE.face_geometry; "
        "SURFACE_PATCH grid referencing BEZIER patches IS the segment list; "
        "unimplemented LoadONBrep stub IS the defect wired into face topology; "
        "shape_null (unimplemented dispatch)"
    ),
)

# ── Two Bezier patches (via B_SPLINE_SURFACE_WITH_KNOTS, degree 1) ────────────
# Patch 0: unit square [0,1]×[0,1]
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p01 = f.cartesian_point((1.0, 0.0, 0.0))
p10 = f.cartesian_point((0.0, 1.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
patch0 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs057_p0',1,1,"
    f"((#{p00.eid},#{p01.eid}),(#{p10.eid},#{p11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# Patch 1: unit square [1,2]×[0,1] (adjacent in U)
p10b = f.cartesian_point((1.0, 0.0, 0.0))
p11b = f.cartesian_point((2.0, 0.0, 0.0))
p20  = f.cartesian_point((1.0, 1.0, 0.0))
p21  = f.cartesian_point((2.0, 1.0, 0.0))
patch1 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs057_p1',1,1,"
    f"((#{p10b.eid},#{p11b.eid}),(#{p20.eid},#{p21.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# ── SURFACE_PATCHes wrapping the two Bezier patches ───────────────────────────
# Byte assertion: contains(b'SURFACE_PATCH')
# SURFACE_PATCH(parent_surface, u_transition, v_transition, u_sense, v_sense)
sp0 = f._emit_raw(
    f"SURFACE_PATCH(#{patch0.eid},.DISCONTINUOUS.,.DISCONTINUOUS.,.T.,.T.)"
)
sp1 = f._emit_raw(
    f"SURFACE_PATCH(#{patch1.eid},.DISCONTINUOUS.,.DISCONTINUOUS.,.T.,.T.)"
)

# ── RECTANGULAR_COMPOSITE_SURFACE: 1×2 grid of patches ───────────────────────
# Byte assertion: contains(b'RECTANGULAR_COMPOSITE_SURFACE')
rcs = f._emit_raw(
    f"RECTANGULAR_COMPOSITE_SURFACE('gs057_rcs',((#{sp0.eid},#{sp1.eid})))"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the RECTANGULAR_COMPOSITE_SURFACE ────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((2.0, 0.0, 0.0))
p_C = f.cartesian_point((2.0, 1.0, 0.0))
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
    pc  = f._emit_raw(f"PCURVE('pc',#{rcs.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 2.0, (0.0,0.0), (1.0,0.0), 2.0)
e1 = mk_edge_line(v_B, v_C, (2.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (2.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (2.0,1.0,0.0), (-1.0,0.0,0.0), 2.0, (2.0,1.0), (-1.0,0.0), 2.0)
e3 = mk_edge_line(v_D, v_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_COMPOSITE_SURFACE IS the face_geometry; unimplemented stub IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], rcs)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
