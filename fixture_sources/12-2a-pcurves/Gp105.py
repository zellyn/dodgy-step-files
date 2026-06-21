"""Gp105 — ShapeAnalysis_Edge.CheckOverlapping zero-tolerance-overlap.

Catalog claim: Two edges with literally coincident 3D geometry (identical LINE
0→5 in x-axis, identical pcurves). Both reference same plane surface.
CheckOverlapping with zero tolerance reports non-overlapping due to
floating-point comparison; misses exact coincidence.

Mechanism: GEOMETRIC_CURVE_SET containing two identical EDGE_CURVEs with the
same LINE curve and the same pcurve range. OCC yields empty.

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp105",
    defect=(
        "two EDGE_CURVEs with identical 3D LINE (0,0,0)→(5,0,0) and identical "
        "linear PCURVEs on same PLANE surface; "
        "CheckOverlapping at zero tolerance misses exact coincidence; "
        "floating-point compare fails to detect overlapping at ε=0; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

anchor = f.cartesian_point((0.0, 0.0, 0.0))

# Host plane
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# 2D parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)

# Shared vertices and 3D curve: both edges use the SAME 3D LINE (coincident)
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((5.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

d_x   = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 5.0)
line3d = f.line(p_start, vec_x)

# Edge A: identical geometry (0,0,0)→(5,0,0)
uv_a0  = f.cartesian_point((0.0, 0.0))
uv_a_d = f.direction((1.0, 0.0))
uv_a_v = f.vector(uv_a_d, 5.0)
line2d_a = f.line(uv_a0, uv_a_v)
defrep_a = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_A',(#{line2d_a.eid}),#{prc.eid})"
)
pcurve_a = f._emit_raw(f"PCURVE('pcurve_A',#{surf.eid},#{defrep_a.eid})")
sc_a = f._emit_raw(
    f"SURFACE_CURVE('edgeA',#{line3d.eid},(#{pcurve_a.eid}),.PCURVE_S1.)"
)
edge_a = f._emit_raw(
    f"EDGE_CURVE('edgeA_coincident',#{v_start.eid},#{v_end.eid},#{sc_a.eid},.T.)"
)

# Edge B: IDENTICAL geometry — exact duplicate of edge A (the defect)
uv_b0  = f.cartesian_point((0.0, 0.0))
uv_b_d = f.direction((1.0, 0.0))
uv_b_v = f.vector(uv_b_d, 5.0)
line2d_b = f.line(uv_b0, uv_b_v)
defrep_b = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_B',(#{line2d_b.eid}),#{prc.eid})"
)
pcurve_b = f._emit_raw(f"PCURVE('pcurve_B',#{surf.eid},#{defrep_b.eid})")
sc_b = f._emit_raw(
    f"SURFACE_CURVE('edgeB',#{line3d.eid},(#{pcurve_b.eid}),.PCURVE_S1.)"
)
edge_b = f._emit_raw(
    f"EDGE_CURVE('edgeB_coincident',#{v_start.eid},#{v_end.eid},#{sc_b.eid},.T.)"
)

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('coincident_edges',(#{anchor.eid},#{edge_a.eid},#{edge_b.eid}))"
)
f.add_product_chain(gcs)
