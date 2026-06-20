"""Gp063 — ShapeAnalysis_Edge.CheckOverlapping bounded-curve trim.

Catalog claim: Two edges share identical 3D line but with non-overlapping
parameter ranges: edge1 covers parameter [0,5], edge2 covers [10,15].
CheckOverlapping fails to intersect trim domains and falsely reports overlap.

Mechanism: Two EDGE_CURVEs both reference the same base LINE via TRIMMED_CURVE
wrappers with disjoint trim ranges [0,5] and [10,15]. Both edges are wired into
the same face's EDGE_LOOP, creating the CheckOverlapping bounded-curve scenario.

The two trimmed curves represent disjoint segments of the same infinite line.
CheckOverlapping, when it sees two edges with geometrically coincident base
curves, must intersect their trim domains before declaring overlap — the bug
is that it declares overlap without checking the [0,5] vs [10,15] disjointness.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp063",
    defect=(
        "Two EDGE_CURVEs share the same 3D LINE base curve; "
        "edge1 trimmed to parameter range [0,5] (3D: x=0..5,y=0,z=0); "
        "edge2 trimmed to parameter range [10,15] (3D: x=10..15,y=0,z=0); "
        "ranges are DISJOINT; CheckOverlapping sees same base curve and falsely "
        "reports overlap without intersecting trim domains; both edges in same face loop"
    ),
)

# Shared base LINE along X from origin
base_line_orig = f.cartesian_point((0.0, 0.0, 0.0))
base_line_dir  = f.direction((1.0, 0.0, 0.0))
base_line_vec  = f.vector(base_line_dir, 1.0)   # unit vector; trimming controls extent
base_line = f.line(base_line_orig, base_line_vec)

# CATALOG MECHANISM: two TRIMMED_CURVEs on the same LINE, disjoint ranges
# Edge1: [0, 5] — x from 0 to 5
trim1 = f._emit_raw(
    f"TRIMMED_CURVE('gp063_trim_0_5',#{base_line.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)
# Edge2: [10, 15] — x from 10 to 15 (DISJOINT from [0,5])
trim2 = f._emit_raw(
    f"TRIMMED_CURVE('gp063_trim_10_15',#{base_line.eid},"
    f"(PARAMETER_VALUE(10.0)),(PARAMETER_VALUE(15.0)),.T.,.PARAMETER.)"
)

# Vertices
p0  = f.cartesian_point((0.0,  0.0, 0.0))
p5  = f.cartesian_point((5.0,  0.0, 0.0))
p10 = f.cartesian_point((10.0, 0.0, 0.0))
p15 = f.cartesian_point((15.0, 0.0, 0.0))
v0  = f.vertex_point(p0)
v5  = f.vertex_point(p5)
v10 = f.vertex_point(p10)
v15 = f.vertex_point(p15)

# Host surface: planar z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('gp063_host',#{plc.eid})")

# UV parametric context for pcurves
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def make_linear_pcurve(u_start, u_end):
    uv_s  = f.cartesian_point((u_start, 0.0))
    uv_d  = f.direction((1.0, 0.0))
    uv_v  = f.vector(uv_d, u_end - u_start)
    uv_ln = f.line(uv_s, uv_v)
    dr    = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('gp063_pcdef_{int(u_start)}_{int(u_end)}',"
        f"(#{uv_ln.eid}),#{prc.eid})"
    )
    return f._emit_raw(f"PCURVE('gp063_uv_{int(u_start)}_{int(u_end)}',#{plane.eid},#{dr.eid})")

pcurve1 = make_linear_pcurve(0.0, 5.0)
pcurve2 = make_linear_pcurve(10.0, 15.0)

# SURFACE_CURVE for each edge
sc1 = f._emit_raw(
    f"SURFACE_CURVE('gp063_sc1',#{trim1.eid},(#{pcurve1.eid}),.PCURVE_S1.)"
)
sc2 = f._emit_raw(
    f"SURFACE_CURVE('gp063_sc2',#{trim2.eid},(#{pcurve2.eid}),.PCURVE_S1.)"
)

edge1 = f._emit_raw(
    f"EDGE_CURVE('gp063_edge1',#{v0.eid},#{v5.eid},#{sc1.eid},.T.)"
)
edge2 = f._emit_raw(
    f"EDGE_CURVE('gp063_edge2',#{v10.eid},#{v15.eid},#{sc2.eid},.T.)"
)

# Both edges in the same EDGE_LOOP — CheckOverlapping sees them together
loop = f.edge_loop([
    f.oriented_edge(edge1, True),
    f.oriented_edge(edge2, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
