"""Gn164 — Rational BSpline Closure Detection Bypass.

Catalog claim: Rational surface with varying weights requires knot-aware grid
sampling, not pole-based shortcut. ShapeAnalysis_Surface.IsURational() gate
bypassed when rational B-spline surface IS the face geometry.

Mechanism: The RATIONAL_B_SPLINE_SURFACE (weight variation 1.0/0.5) IS the
face_geometry, wired into OPEN_SHELL → SHELL_BASED_SURFACE_MODEL.
ShapeAnalysis_Surface.IsURational() takes a pole-based shortcut that misses
the varying weights, producing incorrect closure detection.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn164",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE (complex entity) U-deg 2, V-deg 1, 3x2 poles; "
        "weights alternate (1.0, 0.5) row-by-row to create rational variation; "
        "IS face_geometry; ShapeAnalysis_Surface.IsURational() pole-based shortcut "
        "bypasses knot-aware grid sampling → closure detection bypass → empty"
    ),
)

# Build the rational B-spline surface as a complex STEP entity.
# 3 U-rows × 2 V-cols of control points.
# Weight variation: row 0 all 1.0, row 1 all 0.5, row 2 all 1.0 → IsURational() mismatch.
surf_pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],   # U=0 row
    [(0.5, 0.0, 0.2), (0.5, 1.0, 0.2)],   # U=1 row — elevated Z
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],   # U=2 row
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in surf_pts)

# Weight grid: row 0 = (1.0,1.0), row 1 = (0.5,0.5), row 2 = (1.0,1.0)
# The 0.5 weight in the middle row creates rational variation that
# ShapeAnalysis_Surface.IsURational() misses via its pole-count shortcut.
surf = f._emit_raw(
    f"(B_SPLINE_SURFACE('gn164_rbs',2,1,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((3,3),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_SURFACE(((1.0,1.0),(0.5,0.5),(1.0,1.0)))"
    f"REPRESENTATION_ITEM('')"
    f"SURFACE())"
)

# Edge wiring: single edge along U axis
p_s = f.cartesian_point((0.0, 0.0, 0.0))
p_e = f.cartesian_point((1.0, 0.0, 0.0))
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
line3d = f.line(p_s, vec_x)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
uv_s  = f.cartesian_point((0.0, 0.0))
uv_d  = f.direction((1.0, 0.0))
uv_v  = f.vector(uv_d, 1.0)
uv_ln = f.line(uv_s, uv_v)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn164_pcdef',(#{uv_ln.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn164_uv',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn164_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gn164_edge',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
