"""Xp010 — Negative torus radius × pcurve disagreement × tiny edge."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp010",
             defect='Negative torus radius x pcurve disagreement x tiny edge')

# Defect 1: TOROIDAL_SURFACE with negative major_radius (-10.0)
# Some vendors use negative major radius as an orientation marker
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
# negative major_radius = -10.0 (defect), minor_radius = 1.0
torus = f.toroidal_surface(plc, -10.0, 1.0)

# Build a degenerate face on the torus with a tiny edge
# (endpoints nearly identical — length < 1e-9)
# Defect 3: two consecutive control points differ by < 1e-9 → tiny edge
p0 = f.cartesian_point((9.0,  0.0, 0.0))          # on torus (r=10, rmin=1) approx
p1 = f.cartesian_point((9.0, 1.0e-10, 0.0))       # nearly same → tiny edge
p2 = f.cartesian_point((9.0,  1.0, 0.0))
p3 = f.cartesian_point((8.0,  1.0, 0.0))

v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = max((dx**2 + dy**2 + dz**2) ** 0.5, 1.0e-15)
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, p1, v0, v1)  # TINY edge (< 1e-9 length)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 2: pcurve/3D curve disagreement
# The tiny edge e0 has a pcurve that runs (u=0,v=0) to (u=0.001,v=0.001)
# but the 3D curve endpoints are nearly identical — pcurve and 3D disagree
pcurve_plc = f._emit_raw(
    f"(AXIS2_PLACEMENT_2D(#{orig.eid},*))"
)
pcurve = f._emit_raw(
    f"PCURVE('',(#{torus.eid}),#{pcurve_plc.eid})"
)
f._emit_raw(
    f"/* xp010 defect-2: pcurve ({pcurve.eid}) runs (0,0)-(0.001,0.001) "
    f"but 3D edge #{e0.eid} has length < 1e-9 — pcurve/3D disagree */"
)
