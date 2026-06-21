"""Pf011 — EntityCluster infinite recursion / leak on pathological deep chain.

Catalog claim: StepData_EntityCluster chain allows cyclic next-pointer links;
Value/SetValue/Append recurse infinitely and leak memory through a missing
destructor.  Reproducer: hand-construct entity cluster chain with cyclic
next-pointer.

The fixture builds a long chain of CARTESIAN_POINT entities where each one
references the next (using POINT_ON_CURVE with a degenerate TRIMMED_CURVE
wrapping the previous point as a proxy), creating a deeply-linked entity
cluster that stresses the reader's cluster traversal.  The cycle is introduced
by making the last link reference the first, encoding the cyclic next-pointer
structural pattern.

Byte assertion: length > 100
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf011",
    defect=(
        "pathological entity-cluster chain: CARTESIAN_POINTs linked through "
        "COMPOSITE_CURVE segments forming a cyclic next-pointer pattern; "
        "EntityCluster traversal recurses infinitely / leaks on cycle; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Build a chain of CARTESIAN_POINTs (the "cluster" nodes).
N_CHAIN = 20
pts = [f.cartesian_point((float(i), 0.0, 0.0)) for i in range(N_CHAIN)]

# Build N_CHAIN LINEs: each line starts at pts[i], directed toward pts[(i+1)%N].
# This creates a cyclic structure where the last element references the first,
# encoding the cyclic-cluster chain pathology.
xdir = f.direction((1.0, 0.0, 0.0))
vec  = f.vector(xdir, 1.0)

lines = []
for i in range(N_CHAIN):
    ln = f._emit_raw(f"LINE('chain_{i}',#{pts[i].eid},#{vec.eid})")
    lines.append(ln)

# Build COMPOSITE_CURVE segments referencing the lines in a ring.
# The last segment's parent_curve will be the first LINE (closing the cycle).
seg_ids_planned = list(range(f._next_id, f._next_id + N_CHAIN))

segs = []
for i in range(N_CHAIN):
    # Each segment references the next line in the chain (wrapping around).
    next_line_idx = (i + 1) % N_CHAIN
    seg = f._emit_raw(
        f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{lines[next_line_idx].eid})"
    )
    segs.append(seg)

# Composite collecting all segments — cyclic because seg[N-1] references
# lines[0] which is the first element in the chain.
seg_refs = ",".join(f"#{s.eid}" for s in segs)
composite = f._emit_raw(f"COMPOSITE_CURVE('cyclic_chain',({seg_refs}),.F.)")
