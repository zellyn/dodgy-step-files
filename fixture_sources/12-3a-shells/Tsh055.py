"""Tsh055 — Merging adjacent same-surface faces with opposite normals returns
inverted face.

Catalog claim: Two faces that should be merged have surface normals pointing in
opposite directions (one face is reversed relative to its partner). Same-surface
detection compares unsigned surface descriptors and decides to merge; but the
merge produces an inverted-orientation face that breaks shell normals.

Mechanism IS the shell structure: an OPEN_SHELL contains two coplanar
ADVANCED_FACEs on the same PLANE (z=0) but with OPPOSITE sense flags. Face A
uses sense=.T. (normal +Z), Face B uses sense=.F. (normal −Z). They share one
EDGE_CURVE at x=1, y=0→1 with opposite ORIENTED_EDGE senses. The opposite
sense flag IS wired directly into each ADVANCED_FACE entity. A unifier that
compares unsigned surface geometry will see both faces as same-domain and merge
them, producing an inverted result.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh055",
    defect=(
        "OPEN_SHELL with 2 coplanar ADVANCED_FACEs on the same PLANE (z=0); "
        "Face A uses sense=.T. (normal +Z), Face B uses sense=.F. (normal -Z); "
        "both share one EDGE_CURVE at x=1 with opposite ORIENTED_EDGE orientations; "
        "opposite sense flag IS wired into each ADVANCED_FACE topology; "
        "unsigned same-surface check incorrectly merges opposite-normal faces; "
        "merge must compare oriented surfaces (direction included)"
    ),
)

# ── Shared plane ──────────────────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Points and vertices ───────────────────────────────────────────────────────
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p21 = f.cartesian_point((2.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
v20 = f.vertex_point(p20)
v21 = f.vertex_point(p21)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Shared boundary edge at x=1, y=0→1
shared_edge = line_edge(v10, v11, p10, 0, 1, 0)

# Face A edges (unit square 0,0 → 1,1)
eA_bot = line_edge(v00, v10, p00,  1, 0, 0)
eA_top = line_edge(v11, v01, p11, -1, 0, 0)
eA_lft = line_edge(v01, v00, p01,  0,-1, 0)

loopA = f.edge_loop([
    f.oriented_edge(eA_bot,     True),
    f.oriented_edge(shared_edge, True),   # (1,0)→(1,1) forward
    f.oriented_edge(eA_top,     True),
    f.oriented_edge(eA_lft,     True),
])
# Face A: sense=.T. → normal +Z  (standard outward sense)
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane, same_sense=True)

# Face B edges (unit square 1,0 → 2,1)
eB_bot = line_edge(v10, v20, p10,  1, 0, 0)
eB_rgt = line_edge(v20, v21, p20,  0, 1, 0)
eB_top = line_edge(v21, v11, p21, -1, 0, 0)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot,     True),
    f.oriented_edge(eB_rgt,     True),
    f.oriented_edge(eB_top,     True),
    f.oriented_edge(shared_edge, False),  # (1,1)→(1,0) reversed
])
# Face B: sense=.F. → normal −Z  (opposite sense IS the mechanism)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane, same_sense=False)

# ── OPEN_SHELL: opposite sense flags ARE wired into shell/face topology ────────
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
