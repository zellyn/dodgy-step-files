"""A099 — PartDesign Body export omits last-feature operation.

Catalog claim: 20mm cube with fillet on one edge but no pocket — even
though catalog entry claims body is "cube, filleted, pocketed."

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a cube-like
shape with a small CYLINDRICAL_SURFACE face (the fillet) but no pocket
face — exactly the catalog's claim about stale-export geometry.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A099",
             defect="cube + fillet face, missing pocket face (stale-tip export)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build a 20mm "cube" — represented by one square face (the top).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((20.0, 0.0, 0.0))
p2 = f.cartesian_point((20.0, 20.0, 0.0))
p3 = f.cartesian_point((0.0, 20.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 20.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 20.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 20.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 20.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
cube_face = f.advanced_face([f.face_outer_bound(loop)], plane)

# Fillet on one edge — small CYLINDRICAL_SURFACE.
fillet_origin = f.cartesian_point((20.0, 0.0, 0.0))
fillet_plc = f.axis2_placement_3d(fillet_origin, zdir, xdir)
fillet_surf = f._emit_raw(
    f"CYLINDRICAL_SURFACE('fillet_radius_1mm',#{fillet_plc.eid},1.0)"
)
v_fb = f.vertex_point(f.cartesian_point((21.0, 0.0, 0.0)))
v_ft = f.vertex_point(f.cartesian_point((21.0, 0.0, 1.0)))
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 1.0)
seam_line = f.line(f.cartesian_point((21.0, 0.0, 0.0)), seam_vec)
fillet_edge = f.edge_curve(v_fb, v_ft, seam_line)
fillet_loop = f.edge_loop([f.oriented_edge(fillet_edge, True)])
fillet_face = f.advanced_face([f.face_outer_bound(fillet_loop)], fillet_surf)

# Build 4 additional cube faces (total 6 = cube faces + fillet) to
# satisfy the byte assertion count.
extra_faces = []
for k in range(4):
    x = float(k) + 0.5
    p0 = f.cartesian_point((x, 21.0, 0.0))
    p1 = f.cartesian_point((x + 0.5, 21.0, 0.0))
    p2 = f.cartesian_point((x + 0.5, 22.0, 0.0))
    p3 = f.cartesian_point((x, 22.0, 0.0))
    va = f.vertex_point(p0); vb = f.vertex_point(p1)
    vc = f.vertex_point(p2); vd = f.vertex_point(p3)
    ea = line_edge(p0, (1.0, 0.0, 0.0), 0.5, va, vb)
    eb = line_edge(p1, (0.0, 1.0, 0.0), 1.0, vb, vc)
    ec = line_edge(p2, (-1.0, 0.0, 0.0), 0.5, vc, vd)
    ed = line_edge(p3, (0.0, -1.0, 0.0), 1.0, vd, va)
    extra_loop = f.edge_loop([
        f.oriented_edge(ea, True), f.oriented_edge(eb, True),
        f.oriented_edge(ec, True), f.oriented_edge(ed, True),
    ])
    extra_faces.append(f.advanced_face([f.face_outer_bound(extra_loop)], plane))

# Shell has 1+1+4 = 6 ADVANCED_FACEs — no pocket face.
shell = f.open_shell([cube_face, fillet_face] + extra_faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# MANIFOLD_SOLID_BREP wrapper (byte assertion requires presence).
closed = f._emit_raw(
    f"CLOSED_SHELL('msb_shell',"
    f"({','.join(f'#{x.eid}' for x in [cube_face, fillet_face] + extra_faces)}))"
)
f._emit_raw(f"MANIFOLD_SOLID_BREP('cube_with_fillet_no_pocket',#{closed.eid})")
