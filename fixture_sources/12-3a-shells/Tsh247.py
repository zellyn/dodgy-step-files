"""Tsh247 — Two faces sharing one real EDGE_CURVE with genuinely tangent
(G1) geometry: the default STEP read path's regularity-encoding pass
classifies the shared edge as smooth, not sharp (sew-merged-edge-
continuity-encoding GAP, bonus item — Wave-2 adjudication follow-up).

Catalog claim (occt-coverage GAP `sew-merged-edge-continuity-encoding`,
`exchange/sewing`): after two faces' edges are merged/shared, downstream
consumers need to know how smoothly the two adjoining faces meet there
(sharp corner vs. tangent-continuous vs. curvature-continuous).
`BRepBuilderAPI_Sewing::EdgeRegularity` calls `BRepLib::EncodeRegularity`
for every edge shared by exactly two faces. This class was originally
misclassified as a STEP-INEXPRESSIBLE/oracle-invisible carve-out; a
Wave-2 adversarial verifier REFUTED that (see BACKLOG.md, 2026-07-12):
`EncodeRegularity` is ALSO invoked unconditionally on the harness's
DEFAULT STEP read path — `XSControl_TransferReader::ShapeResult()` calls
`ShapeFix::EncodeRegularity(sh, tolang)` whenever `read.encoderegularity.
angle > 0`, which is OCCT's own default (0.01) and is never overridden by
this harness (`validate.py`/`_oracle_workers.py` only touch
`read.precision.*`, `read.maxprecision.*`, `read.stdsameparameter.mode`,
`read.surfacecurve.mode`) — so NO BRepBuilderAPI_Sewing scaffold is
needed at all for this class; a plain `STEPControl_Reader().
TransferRoots()/.OneShape()` read is sufficient, as long as the two faces
already SHARE the identical EDGE_CURVE entity (the corpus's standard
shared-edge-reuse convention used by dozens of shell/solid fixtures) and
the shared edge is genuinely G1 (tangent, not a sharp crease).

Geometry: a CYLINDRICAL_SURFACE (radius 5, axis +Z) face spanning
theta:[0,90deg], z:[0,10], and a PLANE face at x=5 (normal +X — matching
the cylinder's own outward radial normal at theta=0) spanning y:[-5,0],
z:[0,10]. Both faces reference the SAME EDGE_CURVE entity for their
theta=0/x=5 boundary (the vertical line x=5,y=0,z:[0,10]) — a plane
tangent to a cylinder along one of its generatrices is the textbook G1
(smooth, non-sharp) shared-edge case.

Live verification (this worktree's OCP/OCCT 7.8.1): read via plain
`STEPControl_Reader().TransferRoots()/.OneShape()` (no sewing scaffold).
The shared edge (found by walking both faces' wires and confirming
identical `TopoDS_Edge` identity) queried via `BRep_Tool::Continuity
(edge, face1, face2)` returns `GeomAbs_G1` — NOT the un-encoded default
`GeomAbs_C0` — confirming `EncodeRegularity` genuinely ran and correctly
classified the tangent join. A control comparison (`BRepPrimAPI_MakeBox`
cube written to STEP and read back the same way, all 12 edges genuinely
sharp 90deg corners) keeps EVERY shared edge `GeomAbs_C0` under the
identical read path, ruling out a false positive (i.e. `EncodeRegularity`
is not simply stamping every shared edge non-C0 regardless of actual
geometry).

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'PLANE') == 1
  - count_entity_def(b'ADVANCED_FACE') == 2
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh247",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs — a CYLINDRICAL_SURFACE "
        "(radius 5, axis +Z) quarter-patch and a PLANE at x=5 (normal "
        "+X, matching the cylinder's own outward radial normal at "
        "theta=0) — sharing the SAME EDGE_CURVE entity (the vertical "
        "generatrix line x=5,y=0,z:[0,10]) as their common boundary; the "
        "shared edge is genuinely G1-tangent (plane-tangent-to-cylinder), "
        "not a sharp crease, so BRepLib::EncodeRegularity (invoked "
        "unconditionally on the default STEP read path via "
        "ShapeFix::EncodeRegularity) must classify it as smooth"
    ),
)

R = 5.0
H = 10.0

# ── Shared vertices/edge: x=5, y=0, z:[0,10] — the tangent generatrix ──────
p_b0 = f.cartesian_point((R, 0.0, 0.0))
p_t0 = f.cartesian_point((R, 0.0, H))
v_b0 = f.vertex_point(p_b0)
v_t0 = f.vertex_point(p_t0)

d_pz = f.direction((0.0, 0.0, 1.0))
vec_shared = f.vector(d_pz, H)
ln_shared = f.line(p_b0, vec_shared)
shared_edge = f.edge_curve(v_b0, v_t0, ln_shared)

# ── Cylinder face: theta:[0,90], z:[0,H] ────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

p_t90 = f.cartesian_point((0.0, R, H))
p_b90 = f.cartesian_point((0.0, R, 0.0))
v_t90 = f.vertex_point(p_t90)
v_b90 = f.vertex_point(p_b90)

# Straight edge at theta=90: v_t90 -> v_b90
d_mz = f.direction((0.0, 0.0, -1.0))
vec_t90 = f.vector(d_mz, H)
ln_t90 = f.line(p_t90, vec_t90)
edge_theta90 = f.edge_curve(v_t90, v_b90, ln_t90)

# Top arc (z=H): v_t0 -> v_t90, quarter circle theta:0->90
top_circ_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, H)), cyl_zdir, cyl_xdir)
top_circ = f.circle(top_circ_plc, R)
arc_top = f.edge_curve(v_t0, v_t90, top_circ)

# Bottom arc (z=0): v_b90 -> v_b0, quarter circle theta:90->0
bot_circ_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), cyl_zdir, cyl_xdir)
bot_circ = f.circle(bot_circ_plc, R)
arc_bottom = f.edge_curve(v_b90, v_b0, bot_circ)

loop_cyl = f.edge_loop([
    f.oriented_edge(shared_edge, True),   # v_b0 -> v_t0
    f.oriented_edge(arc_top, True),        # v_t0 -> v_t90
    f.oriented_edge(edge_theta90, True),   # v_t90 -> v_b90
    f.oriented_edge(arc_bottom, True),     # v_b90 -> v_b0
])
fob_cyl = f.face_outer_bound(loop_cyl)
face_cyl = f.advanced_face([fob_cyl], cyl_surf)

# ── Plane face: x=5 (normal +X), y:[-5,0], z:[0,H] ──────────────────────────
plane_orig = f.cartesian_point((R, 0.0, 0.0))
plane_normal = f.direction((1.0, 0.0, 0.0))  # matches cylinder's outward normal at theta=0
plane_refdir = f.direction((0.0, 0.0, 1.0))
plane_plc = f.axis2_placement_3d(plane_orig, plane_normal, plane_refdir)
plane_surf = f.plane(plane_plc)

p_t_out = f.cartesian_point((R, -5.0, H))
p_b_out = f.cartesian_point((R, -5.0, 0.0))
v_t_out = f.vertex_point(p_t_out)
v_b_out = f.vertex_point(p_b_out)

d_my = f.direction((-1.0, 0.0, 0.0))  # placeholder unused
d_negy = f.direction((0.0, -1.0, 0.0))
vec_t_out = f.vector(d_negy, 5.0)
ln_t_out = f.line(p_t0, vec_t_out)
edge_t_out = f.edge_curve(v_t0, v_t_out, ln_t_out)

vec_b_out = f.vector(d_mz, H)
ln_b_out = f.line(p_t_out, vec_b_out)
edge_out_down = f.edge_curve(v_t_out, v_b_out, ln_b_out)

d_posy = f.direction((0.0, 1.0, 0.0))
vec_b_back = f.vector(d_posy, 5.0)
ln_b_back = f.line(p_b_out, vec_b_back)
edge_b_back = f.edge_curve(v_b_out, v_b0, ln_b_back)

loop_plane = f.edge_loop([
    f.oriented_edge(shared_edge, False),  # v_t0 -> v_b0 (opposite sense for this face)
    f.oriented_edge(edge_b_back, False),  # v_b0 -> v_b_out (reversed: edge_b_back is b_out->b0)
    f.oriented_edge(edge_out_down, False),  # v_b_out -> v_t_out (reversed: edge_out_down is t_out->b_out)
    f.oriented_edge(edge_t_out, False),   # v_t_out -> v_t0 (reversed: edge_t_out is t0->t_out)
])
fob_plane = f.face_outer_bound(loop_plane)
face_plane = f.advanced_face([fob_plane], plane_surf)

# ── Both faces in one OPEN_SHELL, sharing the SAME EDGE_CURVE entity ───────
shell = f.open_shell([face_cyl, face_plane], name="tsh247_tangent_shared_edge_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
