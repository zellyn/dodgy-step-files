"""Twi001 — Empty edge_list in EDGE_LOOP.

Catalog claim: STEP EDGE_LOOP declared with empty edge aggregate
(EDGE_LOOP('',());). Translator drops the wire and fails the parent face;
bare reader crashed before guards added.

Mechanism IS the empty EDGE_LOOP: the defect entity is directly referenced
by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL — never orphaned.
The empty loop IS the topological bound of the face. Both the AP203/AP242
entity-reader's edge-loop attribute-validation and the topology translator's
edge-loop transfer pass must guard against the empty list.

Byte assertions:
  - contains(b"EDGE_LOOP('',())")
  - count_entity_def(b'ORIENTED_EDGE') == 0

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi001",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with empty edge list EDGE_LOOP('',()); "
        "empty EDGE_LOOP IS directly wired into face boundary topology; "
        "translator must reject loop with diagnostic; "
        "must not propagate null wire to face; must not crash"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Empty EDGE_LOOP: IS the defect mechanism ──────────────────────────────────
# Must use _emit_raw so the aggregate is genuinely empty (no edges at all).
empty_loop = f._emit_raw("EDGE_LOOP('',())")

# FACE_OUTER_BOUND and ADVANCED_FACE wire the empty loop into face topology.
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{empty_loop.eid},.T.)")
face = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")

# OPEN_SHELL: empty loop IS wired into shell/face topology.
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
