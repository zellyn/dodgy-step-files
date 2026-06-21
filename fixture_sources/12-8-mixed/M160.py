"""M160 — STEP file imports as a near-empty document despite well-formed entities.

Catalog claim: A STEP file with valid MANIFOLD_SOLID_BREPs wrapped in
ADVANCED_BREP_SHAPE_REPRESENTATION, but the assembly is glued together by
SHAPE_REPRESENTATION_RELATIONSHIP records whose rep_1 and rep_2 slots reference
each other in an order the reader's traversal does not expect. The reader walks
only the top-level PRODUCT_DEFINITION chain, finds no shape attached, and
reports success with an empty document.

Reproducer recipe: Two ADVANCED_BREP_SHAPE_REPRESENTATIONs linked by
SHAPE_REPRESENTATION_RELATIONSHIP(#A,#B) where the top-level
PRODUCT_DEFINITION_SHAPE only sees representation A (which contains no
geometry). Geometry lives in B. Reader imports nothing from B.

Byte assertions:
  contains(b'SHAPE_REPRESENTATION_RELATIONSHIP')
  contains(b'MANIFOLD_SOLID_BREP') or contains(b'ADVANCED_BREP_SHAPE_REPRESENTATION')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M160",
    schema="AP214",
    defect=(
        "STEP file imports as near-empty document despite well-formed entities; "
        "input: AP214 STEP file (OCCT MANTIS#0033543 pattern) with "
        "MANIFOLD_SOLID_BREP in ADVANCED_BREP_SHAPE_REPRESENTATION (repB) linked "
        "to a geometry-free repA via SHAPE_REPRESENTATION_RELATIONSHIP; "
        "PRODUCT_DEFINITION_SHAPE references repA (empty) not repB (with geometry); "
        "reader traverses only the top-level PRODUCT_DEFINITION chain, finds repA "
        "with no solid, and reports success with empty document; "
        "geometry in repB is never reached; "
        "expected kernel behavior: heal-and-accept; traverse "
        "SHAPE_REPRESENTATION_RELATIONSHIP in both directions; "
        "emit W_UNATTACHED_SHAPE_REPRESENTATION if any representation containing "
        "geometry is unreached after import; "
        "synonyms: STEP file is not imported correctly, reader returns empty document "
        "on valid file, SHAPE_REPRESENTATION_RELATIONSHIP not traversed, "
        "silent-empty import on legitimate STEP file"
    ),
)

# ── A single planar face in a MANIFOLD_SOLID_BREP (the geometry that gets missed) ─
# Tier-3: n_faces_total == 1
origin = f.cartesian_point((0.0, 0.0, 0.0))
dz     = f.direction((0.0, 0.0, 1.0))
dx     = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(origin, dz, dx)
plane  = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d_line = f.direction((1.0, 0.0, 0.0))
vec    = f.vector(d_line, 1.0)
line   = f.line(p0, vec)
edge   = f.edge_curve(v0, v1, line)
oe     = f.oriented_edge(edge, True)
loop   = f.edge_loop([oe])
fob    = f.face_outer_bound(loop)
face   = f.advanced_face([fob], plane)

# CLOSED_SHELL + MANIFOLD_SOLID_BREP (the geometry that gets missed by naive traversal)
shell = f.closed_shell([face])
solid = f.manifold_solid_brep(shell, name="shape_inside_repB")

# ── Representation context for both reps ─────────────────────────────────────
# Use a raw geom context to match the existing file's GLOBAL_UNIT pattern
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3) "
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({plc.ref()})) "
    f"REPRESENTATION_CONTEXT('','3D'))"
)

# ── repA: empty representation (what PRODUCT_DEFINITION_SHAPE sees) ───────────
# BYTE: contains(b'ADVANCED_BREP_SHAPE_REPRESENTATION')
repA = f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('repA',({plc.ref()}),{geom_ctx.ref()})"
)

# ── repB: contains the solid (but NOT directly reachable from PRODUCT chain) ──
# BYTE: contains(b'MANIFOLD_SOLID_BREP') satisfied by solid entity above
repB = f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('repB',({solid.ref()}),{geom_ctx.ref()})"
)

# ── SHAPE_REPRESENTATION_RELATIONSHIP linking repA → repB ─────────────────────
# BYTE: contains(b'SHAPE_REPRESENTATION_RELATIONSHIP')
srr = f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('','linkAB',{repA.ref()},{repB.ref()})"
)

# ── Product chain links to repA (empty) — the defect ──────────────────────────
# Product entities
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
apd     = f._emit_raw(
    f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{app_ctx.ref()})"
)
pctx    = f._emit_raw(f"PRODUCT_CONTEXT('',{app_ctx.ref()},'mechanical')")
pdctx   = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app_ctx.ref()},'design')")
prod    = f._emit_raw(f"PRODUCT('M160','silent empty','',({pctx.ref()}))")
pdf     = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',{prod.ref()})")
pdef    = f._emit_raw(f"PRODUCT_DEFINITION('design','',{pdf.ref()},{pdctx.ref()})")
pds     = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',{pdef.ref()})")

# SDR links to repA — geometry in repB is unreachable without SRR traversal
sdr = f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION({pds.ref()},{repA.ref()})")

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M160.stp")
