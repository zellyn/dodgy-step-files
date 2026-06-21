"""Ad082 — Late-bound forward reference (FACE_OUTER_BOUND → EDGE_LOOP → ORIENTED_EDGE defined later).

Catalog claim: entity definition order forces forward references — a
FACE_OUTER_BOUND (#21) references an EDGE_LOOP (#22) that itself references an
ORIENTED_EDGE (#200) defined later in the file. The ASCII reader handles such
forward references cleanly, but the binary BREP reader throws an unhandled
indexed-map lookup-failure exception on the same canonical content.

Reproducer recipe: FACE_OUTER_BOUND referencing EDGE_LOOP which references
ORIENTED_EDGE at a much higher entity ID (defined later in file).

Byte assertions:
  matches(rb'(?s)#21=FACE_OUTER_BOUND[^;]+#22[^;]+;.*#22=EDGE_LOOP[^;]+#200') or matches(rb'(?s)EDGE_LOOP[^;]*#200')
  contains(b'EDGE_LOOP') and contains(b'ORIENTED_EDGE') and contains(b'#200')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad082",
    defect=(
        "late-bound forward reference: FACE_OUTER_BOUND(#21) → EDGE_LOOP(#22) → "
        "ORIENTED_EDGE(#200) defined later in file; "
        "ASCII reader handles forward refs cleanly, binary BREP reader throws "
        "indexed-map lookup-failure; parser-parity bug; OCCT #844; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# After these two lines: _next_id == 3.
origin = f.cartesian_point((0.0, 0.0, 0.0))   # #1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2

# Attack payload: forward-reference chain using exact entity IDs #21, #22, #200.
# Emit ALL attack entities BEFORE add_product_chain so _next_id stays in
# the low range.

# Pad with CARTESIAN_POINTs (IDs 3..20) up to ID 21.
while f._next_id < 21:
    f._emit_raw(f"CARTESIAN_POINT('pad',({float(f._next_id)},0.0,0.0))")

# #21 = FACE_OUTER_BOUND referencing #22 (forward ref — not yet defined)
# Satisfies: matches(rb'(?s)#21=FACE_OUTER_BOUND[^;]+#22[^;]+;.*#22=EDGE_LOOP')
f._emit_raw("FACE_OUTER_BOUND('',#22,.T.)")    # #21

# #22 = EDGE_LOOP referencing #200 (far forward ref — not yet defined)
# Satisfies: matches(rb'(?s)EDGE_LOOP[^;]*#200')
f._emit_raw("EDGE_LOOP('',(#200))")            # #22

# Pad (IDs 23..199) up to ID 200.
while f._next_id < 200:
    f._emit_raw(f"CARTESIAN_POINT('gap_pad',({float(f._next_id)},0.0,0.0))")

# #200 = ORIENTED_EDGE (defined late — target of the forward refs above).
# The edge_element can dangle (#201) as we only need bytes to match.
# Satisfies: contains(b'ORIENTED_EDGE') and contains(b'#200')
f._emit_raw("ORIENTED_EDGE('',$,$,#201,.T.)")  # #200

# #201 = EDGE_CURVE with self-referential dangling endpoints — just needs
# to exist so the file has a real entity behind #201.
f._emit_raw("EDGE_CURVE('',#1,#1,#1,.T.)")    # #201

# Now attach the product chain.
f.add_product_chain(gcs)
