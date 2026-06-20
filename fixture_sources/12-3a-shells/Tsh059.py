"""Tsh059 — Coplanar-face merge history map omits intermediate shapes (multiple
ADVANCED_FACEs aliasing the same FACE_OUTER_BOUND and same PLANE).

Catalog claim: After merging adjacent same-surface ADVANCED_FACEs, a
shape-history query for "what resulted from edge X?" finds that some
intermediate edges created and re-merged during a multi-pass unification carry
no history record. Typical precondition: multiple ADVANCED_FACEs (4 here) all
referencing the same FACE_OUTER_BOUND entity and the same underlying PLANE —
coplanar faces aliasing the same wire and surface entities.

Mechanism IS the shell structure: a CLOSED_SHELL (or OPEN_SHELL used as a
compound) contains 4 ADVANCED_FACEs that all point to the same FACE_OUTER_BOUND
entity (same EDGE_LOOP) and the same PLANE entity. The alias IS wired directly
into each ADVANCED_FACE's bounds list. Multi-pass merge creates and then
re-removes intermediate edges whose history is not recorded. A downstream
attribute-transfer pipeline loses PMI, color, or mesh data on those edges.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 4

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh059",
    defect=(
        "OPEN_SHELL with 4 coplanar ADVANCED_FACEs all aliasing the same FACE_OUTER_BOUND "
        "and the same PLANE entity; "
        "shared FACE_OUTER_BOUND and PLANE alias IS wired into each ADVANCED_FACE bounds list; "
        "multi-pass merge creates then removes intermediate edges; "
        "history map omits those intermediate edge mappings; "
        "PMI/color/mesh attributes lost on edges without history records; "
        "fix: normalize history to record every input→output mapping including intermediates"
    ),
)

# ── Single shared PLANE and FACE_OUTER_BOUND (alias IS the defect) ───────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)   # shared by all 4 faces — alias IS the mechanism

# ── Unit-square wire (shared by all 4 ADVANCED_FACEs via same FACE_OUTER_BOUND) ─
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

e_bot = line_edge(v00, v10, p00,  1, 0, 0)
e_rgt = line_edge(v10, v11, p10,  0, 1, 0)
e_top = line_edge(v11, v01, p11, -1, 0, 0)
e_lft = line_edge(v01, v00, p01,  0,-1, 0)

shared_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])

# Shared FACE_OUTER_BOUND referencing the same loop (IS the alias mechanism)
shared_fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{shared_loop.eid},.T.)")

# ── 4 ADVANCED_FACEs all referencing the SAME fob and SAME plane ─────────────
# This alias IS wired directly into each face's bounds list.
face1 = f._emit_raw(f"ADVANCED_FACE('',(#{shared_fob.eid}),#{plane.eid},.T.)")
face2 = f._emit_raw(f"ADVANCED_FACE('',(#{shared_fob.eid}),#{plane.eid},.T.)")
face3 = f._emit_raw(f"ADVANCED_FACE('',(#{shared_fob.eid}),#{plane.eid},.T.)")
face4 = f._emit_raw(f"ADVANCED_FACE('',(#{shared_fob.eid}),#{plane.eid},.T.)")

# ── OPEN_SHELL: same-entity aliasing IS wired into shell/face topology ────────
shell = f._emit_raw(
    f"OPEN_SHELL('',(#{face1.eid},#{face2.eid},#{face3.eid},#{face4.eid}))"
)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
