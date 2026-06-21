"""Twi236 — ShapeFix_Wire.FixGaps3d bridge-creates-degeneracy.

Catalog claim: Wire has a 3D gap at a junction (endpoints separated by ~1e-8,
within tolerance). FixGaps3d attempts to bridge by creating a new edge, but
the bridge itself becomes degenerate with coincident or near-coincident
endpoints.

Mechanism: OPEN_SHELL with one planar face whose EDGE_LOOP has a tiny gap
at one junction (~1e-8 separation) that is within the declared tolerance
(1e-6). A filler edge of length 1e-8 is present as the bridge — it has
nearly-coincident start/end vertices. The shell gives OCC shape(1) but
conservative kernels see a degenerate-bridge wire defect.

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

GAP = 1.0e-8  # gap size — within declared tolerance 1e-6

f = StepFile(
    catalog_id="Twi236",
    defect=(
        "EDGE_LOOP on a planar face has a 1e-8 mm 3D gap at one vertex junction; "
        "declared tolerance is 1e-6 (gap is sub-tolerance); "
        "FixGaps3d bridges via a new edge whose endpoints are ~1e-8 apart (degenerate); "
        "bridge-edge itself becomes degenerate with near-coincident vertices; "
        "OPEN_SHELL with one ADVANCED_FACE — OCC loads shape(1)"
    ),
)

# Host plane z=0, normal +z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# Corner points: a 10x10 square with a tiny gap in the bottom edge
# Bottom-left to bottom-right-minus-gap: main segment
# Then tiny bridge: from (10-GAP, 0, 0) to (10, 0, 0)
# Right, top, left edges complete the square
p_bl = f.cartesian_point((0.0,        0.0, 0.0))
p_br_gap = f.cartesian_point((10.0 - GAP, 0.0, 0.0))  # gap endpoint
p_br = f.cartesian_point((10.0,       0.0, 0.0))       # true corner
p_tr = f.cartesian_point((10.0,      10.0, 0.0))
p_tl = f.cartesian_point(( 0.0,      10.0, 0.0))

v_bl     = f.vertex_point(p_bl)
v_br_gap = f.vertex_point(p_br_gap, name="v_br_gap_end")     # near-coincident with v_br
v_br     = f.vertex_point(p_br,     name="v_br_bridge_start") # bridge start
v_tr     = f.vertex_point(p_tr)
v_tl     = f.vertex_point(p_tl)

# Bottom main edge: BL → BR_gap
d_bot = f.direction((1.0, 0.0, 0.0))
vec_bot = f.vector(d_bot, 10.0 - GAP)
l_bot = f.line(p_bl, vec_bot)
e_bot = f.edge_curve(v_bl, v_br_gap, l_bot, name="e_bot_main")

# Bridge edge: BR_gap → BR (nearly-coincident, length ~1e-8) — THE DEFECT
# This is the degenerate bridge FixGaps3d would create
d_bridge = f.direction((1.0, 0.0, 0.0))
vec_bridge = f.vector(d_bridge, GAP)
l_bridge = f.line(p_br_gap, vec_bridge)
e_bridge = f.edge_curve(v_br_gap, v_br, l_bridge, name="e_bridge_degenerate")

# Right edge: BR → TR
d_rgt = f.direction((0.0, 1.0, 0.0))
vec_rgt = f.vector(d_rgt, 10.0)
l_rgt = f.line(p_br, vec_rgt)
e_rgt = f.edge_curve(v_br, v_tr, l_rgt, name="e_right")

# Top edge: TL → TR (reversed)
d_top = f.direction((1.0, 0.0, 0.0))
vec_top = f.vector(d_top, 10.0)
l_top = f.line(p_tl, vec_top)
e_top = f.edge_curve(v_tl, v_tr, l_top, name="e_top")

# Left edge: BL → TL
d_lft = f.direction((0.0, 1.0, 0.0))
vec_lft = f.vector(d_lft, 10.0)
l_lft = f.line(p_bl, vec_lft)
e_lft = f.edge_curve(v_bl, v_tl, l_lft, name="e_left")

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_bridge, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
