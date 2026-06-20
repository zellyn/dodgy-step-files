"""Gn045 — ShapeUpgrade_SplitSurface.Init split-parameters validation out-of-domain.

Catalog claim: B-spline surface with split request using u_split values outside
[u_min, u_max]. Init() must reject these values but currently accepts them,
producing empty patches instead of raising validation error.

Mechanism: The B-spline surface IS the face_geometry of the ADVANCED_FACE,
wired into an OPEN_SHELL → SHELL_BASED_SURFACE_MODEL. The out-of-domain trigger
is encoded as a TRIMMED_CURVE whose U1 and U2 parameters exceed the surface's
natural U domain [0,1] (specifically U=2.0 > u_max=1.0), placed as the 3D curve
of an EDGE_CURVE on the face. This forces OCC's SplitSurface to encounter
out-of-domain U parameters when processing the edge topology.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn045",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (U-deg 2, V-deg 1, 3x2 poles, domain [0,1]x[0,1]) "
        "IS face_geometry; edge uses TRIMMED_CURVE with U1=1.2 U2=2.0 outside surface "
        "u_max=1.0; SplitSurface.Init receives out-of-domain split param U=2.0 → "
        "empty patch output → shape_null"
    ),
)

# B-spline surface: U-degree=2, V-degree=1, 3x2 poles, domain [0,1]×[0,1]
# This IS the face surface.
surf_pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(0.5, 0.0, 0.1), (0.5, 1.0, 0.1)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in surf_pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn045_surf',2,1,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(2,2),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# Vertices at corners of the surface U=0..1, V=0..1
p_s = f.cartesian_point((0.0, 0.0, 0.0))
p_e = f.cartesian_point((1.0, 0.0, 0.0))
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)

# 3D base line
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
line3d = f.line(p_s, vec_x)

# CATALOG MECHANISM: TRIMMED_CURVE with out-of-domain U1=1.2, U2=2.0
# (surface u_max=1.0). This is the defect — Init() receives U=2.0 split param.
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('gn045_ood_trim',#{line3d.eid},"
    f"(PARAMETER_VALUE(1.2)),(PARAMETER_VALUE(2.0)),.T.,.PARAMETER.)"
)

# UV parametric context for pcurve
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
# Pcurve: line in UV space u=0..1, v=0
uv_s  = f.cartesian_point((0.0, 0.0))
uv_d  = f.direction((1.0, 0.0))
uv_v  = f.vector(uv_d, 1.0)
uv_ln = f.line(uv_s, uv_v)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn045_pcdef',(#{uv_ln.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn045_uv',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gn045_sc',#{trimmed.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gn045_edge',#{v_s.eid},#{v_e.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
