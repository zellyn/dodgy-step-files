"""M063 — Entity has no unit context; defaults silently applied.

Catalog claim: A SHAPE_REPRESENTATION has no GEOMETRIC_REPRESENTATION_CONTEXT
attached, or the context is missing units. The reader silently applies default
units (typically mm).

Reproducer recipe: A SHAPE_REPRESENTATION with context_of_items referencing a
context that lacks LENGTH_UNIT; the GEOMETRIC_REPRESENTATION_CONTEXT is present
but its name is 'no_units' and its global_unit_assigned_context is empty.

Byte assertions:
  contains(b'GEOMETRIC_REPRESENTATION_CONTEXT')
  matches(rb'GEOMETRIC_REPRESENTATION_CONTEXT\\(\\'no_units\\',\\$,3\\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M063",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file where SHAPE_REPRESENTATION references a "
        "GEOMETRIC_REPRESENTATION_CONTEXT lacking LENGTH_UNIT — no unit context, "
        "reader silently applies default units; "
        "input: AP242 STEP file where SHAPE_REPRESENTATION.context_of_items points "
        "to a GEOMETRIC_REPRESENTATION_CONTEXT('no_units',$,3) — the second attribute "
        "(global_unit_assigned_context, a GLOBAL_UNIT_ASSIGNED_CONTEXT mixin) is $=absent; "
        "no LENGTH_UNIT is declared anywhere in the file for this representation; "
        "AP203/214/242 mandate that every geometric representation carry an explicit "
        "unit context; a reader that silently defaults to mm will produce a model that "
        "is 1000× too large or too small when the intended unit was metres or inches; "
        "kernel must reject as malformed (units are mandatory) or warn loudly and "
        "require explicit user confirmation of the assumed unit; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP no units defaulted, kernel guessed units, model 1000x wrong, "
        "no unit context default mm applied, SHAPE_REPRESENTATION lacks unit context"
    ),
)

# ── Context WITHOUT units — the defect ────────────────────────────────────────
# Byte assertions:
#   contains(b'GEOMETRIC_REPRESENTATION_CONTEXT')
#   matches(rb'GEOMETRIC_REPRESENTATION_CONTEXT\(\'no_units\',\$,3\)')
# The literal form 'GEOMETRIC_REPRESENTATION_CONTEXT(\'no_units\',$,3)' matches
# the catalog byte assertion and demonstrates the missing unit context.
no_unit_ctx = f._emit_raw(
    "GEOMETRIC_REPRESENTATION_CONTEXT('no_units',$,3)"
)

# ── Simple geometry that would depend on the missing unit ─────────────────────
pt_a = f._emit_raw("CARTESIAN_POINT('pt_a',(0.,0.,0.))")
pt_b = f._emit_raw("CARTESIAN_POINT('pt_b',(100.,0.,0.))")
pt_c = f._emit_raw("CARTESIAN_POINT('pt_c',(0.,100.,0.))")

dir_z = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.))")
dir_x = f._emit_raw("DIRECTION('x_axis',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('placement',#{pt_a.eid},#{dir_z.eid},#{dir_x.eid})"
)

# ── SHAPE_REPRESENTATION referencing the no-unit context ─────────────────────
# This is what a buggy writer emits: a representation with a bare
# GEOMETRIC_REPRESENTATION_CONTEXT that has no associated unit declarations.
shape_rep_no_units = f._emit_raw(
    f"SHAPE_REPRESENTATION('no_unit_shape',(#{pt_a.eid},#{pt_b.eid},#{pt_c.eid}),"
    f"#{no_unit_ctx.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('shape-representation-missing-unit-context-defaulted',"
    f"(#{no_unit_ctx.eid},#{shape_rep_no_units.eid},"
    f"#{pt_a.eid},#{pt_b.eid},#{pt_c.eid},#{placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M063.stp")
