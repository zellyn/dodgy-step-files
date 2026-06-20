"""Tfa016 — Adjacent faces share same supporting surface (redundant internal edge).

Catalog claim: Two or more coplanar faces from a Boolean union remain separate
even though they share one underlying surface, joined by an artificial internal
edge that does not separate distinct geometry. Feature recognition and CAM/FEA
pipelines see redundant topology where the input was a single feature.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs sharing one PLANE:
  face[0] — left 10×10 square on the shared plane (x:0–10, y:0–10)
  face[1] — right 10×10 square on the SAME PLANE (x:10–20, y:0–10)
  The shared edge at x=10 (from (10,0,0) to (10,10,0)) appears in both
  loops with opposing orientations — the "artificial internal edge" that
  UnifySameDomain would dissolve.
  Both ADVANCED_FACEs reference the SAME PLANE entity (same surface).

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 8
  face[1].surface_type == "plane"
  n_vertices_total >= 16

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa016",
    defect=(
        "OPEN_SHELL: two 10×10 coplanar ADVANCED_FACEs sharing one PLANE entity; "
        "face[0] left square (x:0–10), face[1] right square (x:10–20); "
        "artificial internal edge at x=10 shared by both loops (EDGE_CURVE #71 "
        "used .T. in face[0] and .F. in face[1] — the redundant internal edge); "
        "UnifySameDomain healer must dissolve this edge and merge both faces; "
        "defect is live on face traversal path — same PLANE entity referenced by both faces"
    ),
)

# Shared PLANE — both ADVANCED_FACEs reference this same surface entity
sh_orig  = f.cartesian_point((0.0, 0.0, 0.0))
sh_zdir  = f.direction((0.0, 0.0, 1.0))
sh_xdir  = f.direction((1.0, 0.0, 0.0))
sh_plc   = f.axis2_placement_3d(sh_orig, sh_zdir, sh_xdir)
shared_plane = f.plane(sh_plc)

# ── Vertices for two adjacent 10×10 squares ───────────────────────────────────
# Left square: (0,0,0)–(10,0,0)–(10,10,0)–(0,10,0)
# Right square: (10,0,0)–(20,0,0)–(20,10,0)–(10,10,0)
# Shared edge: (10,0,0)→(10,10,0)

p0 = f.cartesian_point(( 0.0,  0.0, 0.0))   # left-bottom-left
p1 = f.cartesian_point((10.0,  0.0, 0.0))   # shared-bottom (also right-bottom-left)
p2 = f.cartesian_point((10.0, 10.0, 0.0))   # shared-top (also right-top-left)
p3 = f.cartesian_point(( 0.0, 10.0, 0.0))   # left-top-left
p4 = f.cartesian_point((20.0,  0.0, 0.0))   # right-bottom-right
p5 = f.cartesian_point((20.0, 10.0, 0.0))   # right-top-right

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)
v5 = f.vertex_point(p5)

# ── Edges ────────────────────────────────────────────────────────────────────
# Left face edges
ec_a_bot  = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_shared = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_a_top  = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_a_left = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

# Right face edges
ec_b_bot   = f.edge_curve(v1, v4, f.line(p1, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_b_right = f.edge_curve(v4, v5, f.line(p4, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_b_top   = f.edge_curve(v5, v2, f.line(p5, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))

# ── face[0]: left square — uses shared edge forward (.T.) ────────────────────
loop_a = f.edge_loop([
    f.oriented_edge(ec_a_bot,   True),   # (0,0)→(10,0)
    f.oriented_edge(ec_shared,  True),   # (10,0)→(10,10)  [internal edge fwd]
    f.oriented_edge(ec_a_top,   True),   # (10,10)→(0,10)
    f.oriented_edge(ec_a_left,  True),   # (0,10)→(0,0)
])
fob_a = f.face_outer_bound(loop_a)
face_a = f.advanced_face([fob_a], shared_plane)

# ── face[1]: right square — uses shared edge reversed (.F.) ──────────────────
loop_b = f.edge_loop([
    f.oriented_edge(ec_b_bot,   True),   # (10,0)→(20,0)
    f.oriented_edge(ec_b_right, True),   # (20,0)→(20,10)
    f.oriented_edge(ec_b_top,   True),   # (20,10)→(10,10)
    f.oriented_edge(ec_shared,  False),  # (10,10)→(10,0)  [internal edge rev — DEFECT]
])
fob_b = f.face_outer_bound(loop_b)
face_b = f.advanced_face([fob_b], shared_plane)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa016.stp")
