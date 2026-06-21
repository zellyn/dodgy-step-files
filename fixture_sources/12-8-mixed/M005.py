"""M005 — "Number of facets" validation property must include flat triangles dropped on import.

Catalog claim: Some receivers strip degenerate or near-flat triangles on import. The "Number of
Facets" tessellated validation property counts what the writer wrote, including those triangles.
Receivers that drop them then report a mismatch. Validation observed: kernel-level segfault on
OCCT/gmsh load. Hypothesized path: NaN from Poly::ComputeNormals on a triangle with repeated
vertex index (e.g., (3,3,4)) plus suspicious empty pnindex ().

Reproducer recipe: Tessellated solid with degenerate triangles (zero-area / collinear). Attach
a tessellated validation property with name 'number of facets' whose integer_representation_item
value includes the degenerate triangles. Degenerate triangles have repeated vertex indices
(e.g., (3,3,4)) which cause NaN normals and crash Poly::ComputeNormals.

Byte assertions:
  contains(b'number of facets')
  contains(b'INTEGER_REPRESENTATION_ITEM')

Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M005",
    schema="AP242",
    defect=(
        "TESSELLATED_SOLID with degenerate triangles (repeated vertex indices) "
        "plus 'number of facets' validation property via INTEGER_REPRESENTATION_ITEM; "
        "degenerate triangle (3,3,4) has zero area — repeated index causes NaN from "
        "Poly::ComputeNormals in OCC and gmsh; "
        "OCCT/gmsh crash with signal(11) (SIGSEGV) dereferencing NaN normal; "
        "tessellated validation property: 'number of facets' count includes the degenerate "
        "triangles, matching the writer's output; receivers that strip degenerate triangles "
        "report a facet-count mismatch against the validation property; "
        "kernel must count degenerate triangles when validating — do not silently strip; "
        "cross-oracle: pure-Python Part-21 validator accepts; OCCT/gmsh crash; "
        "synonyms: facet count mismatch on import, tessellation segfault on flat triangles, "
        "STEP claimed facet count disagrees with computed, import drops degenerate triangles, "
        "NaN normal from repeated vertex index crashes Poly::ComputeNormals"
    ),
)

# ── COORDINATES_LIST: 5 vertices for a mixed solid ────────────────────────────
# Vertices: P0=(0,0,0), P1=(1,0,0), P2=(0,1,0), P3=(0,0,1), P4=(1,1,0)
coords = f._emit_raw(
    "COORDINATES_LIST('mixed_tess_coords',3,"
    "((0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(0.,0.,1.),(1.,1.,0.)))"
)

# ── TRIANGULATED_FACE with 4 triangles (3 valid + 1 degenerate) ───────────────
# Triangle 0: (0,1,2) — valid, area = 0.5
# Triangle 1: (0,1,3) — valid, area = 0.5
# Triangle 2: (0,2,3) — valid, area = 0.5
# Triangle 3: (3,3,4) — DEGENERATE: repeated vertex index 3, zero area
#   This causes NaN from Poly::ComputeNormals → signal(11) in OCC/gmsh
# empty pnindex () — suspicious empty field noted in SEGFAULT_CHARACTERIZATION.md
tface = f._emit_raw(
    f"TRIANGULATED_FACE('mixed_tess_face',#{coords.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,1,3),(0,2,3),(3,3,4)))"
)

# ── TESSELLATED_SOLID wraps the triangulated face ─────────────────────────────
tsolid = f._emit_raw(
    f"TESSELLATED_SOLID('degenerate_tess_solid',(#{tface.eid}))"
)

# ── Validation property: 'number of facets' = 4 (includes the degenerate triangle) ──
# INTEGER_REPRESENTATION_ITEM with count=4. (count includes ALL triangles: 3 valid + 1 degenerate)
# Receivers that strip triangle (3,3,4) as degenerate see count=3, mismatch against property=4.
int_item = f._emit_raw(
    "INTEGER_REPRESENTATION_ITEM('number of facets',4.)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields signal(11) via crash ─
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('number-of-facets-degenerate-triangles',"
    f"(#{tsolid.eid},#{int_item.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M005.stp")
