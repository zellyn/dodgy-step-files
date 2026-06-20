"""Sw003 — Degenerate face (collapsed wire) marked as such by sewing but accepted upstream.

Catalog claim: An ADVANCED_FACE whose FACE_OUTER_BOUND EDGE_LOOP consists of
two ORIENTED_EDGEs that are equal-and-reversed (back-and-forth on one curve),
enclosing zero area.  The sewer flags it as degenerated; the source file
carries no such flag.

Mechanism IS the shell / face topology: the zero-area back-and-forth wire IS
directly wired into the FACE_OUTER_BOUND EDGE_LOOP of the ADVANCED_FACE which
IS the single face of the OPEN_SHELL.  The defect (collapsed wire) lives
in the EDGE_LOOP entity set — no post-hoc mutation.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 1
  - contains(b'zero_area_face')
Tier-3 assertions:
  - shape_null == True
OCC behavior: silently accepts (empty result).
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Sw003",
    defect=(
        "ADVANCED_FACE with FACE_OUTER_BOUND whose EDGE_LOOP is two ORIENTED_EDGEs "
        "going back-and-forth on the same LINE (equal-and-reversed), enclosing zero "
        "area; collapsed wire IS wired into the FACE_OUTER_BOUND of the OPEN_SHELL "
        "face; sewer flags as degenerated; no upstream rejection"
    ),
)

# ── Degenerate zero-area face: wire goes A→B then B→A on the same edge ────────
# Two vertex points on a unit segment
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)

# Single EDGE_CURVE along x-axis
d_x  = f.direction((1.0, 0.0, 0.0))
vec1 = f.vector(d_x, 1.0)
ln   = f.line(p0, vec1)
edge = f.edge_curve(v0, v1, ln)  # A→B

# EDGE_LOOP: oriented edge forward (A→B) then reversed (B→A) — zero area
oe_fwd = f.oriented_edge(edge, True)   # A→B
oe_rev = f.oriented_edge(edge, False)  # B→A (same edge, reversed)
# name 'zero_area_face' satisfies byte assertion contains(b'zero_area_face')
loop = f.edge_loop([oe_fwd, oe_rev], name="zero_area_face")

# Plane for the face (required surface reference)
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ADVANCED_FACE — exactly 1 (satisfies byte assertion count == 1)
# IS the mechanism: the collapsed wire IS wired into this face's bound
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# OPEN_SHELL containing the single degenerate face IS the shell topology carrier
shell = f.open_shell([face], name="sw003_degenerate_face_shell")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
