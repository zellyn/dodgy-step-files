"""Gp191 — Pcurve whose 2D trim parameters literally collapse to a point
(w1==w2) on an otherwise real, non-degenerate 3D edge (stp-pcurve-trim-
range-repair, PARTIAL, missing subvariant (a): "a pcurve whose 2D trim
parameters literally collapse to a point (w1==w2) on an otherwise real,
non-degenerate 3D edge -- pcurve dropped, edge kept 3D-only"). Live
result differs from the catalog's literal "dropped" prediction -- see the
IMPORTANT live finding below; recorded honestly.

Catalog claim: CheckPCurves (StepToTopoDS_TranslateEdgeLoop.cxx:104-169,
a post-pass run over every edge of a finished wire) detects when a
pcurve's own 2D parameter range collapses to a single point (w1==w2,
:134-140) and drops that single pcurve via RemoveSinglePCurve, leaving the
edge's 3D curve intact but with no 2D representation on that face. This
is the 2D/parametric-space analog of stp-edge-curve-param-range, but
operating on face-boundary pcurves rather than the edge's own 3D curve.
Gp007/Gn019/Gs007/Gp028 all present pcurve DOMAIN mismatches (out-of-
bounds, periodic-band) but none presents a literal w1==w2 collapsed
range. This fixture does: the 3D curve genuinely spans a real 1-unit
LINE (edge_positive_length_3d, (0,0,0)->(1,0,0)), but its PCURVE
(collapsed_pcurve_edge) is a UV LINE with a zero-magnitude VECTOR --
its own 2D domain literally has w1==w2, regardless of the 3D edge's real
traversal.

Mechanism: PLANE host (z=0). EDGE_CURVE 'collapsed_pcurve_edge' between
v_start(0,0,0) and v_end(1,0,0): 3D curve is a real LINE of length 1
wrapped in a SURFACE_CURVE with ONE PCURVE whose own 2D LINE has a
zero-magnitude VECTOR (w1==w2 literally, collapsed to the point (0,0) in
UV regardless of which 3D point the edge is evaluated at). ADVANCED_FACE
-> OPEN_SHELL -> SHELL_BASED_SURFACE_MODEL -> PRODUCT chain; never
orphaned.

Byte assertions:
  - contains(b'collapsed_pcurve_edge')
  - contains(b'edge_positive_length_3d')
  - count_entity_def(b'PCURVE') == 1

Tier-3 assertions:
  - face[0].surface_type == "plane"

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)

IMPORTANT live finding (honest, not overclaimed): a direct BRep_Tool::
CurveOnSurface probe on the resulting edge against the PLANE does NOT come
back empty as "pcurve dropped" would predict -- it returns a live
Geom2d_Line. But evaluating that returned curve at parameter 1.0 gives
(1.0, 0.0), NOT (0.0, 0.0) as our deliberately-collapsed zero-vector
construction declared -- i.e. OCCT did not keep our contradictory pcurve
AND did not literally drop it either; it silently REGENERATED a fresh,
CORRECT, non-degenerate 2D representation (matching the true 3D edge
length) that supersedes the collapsed one we supplied. This is a related
but distinct repair strategy from the catalog's literal
"RemoveSinglePCurve" (drop) claim -- the byte-level input pattern (a
genuinely non-degenerate 3D edge paired with a literal w1==w2 pcurve) is
faithfully reproduced and reachable (occt=shape(1), brepcheck.valid), and
OCCT visibly does NOT propagate the contradiction through to the final
BRep, but the specific repair outcome observed here is "regenerate", not
"drop" -- recorded honestly rather than claimed as an exact match to the
cited RemoveSinglePCurve code path.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp191",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with one EDGE_CURVE "
        "'collapsed_pcurve_edge': v_start(0,0,0) -> v_end(1,0,0), 3D curve "
        "is a real 1-unit LINE 'edge_positive_length_3d', wrapped in a "
        "SURFACE_CURVE whose SOLE PCURVE has a zero-magnitude 2D UV VECTOR "
        "-- the pcurve's own trim domain collapses to a single point "
        "(w1==w2) regardless of the real 3D traversal; CheckPCurves' "
        "w1==w2 -> RemoveSinglePCurve branch IS the mechanism; EDGE_LOOP "
        "IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never "
        "orphaned"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

# ── Real, positive-length 3D LINE ────────────────────────────────────────────
dir3d = f.direction((1.0, 0.0, 0.0))
vec3d = f.vector(dir3d, 1.0)
line3d = f._emit_raw(
    f"LINE('edge_positive_length_3d',#{f.cartesian_point((0.0, 0.0, 0.0)).eid},#{vec3d.eid})"
)

# ── Collapsed pcurve: zero-magnitude 2D vector, w1==w2 literally ────────────
uv_orig = f.cartesian_point((0.0, 0.0))
uv_dir  = f.direction((1.0, 0.0))
uv_vec  = f.vector(uv_dir, 0.0)
uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
drep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")

surf_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('collapsed_pcurve_edge',#{v_start.eid},#{v_end.eid},#{surf_curve.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
