"""Xp020 — Tessellated face × BRep face sharing PMI × unit-system inch/mm collision."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp020",
             defect='Tessellated face x BRep face sharing PMI x inch/mm unit collision',
             schema="AP242")

import math

# BRep half of a cylinder (half-cylinder face on CYLINDRICAL_SURFACE)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f.cylindrical_surface(plc, 1.0)

# Half-cylinder corners (theta: 0 to pi)
p_a0 = f.cartesian_point((1.0,  0.0, 0.0))   # (r=1, theta=0, z=0)
p_b0 = f.cartesian_point((-1.0, 0.0, 0.0))   # (r=1, theta=pi, z=0)
p_a1 = f.cartesian_point((1.0,  0.0, 1.0))   # top
p_b1 = f.cartesian_point((-1.0, 0.0, 1.0))

va0 = f.vertex_point(p_a0); vb0 = f.vertex_point(p_b0)
va1 = f.vertex_point(p_a1); vb1 = f.vertex_point(p_b1)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = max((dx**2 + dy**2 + dz**2) ** 0.5, 1e-15)
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Arcs approximated as lines for simplicity (the defect is in PMI, not geometry precision)
e_bottom = line_edge(p_a0, p_b0, va0, vb0)  # bottom arc (straight approx)
e_top    = line_edge(p_a1, p_b1, va1, vb1)  # top arc
e_left   = line_edge(p_a0, p_a1, va0, va1)  # left vertical
e_right  = line_edge(p_b0, p_b1, vb0, vb1)  # right vertical

loop = f.edge_loop([
    f.oriented_edge(e_bottom, True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_left, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 1: tessellated half-cylinder (AP242) — no STYLED_ITEM binding
coords = f._emit_raw(
    "COORDINATES_LIST('half_cyl_tess',3,("
    "(1.0,0.0,0.0),(0.0,1.0,0.0),(-1.0,0.0,0.0),"
    "(1.0,0.0,1.0),(0.0,1.0,1.0),(-1.0,0.0,1.0)))"
)
tess_face = f._emit_raw(
    f"TRIANGULATED_FACE('tess_half_cyl',#{coords.eid},(),"
    f"(),(),(3,((1,2,3),(4,5,6),(1,4,5))))"
)

# Defect 2: PMI dimensional_size (diameter) bound to both BRep and tess face
# No STYLED_ITEM for tess face → style binding lost
shape_asp_brep = f._emit_raw(f"SHAPE_ASPECT('brep_half','',#9005,.T.)")
shape_asp_tess = f._emit_raw(f"SHAPE_ASPECT('tess_half','',#9005,.T.)")
gisu_brep = f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE(#{shape_asp_brep.eid},#{face.eid})"
)
gisu_tess = f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE(#{shape_asp_tess.eid},#{tess_face.eid})"
)
dim_size = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{shape_asp_brep.eid},'diameter')"
)

# Defect 3: unit system inch/mm collision
# LENGTH_UNIT set to inches (0.0254 m), but PMI value 2.0 is in mm
f._emit_raw(
    "/* xp020 defect-3: LENGTH_UNIT declares inches; PMI diameter value 2.0 is in mm — unit collision */"
)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('unit_note','diameter: 2.0 (mm); LENGTH_UNIT=inches')"
)
