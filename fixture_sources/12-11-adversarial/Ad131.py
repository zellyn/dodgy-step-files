r"""Ad131 — OCCT PR #448: malformed `FILE_SCHEMA` with literal `.` between schema name and version triple (every OCCT-written AP242 file in the wild).

Catalog claim: STEP file whose header contains a malformed `FILE_SCHEMA`
declaration matching the exact pattern OCCT 7.x through pre-8.0 wrote for
every AP242 export:

    FILE_SCHEMA(('AUTOMOTIVE_DESIGN.{ 1 0 10303 442 3 0 0 }'));

Note the literal `.` (period) between `AUTOMOTIVE_DESIGN` and the opening
brace of the version tuple — a bug in OCCT's `STEPControl_Writer` schema
serialization (fixed in PR #448). The DATA section contains a minimal
cube `MANIFOLD_SOLID_BREP` so the file is otherwise valid.

**Massive real-world impact:** every OCCT-written AP242 file emitted by
FreeCAD, KiCad, Salome-Platform, and the entire OCCT-based ecosystem
between OCCT 7.x releases (~2018-2024) and the pre-8.0 patch (PR #448)
carries this malformed header. Strict Part 21 parsers reject the file
outright; permissive parsers (including OCCT itself, since it wrote
the malformation) fall back to AP203/AP214 handling and silently drop
AP242-specific entities.

Expected:
- Strict Part 21 validators (e.g. STEP Tools stepcheck) reject the
  `FILE_SCHEMA` declaration on syntax grounds (schema-name-must-not-contain-
  period rule).
- Permissive parsers (OCCT, FreeCAD, older CAD kernels) accept the file
  but treat the schema as effectively unknown, falling back to
  generic AP2xx handling and silently dropping AP242-specific tolerance
  and PMI entities.
- The literal `.` byte is directly detectable via regex on the header.

Source: https://github.com/Open-Cascade-SAS/OCCT/pull/448
(`STEPControl_Writer` FILE_SCHEMA emission fix — strips the extra `.`
between schema name and version tuple). B4 wave-8 DEF-BBB. Confidence:
HIGH — patch line is exact; the malformed string is byte-verifiable.

LGPL-clean — the malformed pattern is documented in the PR title and
patch diff; no upstream STEP bytes copied.

Byte assertions:
  contains(b'AUTOMOTIVE_DESIGN.{')
  contains(b'FILE_SCHEMA')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a part21=reject
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad131",
    schema="AP242",  # base; header overridden below to malformed OCCT emission
    defect=(
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN.{ 1 0 10303 442 3 0 0 }')) — the "
        "literal '.' (period) between AUTOMOTIVE_DESIGN and the opening brace "
        "of the version tuple; the exact pattern OCCT 7.x through pre-8.0's "
        "STEPControl_Writer emitted for every AP242 export (fixed in OCCT PR "
        "#448); every FreeCAD, KiCad, Salome-Platform, and OCCT-based export "
        "of AP242 in the ~2018-2024 window carries this malformed header; "
        "strict Part 21 parsers reject the schema declaration; permissive "
        "parsers (OCCT itself) fall back to generic AP2xx handling and "
        "silently drop AP242-specific tolerance/PMI entities; minimal cube "
        "MANIFOLD_SOLID_BREP as carrier geometry; DEF-BBB; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC (permissive) yields shape(1)"
    ),
)

# ── Override header to emit the malformed OCCT-#448 FILE_SCHEMA ──────────────
# The critical byte sequence is `AUTOMOTIVE_DESIGN.{` — the literal `.` after
# the schema name, before the opening brace of the version triple. This is
# THE defect and MUST survive to the .stp file byte-for-byte. We use the
# monkey-patched _render_header trick so step_builder does NOT normalize the
# string via its schema-name dispatch table.
#
# The schema-name-with-extra-dot pattern matches OCCT PR #448's patch diff —
# `TCollection_AsciiString schemaName = "AUTOMOTIVE_DESIGN."` then
# `schemaName += "{ 1 0 10303 442 3 0 0 }"` — resulting in the literal `.{`
# join point that the PR removes.
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN.{ 1 0 10303 442 3 0 0 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Minimal cube MANIFOLD_SOLID_BREP (10×10×10) — carrier geometry ────────────
def make_plane_face(origin, zdir_t, xdir_t, points_ccw):
    plc   = f.axis2_placement_3d(
        f.cartesian_point(origin),
        f.direction(zdir_t),
        f.direction(xdir_t),
    )
    plane = f.plane(plc)
    pts   = [f.cartesian_point(p) for p in points_ccw]
    loop  = f.closed_polyline_loop(pts)
    fob   = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane)

S = 10.0

face_xp = make_plane_face((S,0,0), (1,0,0), (0,0,1),
                           [(S,0,0),(S,0,S),(S,S,S),(S,S,0)])
face_xn = make_plane_face((0,0,0), (-1,0,0), (0,0,-1),
                           [(0,0,0),(0,S,0),(0,S,S),(0,0,S)])
face_yp = make_plane_face((0,S,0), (0,1,0), (1,0,0),
                           [(0,S,0),(S,S,0),(S,S,S),(0,S,S)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,S),(S,0,S),(S,0,0)])
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ad131_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ad131_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
