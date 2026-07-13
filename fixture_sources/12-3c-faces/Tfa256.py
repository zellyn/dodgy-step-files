"""Tfa256 — Face with two coincident-edge wires, multi-wire gate satisfied.

Catalog claim: a face with two or more wires contains one wire that consists
of exactly two edges which are the same edge entity traversed twice — a
zero-area "slit" loop that goes out along an edge and immediately back along
the identical curve. When the face carries at least one OTHER wire besides
the slit, the coincident-edge wire must be dropped entirely rather than kept
as a degenerate hole.

Mechanism: a single PLANE face carries TWO wires. The outer wire is an
ordinary valid 10x10 square (FACE_OUTER_BOUND). The inner wire (FACE_BOUND)
is the coincident-edge slit: the SAME EDGE_CURVE entity E — a short segment
from (3,3,0) to (7,3,0) inside the square — is referenced twice by two
ORIENTED_EDGEs, both at FORWARD orientation, forming a 2-edge loop that
bounds no area. Because the face now genuinely has 2 wires (not 1, as in the
prior single-wire fixture Tfa074, where the same reused-edge pattern was the
face's ONLY wire and therefore never reached the multi-wire repair path),
the coincident-edge-wire-removal repair's multi-wire precondition is
satisfied and the defect wire is live-reachable for it to act on.

Byte assertions:
  - contains(b'FACE_OUTER_BOUND')
  - contains(b'FACE_BOUND(')
  - count_entity_def(b'EDGE_CURVE') == 5

Tier-3 assertions:
  - load == "ok"
  - n_faces_total == 1
  - n_edges_total == 4
  - face[0].edge_count == 4
  - face[0].surface_type == "plane"
  - brepcheck.valid == True

Live oracle (2026-07-13, this worktree's OCP/OCCT 7.8.1, default import,
heal-on and heal-off identical): occt=shape(1)/shape(1) gmsh=shape(9)/shape(9)
ifc=schema_n/a. The authored file has 2 wires and 5 EDGE_CURVE entities (4
square + 1 reused twice); the LOADED shape carries only 4 edges and 1 wire —
the entire coincident-edge inner wire (both its edge references) is dropped,
not merely left unmerged. This is the opposite outcome from Tfa074, where the
identical reused-edge pattern survives as a live 2-edge zero-area sliver
because that face has only one wire and the repair's nbWires>=2 gate never
opens.
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa256",
    defect=(
        "Single PLANE face, TWO wires: FACE_OUTER_BOUND is a valid 10x10 square "
        "(0,0,0)-(10,0,0)-(10,10,0)-(0,10,0); FACE_BOUND is a 2-edge slit inside the "
        "square, reusing ONE EDGE_CURVE E=(3,3,0)-(7,3,0) twice via two ORIENTED_EDGEs "
        "both .T. (FORWARD) — the coincident-edge pattern; unlike the single-wire "
        "Tfa074 (whose face has ONLY this wire and never satisfies the nbWires>=2 gate "
        "the removal repair needs), this face's second, ordinary wire genuinely gives "
        "it 2 wires, so the repair's multi-wire precondition is live and reachable; "
        "both bounds ARE wired into one ADVANCED_FACE on a live OPEN_SHELL; "
        "never orphaned"
    ),
)

# ── Outer wire: valid 10x10 square ────────────────────────────────────────
p00 = f.cartesian_point(( 0.0,  0.0, 0.0))
p10 = f.cartesian_point((10.0,  0.0, 0.0))
p11 = f.cartesian_point((10.0, 10.0, 0.0))
p01 = f.cartesian_point(( 0.0, 10.0, 0.0))
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
ec0 = f.edge_curve(v00, v10, f.line(p00, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec1 = f.edge_curve(v10, v11, f.line(p10, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec2 = f.edge_curve(v11, v01, f.line(p11, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec3 = f.edge_curve(v01, v00, f.line(p01, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))
outer_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])
outer_bound = f.face_outer_bound(outer_loop)

# ── Inner wire: THE DEFECT — same EDGE_CURVE E used twice, both FORWARD ───
p_left  = f.cartesian_point((3.0, 3.0, 0.0))
p_right = f.cartesian_point((7.0, 3.0, 0.0))
v_left  = f.vertex_point(p_left)
v_right = f.vertex_point(p_right)
ec_E = f.edge_curve(
    v_left, v_right,
    f.line(p_left, f.vector(f.direction((1.0, 0.0, 0.0)), 4.0))
)
slit_loop = f.edge_loop([
    f.oriented_edge(ec_E, True),
    f.oriented_edge(ec_E, True),
])
inner_bound = f.face_bound(slit_loop)

ax0 = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face0 = f.advanced_face([outer_bound, inner_bound], f.plane(ax0))

open_sh = f.open_shell([face0])
sbsm = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa256.stp")
