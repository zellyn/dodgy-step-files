"""Gp002 — Pcurve endpoints disagree with edge vertex 3D positions.

Catalog claim: An EDGE_CURVE carries a PCURVE whose evaluation at its
parameter endpoints does not match the edge's VERTEX_POINT 3D positions.
Lifting the pcurve through the host surface lands at a different point
than the edge's vertex coordinates.

Fixture: CYLINDRICAL_SURFACE (radius 10) with a vertical edge along
the generator at U=0 (v=0 to v=5). Vertices are correctly at U=0 (0,0,0)
and (0,5) in UV. The pcurve is deliberately wrong: it runs from (u=0,v=0)
to (u=π/2,v=5), so when lifted via the cylinder, the end point lands at
approximately (0,10,5) instead of (10,0,5).
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp002",
             defect="pcurve endpoints disagree with edge vertex 3D positions")

# Cylindrical surface: radius 10, axis along Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{plc.eid},10.0)")

# 3D edge: vertical line from (10,0,0) to (10,0,5) - generator at U=0
p_start = f.cartesian_point((10.0, 0.0, 0.0))
p_end = f.cartesian_point((10.0, 0.0, 5.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

zdir_edge = f.direction((0.0, 0.0, 1.0))
zvec = f.vector(zdir_edge, 5.0)
line3d = f.line(p_start, zvec)

# DEFECT: 2D pcurve runs from (u=0,v=0) to (u=π/2,v=5)
# When lifted: start at 0 → (10,0,0) ✓
#              end at π/2 on cylinder → (0,10,5) ✗ (should be (10,0,5))
uv_start = f.cartesian_point((0.0, 0.0))
uv_dir = f.direction((pi/2.0, 1.0))
uv_vec = f.vector(uv_dir, 1.0)
line2d = f.line(uv_start, uv_vec)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{line2d.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{cyl.eid},#{defrep.eid})")
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

# Build the face and shell for the PRODUCT chain
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
