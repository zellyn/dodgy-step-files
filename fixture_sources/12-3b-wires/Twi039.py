"""Twi039 — Wire self-intersection check fails on mirrored-then-rotated arc footprints.

Catalog claim: A custom pad shape consisting of one arc and one line is mirrored to
the bottom layer with a small non-zero rotation. The mirror negates Y but does not
invert the arc's parameterisation symmetrically, so the resulting wire's closure
check fails at floating-point ULP level; the wire reads as "not closed in 2D" or
"self-interfering" even though the geometry is fine.

Mechanism IS the EDGE_LOOP on a planar ADVANCED_FACE containing one CIRCLE-based
EDGE_CURVE (arc) and one LINE-based EDGE_CURVE; the vertices of the arc are placed
via mirrored-then-rotated coordinates (Y negated, then a small rotation applied)
such that the arc's start-point evaluation lands at a ULP-scale distance from the
closing vertex — this arc IS wired into the EDGE_LOOP which IS referenced by a
FACE_OUTER_BOUND in an ADVANCED_FACE in a SHELL_BASED_SURFACE_MODEL; never
orphaned. The ULP-scale closure gap IS the mechanism (false-positive self-
intersection on mirrored-and-rotated arc).

Reproducer: Planar face with a semicircle arc (radius 1, centre at origin, bottom
layer: Y-negated arc) connected by a closing line segment; one vertex carries a
1-ULP Y shift (~2.22e-16) to represent the mirror+rotation parameterisation skew.

Byte assertions:
  - count_entity_def(b'CIRCLE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - n_edges_total >= 2
  - face[0].surface_type == "plane"
  - n_vertices_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi039",
    defect=(
        "ADVANCED_FACE on a PLANE; EDGE_LOOP contains a CIRCLE-arc edge and a LINE edge; "
        "arc vertices are mirrored-then-rotated: one closing vertex carries a ULP-scale "
        "Y-offset (~2.22e-16) from the arc endpoint evaluation after Y-negation + 1° rotation; "
        "this ULP gap IS the mechanism (false-positive self-intersection / not-closed in 2D); "
        "both edges ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in shell; "
        "kernel closure-check must tolerate ULP-scale parameterisation skew"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: arc from (-1,0,0) to (1,0,0) via bottom; closing vertex has ULP shift ─
# v_left: true left endpoint of semicircle at (-1, 0, 0)
v_left  = f.vertex_point(f.cartesian_point((-1.0, 0.0, 0.0)))
# v_right: right endpoint — Y-negated mirror + 1° rotation introduces ULP skew
# cos(1°)=0.99984769, sin(1°)=0.01745241; for point (1,0): (0.99984769, 0.01745241)
# but mirror flips Y, then the parameterisation skew lands at ULP offset; we encode
# the skew directly as a tiny Y displacement representing the float rounding artifact.
ULP = 2.220446049250313e-16  # one ULP of 1.0
v_right = f.vertex_point(f.cartesian_point((1.0, ULP, 0.0)))

# ── Circle: centre at origin, radius 1, in XY plane ──────────────────────────
# Arc traverses bottom half: from v_right (1,ULP,0) CCW to v_left (-1,0,0) via (0,-1,0)
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, -1.0))   # -Z so arc goes through bottom (Y<0)
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_plc  = f.axis2_placement_3d(circ_orig, circ_zdir, circ_xdir)
circle    = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},1.0)")

e_arc  = f.edge_curve(v_right, v_left, circle)
oe_arc = f.oriented_edge(e_arc, True)

# ── Line: v_left → v_right (closing segment) ─────────────────────────────────
line_dir  = f.direction((1.0, 0.0, 0.0))
line_vec  = f.vector(line_dir, 2.0)
line_geom = f.line(f.cartesian_point((-1.0, 0.0, 0.0)), line_vec)
e_line    = f.edge_curve(v_left, v_right, line_geom)
oe_line   = f.oriented_edge(e_line, True)

# ── EDGE_LOOP: arc then closing line ─────────────────────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_arc.eid},#{oe_line.eid}))")

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
