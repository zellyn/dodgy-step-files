r"""Le060 — OCCT #1318: STEP writer infinite loop on oversized raw string with indentation prefix.

Catalog claim: STEP file containing a `DESCRIPTIVE_REPRESENTATION_ITEM`
(reachable through the PMI representation chain) whose `description`
attribute is an oversized raw string — greater than 4096 bytes and
containing a leading indentation prefix. Under pre-fix OCCT (≤ 7.9),
`STEPControl_Writer` re-serializing this file enters an infinite loop
in its 72-character line-wrap logic: the indentation-depth-plus-prefix
combined with the raw string length causes zero remaining columns after
the indent, so the wrap advance is 0 and the writer spins forever.
Post-fix (OCCT PR #1318) the writer either drops the indent or splits
the string cleanly.

The input bytes are readable; the defect surfaces only on `write →
reread`. This fixture encodes the input file that would trigger the
pre-fix writer loop.

Source: https://github.com/Open-Cascade-SAS/OCCT/pull/1318
(STEPControl_Writer 72-col wrap fix). B4 wave-8 DEF-CCC.
Confidence: MEDIUM — mechanism fully described; exact trip conditions
depend on OCCT writer's indent policy. LGPL-clean — pattern only, no
upstream bytes copied.

Byte assertions:
  contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')
  contains(b'oversized_writer_trip')
  contains(b'MANIFOLD_SOLID_BREP')
  file_size > 4096

Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le060",
    defect=(
        "OCCT #1318 STEP writer infinite-loop input: "
        "DESCRIPTIVE_REPRESENTATION_ITEM whose description attribute is a raw "
        "string > 4096 bytes with a leading indentation prefix (32 spaces); "
        "pre-fix OCCT STEPControl_Writer's 72-column line-wrap logic sees "
        "zero remaining columns after the indent-depth-plus-prefix, so the "
        "wrap advance is 0 and the writer spins forever; post-fix (OCCT PR "
        "#1318) either drops the indent or splits the string cleanly; the "
        "input bytes ARE readable — defect surfaces only on write→reread; "
        "carrier cube MANIFOLD_SOLID_BREP; DEF-CCC; MANIFOLD_SOLID_BREP IS "
        "model entity — OCC (reading input) yields shape(1)"
    ),
)


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
shell = f._emit_raw(f"CLOSED_SHELL('le060_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('le060_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── DEFECT payload: an oversized raw string with an indentation prefix ───────
# 32-space indentation prefix + a payload of repeated 'A' bytes long enough
# to push the total string past 4096 bytes. The exact trip conditions in the
# OCCT #1318 report are: total content bytes > 4096, leading indent prefix
# consumes enough of the 72-column line-wrap buffer that remaining columns
# after prefix drop to 0, so the writer's advance-pointer never advances.
# Generate programmatically so the fixture is self-explanatory.
INDENT_PREFIX = " " * 32  # 32-space leading indent
PAYLOAD_BODY  = "A" * 4200  # 4200 A's → total > 4232 bytes
OVERSIZED = INDENT_PREFIX + PAYLOAD_BODY

# Escape any single quotes for the Part-21 string literal (STEP string
# escaping doubles the quote); our payload has no quotes, so pass through.
# Byte assertion: contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')
# Byte assertion: contains(b'oversized_writer_trip')
oversized_item = f._emit_raw(
    f"DESCRIPTIVE_REPRESENTATION_ITEM('oversized_writer_trip','{OVERSIZED}')"
)

# ── Tie the oversized item into a property representation so a writer would
# ── attempt to re-emit it (and thereby trigger the loop on pre-fix OCCT).
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('le060_writer_trip',"
    f"'oversized-string writer-loop input — OCCT #1318',"
    f"#9055)"
)
oversized_rep = f._emit_raw(
    f"REPRESENTATION('oversized_rep',(#{oversized_item.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{oversized_rep.eid})"
)
