"""Ad103 — Coincident VERTEX_POINTs at identical CARTESIAN_POINT coordinates trigger vertex-merge healing throws on already-absorbed vertex.

Catalog claim: a vertex-union step is invoked on two vertices that are
marked already-merged from a previous pass. The internal index of merged
vertices is queried with one of the vertices, returning a stale entry
pointing at a freed vertex object — accessed afterwards. Fixture
precondition: two distinct VERTEX_POINTs reference separate CARTESIAN_POINT
entities with identical coordinates (e.g. both at (0,0,0)) — coincident
vertices that have not been merged.

Reproducer recipe: Two VERTEX_POINTs V1, V2 referencing CARTESIAN_POINTs
at the same coordinates. Union them once (V2 absorbed into V1). Then
attempt to union V2 again with V3.

Byte assertions:
  contains(b'ISO-10303-21')
  contains(b'END-ISO-10303-21')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad103",
    defect=(
        "coincident VERTEX_POINTs at identical CARTESIAN_POINT coordinates; "
        "vertex-union table queried with already-absorbed vertex returns stale "
        "entry pointing at freed vertex object; "
        "vertex-union table must be updated atomically; "
        "re-query of absorbed vertex must return canonical replacement; "
        "must not throw on already-absorbed vertex; "
        "OCCT MANTIS#0027078, #0024919; See also Tsh050, N045; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# Satisfies: contains(b'ISO-10303-21') and contains(b'END-ISO-10303-21')
# (both appear in the standard Part-21 bookends emitted by render()).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: three VERTEX_POINTs where V1 and V2 are coincident
# (same coordinates (0,0,0)) and V3 is coincident with V2 (same coords).
# The vertex-merge healing pass will:
#   1. Merge V2 into V1 (V2 absorbed, canonical = V1).
#   2. Attempt a second merge: V2 (now absorbed) with V3 — stale-entry access.
#
# Provenance note: the stale-entry use-after-free requires the kernel to
# perform two successive merge passes retaining multi-pass state. The static
# fixture encodes the input precondition (coincident vertices); the runtime
# defect is triggered by the kernel's healing pipeline.

# Three separate CARTESIAN_POINT entities: cp1 and cp2 at (0,0,0), cp3 at (0,0,0).
# All three coincident → kernel must merge all three → multi-pass merge.
cp1 = f.cartesian_point((0.0, 0.0, 0.0), name="coincident_a")
cp2 = f.cartesian_point((0.0, 0.0, 0.0), name="coincident_b")
cp3 = f.cartesian_point((0.0, 0.0, 0.0), name="coincident_c")

# Three distinct VERTEX_POINT entities pointing at those coordinates.
# V1 and V2 reference identical coordinates; V2 and V3 also reference
# identical coordinates. After absorbing V2→V1, re-querying V2 triggers
# the stale-entry dereference when the kernel next tries to merge V3.
v1 = f.vertex_point(cp1, name="vertex_canonical")
v2 = f.vertex_point(cp2, name="vertex_absorbed")
v3 = f.vertex_point(cp3, name="vertex_third")

# Extra pair of coincident vertices at a different location to exercise
# the multi-location merge path and maximise coverage of the stale-entry bug.
cp4 = f.cartesian_point((1.0, 0.0, 0.0), name="coincident_d")
cp5 = f.cartesian_point((1.0, 0.0, 0.0), name="coincident_e")
v4 = f.vertex_point(cp4, name="vertex_second_canonical")
v5 = f.vertex_point(cp5, name="vertex_second_absorbed")

# Emit these vertices in a GEOMETRIC_CURVE_SET so the reader processes them.
# (The vertex-merge pass operates over all VERTEX_POINTs visible from
# the model entity.)
f._emit_raw(
    f"GEOMETRIC_CURVE_SET('coincident_vertices',"
    f"({cp1.ref()},{cp2.ref()},{cp3.ref()},{cp4.ref()},{cp5.ref()}))"
)
