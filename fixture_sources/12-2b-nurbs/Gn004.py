"""Gn004 — Complex BSpline surface entity with empty knots/multiplicities.

Catalog claim: complex entity (BOUNDED_SURFACE() B_SPLINE_SURFACE()
B_SPLINE_SURFACE_WITH_KNOTS() ... RATIONAL_B_SPLINE_SURFACE()) carries empty
KNOTS()/KNOT_MULTIPLICITIES() lists or empty name. Reader null-derefs.
OCCT crashes (signal 11).

Byte assertion: contains(b'B_SPLINE_SURFACE')
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn004",
    defect=(
        "Complex rational BSpline surface entity with empty knot/multiplicity lists "
        "and an empty name; OCCT readers null-deref'd (Mantis 0029478, commit 5dd92c3); "
        "reject the surface and skip the host face; emit per-entity diagnostic; "
        "never crash; "
        "4x4 control net present but surface declaration has empty KNOTS()/mults and '' name"
    ),
)

# 4x4 control net
pts = {}
for i in range(4):
    for j in range(4):
        pts[(i,j)] = f.cartesian_point((float(i), float(j), 0.1 * i * (3 - j)))

def row_refs(i):
    return "(" + ",".join(f"#{pts[(i,j)].eid}" for j in range(4)) + ")"

cp_grid = "(" + ",".join(row_refs(i) for i in range(4)) + ")"

# THE DEFECT: complex entity with empty knots and multiplicities
f._emit_raw(
    f"(\n"
    f"  BOUNDED_SURFACE()\n"
    f"  B_SPLINE_SURFACE(3,3,{cp_grid},.UNSPECIFIED.,.F.,.F.,.F.)\n"
    f"  B_SPLINE_SURFACE_WITH_KNOTS((),(),(),(),.UNSPECIFIED.)\n"
    f"  GEOMETRIC_REPRESENTATION_ITEM()\n"
    f"  RATIONAL_B_SPLINE_SURFACE(((1.,1.,1.,1.),(1.,1.,1.,1.),(1.,1.,1.,1.),(1.,1.,1.,1.)))\n"
    f"  REPRESENTATION_ITEM('')\n"
    f"  SURFACE()\n"
    f")"
)
