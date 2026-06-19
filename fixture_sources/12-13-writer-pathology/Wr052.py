"""Wr052 — Writer emits EDGE_CURVE backed by untrimmed LINE.

Catalog claim: a STEP writer emits an EDGE_CURVE whose edge_geometry is
an unbounded LINE entity, without a containing TRIMMED_CURVE or explicit
edge-domain bookkeeping. Receivers cannot determine the edge's
parametric extent from the LINE alone; downstream traversals that ask
'where does this edge end?' get an unbounded answer.

Source: pattern-matched from OCCT bugs/step/bug32817_1, which exercises
the WriteStep path emitting an unbounded line edge. The OCCT regression
is on the WRITER side; we synthesize a *post-pathology* fixture
demonstrating the structural defect for receivers to handle.

LGPL-clean: pattern-matched, no bytes copied from OCCT's test data.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Wr052",
             defect="EDGE_CURVE references unbounded LINE without TRIMMED_CURVE wrap")

# Two vertices, but the EDGE_CURVE's curve geometry is an unbounded LINE,
# not a TRIMMED_CURVE(LINE, [t0, t1]).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)

d = f.direction((0.0, 1.0, 0.0))
vec = f.vector(d, 1.0)
# LINE is intrinsically unbounded; EDGE_CURVE referencing it directly is
# the writer-pathology pattern we're modelling.
untrimmed_line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, untrimmed_line)

# Carrier plane and minimal face so the fixture is consumable.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
