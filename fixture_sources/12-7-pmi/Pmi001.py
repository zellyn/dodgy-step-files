"""Pmi001 — Hole emitted as two half-cylinders breaks PMI feature association.

Catalog claim: A through-hole exported as two ADVANCED_FACE instances backed
by halves of a CYLINDRICAL_SURFACE. PMI (diameter dimensions, position
tolerances, datums) targeting the whole hole must reach both halves through a
shared SHAPE_ASPECT plus two GEOMETRIC_ITEM_SPECIFIC_USAGE entries. Receivers
that expect one face per cylindrical feature drop or duplicate the PMI link.

Reproducer: 50×50×20 mm plate with one 10 mm-diameter through-hole. The hole
wall is two ADVANCED_FACEs sharing ONE CYLINDRICAL_SURFACE. The SHAPE_ASPECT
'hole_feature' links to both via two GISUs. A DIMENSIONAL_SIZE 'diameter'
targets the shared SHAPE_ASPECT.

Tier-3 assertions:
  n_faces_total == 8
  face[6].surface_type == "cylinder"
  face[7].surface_type == "cylinder"
  face[6].area > 311 and < 317
  brepcheck.valid == True

Expected: occt=shape(1)/shape(1) gmsh=shape(39) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi001",
    defect=(
        "through-hole emitted as TWO half-cylinder ADVANCED_FACEs sharing "
        "ONE CYLINDRICAL_SURFACE; PMI SHAPE_ASPECT links both halves via "
        "two GEOMETRIC_ITEM_SPECIFIC_USAGE entries; receivers expecting "
        "one face per hole feature drop or duplicate the PMI dimension link"
    ),
)

# ── Plate corners: 50×50×20 mm ────────────────────────────────────────────────
p000 = f.cartesian_point((0.0, 0.0, 0.0))
p100 = f.cartesian_point((50.0, 0.0, 0.0))
p110 = f.cartesian_point((50.0, 50.0, 0.0))
p010 = f.cartesian_point((0.0, 50.0, 0.0))
p001 = f.cartesian_point((0.0, 0.0, 20.0))
p101 = f.cartesian_point((50.0, 0.0, 20.0))
p111 = f.cartesian_point((50.0, 50.0, 20.0))
p011 = f.cartesian_point((0.0, 50.0, 20.0))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# ── Hole: cylindrical_surface, axis along +Z at (25,25,0), radius 5 ──────────
hole_center = f.cartesian_point((25.0, 25.0, 0.0))
hole_axis   = f.direction((0.0, 0.0, 1.0))
hole_ref    = f.direction((1.0, 0.0, 0.0))
hole_plc    = f.axis2_placement_3d(hole_center, hole_axis, hole_ref)
cyl_surf    = f._emit_raw(f"CYLINDRICAL_SURFACE('hole_surface',#{hole_plc.eid},5.0)")

# Seam vertices on bottom (z=0) and top (z=20).
# theta=0 → point (30,25); theta=π → point (20,25).
seam0_bot = f.cartesian_point((30.0, 25.0, 0.0))   # theta=0, z=0
seamP_bot = f.cartesian_point((20.0, 25.0, 0.0))   # theta=pi, z=0
seam0_top = f.cartesian_point((30.0, 25.0, 20.0))  # theta=0, z=20
seamP_top = f.cartesian_point((20.0, 25.0, 20.0))  # theta=pi, z=20

vs0b = f.vertex_point(seam0_bot); vsPb = f.vertex_point(seamP_bot)
vs0t = f.vertex_point(seam0_top); vsPt = f.vertex_point(seamP_top)

# Circle curves for the top and bottom rings.
hole_top_center = f.cartesian_point((25.0, 25.0, 20.0))
top_plc = f.axis2_placement_3d(hole_top_center, hole_axis, hole_ref)
top_circle = f._emit_raw(f"CIRCLE('hole_top_circle',#{top_plc.eid},5.0)")
bot_plc = f.axis2_placement_3d(hole_center, hole_axis, hole_ref)
bot_circle = f._emit_raw(f"CIRCLE('hole_bot_circle',#{bot_plc.eid},5.0)")

# Half-circle edge_curves (share the circle geometry).
bot_A = f.edge_curve(vs0b, vsPb, bot_circle)  # theta=0..pi bot
bot_B = f.edge_curve(vsPb, vs0b, bot_circle)  # theta=pi..2pi bot
top_A = f.edge_curve(vs0t, vsPt, top_circle)  # theta=0..pi top
top_B = f.edge_curve(vsPt, vs0t, top_circle)  # theta=pi..2pi top

# Vertical seam edges shared by both half-cylinder faces.
zdir  = f.direction((0.0, 0.0, 1.0))
zvec  = f.vector(zdir, 20.0)
seam0_line = f.line(seam0_bot, zvec)
seam0_ec   = f.edge_curve(vs0b, vs0t, seam0_line)  # seam at theta=0
seamP_line = f.line(seamP_bot, zvec)
seamP_ec   = f.edge_curve(vsPb, vsPt, seamP_line)  # seam at theta=pi

# ── Outer plate edges ─────────────────────────────────────────────────────────
def le(p, vstart, vend, dvec, length):
    d = f.direction(dvec)
    return f.edge_curve(vstart, vend, f.line(p, f.vector(d, length)))

e_b0 = le(p000, v000, v100, (1,0,0), 50.0)
e_b1 = le(p100, v100, v110, (0,1,0), 50.0)
e_b2 = le(p010, v110, v010, (-1,0,0), 50.0)
e_b3 = le(p000, v010, v000, (0,-1,0), 50.0)
e_t0 = le(p001, v001, v101, (1,0,0), 50.0)
e_t1 = le(p101, v101, v111, (0,1,0), 50.0)
e_t2 = le(p011, v111, v011, (-1,0,0), 50.0)
e_t3 = le(p001, v011, v001, (0,-1,0), 50.0)
e_v0 = le(p000, v000, v001, (0,0,1), 20.0)
e_v1 = le(p100, v100, v101, (0,0,1), 20.0)
e_v2 = le(p110, v110, v111, (0,0,1), 20.0)
e_v3 = le(p010, v010, v011, (0,0,1), 20.0)

def oe(e, sense): return f.oriented_edge(e, sense)

# ── Plate face planes ─────────────────────────────────────────────────────────
def pface(normal_xyz, orig_xyz, xdir_xyz, loops, is_outer=True):
    orig = f.cartesian_point(orig_xyz)
    zd = f.direction(normal_xyz)
    xd = f.direction(xdir_xyz)
    plc = f.axis2_placement_3d(orig, zd, xd)
    plane = f.plane(plc)
    bounds = []
    for i, loop in enumerate(loops):
        el = f.edge_loop(loop)
        if i == 0:
            bounds.append(f.face_outer_bound(el))
        else:
            bounds.append(f._emit_raw(f"FACE_BOUND('',#{el.eid},.T.)"))
    return f.advanced_face(bounds, plane)

# Bottom face (z=0): outer square + inner hole (both halves CW when viewed -Z)
bot_hole_loop = [oe(bot_A, True), oe(bot_B, True)]
bot_face = pface(
    (0,0,-1), (25,25,0), (1,0,0),
    [
        [oe(e_b0, True), oe(e_b1, True), oe(e_b2, True), oe(e_b3, True)],
        bot_hole_loop,
    ]
)

# Top face (z=20): outer square + inner hole
top_hole_loop = [oe(top_B, False), oe(top_A, False)]
top_face = pface(
    (0,0,1), (25,25,20), (1,0,0),
    [
        [oe(e_t0, True), oe(e_t1, True), oe(e_t2, True), oe(e_t3, True)],
        top_hole_loop,
    ]
)

# Side faces
front_face = pface(
    (0,-1,0), (25,0,10), (1,0,0),
    [[oe(e_b0, True), oe(e_v1, True), oe(e_t0, False), oe(e_v0, False)]]
)
back_face = pface(
    (0,1,0), (25,50,10), (1,0,0),
    [[oe(e_b2, False), oe(e_v3, True), oe(e_t2, False), oe(e_v2, False)]]
)
left_face = pface(
    (-1,0,0), (0,25,10), (0,1,0),
    [[oe(e_b3, False), oe(e_v0, True), oe(e_t3, False), oe(e_v3, False)]]
)
right_face = pface(
    (1,0,0), (50,25,10), (0,1,0),
    [[oe(e_b1, True), oe(e_v2, True), oe(e_t1, False), oe(e_v1, False)]]
)

# ── Two half-cylinder hole walls — both share cyl_surf ───────────────────────
# Half A: theta=0..pi (seam0 → seamPi)
wallA_loop = f.edge_loop([
    oe(bot_A, False),    # bot half A reversed (bottom boundary, inward)
    oe(seam0_ec, True),  # seam0 going up
    oe(top_A, True),     # top half A
    oe(seamP_ec, False), # seam_pi going down
])
wallA_fob  = f.face_outer_bound(wallA_loop)
wallA_face = f._emit_raw(
    f"ADVANCED_FACE('hole_half_A',(#{wallA_fob.eid}),#{cyl_surf.eid},.T.)"
)

# Half B: theta=pi..2pi (seamPi → seam0)
wallB_loop = f.edge_loop([
    oe(bot_B, False),    # bot half B reversed
    oe(seamP_ec, True),  # seam_pi going up
    oe(top_B, True),     # top half B
    oe(seam0_ec, False), # seam0 going down
])
wallB_fob  = f.face_outer_bound(wallB_loop)
wallB_face = f._emit_raw(
    f"ADVANCED_FACE('hole_half_B',(#{wallB_fob.eid}),#{cyl_surf.eid},.T.)"
)

# ── Closed shell + solid ──────────────────────────────────────────────────────
shell = f.closed_shell([bot_face, top_face, front_face, back_face,
                        left_face, right_face, wallA_face, wallB_face])
msb = f.manifold_solid_brep(shell)
f.add_product_chain(msb, mode="brep_shape")

# ── PMI: SHAPE_ASPECT 'hole_feature' with two GISUs + DIMENSIONAL_SIZE ───────
# The shared SHAPE_ASPECT references both half-faces via separate GISUs.
# This is the defect target: receivers expecting one face per hole drop one GISU.
hole_asp = f._emit_raw(
    "SHAPE_ASPECT('hole_feature','through hole (two-half feature)',#9055,.T.)"
)
# Two GISUs — one per half-cylinder face.
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('GISU_A',$,#{hole_asp.eid},#9061,#{wallA_face.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('GISU_B',$,#{hole_asp.eid},#9061,#{wallB_face.eid})"
)
# Diameter DIMENSIONAL_SIZE on the shared SHAPE_ASPECT.
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{hole_asp.eid},'diameter')"
)
diam_mri = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(10.0),#9056)"
)
