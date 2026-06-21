"""M052 — Open shell where closed solid expected (sheet-vs-solid demotion).

Catalog claim: A topologically closed solid is emitted as OPEN_SHELL
inside SHELL_BASED_SURFACE_MODEL instead of MANIFOLD_SOLID_BREP.
Round-trip through OCCT writer can demote closed_shell to
open_shell/OpenPolysurface; FEA/CFD pipelines reject the body for meshing.

Reproducer recipe: A topologically closed shell whose root entity in
ADVANCED_BREP_SHAPE_REPRESENTATION is SHELL_BASED_SURFACE_MODEL →
OPEN_SHELL instead of MANIFOLD_SOLID_BREP → CLOSED_SHELL.

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 3

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M052",
    schema="AP214",
    defect=(
        "Open shell where closed solid expected (sheet-vs-solid demotion); "
        "input: AP214 STEP file (SpaceClaim / HOOPS Exchange regression pattern) "
        "with a topologically closed cube emitted as OPEN_SHELL inside "
        "SHELL_BASED_SURFACE_MODEL instead of MANIFOLD_SOLID_BREP → CLOSED_SHELL; "
        "round-trip through OCCT writer demotes closed_shell to open_shell / "
        "OpenPolysurface; FEA/CFD pipelines reject the body for meshing; "
        "KiCad kicad-packages3D bundles use SHELL_BASED_SURFACE_MODEL rather than "
        "closed MANIFOLD_SOLID_BREP; "
        "kernel must heal: promote to closed shell when topology proves closure; "
        "sew within scaled tolerance and try MakeSolid; "
        "do not rely solely on entity type; "
        "synonyms: closed solid emitted as OPEN_SHELL, solid demoted to sheet body, "
        "manifold solid as shell-based-surface-model, solid expected but open shell found"
    ),
)

# ── Single triangular planar face — defect is the OPEN_SHELL wrapper ──────────
# A triangular face on a plane: the OPEN_SHELL wraps it instead of CLOSED_SHELL.
# OCCT reads SHELL_BASED_SURFACE_MODEL → OPEN_SHELL and produces a shape.

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)

dx = f.direction((1.0, 0.0, 0.0))
dy = f.direction((0.0, 1.0, 0.0))
dz = f.direction((0.0, 0.0, 1.0))
# diagonal direction from p1 → p2
dxy = f.direction((-0.7071067811865476, 0.7071067811865476, 0.0))

vx = f.vector(dx, 1.0)
vy = f.vector(dy, 1.0)
vxy = f.vector(dxy, 1.4142135623730951)

line_bot = f.line(p0, vx)           # p0 → p1 along x
line_diag = f.line(p1, vxy)         # p1 → p2 diagonal
line_left = f.line(p0, vy)          # p0 → p2 along y

e_bot  = f.edge_curve(v0, v1, line_bot)
e_diag = f.edge_curve(v1, v2, line_diag)
e_left = f.edge_curve(v0, v2, line_left)

loop = f.edge_loop([
    f.oriented_edge(e_bot,  True),
    f.oriented_edge(e_diag, True),
    f.oriented_edge(e_left, False),
])

plc = f.axis2_placement_3d(p0, dz, dx)
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="placeholder")

# THE DEFECT: OPEN_SHELL instead of CLOSED_SHELL as root of SBSM
shell = f.open_shell([face], name="topologically_closed_but_open")
sbsm = f.shell_based_surface_model([shell], name="demoted_cube")

# Product chain with ADVANCED_BREP_SHAPE_REPRESENTATION (SBSM inside ABSR = defect)
f._absr_name = "cube_as_sheet"
f.add_product_chain(sbsm, mode="surface_shape")

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M052.stp")
