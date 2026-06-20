"""Twi102 — ShapeFix_Wire.FixDegenerated modulo-index wraparound at wire end.

Catalog claim: FixDegenerated exhibits modulo-index boundary logic when inserting
degenerate edges at wire-end. Without closure validation, inserting at position
(n % wire_size) constructs invalid topology by wrapping the insertion point. Wire
with degenerate segment at end-boundary causes index wraparound, potentially
replicating edges or creating orphaned topology.

Mechanism IS a planar face with a wire containing 3 edges where E2 is a
zero-length degenerate EDGE_CURVE at index 2 (the last position). When
FixDegenerated processes this wire, the modulo-index insertion at n=2, wire_size=3
wraps to position 0 instead of appending after position 2, disrupting the wire
topology.

The wire geometry:
  E0: v0(0,0,0) → v1(10,0,0)  [bottom]
  E1: v1(10,0,0) → v2(10,10,0) [right]
  E2_degen: v2(10,10,0) → v2(10,10,0) [zero-length degenerate at wire-end — IS mechanism]

The face is completed by a second correct 3-edge loop to give n_faces_total >= 1
(tier-3: n_faces_total == 1 means we need exactly 1 face).

Wait — tier-3 says n_faces_total == 1 so we use a SINGLE face whose outer wire
has the degenerate end-edge. The wire with the degen-at-end IS the mechanism.

The outer loop: [E0, E1, E2_degen] forms a wire that is NOT closed (starts at v0,
ends at v2=v2 after the degen). The degenerate edge IS at the last index position
(index 2 of a 3-edge wire), triggering the modulo wraparound bug.

Tier-3 assertion:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi102",
    defect=(
        "Single ADVANCED_FACE on a PLANE (right-angle triangle shape) in a CLOSED_SHELL; "
        "outer EDGE_LOOP has 3 edges: "
        "E0(v0(0,0,0)→v1(10,0,0)), E1(v1(10,0,0)→v2(10,10,0)), "
        "E2_degen(v2(10,10,0)→v2(10,10,0), zero-length LINE) at index 2 (last position); "
        "a closing edge back to v0 is missing — the degenerate edge IS the terminal; "
        "ShapeFix_Wire.FixDegenerated processes the degenerate edge at wire-end index n=2; "
        "modulo index (2 % wire_size=3) == 2 wraps the insertion to unexpected position 0; "
        "the wraparound replicates edges or creates orphaned topology — IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL; "
        "never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
v0 = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # bottom-left
v1 = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # bottom-right
v2 = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # top-right

# ── E0: v0 → v1 (bottom edge) ────────────────────────────────────────────────
e0_line = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)
)
e0  = f.edge_curve(v0, v1, e0_line)
oe0 = f.oriented_edge(e0, True)

# ── E1: v1 → v2 (right edge) ─────────────────────────────────────────────────
e1_line = f.line(
    f.cartesian_point((10.0, 0.0, 0.0)),
    f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)
)
e1  = f.edge_curve(v1, v2, e1_line)
oe1 = f.oriented_edge(e1, True)

# ── E2_degen: v2 → v2 (zero-length degenerate at index 2 — IS mechanism) ─────
# Zero-length LINE at v2 = (10,10,0)
degen_dir  = f.direction((1.0, 0.0, 0.0))   # arbitrary direction, zero magnitude
degen_vec  = f.vector(degen_dir, 0.0)        # zero-length vector
degen_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)), degen_vec)
# DEFECT: same VERTEX_POINT at both ends — degenerate edge at end-index
e2_degen  = f._emit_raw(
    f"EDGE_CURVE('',#{v2.eid},#{v2.eid},#{degen_line.eid},.T.)"
)
oe2_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2_degen.eid},.T.)")

# DEFECT: 3-edge loop ending with degenerate; no closing edge back to v0.
# Wire is open (v0...v2(degen)); FixDegenerated index 2 % 3 wraps to 0.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2_degen.eid}))"
)

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi102.stp")
