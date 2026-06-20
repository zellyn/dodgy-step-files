"""Twi006 — ORIENTED_EDGE underlying EDGE_CURVE is null/missing reference.

Catalog claim: ORIENTED_EDGE whose edge_element slot is `$` or null reference
(or unresolved id), or — conversely — derived attributes edge_start/edge_end
filled with explicit vertices instead of `*`. Either form violates Part-21
§6.4.4 but is seen in the wild.

Mechanism IS the null edge_element in the ORIENTED_EDGE: one ORIENTED_EDGE
in the EDGE_LOOP has its edge_element slot set to `$` (null/missing
reference). A second, valid ORIENTED_EDGE closes the loop so the file
parses. The defect ORIENTED_EDGE IS referenced in an EDGE_LOOP, which IS
referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL;
never orphaned. Kernel must heal and accept: normalize / tolerate the null
form on read; coerce derived attributes to `*` on write per spec.

Tier-3 assertions:
  - n_edges_total >= 1
  - face[0].surface_type == "plane"
  - n_vertices_total >= 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi006",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two ORIENTED_EDGEs; "
        "the first ORIENTED_EDGE has edge_element = $ (null/missing reference); "
        "the second is a valid half-circle EDGE_CURVE so the loop parses; "
        "null edge_element IS the defect; kernel must normalize/tolerate on read; "
        "must coerce derived attributes to * on write per Part-21 §6.4.4"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Valid EDGE_CURVE: half-circle from (1,0,0) to (-1,0,0) ───────────────────
# This provides the loop's valid edge; the other will be the null-ref edge.
centre  = f.cartesian_point((0.0, 0.0, 0.0))
c_zdir  = f.direction((0.0, 0.0, 1.0))
c_xdir  = f.direction((1.0, 0.0, 0.0))
c_plc   = f.axis2_placement_3d(centre, c_zdir, c_xdir)
circle  = f._emit_raw(f"CIRCLE('',#{c_plc.eid},1.0)")

p_right = f.cartesian_point(( 1.0, 0.0, 0.0))
p_left  = f.cartesian_point((-1.0, 0.0, 0.0))
v_right = f.vertex_point(p_right)
v_left  = f.vertex_point(p_left)

# Valid EDGE_CURVE: right → left along the upper half of the circle.
ec_valid = f._emit_raw(
    f"EDGE_CURVE('',#{v_right.eid},#{v_left.eid},#{circle.eid},.T.)"
)

# ── Defect ORIENTED_EDGE: edge_element = $ (null reference) ──────────────────
# This IS the mechanism. Its start/end in the loop would go left → right
# (closing the loop), but the edge_element is missing.
oe_null  = f._emit_raw("ORIENTED_EDGE('',*,*,$,.T.)")

# ── Valid ORIENTED_EDGE wrapping the good EDGE_CURVE ─────────────────────────
oe_valid = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_valid.eid},.T.)")

# ── EDGE_LOOP: null-ref edge followed by valid edge ───────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_null.eid},#{oe_valid.eid}))")

# Wire defect loop into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
