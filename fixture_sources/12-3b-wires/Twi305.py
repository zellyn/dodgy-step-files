"""Twi305 — Apex-bridging edge already PRESENT at the cone singularity
(exactly one, correctly positioned, not missing, not duplicated): the
"dgnr" (sitting-on-the-singularity) input configuration that
ShapeFix_Wire::FixDegenerated's DONE2/replace branch processes, as
distinct from Twi021's "lack" (DONE1/insert, no edge at all bridges the
apex) and Twi031's duplicate (two edges both at the apex, dedup)
(tkshh-wire-missing-or-bad-degenerated-edge, PARTIAL, subvariant 2: "edge
sitting on the singularity that must become/be replaced by a proper
degenerated edge (dgnr, DONE2)").

Catalog claim: ShapeAnalysis_Wire::CheckDegenerated (ShapeAnalysis_Wire.cxx
:806-988) walks the wire looking for the singular row; when it finds a
GAP (no edge occupies the singularity's wire slot) it reports "lack"
(DONE1: ShapeFix_Wire::FixDegenerated INSERTS a new 2D-line degenerated
edge, ShapeFix_Wire.cxx:1725-1735 -- Twi021's exact input). When it
instead finds an EDGE ALREADY OCCUPYING that wire slot, sitting exactly at
the singularity, it reports "dgnr" (DONE2: FixDegenerated REPLACES the
existing edge with a freshly-built canonical 2D-line degenerated edge,
ShapeFix_Wire.cxx:1736-1760) -- a structurally different code path from
DONE1 even though (for a correctly-formed single apex edge, as here) the
replacement is a near no-op in the final geometry. This fixture supplies
exactly the "dgnr" input shape: a SINGLE apex-bridging EDGE_CURVE, present
in the wire (not missing like Twi021, not duplicated like Twi031),
occupying the exact singular position (both vertices identical, at the
true apex (0,0,0)) with zero-length LINE geometry -- so CheckDegenerated's
traversal encounters an edge to inspect/replace at that slot rather than a
gap to insert into.

Mechanism: CONICAL_SURFACE (apex at origin, semi-angle 30 deg, axis +Z),
same skeleton as Twi021/Twi031. FOUR declared edges (vs. Twi021's THREE
and Twi031's FIVE): two lateral LINE edges (apex -> base_0, base_pi ->
apex, same vertex object 'apex' reused at both lateral edges' apex ends),
one base CIRCLE arc, and exactly ONE apex-bridging EDGE_CURVE
('single_apex_degenerate_edge': apex -> apex, same VERTEX_POINT object at
both ends, zero-length LINE) -- present, singular, correctly positioned.
Live-verified: reads to a 4-edge healed wire (matching Twi021/Twi031's own
converged output) with exactly one edge Degenerated=True post-read,
confirming the singularity bridge survives as a single, valid, canonical
degenerate edge. EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE,
OPEN_SHELL; never orphaned.

Byte assertions:
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 4
  - contains(b'single_apex_degenerate_edge')

Tier-3 assertions:
  - face[0].surface_type == "cone"
  - n_edges_total >= 4
  - n_vertices_total >= 6
  - brepcheck.valid == True

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)

Live finding (honest, not overclaimed): a direct BRep_Tool::Degenerated_s()
probe on the resulting shape shows exactly ONE of the 4 read-back edges
comes back True (the apex bridge), matching both Twi021's and Twi031's own
converged post-heal shape exactly. This is expected for a well-formed
input to the "dgnr" path (whose defining characteristic is what INPUT
STRUCTURE it presents to CheckDegenerated -- an edge occupying the
singular slot vs. a gap -- not a different final geometry); an earlier
near-tolerance variant of this fixture (apex vertices offset ~1e-6/1e-7
from the true apex rather than bit-identical) was live-tested and found to
NOT trigger the replace path at all -- it instead left the imperfect small
edge in place UNTOUCHED and additionally inserted a second, fresh
degenerate edge (5 edges total, "lack" behavior firing alongside it),
which is why this fixture uses the bit-identical-vertex construction
instead.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi305",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE (apex at "
        "origin, semi-angle 30deg, axis +Z); FACE_OUTER_BOUND references a "
        "4-edge EDGE_LOOP: single_apex_degenerate_edge (apex -> apex, SAME "
        "VERTEX_POINT object at both ends, zero-length LINE -- present, "
        "singular, correctly positioned, NOT missing like Twi021 and NOT "
        "duplicated like Twi031), lat_L (apex -> base_0), base_arc "
        "(base_0 -> base_pi), lat_R (base_pi -> apex); the apex-bridging "
        "edge occupying its wire slot (rather than a gap) is what forces "
        "ShapeFix_Wire::FixDegenerated's dgnr/DONE2 replace branch rather "
        "than the lack/DONE1 insert branch; EDGE_LOOP IS wired into "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)

SEMI_ANGLE_RAD = math.radians(30.0)
HEIGHT = 2.0
BASE_R = HEIGHT * math.tan(SEMI_ANGLE_RAD)

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f._emit_raw(f"CONICAL_SURFACE('',#{cone_plc.eid},0.0,{SEMI_ANGLE_RAD:.10f})")

# ── SAME vertex object at the exact apex, reused everywhere the wire touches
#    the singularity — this is what makes the bridge "present and correct",
#    not "near but not identical" (which live-tested as behaving like lack).
v_apex    = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_base_0  = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))
v_base_pi = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))

# ── single_apex_degenerate_edge: apex -> apex, zero-length LINE ─────────────
deg_dir  = f.direction((1.0, 0.0, 0.0))
deg_vec  = f.vector(deg_dir, 0.0)
deg_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)), deg_vec)
ec_bridge = f._emit_raw(
    f"EDGE_CURVE('single_apex_degenerate_edge',#{v_apex.eid},#{v_apex.eid},#{deg_line.eid},.T.)"
)
oe_bridge = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bridge.eid},.T.)")

# ── Left lateral: apex -> base_0 ─────────────────────────────────────────────
_mag = math.hypot(BASE_R, HEIGHT)
lat_L_dir = f.direction((BASE_R / _mag, 0.0, HEIGHT / _mag))
lat_L_vec = f.vector(lat_L_dir, _mag)
lat_L_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), lat_L_vec)
edge_lat_L = f.edge_curve(v_apex, v_base_0, lat_L_ln)
oe_lat_L   = f.oriented_edge(edge_lat_L, True)

# ── Base semi-circle: base_0 -> base_pi ──────────────────────────────────────
base_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, HEIGHT)), cone_zdir, cone_xdir)
base_circ = f._emit_raw(f"CIRCLE('',#{base_plc.eid},{BASE_R:.10f})")
base_arc_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_0.eid},#{v_base_pi.eid},#{base_circ.eid},.T.)"
)
oe_base = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{base_arc_edge.eid},.T.)")

# ── Right lateral: base_pi -> apex ───────────────────────────────────────────
lat_R_dir = f.direction((-BASE_R / _mag, 0.0, HEIGHT / _mag))
lat_R_vec = f.vector(lat_R_dir, _mag)
lat_R_ln  = f.line(f.cartesian_point((-BASE_R, 0.0, HEIGHT)), lat_R_vec)
edge_lat_R = f.edge_curve(v_base_pi, v_apex, lat_R_ln)
oe_lat_R   = f.oriented_edge(edge_lat_R, True)

# ── EDGE_LOOP: apex -(lat_L)-> base_0 -(base_arc)-> base_pi -(lat_R)-> apex ──
#    -(bridge)-> apex (closes) ────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_lat_L.eid},#{oe_base.eid},#{oe_lat_R.eid},#{oe_bridge.eid}))"
)

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cone_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
