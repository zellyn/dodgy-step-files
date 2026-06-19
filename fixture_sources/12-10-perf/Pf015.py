"""Pf015 — Pathological B-rep from mesh conversion: OPEN_SHELL with many tiny triangle ADVANCED_FACEs.

Catalog claim: each input mesh triangle becomes one ADVANCED_FACE in a
huge OPEN_SHELL. Sewing fails. Booleans fail with 'BRepAlgoAPI_BuilderArgs
check failed'. Joining > 10k faces takes O(n^2).

The OPEN_SHELL form is deliberate — it advertises the non-watertightness
inherited from the mesh. Previous fixture used 8 placeholder triangle
faces with shared structures. Regen: 100 actual triangle ADVANCED_FACEs,
each a unique tiny triangle, in ONE OPEN_SHELL.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf015",
             defect="huge OPEN_SHELL of tiny triangle ADVANCED_FACEs from mesh→STEP")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

ROWS = 10   # 10x10 = 100 triangle faces

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

import math
faces = []
for i in range(ROWS):
    for j in range(ROWS):
        # One triangle per cell.
        x = float(i)
        y = float(j)
        p0 = f.cartesian_point((x, y, 0.0))
        p1 = f.cartesian_point((x + 1.0, y, 0.0))
        p2 = f.cartesian_point((x + 0.5, y + 1.0, 0.0))
        v0 = f.vertex_point(p0)
        v1 = f.vertex_point(p1)
        v2 = f.vertex_point(p2)
        e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
        # Diagonal edge p1 → p2.
        dx, dy = -0.5, 1.0
        mag = math.hypot(dx, dy)
        e1 = line_edge(p1, (dx / mag, dy / mag, 0.0), mag, v1, v2)
        # Diagonal edge p2 → p0.
        dx, dy = -0.5, -1.0
        e2 = line_edge(p2, (dx / mag, dy / mag, 0.0), mag, v2, v0)
        loop = f.edge_loop([
            f.oriented_edge(e0, True),
            f.oriented_edge(e1, True),
            f.oriented_edge(e2, True),
        ])
        faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

# The non-watertight OPEN_SHELL is the signature of the defect.
shell = f._emit_raw(
    f"OPEN_SHELL('mesh_derived_open_shell',"
    f"({','.join(f'#{x.eid}' for x in faces)}))"
)
sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('mesh_sbsm',(#{shell.eid}))"
)
f.add_product_chain(sbsm)
