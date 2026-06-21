"""M054 — FACETED_BREP linked to OPEN_SHELL (schema-illegal).

Catalog claim: FACETED_BREP is required by the schema to reference a
CLOSED_SHELL. Some producers emit it pointing at an OPEN_SHELL. OCCT only
handles the closed case, so loading aborts.

Reproducer recipe: #N = FACETED_BREP('', #M); where #M = OPEN_SHELL('', (..));

Byte assertions:
  contains(b'FACETED_BREP')
  contains(b'OPEN_SHELL')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M054",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing FACETED_BREP referencing OPEN_SHELL — "
        "schema-illegal: FACETED_BREP must reference CLOSED_SHELL; "
        "input: AP242 STEP file where FACETED_BREP points at an OPEN_SHELL instead "
        "of the schema-required CLOSED_SHELL; "
        "ISO 10303-42 §B.2 / AP242 schema: FACETED_BREP.outer is typed "
        "CLOSED_SHELL — no relaxation permitted; "
        "OCCT forum: loading aborts silently on open-shell FACETED_BREP; "
        "kernel must reject with a precise diagnostic; optionally heal by promoting "
        "the shell to CLOSED_SHELL if topology actually closes; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: FACETED_BREP linked to OPEN_SHELL, schema-illegal faceted brep, "
        "faceted brep needs closed shell, schema-version vs entity-vocabulary disagreement"
    ),
)

# ── Vertex geometry for a simple triangle (3-point open face) ─────────────────
vp0 = f._emit_raw("CARTESIAN_POINT('v0',(0.,0.,0.))")
vp1 = f._emit_raw("CARTESIAN_POINT('v1',(10.,0.,0.))")
vp2 = f._emit_raw("CARTESIAN_POINT('v2',(0.,10.,0.))")

vertex0 = f._emit_raw(f"VERTEX_POINT('vx0',#{vp0.eid})")
vertex1 = f._emit_raw(f"VERTEX_POINT('vx1',#{vp1.eid})")
vertex2 = f._emit_raw(f"VERTEX_POINT('vx2',#{vp2.eid})")

# ── Edges for the triangle ────────────────────────────────────────────────────
dir01 = f._emit_raw("DIRECTION('d01',(1.,0.,0.))")
vec01 = f._emit_raw(f"VECTOR(#{dir01.eid},10.)")
line01 = f._emit_raw(f"LINE('l01',#{vp0.eid},#{vec01.eid})")
ec01 = f._emit_raw(
    f"EDGE_CURVE('e01',#{vertex0.eid},#{vertex1.eid},#{line01.eid},.T.)"
)

dir12 = f._emit_raw("DIRECTION('d12',(-1.,1.,0.))")
vec12 = f._emit_raw(f"VECTOR(#{dir12.eid},14.142)")
line12 = f._emit_raw(f"LINE('l12',#{vp1.eid},#{vec12.eid})")
ec12 = f._emit_raw(
    f"EDGE_CURVE('e12',#{vertex1.eid},#{vertex2.eid},#{line12.eid},.T.)"
)

dir20 = f._emit_raw("DIRECTION('d20',(0.,-1.,0.))")
vec20 = f._emit_raw(f"VECTOR(#{dir20.eid},10.)")
line20 = f._emit_raw(f"LINE('l20',#{vp2.eid},#{vec20.eid})")
ec20 = f._emit_raw(
    f"EDGE_CURVE('e20',#{vertex2.eid},#{vertex0.eid},#{line20.eid},.T.)"
)

oe01 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec01.eid},.T.)")
oe12 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec12.eid},.T.)")
oe20 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec20.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe01.eid},#{oe12.eid},#{oe20.eid}))")

# ── Plane for the triangle face ───────────────────────────────────────────────
plane_origin = f._emit_raw("CARTESIAN_POINT('plane_origin',(0.,0.,0.))")
plane_dir_z = f._emit_raw("DIRECTION('plane_normal',(0.,0.,1.))")
plane_dir_x = f._emit_raw("DIRECTION('plane_ref',(1.,0.,0.))")
plane_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_placement',"
    f"#{plane_origin.eid},#{plane_dir_z.eid},#{plane_dir_x.eid})"
)
plane = f._emit_raw(f"PLANE('tri_plane',#{plane_placement.eid})")
face_bound = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face = f._emit_raw(
    f"ADVANCED_FACE('tri_face',(#{face_bound.eid}),#{plane.eid},.T.)"
)

# ── OPEN_SHELL — the schema-illegal target for FACETED_BREP ──────────────────
# Byte assertion: contains(b'OPEN_SHELL')
open_shell = f._emit_raw(f"OPEN_SHELL('open_shell_illegal',(#{face.eid}))")

# ── FACETED_BREP referencing OPEN_SHELL instead of CLOSED_SHELL ──────────────
# Byte assertion: contains(b'FACETED_BREP')
faceted = f._emit_raw(f"FACETED_BREP('faceted_brep_open_shell',#{open_shell.eid})")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('faceted-brep-linked-to-open-shell',"
    f"(#{faceted.eid},#{open_shell.eid},#{plane_placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M054.stp")
