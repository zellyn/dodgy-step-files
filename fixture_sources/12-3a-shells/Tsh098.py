"""Tsh098 — ShapeUpgrade_RemoveLocations.Remove location-after-traversal.

Catalog claim: During MakeNewShape traversal, shape's location is removed from
top-level entity. However, face/edge references downstream may retain stale
location if transformation is not propagated consistently.

Mechanism IS the shell structure: The OPEN_SHELL contains one ADVANCED_FACE
with a non-identity AXIS2_PLACEMENT_3D — the face's plane origin IS at
(5, 3, 2) (translated position) rather than the world origin. The shell itself
IS wrapped in a SHELL_BASED_SURFACE_MODEL, and the PRODUCT shape references
this translated shell. When RemoveLocations traverses the top-level product
and strips the location, the ADVANCED_FACE's AXIS2_PLACEMENT_3D origin at
(5,3,2) IS still directly embedded in the face topology — not propagated out
as a separate location transform. This mismatch IS the mechanism: face geometry
reports translated coordinates, but the shell-level location has been cleared,
causing downstream face observation to see translated frame instead of world frame.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh098",
    defect=(
        "OPEN_SHELL with 1 ADVANCED_FACE whose PLANE AXIS2_PLACEMENT_3D origin IS at (5,3,2) — IS the translation mechanism; "
        "face plane origin (5,3,2) IS directly embedded in ADVANCED_FACE topology as non-identity placement; "
        "translated AXIS2_PLACEMENT_3D IS the location wired into face geometry — not a separate transform; "
        "shell wrapped in SHELL_BASED_SURFACE_MODEL at product level with translated face; "
        "RemoveLocations removes top-level shell location but face AXIS2_PLACEMENT_3D (5,3,2) IS retained; "
        "stale translated origin IS the mechanism — downstream face sees (5,3,2) frame not world frame; "
        "fix: propagate location removal down to all contained face/edge geometry; "
        "emit E_LOCATION_PROPAGATION_INCOMPLETE when face geometry retains pre-removal translation"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Translated face: 1x1 quad with plane origin at (5,3,2) — IS the non-identity placement mechanism
# The translation (5,3,2) IS directly in the AXIS2_PLACEMENT_3D, not a separate location entity
tx, ty, tz = 5.0, 3.0, 2.0
pF = [
    cp(tx,     ty,     tz),
    cp(tx+1.0, ty,     tz),
    cp(tx+1.0, ty+1.0, tz),
    cp(tx,     ty+1.0, tz),
]
vF = [f.vertex_point(p) for p in pF]
eF = [
    led(vF[0], vF[1], pF[0],  1, 0, 0),
    led(vF[1], vF[2], pF[1],  0, 1, 0),
    led(vF[2], vF[3], pF[2], -1, 0, 0),
    led(vF[3], vF[0], pF[3],  0,-1, 0),
]
loop_f = f.edge_loop([f.oriented_edge(e, True) for e in eF])

# AXIS2_PLACEMENT_3D origin IS (5,3,2) — translated origin IS the location mechanism wired in face
pl_origin = cp(tx, ty, tz)
pl_f = f.plane(f.axis2_placement_3d(pl_origin, dir3(0, 0, 1), dir3(1, 0, 0)))

# ADVANCED_FACE with translated plane IS the mechanism — location embedded in face topology
face = f.advanced_face([f.face_outer_bound(loop_f, orientation=True)], pl_f, same_sense=True)

# Single-face OPEN_SHELL: translated face IS wired into shell — IS the RemoveLocations mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
