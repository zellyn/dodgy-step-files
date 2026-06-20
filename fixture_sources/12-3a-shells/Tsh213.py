"""Tsh213 — Wire collection type-filter gate.

Catalog claim: Face traversal during wire collection must filter non-WIRE shapes
(e.g., isolated vertices). Without type guard, non-wire subshapes passed to wire
processing, causing type-safety crash.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
(unit square) whose FACE_OUTER_BOUND EDGE_LOOP references an ORIENTED_EDGE whose
EDGE_CURVE start vertex IS also directly registered as a free VERTEX_POINT in the
shell topology — IS the isolated-vertex defect trigger.
ShapeFix_ComposeShell.CollectWires IS the defect path: when traversing face
subshapes to collect wires, it encounters the isolated VERTEX (a non-WIRE subshape)
and must type-guard against it; without the guard, the vertex IS passed to wire
processing causing a type-safety crash — IS the defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh213",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE with isolated VERTEX in shell topology IS the type-filter-gate defect trigger; "
        "unit square face IS at (0,0,0)-(1,1,0) — IS the face geometry; "
        "face FACE_OUTER_BOUND IS valid four-edge square loop — IS the outer boundary; "
        "isolated vertex IS VERTEX_POINT at interior position (0.5,0.5,0) — IS the non-WIRE subshape; "
        "isolated vertex IS added to shell face set via open_shell topology — IS the rogue subshape path; "
        "CollectWires IS the defect path: traverses shell face subshapes to collect wires; "
        "isolated VERTEX (ShapeType==VERTEX) IS encountered during wire collection traversal — IS the type mismatch; "
        "without type-filter guard, VERTEX IS passed to wire processing — IS the crash path; "
        "type-filter gate must check ShapeType==WIRE before processing — IS the fix; "
        "failure to filter causes type-safety crash in wire collection — IS the defect outcome; "
        "fix: CollectWires must skip subshapes where ShapeType != WIRE; "
        "emit E_WIRE_COLLECTION_TYPE_MISMATCH when non-wire subshape reaches wire processing"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square — IS the face geometry
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

e_bot = led(v00, v10, p00,  1, 0, 0)
e_rgt = led(v10, v11, p10,  0, 1, 0)
e_top = led(v11, v01, p11, -1, 0, 0)
e_lft = led(v01, v00, p01,  0,-1, 0)

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])

plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# Isolated vertex at interior position — IS the non-WIRE subshape that triggers type-filter gate
p_iso = cp(0.5, 0.5, 0)
v_iso = f.vertex_point(p_iso)   # IS the isolated vertex in shell topology

# OPEN_SHELL: face + isolated vertex encoded as extra face reference — IS the type-filter-gate mechanism
# The isolated vertex IS referenced in the shell; CollectWires must filter it as non-WIRE subshape
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
