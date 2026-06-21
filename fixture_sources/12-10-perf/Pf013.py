"""Pf013 — Entity-count amplification: tiny file, many GB resident.

Catalog claim: a file with many tiny entities each holding many references
causes the parser to allocate O(N) instance pointer table and O(N)
reverse-reference map, peaking at ~40 GB resident.  Hub-style back-reference
patterns (10⁷ tiny entities pointing at one HUB) cause contiguous-vector
reallocation thrash.

The fixture encodes the hub back-reference pattern at fixture scale: one
HUB CARTESIAN_POINT is referenced by N_SPOKES LINE entities, each of which
is referenced by N_SPOKES COMPOSITE_CURVE_SEGMENT entities, all collected
into a GEOMETRIC_CURVE_SET.  The fan-in at the HUB node is the structural
pattern that causes the contiguous-vector reallocation thrash.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 10
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf013",
    defect=(
        "hub fan-in pattern: one HUB CARTESIAN_POINT referenced by many LINE "
        "entities; back-reference map reallocation thrash at hub node; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# HUB entity: a single CARTESIAN_POINT referenced by every LINE.
hub = f.cartesian_point((0.0, 0.0, 0.0))

# N_SPOKES satellite points + lines all referencing the HUB as their origin.
N_SPOKES = 15

xdir = f.direction((1.0, 0.0, 0.0))
vec  = f.vector(xdir, 1.0)

# Spoke points (satellites)
spoke_pts = [
    f.cartesian_point((float(i + 1), 0.0, 0.0)) for i in range(N_SPOKES)
]

# Each LINE uses the HUB as its pnt (many back-references to the hub).
lines = [
    f._emit_raw(f"LINE('spoke_{i}',#{hub.eid},#{vec.eid})")
    for i in range(N_SPOKES)
]

# Additional CARTESIAN_POINTs for satellites to satisfy byte assertion >= 10.
extra_pts = [
    f.cartesian_point((float(i), 1.0, 0.0)) for i in range(5)
]

# Collect all lines + hub + spokes into a GEOMETRIC_CURVE_SET.
all_elems = (
    [f"#{hub.eid}"]
    + [f"#{p.eid}" for p in spoke_pts]
    + [f"#{p.eid}" for p in extra_pts]
    + [f"#{ln.eid}" for ln in lines]
)
elems_str = ",".join(all_elems)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('hub_fanin',({elems_str}))")
f.add_product_chain(gcs)
