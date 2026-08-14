"""Ad140 — ADVANCED_FACE with a null (`$`) element in its mandatory bounds list → signal(11).

Catalog claim (input pattern): an `ADVANCED_FACE` supplies `($)` for its
mandatory `bounds` list — a non-empty aggregate whose single element is the null
token `$` instead of a `FACE_OUTER_BOUND`/`FACE_BOUND` reference. When the reader
transfers the face and iterates its bounds, it dereferences the null element
without checking it resolved. Sibling of Ad139 (VECTOR null scalar-reference):
that is a null in a mandatory SCALAR reference slot; this is a null ELEMENT
inside a mandatory AGGREGATE — a distinct code path and a distinct structural
shape. Discovered by null-slot fuzzing of the (valid) M202 cone, generalising
the ZDI-22-1467 / CVE-2022-43609 null-mandatory-reference crash class.

`$` inside an aggregate is not an empty aggregate (`()`), so the structural
linter's EMPTY_AGGREGATE check does not fire; part21 accepts `$` as a null
token; a strict reader must reject a null aggregate element (or drop the face)
rather than dereference it.

Byte assertions:
  contains(b'ADVANCED_FACE')
  matches(rb"ADVANCED_FACE\('',\(\$\)")

OCC behavior: signal(11) — both heal modes SIGSEGV iterating the null bounds element.
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad140",
    defect=(
        "an ADVANCED_FACE supplies ($) for its mandatory bounds list: a "
        "non-empty aggregate whose single element is the null token $ instead "
        "of a FACE_OUTER_BOUND reference; when the reader transfers the face "
        "and iterates its bounds it dereferences the null element without "
        "checking it resolved; distinct from Ad139 (null in a scalar reference "
        "slot) — this is a null element inside a mandatory aggregate, a "
        "different code path; $ inside an aggregate is not an empty aggregate "
        "so EMPTY_AGGREGATE does not catch it and part21 accepts $ as a null "
        "token; expected robust behavior: reject a null aggregate element or "
        "drop the face, never dereference it; synonyms: null bound in "
        "ADVANCED_FACE, null element in bounds list, $ in face_outer_bound "
        "list, null aggregate element crash; the null bounds element is the "
        "defect carrier"
    ),
)

# Valid conical surface; the FACE carries a null ($) bound element.
semi_angle, base_r = 0.4, 1.0
cone_surf = f.conical_surface(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    base_r, semi_angle)
# DEFECT: bounds aggregate is ($) — one null element, no FACE_OUTER_BOUND.
bad_face = f._emit_raw(f"ADVANCED_FACE('',($),#{cone_surf.eid},.T.)")
f.add_product_chain(f.manifold_solid_brep(f.closed_shell([bad_face])), mode="brep_shape")
