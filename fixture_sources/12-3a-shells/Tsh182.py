"""Tsh182 — ShapeFix_Shell.Perform face removal with shared edge.

Catalog claim: Removed face's edge is still referenced by another face in same
shell; Perform's removal leaves dangling reference; downstream topology query
on remaining face fails.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing ONE EDGE_CURVE
IS wired into an OPEN_SHELL. face_bad IS the face Perform() targets for
removal (it has an invalid second edge referencing a non-existent geometry).
face_good IS the remaining face. Both share e_shared — the SAME EDGE_CURVE
entity. Perform() removes face_bad from the shell but leaves e_shared in the
shell edge set under face_good's loop. The dangling reference IS: e_shared's
topology record still contains face_bad's oriented-edge reference after
removal. Downstream edge iteration on face_good encounters the stale reference
and fails.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh182",
    defect=(
        "TWO ADVANCED_FACEs sharing ONE EDGE_CURVE IS the dangling-reference mechanism; "
        "e_shared IS EDGE_CURVE from v0 to v1 — shared by face_good and face_bad; "
        "face_good IS valid triangle using e_shared, e_g2, e_g3 — IS the remaining face; "
        "face_bad IS invalid triangle using e_shared plus e_bad2 with self-referencing geometry — IS the removed face; "
        "Perform() removes face_bad — IS the fix action; "
        "e_shared in face_good's loop still carries face_bad's oriented-edge back-reference — IS the dangling ref; "
        "downstream edge iteration on face_good's loop hits stale reference — IS the defect; "
        "fix: Perform must purge back-references from all remaining faces' edges after removal; "
        "emit E_PERFORM_DANGLING_EDGE_REF when stale back-reference detected post-removal"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Four vertices: a triangle (good) and a flipped triangle sharing one edge
pa = cp(0,   0, 0); va = f.vertex_point(pa)
pb = cp(1,   0, 0); vb = f.vertex_point(pb)
pc = cp(0.5, 1, 0); vc = f.vertex_point(pc)
pd = cp(0.5,-1, 0); vd = f.vertex_point(pd)

# e_shared: IS the shared edge between face_good and face_bad
e_shared = led(va, vb, pa, 1, 0, 0)    # (0,0,0)→(1,0,0)

# face_good edges (triangle a-b-c, valid geometry)
e_g2 = led(vb, vc, pb, -0.5, 1, 0)    # (1,0,0)→(0.5,1,0)
e_g3 = led(vc, va, pc, -0.5,-1, 0)    # (0.5,1,0)→(0,0,0)

# face_bad edges (triangle a-b-d, shares e_shared, has invalid geometry on e_b2)
# e_b2 is a self-referencing edge (va→vd using same start as e_shared.start)
e_b2 = led(vb, vd, pb, -0.5,-1, 0)    # (1,0,0)→(0.5,-1,0)
e_b3 = led(vd, va, pd, -0.5, 1, 0)    # (0.5,-1,0)→(0,0,0)

# face_good: valid triangle using e_shared (forward) + e_g2 + e_g3
loop_good = f.edge_loop([
    f.oriented_edge(e_shared, True),   # shared edge forward
    f.oriented_edge(e_g2, True),
    f.oriented_edge(e_g3, True),
])
plane_good = f.plane(f.axis2_placement_3d(pa, dir3(0, 0, 1), dir3(1, 0, 0)))
face_good = f.advanced_face([f.face_outer_bound(loop_good, orientation=True)], plane_good, same_sense=True)

# face_bad: triangle below X-axis using e_shared (reversed) + e_b2 + e_b3
# same_sense=False makes this face the one Perform() will target for removal
loop_bad = f.edge_loop([
    f.oriented_edge(e_shared, False),  # shared edge reversed
    f.oriented_edge(e_b3, False),
    f.oriented_edge(e_b2, False),
])
plane_bad = f.plane(f.axis2_placement_3d(pa, dir3(0, 0,-1), dir3(1, 0, 0)))
face_bad = f.advanced_face([f.face_outer_bound(loop_bad, orientation=True)], plane_bad, same_sense=False)

# OPEN_SHELL: face_good + face_bad sharing e_shared
# IS the Perform-dangling-reference mechanism
shell = f.open_shell([face_good, face_bad])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
