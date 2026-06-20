"""Twi040 — EDGE_CURVE LINE slightly off CYLINDRICAL_SURFACE (~Precision::Confusion() deviation):
"Could not fix wire in surface" regression after OCCT version bump.

Catalog claim: An EDGE_CURVE LINE on a CYLINDRICAL_SURFACE whose start point is
offset from the surface by Precision::Confusion()-scale (e.g. line starting at
(10.0000001, 0, 0) on a R=10 cylinder while the endpoint VERTEX_POINTs lie exactly
on R=10). Until gmsh 4.11 this logged a warning and fixed the wire; from 4.12 the
same input throws fatal exceptions; a tolerance-handling regression.

Mechanism IS the EDGE_LOOP on a CYLINDRICAL_SURFACE ADVANCED_FACE whose one
EDGE_CURVE LINE start-point is at (10.0000001, 0, 0) — offset from the R=10
cylinder surface by ~1e-7 (Precision::Confusion() scale) — while both
VERTEX_POINTs lie exactly on R=10. This LINE IS the 3D curve of the EDGE_CURVE,
which IS wired into the EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in a
SHELL_BASED_SURFACE_MODEL; never orphaned. The sub-Confusion() offset IS the
mechanism (wire-in-surface fix failure / tolerance regression).

Reproducer: Cylindrical face (R=10, height 5) with a seam edge whose LINE
starts at (10.0000001, 0, 0) instead of exactly (10, 0, 0).

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - face[0].surface_type == "cylinder"
  - n_edges_total >= 1
  - n_vertices_total >= 2
  - brepcheck.valid == False

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi040",
    defect=(
        "ADVANCED_FACE on a CYLINDRICAL_SURFACE R=10, height=5; "
        "EDGE_LOOP contains one EDGE_CURVE whose LINE start-point is at "
        "(10.0000001, 0, 0) — offset ~1e-7 from the R=10 cylinder surface; "
        "both VERTEX_POINTs lie exactly on R=10; "
        "this Precision::Confusion()-scale offset IS the mechanism "
        "(wire-in-surface fix failure / tolerance regression after OCCT bump); "
        "EDGE_CURVE IS wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in shell; "
        "kernel must degrade to warn-and-accept rather than fatal error"
    ),
)

# ── Cylindrical surface: R=10, axis along +Z ─────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},10.0)")

# ── Two vertices on the seam line at θ=0 ─────────────────────────────────────
# Both lie exactly on R=10
v_bot = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))   # z=0, exactly on R=10
v_top = f.vertex_point(f.cartesian_point((10.0, 0.0, 5.0)))   # z=5, exactly on R=10

# ── Seam edge: LINE whose start is offset by ~1e-7 from the cylinder surface ─
# The defect: line origin at (10.0000001, 0, 0) instead of (10, 0, 0)
seam_line_orig = f.cartesian_point((10.0000001, 0.0, 0.0))    # <-- offset IS mechanism
seam_line_dir  = f.direction((0.0, 0.0, 1.0))
seam_line_vec  = f.vector(seam_line_dir, 5.0)
seam_line      = f.line(seam_line_orig, seam_line_vec)

e_seam  = f.edge_curve(v_bot, v_top, seam_line)
oe_seam = f.oriented_edge(e_seam, True)

# ── EDGE_LOOP with single seam edge (degenerate cylinder patch / seam only) ──
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_seam.eid}))")

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
