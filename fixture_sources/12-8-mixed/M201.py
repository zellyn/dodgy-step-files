"""M201 — Tessellated solid with an empty items list.

Catalog claim: an AP242 tessellated solid is written as
`TESSELLATED_SOLID('empty_items',(),$)` — the items list empty where the
schema requires at least one tessellated structured item, and the
optional exact-geometry link unset. The solid sibling of the corpus's
empty-tessellated-SHELL fixture: same producer bug (emitting the
container before its contents and never filling it), one level up the
tessellation hierarchy.

Canonical claimant for the tessellated-solid row of the nonempty-aggregate
table (structural-linter v4).

Byte assertions:
  - contains(b"TESSELLATED_SOLID('empty_items',(),$)")
  - count_entity_def(b'TESSELLATED_SHAPE_REPRESENTATION') == 1

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M201",
    schema="AP242",
    defect=(
        "TESSELLATED_SOLID('empty_items',(),$) — the items list empty where "
        "the schema requires at least one tessellated structured item, the "
        "exact-geometry link unset; carried by a tessellated shape "
        "representation, so the empty container is what the receiver is "
        "asked to build"
    ),
)

# Minimal AP242 tessellated file: context + the empty solid in a
# tessellated shape representation (mirrors the empty-shell sibling's
# structure; no B-rep product chain).
u_len = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
u_ang = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
u_sol = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{u_len.eid},"
    "'distance_accuracy_value','')")
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{u_len.eid},#{u_ang.eid},#{u_sol.eid}))"
    f"REPRESENTATION_CONTEXT('part','3D'))")

# THE DEFECT: empty items list, unset geometry link.
ts = f._emit_raw("TESSELLATED_SOLID('empty_items',(),$)")
f._emit_raw(f"TESSELLATED_SHAPE_REPRESENTATION('',(#{ts.eid}),#{ctx.eid})")
