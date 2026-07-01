"""Tsh232 — Fusion 360 fillet-junction three-valent ORIENTED_EDGE in CLOSED_SHELL.

Catalog claim: STEP file with a CLOSED_SHELL containing two adjacent cylindrical
fillet ADVANCED_FACEs (F2, F3) and one planar base face (F1), where the shared
edge E between the two fillets is referenced by three ORIENTED_EDGE records —
one per incident face — making the edge topologically three-valent.  The STEP
schema (ISO 10303-42 §4.5) requires exactly two ADVANCED_FACEs per EDGE_CURVE
in a CLOSED_SHELL; a three-valent edge is a non-manifold topology defect.

Source: Fusion 360 community — fillet-fillet junction STEP export (B4 wave-6 DEF-T).

Mechanism: shared EDGE_CURVE E IS referenced by three ORIENTED_EDGE entities,
one per face loop of F1 (plane), F2 (cylinder), and F3 (cylinder). The CLOSED_SHELL
IS the model entity.

Topology:
  F1 (plane): planar left half, loop 00→10→11→01→00, uses e_shared(10→11) forward
  F2 (cylinder): left cyl fillet, loop 10→11→01→00→10, uses e_shared(10→11) forward
  F3 (cylinder): right cyl patch,  loop 10→20→21→11→10, uses e_shared(11→10) reversed
  The same EDGE_CURVE (10→11) appears in F1, F2, F3 — three-valent.

Byte assertions:
  contains(b'CLOSED_SHELL')
  contains(b'CYLINDRICAL_SURFACE')
  count_entity_def(b'ADVANCED_FACE') == 3
  count_entity_def(b'ORIENTED_EDGE') >= 3

Tier-3 assertion: n_faces_total == 3
Expected: occt=shape(1)/shape(1) — non-manifold accepted with 3 faces
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh232",
    defect=(
        "CLOSED_SHELL IS model entity; shared EDGE_CURVE E IS referenced by three "
        "ORIENTED_EDGE records (F1-planar, F2-cylinder, F3-cylinder) — three-valent "
        "non-manifold topology; Fusion 360 fillet-fillet junction STEP export (DEF-T); "
        "OCCT may load with non-manifold shape or silently accept"
    ),
)

# ── Points and vertices ────────────────────────────────────────────────────────
# Layout: two halves side-by-side in X, 1 unit wide each, 1 unit deep in Y
# p00=(0,0,0) p10=(1,0,0) p20=(2,0,0)
# p01=(0,1,0) p11=(1,1,0) p21=(2,1,0)
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p21 = f.cartesian_point((2.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01)
v11 = f.vertex_point(p11)
v21 = f.vertex_point(p21)

def line_edge(va, vb, pstart, dx, dy, dz, length=1.0):
    d   = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, float(length))
    ln  = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# ── Shared edge E: 10→11 (the three-valent edge) ──────────────────────────────
e_shared = line_edge(v10, v11, p10, 0, 1, 0, 1.0)

# ── F1: planar left half, loop 00→10→11→01→00 ─────────────────────────────────
e_f1_bot = line_edge(v00, v10, p00,  1, 0, 0, 1.0)   # 00→10
e_f1_top = line_edge(v11, v01, p11, -1, 0, 0, 1.0)   # 11→01
e_f1_lft = line_edge(v01, v00, p01,  0,-1, 0, 1.0)   # 01→00
lp_f1 = f.edge_loop([
    f.oriented_edge(e_f1_bot, True),   # 00→10
    f.oriented_edge(e_shared, True),   # 10→11 ← first use of E
    f.oriented_edge(e_f1_top, True),   # 11→01
    f.oriented_edge(e_f1_lft, True),   # 01→00
])
ax_f1   = f.axis2_placement_3d(p00, f.direction((0, 0, -1)), f.direction((1, 0, 0)))
face_f1 = f.advanced_face([f.face_outer_bound(lp_f1)], f.plane(ax_f1))

# ── Cylindrical surface for F2 (axis along Y at x=0.5) ───────────────────────
# Large radius so the fillet is nearly planar (geometrically coherent cylinder)
cyl2_orig = f.cartesian_point((0.5, 0.0, 0.0))
cyl2_axis = f.direction((0.0, 1.0, 0.0))
cyl2_xdir = f.direction((1.0, 0.0, 0.0))
cyl2_plc  = f.axis2_placement_3d(cyl2_orig, cyl2_axis, cyl2_xdir)
cyl2_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('tsh232_cyl2',#{cyl2_plc.eid},100.0)")

# F2 loop: 10→11 (E) → 11→01 → 01→00 → 00→10  (same edges as F1!)
# Second use of e_shared and e_f1_{top,lft,bot}
lp_f2 = f.edge_loop([
    f.oriented_edge(e_shared,  True),  # 10→11 ← SECOND use of E
    f.oriented_edge(e_f1_top,  True),  # 11→01
    f.oriented_edge(e_f1_lft,  True),  # 01→00
    f.oriented_edge(e_f1_bot,  False), # 10←00 (00→10 reversed = 10→00)
])
face_f2 = f.advanced_face([f.face_outer_bound(lp_f2)], cyl2_surf)

# ── Cylindrical surface for F3 (axis along Y at x=1.5) ───────────────────────
cyl3_orig = f.cartesian_point((1.5, 0.0, 0.0))
cyl3_axis = f.direction((0.0, 1.0, 0.0))
cyl3_xdir = f.direction((1.0, 0.0, 0.0))
cyl3_plc  = f.axis2_placement_3d(cyl3_orig, cyl3_axis, cyl3_xdir)
cyl3_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('tsh232_cyl3',#{cyl3_plc.eid},100.0)")

# F3: right cyl patch, loop 10→20→21→11→10 with e_shared reversed (11→10)
e_f3_bot = line_edge(v10, v20, p10,  1, 0, 0, 1.0)  # 10→20
e_f3_rgt = line_edge(v20, v21, p20,  0, 1, 0, 1.0)  # 20→21
e_f3_top = line_edge(v21, v11, p21, -1, 0, 0, 1.0)  # 21→11
lp_f3 = f.edge_loop([
    f.oriented_edge(e_f3_bot, True),   # 10→20
    f.oriented_edge(e_f3_rgt, True),   # 20→21
    f.oriented_edge(e_f3_top, True),   # 21→11
    f.oriented_edge(e_shared, False),  # 11→10 (E reversed) ← THIRD use of E
])
face_f3 = f.advanced_face([f.face_outer_bound(lp_f3)], cyl3_surf)

# ── CLOSED_SHELL containing 3 faces (topologically non-manifold via e_shared) ─
faces = [face_f1, face_f2, face_f3]
face_refs = ",".join(f"#{fa.eid}" for fa in faces)
shell = f._emit_raw(f"CLOSED_SHELL('tsh232_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('tsh232_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
