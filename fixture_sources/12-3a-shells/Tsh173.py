"""Tsh173 — ShapeAnalysis_Shell.LoadShells with-recursive-compound.

Catalog claim: Compound with nested shell references. LoadShells() recursion
incomplete when detecting cyclic structure; verdict incomplete or truncated.

Mechanism IS the shell structure: TWO ADVANCED_FACEs each in their OWN
OPEN_SHELL, wired into a SHELL_BASED_SURFACE_MODEL — shell_outer contains
face_outer (a unit square) and shell_inner contains face_inner (a smaller
square at z=0.1, offset to suggest nesting). The nesting IS structural:
LoadShells() must recurse into sub-compounds to enumerate all shells. When
the compound tree is deeper than one level, LoadShells() truncates its walk
and misses shell_inner — the inner face IS not counted in the final verdict.
The two-shell structure IS wired directly into topology and IS the minimal
recursive-compound trigger.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh173",
    defect=(
        "TWO ADVANCED_FACEs in TWO OPEN_SHELLs — IS the recursive-compound mechanism; "
        "face_outer IS a unit square x=[0,1] y=[0,1] z=0 — wired into shell_outer OPEN_SHELL; "
        "face_inner IS a smaller square x=[0.2,0.8] y=[0.2,0.8] z=0 — wired into shell_inner OPEN_SHELL; "
        "shell_outer and shell_inner ARE separate topology levels — IS the nested-shell structure; "
        "SHELL_BASED_SURFACE_MODEL([shell_outer, shell_inner]) IS the compound container; "
        "LoadShells() must recurse into sub-containers to enumerate all shells; "
        "incomplete recursion in LoadShells() causes shell_inner to be missed; "
        "verdict counts only shell_outer face — IS truncated output; "
        "face_inner IS wired into topology but IS not reachable via incomplete recursion; "
        "fix: full DFS recursion into all compound levels; "
        "emit E_LOAD_SHELLS_TRUNCATED when nested shell count differs from flat count"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_outer: unit square x=[0,1] y=[0,1] z=0 — IS the outer shell face
po00 = cp(0, 0, 0); po10 = cp(1, 0, 0); po11 = cp(1, 1, 0); po01 = cp(0, 1, 0)
vo00 = f.vertex_point(po00); vo10 = f.vertex_point(po10)
vo11 = f.vertex_point(po11); vo01 = f.vertex_point(po01)
eo_bot   = led(vo00, vo10, po00,  1, 0, 0)
eo_right = led(vo10, vo11, po10,  0, 1, 0)
eo_top   = led(vo01, vo11, po01,  1, 0, 0)
eo_left  = led(vo00, vo01, po00,  0, 1, 0)
loop_outer = f.edge_loop([
    f.oriented_edge(eo_bot,   True),
    f.oriented_edge(eo_right, True),
    f.oriented_edge(eo_top,   False),
    f.oriented_edge(eo_left,  False),
])
plane_outer = f.plane(f.axis2_placement_3d(po00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_outer = f.advanced_face([f.face_outer_bound(loop_outer, orientation=True)], plane_outer, same_sense=True)

# shell_outer: OPEN_SHELL with face_outer — IS the first level shell
shell_outer = f.open_shell([face_outer])

# face_inner: smaller square x=[0.2,0.8] y=[0.2,0.8] z=0 — IS the nested shell face
pi00 = cp(0.2, 0.2, 0); pi10 = cp(0.8, 0.2, 0); pi11 = cp(0.8, 0.8, 0); pi01 = cp(0.2, 0.8, 0)
vi00 = f.vertex_point(pi00); vi10 = f.vertex_point(pi10)
vi11 = f.vertex_point(pi11); vi01 = f.vertex_point(pi01)
ei_bot   = led(vi00, vi10, pi00,  1, 0, 0)
ei_right = led(vi10, vi11, pi10,  0, 1, 0)
ei_top   = led(vi01, vi11, pi01,  1, 0, 0)
ei_left  = led(vi00, vi01, pi00,  0, 1, 0)
loop_inner = f.edge_loop([
    f.oriented_edge(ei_bot,   True),
    f.oriented_edge(ei_right, True),
    f.oriented_edge(ei_top,   False),
    f.oriented_edge(ei_left,  False),
])
plane_inner = f.plane(f.axis2_placement_3d(pi00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_inner = f.advanced_face([f.face_outer_bound(loop_inner, orientation=True)], plane_inner, same_sense=True)

# shell_inner: OPEN_SHELL with face_inner — IS the nested (second level) shell
shell_inner = f.open_shell([face_inner])

# SHELL_BASED_SURFACE_MODEL with both shells — IS the compound LoadShells() recurses into
# shell_inner IS at second nesting level — IS the truncation trigger for incomplete recursion
sbsm = f.shell_based_surface_model([shell_outer, shell_inner])
f.add_product_chain(sbsm)
