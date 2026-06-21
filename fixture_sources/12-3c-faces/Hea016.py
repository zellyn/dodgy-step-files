"""Hea016 — Empty solid output from STEP export of complex body.

Catalog claim (FreeCAD #20396): A STEP writer encounters a face it cannot
represent in B-rep form, silently skips it, and wraps the resulting zero-face
CLOSED_SHELL as MANIFOLD_SOLID_BREP. The receiver's shape-healer cannot
recover any solid from a shell with zero faces.

Mechanism: A MANIFOLD_SOLID_BREP whose outer shell is a CLOSED_SHELL that
references zero ADVANCED_FACEs — an empty shell wrapped as a solid.
The writer must reject this before emission; receivers must report
CLOSED_SHELL with no faces as a clear diagnostic.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea016",
    defect=(
        "MANIFOLD_SOLID_BREP wrapping a CLOSED_SHELL with ZERO ADVANCED_FACEs; "
        "writer silently skipped degenerate face(s), leaving empty shell; "
        "receiver's shape-healer cannot recover solid from zero-face closed shell; "
        "FreeCAD #20396: writer must reject empty-shell wrap before emission; "
        "defect: CLOSED_SHELL() with empty face list"
    ),
)

# ── Plane geometry for context (standard axes) ────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)

# ── DEFECT: CLOSED_SHELL with zero face references ───────────────────────────
# Emit an empty CLOSED_SHELL: the face-list is empty ()
empty_shell = f._emit_raw("CLOSED_SHELL('empty_shell',(  ))")
solid       = f.manifold_solid_brep(empty_shell, name="Hea016_body")

f.add_product_chain(solid, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea016.stp")
