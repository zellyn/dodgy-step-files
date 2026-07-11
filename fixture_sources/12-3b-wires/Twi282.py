"""Twi282 — Cyclic ORIENTED_EDGE.edge_element self-reference (unbounded
EdgeStart/EdgeEnd recursion → stack-overflow DoS).

Catalog claim: an ORIENTED_EDGE whose 4th arg (edge_element) references
ITSELF, e.g. `#N=ORIENTED_EDGE('',*,*,#N,.F.);`. The spec requires
edge_element to be an EDGE (ultimately an EDGE_CURVE); here it is the
ORIENTED_EDGE itself. OCCT's derived-attribute accessors
`StepShape_OrientedEdge::EdgeStart()`/`EdgeEnd()` delegate to
`edge_element->EdgeStart()` (swapping to EdgeEnd when orientation=.F.);
a self-cycle never reaches an EDGE_CURVE, so the two accessors recurse
into each other forever and blow the C stack (fuzz-grade DoS).

Distinct from Twi004 (a FINITE wrapper chain that terminates at an
EDGE_CURVE and is healed by traversal — silent-empty, no crash). This is
the UNBOUNDED-cycle variant. Cross-listed with §12.11 Ad (adversarial /
fuzz DoS): a receiver must chase ORIENTED_EDGE wrapper chains under a
depth/visited-set guard and give up gracefully, never stack-overflow.

Mechanism IS the self-referential ORIENTED_EDGE: its edge_element points
at its own entity id (obtained via the f._next_id peek trick, as in
Xp007's self-referential REPRESENTATION_RELATIONSHIP). It is wired into
an EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE (on a PLANE) → OPEN_SHELL
so the transfer pass dereferences it; never orphaned.

Byte assertions:
  contains(b'ORIENTED_EDGE')
  count_entity_def(b'ORIENTED_EDGE') == 1        # single self-loop, not a chain
  matches(rb"#(\d+)=ORIENTED_EDGE\('',\*,\*,#\1,\.F\.\)")   # literal self-reference

Expected (PROVISIONAL — crasher; oracle not run in this worktree):
  occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi282",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP whose single ORIENTED_EDGE "
        "has its edge_element (4th arg) pointing at ITSELF — a cyclic "
        "self-reference with no EDGE_CURVE anywhere in the cycle; the derived "
        "EdgeStart()/EdgeEnd() accessors recurse into each other unbounded and "
        "overflow the stack; receiver must guard wrapper-chain traversal with a "
        "visited-set/depth bound and never crash"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Cyclic self-referential ORIENTED_EDGE ─────────────────────────────────────
# Peek the id this entity will receive so it can reference itself; the
# edge_element (4th positional arg) IS its own id — an unbounded cycle.
cyc_eid = f._next_id
cyc = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{cyc_eid},.F.)")

# ── Wire the self-cycle into a reachable face/shell so the transfer pass
#    dereferences it; never orphaned. ─────────────────────────────────────────
loop  = f._emit_raw(f"EDGE_LOOP('',(#{cyc.eid}))")
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
