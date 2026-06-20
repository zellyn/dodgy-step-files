"""Twi005 — ORIENTED_EDGE.edge_element references non-EDGE_CURVE.

Catalog claim: ORIENTED_EDGE.edge_element resolves to something other than
EDGE_CURVE (e.g. VERTEX_POINT, an unrelated geometric_representation_item,
or unresolved id). Dereferencing assumes EDGE_CURVE and crashes.

Mechanism IS the type-confused edge_element: the ORIENTED_EDGE's
edge_element slot holds a VERTEX_POINT instead of an EDGE_CURVE.
The defect ORIENTED_EDGE IS referenced in an EDGE_LOOP, which IS referenced
by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.
Kernel must validate the dereferenced entity's type before treating it as
an EDGE_CURVE; skip the oriented-edge with warning rather than crash.

Byte assertions:
  - count_entity_def(b'EDGE_CURVE') == 0
  - contains(b'VERTEX_POINT(')
  - contains(b'ORIENTED_EDGE(')

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi005",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP whose ORIENTED_EDGE "
        "has edge_element pointing at a VERTEX_POINT (not an EDGE_CURVE); "
        "no EDGE_CURVE entity is present in the file; "
        "kernel must validate entity type before dereference; "
        "must skip bad oriented-edge with warning; must not crash"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── VERTEX_POINT used as (wrong) edge_element target ─────────────────────────
# This is the entity that will be referenced where an EDGE_CURVE is expected.
p_bad = f.cartesian_point((1.0, 0.0, 0.0))
bad_vp = f.vertex_point(p_bad)

# ── ORIENTED_EDGE whose edge_element IS the VERTEX_POINT (defect mechanism) ──
bad_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bad_vp.eid},.T.)")

# ── EDGE_LOOP referencing the defect ORIENTED_EDGE ───────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{bad_oe.eid}))")

# Wire defect loop into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
