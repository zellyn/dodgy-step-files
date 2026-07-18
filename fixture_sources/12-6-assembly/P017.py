"""P017 — Free wires in a top-level COMPOUND silently dropped.

Catalog claim: STEP file with a top-level COMPOUND mixing solids and free
EDGE_CURVE / WIRE items at the same level. With importer's "compound merge"
preference OFF, loose edges are dropped silently.

The defect: three free wires are represented as loose *topological* EDGE_CURVE
items (with their VERTEX_POINTs) and wired as members of the GEOMETRIC_CURVE_SET
that IS the shape-representation item (reachable from the SHAPE root). Per
ISO 10303-42 a GEOMETRIC_CURVE_SET's members are geometric point|curve|surface
selects, NOT topological EDGE_CURVE; OCCT's STEP transfer walks the reachable
set, cannot make geometry from the loose edge topology, and silently drops the
whole set — producing an EMPTY shape (accept_silent, shape_null). A well-formed
control that carries the same three wires as bounded geometric curves
(TRIMMED_CURVE of the same LINE) is preserved: OCCT builds 3 edges + 6 vertices.
The empty result is therefore caused by the loose-wire defect, not the
construction — a genuine, oracle-distinguishable demonstration of free wires
being silently dropped.

Verified live (OCCT 7.8.1, 2026-07-18):
  defect  occt_heal_on/off = empty (accept_silent, shape_null); gmsh = empty
  control (same wires as TRIMMED_CURVE) = occt shape(6 vertex,3 edge); gmsh 9

Byte assertions:
  count_entity_def(b'EDGE_CURVE') >= 2
  count_entity_def(b'VERTEX_POINT') >= 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P017",
    defect=(
        "three free wires represented as loose topological EDGE_CURVE + "
        "VERTEX_POINT items are wired as members of the GEOMETRIC_CURVE_SET "
        "that IS the shape-representation item (reachable from the SHAPE root); "
        "GEOMETRIC_CURVE_SET members must be geometric point/curve/surface, not "
        "topological EDGE_CURVE, so OCCT's transfer silently drops the loose "
        "wires and yields an empty shape; a control carrying the same wires as "
        "bounded TRIMMED_CURVE geometry is preserved (3 edges + 6 vertices) — "
        "compliant receivers must preserve free wires in the top-level COMPOUND"
    ),
    schema="AP242",
)

# ── The defect: three free wires as loose EDGE_CURVE topology ─────────────────
# Each wire = CARTESIAN_POINT x2 -> VERTEX_POINT x2 -> LINE -> EDGE_CURVE.
WIRES = [
    ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0)),  # wire 1
    ((0.0, 1.0, 0.0), (3.0, 1.0, 0.0)),  # wire 2
    ((1.0, 0.0, 0.0), (4.0, 3.0, 0.0)),  # wire 3 (diagonal)
]

edge_refs = []
for idx, (a, b) in enumerate(WIRES, start=1):
    pa = f.cartesian_point(a, name=f"wire{idx}_p0")
    pb = f.cartesian_point(b, name=f"wire{idx}_p1")
    va = f.vertex_point(pa, name=f"wire{idx}_v0")
    vb = f.vertex_point(pb, name=f"wire{idx}_v1")
    dx, dy, dz = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    d = f.direction((dx / length, dy / length, dz / length), name=f"wire{idx}_dir")
    vec = f.vector(d, length)
    line = f.line(pa, vec, name=f"wire{idx}_line")
    edge = f.edge_curve(va, vb, line, True, name=f"wire{idx}_edge")
    edge_refs.append(edge)

# GEOMETRIC_CURVE_SET holding the loose EDGE_CURVE wires, made the shape-rep
# item so the defect carriers are REACHABLE from the SHAPE root (the wiring fix).
refs = ",".join(f"#{e.eid}" for e in edge_refs)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('free_wires',({refs}))")
f.add_product_chain(gcs)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('FreeWireComp','FreeWireComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','free_wire_instance','',#9054,#{sub_pdef.eid},$)"
)
