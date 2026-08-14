"""Ad139 — Malformed VECTOR (null orientation-direction) on a live edge → uninitialized-pointer risk.

Catalog claim (input pattern): a VECTOR entity supplies `$` (null) for its
mandatory `orientation` DIRECTION reference — `VECTOR('null_dir_vector',$,...)`.
Here the VECTOR is the direction of a LINE that is the 3D curve of a real
EDGE_CURVE in a transferred solid, so a reader actually *constructs* the VECTOR.
A reader that allocates the direction pointer while building the VECTOR and
dereferences it without checking that the orientation slot resolved to a real
DIRECTION accesses an uninitialized pointer. Pattern-mined from ZDI-22-1467 /
CVE-2022-43609 (IronCAD STP importer: "When parsing the VECTOR element, the
process does not properly initialize a pointer prior to accessing it" —
uninitialized-pointer RCE). Independent, non-OCCT commercial reader; pattern
only, no bytes copied.

A robust reader validates that the orientation slot holds a DIRECTION before
using it, and drops/rejects the malformed VECTOR rather than dereferencing an
uninitialized direction pointer.

Byte assertions:
  contains(b"VECTOR('null_dir_vector',$,")

OCC behavior: signal(11) — both heal modes SIGSEGV while constructing the
null-orientation VECTOR for the seam edge. part21 accepts ($ is a valid null
token) and the structural linter passes (null in a mandatory scalar-reference
slot is not one of its 5 checks), so this crash is currently unrefusable
pre-transfer. gmsh count is CI-Linux-authoritative if it diverges.
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad139",
    defect=(
        "a VECTOR entity supplies $ (null) for its mandatory orientation "
        "DIRECTION reference and is the direction of a LINE used as the 3D "
        "curve of a real EDGE_CURVE in a transferred solid, so the reader "
        "constructs the VECTOR on a live path; a reader that allocates the "
        "direction pointer while building the VECTOR and dereferences it "
        "without checking the orientation slot resolved accesses an "
        "uninitialized pointer (ZDI-22-1467 / CVE-2022-43609, IronCAD STP "
        "importer); expected robust behavior: validate that the orientation "
        "slot holds a DIRECTION before use, drop or reject the malformed "
        "VECTOR, never dereference an uninitialized direction pointer; "
        "synonyms: null orientation in VECTOR, VECTOR missing direction, "
        "uninitialized pointer parsing VECTOR, VECTOR null mandatory "
        "reference; the null-orientation VECTOR is the defect carrier"
    ),
)

# Clean truncated-cone solid (as in M202) but the seam edge's LINE gets a
# malformed VECTOR (null orientation) as its direction.
semi_angle, base_r, h_face = 0.4, 1.0, 1.0
apex_r = base_r - h_face * _math.tan(semi_angle)
cone_surf = f.conical_surface(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    base_r, semi_angle)
pt_base = f.cartesian_point((base_r, 0.0, 0.0))
pt_apex = f.cartesian_point((apex_r, 0.0, h_face))
v_base, v_apex = f.vertex_point(pt_base), f.vertex_point(pt_apex)
base_edge = f.edge_curve(v_base, v_base, f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))), base_r))
apex_edge = f.edge_curve(v_apex, v_apex, f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, h_face)),
                         f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))), apex_r))
# DEFECT: the seam LINE's direction is a VECTOR with null orientation.
seam_len = _math.sqrt((apex_r - base_r) ** 2 + h_face ** 2)
bad_vec = f._emit_raw(f"VECTOR('null_dir_vector',$,{seam_len})")
seam_line = f._emit_raw(f"LINE('',#{pt_base.eid},#{bad_vec.eid})")
seam_edge = f.edge_curve(v_base, v_apex, seam_line)
face = f.advanced_face([f.face_outer_bound(f.edge_loop([
    f.oriented_edge(seam_edge, True), f.oriented_edge(apex_edge, True),
    f.oriented_edge(seam_edge, False), f.oriented_edge(base_edge, False)]))], cone_surf)
f.add_product_chain(f.manifold_solid_brep(f.closed_shell([face])), mode="brep_shape")
