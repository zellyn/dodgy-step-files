"""Twi289 — Edge with NEITHER a 3D curve NOR a usable pcurve (zero-length
pcurve range, from start==end vertex) inside an otherwise-healthy wire: the
REMOVAL path, not the reconstruct-from-pcurve path Twi047 covers.

Catalog claim: ShapeFix_Wire::FixEdgeCurves has two outcomes for an edge
missing its 3D curve: (1) if the edge's pcurve is usable, reconstruct the 3D
curve by lifting the pcurve through the host surface (ShapeFix_Edge::
FixAddCurve3d — Twi047's mechanism); (2) if the edge has NEITHER a 3D curve
NOR a usable pcurve (its own parametric range collapses to zero length), the
edge cannot be salvaged at all and is REMOVED from the wire
(ShapeFix_Wire.cxx:744-759); the wire is then re-closed / re-connected around
the resulting gap.

This fixture is deliberately the REMOVAL path: a pentagon wire (5 healthy
edges, ordinary 3D LINE geometry) with ONE extra degenerate edge spliced in
at corner 2 — start vertex == end vertex (both #v2, the same VERTEX_POINT
entity), and its curve is a SURFACE_CURVE wrapping only a PCURVE (Twi047's
pattern: no 3D curve at all). Because the edge's own start and end vertex are
identical, its trimmed parametric range collapses to zero length in BOTH the
(absent) 3D sense and the pcurve sense — there is no 3D curve to fall back on
and no non-degenerate pcurve range to lift through the surface either. The
healer's only option is to drop the degenerate edge entirely and treat corner
2 as an ordinary single vertex where the pentagon's two healthy neighbor
edges already meet.

Mechanism IS the sixth EDGE_CURVE spliced between the pentagon's healthy
edge 1 and edge 2: start vertex #v2 == end vertex #v2 (same entity, matching
Twi018's zero-arc-length pattern), curve is a SURFACE_CURVE whose
associated_geometry lists only a PCURVE (matching Twi047's no-3D-curve
pattern) — the combination yields an edge with neither a 3D curve nor a
usable (non-zero-range) pcurve. All six edges ARE wired into one EDGE_LOOP ->
FACE_OUTER_BOUND -> ADVANCED_FACE in an OPEN_SHELL; never orphaned.

Byte assertions:
  - count_entity_def(b'EDGE_CURVE') == 6
  - count_entity_def(b'SURFACE_CURVE') == 1

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 5

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi289",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (regular pentagon, "
        "radius 5); FACE_OUTER_BOUND references an EDGE_LOOP of six edges — "
        "five ordinary healthy LINE-based EDGE_CURVEs forming the pentagon, "
        "plus one degenerate EDGE_CURVE spliced in at corner 2: start vertex "
        "#v2 == end vertex #v2 (same VERTEX_POINT entity), curve is a "
        "SURFACE_CURVE whose associated_geometry lists only a PCURVE — no 3D "
        "curve; the combination of same-vertex (zero 3D extent) and "
        "pcurve-only (no 3D curve) means neither a 3D curve nor a usable "
        "pcurve range IS available for this edge — this IS the mechanism; "
        "ShapeFix_Wire::FixEdgeCurves' incomplete-edge removal path must drop "
        "the degenerate edge and re-close/re-connect the wire (corner 2's two "
        "healthy neighbor edges already meet there), or reject the wire; "
        "the defective EDGE_CURVE IS wired into EDGE_LOOP, FACE_OUTER_BOUND, "
        "ADVANCED_FACE, OPEN_SHELL — never orphaned"
    ),
)

# Host plane: z=0, normal +Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# Regular pentagon corners (radius 5), UV == XY (identity plane frame).
N = 5
R = 5.0
pent_pts = [(R * math.cos(2 * math.pi * i / N + math.pi / 2),
             R * math.sin(2 * math.pi * i / N + math.pi / 2)) for i in range(N)]
pent_v = [f.vertex_point(f.cartesian_point((px, py, 0.0))) for px, py in pent_pts]

# 2D parametric context for the degenerate edge's pcurve
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('','2D'))"
)

def mk_healthy_edge(i):
    pa, pb = pent_pts[i], pent_pts[(i + 1) % N]
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln  = f.line(f.cartesian_point((pa[0], pa[1], 0.0)), vec)
    return f.edge_curve(pent_v[i], pent_v[(i + 1) % N], ln)

def mk_degenerate_no_curve_no_pcurve_edge(vi):
    """EDGE_CURVE with start==end vertex (zero 3D extent, Twi018's pattern)
    whose curve is a SURFACE_CURVE wrapping only a PCURVE (no 3D curve,
    Twi047's pattern) — neither representation is usable. IS the mechanism."""
    px, py = pent_pts[vi]
    uv_start_pt = f.cartesian_point((px, py))
    uv_dir = f.direction((1.0, 0.0))
    uv_vec = f.vector(uv_dir, 1.0)
    line2d = f.line(uv_start_pt, uv_vec)
    defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{line2d.eid}),#{prc.eid})")
    pcurve = f._emit_raw(f"PCURVE('',#{surf.eid},#{defrep.eid})")
    surface_curve = f._emit_raw(
        f"SURFACE_CURVE('',#{pcurve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
    )
    edge = f._emit_raw(
        f"EDGE_CURVE('',#{pent_v[vi].eid},#{pent_v[vi].eid},"
        f"#{surface_curve.eid},.T.)"
    )
    return edge

# Healthy edges 0 and 1 (corners 0->1, 1->2)
e0 = mk_healthy_edge(0)
e1 = mk_healthy_edge(1)
# Degenerate edge spliced in AT corner 2 (start==end==#v2, no 3D curve, no
# usable pcurve) — IS the mechanism.
e_bad = mk_degenerate_no_curve_no_pcurve_edge(2)
# Remaining healthy edges 2, 3, 4 (corners 2->3, 3->4, 4->0)
e2 = mk_healthy_edge(2)
e3 = mk_healthy_edge(3)
e4 = mk_healthy_edge(4)

oedges = [
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e_bad, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True),
]
loop = f.edge_loop(oedges)
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
