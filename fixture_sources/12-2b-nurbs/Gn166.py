"""Gn166 — Boundary Pole Singularity (First Row).

Catalog claim: U-boundary poles coalesce; ShapeAnalysis_CheckSmallFace.CheckPin
must iterate boundary rows via IsoStat, not interior poles.

Mechanism: The B-spline surface with coalesced U=0 boundary poles IS the
face_geometry, wired into OPEN_SHELL → SHELL_BASED_SURFACE_MODEL.
The first U-row (U=0) has all poles at the same 3D point (0,0,0),
creating a boundary pole singularity (degenerate first row). The interior
rows are normal. CheckPin iterates over interior poles and misses the
boundary singularity, while IsoStat-based boundary scan would catch it.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn166",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS U-deg 2, V-deg 1; 3x3 poles; "
        "first U-row (U=0) all poles coalesced at (0,0,0) → boundary pole singularity; "
        "interior poles normal (0.5,*,0) and (1.0,*,0); "
        "U-knots (0.0,1.0) mults (3,3); V-knots (0.0,1.0) mults (3,3); "
        "CheckPin iterates interior poles only, misses first-row singularity; "
        "IS face_geometry → shape_null"
    ),
)

# 3 U-rows × 3 V-cols; U-degree=2, V-degree=2.
# U knots: (0.0, 1.0) mults (3,3) sum=6=3+2+1 ✓
# V knots: (0.0, 1.0) mults (3,3) sum=6=3+2+1 ✓
# DEFECT: first U-row all poles at (0,0,0) → degenerate boundary.
surf_pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],   # U=0 COALESCED (singularity)
    [(0.5, 0.0, 0.0), (0.5, 0.5, 0.0), (0.5, 1.0, 0.0)],   # U=1 normal
    [(1.0, 0.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 0.0)],   # U=2 normal
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in surf_pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn166_boundary_sing',2,2,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# Minimal edge wiring — use far end of surface (U=1 side) so edge is non-degenerate
p_s = f.cartesian_point((1.0, 0.0, 0.0))
p_e = f.cartesian_point((1.0, 1.0, 0.0))
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)
d_y = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(d_y, 1.0)
line3d = f.line(p_s, vec_y)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
# pcurve: V-iso at U=1.0 from V=0 to V=1
uv_s  = f.cartesian_point((1.0, 0.0))
uv_d  = f.direction((0.0, 1.0))
uv_v  = f.vector(uv_d, 1.0)
uv_ln = f.line(uv_s, uv_v)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn166_pcdef',(#{uv_ln.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn166_uv',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn166_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gn166_edge',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
