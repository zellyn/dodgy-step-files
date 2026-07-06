"""Me1184 — out-of-plane spike (outlier/noise) vertex: one interior vertex of a
  flat patch displaced far off the local surface, producing a fan of extreme-
  aspect-ratio needle triangles with NO self-intersection.

Input pattern (defect class: spike_vertex):
  A flat hexagonal patch is fanned from its centre vertex. The centre vertex,
  which should sit in the z=0 plane with its six rim neighbours, is instead
  displaced to z=50 — a single gross outlier ("spike" / "noise vertex"), the
  kind produced by a bad scan sample or a units/typo error on one coordinate.
  The six fan triangles each become a tall thin needle (longest edge ~50, base
  ~1) with aspect ratio ~50, versus ~1.7 for the clean flat fan. Crucially the
  spike protrudes OUTWARD into empty space, so — unlike a displaced apex that
  dips through a facing patch (Me018 / Me1112, which self-INTERSECT) — none of
  the needle triangles cross each other. The defect is purely a geometric
  outlier: the mesh stays a valid manifold fan, but one vertex is nowhere near
  where the surface should be.

  A robust kernel must recognize the outlier (dihedral / aspect / distance-to-
  fitted-plane heuristic) and either smooth the spike vertex back toward the
  patch plane or flag it, rather than treating the needle sliver fan as signal.

Geometry:
  rim r0..r5 on a unit hexagon at z=0; apex at (0,0,50); six needle triangles
  (apex, r_i, r_{i+1}). Rim loop [r0..r5] is the open boundary of the fan.
"""
import math

from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1184",
    title="out-of-plane spike vertex: one interior vertex of a flat patch displaced far off-surface, fanning extreme-aspect needle triangles with no self-intersection (outlier vertex)",
    defect_class="spike_vertex",
)

H = 50.0   # apex displacement — the outlier
apex = m.vertex(0.0, 0.0, H)   # 0 — the spike vertex (should be at z=0)

rim = []
for k in range(6):
    ang = math.pi / 3.0 * k
    rim.append(m.vertex(math.cos(ang), math.sin(ang), 0.0))   # 1..6

# Six needle triangles fanning from the spike apex.
tris = []
for k in range(6):
    a = rim[k]
    b = rim[(k + 1) % 6]
    tris.append(m.triangle(apex, a, b))

# Each fan triangle is an extreme-aspect needle (spike). Clean flat fan ~1.7.
for ti in tris:
    m.assert_triangle_aspect_ratio_gt(ti, 30.0)

# The spike protrudes outward: adjacent and opposite needles do NOT cross —
# this is an outlier defect, not a self-intersection (contrast Me018/Me1112).
m.assert_triangles_do_not_intersect(tris[0], tris[3])   # opposite needles
m.assert_triangles_do_not_intersect(tris[0], tris[2])   # non-adjacent needles

# The rim is the open boundary loop of the fan (mesh stays a valid manifold fan).
m.assert_hole_boundary([rim[0], rim[1], rim[2], rim[3], rim[4], rim[5]])
