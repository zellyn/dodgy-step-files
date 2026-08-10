# Implementer's roadmap

**Audience: you are writing a CAD kernel and need to survive real-world STEP files.** This document is the corpus re-cut along the axis you actually work on.

The catalog ([`STEP_PROBLEM_CATALOG.md`](STEP_PROBLEM_CATALOG.md)) is organised one entry per broken file, which is right for auditing and wrong for building — 3335 entries do not tell you where to start. This page inverts it into the **169 distinct repair mechanisms** those files exercise, ordered so the failures that hurt users most come first, each pointing at the fixtures that prove you got it right (620 fixtures cited).

> **Generated file — do not edit.** `python3 occt-coverage/make_roadmap.py`.
> Everything below is joined from `occt-coverage/*/problems.json` and the catalog's CI-verified `Expected validation` lines. No hand-entered claims.

## How to use this

1. Work down the tiers. Inside a tier the order is by blast radius, not importance-by-opinion.
2. For each mechanism, read the cited fixtures' **`Expected kernel behavior`** field in the catalog. That field — not `Expected validation` — is the specification of what a *correct* kernel should do. `Expected validation` records what OCCT 7.8.1 was measured doing, which includes its bugs.
3. Run your kernel over the cited `.stp` files and compare.

## The one caveat that matters

The tiering below is derived from **observed reference-engine behaviour**, not from a judgement about correctness. In particular `empty` — the file parsed but no shape came back — is sometimes exactly right (a garbage file *should* yield nothing) and sometimes the worst possible outcome (a valid solid silently vanished). The corpus cannot tell these apart from the token alone; the per-fixture `Expected kernel behavior` field can. Treat T1 as *"look here first"*, not as *"these are all bugs"*.

## Start here: silent total geometry loss

**106 fixtures hand the reader a complete, connected B-rep and get an empty shape back.** Not a partial result, not a repaired face — nothing, and no error. This is the worst outcome in the corpus, because the import reports success and the user's geometry is simply gone.

These are separated from the general `empty` population on purpose. `empty` alone is ambiguous — a garbage file *should* yield nothing. Each fixture here was checked to have an `ADVANCED_FACE` **actually referenced by a shell** (not merely present in the file), a `SHAPE_DEFINITION_REPRESENTATION` root, and a solid or surface-model wrapper. There was something to build.

**What the concentration tells you:** {'Gp': 58, 'Gn': 43, 'Gs': 1, 'M': 1, 'Pf': 1, 'Tfa': 1, 'Tsh': 1} — by ID prefix. These are overwhelmingly *curve*-level defects (pcurves and NURBS curves), not shell- or solid-level ones. So the lesson is that in this reference engine **a single bad curve on a face escalates all the way to total loss of the model**, rather than degrading to a dropped edge or a repaired approximation. If your kernel takes the same path, decide deliberately whether that is the behaviour you want — and if it is, at least emit a diagnostic.

**Test against:** `Gn001`, `Gn009`, `Gn010`, `Gn013`, `Gn014`, `Gn017`, `Gn018`, `Gn019`, `Gn025`, `Gn026`, `Gn031`, `Gn032`, `Gn033`, `Gn034`, `Gn035`, `Gn037`, `Gn038`, `Gn039`, `Gn046`, `Gn047` …and 86 more

## Cheapest crash defence: five checks, before any geometry

**163 of the 177 crashing fixtures (92%) are refusable before a single geometric entity is constructed** — by five checks that need nothing but the file and a schema table:

1. **Wrong type in a reference slot** (103 fixtures) — the single biggest one. Every attribute that names another entity has a declared type; these files put something else there. `LINE.dir` is declared `VECTOR` and points at a `DIRECTION`; `ADVANCED_FACE.bounds` is declared `FACE_BOUND` and holds a raw `EDGE_LOOP`; `EDGE_LOOP.edge_list` holds an `EDGE_CURVE` with no `ORIENTED_EDGE` wrapper. Repairing the reference makes the file load — verified individually on 26 of the `LINE.dir` cases, so this is cause, not correlation. Checking **all** reference slots rather than one flags 56% of crashers against **0.9%** of non-crashers.
2. **Wrong argument count** (22 fixtures), detailed below.
3. **Empty aggregate where the schema requires one or more** (21 fixtures) — `SHELL_BASED_SURFACE_MODEL('',())`, `TESSELLATED_SHELL('',(),$)`, `SURFACE_CURVE('',#33,(),.PCURVE_S1.)`. These crash in the *reference-graph walk*, before conversion is even attempted, which is why no amount of care in the geometry code would catch them. Present in 1.6% of non-crashing fixtures, so it is a strong signal rather than a certainty.
4. **Inline entity instance in an argument** (28 fixtures) — `LINE('',#100,VECTOR('',(1,0,0),1.0))`. Entity instances must be top-level `#N=` statements; a typed value inside an argument is only legal for defined types such as measures, never for entity types. The parser cannot bind the inline construct, so the attribute silently becomes null. Present in 0.2% of non-crashing fixtures — each a deliberate fixture of this very construct.
5. **Wrong argument count on core geometry entities** (10 fixtures) — `VECTOR(#2,100.)`: the name omitted, two arguments where three are declared, so every later value sits in the wrong slot. Same positional mechanism as the B-spline case in check 2, on the small entities.

None of the five needs a kernel, and each produces a diagnostic naming the entity and what was wrong with it — a far better outcome than a segfault, and better than the silent empty shape the other sections describe. Note where check 3 fires: in the reference-graph walk, *before* conversion starts. Robustness in the geometry code cannot reach it.

### The argument-count check

Of the fixtures containing a `B_SPLINE_CURVE_WITH_KNOTS` or `B_SPLINE_SURFACE_WITH_KNOTS`:

| argument count vs. schema | crashes | rate |
|---|---|---|
| **deviates** | 22 / 23 | **96%** |
| correct | 14 / 420 | 3% |

A file that gives one of these entities the wrong *number* of arguments crashes this reference engine almost every time; a file that gets the count right almost never does. Nothing else about the entity predicts a crash nearly as well — a flat control-point list, knot multiplicities written as reals, and a control-point count that contradicts the multiplicities were each tested in isolation against a known-good surface, and **all three load fine**.

The reason is positional. These entities are read by slot, so omitting an attribute does not produce a missing value — it shifts every later argument one position left, and the reader ends up taking a list where the schema promised it an enum. It then uses the result without checking, and dereferences null.

**Where it lands varies; the input pattern does not.** Traced crash sites include the vector constructor, the B-spline surface constructor, and the face translator — whichever converter happens to reach the malformed entity first. Treating these as three separate bugs to null-check individually is the expensive path.

**The cheap path:** validate argument counts against the schema *at parse time*. That is a table lookup and a comparison. It rejects these files with a precise, actionable diagnostic naming the entity and the expected count, and no converter ever sees them. Downstream null-checking, by contrast, has to be repeated at every construction site and still produces a worse message.

**Scope, measured rather than assumed:** this is a *B-spline* effect, not a universal law. Learning each entity type's arity from the corpus (the modal count over 71 types with enough instances to be confident) and asking whether *any* deviation predicts a crash gives 24% against a 6% base rate — real signal, but four-fold rather than thirty-fold. A wrong count on a `PLANE` or a `VECTOR` mostly does not reach a null dereference. So implement the check everywhere, because it is nearly free and catches malformed files early — but expect the crashes it prevents to be concentrated in the entities with long, heterogeneous argument lists, where a shift silently changes a value's type.

Honest caveat: 1 deviating fixture — `Gn169` — does not crash, so the count is a very strong predictor rather than a law. The correlation was measured across the whole corpus; only some of the crashes were traced to a call site individually.

**Test against** — everything either check refuses. Wrong count: `Gn043`, `Gn105`, `Gn107`, `Gn173`, `Gp056`, `Gp058`, `Gp060`, `Gp101`, `Gp102`, `Gp104`, `Gs134`, `Gs137`, `Gs138`, `Tfa141`, `Tfa144`, `Tfa172`, `Tfa174`, `Tfa175`, `Tfa180`, `Tfa187`, `Twi227`, `Twi230`. Wrong type: `Ad015`, `Ad050`, `Ad134`, `Gb002`, `Gb003`, `Gn003`, `Gn055`, `Gn058`, `Gp001`, `Gp019`, `Gp042`, `Gp046`, `Gp047`, `Gp049`, `Gp059`, `Gp096`, `Gp098`, `Gp099`, `Gp112`, `Gp113` …and 121 more. A kernel that refuses all of these at parse time gives up nothing — every one is a file no correct reader should accept.

## What this page does *not* cover

**2531 of the 2531 STEP fixtures (100%) carry a written `Expected kernel behavior`.** The other 0 are real fixtures with real, CI-verified assertions — they are good *tests* — but they do not state what a correct kernel should do, so they teach an implementer nothing on their own. They are marked † below. Most of that remainder is deliberate: an entry whose bytes were found to contradict its own title is left unspecced ON PURPOSE, because a specification written on a disproved claim would propagate the error rather than fix it.

It cites **620 of the 2531 STEP fixtures (24%)**. The other 1911 are real, CI-verified fixtures that simply have not been linked to a named repair mechanism yet — they are reachable through the catalog and [`browse/`](browse/), just not from here. So this is a *starting* map, not an exhaustive one: finishing a tier does not mean you have handled everything the corpus knows about. Growing the linkage is tracked in `occt-coverage/`.

> Of the two, **linkage is currently the larger gap** (1911 fixtures vs 0).

## Tier summary

| tier | meaning | mechanisms |
|---|---|---:|
| `T0` | at least one fixture **aborts** the reference engine — a kernel must never do this | 31 |
| `T1` | most fixtures parse but yield **no geometry** — silent loss, check these early | 6 |
| `T2` | the file loads; the question is whether the repair was **faithful** | 132 |


## T0 crash-exposing

### `tkshh-face-small-area-wire`

*TKShHealing* · 13 fixtures · observed: loads×7, crash×5, empty×1 · **13/13 carry a written spec** · corpus coverage: COVERED

A face contains a wire that encloses (near-)zero area in UV -- a sliver loop, a collapsed rectangle of width ~1e-4, or a micro loop far below model tolerance. Such wires carry no usable material information and corrupt downstream classification. OCCT (ShapeAnalysis_Wire::CheckSmallArea inside ShapeFix_Face::FixSmallAreaWire) detects them and rebuilds the face without them; if every wire of the…

**Test against:** `Tfa208`, `Tfa123`, `Twi045`, `Tfa130`, `Tfa093`, `Tfa077`, `Twi044`, `Twi079`, `Tsh089`, `Tsh106`, `Tsh113`, `Tsh124` …and 1 more

### `tkshh-shell-inconsistent-face-orientation`

*TKShHealing* · 13 fixtures · observed: loads×8, crash×5 · **13/13 carry a written spec** · corpus coverage: COVERED

A shell's constituent faces have inconsistent orientation relative to each other -- some faces are flipped relative to a globally-consistent (outward-facing) convention, possibly combined with exact-duplicate faces, edges shared by three or more faces (non-manifold connectivity), or a mismatch between the shell's cached Closed flag and its actual free-edge state. OCCT repairs this by…

**Test against:** `Tsh070`, `Tsh085`, `Tsh090`, `Tsh094`, `Tsh100`, `Tsh104`, `Tsh112`, `Tsh122`, `Tsh128`, `Tsh132`, `Tsh139`, `Tsh144` …and 1 more

### `tkshh-edge-3d-2d-parameterization-mismatch`

*TKShHealing* · 23 fixtures · observed: loads×10, empty×10, crash×3 · **23/23 carry a written spec** · corpus coverage: COVERED

An edge's 3D curve and its pcurve disagree as parameterizations: at the same parameter the 3D point and the surface-evaluated pcurve point diverge beyond tolerance (SameParameter violation), the declared parameter ranges differ while SameRange is asserted, the pcurve's range is invalid for its surface domain, or the two representations drift apart mid-edge while agreeing at the ends.

**Test against:** `Gp022`, `Twi082`, `Twi070`, `Twi133`, `Twi246`, `Gp050`, `Gp073`, `Twi040`, `Gp045`, `Gp052`, `Gp059`, `Gp066` …and 11 more

### `tkshh-wire-lacking-edge-2d`

*TKShHealing* · 11 fixtures · observed: empty×6, crash×3, loads×2 · **11/11 carry a written spec** · corpus coverage: COVERED

Two consecutive edges share a vertex in 3D (topologically connected) but their pcurves are disconnected in the face's UV space - a boundary segment is missing in parameter space (classically at a seam or degenerated boundary of the surface). The wire cannot bound a UV region until an edge is inserted or the pcurves are deformed.

**Test against:** `Twi036`, `Twi067`, `Twi118`, `Twi131`, `Twi146`, `Twi150`, `Twi160`, `Twi173`, `Twi187`, `Twi211`, `Twi220`

### `tkshh-edge-missing-pcurve`

*TKShHealing* · 8 fixtures · observed: loads×4, crash×3, empty×1 · **8/8 carry a written spec** · corpus coverage: COVERED

An edge used in a face's wire has no pcurve on that face's surface (only a 3D curve). The 2D representation must be computed by projecting the 3D curve onto the surface (with special handling for seams and singular rows).

**Test against:** `Gp001`, `Gp035`, `Gp042`, `Gp019`, `Gp048`, `Gp076`, `Twi047`, `Gp012`

### `tkshh-wire-adjacent-edges-intersect`

*TKShHealing* · 11 fixtures · observed: loads×5, empty×4, crash×2 · **11/11 carry a written spec** · corpus coverage: COVERED

Two consecutive edges of a wire cross each other in the face's parameter space at a point away from their shared vertex - the corner region self-overlaps. Repair trims the edges back to the intersection point, moves the shared vertex there, or absorbs the crossing in vertex/edge tolerance.

**Test against:** `Twi106`, `Twi130`, `Twi137`, `Twi152`, `Twi162`, `Twi167`, `Twi176`, `Twi194`, `Twi204`, `Twi212`, `Twi219`

### `tkshh-edge-curve-inconsistent-with-vertex-removed`

*TKShHealing* · 10 fixtures · observed: loads×5, empty×3, crash×2 · **10/10 carry a written spec** · corpus coverage: COVERED

An edge carries a 3D curve or a pcurve whose endpoint(s), when evaluated, land farther from the edge's actual vertex position than the vertex tolerance allows (i.e., the curve representation itself is stale, wrong, or was computed for a different placement) — or a pcurve's declared parameter range does not correspond to a valid sub-domain of its curve (exceeds the curve's bounds or wraps past…

**Test against:** `Gp064`, `Gp136`, `Gp047`, `Gp058`, `Gp086`, `Gp103`, `Gp108`, `Gp123`, `Gp151`, `Gp179`

### `tkshh-edge-self-intersecting`

*TKShHealing* · 10 fixtures · observed: loads×4, empty×4, crash×2 · **10/10 carry a written spec** · corpus coverage: COVERED

A single edge's curve crosses itself: the pcurve (and correspondingly the 3D curve) forms a loop or lemniscate within the edge's parameter range, so the edge cannot bound a simple region.

**Test against:** `Twi103`, `Twi129`, `Twi141`, `Twi151`, `Twi166`, `Twi172`, `Twi188`, `Twi206`, `Twi269`, `Gn024`

### `tkshh-seam-pcurves-swapped`

*TKShHealing* · 10 fixtures · observed: loads×5, empty×3, crash×2 · **10/10 carry a written spec** · corpus coverage: COVERED

A seam edge on a periodic surface carries two pcurves (one per side of the seam), but they are assigned to the wrong sides - the FORWARD-orientation pcurve is the one that belongs to the REVERSED side and vice versa (or both slots carry the same curve), breaking UV closure by one period.

**Test against:** `Twi022`, `Twi071`, `Twi121`, `Twi144`, `Twi154`, `Twi183`, `Twi201`, `Twi217`, `Twi268`, `Gp011`

### `tkshh-face-intersecting-wires`

*TKShHealing* · 9 fixtures · observed: loads×4, empty×3, crash×2 · **9/9 carry a written spec** · corpus coverage: COVERED

Two DIFFERENT wires of the same face intersect each other in UV: a hole boundary crosses the outer boundary, two hole wires cross, or wires share a collinear segment. Holes cut by intersecting wires make containment/orientation undecidable. OCCT's ShapeFix_IntersectionTool::FixIntersectingWires intersects all edge pairs across wire pairs and repairs exactly like the self-intersection case:…

**Test against:** `Tfa039`, `Twi250`, `Tfa126`, `Tfa131`, `Tfa160`, `N141`, `Twi249`, `Tfa253`, `Tfa254`

### `tkshh-wire-duplicate-opposed-edge-pair`

*TKShHealing* · 8 fixtures · observed: loads×4, crash×2, empty×2 · **8/8 carry a written spec** · corpus coverage: COVERED

A wire contains two consecutive edges that traverse (nearly) the same curve in opposite directions - a 'dummy seam' or duplicated out-and-back pair that encloses nothing. The pair must be removed and the wire's neighboring edges re-joined at a combined vertex.

**Test against:** `Twi033`, `Twi111`, `Twi132`, `Twi149`, `Twi174`, `Twi221`, `Twi057`, `Twi063`

### `stp-missing-pcurve-projection`

*exchange/step-reader* · 4 fixtures · observed: loads×2, crash×2 · **4/4 carry a written spec** · corpus coverage: COVERED

An edge on a face boundary has no usable 2D (pcurve) representation: the EDGE_CURVE's geometry has no associated pcurve entity at all, the listed pcurve(s) fail to translate, or the paired seam pcurves are missing. Rather than leaving the edge without any 2D trim, OCCT defers and computes the pcurve later by projecting the already-built 3D edge onto the face's surface; if even that projection…

**Test against:** `Gp035`, `Gp001`, `Gp042`, `Gp189`

### `tkshh-wire-missing-or-bad-degenerated-edge`

*TKShHealing* · 16 fixtures · observed: loads×12, empty×3, crash×1 · **16/16 carry a written spec** · corpus coverage: PARTIAL

A wire on a surface with a singularity (cone apex, sphere pole, degenerated torus/revolution row) is missing the degenerated edge (zero 3D length, finite UV length) that must bridge the singular row - or carries a degenerated edge whose flag/pcurve is wrong (no pcurve and no singularity actually present, bad parametrization vs neighbors, or duplicated degenerated edges).

**Test against:** `Twi021`, `Twi031`, `Twi083`, `Twi102`, `Twi142`, `Twi169`, `Twi196`, `Twi216`, `Twi234`, `Tfa005`, `Twi296`, `Twi297` …and 4 more

### `tkshh-vertex-not-on-curve-endpoints`

*TKShHealing* · 14 fixtures · observed: loads×11, empty×2, crash×1 · **14/14 carry a written spec** · corpus coverage: COVERED

An edge's vertex 3D points do not lie on the ends of the edge's 3D curve and/or its pcurve (lifted to the surface) within the vertex tolerance - the declared endpoint and the geometric endpoint disagree. Healing enlarges vertex tolerance to cover the actual curve ends.

**Test against:** `Twi046`, `Twi048`, `Twi059`, `Twi060`, `Twi061`, `Twi085`, `Gp002`, `Gp038`, `Bo030`, `Gp046`, `N054`, `Twi003` …and 2 more

### `tkshh-wire-multivertex-loop`

*TKShHealing* · 14 fixtures · observed: empty×8, loads×5, crash×1 · **14/14 carry a written spec** · corpus coverage: COVERED

A wire visits the same vertex more than twice (a vertex has more than two incident wire edges, after discounting seams, degenerated and small edges): a pinched / figure-eight / branching wire that is really several loops glued at a point, and must be split into separate wires.

**Test against:** `Twi010`, `Twi087`, `Twi256`, `Twi258`, `Twi259`, `Twi260`, `Twi261`, `Twi274`, `Twi276`, `Twi076`, `Tfa151`, `Tfa091` …and 2 more

### `tkshh-wire-small-edge`

*TKShHealing* · 11 fixtures · observed: empty×6, loads×4, crash×1 · **11/11 carry a written spec** · corpus coverage: COVERED

A wire contains a geometrically negligible edge: its two endpoint vertices and its curve midpoint all coincide within tolerance (sliver / zero-length edge, e.g. remnant of over-trimming). The edge must be removed and the wire re-stitched.

**Test against:** `Twi013`, `Twi119`, `Twi138`, `Twi237`, `Twi244`, `Twi184`, `N010`, `N014`, `Twi302`, `Twi303`, `Twi304`

### `tkshh-face-wire-orientation-wrong`

*TKShHealing* · 10 fixtures · observed: loads×6, empty×3, crash×1 · **10/10 carry a written spec** · corpus coverage: COVERED

The wires of a face are wound the wrong way relative to the surface normal / to each other: the outer boundary is traversed clockwise (encloses the infinite point), a hole wire is oriented like an outer boundary, or outer and inner senses are swapped so that the material side is inverted. OCCT classifies each wire against the others (point-in-face tests anchored by PerformInfinitePoint) and…

**Test against:** `Tfa236`, `Tfa081`, `Ps002`, `Tfa133`, `Tfa161`, `Tfa186`, `Twi177`, `Twi233`, `Twi267`, `Twi024`

### `tkshh-wire-not-closed`

*TKShHealing* · 10 fixtures · observed: empty×5, loads×4, crash×1 · **10/10 carry a written spec** · corpus coverage: COVERED

A wire that bounds a face (and therefore must be closed) is open: the last edge's end and the first edge's start do not coincide - either a small snapable gap, or the closing edge is missing entirely.

**Test against:** `Twi034`, `Twi053`, `Twi066`, `Twi195`, `Twi210`, `Twi239`, `Twi245`, `Twi126`, `Twi148`, `Twi265`

### `stp-partial-assembly-continuation`

*exchange/step-reader* · 9 fixtures · observed: loads×7, crash×1, empty×1 · **9/9 carry a written spec** · corpus coverage: PARTIAL

A constituent member of a topological container -- a face within a shell/solid, a void shell within a BREP_WITH_VOIDS, a shell within a SHELL_BASED_SURFACE_MODEL, a face within a FACE_BASED_SURFACE_MODEL, an edge within an EDGE_BASED_WIREFRAME_MODEL's connected-edge-set, a patch within a RECTANGULAR_COMPOSITE_SURFACE, or an element within a GEOMETRIC_SET -- fails to translate (or is a…

**Test against:** `Xp008`, `Tsh023`, `M051`, `Xp017`, `Bo001`, `Bo002`, `Tsh256`, `Tsh257`, `Bo031`

### `tkshh-same-surface-fragmented-faces`

*TKShHealing* · 9 fixtures · observed: loads×6, empty×2, crash×1 · **9/9 carry a written spec** · corpus coverage: COVERED

Adjacent faces of a shell lie on the same geometric surface (coplanar planes, co-axial same-radius cylinders/cones, identical B-spline surfaces) and are separated only by artificial edges that bound no real geometry change — the typical output of boolean fuses and fragmenting translators. ShapeUpgrade_UnifySameDomain (UnifyFaces/IntUnifyFaces) verifies same-domain geometry within…

**Test against:** `Tfa016`, `Tfa018`, `Tfa019`, `Tsh046`, `Tsh047`, `Tsh049`, `Tsh057`, `N003`, `Xp033`

### `sew-free-edge-gap-merge`

*exchange/sewing* · 8 fixtures · observed: loads×7, crash×1 · **8/8 carry a written spec** · corpus coverage: COVERED

Two free (unshared) edges that geometrically represent the same boundary curve but sit a small distance apart (gap smaller than the sewing tolerance) are recognized as the same edge and merged into one shared edge, instead of being left as two separate, non-conformal edges. Distance is evaluated by sampling points along the candidate edge and projecting them onto the reference edge (and vice…

**Test against:** `Tfa020`, `Tsh203`, `Tsh187`, `Twi037`, `Tfa019`, `Tsh181`, `Tsh243`, `Tsh244`

### `tkshh-wire-2d-pcurve-gap`

*TKShHealing* · 8 fixtures · observed: empty×4, loads×3, crash×1 · **8/8 carry a written spec** · corpus coverage: COVERED

The pcurves of two consecutive edges do not meet in the face's UV space: edge n's pcurve ends at a different UV point than edge n+1's pcurve starts (beyond the surface UV resolution of the precision), while 3D may be fine. Repair modifies the pcurve geometry to close the parametric contour (distinct from inserting a lacking edge).

**Test against:** `Twi112`, `Twi158`, `Twi192`, `Twi207`, `Twi069`, `Twi073`, `Gp020`, `Twi067`

### `tkshh-face-wires-bound-multiple-disjoint-regions`

*TKShHealing* · 7 fixtures · observed: loads×5, crash×1, empty×1 · **7/7 carry a written spec** · corpus coverage: COVERED

One face's wires actually bound several disjoint regions of the surface -- more than one closed wire acts as an 'outer' boundary (each possibly with its own holes), so the single FACE entity should really be several faces. This arises from merged faces on closed surfaces or from split-by-wire operations. OCCT's FixOrientation records which wires contain which (MapWires) and FixSplitFace then…

**Test against:** `Tfa085`, `Tfa145`, `Tfa210`, `Tfa239`, `Tfa075`, `Tsh013`, `Tfa011`

### `tkshh-face-natural-bound-missing`

*TKShHealing* · 6 fixtures · observed: loads×5, crash×1 · **6/6 carry a written spec** · corpus coverage: COVERED

A face on a closed surface lacks its outer boundary: either the ADVANCED_FACE has no bounds at all (legal STEP for 'the whole surface'), or -- on a doubly-periodic surface (sphere, torus) -- it carries only hole wires, the intended semantics being 'entire surface minus holes'. OCCT creates the natural (full parametric rectangle) boundary: an empty face is rebuilt via BRepBuilderAPI_MakeFace; a…

**Test against:** `Tfa002`, `Tfa004`, `Tfa038`, `Tfa088`, `Tfa101`, `Tfa255`

### `tkshh-faceconnect-unshared-boundary-edges`

*TKShHealing* · 6 fixtures · observed: loads×5, crash×1 · **6/6 carry a written spec** · corpus coverage: COVERED

Two adjacent faces that physically touch along a common boundary each carry their own independent copy of the boundary edge (and its endpoint vertices) instead of referencing one shared topological edge — a geometric crack/gap in an otherwise visually-closed shell. The healer geometrically sews the registered face pairs together (via BRepBuilderAPI_Sewing), rebuilds the affected wires with the…

**Test against:** `Tfa019`, `Twi037`, `Tsh086`, `Tsh095`, `Tsh101`, `Tsh110`

### `bc-check-fail`

*exchange/brepcheck* · 5 fixtures · observed: empty×3, crash×1, loads×1 · **5/5 carry a written spec** · corpus coverage: PARTIAL

The underlying geometric evaluation for a specific sub-check (e.g. curve/surface projection, intersection) throws an OCCT Standard_Failure exception because the input geometry is too degenerate to evaluate at all; the analyzer catches it and records a diagnosable status on the offending subshape instead of crashing or losing the result.

**Test against:** `In011`, `Gn037`, `Gn003`, `Ad132`, `Ad045`

### `sew-tolerance-budget-acceptance-and-cap`

*exchange/sewing* · 5 fixtures · observed: loads×4, crash×1 · **5/5 carry a written spec** · corpus coverage: COVERED

Perfect 3D/2D parameter synchronization (see sew-pcurve-parameter-desync-repair) cannot always be achieved. Rather than failing the merge outright whenever the residual 3D-to-2D mismatch isn't exactly zero, Sewing accepts the merge as long as the mismatch fits within a tolerance budget derived from the edge's own existing tolerance and the curves' intrinsic precision, and then tightens the…

**Test against:** `Tsh187`, `Tfa020`, `Tsh203`, `Tsh251`, `Tsh252`

### `sew-vertex-coincidence-merge`

*exchange/sewing* · 5 fixtures · observed: loads×3, crash×1, empty×1 · **5/5 carry a written spec** · corpus coverage: COVERED

Vertices from originally-separate shapes/edges that sit within tolerance of each other, but are not the literal same topological vertex, get unified into one shared 'node' vertex so that edges from different shapes actually connect at a shared point. This is done as a transitive spatial clustering (using a cell-filter spatial index) rather than naive pairwise snapping, and per-pair merges are…

**Test against:** `Tfa019`, `Twi037`, `Tsh203`, `Tfa022`, `N149`

### `sew-edge-endpoint-tolerance-reconciliation`

*exchange/sewing* · 4 fixtures · observed: loads×3, crash×1 · **4/4 carry a written spec** · corpus coverage: COVERED

Once two edges' endpoints are correctly paired (see sew-vertex-endpoint-pairing-orientation), the two original vertices at a paired endpoint are rarely exactly coincident — they sit at slightly different positions with their own tolerances. Rather than naively snapping one vertex's position onto the other (which could leave the discarded vertex's original position outside the new vertex's…

**Test against:** `Tfa020`, `Tsh203`, `Tsh187`, `Tfa257`

### `stp-oriented-edge-malformed`

*exchange/step-reader* · 4 fixtures · observed: loads×3, crash×1 · **4/4 carry a written spec** · corpus coverage: COVERED

An entry in an EDGE_LOOP's oriented-edge list is itself malformed: either the ORIENTED_EDGE (or its EdgeElement) is null/unresolved, its EdgeElement is not an EDGE_CURVE, or -- a subtler defect -- the ORIENTED_EDGE wraps another ORIENTED_EDGE instead of directly wrapping an EDGE_CURVE (an extra, illegitimate layer of indirection). The first class is skipped so the rest of the loop still…

**Test against:** `Twi006`, `Twi005`, `Twi004`, `Twi282`

### `seq-drop-small-edges`

*exchange/heal-sequence* · 2 fixtures · observed: loads×1, crash×1 · **2/2 carry a written spec** · corpus coverage: COVERED

Edges shorter than tolerance inside wires — micro-edges that fragment contours and destabilize downstream meshing/booleans — to be merged with neighboring edges. Registered under the (historically named) 'DropSmallEdges' operator but implemented as a merge.

**Test against:** `Twi013`, `Gp059`


## T1 silent-empty dominant

### `tkshh-curve-tolerance-closure-detection`

*TKShHealing* · 8 fixtures · observed: empty×5, loads×3 · **8/8 carry a written spec** · corpus coverage: COVERED

A curve's own type/flag does not report IsClosed()==true (e.g. it is not flagged periodic, or is a trimmed/reparametrized curve), yet its two 3D endpoints coincide within the supplied tolerance (or Precision::Confusion() as a floor). The curve must still be recognized as topologically closed via an explicit endpoint-distance check, while curves with an infinite parameter bound are safely…

**Test against:** `Gn039`, `Gn049`, `Gn064`, `Gn071`, `Gn077`, `Gn088`, `Gn094`, `Gn101`

### `tkshh-wire-3d-curve-gap`

*TKShHealing* · 8 fixtures · observed: empty×5, loads×3 · **8/8 carry a written spec** · corpus coverage: COVERED

The 3D curves of two consecutive edges do not meet: the end point of edge n's 3D curve and the start point of edge n+1's 3D curve are separated by more than precision, even though the wire's topology may claim connection. Repair modifies the curve geometry itself - translating/extending curve ends or replacing curve segments - to close the gap (distinct from merely merging vertices or…

**Test against:** `Twi108`, `Twi180`, `Twi189`, `Twi199`, `Twi266`, `Twi068`, `Twi072`, `Twi003`

### `tkshh-wire-adjacent-vertex-gap`

*TKShHealing* · 8 fixtures · observed: empty×5, loads×3 · **8/8 carry a written spec** · corpus coverage: COVERED

Consecutive edges of a wire are listed in correct order but do not share a vertex: the end vertex of edge n and the start vertex of edge n+1 are distinct VERTEX instances separated by a small 3D distance. The wire is topologically broken at the junction; the vertices must be merged (identical points) or combined into an averaged vertex.

**Test against:** `Twi003`, `Twi043`, `Twi056`, `Twi116`, `Twi136`, `Twi238`, `Twi243`, `Twi264`

### `tkshh-wire-tail`

*TKShHealing* · 8 fixtures · observed: empty×7, loads×1 · **8/8 carry a written spec** · corpus coverage: COVERED

A tail (hair): at the junction of two consecutive edges the boundary shoots out and comes straight back, forming a protrusion narrower than a configured max width (and optionally sharper than a max angle). The out-and-back portions must be cut off the two edges and the residual out/back pair removed.

**Test against:** `Twi011`, `Twi077`, `Twi098`, `Twi114`, `Twi122`, `Twi182`, `Twi197`, `Twi215`

### `tkshh-same-curve-fragmented-edges`

*TKShHealing* · 6 fixtures · observed: empty×4, loads×2 · **6/6 carry a written spec** · corpus coverage: COVERED

A chain of edges joined at degree-2 vertices lies on the same geometric curve — collinear line segments, arcs of one circle (possibly closing into a full circle), or a spliceable B-spline/Bezier sequence — so the interior vertices are topologically unnecessary fragmentation. ShapeUpgrade_UnifySameDomain (UnifyEdges -> MergeEdges/generateSubSeq -> MergeSeq/MergeSubSeq) validates co-curve…

**Test against:** `Twi089`, `Tsh046`, `N154`, `N144`, `Twi294`, `Twi295`

### `stp-tolerance-ceiling-clamp`

*exchange/step-reader* · 4 fixtures · observed: empty×3, loads×1 · **4/4 carry a written spec** · corpus coverage: COVERED

Per-entity repairs elsewhere in the translation pipeline enlarge vertex/edge tolerances to absorb small inconsistencies between STEP-declared points and computed geometry; taken together across a whole shape, these could in principle accumulate into unreasonably large tolerances. After the full solid/shell/model is assembled, a global, configurable post-pass clamps every tolerance in the…

**Test against:** `Tb020`, `N040`, `N007`, `N173`


## T2 loads-and-heals

### `tkshh-wire-nonadjacent-edges-intersect`

*TKShHealing* · 15 fixtures · observed: loads×10, empty×5 · **15/15 carry a written spec** · corpus coverage: COVERED

Two non-adjacent edges of the same wire cross in parameter space (global self-intersection, e.g. a figure-eight or bow-tie contour). Repair splits the edges at the crossing, cuts back, or removes the enclosed sub-segment.

**Test against:** `Twi049`, `Twi076`, `Twi157`, `Twi214`, `Twi232`, `Twi263`, `Twi249`, `Twi250`, `Twi251`, `Gs011`, `Gs009`, `Twi103` …and 3 more

### `tkshh-tolerance-out-of-range`

*TKShHealing* · 13 fixtures · observed: loads×7, empty×6 · **13/13 carry a written spec** · corpus coverage: COVERED

A vertex, edge, or face carries a tolerance value that falls outside an application-specified acceptable range [tmin, tmax] -- either unrealistically tight (masking nothing, but inconsistent with the rest of the model) or excessively loose (hiding real geometric gaps/deviations downstream). OCCT repairs this by clamping the offending tolerance to the nearer bound of the range, recursing…

**Test against:** `N040`, `N055`, `N065`, `N070`, `N080`, `N089`, `N097`, `N119`, `N128`, `N132`, `N134`, `N167` …and 1 more

### `tkshh-surface-curve-continuity-below-required`

*TKShHealing* · 11 fixtures · observed: loads×11 · **11/11 carry a written spec** · corpus coverage: COVERED

A face's boundary curves, pcurves, or its underlying surface have geometric continuity below a required order (by default C1) at internal parametric locations — e.g. a composite/multi-knot curve or surface with only C0 (positionally-continuous-but-kinked) joins between segments — which downstream consumers that assume at least C1 continuity (for tangent/normal computation, offsetting, meshing)…

**Test against:** `Gn012`, `Gs049`, `Gs070`, `Gs085`, `Gs132`, `Gs182`, `Hea010`, `Gn172`, `Gs162`, `Gs197`, `Gs198`

### `tkshh-edge-pcurve-reversed`

*TKShHealing* · 10 fixtures · observed: loads×6, empty×4 · **10/10 carry a written spec** · corpus coverage: COVERED

An edge's pcurve traces the boundary in the opposite parametric direction from its 3D curve / edge orientation — sampling the 3D curve and the pcurve at the same parameter lands on opposite ends of the edge. The healer detects this via a 3D/2D consistency check and reverses the pcurve's parametrization (swapping and re-deriving first/last parameters), flagging the edge as no longer…

**Test against:** `Gp054`, `Gp068`, `Gp080`, `Gp089`, `Gp109`, `Gp124`, `Gs018`, `Twi062`, `Twi065`, `Gp043`

### `tkshh-wire-edges-disordered`

*TKShHealing* · 10 fixtures · observed: loads×7, empty×3 · **10/10 carry a written spec** · corpus coverage: COVERED

The edges of a wire are stored out of traversal order: consecutive entries in the edge list do not chain head-to-tail, although a valid ordering (possibly with some edges reversed, or with the closed wire's start rotated) exists. Includes the sub-case where an individual edge's stored orientation is opposite to its traversal direction.

**Test against:** `Twi007`, `Twi078`, `Twi028`, `Twi038`, `Twi159`, `Twi008`, `Twi107`, `Twi200`, `Twi242`, `Twi193`

### `tkshh-face-closed-surface-unsplit-at-seam`

*TKShHealing* · 9 fixtures · observed: loads×7, empty×2 · **9/9 carry a written spec** · corpus coverage: COVERED

A face is built directly on a fully closed/periodic surface (full cylinder, cone, torus, or sphere) without being explicitly split along the periodic seam, or is trimmed such that it still effectively wraps a full period in U and/or V. Many downstream consumers cannot represent or process a face that wraps a full period. The healer detects the seam — either from an explicit seam edge already…

**Test against:** `Twi032`, `N005`, `Gp027`, `Gs193`, `Wr037`, `Gp028`, `Gs194`, `Gs195`, `Gs196`

### `stp-edge-curve-param-range`

*exchange/step-reader* · 8 fixtures · observed: loads×6, empty×2 · **8/8 carry a written spec** · corpus coverage: COVERED

An EDGE_CURVE's 3D-curve trim parameters (as recomputed by projecting the edge's two vertices onto the curve) do not form a valid, correctly-ordered range that bounds the edge: they may fall outside the curve's own definition bounds, wrap the wrong way around a periodic curve's seam, cross the origin of a closed-but-non-periodic curve, only look closed within 3D tolerance without being flagged…

**Test against:** `Gs029`, `Gp171`, `Twi017`, `Twi086`, `Twi084`, `Gs201`, `Gs202`, `Gs203`

### `stp-seam-pcurve-selection`

*exchange/step-reader* · 8 fixtures · observed: loads×8 · **8/8 carry a written spec** · corpus coverage: COVERED

An edge lies on a closed surface and is associated with two pcurves (via a SEAM_CURVE, via being referenced twice within one wire, or via a CATIA-style pattern where two different faces are built on the same underlying surface without either surface or curve being formally flagged closed/seam). OCCT must determine which of the two pcurves is the 'forward' one for this particular edge/wire/face…

**Test against:** `Gs193`, `Gp013`, `Gp011`, `Gs028`, `Twi022`, `Gp119`, `Gp190`, `Gp194`

### `tkshh-surface-closure-vs-declared-periodicity-mismatch`

*TKShHealing* · 7 fixtures · observed: loads×7 · **7/7 carry a written spec** · corpus coverage: COVERED

A surface is geometrically closed in U and/or V (its poles/boundary curve coincide within tolerance at the two parametric extremes) even though it is not flagged periodic by its Geom type or STEP declaration — or vice versa, a surface that merely comes close but is not truly closed must not be misreported as closed. Type-specific heuristics locate the true closure distance (pole comparison for…

**Test against:** `Gs081`, `Gs091`, `Gs103`, `Gs139`, `Tfa197`, `Gs064`, `Gs140`

### `seq-surface-to-bspline`

*exchange/heal-sequence* · 6 fixtures · observed: loads×5, empty×1 · **6/6 carry a written spec** · corpus coverage: COVERED

Shapes carrying linear-extrusion, revolution, or offset surfaces that the consumer cannot accept in procedural/swept form and which must be re-expressed as explicit B-spline geometry. Offset surfaces in particular are frequently unsupported downstream.

**Test against:** `Gs032`, `Gs046`, `Ad120`, `Gs188`, `Tfa026`, `N019`

### `stp-makeedge-validity-fallback`

*exchange/step-reader* · 6 fixtures · observed: loads×5, empty×1 · **6/6 carry a written spec** · corpus coverage: COVERED

Building a proper OCCT edge from the translated 3D curve, its two vertices, and their trim parameters (via BRepLib_MakeEdge, which performs geometric sanity checks) fails for one of several reasons: the vertex point cannot be projected onto the curve, a trim parameter is out of range, a projected point has an infinite parameter, projected points/parameters disagree with the vertex points, or…

**Test against:** `Twi086`, `Twi013`, `Gs029`, `Bo030`, `Twi299`, `Twi300`

### `stp-nm-shared-entity-reuse`

*exchange/step-reader* · 6 fixtures · observed: loads×6 · **6/6 carry a written spec** · corpus coverage: COVERED

In a non-manifold STEP model, the same EDGE_CURVE, FaceSurface's underlying surface, or VERTEX entity is legitimately referenced from more than one face/shell context, and the second (and subsequent) references must resolve to the very same OCCT shape (with orientation adjusted) rather than being independently re-translated into duplicate geometry. OCCT tracks entities already produced for the…

**Test against:** `Tsh019`, `Tsh232`, `Bo006`, `M045`, `Tsh254`, `Tsh255`

### `stp-pcurve-trim-range-repair`

*exchange/step-reader* · 6 fixtures · observed: loads×5, empty×1 · **6/6 carry a written spec** · corpus coverage: PARTIAL

An edge's 2D (pcurve) trim parameters on a face are inconsistent with the underlying parametric curve or surface: the range may collapse to a single point (start==end) despite the edge being a real, non-degenerate 3D edge; the range may extend beyond the pcurve's own definition bounds; or, on a U-periodic surface, the range may straddle the periodic seam in the wrong order. OCCT repairs each…

**Test against:** `Gp007`, `Gn019`, `Gs007`, `Gp028`, `Gp191`, `Gp192`

### `stp-vertex-tol-gap`

*exchange/step-reader* · 6 fixtures · observed: loads×3, empty×3 · **6/6 carry a written spec** · corpus coverage: COVERED

After projecting an edge's declared vertex points onto its 3D curve, the projected point and the vertex's authored coordinate do not coincide exactly (STEP data is only approximately consistent). Rather than reject the edge, the vertex's tolerance is enlarged to the (slightly inflated) measured gap so the vertex remains valid at its stated position while covering the discrepancy.

**Test against:** `Bo030`, `Ad045`, `Gp038`, `N007`, `N009`, `N174`

### `stp-vertexloop-bound-mismatch`

*exchange/step-reader* · 6 fixtures · observed: loads×6 · **6/6 carry a written spec** · corpus coverage: COVERED

A face bound is expressed as a VERTEX_LOOP (a single point, normally meant for degenerate apex-type bounds), but this doesn't correspond to valid/meaningful boundary topology for the surface kind it's attached to. OCCT's response depends on the surface: on a sphere/B-spline/surface-of-revolution where the VERTEX_LOOP is the face's only bound, it is discarded and the face is instead given its…

**Test against:** `Gs039`, `Twi281`, `Twi041`, `Pf025`, `Tfa004`, `Gs199`

### `tkshh-edge-missing-3d-curve`

*TKShHealing* · 6 fixtures · observed: loads×4, empty×2 · **6/6 carry a written spec** · corpus coverage: COVERED

An edge has no 3D curve (only a pcurve on a surface, or no geometry at all). The 3D curve must be rebuilt from the pcurve lifted to the surface; an edge with neither representation is unusable and is removed from the wire.

**Test against:** `Twi047`, `Twi088`, `Os012`, `Gp057`, `Gp082`, `Twi289`

### `tkshh-face-missing-seam-edge`

*TKShHealing* · 6 fixtures · observed: loads×5, empty×1 · **6/6 carry a written spec** · corpus coverage: COVERED

A face lies on a closed (periodic) surface -- cylinder, torus, sphere, periodic B-spline -- and its boundary wraps around the periodic direction, but the file contains no seam edge. The wire closes in 3D yet is open in UV parameter space (e.g. two half-circles at top and bottom of a cylinder with nothing joining them along the U=0 isoline). OCCT detects the 2D-open wires, chooses a seam…

**Test against:** `Twi020`, `Tfa199`, `Tfa215`, `Gp137`, `Gs141`, `Xp015`

### `tkshh-pcurve-collapse-onto-surface-singularity`

*TKShHealing* · 6 fixtures · observed: loads×6 · **6/6 carry a written spec** · corpus coverage: COVERED

When an edge's 3D curve runs through (or partially through) one of a surface's known singularities (see tkshh-surface-analytic-singularity-detection), the corresponding pcurve's 2D samples must be recognized as degenerate and repaired rather than left as noisy/undefined UV values: if the whole pcurve collapses onto the singularity, its non-degenerate parametric axis is evenly redistributed…

**Test against:** `Gp157`, `Gp158`, `Gp159`, `Gp160`, `Gs148`, `Tfa200`

### `tkshh-wire-pcurve-period-shifted`

*TKShHealing* · 6 fixtures · observed: loads×5, empty×1 · **6/6 carry a written spec** · corpus coverage: COVERED

On a closed/periodic surface, one or more edges' pcurves are displaced by (a multiple of) the surface period relative to their neighbors - typically because the pcurve was recomputed from 3D near the seam. The 2D contour is discontinuous or lies outside the surface's nominal parametric range even though the 3D wire is fine.

**Test against:** `Twi109`, `Twi134`, `Twi240`, `Twi035`, `Twi032`, `Gp023`

### `bc-invalid-degenerated-flag`

*exchange/brepcheck* · 5 fixtures · observed: loads×4, empty×1 · **5/5 carry a written spec** · corpus coverage: PARTIAL

An edge marked as 'degenerated' does not actually collapse to a single point (or a genuinely-degenerate edge is not marked), inconsistent with topological expectation at a surface pole/apex.

**Test against:** `Twi031`, `Twi083`, `Twi021`, `Twi018`, `Twi301`

### `bc-not-closed`

*exchange/brepcheck* · 5 fixtures · observed: loads×5 · **5/5 carry a written spec** · corpus coverage: COVERED

A wire that should form a closed loop (or a shell that should form a closed shell bounding a solid) has a gap — endpoints/edges don't connect all the way around.

**Test against:** `Twi053`, `Twi034`, `Twi066`, `Tsh029`, `Hea002`

### `seq-set-tolerance`

*exchange/heal-sequence* · 5 fixtures · observed: loads×5 · **5/5 carry a written spec** · corpus coverage: COVERED

Tolerance values on the translated shape are unreliable: out of the acceptable band (too tight or too loose relative to a target value/ratio), or stale relative to actual sub-shape geometry (vertex tolerance smaller than edge deviation, etc.). Also covers continuity/regularity flags on edges being absent even where adjacent faces actually meet smoothly.

**Test against:** `Twi048`, `Twi061`, `Bo030`, `Bo025`, `N172`

### `seq-xsalgo-pcurve-consistency`

*exchange/heal-sequence* · 5 fixtures · observed: loads×5 · **5/5 carry a written spec** · corpus coverage: COVERED

A translated edge's parameter-space curve is inconsistent with its 3D data in one of three ways: (a) the pcurve winds across many periods of a closed surface (parametric span vastly exceeding the surface domain, e.g. degree-vs-radian confusion producing dozens of wraps); (b) the surface points at the pcurve's ends do not match the edge's 3D endpoints within precision; (c) the pcurve deviates…

**Test against:** `Gp002`, `Gp022`, `Gs007`, `Gp023`, `Gp185`

### `stp-loop-vertex-merge`

*exchange/step-reader* · 5 fixtures · observed: loads×5 · **5/5 carry a written spec** · corpus coverage: COVERED

Two distinct STEP vertex entities used within the same wire -- either as the (translated) start and end of a single edge, or as the endpoints two adjacent edges are each supposed to share at their common corner -- turn out to be geometrically coincident within tolerance even though STEP declared them as separate entities. OCCT unifies them into a single OCCT vertex (rebinding one STEP vertex…

**Test against:** `Twi017`, `Gp171`, `Twi003`, `Hea012`, `Twi291`

### `stp-null-arc-edge-fallback`

*exchange/step-reader* · 5 fixtures · observed: loads×3, empty×2 · **5/5 carry a written spec** · corpus coverage: COVERED

An edge's 3D curve cannot be validly trimmed between its two vertex parameters (a 'different points on closed curve' construction error) even though the curve itself is not closed and the two declared vertices are distinct points, indicating a near-zero-length or otherwise malformed arc. OCCT discards the STEP-specified curve for this edge and substitutes a straight line segment built directly…

**Test against:** `Twi018`, `Twi086`, `Twi099`, `Twi013`, `Twi290`

### `tkshh-edge-crossing-surface-singularity`

*TKShHealing* · 5 fixtures · observed: loads×5 · **5/5 carry a written spec** · corpus coverage: COVERED

An edge's curve passes over a surface singularity (cone apex, sphere pole) in its interior, so a single pcurve cannot represent it faithfully: after pcurve (re)computation the edge must be split at the singularity parameter(s); a related form is a contour that goes around a degenerated pole and the seam, whose pcurve must be recomputed with over-degenerate adjustment disabled.

**Test against:** `Xp013`, `Gp048`, `Gp084`, `Gp177`, `Gp178`

### `tkshh-strip-face`

*TKShHealing* · 5 fixtures · observed: loads×5 · **5/5 carry a written spec** · corpus coverage: COVERED

A face has degenerated into a zero-width sliver/ribbon: either (a) it is bounded by exactly two long edges plus tiny connecting edges, and the two long edges run coincident within tolerance along their full length, or (b) the underlying BSpline/Bezier surface's control-point grid collapses to within tolerance across an entire row/column in one parametric direction. OCCT detects this ('strip…

**Test against:** `Tfa007`, `Tfa042`, `Tfa047`, `Tfa048`, `Gs014`

### `tkshh-wire-notched-edges`

*TKShHealing* · 5 fixtures · observed: loads×3, empty×2 · **5/5 carry a written spec** · corpus coverage: COVERED

Two adjacent edges form a notch: from the shared vertex they run back along (nearly) the same track - collinear/tangent within ~0.1 rad and within tolerance of each other - so one edge (the short one) retraces part of the other, creating a zero-area slit in the boundary. Fix removes the short edge and splits the long one at the projection of the short edge's far end.

**Test against:** `Twi054`, `Twi074`, `Twi117`, `Twi241`, `Hea005`

### `bc-bad-orientation-of-subshape`

*exchange/brepcheck* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: COVERED

A subshape's TopAbs_Orientation (FORWARD/REVERSED) is inconsistent with how it is used by its parent (e.g. an edge's orientation within a wire contradicts the wire's implied traversal direction, or a face's orientation contradicts shell consistency).

**Test against:** `Tfa057`, `Ps010`, `Tsh011`, `Ps002`

### `bc-intersecting-wires`

*exchange/brepcheck* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: GAP

Two distinct wires bounding the same face cross each other in parametric space.

**Test against:** `Tfa039`, `Tfa242`, `Gp069`, `Gs155`

### `bc-invalid-same-range-flag`

*exchange/brepcheck* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: COVERED

An edge's SameRange flag asserts the 3D curve and pcurve share an identical parameter range, but the stored ranges actually differ.

**Test against:** `Twi082`, `Gp050`, `Gp045`, `Gp183`

### `seq-bspline-restriction`

*exchange/heal-sequence* · 4 fixtures · observed: loads×2, empty×2 · **4/4 carry a written spec** · corpus coverage: COVERED

B-spline curves/surfaces (or geometry convertible to them) whose degree, segment count, continuity class, or rational form exceeds what the receiving system supports — e.g. degree above a cap, too many knots/segments, rational weights where only polynomial is accepted, or offset/swept/elementary surfaces that must be re-approximated into constrained B-spline form.

**Test against:** `Gn011`, `Gn009`, `Gn026`, `Gn177`

### `seq-split-continuity`

*exchange/heal-sequence* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: COVERED

Curves, pcurves, or surfaces whose internal smoothness is below the required continuity class (e.g. C0 kinks inside a single B-spline where downstream needs C1): the entity must be divided at the discontinuity points into separately-valid pieces.

**Test against:** `Gp120`, `Gs049`, `Gs070`, `Gp184`

### `sew-pcurve-parameter-desync-repair`

*exchange/sewing* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: PARTIAL

After a merged edge's 3D curve and 2D pcurve(s) are assembled, they may not walk in lockstep (the 'SameParameter' property OCCT requires: evaluating the 3D curve and each pcurve at the same parameter value should land on corresponding points, within tolerance). A common cause is a pcurve with a C0 (kinked/non-smooth) discontinuity at an interior knot, which prevents the…

**Test against:** `Gp040`, `Gp033`, `Twi248`, `Gp187`

### `sew-seam-closed-surface-merge`

*exchange/sewing* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: COVERED

On a periodic/closed surface (e.g. cylinder, cone, torus, sphere), an edge running along the seam can look 'close' to another edge in 3D while actually being unrelated, or can be the correct seam partner despite looking far apart when naively measured. Before approving such a merge, Sewing checks that the two edges' 2D (parametric) footprints actually overlap across the closed direction of the…

**Test against:** `Tsh209`, `Gp139`, `Gs200`, `Gs204`

### `stp-face-bound-fail-continue`

*exchange/step-reader* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: COVERED

One of a face's several FACE_BOUND wires fails to translate (its EdgeLoop couldn't be mapped, or its Loop is of an entity subtype OCCT doesn't implement), or the geometry needed to compute the face's natural (implicit) outer bound is missing. Rather than discarding the whole face, OCCT proceeds without that one bound; only if the failed/missing bound was specifically the outer bound is a…

**Test against:** `Xp008`, `Tsh023`, `Twi001`, `Tfa003`

### `stp-srrwt-axis-swap`

*exchange/step-reader* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: COVERED

In a SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION (used to position one assembly component's shape representation relative to another via a pair of AXIS2_PLACEMENT_3D entities), the Origin and Target placements are found to actually belong to the opposite representations from what their role names would suggest -- i.e. they are swapped. OCCT cross-checks each placement's membership in…

**Test against:** `A007`, `Ps007`, `Hea014`, `A120`

### `stp-toroidal-neg-radius-orientation`

*exchange/step-reader* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: COVERED

A FACE_SURFACE's underlying TOROIDAL_SURFACE (possibly wrapped in a RECTANGULAR_TRIMMED_SURFACE) is authored with a negative major radius, a non-standard convention some CAD systems (e.g. SolidWorks) use to signal that the face's orientation should be flipped relative to what the surface's own parametrization would imply. OCCT detects the negative radius and flips the interpreted face…

**Test against:** `Gs001`, `Tsh035`, `Xp010`, `Xp022`

### `stp-transfer-exception-to-fail`

*exchange/step-reader* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: COVERED

Translating a piece of STEP geometry (a root shape entity dispatched by type, a wire's per-edge 3D curve conversion, a composite-curve segment's curve/pcurve conversion, or a GeometricSet curve element) raises an uncaught C++ exception somewhere deep in the geometric construction call chain -- typically triggered by numerically degenerate or self-contradictory geometry definitions that only…

**Test against:** `Ad043`, `Xp008`, `Ad137`, `Ad138`

### `tkshh-face-period-wrapped-uv-placement`

*TKShHealing* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: COVERED

On a periodic surface, a face's wires are written with UV coordinates outside or straddling the canonical period window: one wire near u=0, another a full period away (u~2pi+x), or a wire wrapping across the seam so its 2D bounding box splits to opposite ends of the domain. Geometry is valid modulo the period, but naive containment/nesting tests see disjoint boxes and misclassify. OCCT…

**Test against:** `Tfa207`, `Tfa242`, `Tfa243`, `Gp137`

### `tkshh-face-wire-of-two-coincident-edges`

*TKShHealing* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: COVERED

A face (with at least two wires) contains a wire that consists of exactly two edges which are the same edge entity traversed twice -- a zero-area 'slit' loop that goes out along an edge and immediately back along the identical curve. The wire bounds no area and must be dropped. OCCT's FixWiresTwoCoincEdges rebuilds the face keeping every wire except those whose two edges are identical when…

**Test against:** `Tfa074`, `Tfa232`, `Tfa209`, `Tfa256`

### `tkshh-nonperiodic-bspline-seamlike-edge`

*TKShHealing* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: PARTIAL

A closed body is encoded on a B-spline surface that is geometrically closed but NOT declared periodic (e.g. CATIA 'like-seam' cylinders): two faces share an edge carrying two pcurves on the same surface — behaving like a seam — yet the surface has no period, so ordinary unification cannot wrap around. During face unification OCCT detects the smooth seam-like edge, converts/declares the surface…

**Test against:** `Gp013`, `Gp181`, `Gp182`, `Gp194`

### `tkshh-spot-face`

*TKShHealing* · 4 fixtures · observed: loads×4 · **4/4 carry a written spec** · corpus coverage: COVERED

A face's entire boundary has collapsed within tolerance to a single point: every wire vertex is coincident (or the outer wire's bounding box is smaller than the working precision), so the face has no usable 2D interior and contributes nothing to the shape's area/volume. OCCT detects this ('spot face') and repairs it by merging all of the face's vertices into one shared tolerant vertex and…

**Test against:** `Tfa006`, `Tfa041`, `Tfa072`, `Gs014`

### `tkshh-wire-only-degenerated-edges`

*TKShHealing* · 4 fixtures · observed: loads×3, empty×1 · **4/4 carry a written spec** · corpus coverage: COVERED

A wire consists solely of degenerated / zero-extent edges (all edges collapse to a single point, e.g. leftover pole caps or authoring debris): it bounds nothing and poisons seam construction and orientation analysis. OCCT removes such wires: FixMissingSeam drops completely-degenerated extra open wires before pairing seam wires; ComposeShell::DispatchWires prunes empty or…

**Test against:** `Tfa224`, `Tfa096`, `Tfa168`, `Tfa206`

### `bc-free-edge`

*exchange/brepcheck* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

An edge belongs to only one face within a shell/wire context where the surrounding topology implies it should be shared (naked edge in what is otherwise treated as a closed boundary).

**Test against:** `Tsh029`, `Tsh044`, `Tsh072`

### `bc-invalid-curve-on-closed-surface`

*exchange/brepcheck* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A seam edge on a closed/periodic surface has forward and reverse pcurves that don't correctly bound the same parametric span (seam mismatch).

**Test against:** `Twi022`, `Gp011`, `Gp013`

### `bc-invalid-curve-on-surface`

*exchange/brepcheck* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

An edge's pcurve on a face does not track the edge's 3D curve within tolerance (the 2D and 3D representations disagree).

**Test against:** `Gp041`, `Gp002`, `Gp021`

### `bc-invalid-multi-connexity`

*exchange/brepcheck* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

An edge is shared by more than two faces (non-manifold edge) where the structure being checked expects at most two.

**Test against:** `Bo006`, `Tsh019`, `Tsh232`

### `bc-self-intersecting-wire`

*exchange/brepcheck* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A wire's own edges cross each other in parametric/3D space, making it a non-simple loop.

**Test against:** `Twi286`, `Gs009`, `Gs012`

### `seq-direct-faces`

*exchange/heal-sequence* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

Faces whose underlying surface's natural normal direction is opposite to the topological face orientation (face marked REVERSED relative to its surface). Some source systems emit geometry this way; downstream consumers expect the surface parametrization to agree with face orientation.

**Test against:** `Ps003`, `Tsh032`, `Tsh010`

### `seq-drop-small-solids`

*exchange/heal-sequence* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

Solids of negligible size — volume below a threshold or thin-plate/sliver bodies detected via a width-factor criterion — typically translation debris or modeling artifacts, to be removed outright or merged into an adjacent larger solid.

**Test against:** `Tsh238`, `Tsh239`, `Tsh264`

### `seq-fix-shape`

*exchange/heal-sequence* · 3 fixtures · observed: loads×2, empty×1 · **3/3 carry a written spec** · corpus coverage: COVERED

Catch-all: the translated shape violates BRep validity in any of the broad ShapeFix_Shape categories (disconnected or misordered wires, wrong face/shell orientation, missing seams or natural bounds, self-intersecting or small entities, bad vertex positions/tolerances, edges lacking pcurves or 3D curves, etc.). This is the ONLY operator wired into the default STEP and IGES import sequences; its…

**Test against:** `Hea001`, `Tsh043`, `Twi051`

### `seq-fix-wire-gaps`

*exchange/heal-sequence* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

Wires whose consecutive edges do not meet: 3D and/or 2D gaps between the end of one edge and the start of the next exceed tolerance, leaving the wire discontinuous even though the file presents it as a connected contour.

**Test against:** `Twi053`, `Twi003`, `Gp020`

### `seq-split-closed-faces`

*exchange/heal-sequence* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

Faces lying on surfaces closed (periodic) in a parametric direction and spanning the full period — cylinders, tori, spheres, closed B-splines — which many consumers cannot represent as a single face; the face must be split into two or more patches, each not closed on itself.

**Test against:** `Twi032`, `Gs193`, `Gp027`

### `seq-swept-to-elementary`

*exchange/heal-sequence* · 3 fixtures · observed: loads×2, empty×1 · **3/3 carry a written spec** · corpus coverage: COVERED

The inverse mismatch: surfaces encoded as generic sweeps (revolution/extrusion) that are actually elementary quadrics in disguise — a cylinder written as a revolved line, a cone as a revolved slanted line, etc. Canonical-form recovery targets translators that always emit swept forms.

**Test against:** `N030`, `Gn015`, `Gn179`

### `sew-cutting-hanging-vertex-split`

*exchange/sewing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: PARTIAL

An edge that geometrically passes through or very near a vertex belonging to a different, unrelated free edge — without topologically sharing that vertex — creates a non-conformal T-junction: the two edges LOOK connected in 3D but the mesh/topology doesn't actually share a vertex there. Sewing detects such hanging vertices projecting onto a boundary edge and cuts (splits) that edge at the…

**Test against:** `Tsh260`, `Tsh261`, `Tsh262`

### `sew-edge-multiplicity-reporting`

*exchange/sewing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

After sewing completes, every edge in the result is classified by how many face-boundary sections ultimately mapped to it: exactly one section means the edge is genuinely free (a real boundary, or -- if formally degenerate -- tracked separately from ordinary free edges); exactly two means it's an ordinary (contiguous/manifold) shared edge; three or more means it's a non-manifold ('multiple')…

**Test against:** `Sw001`, `Tfa020`, `Tsh040`

### `sew-floating-wireframe-edge-mode`

*exchange/sewing* · 3 fixtures · observed: loads×2, empty×1 · **3/3 carry a written spec** · corpus coverage: COVERED

Edges that belong to no face at all (pure wireframe/curve topology, zero incident faces) are, by default, ignored by sewing since there is no face-boundary context to reconcile. When explicitly enabled (floating-edges mode), Sewing extends its gap-closing and vertex-merging behavior to these standalone edges too, letting a defective wireframe/curve-network model (e.g. imported skeleton curves…

**Test against:** `Tfa022`, `N147`, `N149`

### `sew-pcurve-domain-reconciliation`

*exchange/sewing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

Two edges being merged each carry their own 2D pcurve(s), independently parametrized to their own original 3D edge's parameter range. Once merged into one edge with one shared 3D parameter range, every contributing pcurve must be rescaled (and, for reversed-orientation contributors, reversed) onto that new shared domain, or the 2D-to-3D correspondence would be wrong on the non-reference edge's…

**Test against:** `Gp050`, `Gp052`, `Gp186`

### `stp-edgeloop-empty`

*exchange/step-reader* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

An EDGE_LOOP entity is present but declares zero edges, which cannot form any wire. OCCT detects this specific empty-list condition and fails the wire's translation with a targeted diagnostic rather than crashing or producing a degenerate wire object.

**Test against:** `Twi001`, `Tsh023`, `Xp008`

### `stp-ideas-shell-closing`

*exchange/step-reader* · 3 fixtures · observed: loads×2, empty×1 · **3/3 carry a written spec** · corpus coverage: COVERED

An I-DEAS-authored STEP file represents what is really one closed solid boundary as several separate OPEN shells: a 'main' open shell plus one or more extra shells composed entirely of non-manifold (shared) edges that exist only to close the gap. OCCT recognizes this preprocessor-specific pattern, identifies candidate closing shells adjacent to each open shell, merges their faces in to close…

**Test against:** `Lh031`, `Lh053`, `Lh054`

### `stp-pcurve-basis-surface-match`

*exchange/step-reader* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A SURFACE_CURVE lists multiple associated pcurve candidates in its AssociatedGeometry list (some possibly null, or lying on a different surface than the one currently being trimmed against). OCCT selects the correct candidate by matching each candidate's basis surface against the target surface, skipping null or non-matching entries rather than picking the first one blindly.

**Test against:** `Gp172`, `Gp012`, `Gp010`

### `stp-surface-force-periodic`

*exchange/step-reader* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A B-spline surface used as a face's basis geometry (directly, or as the basis of a CURVE_BOUNDED_SURFACE) is geometrically closed/periodic in one parametric direction (e.g. a full revolution) but the STEP data does not flag it as periodic, which would otherwise cause a mismatched seam when boundary wires are trimmed against it. OCCT converts the surface to an explicitly periodic form before…

**Test against:** `Gs005`, `Gp013`, `Tfa197`

### `stp-tess-dangling-brep-link`

*exchange/step-reader* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A tessellated face/shell/solid declares a geometric or topological link to an exact-BRep counterpart that cannot be resolved (nothing is bound for the referenced entity). Instead of failing, a fresh empty face/shell/solid is created to host the tessellation, and the result is marked as carrying no exact geometry.

**Test against:** `M193`, `M194`, `M195`

### `tkshh-closed-edge-full-period-unsplit`

*TKShHealing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

An edge spans the full period of a closed curve - its start and end vertex coincide (e.g. a full-circle EDGE_CURVE with one vertex) - and must be split at a parametric break before wire/face logic can treat it; when splitting, transferred knots near the closure point need a small periodic correction. Reframed from group-B's 'derived-edge-range-construction' (the TransferRange machinery) to the…

**Test against:** `Twi019`, `Twi292`, `Twi293`

### `tkshh-curve-projection-degenerate-parametrization`

*TKShHealing* · 3 fixtures · observed: loads×2, empty×1 · **3/3 carry a written spec** · corpus coverage: COVERED

A 3D point needs to be projected onto a Geom_Curve/edge whose parametrization is itself abnormal: FirstParameter()>LastParameter() (reversed range), an unbounded/infinite parametric domain (e.g. an unclamped Geom_Line), or a curve that has degenerated to (near-)zero length (e.g. coincident control points). Project()/NextProject() must swap the range, special-case infinite bounds, and tolerate…

**Test against:** `Gs029`, `Gp129`, `Gp037`

### `tkshh-shape-unbaked-location-transform`

*TKShHealing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

Shape sub-elements (faces, edges, vertices, or entire branches of a compound) carry a non-identity TopLoc_Location transform applied at the topology level rather than having their geometry expressed directly in absolute/global coordinates. This is a normal and valid OCCT representation, but is inconvenient or actively broken for some consumers/algorithms/round-trips that don't correctly track…

**Test against:** `Tsh098`, `Tsh133`, `A067`

### `tkshh-sliver-solid`

*TKShHealing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A compound/comp-solid contains one or more degenerate 'sliver' solids -- artifacts of Boolean/import operations whose volume is below an application-supplied threshold, and/or whose width factor (volume divided by half its surface area, a proxy for 'thinness') is below a threshold. OCCT repairs this by either deleting the sliver solid outright, or merging it into an adjacent non-small solid…

**Test against:** `Tsh234`, `Tsh235`, `Tsh263`

### `tkshh-solid-globally-inverted-shell`

*TKShHealing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

A solid built from a single closed shell has its overall orientation globally inverted: every face is consistently flipped together, so classifying a point at infinity against the resulting solid reports it as 'inside' (i.e. the shell bounds the complement of the intended region -- material and void are swapped). OCCT repairs this by reversing the entire shell (all faces at once) so the…

**Test against:** `Bo024`, `Ps001`, `Tsh010`

### `tkshh-surface-implicit-degenerate-edge`

*TKShHealing* · 3 fixtures · observed: loads×3 · **3/3 carry a written spec** · corpus coverage: COVERED

An edge segment can be geometrically degenerate in 3D (its two endpoints and midpoint all map to nearly the same 3D point) even though it spans a non-trivial 2D parametric distance and is nowhere near one of the surface's canonical analytic singularities (cone apex, sphere pole, torus pinch). This is detected by comparing the 3D span against the 2D parametric span scaled by the surface's local…

**Test against:** `Gs084`, `Gs098`, `Gs111`

### `bc-empty-wire`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A wire contains no edges.

**Test against:** `Twi001`, `Tsh023`

### `bc-enclosed-region`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A solid contains an internal shell fully enclosed within another shell (a void/nested-solid configuration) that the analyzer flags as needing attention rather than assuming intentional void semantics.

**Test against:** `Tsh015`, `Tsh240`

### `bc-invalid-imbrication-of-wires`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Inner/outer wire nesting on a face is topologically inconsistent (e.g. hole wires improperly nested/overlapping containment levels).

**Test against:** `Tfa056`, `Twi024`

### `bc-invalid-range`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

An edge's declared parametric range (First/Last parameter) does not match the underlying curve's actual valid domain, or the range doesn't bound the edge's own vertex parameters.

**Test against:** `Gp007`, `Gp103`

### `bc-invalid-same-parameter-flag`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

An edge's SameParameter flag asserts 3D-curve-parameter and pcurve-parameter are synchronized (same parameter maps to the same physical point within tolerance), but they are not.

**Test against:** `Gp022`, `Twi065`

### `bc-no-3d-curve`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

An edge has no 3D curve representation at all (only a pcurve, or nothing) where one is required.

**Test against:** `Twi047`, `Twi248`

### `bc-no-curve-on-surface`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

An edge used as a boundary of a face has no pcurve (2D parametric curve) defined for that face's surface.

**Test against:** `Gp175`, `Gp091`

### `bc-not-connected`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Consecutive edges within a wire (or faces within a shell) are not topologically connected — a gap exists between what should be adjoining subshapes.

**Test against:** `Twi003`, `Bo022`

### `bc-redundant-edge`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

The same edge (same TShape) appears more than once within a single wire.

**Test against:** `Tfa074`, `Tfa209`

### `bc-subshape-not-in-shape`

*exchange/brepcheck* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A parent topological entity references a subshape (vertex/edge/wire/face) that is not actually present/bound in the shape's own topology map — an orphan or dangling topological reference (distinct from a dangling STEP-file entity reference; this is a live TopoDS-level inconsistency).

**Test against:** `Bo007`, `Bo003`

### `seq-elementary-to-revolution`

*exchange/heal-sequence* · 2 fixtures · observed: empty×1, loads×1 · **2/2 carry a written spec** · corpus coverage: COVERED

Shapes carrying analytic elementary surfaces (cylinder, cone, sphere, torus) in contexts where the consumer only accepts the surface-of-revolution representation; the mismatch between analytic-canonical and swept representation is the input pattern being normalized.

**Test against:** `Gn013`, `Gn178`

### `seq-fix-face-size`

*exchange/heal-sequence* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Faces of negligible extent — spot faces (all boundary within tolerance of a point) or strip/sliver faces (negligible width) — that carry no real geometry and should be collapsed or merged into neighbors.

**Test against:** `Tfa040`, `Tfa072`

### `seq-same-parameter`

*exchange/heal-sequence* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Edges where the 3D curve and its 2D parameter-space curves are not parameter-synchronized within tolerance (the SameParameter flag/actual deviation is wrong), so evaluating the pcurve and the 3D curve at the same parameter gives points farther apart than the edge tolerance claims.

**Test against:** `Gp022`, `Gp050`

### `seq-split-angle`

*exchange/heal-sequence* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Faces on rotational/angularly-periodic surfaces spanning an angular extent larger than a downstream consumer can handle (e.g. a full 2π cylinder face where the target requires patches under a maximum angle). The input isn't invalid BRep; it is a representation the target cannot digest without angular subdivision.

**Test against:** `Twi032`, `Gs193`

### `seq-split-closed-edges`

*exchange/heal-sequence* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Edges closed onto themselves (start vertex == end vertex, e.g. a full circle as one edge) that some consumers cannot accept; the edge must be divided at one or more interior points into open edges.

**Test against:** `Twi019`, `Twi287`

### `seq-split-common-vertex`

*exchange/heal-sequence* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Two wires of a face sharing a single common vertex (a pinch point). This is legal in the BRep model but illegal in the STEP schema, so the vertex must be duplicated so each wire owns its own. The input pattern (pinched contours meeting at one vertex) is what a fixture would demonstrate.

**Test against:** `Twi009`, `Twi288`

### `seq-to-bezier`

*exchange/heal-sequence* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Geometry (3D curves, pcurves, surfaces — including lines, circles, conics, planes, revolutions, extrusions, B-splines) that a consumer requires in Bezier form; the input pattern is any non-Bezier parametric geometry destined for a Bezier-only target.

**Test against:** `Gn042`, `Gn044`

### `sew-candidate-tiebreak-reciprocity`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

When more than one free edge lies within tolerance of a given reference edge, Sewing must pick exactly one to merge with (in manifold mode). Equidistant candidates are broken by preferring the one whose closest sampled point is nearer (not just insertion order), and — more importantly — a candidate is only finally accepted if it is a mutual/reciprocal best match: the candidate's own best match…

**Test against:** `M045`, `Tsh245`

### `sew-degenerate-edge-passthrough`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Some edges are legitimately zero-length in parameter space by design (e.g. the edge running along a cone's apex, or a seam-collapse point on a sphere) — these are formally 'degenerate' edges, a normal and expected part of valid B-Rep topology, not a defect. Sewing must recognize and pass these through unchanged rather than mistaking them for small/defective edges that need repair or removal.

**Test against:** `Gs189`, `Gs205`

### `sew-duplicate-face-reference-dedup`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

When the same face object is reachable more than once while exploring the input shape(s) (e.g. referenced from two different shells, or appearing twice inside a compound), Sewing processes it only once for boundary-edge discovery, instead of double-counting its edges as though two different faces shared them (which would falsely make genuinely free boundary edges look like…

**Test against:** `Bo007`, `A085`

### `sew-longest-edge-reference-selection`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

When two candidate edges are merged into one, they may not be exactly the same length (e.g. one was trimmed short by an earlier defect). Sewing designates the longer of the two edges' 3D curve and parametrization as the authoritative reference for the merged result, and re-derives/reprojects the shorter edge's contribution (its 2D pcurves) onto that reference, rather than arbitrarily picking…

**Test against:** `N148`, `Tsh246`

### `sew-nonmanifold-candidate-disambiguation`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

At a non-manifold junction where 3+ free edges all lie within tolerance of each other (e.g. three shells meeting along one theoretical edge), Sewing must decide, per adjoining face, which of the several nearby edges is the actual correct match for that face — rather than merging all of them together indiscriminately or merging the wrong pair. It disqualifies a candidate for a given face if…

**Test against:** `M045`, `Tsh248`

### `sew-nonmanifold-multi-edge-merge-chain`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

At a genuinely non-manifold junction, more than two free edges (e.g. three or more shells meeting along a common edge) may all need to become one single merged edge, not just a pairwise merge. Sewing discovers the full set of mutually-contiguous edge fragments (including fragments produced by an earlier Cutting split, tracked via a cutting-node adjacency graph), picks the longest as the…

**Test against:** `M045`, `Tsh249`

### `sew-nonmanifold-shell-unification`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

In non-manifold sewing mode, faces originating from what were, in the input, separate shells can end up sharing a merged (non-manifold) edge after sewing -- meaning they should really belong to one connected shell in the output, not remain as separate disconnected shell fragments. Sewing detects this post-merge by checking whether any two provisional output shells share an edge, and if so,…

**Test against:** `M045`, `Tfa023`

### `sew-per-edge-fault-isolation`

*exchange/sewing* · 2 fixtures · observed: loads×1, empty×1 · **2/2 carry a written spec** · corpus coverage: PARTIAL

Some input edges have geometry pathological enough (e.g. a self-inconsistent 2D/3D curve pairing) that the underlying parameter-synchronization or continuity-encoding algorithms throw an internal exception when processing them. Rather than letting such an exception abort the entire Perform() call and lose all other, successfully-processed geometry, Sewing catches these exceptions at the…

**Test against:** `Twi248`, `Twi247`

### `sew-seam-dual-pcurve-preservation`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A seam edge on a closed/periodic surface (e.g. running along a cylinder's or torus's parametric seam) maps to two different locations in the surface's 2D parameter space depending on which side of the seam you approach from. When such an edge is a participant in a merge, both its forward and reversed 2D-curve representations must be preserved and correctly attached to the resulting merged…

**Test against:** `Tsh209`, `Tsh250`

### `sew-vertex-endpoint-pairing-orientation`

*exchange/sewing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

When merging two edges, their two endpoints must be paired up correctly according to the edges' relative orientation: if the edges run in the same direction the first-to-first, second-to-second pairing is correct, but if one is effectively reversed relative to the other, the pairing must cross (first-to-second, second-to-first) or the merged edge would be twisted. Sewing computes this…

**Test against:** `Tsh176`, `Tsh253`

### `stp-closed-curve-two-vertices`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

An edge is defined on a genuinely closed 3D curve (e.g. a full circle), but its two STEP vertex entities, though geometrically coincident, are distinct entity instances, causing edge construction to fail with a 'different points on closed curve' error. OCCT detects that the underlying curve actually is closed and repairs the topology by treating the second vertex as the same OCCT vertex as the…

**Test against:** `Twi017`, `Gp171`

### `stp-compcurve-disconnected`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

After segment reordering, adjacent COMPOSITE_CURVE segments' endpoints still do not coincide (a genuine gap in the curve's connectivity, not just an ordering problem). OCCT does not fail the whole composite-curve translation for this; it flags the disconnection as a warning and still returns the (locally disconnected) wire for the caller to use or further repair.

**Test against:** `Gp034`, `Gp188`

### `stp-compcurve-reorder`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A COMPOSITE_CURVE's list of segments is not given in connected geometric/topological sequence (successive segments don't follow on from one another in list order). OCCT detects and algorithmically reorders the segments (delegating to ShapeFix_Wire's reordering pass) before assembling them into a single wire, rather than building a disjoint or self-intersecting wire from the segments in their…

**Test against:** `Gp176`, `Gp195`

### `stp-geomset-gri-fallback`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A GEOMETRIC_SET element is none of the directly supported kinds (curve, cartesian point, surface) but is still some geometric representation item. Instead of rejecting it, the element is routed through the general transfer actor as a last-resort fallback so a shape can still be produced for otherwise-unhandled representation item types.

**Test against:** `M196`, `M064`

### `stp-mapped-item-no-transform`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A MAPPED_ITEM (placing one assembly-component shape representation into a using context) provides neither a resolvable CartesianTransformationOperator3d nor a resolvable Origin/Target AXIS2_PLACEMENT_3D pair to compute its placement transform from. Rather than failing the whole component instance, OCCT leaves it at the identity transform (effectively un-positioned) and logs a warning instead…

**Test against:** `Tfa248`, `A119`

### `stp-missing-geometry-definition`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A topological entity references its underlying geometric definition (a VERTEX_POINT's point, an EDGE_CURVE's curve, or a FACE_SURFACE's / CURVE_BOUNDED_SURFACE's basis surface), but that referenced definition is null or could not itself be resolved/translated. OCCT detects this missing-geometry condition per entity and fails cleanly just for that one entity (logged, not crashed), leaving the…

**Test against:** `Tfa252`, `Tfa001`

### `stp-missing-unit-context-default`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A geometry entity is translated in a context where OCCT cannot locate a governing SHAPE_REPRESENTATION (and hence its length/angle unit conversion factors) by walking the STEP entity graph upward -- for instance when an entity is requested for standalone translation, or when a representation is unusually structured. Rather than aborting for lack of units, OCCT falls back to a default…

**Test against:** `U051`, `U052`

### `stp-shell-to-solid-promotion`

*exchange/step-reader* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A non-manifold-enabled STEP model represents what is topologically a closed, single-volume solid purely as loose shells (e.g. via SHELL_BASED_SURFACE_MODEL) without an explicit enclosing SOLID/MANIFOLD_SOLID_BREP entity wrapping them. After translating and non-manifold-fixing the shells, OCCT scans for shells that turn out to be closed and automatically re-wraps each one as a proper…

**Test against:** `Tsh003`, `Tsh258`

### `tkshh-face-area-exceeds-threshold`

*TKShHealing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A single face's surface area exceeds a caller-configured maximum (or exceeds what a fixed target part-count can address), which causes numerical or downstream-meshing problems for excessively large faces. The healer computes the number of sub-parts needed (area / max-area, rounded up), delegates to a surface-splitting tool to grid the surface into that many parts, and recursively re-applies…

**Test against:** `Tfa013`, `Tfa052`

### `tkshh-near-zero-knot-span-thin-patch-filter`

*TKShHealing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A curve or surface's knot vector contains near-duplicate/clustered knots (e.g. from an interior knot inserted to full multiplicity, or STEP data with two knots separated by less than working precision) that would otherwise produce a near-zero-length Bezier arc (2D curve conversion) or a near-zero-extent Bezier patch (surface conversion) after decomposition. These degenerate spans are detected…

**Test against:** `Gn042`, `Gp180`

### `tkshh-shell-free-boundary-gap`

*TKShHealing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Two (or more) faces that geometrically share a boundary curve each carry their own separate copy of that boundary's edges/vertices, so the shell's free (single-face) boundary edges are geometrically coincident but topologically disjoint -- either exactly coincident (pure duplicate) or separated by a small gap that is larger than the sewing tolerance but within an application-specified closing…

**Test against:** `Twi037`, `Tfa020`

### `tkshh-solid-unstructured-multishell`

*TKShHealing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A shape intended to become a solid is built from more than one shell without pre-established outer-boundary/void nesting -- e.g. an unstructured compound of shells that should really be recognized as either (a) an outer boundary shell plus nested internal cavity shell(s) forming one valid solid, or (b) multiple disjoint solids incorrectly bundled together. OCCT repairs this by…

**Test against:** `Tsh236`, `Tsh237`

### `tkshh-vertex-spuriously-shared-across-wires`

*TKShHealing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

A single TopoDS_Vertex object is referenced by two different wires of the same face (e.g., an outer boundary wire and an inner/hole wire, or two hole wires) at a point where they touch. This is representable and tolerated inside OCCT's in-memory BRep model but is invalid for STEP export, where each wire must own distinct vertex instances even at coincident locations. The healer detects such…

**Test against:** `Twi009`, `Twi050`

### `tkshh-wire-duplicate-coincident-vertex-instances`

*TKShHealing* · 2 fixtures · observed: loads×2 · **2/2 carry a written spec** · corpus coverage: COVERED

Two or more edges that are topologically connected (consecutive edges in a wire, or arbitrary edges registered as touching) reference geometrically coincident (within tolerance) but topologically DISTINCT vertex objects, instead of sharing one common vertex. The healer merges the group of coincident vertex instances into a single shared vertex, computing its position as the midpoint of the…

**Test against:** `Twi284`, `Twi285`

### `bc-empty-shell`

*exchange/brepcheck* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A shell contains no faces.

**Test against:** `Bo001`

### `bc-invalid-imbrication-of-shells`

*exchange/brepcheck* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: PARTIAL

Shell nesting within a solid is topologically inconsistent (shells improperly nested).

**Test against:** `Tsh067`

### `bc-no-surface`

*exchange/brepcheck* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A face has no underlying surface geometry at all.

**Test against:** `M193`

### `bc-redundant-face`

*exchange/brepcheck* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

The same face (same TShape) appears more than once within a shell.

**Test against:** `Bo007`

### `bc-redundant-wire`

*exchange/brepcheck* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

The same wire (same TShape) appears more than once in a face's boundary list.

**Test against:** `Gs031`

### `bc-unorientable-shape`

*exchange/brepcheck* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A face or shell's orientation cannot be consistently determined/propagated (e.g. non-orientable surface topology such as a Möbius-like construction).

**Test against:** `Bo005`

### `seq-xsalgo-unit-mismatch`

*exchange/heal-sequence* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

The file's declared length unit differs from the session's target (CASCADE) unit, so translated geometry and all repair tolerances must be scaled by the unit factor before healing; readers pass unit-scaled precision into shape processing so that fixes act at the right physical scale.

**Test against:** `U050`

### `sew-degenerate-free-wire-collapse`

*exchange/sewing* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

After the main merge pass, some free (still-unmatched) boundary edges may form a closed wire loop whose overall size is geometrically negligible (a leftover sliver boundary, e.g. from an originally tiny face or a near-degenerate seam that didn't fully collapse earlier). Rather than leaving this as spurious 'real' free-boundary geometry in the output, Sewing detects such loops and collapses the…

**Test against:** `Tsh242`

### `sew-malformed-subshape-tolerance`

*exchange/sewing* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: PARTIAL

Corrupt or incomplete sub-shape data supplied as part of the input — a null shape entry in the list of added shapes, an edge whose vertex reference is null, or a face whose boundary iteration yields something other than a proper wire — is tolerated by skipping just the offending element, rather than aborting the whole sewing operation or dereferencing a null handle.

**Test against:** `Tfa001`

### `sew-merged-edge-continuity-encoding`

*exchange/sewing* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

After two faces' edges are merged, downstream consumers (e.g. shading, meshing, or further healing steps) often need to know how smoothly the two adjoining faces meet at that edge (sharp corner vs. tangent-continuous vs. curvature-continuous). Sewing computes and encodes this continuity classification on every newly-merged edge shared by exactly two faces. Edges that end up shared by a…

**Test against:** `Tsh247`

### `sew-tiny-edge-face-culling`

*exchange/sewing* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

During pre-sewing face analysis, edges whose length is below tolerance (effectively zero-length, but not degenerate in the formal topological sense) are identified as 'small' and their endpoint vertices are glued together, collapsing the edge; if the accumulation of this leaves a face with every one of its edges marked small (i.e. the whole face has shrunk to a negligible sliver or point), the…

**Test against:** `Tsh091`

### `stp-compcurve-cyclic-ref`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A COMPOSITE_CURVE_SEGMENT's parent curve is (directly) the very COMPOSITE_CURVE it belongs to, i.e. a self-referencing cycle in the curve definition graph that would otherwise send the recursive segment-translation into infinite recursion. OCCT detects the self-reference and drops just that segment instead of recursing or crashing.

**Test against:** `Gs054`

### `stp-compcurve-infinite-segment`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A COMPOSITE_CURVE segment's underlying curve is geometrically unbounded (an infinite first and/or last parameter, e.g. an unterminated line used as a segment), which cannot participate in a normal closed/connected wire. OCCT still builds an edge for it but flags the whole composite curve as containing an infinite segment; downstream (when building a GEOMETRIC_SET member from such a composite…

**Test against:** `Gs055`

### `stp-degenerate-edge-multiface`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A degenerate edge (e.g. at a cone apex or sphere pole) is referenced by several faces. A single shared OCCT edge cannot carry the different pcurves each face needs, so when the cached translation result for an EDGE_CURVE is found to be degenerated, the edge is re-translated separately for the current face (with a warning) instead of reusing the shared result.

**Test against:** `Tsh241`

### `stp-loop-degenerate-edge-drop`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

Within an EDGE_LOOP, one oriented edge references an EDGE_CURVE whose declared start and end vertex are literally the same STEP vertex entity (a self-loop / degenerate edge), and that edge's translation otherwise failed. Instead of failing the whole wire because of this one bad edge, OCCT recognizes the same-vertex signature and silently drops the edge from the wire, letting the rest of the…

**Test against:** `Twi018`

### `stp-polyloop-dup-point`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A FACETED_BREP POLY_LOOP (a faceted polygon boundary given as a flat list of cartesian points) lists the very same point twice in immediate succession, which would otherwise produce a zero-length edge in the resulting wire. OCCT detects the repeat and simply omits the degenerate segment rather than creating a zero-length edge.

**Test against:** `M197`

### `stp-polyloop-nonplanar-surface`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A POLY_LOOP face bound is attached to a face whose underlying surface is not planar, which violates the FACETED_BREP schema's implicit assumption that faceted boundaries are defined on planar surfaces. Rather than rejecting the face, OCCT logs the violation and proceeds anyway, computing the polygon's UV placement via a general surface-projection tool instead of the simpler planar-projection path.

**Test against:** `M055`

### `stp-srr-nauo-reversed`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

In an assembly, the shape representation relationship attached to a CONTEXT_DEPENDENT_SHAPE_REPRESENTATION relates its two representations in the direction opposite to what the governing NEXT_ASSEMBLY_USAGE_OCCURRENCE defines. The reversal is detected, the NAUO's definition is taken as authoritative (with a warning), and the component's placement transformation is applied inverted so the…

**Test against:** `A118`

### `stp-tess-degenerate-triangles`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

Tessellated geometry (TRIANGULATED_FACE / COMPLEX_TRIANGULATED_FACE) whose triangle strips or fans contain index triples that repeat a vertex, i.e. degenerate zero-area triangles. These are detected in both the counting and the population passes and excluded from the built triangulation instead of producing degenerate mesh elements.

**Test against:** `M198`

### `stp-tess-malformed-normals`

*exchange/step-reader* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A tessellated item's normals table does not have exactly three components per row (not valid XYZ vectors). The normals are silently ignored and the mesh is built without them, rather than misreading the data or failing the face.

**Test against:** `M199`

### `tkshh-splitting-vertex-face`

*TKShHealing* · 1 fixtures · observed: loads×1 · **1/1 carry a written spec** · corpus coverage: COVERED

A face contains a vertex that is NOT an endpoint of a given edge of that same face, but whose 3D position projects within tolerance onto the interior of that edge's curve (a geometric T-junction/self-touch that isn't expressed as shared topology). OCCT detects this ('splitting vertex') and repairs it by inserting a synthetic splitting edge from the vertex to its projected point and dividing…

**Test against:** `Tfa249`

