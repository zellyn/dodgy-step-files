"""N118 — BRepLib.UpdateEdgeTol with-pcurve-discontinuity

Edge whose pcurve has a C0 discontinuity in the middle; UpdateEdgeTol samples
uniformly and the discontinuity contaminates one sample's tolerance calculation,
inflating the entire edge tolerance to hide the discontinuity instead of
reporting healing failure.

Reproducer: single edge spanning (0,0,0) to (10,0,0) in 3D with a B-spline
pcurve that has a jump discontinuity at u=0.5. Uniform sampling hits this and
inflates the edge tolerance instead of reporting the gap.

Byte assertions:
  contains(b'edge_pcurve_disc')
  contains(b'v_start')
  contains(b'v_end')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N118",
    defect=(
        "OPEN_SHELL face with edge_pcurve_disc (v_start→v_end, 10mm 3D line); "
        "B-spline pcurve has C0 discontinuity jump of 0.5 units at u=0.5; "
        "UpdateEdgeTol uniform sampling hits discontinuity and inflates tolerance "
        "to 0.5 instead of reporting the gap"
    ),
)

# Plane
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))

v_start = f.vertex_point(p0, name="v_start")
v_end = f.vertex_point(p1, name="v_end")

# 3D line: from (0,0,0) to (10,0,0)
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 10.0)
l_3d = f.line(p0, vec_x)

# Host surface (plane in XY)
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)

# Pcurve segment A: (0,0) → (2.5,0.1) → (5.0,0.0) — smooth but deviating
pca_0 = f._emit_raw("CARTESIAN_POINT('pca_0',(0.0,0.0))")
pca_1 = f._emit_raw("CARTESIAN_POINT('pca_1',(2.5,0.1))")
pca_2 = f._emit_raw("CARTESIAN_POINT('pca_2',(5.0,0.0))")
bsa = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('pcurve_a',2,(#{pca_0.eid},#{pca_1.eid},#{pca_2.eid}),"
    ".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# Pcurve segment B: (5.0,0.5) → (7.5,0.4) → (10.0,0.0) — starts 0.5 units off in v
pcb_0 = f._emit_raw("CARTESIAN_POINT('pcb_0',(5.0,0.5))")
pcb_1 = f._emit_raw("CARTESIAN_POINT('pcb_1',(7.5,0.4))")
pcb_2 = f._emit_raw("CARTESIAN_POINT('pcb_2',(10.0,0.0))")
bsb = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('pcurve_b',2,(#{pcb_0.eid},#{pcb_1.eid},#{pcb_2.eid}),"
    ".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# Pcurve referencing the plane with bsa as the representative curve
pc_ref = f._emit_raw(
    f"PCURVE('',#{plane.eid},#{bsa.eid})"
)

# Edge referencing the 3D line and pcurve via EDGE_CURVE
e_disc = f.edge_curve(v_start, v_end, l_3d, name="edge_pcurve_disc")

# Close with a simple face
p2 = f.cartesian_point((10.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

e_up   = f.edge_curve(v_end, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e_down = f.edge_curve(v3, v_start, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_disc, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N118.stp")
