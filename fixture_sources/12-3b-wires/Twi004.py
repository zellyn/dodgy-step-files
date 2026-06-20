"""Twi004 — ORIENTED_EDGE wrapping another ORIENTED_EDGE.

Catalog claim: An ORIENTED_EDGE whose edge_element is itself an ORIENTED_EDGE
instead of an EDGE_CURVE. Technically illegal but observed in the wild.
The translator's edge-loop transfer pass must chase wrapper chains until it
finds the underlying EDGE_CURVE, composing orientation flags as it descends.

Mechanism IS the double-wrapped edge reference: an outer ORIENTED_EDGE's
edge_element points at an inner ORIENTED_EDGE (which itself wraps an
EDGE_CURVE). Both ORIENTED_EDGE entities are emitted via _emit_raw to
reproduce the illegal wrapping exactly. The outer ORIENTED_EDGE IS
referenced in an EDGE_LOOP, which IS referenced by a FACE_OUTER_BOUND in an
ADVANCED_FACE in an OPEN_SHELL; never orphaned.

Reproducer: #1=ORIENTED_EDGE('',*,*,#2,.T.); #2=ORIENTED_EDGE(..,#3,.T.);
            #3=EDGE_CURVE(..);

Tier-3 assertions:
  - n_edges_total >= 1
  - face[0].surface_type == "plane"
  - n_vertices_total >= 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi004",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP whose single ORIENTED_EDGE "
        "has edge_element pointing at another ORIENTED_EDGE (not an EDGE_CURVE); "
        "the inner ORIENTED_EDGE wraps a proper EDGE_CURVE for a full-circle ellipse; "
        "translator must chase wrapper chain, composing orientation flags; "
        "never crash on double-wrapped ORIENTED_EDGE reference"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Full-circle EDGE_CURVE (circle so start == end, valid single-edge loop) ──
centre  = f.cartesian_point((0.0, 0.0, 0.0))
c_zdir  = f.direction((0.0, 0.0, 1.0))
c_xdir  = f.direction((1.0, 0.0, 0.0))
c_plc   = f.axis2_placement_3d(centre, c_zdir, c_xdir)
circle  = f._emit_raw(f"CIRCLE('',#{c_plc.eid},1.0)")

# Single vertex at (1,0,0): start == end for a closed circle.
p_v = f.cartesian_point((1.0, 0.0, 0.0))
v   = f.vertex_point(p_v)

# EDGE_CURVE wrapping the circle; same vertex for start and end (closed).
edge_curve = f._emit_raw(
    f"EDGE_CURVE('',#{v.eid},#{v.eid},#{circle.eid},.T.)"
)

# ── Inner ORIENTED_EDGE wrapping the EDGE_CURVE ───────────────────────────────
inner_oe = f._emit_raw(
    f"ORIENTED_EDGE('',*,*,#{edge_curve.eid},.T.)"
)

# ── Outer ORIENTED_EDGE whose edge_element IS the inner ORIENTED_EDGE ─────────
# This IS the defect: edge_element must be EDGE_CURVE per spec, not ORIENTED_EDGE.
outer_oe = f._emit_raw(
    f"ORIENTED_EDGE('',*,*,#{inner_oe.eid},.T.)"
)

# ── EDGE_LOOP references the outer (wrapped) ORIENTED_EDGE ────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{outer_oe.eid}))")

# Wire defect loop into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
