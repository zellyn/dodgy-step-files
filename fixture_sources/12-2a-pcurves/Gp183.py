"""Gp183 — Edge same_range flag claims parametric agreement that does not
hold, face-hosted so the flag lie is live (not Twi082's orphan GEOMETRIC_
CURVE_SET, which OCC translates to empty and never binds the pcurve to a
face at all).

Work packet D2, item `bc-invalid-same-range-flag` (PARTIAL), problem_id
`bc-invalid-same-range-flag`: "An edge's SameRange flag asserts the 3D
curve and pcurve share an identical parameter range, but the stored ranges
actually differ." (BRepCheck_Edge::Blind/InContext, BRepCheck_Edge.cxx:
299,336 — sets BRepCheck_InvalidSameRangeFlag). Twi082 encodes the exact
same numeric mismatch (3D range [0,10] vs pcurve range [0,5], same_range=
.T.) but wraps it in a GEOMETRIC_CURVE_SET, which OCC translates to
shape_null=True — the pcurve never actually binds to an ADVANCED_FACE, so
BRepCheck_Edge is never invoked against a live TopoDS_Edge sitting on a
TopoDS_Face. This fixture ports Twi082's identical numeric defect onto a
PLANE-hosted ADVANCED_FACE, so the edge with the lying same_range flag is
reachable in the translated shape and BRepCheck_Analyzer can actually
flag it.

Mechanism: PLANE surface. EDGE_CURVE's SURFACE_CURVE wraps a 3D LINE
spanning parameter range [0,10] (from (0,0,0), direction (1,0,0), length
10) and a PCURVE whose 2D LINE spans parameter range [0,5] (from (0,0) in
UV, direction (1,0), length 5) — genuinely different ranges. The
EDGE_CURVE's same_range flag is set .T. anyway. Single-edge FACE_OUTER_
BOUND wired to the plane (same open-loop idiom already used by the
existing Gp050/Gp022 fixtures in this section, which reach shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp183",
    defect=(
        "PLANE-hosted EDGE_CURVE: 3D LINE from (0,0,0) along (1,0,0) length 10 "
        "(3D parameter range [0,10]) paired with a PCURVE whose UV LINE runs from "
        "(0,0) along (1,0) length 5 (parameter range [0,5]) -- genuinely different "
        "ranges -- but same_range=.T.; face-hosted so BRepCheck_Edge actually sees "
        "a live edge on a live face (Twi082's identical numeric mismatch lives in "
        "an orphan GEOMETRIC_CURVE_SET that OCC translates to empty)"
    ),
)

# PLANE host surface, standard placement.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D LINE: (0,0,0) along (1,0,0), length 10 -- parameter range [0,10].
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((10.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
line_3d = f.line(p_start, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))

# PCURVE: UV LINE from (0,0) along (1,0), length 5 -- parameter range [0,5].
pc_start = f.cartesian_point((0.0, 0.0))
pc_dir = f.direction((1.0, 0.0))
pc_vec = f.vector(pc_dir, 5.0)
pc_line = f._emit_raw(f"LINE('same_range_lie',#{pc_start.eid},#{pc_vec.eid})")
pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp183_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp183_uv',#{plane.eid},#{pc_def.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp183_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# THE DEFECT: same_range=.T. even though 3D range [0,10] != UV range [0,5].
edge = f._emit_raw(
    f"EDGE_CURVE('gp183_edge',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
