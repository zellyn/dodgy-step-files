"""Ad053 — Cyclic reference-to-reference chain of SHAPE_REPRESENTATION_RELATIONSHIP.

Catalog claim: a SHAPE_REPRESENTATION_RELATIONSHIP (SRR) is used as the
right-hand side (rep_2) of another SRR — a "reference to reference" chain —
producing an invalid model.  Common attack shape: three SRR entities forming
a 3-cycle by each referencing the next in rep_2 (#100→#101→#102→#100);
deeper chains are quadratic or cyclic.

Reproducer recipe: SHAPE_REPRESENTATION_RELATIONSHIP whose rep_2 is itself
an SRR.

Byte assertions:
  count_entity_def(b'SHAPE_REPRESENTATION_RELATIONSHIP') >= 3
  matches(rb'(?s)#100=SHAPE_REPRESENTATION_RELATIONSHIP[^;]+#101[^;]+;.*#101=SHAPE_REPRESENTATION_RELATIONSHIP[^;]+#102')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad053",
    defect=(
        "cyclic SHAPE_REPRESENTATION_RELATIONSHIP chain: #100→#101→#102→#100; "
        "SRR used as rep_2 of another SRR — invalid reference-to-reference; "
        "resolver must cap recursion depth; must not infinite loop; "
        "Mantis 0031568; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))  # ID 1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # ID 2

# The byte assertions require exact entity IDs #100, #101, #102.
# add_product_chain() uses IDs 9000+, so we pad BEFORE calling it.
# After origin(1) + gcs(2), _next_id == 3.  Pad to 100 with dummy points.
while f._next_id < 100:
    f._emit_raw("CARTESIAN_POINT('pad',(0.0,0.0,0.0))")

# Now _next_id == 100.  Emit the 3-cycle:
#   #100 = SRR('','', rep_1=placeholder, rep_2=#101)
#   #101 = SRR('','', rep_1=placeholder, rep_2=#102)
#   #102 = SRR('','', rep_1=placeholder, rep_2=#100)  ← closes the cycle
#
# rep_1 is a forward-ref to a placeholder representation (#200) so the
# entity tree is syntactically complete while the cycle sits in rep_2.

# #100: rep_2 = #101 (forward reference — emitted before #101 is declared).
# Satisfies first half of the multiline regex.
f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('cycle_a','',#200,#101)"
)

# #101: rep_2 = #102 (forward reference).
# Satisfies second half of the multiline regex.
f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('cycle_b','',#200,#102)"
)

# #102: rep_2 = #100 — closes the 3-cycle.
f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('cycle_c','',#200,#100)"
)

# Pad a placeholder SHAPE_REPRESENTATION at #200 so rep_1 refs resolve.
while f._next_id < 200:
    f._emit_raw("CARTESIAN_POINT('pad2',(0.0,0.0,0.0))")
f._emit_raw(f"SHAPE_REPRESENTATION('placeholder',(#{origin.eid}),#{origin.eid})")

f.add_product_chain(gcs)

# Satisfies: count_entity_def(b'SHAPE_REPRESENTATION_RELATIONSHIP') >= 3
# (three SRR definitions at #100, #101, #102).
