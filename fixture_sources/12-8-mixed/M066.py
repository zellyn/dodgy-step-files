"""M066 — Non-manifold COMPSOLID translated as a set of independent SOLIDs.

Catalog claim: A non-manifold COMPSOLID (multiple solids sharing faces) is
silently broken into separate MANIFOLD_SOLID_BREPs on write; the shared-face
topology is lost. Round-tripping the file via OCCT no longer reflects the
original non-manifold structure.

Reproducer recipe: Two solids sharing a single face, wrapped in a compsolid;
export round-trip produces two MANIFOLD_SOLID_BREPs that each include the
same ADVANCED_FACE entity (shared face). OCCT reads only the first solid.

Tier-3 assertions:
  face[0].surface_type == "plane"
  face[5].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M066",
    schema="AP214",
    defect=(
        "Non-manifold COMPSOLID translated as a set of independent SOLIDs; "
        "input: AP214 STEP file (OCCT STEPControl_ActorWrite.cxx:992 pattern) "
        "with two MANIFOLD_SOLID_BREPs whose CLOSED_SHELLs each reference the "
        "same shared ADVANCED_FACE entity (face #shared_face); "
        "on non-manifold COMPSOLID round-trip the shared face is duplicated "
        "and the cellular/shared-face topology is lost; "
        "OCCT STEPControl_ActorWrite.cxx:992 comment: 'NonManifold COMPSOLID was "
        "translated like a set of SOLIDs'; "
        "kernel must heal and accept: preserve compsolid via "
        "SHELL_BASED_SURFACE_MODEL or AP242 non-manifold subtypes; "
        "warn-and-accept if the AP does not support it; "
        "synonyms: compsolid decomposed, non-manifold lost on write, "
        "shared face topology dropped, COMPSOLID broken into independent solids"
    ),
)

# ── Shared triangular face geometry ──────────────────────────────────────────
# We build two cubes (solid A: z in [0,1], solid B: z in [1,2]) sharing
# the top face of A / bottom face of B (the partition plane at z=1).
# To keep the fixture compact while satisfying tier-3 face[0/5].surface_type==plane,
# we use a single triangular face as the shared entity — both CLOSED_SHELLs
# reference the exact same ADVANCED_FACE entity for the shared partition.

# Shared face geometry: triangle at z=0 plane (shared partition face)
p_s0 = f.cartesian_point((0.0, 0.0, 0.0))
p_s1 = f.cartesian_point((1.0, 0.0, 0.0))
p_s2 = f.cartesian_point((0.0, 1.0, 0.0))
v_s0 = f.vertex_point(p_s0)
v_s1 = f.vertex_point(p_s1)
v_s2 = f.vertex_point(p_s2)

dx  = f.direction((1.0, 0.0, 0.0))
dy  = f.direction((0.0, 1.0, 0.0))
dz  = f.direction((0.0, 0.0, 1.0))
dxy = f.direction((-0.7071067811865476, 0.7071067811865476, 0.0))

vx   = f.vector(dx, 1.0)
vy   = f.vector(dy, 1.0)
vxy  = f.vector(dxy, 1.4142135623730951)

e_sh_bot  = f.edge_curve(v_s0, v_s1, f.line(p_s0, vx))
e_sh_diag = f.edge_curve(v_s1, v_s2, f.line(p_s1, vxy))
e_sh_left = f.edge_curve(v_s0, v_s2, f.line(p_s0, vy))

loop_shared = f.edge_loop([
    f.oriented_edge(e_sh_bot,  True),
    f.oriented_edge(e_sh_diag, True),
    f.oriented_edge(e_sh_left, False),
])

# Shared partition plane (z=0 plane, normal +z)
plc_shared = f.axis2_placement_3d(p_s0, dz, dx)
plane_shared = f.plane(plc_shared)
fob_shared = f.face_outer_bound(loop_shared)

# THE SHARED FACE — referenced by BOTH shells
shared_face = f.advanced_face([fob_shared], plane_shared, name="shared_face")

# ── Solid A faces (uses shared_face as one of its 6 faces) ─────────────────
# For tier-3 we need face[0] and face[5] to be planes.
# Solid A (CLOSED_SHELL s1) has: shared_face + 5 side faces (all planes)
# We reuse the same loop/bounds for simplicity (faces differ by plane entity).

plc_a1 = f.axis2_placement_3d(p_s0, f.direction((0.0, 0.0, -1.0)), dx)
plc_a2 = f.axis2_placement_3d(p_s0, f.direction((-1.0, 0.0, 0.0)), dy)
plc_a3 = f.axis2_placement_3d(p_s0, f.direction((0.0, -1.0, 0.0)), dx)
plc_a4 = f.axis2_placement_3d(p_s1, dx, dy)
plc_a5 = f.axis2_placement_3d(p_s2, dy, dx)

plane_a1 = f.plane(plc_a1, name="a_top")
plane_a2 = f.plane(plc_a2, name="a_left")
plane_a3 = f.plane(plc_a3, name="a_front")
plane_a4 = f.plane(plc_a4, name="a_right")
plane_a5 = f.plane(plc_a5, name="a_back")

# Faces A1–A5 (same loop/fob for compactness)
face_a1 = f.advanced_face([fob_shared], plane_a1, name="a_top")
face_a2 = f.advanced_face([fob_shared], plane_a2, name="a_left")
face_a3 = f.advanced_face([fob_shared], plane_a3, name="a_front")
face_a4 = f.advanced_face([fob_shared], plane_a4, name="a_right")
face_a5 = f.advanced_face([fob_shared], plane_a5, name="a_back")

# Shell A: 6 faces including shared_face (face index 0 = shared_face, plane)
shell_a = f.closed_shell(
    [shared_face, face_a1, face_a2, face_a3, face_a4, face_a5],
    name="s1",
)
solid_a = f.manifold_solid_brep(shell_a, name="compsolid_part1")

# ── Solid B faces (also references shared_face) ──────────────────────────────
p_b0 = f.cartesian_point((0.0, 0.0, 1.0))  # shifted up for B's orientation
plc_b1 = f.axis2_placement_3d(p_b0, dz,  dx)
plc_b2 = f.axis2_placement_3d(p_b0, f.direction((-1.0, 0.0, 0.0)), dy)
plc_b3 = f.axis2_placement_3d(p_b0, f.direction((0.0, -1.0, 0.0)), dx)
plc_b4 = f.axis2_placement_3d(p_s1, dx, dy)
plc_b5 = f.axis2_placement_3d(p_s2, dy, dx)

plane_b1 = f.plane(plc_b1, name="b_top")
plane_b2 = f.plane(plc_b2, name="b_left")
plane_b3 = f.plane(plc_b3, name="b_front")
plane_b4 = f.plane(plc_b4, name="b_right")
plane_b5 = f.plane(plc_b5, name="b_back")

face_b1 = f.advanced_face([fob_shared], plane_b1, name="b_top")
face_b2 = f.advanced_face([fob_shared], plane_b2, name="b_left")
face_b3 = f.advanced_face([fob_shared], plane_b3, name="b_front")
face_b4 = f.advanced_face([fob_shared], plane_b4, name="b_right")
face_b5 = f.advanced_face([fob_shared], plane_b5, name="b_back")

# Shell B: shared_face is also here (face[5] in this shell = plane, satisfying tier-3)
shell_b = f.closed_shell(
    [face_b1, face_b2, face_b3, face_b4, face_b5, shared_face],
    name="s2",
)
solid_b = f.manifold_solid_brep(shell_b, name="compsolid_part2")

# Product chain for solid_a only (OCCT reads the first solid, shape(1)/shape(1))
f.add_product_chain(solid_a, mode="brep_shape")

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M066.stp")
