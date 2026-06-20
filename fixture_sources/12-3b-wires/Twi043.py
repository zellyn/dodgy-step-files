"""Twi043 — Disjoined / nearly-coincident wire vertices need merge or split decision.

Catalog claim: A wire's vertices include same-coordinate or close-coordinate vertices
that the global vertex-equality tolerance would treat as separate, but local context
(wire-level adjacency) suggests they should be merged. Or a wire may have a single
vertex referenced where two distinct vertices are required.

Mechanism IS the EDGE_LOOP on a planar ADVANCED_FACE where two adjacent EDGE_CURVEs
share a topological seam vertex, but their respective geometric VERTEX_POINTs are at
(0,0,0) and (1e-7,0,0) — separated by a distance that lies below the global
UNCERTAINTY_MEASURE_WITH_UNIT (1e-6) but is nonzero, so the kernel's global equality
test would treat them as distinct. These two VERTEX_POINTs ARE the mechanism; both
are wired into EDGE_CURVEs that ARE in the EDGE_LOOP → FACE_OUTER_BOUND →
ADVANCED_FACE in a SHELL_BASED_SURFACE_MODEL; never orphaned. The wire-local context
requires a merge-or-split decision based on local tolerance, not global.

Reproducer: Triangular planar face where vertex v_B is used by edge_1 as its end,
while a distinct vertex v_B2 at (1e-7, 0, 0) is used by edge_2 as its start;
global tolerance is 1e-6, so |v_B - v_B2| < tolerance but they are separate entities.

Byte assertions:
  - count_entity_def(b'PLANE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - n_edges_total >= 3
  - face[0].surface_type == "plane"
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi043",
    defect=(
        "ADVANCED_FACE on a PLANE; EDGE_LOOP contains three EDGE_CURVEs forming a triangle; "
        "edge_1 ends at VERTEX_POINT v_B at (0.0,0.0,0.0); "
        "edge_2 starts at DISTINCT VERTEX_POINT v_B2 at (1e-7,0.0,0.0); "
        "these two vertices are separate STEP entities but |v_B - v_B2| = 1e-7 < global tolerance 1e-6; "
        "the sub-tolerance gap between v_B and v_B2 IS the mechanism (merge-or-split decision needed); "
        "all three edges ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in shell; "
        "kernel must use wire-local context, not global tolerance, for the merge decision"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices — two near-coincident at the seam ────────────────────────────────
v_A  = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))      # apex
v_B  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))      # base-left (end of edge_1)
v_B2 = f.vertex_point(f.cartesian_point((1e-7, 0.0, 0.0)))     # near-coincident (start of edge_2) IS mechanism
v_C  = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))      # base-right (shared cleanly)

# ── Edge_1: v_C → v_B  (right base to base-left — clean end) ─────────────────
e1_line = f.line(f.cartesian_point((2.0, 2.0, 0.0)),
                 f.vector(f.direction((-1.0, -1.0, 0.0)), 2.0 * (2.0**0.5)))
e1  = f.edge_curve(v_C, v_B, e1_line)
oe1 = f.oriented_edge(e1, True)

# ── Edge_2: v_B2 → v_A  (near-coincident start) ──────────────────────────────
e2_line = f.line(f.cartesian_point((1e-7, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 2.0))
e2  = f.edge_curve(v_B2, v_A, e2_line)
oe2 = f.oriented_edge(e2, True)

# ── Edge_3: v_A → v_C  (apex to base-right) ──────────────────────────────────
e3_line = f.line(f.cartesian_point((2.0, 0.0, 0.0)),
                 f.vector(f.direction((0.0, 1.0, 0.0)), 2.0))
e3  = f.edge_curve(v_A, v_C, e3_line)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
