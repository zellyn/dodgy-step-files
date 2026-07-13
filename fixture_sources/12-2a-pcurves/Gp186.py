"""Gp186 — Two pcurve-bearing edges actually merged by sewing, one
contributor reversed-orientation and independently (differently) speed-
parametrized, exercising Reverse()+ReversedParameter before the
SameRange rescale (sew-pcurve-domain-reconciliation, PARTIAL -- prior
witnesses Gp050/Gp052 are single-edge ShapeFix_Edge probes, not an
actual two-edge sewing merge).

Work packet D2, item `sew-pcurve-domain-reconciliation` (PARTIAL),
problem_id `sew-pcurve-domain-reconciliation`:
"Two edges being merged each carry their own 2D pcurve(s), independently
parametrized to their own original 3D edge's parameter range. Once
merged into one edge with one shared 3D parameter range, every
contributing pcurve must be rescaled (and, for reversed-orientation
contributors, reversed) onto that new shared domain."
(BRepBuilderAPI_Sewing::SameParameterEdge, BRepBuilderAPI_Sewing.cxx:
757-784 -- Reverse()+ReversedParameter for the non-reference edge when
orientation is reversed, then SameRange rescale onto [first,last];
:785 -- if rescaling fails, that face's contribution is skipped.)

Mechanism: Two coplanar unit-scale PLANE rectangles that are NOT
topologically stitched -- each is its own independent 4-edge
ADVANCED_FACE with its own VERTEX_POINT/EDGE_CURVE/PCURVE entities --
but share one geometrically coincident boundary:

  Face A (upper): A=(0,0,0) -> B=(1,0,0) -> C=(1,1,0) -> D=(0,1,0).
  The bottom edge A->B carries a 3D LINE of magnitude 1 (parameter
  domain [0,1]) and a matching-speed PCURVE (domain [0,1]).

  Face B (lower, mirrored below): B'=(1,0,0) -> A'=(0,0,0) -> E=(0,-1,0)
  -> G=(1,-1,0). B' and A' are DISTINCT VERTEX_POINT entities from A and
  B, at the same coordinates -- genuinely unstitched. The top edge
  B'->A' is geometrically the SAME physical segment as Face A's A->B,
  but traversed in the OPPOSITE 3D direction (reversed-orientation
  contributor) AND parametrized 4x slower (vector magnitude 0.25,
  parameter domain [0,4] instead of [0,1]) -- a genuine cross-edge
  domain mismatch that only a real sewing merge (not a single-edge
  ShapeFix_Edge probe) is positioned to reconcile.

Verified live (see fixture report): a standalone BRepBuilderAPI_Sewing
pass (tolerance 1e-2) over the STEPControl_Reader-translated 2-face
shape actually merges the two boundary edges into one shared edge,
demonstrating the input genuinely demands the Reverse()+ReversedParameter
+SameRange-rescale codepath this class targets.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp186",
    defect=(
        "Two independent, unstitched coplanar PLANE rectangles (Face A upper, "
        "Face B lower) sharing a geometrically coincident but topologically "
        "distinct boundary segment: Face A's bottom edge A->B (3D LINE magnitude "
        "1, domain [0,1], matching-speed pcurve) vs Face B's top edge B'->A' "
        "(SAME physical segment, opposite 3D direction, vector magnitude 0.25, "
        "domain [0,4], matching-speed own pcurve) -- reversed-orientation AND "
        "4x-domain-mismatched contributor requiring BRepBuilderAPI_Sewing's "
        "Reverse()+ReversedParameter+SameRange rescale to merge into one edge"
    ),
)

# Shared coplanar PLANE, z=0, standard axis (UV == XY).
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane = f.plane(p_axis)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def _edge(name, p1, p2, v1, v2, dir3d, mag, pc_origin, pc_dir, pc_mag):
    """Build one EDGE_CURVE with a matching-speed PCURVE on `plane`."""
    line3d = f.line(p1, f.vector(f.direction(dir3d), mag))
    pc_start = f.cartesian_point(pc_origin)
    pc_vec = f.vector(f.direction(pc_dir), pc_mag)
    pc_line = f.line(pc_start, pc_vec)
    pc_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('{name}_def',(#{pc_line.eid}),#{prc.eid})"
    )
    pcurve = f._emit_raw(f"PCURVE('{name}_pc',#{plane.eid},#{pc_def.eid})")
    sc = f._emit_raw(
        f"SURFACE_CURVE('{name}_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
    )
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v1.eid},#{v2.eid},#{sc.eid},.T.)")


# ---------------------------------------------------------------------
# Face A (upper rectangle): A=(0,0,0) B=(1,0,0) C=(1,1,0) D=(0,1,0)
# ---------------------------------------------------------------------
pA_a = f.cartesian_point((0.0, 0.0, 0.0))
pA_b = f.cartesian_point((1.0, 0.0, 0.0))
pA_c = f.cartesian_point((1.0, 1.0, 0.0))
pA_d = f.cartesian_point((0.0, 1.0, 0.0))
vA_a = f.vertex_point(pA_a)
vA_b = f.vertex_point(pA_b)
vA_c = f.vertex_point(pA_c)
vA_d = f.vertex_point(pA_d)

# Bottom edge A->B: domain [0,1], matching-speed pcurve. This is the
# shared-boundary reference edge (natural orientation, natural speed).
eA_bottom = _edge("faceA_bottom", pA_a, pA_b, vA_a, vA_b,
                   (1.0, 0.0, 0.0), 1.0, (0.0, 0.0), (1.0, 0.0), 1.0)
eA_right = _edge("faceA_right", pA_b, pA_c, vA_b, vA_c,
                  (0.0, 1.0, 0.0), 1.0, (1.0, 0.0), (0.0, 1.0), 1.0)
eA_top = _edge("faceA_top", pA_d, pA_c, vA_d, vA_c,
               (1.0, 0.0, 0.0), 1.0, (0.0, 1.0), (1.0, 0.0), 1.0)
eA_left = _edge("faceA_left", pA_d, pA_a, vA_d, vA_a,
                (0.0, -1.0, 0.0), 1.0, (0.0, 1.0), (0.0, -1.0), 1.0)

loopA = f.edge_loop([
    f.oriented_edge(eA_bottom, True),   # A->B
    f.oriented_edge(eA_right, True),    # B->C
    f.oriented_edge(eA_top, False),     # C->D (reversed)
    f.oriented_edge(eA_left, True),     # D->A
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)

# ---------------------------------------------------------------------
# Face B (lower rectangle, mirrored below A): B'=(1,0,0) A'=(0,0,0)
# E=(0,-1,0) G=(1,-1,0). B' and A' are DISTINCT entities from A's B/A --
# genuinely unstitched.
# ---------------------------------------------------------------------
pB_bp = f.cartesian_point((1.0, 0.0, 0.0))
pB_ap = f.cartesian_point((0.0, 0.0, 0.0))
pB_e = f.cartesian_point((0.0, -1.0, 0.0))
pB_g = f.cartesian_point((1.0, -1.0, 0.0))
vB_bp = f.vertex_point(pB_bp)
vB_ap = f.vertex_point(pB_ap)
vB_e = f.vertex_point(pB_e)
vB_g = f.vertex_point(pB_g)

# THE DEFECT edge: top edge B'->A' -- geometrically the SAME segment as
# Face A's A->B but traversed in the OPPOSITE 3D direction (reversed
# contributor), 4x SLOWER (magnitude 0.25, domain [0,4] instead of
# [0,1]) -- a genuine cross-edge parameter-domain mismatch.
eB_top = _edge("faceB_top", pB_bp, pB_ap, vB_bp, vB_ap,
               (-1.0, 0.0, 0.0), 0.25, (1.0, 0.0), (-1.0, 0.0), 0.25)
eB_left = _edge("faceB_left", pB_ap, pB_e, vB_ap, vB_e,
                 (0.0, -1.0, 0.0), 1.0, (0.0, 0.0), (0.0, -1.0), 1.0)
eB_bottom = _edge("faceB_bottom", pB_e, pB_g, vB_e, vB_g,
                   (1.0, 0.0, 0.0), 1.0, (0.0, -1.0), (1.0, 0.0), 1.0)
eB_right = _edge("faceB_right", pB_g, pB_bp, vB_g, vB_bp,
                  (0.0, 1.0, 0.0), 1.0, (1.0, -1.0), (0.0, 1.0), 1.0)

loopB = f.edge_loop([
    f.oriented_edge(eB_top, True),      # B'->A' (reversed vs Face A, 4x slower)
    f.oriented_edge(eB_left, True),     # A'->E
    f.oriented_edge(eB_bottom, True),   # E->G
    f.oriented_edge(eB_right, True),    # G->B'
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)

shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
