"""Tfa209 — FixWiresTwoCoincEdges duplicate coincident edges

Square wire with two sequential identical edge instances (same curve, same
vertices) appearing as consecutive edges. Tests coincident-edge consolidation
branch that detects and merges redundant edge pairs sharing both endpoints.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The outer boundary
is a wire with 5 oriented edges instead of 4: the right-side edge appears twice
in sequence (edges 2 and 3 are the same edge entity, both oriented True). This
creates a wire with a duplicate coincident edge pair — two consecutive edges
sharing identical start/end vertices and using the same underlying EDGE_CURVE.
The OCCT FixWiresTwoCoincEdges code path at lines 2669-2726 detects the
duplicate by checking pairs of consecutive edges for shared endpoint vertices
and merges them into a single edge, cleaning the wire topology. The duplicate
coincident edge pair is the defect on the live traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa209",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "outer wire: 5 oriented edges forming square boundary; "
        "edges 2 and 3 are the SAME edge entity (right-side edge) both oriented True "
        "(coincident duplicate pair: identical curve, identical start/end vertices); "
        "FixWiresTwoCoincEdges lines 2669-2726: detects consecutive edges sharing "
        "both endpoints, consolidates duplicate into single edge; "
        "without consolidation: wire has redundant edge creating false loop segment; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Square vertices ───────────────────────────────────────────────────────────
p_ll = f.cartesian_point((0.0, 0.0, 0.0))
p_lr = f.cartesian_point((1.0, 0.0, 0.0))
p_ur = f.cartesian_point((1.0, 1.0, 0.0))
p_ul = f.cartesian_point((0.0, 1.0, 0.0))

v_ll = f.vertex_point(p_ll)
v_lr = f.vertex_point(p_lr)
v_ur = f.vertex_point(p_ur)
v_ul = f.vertex_point(p_ul)

# ── Square edges ──────────────────────────────────────────────────────────────
e_bot = f.edge_curve(v_ll, v_lr, f.line(p_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
# e_rgt appears TWICE as consecutive edges (coincident duplicate defect)
e_rgt = f.edge_curve(v_lr, v_ur, f.line(p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_top = f.edge_curve(v_ur, v_ul, f.line(p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_lft = f.edge_curve(v_ul, v_ll, f.line(p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

# Wire has 5 edges: e_bot, e_rgt (first instance), e_rgt (duplicate!), e_top, e_lft
face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),    # first instance
    f.oriented_edge(e_rgt, True),    # coincident duplicate — same edge entity
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa209.stp")
