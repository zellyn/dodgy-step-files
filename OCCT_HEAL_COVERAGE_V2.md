# OCCT healing-operation coverage — per-method deep pass (v2)

This is the **second** OCCT coverage pass, built from per-method
enumeration of OCCT's `.cxx` healing implementations. The first pass
([`OCCT_HEAL_COVERAGE.md`](OCCT_HEAL_COVERAGE.md)) was API-surface
only; this one walks the source line by line, isolating each
`if`/`else if` repair branch as a separate coverage unit.

## Totals

| | Count |
|---|---:|
| Methods enumerated | 317 |
| Repair branches enumerated | 3399 |
| COVERED (≥1 fixture matches a search anchor) | 867 (25.5%) |
| UNCOVERED | 2532 |

## Methodology

A master enumerator agent walked OCCT's `TKShHealing` toolkit plus
`BRepLib`, `BRepBuilderAPI_Sewing`, `ShapeCustom`, `ShapeExtend`, and
`ShapeProcess`, producing a list of 320 public methods with line
ranges. ~65 Haiku worker agents then enumerated repair branches in
each method — every `if`/`else if` decision point where the kernel
takes a different repair action for a different defect input. Each
branch carries a list of `search_anchors` (defect-class phrases). The
aggregator regex-matches anchors against catalog entry text;
matching is biased toward false positives over false negatives — what
matters is finding the branches no catalog fixture mentions at all.

All worker outputs were prose-laundered from upstream OCCT source. No
OCCT code or test fixture bytes were copied into this catalog.

## Coverage map

### `...ShapeAnalysis_CheckSmallFace.cxx`

1 methods, 7 branches, 6 covered.

#### `ShapeAnalysis_CheckSmallFace.CheckTwisted` — lines 975–1059
(7 branches, 6 covered.)

- **Branch 1** @ line 978 — *geometry-type* — **UNCOVERED**
  - What it tests: surf->IsKind(STANDARD_TYPE(Geom_ElementarySurface))
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'surf->IsKind(STANDARD_TYPE(Geom_ElementarySurface))'
- **Branch 2** @ line 984 — *tolerance-check* — COVERED by: a032, a097, ad005, ad045, ad049, ad086, ad090, ad095 (+384 more)
  - What it tests: toler < 0
  - Repair action: branch-dispatch
- **Branch 3** @ line 1004 — *validation-gate* — COVERED by: a095, ad086, bo005, bo025, fi003, fi007, gn014, gn020 (+85 more)
  - What it tests: iu = 1; iu <= nbint; iu++
  - Repair action: modify-geometry
- **Branch 4** @ line 1006 — *validation-gate* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1154 more)
  - What it tests: iv = 1; iv <= nbint; iv++
  - Repair action: modify-geometry
- **Branch 5** @ line 1026 — *geometry-type* — COVERED by: a095, ad086, bo005, bo025, fi003, fi007, gn014, gn020 (+85 more)
  - What it tests: iu = 1; iu < nbint; iu++
  - Repair action: branch-dispatch
- **Branch 6** @ line 1028 — *validation-gate* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1154 more)
  - What it tests: iv = 1; iv < nbint; iv++
  - Repair action: branch-dispatch
- **Branch 7** @ line 1033 — *twist-detection* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: if (TwistedNorm(nx(iu, iv),
  - Repair action: branch-dispatch


### `...ShapeAnalysis_Curve.cxx`

1 methods, 5 branches, 0 covered.

#### `ShapeAnalysis_Curve.Project` — lines 212–261
(5 branches, 0 covered.)

- **Branch 1** @ line 217 — *parameter-bounds* — **UNCOVERED**
  - What it tests: Precision::IsInfinite(uMin) && Precision::IsInfinite(uMax)
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'Precision::IsInfinite(uMin)'
- **Branch 2** @ line 231 — *gap-analysis* — **UNCOVERED**
  - What it tests: distmin_L <= prec
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'distmin_L'
- **Branch 3** @ line 238 — *validation-gate* — **UNCOVERED**
  - What it tests: distmin_H <= prec
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'distmin_H'
- **Branch 4** @ line 246 — *validation-gate* — **UNCOVERED**
  - What it tests: distProj < distmin_L + Precision::Confusion(
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'distProj'
- **Branch 5** @ line 252 — *validation-gate* — **UNCOVERED**
  - What it tests: distmin_L < distmin_H
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'distmin_L'


### `...ShapeAnalysis_FreeBounds.cxx`

3 methods, 13 branches, 3 covered.

#### `ShapeAnalysis_FreeBounds.ConnectEdgesToWires` — lines 135–175
(4 branches, 1 covered.)

- **Branch 1** @ line 144 — *Single-edge wire wrapping* — **UNCOVERED**
  - What it tests: for each edge in sequence
  - Repair action: Create wire, add edge
  - Suggested fixture: defect mentioning 'B.MakeWire', 'B.Add(wire'
- **Branch 2** @ line 153 — *Wire-to-wire connection* — **UNCOVERED**
  - What it tests: Call ConnectWiresToWires
  - Repair action: Connect single-edge wires
  - Suggested fixture: defect mentioning 'ConnectWiresToWires'
- **Branch 3** @ line 157 — *Edge orientation correction* — COVERED by: a024, a026, ad047, ad057, ad086, bo001, bo002, bo003 (+142 more)
  - What it tests: iwires orientation==REVERSED
  - Repair action: Reverse input edge
- **Branch 4** @ line 174 — *Wrapper overload dispatch* — **UNCOVERED**
  - What it tests: Signature with reference param
  - Repair action: Delegate to _1 overload
  - Suggested fixture: defect mentioning 'ConnectEdgesToWires(edges'

#### `ShapeAnalysis_FreeBounds.DispatchWires` — lines 609–639
(5 branches, 1 covered.)

- **Branch 1** @ line 615 — *Null closed compound* — **UNCOVERED**
  - What it tests: closed.IsNull()
  - Repair action: Initialize closed compound
  - Suggested fixture: defect mentioning 'MakeCompound'
- **Branch 2** @ line 619 — *Null open compound* — **UNCOVERED**
  - What it tests: open.IsNull()
  - Repair action: Initialize open compound
  - Suggested fixture: defect mentioning 'MakeCompound'
- **Branch 3** @ line 623 — *Null input sequence* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: wires.IsNull()
  - Repair action: Early return
- **Branch 4** @ line 630 — *Closed wire classification* — **UNCOVERED**
  - What it tests: wires->Value(iw).Closed()
  - Repair action: Add to closed compound
  - Suggested fixture: defect mentioning 'B.Add(closed'
- **Branch 5** @ line 635 — *Open wire classification* — **UNCOVERED**
  - What it tests: else case
  - Repair action: Add to open compound
  - Suggested fixture: defect mentioning 'B.Add(open'

#### `ShapeAnalysis_FreeBounds.SplitWires` — lines 588–690
(4 branches, 1 covered.)

- **Branch 1** @ line 598 — *Per-wire split dispatch* — **UNCOVERED**
  - What it tests: for each wire in sequence
  - Repair action: Call SplitWire; append results
  - Suggested fixture: defect mentioning 'SplitWire', 'closed->Append'
- **Branch 2** @ line 650 — *No splitting needed* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: !mySplitClosed && !mySplitOpen
  - Repair action: Early return
- **Branch 3** @ line 660 — *Closed wire splitting enabled* — **UNCOVERED**
  - What it tests: mySplitClosed
  - Repair action: Process closed wires
  - Suggested fixture: defect mentioning 'mySplitClosed'
- **Branch 4** @ line 670 — *Open wire splitting enabled* — **UNCOVERED**
  - What it tests: mySplitOpen
  - Repair action: Process open wires
  - Suggested fixture: defect mentioning 'mySplitOpen'


### `...ShapeAnalysis_FreeBoundsProperties.cxx`

1 methods, 9 branches, 3 covered.

#### `ShapeAnalysis_FreeBoundsProperties.CheckNotches` — lines 302–387
(9 branches, 3 covered.)

- **Branch 1** @ line 308 — *notch-check* — COVERED by: ad086, pmi132, twi074, wr051
  - What it tests: (num <= 0) || (num > wdt->NbEdges())
  - Repair action: validation-gate
- **Branch 2** @ line 322 — *tolerance-check* — **UNCOVERED**
  - What it tests: saw->CheckSmall(n2, tol)
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'saw->CheckSmall(n2,'
- **Branch 3** @ line 335 — *geometry-type* — **UNCOVERED**
  - What it tests: !sae.Curve3d(E1, c3d1, First1, Last1) || !sae.Curve3d(E2,...
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning '!sae.Curve3d(E1,'
- **Branch 4** @ line 344 — *orientation-check* — **UNCOVERED**
  - What it tests: E1.Orientation() == TopAbs_REVERSED
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'E1.Orientation()'
- **Branch 5** @ line 348 — *orientation-check* — **UNCOVERED**
  - What it tests: E2.Orientation() == TopAbs_REVERSED
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'E2.Orientation()'
- **Branch 6** @ line 354 — *validation-gate* — COVERED by: a002, a004, a106, ad005, ad014, ad043, ad081, ad086 (+176 more)
  - What it tests: angl > 0.95 * M_PI
  - Repair action: branch-dispatch
- **Branch 7** @ line 357 — *validation-gate* — COVERED by: a001, a002, a003, a004, a005, a006, a009, a012 (+980 more)
  - What it tests: int i = 0; i < NbControl; i++
  - Repair action: branch-dispatch
- **Branch 8** @ line 363 — *validation-gate* — **UNCOVERED**
  - What it tests: First2 < Last2
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'First2'
- **Branch 9** @ line 377 — *gap-analysis* — **UNCOVERED**
  - What it tests: newDist > distMax
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'newDist'


### `...ShapeAnalysis_Shell.cxx`

4 methods, 12 branches, 3 covered.

#### `ShapeAnalysis_Shell.BadEdges` — lines 280–291
(2 branches, 0 covered.)

- **Branch 1** @ line 282 — *Compound creation* — **UNCOVERED**
  - What it tests: Always execute
  - Repair action: Build empty compound
  - Suggested fixture: defect mentioning 'BRep_Builder', 'MakeCompound'
- **Branch 2** @ line 286 — *Iterate bad edges* — **UNCOVERED**
  - What it tests: myBad.Extent() loop
  - Repair action: Add each to compound
  - Suggested fixture: defect mentioning 'myBad.FindKey', 'B.Add'

#### `ShapeAnalysis_Shell.CheckOrientedShells` — lines 139–244
(5 branches, 1 covered.)

- **Branch 1** @ line 144 — *Null input shape* — COVERED by: in014
  - What it tests: shape.IsNull()
  - Repair action: Return false
- **Branch 2** @ line 155 — *Bad edges detected* — **UNCOVERED**
  - What it tests: CheckEdges(sh, myBad...)
  - Repair action: Record shell and set result=true
  - Suggested fixture: defect mentioning 'CheckEdges', 'myShells.Add'
- **Branch 3** @ line 165 — *Free edge analysis disabled* — **UNCOVERED**
  - What it tests: !alsofree
  - Repair action: Skip free edge mapping
  - Suggested fixture: defect mentioning 'alsofree', 'return res'
- **Branch 4** @ line 177 — *Edge unidirectional* — **UNCOVERED**
  - What it tests: !myBad.Contains(sh) && !revs.Contains(sh)
  - Repair action: Add to myFree
  - Suggested fixture: defect mentioning 'revs.Contains', 'myFree.Add'
- **Branch 5** @ line 181 — *Internal edge present* — **UNCOVERED**
  - What it tests: checkinternaledges && !ints.Contains(sh)
  - Repair action: Add to myFree or set myConex
  - Suggested fixture: defect mentioning 'ints.Contains', 'myConex'

#### `ShapeAnalysis_Shell.FreeEdges` — lines 302–313
(2 branches, 0 covered.)

- **Branch 1** @ line 304 — *Compound creation* — **UNCOVERED**
  - What it tests: Always execute
  - Repair action: Build empty compound
  - Suggested fixture: defect mentioning 'MakeCompound'
- **Branch 2** @ line 307 — *Iterate free edges* — **UNCOVERED**
  - What it tests: myFree.Extent() loop
  - Repair action: Add each to compound
  - Suggested fixture: defect mentioning 'myFree.FindKey', 'B.Add'

#### `ShapeAnalysis_Shell.LoadShells` — lines 45–64
(3 branches, 2 covered.)

- **Branch 1** @ line 47 — *Null shape* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: shape.IsNull()
  - Repair action: Early return
- **Branch 2** @ line 52 — *Shape is shell* — **UNCOVERED**
  - What it tests: shape.ShapeType() == TopAbs_SHELL
  - Repair action: Add directly to myShells
  - Suggested fixture: defect mentioning 'myShells.Add', 'TopAbs_SHELL'
- **Branch 3** @ line 58 — *Shape contains shells* — COVERED by: tsh018
  - What it tests: else branch
  - Repair action: Extract nested shells via TopExp_Explorer


### `...ShapeAnalysis_Wire.cxx`

2 methods, 24 branches, 9 covered.

#### `ShapeAnalysis_Wire.CheckShapeConnect` — lines 2117–2203
(13 branches, 4 covered.)

- **Branch 1** @ line 2119 — *validation-gate* — **UNCOVERED**
  - What it tests: !IsLoaded() || shape.IsNull()
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning '!IsLoaded()'
- **Branch 2** @ line 2127 — *validation-gate* — **UNCOVERED**
  - What it tests: shape.ShapeType() == TopAbs_EDGE
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'shape.ShapeType()'
- **Branch 3** @ line 2133 — *validation-gate* — **UNCOVERED**
  - What it tests: shape.ShapeType() == TopAbs_WIRE
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'shape.ShapeType()'
- **Branch 4** @ line 2159 — *validation-gate* — **UNCOVERED**
  - What it tests: tailhead > tailtail
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'tailhead'
- **Branch 5** @ line 2164 — *validation-gate* — **UNCOVERED**
  - What it tests: headtail > headhead
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'headtail'
- **Branch 6** @ line 2172 — *validation-gate* — **UNCOVERED**
  - What it tests: dm1 > dm2
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'dm1'
- **Branch 7** @ line 2177 — *validation-gate* — COVERED by: gs044
  - What it tests: multi-branch condition
  - Repair action: iteration-control
- **Branch 8** @ line 2179 — *validation-gate* — COVERED by: a008, ad045, ad049, ad086, ad090, bo001, bo003, gn001 (+59 more)
  - What it tests: case 1:
  - Repair action: iteration-control
- **Branch 9** @ line 2182 — *validation-gate* — COVERED by: a008, ad045, ad049, ad086, ad090, bo001, bo003, gn001 (+59 more)
  - What it tests: case 2:
  - Repair action: iteration-control
- **Branch 10** @ line 2185 — *validation-gate* — COVERED by: a008, ad045, ad049, ad086, ad090, bo001, bo003, gn001 (+59 more)
  - What it tests: case 3:
  - Repair action: iteration-control
- **Branch 11** @ line 2189 — *validation-gate* — **UNCOVERED**
  - What it tests: !res1
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning '!res1'
- **Branch 12** @ line 2193 — *validation-gate* — **UNCOVERED**
  - What it tests: !res2
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning '!res2'
- **Branch 13** @ line 2198 — *validation-gate* — **UNCOVERED**
  - What it tests: myMin3d > std::max(myPrecision, prec)
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'myMin3d'

#### `ShapeAnalysis_Wire.CheckSmallArea` — lines 2005–2099
(11 branches, 5 covered.)

- **Branch 1** @ line 2009 — *validation-gate* — **UNCOVERED**
  - What it tests: !IsReady() || NbEdges < 1
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 2021 — *closure-test* — COVERED by: a001, a002, a003, a004, a005, a006, a009, a012 (+980 more)
  - What it tests: int j = 1; j <= NbEdges; ++j
  - Repair action: branch-dispatch
- **Branch 3** @ line 2024 — *geometry-type* — **UNCOVERED**
  - What it tests: !anAnalyzer.PCurve(myWire->Edge(j), myFace, aCurve2d, aF,...
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning '!anAnalyzer.PCurve(myWire->Edge(j),'
- **Branch 4** @ line 2030 — *validation-gate* — COVERED by: a001, a002, a003, a004, a005, a006, a009, a012 (+980 more)
  - What it tests: int i = 1; i < aNbControl; ++i
  - Repair action: branch-dispatch
- **Branch 5** @ line 2044 — *geometry-type* — COVERED by: a001, a002, a003, a004, a005, a006, a009, a012 (+980 more)
  - What it tests: int j = 1; j <= NbEdges; ++j
  - Repair action: branch-dispatch
- **Branch 6** @ line 2047 — *geometry-type* — **UNCOVERED**
  - What it tests: !anAnalizer.Curve3d(myWire->Edge(j), aCurve3d, aF, aL)
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning '!anAnalizer.Curve3d(myWire->Edge(j),'
- **Branch 7** @ line 2052 — *validation-gate* — **UNCOVERED**
  - What it tests: Precision::IsInfinite(aF) || Precision::IsInfinite(aL)
  - Repair action: iteration-control
  - Suggested fixture: defect mentioning 'Precision::IsInfinite(aF)'
- **Branch 8** @ line 2058 — *validation-gate* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1004 more)
  - What it tests: j == 1
  - Repair action: branch-dispatch
- **Branch 9** @ line 2064 — *geometry-type* — COVERED by: a001, a002, a003, a004, a005, a006, a009, a012 (+980 more)
  - What it tests: int i = aBegin; i < aNbControl; ++i
  - Repair action: branch-dispatch
- **Branch 10** @ line 2080 — *tolerance-check* — **UNCOVERED**
  - What it tests: aCross.Modulus() < aTolerance
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'aCross.Modulus()'
- **Branch 11** @ line 2091 — *tolerance-check* — **UNCOVERED**
  - What it tests: std::abs(aProps.Mass()) < 0.5 * aNewTolerance
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'std::abs(aProps.Mass())'


### `...ShapeFix_IntersectionTool.cxx`

1 methods, 10 branches, 0 covered.

#### `ShapeFix_IntersectionTool.CutEdge` — lines 199–262
(10 branches, 0 covered.)

- **Branch 1** @ line 200 — *validation-gate* — **UNCOVERED**
  - What it tests: std::abs(cut - pend) < 10. * Precision::PConfusion()
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'std::abs(cut'
- **Branch 2** @ line 208 — *parameter-bounds* — **UNCOVERED**
  - What it tests: aRange < 10. * Precision::PConfusion()
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'aRange'
- **Branch 3** @ line 214 — *parameter-bounds* — **UNCOVERED**
  - What it tests: !BRep_Tool::SameParameter(edge)
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning '!BRep_Tool::SameParameter(edge)'
- **Branch 4** @ line 219 — *geometry-type* — **UNCOVERED**
  - What it tests: sae.PCurve(edge, face, Crv, fp, lp, false)
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'sae.PCurve(edge,'
- **Branch 5** @ line 221 — *geometry-type* — **UNCOVERED**
  - What it tests: Crv->IsKind(STANDARD_TYPE(Geom2d_TrimmedCurve))
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'Crv->IsKind(STANDARD_TYPE(Geom2d_TrimmedCurve))'
- **Branch 6** @ line 224 — *geometry-type* — **UNCOVERED**
  - What it tests: tc->BasisCurve()->IsKind(STANDARD_TYPE(Geom2d_Line))
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'tc->BasisCurve()->IsKind(STANDARD_TYPE(Geom2d_Line))'
- **Branch 7** @ line 228 — *parameter-bounds* — **UNCOVERED**
  - What it tests: std::abs(pend - lp) < Precision::PConfusion()
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'std::abs(pend'
- **Branch 8** @ line 234 — *parameter-bounds* — **UNCOVERED**
  - What it tests: std::abs(pend - fp) < Precision::PConfusion()
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'std::abs(pend'
- **Branch 9** @ line 249 — *parameter-bounds* — **UNCOVERED**
  - What it tests: std::abs(std::abs(a - b) - aRange) < Precision::PConfusion()
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'std::abs(std::abs(a'
- **Branch 10** @ line 253 — *parameter-bounds* — **UNCOVERED**
  - What it tests: aRange < 10. * Precision::PConfusion()
  - Repair action: validation-gate
  - Suggested fixture: defect mentioning 'aRange'


### `...ShapeFix_SplitCommonVertex.cxx`

1 methods, 9 branches, 4 covered.

#### `ShapeFix_SplitCommonVertex.Perform` — lines 62–160
(9 branches, 4 covered.)

- **Branch 1** @ line 64 — *Shape type filter* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: st > TopAbs_FACE
  - Repair action: Early return
- **Branch 2** @ line 81 — *Context apply fails* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: F.IsNull()
  - Repair action: Skip to next face
- **Branch 3** @ line 87 — *Single-wire face* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: wires.Length() < 2
  - Repair action: Skip face (no common vertices)
- **Branch 4** @ line 108 — *Common vertex between wires* — **UNCOVERED**
  - What it tests: V1 == V2
  - Repair action: Create/reuse new vertex
  - Suggested fixture: defect mentioning 'MapVV.IsBound', 'B.MakeVertex'
- **Branch 5** @ line 112 — *Vertex already split* — **UNCOVERED**
  - What it tests: MapVV.IsBound(V2)
  - Repair action: Retrieve new vertex from map
  - Suggested fixture: defect mentioning 'MapVV.Find'
- **Branch 6** @ line 132 — *Edge first-vertex coincidence* — **UNCOVERED**
  - What it tests: FV == V2
  - Repair action: Replace first vertex
  - Suggested fixture: defect mentioning 'FV = Vnew'
- **Branch 7** @ line 137 — *Edge last-vertex coincidence* — **UNCOVERED**
  - What it tests: LV == V2
  - Repair action: Replace last vertex
  - Suggested fixture: defect mentioning 'LV = Vnew'
- **Branch 8** @ line 142 — *Edge vertex replacement* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+33 more)
  - What it tests: IsCoinc
  - Repair action: Replace edge via CopyReplaceVertices
- **Branch 9** @ line 153 — *Splits recorded* — **UNCOVERED**
  - What it tests: !MapVV.IsEmpty()
  - Repair action: Send warning message
  - Suggested fixture: defect mentioning 'SendWarning', 'MapVV.IsEmpty'


### `...ShapeProcess_OperLibrary.cxx`

2 methods, 8 branches, 3 covered.

#### `ShapeProcess_OperLibrary.ApplyModifier` — lines 55–110
(5 branches, 2 covered.)

- **Branch 1** @ line 67 — *Compound shape input* — COVERED by: a017, a018, a066, a067, a072, a073, a078, ad086 (+43 more)
  - What it tests: SF.ShapeType() == TopAbs_COMPOUND
  - Repair action: Process components recursively with sharing cache
- **Branch 2** @ line 79 — *Component cached* — **UNCOVERED**
  - What it tests: map.IsBound(shape)
  - Repair action: Retrieve from cache; skip recomputation
  - Suggested fixture: defect mentioning 'map.IsBound', 'map.Find'
- **Branch 3** @ line 88 — *Component modified* — **UNCOVERED**
  - What it tests: !res.IsSame(shape)
  - Repair action: Mark compound modified
  - Suggested fixture: defect mentioning 'IsSame', 'locModified=true'
- **Branch 4** @ line 95 — *No component changes* — COVERED by: le049, twi074
  - What it tests: !locModified
  - Repair action: Return original shape
- **Branch 5** @ line 105 — *Non-compound shape* — **UNCOVERED**
  - What it tests: SF.ShapeType() != COMPOUND
  - Repair action: Apply BRepTools_Modifier directly
  - Suggested fixture: defect mentioning 'BRepTools_Modifier', 'MD.Perform'

#### `ShapeProcess_OperLibrary.Init` — lines 982–1013
(3 branches, 1 covered.)

- **Branch 1** @ line 984 — *Duplicate initialization* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: done == true
  - Repair action: Early return
- **Branch 2** @ line 991 — *ShapeExtend not initialized* — **UNCOVERED**
  - What it tests: Entry point
  - Repair action: Call ShapeExtend::Init()
  - Suggested fixture: defect mentioning 'ShapeExtend::Init'
- **Branch 3** @ line 993 — *DirectFaces operator missing* — **UNCOVERED**
  - What it tests: RegisterOperator loop
  - Repair action: Register all 13 OCCT operators
  - Suggested fixture: defect mentioning 'RegisterOperator', 'directfaces'


### `...ShapeProcess_ShapeContext.cxx`

3 methods, 20 branches, 12 covered.

#### `ShapeProcess_ShapeContext.GetContinuity` — lines 415–460
(6 branches, 6 covered.)

- **Branch 1** @ line 418 — *Missing parameter* — COVERED by: in014
  - What it tests: !GetString(param, str)
  - Repair action: Return false
- **Branch 2** @ line 427 — *C0 continuity requested* — COVERED by: a083, ad086, bo025, gb003, gn012, gp033, gs025, gs048 (+10 more)
  - What it tests: str.IsEqual("C0")
  - Repair action: Set cont=GeomAbs_C0
- **Branch 3** @ line 431 — *G1 continuity requested* — COVERED by: a022, ad043, ad086, bo025, bo028, gn016, gp008, gp028 (+25 more)
  - What it tests: str.IsEqual("G1")
  - Repair action: Set cont=GeomAbs_G1
- **Branch 4** @ line 435 — *C1 continuity requested* — COVERED by: ad086, bo028, gb003, gn012, gp012, gp033, gs025, gs049 (+4 more)
  - What it tests: str.IsEqual("C1")
  - Repair action: Set cont=GeomAbs_C1
- **Branch 5** @ line 439 — *G2 continuity requested* — COVERED by: a009, a025, ad043, ad045, ad047, ad050, ad086, gn011 (+20 more)
  - What it tests: str.IsEqual("G2")
  - Repair action: Set cont=GeomAbs_G2
- **Branch 6** @ line 443 — *C2 continuity requested* — COVERED by: a098, gn011, gn026, gp008, gs058, lh009, lh019, m135 (+4 more)
  - What it tests: str.IsEqual("C2")
  - Repair action: Set cont=GeomAbs_C2

#### `ShapeProcess_ShapeContext.PrintStatistics` — lines 473–555
(7 branches, 2 covered.)

- **Branch 1** @ line 481 — *Deleted shell mapping* — **UNCOVERED**
  - What it tests: valueshape.IsNull() && key.ShapeType()==SHELL
  - Repair action: Increment SN (null shell)
  - Suggested fixture: defect mentioning 'IsNull', 'SN++'
- **Branch 2** @ line 488 — *Preserved shell mapping* — **UNCOVERED**
  - What it tests: !valueshape.IsNull() && key.ShapeType()==SHELL
  - Repair action: Increment SS (shell->shell)
  - Suggested fixture: defect mentioning 'SS++'
- **Branch 3** @ line 492 — *Deleted face mapping* — **UNCOVERED**
  - What it tests: valueshape.IsNull() && key.ShapeType()==FACE
  - Repair action: Increment FN (null face)
  - Suggested fixture: defect mentioning 'FN++'
- **Branch 4** @ line 498 — *Face to shell mapping* — **UNCOVERED**
  - What it tests: valueshape.ShapeType()==SHELL
  - Repair action: Increment FS (face->shell)
  - Suggested fixture: defect mentioning 'FS++', 'TopAbs_SHELL'
- **Branch 5** @ line 504 — *Face to face mapping* — **UNCOVERED**
  - What it tests: else case
  - Repair action: Increment FF (face->face)
  - Suggested fixture: defect mentioning 'FF++'
- **Branch 6** @ line 539 — *Zero shell population* — COVERED by: hea003, hea004, hea005, hea008, p008, p009, tb008, wr007
  - What it tests: NbS > 0
  - Repair action: Calculate shell prep ratio SPR
- **Branch 7** @ line 543 — *Zero face population* — COVERED by: a079
  - What it tests: NbF > 0
  - Repair action: Calculate face prep ratio FPR

#### `ShapeProcess_ShapeContext.RecordModification` — lines 247–411
(7 branches, 4 covered.)

- **Branch 1** @ line 251 — *Empty replacement map* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: repl.Extent() <= 0
  - Repair action: Early return; skip map update
- **Branch 2** @ line 283 — *Shape already mapped* — **UNCOVERED**
  - What it tests: map.IsBound(r)
  - Repair action: Retrieve from map before status check
  - Suggested fixture: defect mentioning 'map.IsBound', 'map.Find'
- **Branch 3** @ line 290 — *Shape modified in repl* — COVERED by: a003, ad043, ad045, ad056, ad086, ad119, gb001, gb002 (+34 more)
  - What it tests: repl->Status(r, res, true) && res != r
  - Repair action: Bind modified result to map
- **Branch 4** @ line 297 — *Shape hierarchy type mismatch* — COVERED by: a019, a028, a038, ad056, ad086, gn035, gp014, gp018 (+40 more)
  - What it tests: r.ShapeType() < S.ShapeType()
  - Repair action: Apply modifier at parent level
- **Branch 5** @ line 308 — *Message propagation required* — **UNCOVERED**
  - What it tests: msgmap.IsBound(cur)
  - Repair action: Forward messages through substitution chain
  - Suggested fixture: defect mentioning 'msgmap', 'myMsg->Send'
- **Branch 6** @ line 332 — *Recursion depth limit* — COVERED by: ad004, ad098, le014, le015, le037, le057, n005, n038 (+12 more)
  - What it tests: until == TopAbs_SHAPE || S.ShapeType() >= until
  - Repair action: Terminate recursive descent
- **Branch 7** @ line 363 — *Null message registrator* — **UNCOVERED**
  - What it tests: msg parameter is null
  - Repair action: Delegate to overload with null msg
  - Suggested fixture: defect mentioning 'occ::handle<ShapeExtend_MsgRegistrator>', 'RecordModification'


### `...ShapeUpgrade_SplitSurface.cxx`

1 methods, 7 branches, 1 covered.

#### `ShapeUpgrade_SplitSurface.Init` — lines 88–171
(7 branches, 1 covered.)

- **Branch 1** @ line 104 — *geometry-type* — **UNCOVERED**
  - What it tests: mySurface->IsUPeriodic() && ULast - UFirst <= U2 - U1 + p...
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'mySurface->IsUPeriodic()'
- **Branch 2** @ line 109 — *geometry-type* — **UNCOVERED**
  - What it tests: mySurface->IsVPeriodic() && VLast - VFirst <= V2 - V1 + p...
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'mySurface->IsVPeriodic()'
- **Branch 3** @ line 115 — *geometry-type* — **UNCOVERED**
  - What it tests: UFirst > U2 - precision || ULast < U1 - precision
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'UFirst'
- **Branch 4** @ line 125 — *validation-gate* — **UNCOVERED**
  - What it tests: VFirst > V2 - precision || VLast < V1 - precision
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'VFirst'
- **Branch 5** @ line 136 — *validation-gate* — **UNCOVERED**
  - What it tests: myArea != 0.
  - Repair action: modify-geometry
  - Suggested fixture: defect mentioning 'myArea'
- **Branch 6** @ line 154 — *validation-gate* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1186 more)
  - What it tests: UL - UF < precision
  - Repair action: branch-dispatch
- **Branch 7** @ line 160 — *validation-gate* — **UNCOVERED**
  - What it tests: VL - VF < precision
  - Repair action: branch-dispatch
  - Suggested fixture: defect mentioning 'VL'


### `Multiple files`

3 methods, 42 branches, 2 covered.

#### `BRepLib.CheckSameRange` — lines 149–183
(6 branches, 0 covered.)

- **Branch 1** @ line 160 — *curve_representation_iteration* — **UNCOVERED**
  - What it tests: More curve representations exist to check
  - Repair action: loop through all curve representations on edge
  - Suggested fixture: defect mentioning 'while (IsSameRange && an_Iterator.More())'
- **Branch 2** @ line 162 — *geometric_curve_type_check* — **UNCOVERED**
  - What it tests: Representation is valid GCurve vs other curve type
  - Repair action: process only valid geometric curves; skip invalid types
  - Suggested fixture: defect mentioning 'occ::down_cast<BRep_GCurve>', '!geometric_representation_ptr.IsNull()'
- **Branch 3** @ line 168 — *first_curve_baseline* — **UNCOVERED**
  - What it tests: First curve in iteration vs subsequent curves
  - Repair action: save first curve range as baseline for comparison
  - Suggested fixture: defect mentioning 'first_time_in'
- **Branch 4** @ line 176 — *range_mismatch_detection* — **UNCOVERED**
  - What it tests: Current curve range matches baseline within tolerance
  - Repair action: set IsSameRange false if mismatch detected
  - Suggested fixture: defect mentioning 'std::abs(current_first - first) <= Tolerance'
- **Branch 5** @ line 176 — *first_param_tolerance_check* — **UNCOVERED**
  - What it tests: First parameter deviation exceeds tolerance
  - Repair action: mark edge as not same range; flag defect
  - Suggested fixture: defect mentioning 'std::abs(current_first - first)'
- **Branch 6** @ line 177 — *last_param_tolerance_check* — **UNCOVERED**
  - What it tests: Last parameter deviation exceeds tolerance
  - Repair action: mark edge as not same range; flag defect
  - Suggested fixture: defect mentioning 'std::abs(current_last - last)'

#### `BRepLib.ExtendFace` — lines 3127–3295
(20 branches, 1 covered.)

- **Branch 1** @ line 3146 — *surface_type_classification* — COVERED by: gn014, n030
  - What it tests: Analytical surface (Plane/Sphere/Cylinder/Torus/Cone) vs general bounded surface
  - Repair action: use analytical bounds adjustment vs use GeomLib extension
- **Branch 2** @ line 3158 — *u_periodicity_detection* — **UNCOVERED**
  - What it tests: Surface is U-periodic vs non-periodic
  - Repair action: adjust face bounds to first period and add delta
  - Suggested fixture: defect mentioning 'isUPeriodic', 'anUPeriod'
- **Branch 3** @ line 3168 — *v_periodicity_detection* — **UNCOVERED**
  - What it tests: Surface is V-periodic vs non-periodic
  - Repair action: adjust face bounds to first period and add delta
  - Suggested fixture: defect mentioning 'isVPeriodic', 'aVPeriod'
- **Branch 4** @ line 3178 — *u_extension_request* — **UNCOVERED**
  - What it tests: UMin or UMax extension requested
  - Repair action: compute U resolution for extension parameter
  - Suggested fixture: defect mentioning 'theExtUMin || theExtUMax', 'anURes'
- **Branch 5** @ line 3182 — *v_extension_request* — **UNCOVERED**
  - What it tests: VMin or VMax extension requested
  - Repair action: compute V resolution for extension parameter
  - Suggested fixture: defect mentioning 'theExtVMin || theExtVMax', 'aVRes'
- **Branch 6** @ line 3187 — *umin_extension* — **UNCOVERED**
  - What it tests: Extend UMin direction requested
  - Repair action: subtract resolution from UMin, clamped to surface minimum
  - Suggested fixture: defect mentioning 'theExtUMin', 'aFUMin = std::max'
- **Branch 7** @ line 3191 — *umax_extension* — **UNCOVERED**
  - What it tests: Extend UMax direction requested
  - Repair action: add resolution to UMax, clamped to surface max or periodic period
  - Suggested fixture: defect mentioning 'theExtUMax', 'aFUMax = std::min'
- **Branch 8** @ line 3193 — *umax_periodic_bounds* — **UNCOVERED**
  - What it tests: U-periodic vs non-periodic for UMax clamping
  - Repair action: use period-based bound vs absolute surface maximum
  - Suggested fixture: defect mentioning 'isUPeriodic ? aFUMin + anUPeriod : aSUMax'
- **Branch 9** @ line 3195 — *vmin_extension* — **UNCOVERED**
  - What it tests: Extend VMin direction requested
  - Repair action: subtract resolution from VMin, clamped to surface minimum
  - Suggested fixture: defect mentioning 'theExtVMin', 'aFVMin = std::max'
- **Branch 10** @ line 3199 — *vmax_extension* — **UNCOVERED**
  - What it tests: Extend VMax direction requested
  - Repair action: add resolution to VMax, clamped to surface max or periodic period
  - Suggested fixture: defect mentioning 'theExtVMax', 'aFVMax = std::min'
- **Branch 11** @ line 3201 — *vmax_periodic_bounds* — **UNCOVERED**
  - What it tests: V-periodic vs non-periodic for VMax clamping
  - Repair action: use period-based bound vs absolute surface maximum
  - Suggested fixture: defect mentioning 'isVPeriodic ? aFVMin + aVPeriod : aSVMax'
- **Branch 12** @ line 3207 — *u_closes_to_periodic* — **UNCOVERED**
  - What it tests: Extended bounds equal one full U period
  - Repair action: use full surface bounds (make face closed in U)
  - Suggested fixture: defect mentioning 'isUPeriodic && std::abs(aFUMax - aFUMin - anUPeriod)'
- **Branch 13** @ line 3212 — *v_closes_to_periodic* — **UNCOVERED**
  - What it tests: Extended bounds equal one full V period
  - Repair action: use full surface bounds (make face closed in V)
  - Suggested fixture: defect mentioning 'isVPeriodic && std::abs(aFVMax - aFVMin - aVPeriod)'
- **Branch 14** @ line 3226 — *unbounded_surface_fallback* — **UNCOVERED**
  - What it tests: Bounded surface conversion fails for general surface
  - Repair action: return input face unchanged; extension not possible
  - Suggested fixture: defect mentioning 'aSB.IsNull()'
- **Branch 15** @ line 3243 — *general_umin_extension* — **UNCOVERED**
  - What it tests: UMin extension requested and surface not closed and UMin finite
  - Repair action: extend surface by length in U direction, min side
  - Suggested fixture: defect mentioning 'theExtUMin && !isUClosed && !Precision::IsInfinite(aSUMin)'
- **Branch 16** @ line 3249 — *general_umax_extension* — **UNCOVERED**
  - What it tests: UMax extension requested and surface not closed and UMax finite
  - Repair action: extend surface by length in U direction, max side
  - Suggested fixture: defect mentioning 'theExtUMax && !isUClosed && !Precision::IsInfinite(aSUMax)'
- **Branch 17** @ line 3255 — *general_vmin_extension* — **UNCOVERED**
  - What it tests: VMin extension requested and surface not closed and VMin finite
  - Repair action: extend surface by length in V direction, min side
  - Suggested fixture: defect mentioning 'theExtVMin && !isVClosed && !Precision::IsInfinite(aSVMax)'
- **Branch 18** @ line 3261 — *general_vmax_extension* — **UNCOVERED**
  - What it tests: VMax extension requested and surface not closed and VMax finite
  - Repair action: extend surface by length in V direction, max side
  - Suggested fixture: defect mentioning 'theExtVMax && !isVClosed && !Precision::IsInfinite(aSVMax)'
- **Branch 19** @ line 3271 — *extended_bounds_sync* — **UNCOVERED**
  - What it tests: UMin/UMax/VMin/VMax extension flags after surface extension
  - Repair action: update face bounds from extended surface bounds
  - Suggested fixture: defect mentioning 'if (isExtUMin)', 'aFUMin = aSUMin'
- **Branch 20** @ line 3291 — *output_orientation* — **UNCOVERED**
  - What it tests: Input face is reversed vs forward
  - Repair action: reverse output extended face to match input orientation
  - Suggested fixture: defect mentioning 'theF.Orientation() == TopAbs_REVERSED'

#### `ShapeFix_Wire.FixTails` — lines 4314–4478
(16 branches, 1 covered.)

- **Branch 1** @ line 4316 — *uninitialized_parameter* — **UNCOVERED**
  - What it tests: Check if maxTailWidth is valid or wire not ready
  - Repair action: early return false; skip all repairs
  - Suggested fixture: defect mentioning 'myMaxTailWidth < 0', '!IsReady()'
- **Branch 2** @ line 4322 — *context_management* — **UNCOVERED**
  - What it tests: If Context exists vs is null
  - Repair action: call UpdateWire() to sync wire data with context
  - Suggested fixture: defect mentioning '!Context().IsNull()'
- **Branch 3** @ line 4329 — *edge_sequence_bounds* — **UNCOVERED**
  - What it tests: Edge count >= 2 and iteration can proceed
  - Repair action: loop through pairs of consecutive edges checking for tails
  - Suggested fixture: defect mentioning 'aECount >= 2', 'aENs[1] <= aECount'
- **Branch 4** @ line 4333 — *tail_geometry_defect* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: CheckTail returns false (no tail found vs tail detected)
  - Repair action: continue to next pair; increment index and reset angle check
- **Branch 5** @ line 4351 — *split_count_constraint* — **UNCOVERED**
  - What it tests: Result would leave fewer than 1 edge after removal
  - Repair action: skip repair to preserve minimum edge count
  - Suggested fixture: defect mentioning 'aECount + aSplitCounts[0] + aSplitCounts[1] < 1 + aRemoveCount'
- **Branch 6** @ line 4361 — *partial_tail_split* — **UNCOVERED**
  - What it tests: First edge has no split part vs has split
  - Repair action: skip to next edge in the split loop
  - Suggested fixture: defect mentioning 'aSplitCounts[aEI] == 0'
- **Branch 7** @ line 4368 — *context_edge_replacement* — **UNCOVERED**
  - What it tests: Context exists to handle edge-to-wire replacement
  - Repair action: replace edge with wire of its parts in shape context
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Replace(aFE, aEWire)'
- **Branch 8** @ line 4379 — *edge_orientation* — **UNCOVERED**
  - What it tests: Which part comes first based on FORWARD/REVERSED orientation
  - Repair action: reorder split parts to maintain orientation
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'aFirstPI'
- **Branch 9** @ line 4389 — *dual_tail_removal* — **UNCOVERED**
  - What it tests: Both edges removed vs one edge removed
  - Repair action: remove dummy seam and restart scan; set done status
  - Suggested fixture: defect mentioning 'aRemoveCount == 2'
- **Branch 10** @ line 4399 — *split_count_symmetry* — **UNCOVERED**
  - What it tests: Both edges split by 1 vs asymmetric split
  - Repair action: advance to next edge pair; continue outer loop
  - Suggested fixture: defect mentioning 'aSplitCounts[0] + aSplitCounts[1] == 2'
- **Branch 11** @ line 4405 — *dual_split_count* — **UNCOVERED**
  - What it tests: Both edges split equally vs unequal split
  - Repair action: decrement edge count by 2; reposition scan indices
  - Suggested fixture: defect mentioning 'aSplitCounts[0] == aSplitCounts[1]'
- **Branch 12** @ line 4408 — *scan_position_boundary* — **UNCOVERED**
  - What it tests: Second index >= 3 vs boundary case
  - Repair action: decrement both indices vs reset to wrap around
  - Suggested fixture: defect mentioning 'aENs[1] >= 3'
- **Branch 13** @ line 4422 — *single_tail_removal* — **UNCOVERED**
  - What it tests: Only one edge removed; select which one
  - Repair action: decrement edge count; reposition scan based on split result
  - Suggested fixture: defect mentioning '--aECount'
- **Branch 14** @ line 4446 — *partial_split_selection* — **UNCOVERED**
  - What it tests: Which edge is not removed based on split result
  - Repair action: select index of remaining split edge for reposition
  - Suggested fixture: defect mentioning 'aEParts[0][0].IsNull()'
- **Branch 15** @ line 4467 — *edge_removal_index* — **UNCOVERED**
  - What it tests: Compute removal index based on edge and split status
  - Repair action: remove specific edge from wire data
  - Suggested fixture: defect mentioning 'aSEWD->Remove'
- **Branch 16** @ line 4468 — *context_edge_removal* — **UNCOVERED**
  - What it tests: Context exists to handle edge removal
  - Repair action: remove edge from parent shape context
  - Suggested fixture: defect mentioning 'Context()->Remove'


### `ShapeAnalysis_ShapeTolerance.cxx, ShapeFix_ShapeTolerance.cxx`

6 methods, 61 branches, 19 covered.

#### `ShapeAnalysis_ShapeTolerance.AddTolerance` — lines 240–300
(7 branches, 2 covered.)

- **Branch 1** @ line 248 — *shape_type_selector* — COVERED by: tsh018
  - What it tests: Face iteration: explicit FACE type or wildcard SHAPE
  - Repair action: Accumulates face tolerances via AddTol helper
- **Branch 2** @ line 261 — *shape_type_selector* — **UNCOVERED**
  - What it tests: Edge iteration: explicit EDGE type or wildcard SHAPE
  - Repair action: Accumulates edge tolerances via AddTol helper
  - Suggested fixture: defect mentioning 'TopAbs_EDGE', 'TopAbs_SHAPE'
- **Branch 3** @ line 274 — *shape_type_selector* — **UNCOVERED**
  - What it tests: Vertex iteration: explicit VERTEX type or wildcard SHAPE
  - Repair action: Accumulates vertex tolerances via AddTol helper
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX', 'TopAbs_SHAPE'
- **Branch 4** @ line 286 — *empty_collection_guard* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: No sub-shapes found: nbt == 0
  - Repair action: Early return to avoid division by zero and NaN propagation
- **Branch 5** @ line 290 — *min_tolerance_tracking* — **UNCOVERED**
  - What it tests: Update min tolerance on first accumulation or when smaller
  - Repair action: Sets myTols[0] = cmin when myNbTol == 0 or cmin is lower
  - Suggested fixture: defect mentioning 'myNbTol == 0 || myTols[0] > cmin'
- **Branch 6** @ line 294 — *max_tolerance_tracking* — **UNCOVERED**
  - What it tests: Update max tolerance on first accumulation or when larger
  - Repair action: Sets myTols[2] = cmax when myNbTol == 0 or cmax is higher
  - Suggested fixture: defect mentioning 'myNbTol == 0 || myTols[2] < cmax'
- **Branch 7** @ line 298 — *cumulative_stats_update* — **UNCOVERED**
  - What it tests: Accumulate average (cmoy) and count
  - Repair action: Adds weighted tolerance sum and shape count for later averaging
  - Suggested fixture: defect mentioning 'myTols[1] += cmoy', 'myNbTol += nbt'

#### `ShapeAnalysis_ShapeTolerance.GlobalTolerance` — lines 305–332
(5 branches, 1 covered.)

- **Branch 1** @ line 308 — *empty_collection_guard* — **UNCOVERED**
  - What it tests: No tolerances accumulated: myNbTol == 0
  - Repair action: Returns 0 when no sub-shapes were analyzed
  - Suggested fixture: defect mentioning 'if (myNbTol != 0.)', 'return result'
- **Branch 2** @ line 310 — *mode_selector_minimum* — **UNCOVERED**
  - What it tests: Request minimum tolerance: mode < 0
  - Repair action: Returns minimum recorded tolerance (myTols[0])
  - Suggested fixture: defect mentioning 'if (mode < 0)', 'myTols[0]'
- **Branch 3** @ line 314 — *mode_selector_average* — **UNCOVERED**
  - What it tests: Request average tolerance: mode == 0
  - Repair action: Returns average (or min if all equal)
  - Suggested fixture: defect mentioning 'if (mode == 0)', 'myTols[1] / myNbTol'
- **Branch 4** @ line 316 — *equal_tolerance_shortcut* — **UNCOVERED**
  - What it tests: All sub-shapes have same tolerance: myTols[0] == myTols[2]
  - Repair action: Returns that single value to avoid division error
  - Suggested fixture: defect mentioning 'myTols[0] == myTols[2]'
- **Branch 5** @ line 325 — *mode_selector_maximum* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Request maximum tolerance: mode > 0
  - Repair action: Returns maximum recorded tolerance (myTols[2])

#### `ShapeAnalysis_ShapeTolerance.InTolerance` — lines 102–226
(14 branches, 5 covered.)

- **Branch 1** @ line 104 — *range_mode_detection* — **UNCOVERED**
  - What it tests: Detect open-ended range (no upper limit) vs bounded range
  - Repair action: Sets 'over' flag when valmax < valmin to disable max checks
  - Suggested fixture: defect mentioning 'valmax < valmin', 'over ||'
- **Branch 2** @ line 111 — *shape_type_selector* — COVERED by: tsh018
  - What it tests: Face iteration: explicit FACE type or wildcard SHAPE
  - Repair action: Explores and filters faces by tolerance bounds
- **Branch 3** @ line 117 — *tolerance_range_check* — **UNCOVERED**
  - What it tests: Face tolerance within min and conditional max
  - Repair action: Appends face when tol >= valmin AND (unbounded OR tol <= valmax)
  - Suggested fixture: defect mentioning 'tol >= valmin', 'over ||', 'tol <= valmax'
- **Branch 4** @ line 127 — *shape_type_selector* — **UNCOVERED**
  - What it tests: Edge iteration: explicit EDGE type or wildcard SHAPE
  - Repair action: Explores and filters edges by tolerance bounds
  - Suggested fixture: defect mentioning 'TopAbs_EDGE', 'TopAbs_SHAPE'
- **Branch 5** @ line 133 — *tolerance_range_check* — **UNCOVERED**
  - What it tests: Edge tolerance within min and conditional max
  - Repair action: Appends edge when tol >= valmin AND (unbounded OR tol <= valmax)
  - Suggested fixture: defect mentioning 'tol >= valmin', 'over ||', 'tol <= valmax'
- **Branch 6** @ line 143 — *shape_type_selector* — **UNCOVERED**
  - What it tests: Vertex iteration: explicit VERTEX type or wildcard SHAPE
  - Repair action: Explores and filters vertices by tolerance bounds
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX', 'TopAbs_SHAPE'
- **Branch 7** @ line 149 — *tolerance_range_check_vertex_bug* — COVERED by: a096
  - What it tests: Vertex tolerance check: ASYMMETRIC condition (>= instead of <=)
  - Repair action: BUG: Uses (tol >= valmax) instead of (tol <= valmax); appends wrong vertices
- **Branch 8** @ line 159 — *shape_type_selector* — COVERED by: ad046, ad081, m015, m074, m083, n039, ps013, twi065 (+1 more)
  - What it tests: Shell iteration: special combined mode
  - Repair action: Explores shells with recursive face/edge/vertex inspection
- **Branch 9** @ line 164 — *shell_recursion* — **UNCOVERED**
  - What it tests: Explore faces within shells; recursive InTolerance call
  - Repair action: Recursively checks faces in shell, appends shell if any face matches
  - Suggested fixture: defect mentioning 'for (TopExp_Explorer face', 'iashell = true'
- **Branch 10** @ line 172 — *recursive_call* — **UNCOVERED**
  - What it tests: Recursive InTolerance call with TopAbs_SHELL type
  - Repair action: Re-enters with TopAbs_SHELL instead of TopAbs_FACE; cascades shell logic
  - Suggested fixture: defect mentioning 'InTolerance(face.Current(), valmin, valmax, type)'
- **Branch 11** @ line 191 — *duplicate_avoidance* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Skip faces already in shell map
  - Repair action: Avoids re-checking faces that were already visited inside shells
- **Branch 12** @ line 196 — *tolerance_range_check* — COVERED by: sw001, sw002, sw003, sw004, sw005, sw006, sw007, sw008 (+1 more)
  - What it tests: Free face tolerance within bounds
  - Repair action: Sets iaface=true when face itself matches bounds
- **Branch 13** @ line 204 — *edge_cascade_check* — **UNCOVERED**
  - What it tests: If free face tolerance doesn't match, recursively check contained edges
  - Repair action: Appends face if any edge within it matches bounds
  - Suggested fixture: defect mentioning 'InTolerance(myExp.Current(), valmin, valmax, TopAbs_EDGE)'
- **Branch 14** @ line 211 — *vertex_cascade_check* — **UNCOVERED**
  - What it tests: If no edge in face matches, recursively check vertices
  - Repair action: Appends face if any vertex within it matches bounds
  - Suggested fixture: defect mentioning 'InTolerance(myExp.Current(), valmin, valmax, TopAbs_VERTEX)'

#### `ShapeAnalysis_ShapeTolerance.OverTolerance` — lines 84–93
(1 branches, 0 covered.)

- **Branch 1** @ line 85 — *sign_handling* — **UNCOVERED**
  - What it tests: Positive vs negative tolerance value dispatch
  - Repair action: Converts negative value to max bound, positive to min bound
  - Suggested fixture: defect mentioning 'value >= 0', 'InTolerance'

#### `ShapeFix_ShapeTolerance.LimitTolerance` — lines 39–138
(19 branches, 6 covered.)

- **Branch 1** @ line 40 — *input_validation* — COVERED by: in014
  - What it tests: Null shape or negative tmin
  - Repair action: Returns false to reject invalid input
- **Branch 2** @ line 44 — *range_mode_detection* — **UNCOVERED**
  - What it tests: Bounded range (tmax >= tmin) vs open upper bound
  - Repair action: Sets iamax flag to control max limit check
  - Suggested fixture: defect mentioning 'iamax = (tmax >= tmin)'
- **Branch 3** @ line 47 — *shape_type_selector* — **UNCOVERED**
  - What it tests: Single shape type (VERTEX, EDGE, FACE) vs grouped/compound
  - Repair action: Enters specialized loop for single type or falls through to else
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX || styp == TopAbs_EDGE || styp == TopAbs_FACE'
- **Branch 4** @ line 57 — *tolerance_clamp_exceed_max* — **UNCOVERED**
  - What it tests: Vertex tolerance exceeds tmax (when max is defined)
  - Repair action: Sets newtol=1 to clamp down to tmax
  - Suggested fixture: defect mentioning 'iamax && prec > tmax', 'newtol = 1'
- **Branch 5** @ line 61 — *tolerance_clamp_below_min* — **UNCOVERED**
  - What it tests: Vertex tolerance below tmin
  - Repair action: Sets newtol=-1 to clamp up to tmin
  - Suggested fixture: defect mentioning 'prec < tmin', 'newtol = -1'
- **Branch 6** @ line 65 — *tolerance_write_conditional* — **UNCOVERED**
  - What it tests: Vertex was clamped (newtol != 0)
  - Repair action: Writes corrected tolerance to internal BRep_TVertex structure
  - Suggested fixture: defect mentioning 'if (newtol)', 'BRep_TVertex'
- **Branch 7** @ line 72 — *shape_type_branch_edge* — **UNCOVERED**
  - What it tests: Edge type branch within single-type selector
  - Repair action: Processes edges with same clamping logic as vertices
  - Suggested fixture: defect mentioning 'else if (styp == TopAbs_EDGE)'
- **Branch 8** @ line 76 — *tolerance_clamp_exceed_max* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+580 more)
  - What it tests: Edge tolerance exceeds tmax
  - Repair action: Sets newtol=1 to clamp down
- **Branch 9** @ line 80 — *tolerance_clamp_below_min* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+580 more)
  - What it tests: Edge tolerance below tmin
  - Repair action: Sets newtol=-1 to clamp up
- **Branch 10** @ line 84 — *tolerance_write_conditional* — **UNCOVERED**
  - What it tests: Edge was clamped
  - Repair action: Writes to BRep_TEdge structure
  - Suggested fixture: defect mentioning 'if (newtol)', 'BRep_TEdge'
- **Branch 11** @ line 91 — *shape_type_branch_face* — **UNCOVERED**
  - What it tests: Face type branch within single-type selector
  - Repair action: Processes faces with same clamping logic
  - Suggested fixture: defect mentioning 'else if (styp == TopAbs_FACE)'
- **Branch 12** @ line 95 — *tolerance_clamp_exceed_max* — COVERED by: a002, a003, a013, a014, a017, a018, a019, a020 (+747 more)
  - What it tests: Face tolerance exceeds tmax
  - Repair action: Sets newtol=1 to clamp down
- **Branch 13** @ line 99 — *tolerance_clamp_below_min* — COVERED by: a002, a003, a013, a014, a017, a018, a019, a020 (+747 more)
  - What it tests: Face tolerance below tmin
  - Repair action: Sets newtol=-1 to clamp up
- **Branch 14** @ line 103 — *tolerance_write_conditional* — **UNCOVERED**
  - What it tests: Face was clamped
  - Repair action: Writes to BRep_TFace structure
  - Suggested fixture: defect mentioning 'if (newtol)', 'BRep_TFace'
- **Branch 15** @ line 112 — *shape_type_branch_wire* — **UNCOVERED**
  - What it tests: WIRE type selector: special combined mode
  - Repair action: Processes edges and vertices of wire recursively
  - Suggested fixture: defect mentioning 'else if (styp == TopAbs_WIRE)'
- **Branch 16** @ line 118 — *recursive_call_edge_part* — **UNCOVERED**
  - What it tests: Wire branch: recursive call for edge
  - Repair action: Clamps edge and its vertices within wire
  - Suggested fixture: defect mentioning 'LimitTolerance(E, tmin, tmax, TopAbs_EDGE)'
- **Branch 17** @ line 121 — *vertex_null_guard* — **UNCOVERED**
  - What it tests: First vertex of edge exists
  - Repair action: Conditionally calls LimitTolerance on V1
  - Suggested fixture: defect mentioning '!V1.IsNull()'
- **Branch 18** @ line 125 — *vertex_null_guard* — **UNCOVERED**
  - What it tests: Second vertex of edge exists
  - Repair action: Conditionally calls LimitTolerance on V2
  - Suggested fixture: defect mentioning '!V2.IsNull()'
- **Branch 19** @ line 131 — *shape_type_branch_else* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Compound or other shape: cascade to all sub-types
  - Repair action: Recursively calls LimitTolerance for VERTEX, EDGE, FACE

#### `ShapeFix_ShapeTolerance.SetTolerance` — lines 145–212
(15 branches, 5 covered.)

- **Branch 1** @ line 149 — *input_validation* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Null shape or non-positive precision
  - Repair action: Returns early to reject invalid input
- **Branch 2** @ line 153 — *shape_type_selector* — **UNCOVERED**
  - What it tests: Single shape type (VERTEX, EDGE, FACE) vs grouped/compound
  - Repair action: Enters specialized loop for single type or falls through to else
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX || styp == TopAbs_EDGE || styp == TopAbs_FACE'
- **Branch 3** @ line 158 — *shape_type_branch_vertex* — **UNCOVERED**
  - What it tests: VERTEX type branch within single-type selector
  - Repair action: Sets tolerance on all vertices in shape
  - Suggested fixture: defect mentioning 'if (styp == TopAbs_VERTEX)'
- **Branch 4** @ line 162 — *tolerance_write_unconditional* — **UNCOVERED**
  - What it tests: Write vertex tolerance directly
  - Repair action: Sets preci on BRep_TVertex without condition
  - Suggested fixture: defect mentioning 'TV->Tolerance(preci)', 'BRep_TVertex'
- **Branch 5** @ line 165 — *shape_type_branch_edge* — **UNCOVERED**
  - What it tests: EDGE type branch within single-type selector
  - Repair action: Sets tolerance on all edges in shape
  - Suggested fixture: defect mentioning 'else if (styp == TopAbs_EDGE)'
- **Branch 6** @ line 170 — *tolerance_write_unconditional* — **UNCOVERED**
  - What it tests: Write edge tolerance directly
  - Repair action: Sets preci on BRep_TEdge without condition
  - Suggested fixture: defect mentioning 'TE->Tolerance(preci)', 'BRep_TEdge'
- **Branch 7** @ line 172 — *shape_type_branch_face* — **UNCOVERED**
  - What it tests: FACE type branch within single-type selector
  - Repair action: Sets tolerance on all faces in shape
  - Suggested fixture: defect mentioning 'else if (styp == TopAbs_FACE)'
- **Branch 8** @ line 177 — *tolerance_write_unconditional* — **UNCOVERED**
  - What it tests: Write face tolerance directly
  - Repair action: Sets preci on BRep_TFace without condition
  - Suggested fixture: defect mentioning 'TF->Tolerance(preci)', 'BRep_TFace'
- **Branch 9** @ line 181 — *shape_type_branch_wire* — **UNCOVERED**
  - What it tests: WIRE type selector: special combined mode
  - Repair action: Sets tolerance on edges and vertices of wire
  - Suggested fixture: defect mentioning 'else if (styp == TopAbs_WIRE)'
- **Branch 10** @ line 188 — *tolerance_write_unconditional* — COVERED by: ad101, gs009, tfa037, twi007, twi052, twi065
  - What it tests: Write edge tolerance in wire branch
  - Repair action: Sets preci on edge without condition
- **Branch 11** @ line 192 — *vertex_null_guard* — **UNCOVERED**
  - What it tests: First vertex of edge exists
  - Repair action: Conditionally sets V1 tolerance
  - Suggested fixture: defect mentioning '!V1.IsNull()'
- **Branch 12** @ line 195 — *tolerance_write_unconditional* — COVERED by: a029, ad101, ad103, bo008, m010, m012, m025, m126 (+11 more)
  - What it tests: Write first vertex tolerance in wire
  - Repair action: Sets preci on V1
- **Branch 13** @ line 198 — *vertex_null_guard* — **UNCOVERED**
  - What it tests: Second vertex of edge exists
  - Repair action: Conditionally sets V2 tolerance
  - Suggested fixture: defect mentioning '!V2.IsNull()'
- **Branch 14** @ line 201 — *tolerance_write_unconditional* — COVERED by: a001, ad095, ad101, ad103, bo008, n010, twi006, twi017 (+4 more)
  - What it tests: Write second vertex tolerance in wire
  - Repair action: Sets preci on V2
- **Branch 15** @ line 206 — *shape_type_branch_else* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Compound or other shape: cascade to all sub-types
  - Repair action: Recursively calls SetTolerance for VERTEX, EDGE, FACE


### `ShapeUpgrade_ConvertCurve2dToBezier.cxx, ShapeUpgrade_ClosedFaceDivide.cxx, ShapeUpgrade_RemoveLocations.cxx`

5 methods, 86 branches, 6 covered.

#### `ShapeUpgrade_ClosedFaceDivide.SplitSurface` — lines 63–292
(30 branches, 5 covered.)

- **Branch 1** @ line 65 — *split-tool-null-check* — **UNCOVERED**
  - What it tests: SplitSurface tool not initialized
  - Repair action: return-false-no-split
  - Suggested fixture: defect mentioning 'SplitSurf.IsNull()'
- **Branch 2** @ line 70 — *face-validation* — **UNCOVERED**
  - What it tests: Result shape is not a valid Face
  - Repair action: encode-fail3-return-false
  - Suggested fixture: defect mentioning 'myResult.IsNull()', 'ShapeType() != TopAbs_FACE'
- **Branch 3** @ line 80 — *infinite-bounds-detection* — **UNCOVERED**
  - What it tests: Face UV bounds contain infinite values (unbounded surfaces)
  - Repair action: return-false-unbounded
  - Suggested fixture: defect mentioning 'Precision::IsInfinite(Uf)', 'IsInfinite(Ul)', 'IsInfinite(Vf)'
- **Branch 4** @ line 94 — *seam-edge-detection-loop* — **UNCOVERED**
  - What it tests: Iterate through face wires searching for seam edge
  - Repair action: loop-until-seam-found
  - Suggested fixture: defect mentioning 'for (TopoDS_Iterator iter(face);', '!doSplit; iter.Next()'
- **Branch 5** @ line 102 — *edge-seam-check* — **UNCOVERED**
  - What it tests: Edge is marked as seam (shared by two faces with different parametrization)
  - Repair action: process-seam-edge
  - Suggested fixture: defect mentioning 'sewd->IsSeam(i)'
- **Branch 6** @ line 104 — *seam-pcurve-forward* — **UNCOVERED**
  - What it tests: Obtain forward PCurve for seam edge
  - Repair action: extract-forward-pcurve
  - Suggested fixture: defect mentioning 'sae.PCurve(edge, face, c1, f1, l1, false)'
- **Branch 7** @ line 111 — *seam-pcurve-forward-missing* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Forward PCurve extraction fails (edge not on face)
  - Repair action: skip-seam-edge
- **Branch 8** @ line 117 — *seam-pcurve-reversed* — **UNCOVERED**
  - What it tests: Obtain reversed PCurve for seam edge
  - Repair action: extract-reversed-pcurve
  - Suggested fixture: defect mentioning 'edge.Reversed()', 'tmpE', 'sae.PCurve(TopoDS::Edge(tmpE)'
- **Branch 9** @ line 118 — *seam-pcurve-reversed-missing* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Reversed PCurve extraction fails
  - Repair action: skip-seam-edge
- **Branch 10** @ line 121 — *seam-same-pcurve-degenerate* — **UNCOVERED**
  - What it tests: Forward and reversed PCurves are identical (degenerate seam)
  - Repair action: skip-degenerate-seam
  - Suggested fixture: defect mentioning 'c2d == c1'
- **Branch 11** @ line 128 — *pcurve-bounding-box-computation* — **UNCOVERED**
  - What it tests: Compute 2D bounding boxes for both PCurves to find split domain
  - Repair action: compute-bbox-bounds
  - Suggested fixture: defect mentioning 'sac.FillBndBox', 'Bnd_Box2d', 'B1.Get'
- **Branch 12** @ line 135 — *u-dimension-largest* — **UNCOVERED**
  - What it tests: U-dimension separation larger than V-dimension
  - Repair action: split-in-u-direction
  - Suggested fixture: defect mentioning 'if (x1min < x2min)', 'dU > dV'
- **Branch 13** @ line 138 — *u-split-parameter-range* — **UNCOVERED**
  - What it tests: Generate U-domain split points between PCurve bounding boxes
  - Repair action: generate-u-split-values
  - Suggested fixture: defect mentioning 'xf = x1max', 'xl = x2min', 'isUSplit = true'
- **Branch 14** @ line 142 — *u-split-bounds-reversed* — **UNCOVERED**
  - What it tests: Reverse U-dimension bounds when first box beyond second
  - Repair action: swap-u-bounds
  - Suggested fixture: defect mentioning 'xf = x2max', 'xl = x1min'
- **Branch 15** @ line 145 — *v-dimension-check* — COVERED by: a002, a008, a012, a018, a019, a020, a021, a022 (+223 more)
  - What it tests: V-dimension separation analysis (similar to U)
  - Repair action: determine-v-bounds
- **Branch 16** @ line 158 — *split-direction-selection* — **UNCOVERED**
  - What it tests: Choose split direction (U vs V) based on largest separation
  - Repair action: select-u-or-v-split
  - Suggested fixture: defect mentioning 'if (dU > dV)'
- **Branch 17** @ line 160 — *uniform-split-point-generation* — **UNCOVERED**
  - What it tests: Generate evenly-spaced split points along chosen direction
  - Repair action: create-split-values
  - Suggested fixture: defect mentioning 'double step = dU / (myNbSplit + 1)', 'double val = xf + step'
- **Branch 18** @ line 182 — *geometric-closure-check* — COVERED by: n010
  - What it tests: Fallback: check geometric closure when no seam edge found
  - Repair action: analyze-geometric-closure
- **Branch 19** @ line 186 — *u-closure-detection* — **UNCOVERED**
  - What it tests: Surface is parametrically closed in U-direction
  - Repair action: test-u-geometric-closure
  - Suggested fixture: defect mentioning 'sas->IsUClosed(Precision())'
- **Branch 20** @ line 189 — *u-closure-gap-detection* — **UNCOVERED**
  - What it tests: Face UV bounds differ from surface bounds in U (thin closure case)
  - Repair action: identify-thin-u-closure
  - Suggested fixture: defect mentioning '(U2 - U1) - (Ul - Uf) < toler'
- **Branch 21** @ line 194 — *u-half-surface-test* — COVERED by: a002, a003, a005, a011, a013, a017, a066, a068 (+306 more)
  - What it tests: Test if half-surface still closed (detecting degenerate geometry)
  - Repair action: test-half-surface-u-closed
- **Branch 22** @ line 201 — *u-split-needed* — **UNCOVERED**
  - What it tests: Half-surface is not closed, indicating degenerate edge needing split
  - Repair action: set-u-split-flag
  - Suggested fixture: defect mentioning '!sast->IsUClosed(Precision())', 'doSplit = true', 'isUSplit = true'
- **Branch 23** @ line 216 — *v-closure-detection* — **UNCOVERED**
  - What it tests: Surface is parametrically closed in V-direction
  - Repair action: test-v-geometric-closure
  - Suggested fixture: defect mentioning 'if (vclosed && !doSplit)', 'sas->IsVClosed'
- **Branch 24** @ line 221 — *v-closure-gap-detection* — **UNCOVERED**
  - What it tests: Face UV bounds differ from surface bounds in V (thin closure case)
  - Repair action: identify-thin-v-closure
  - Suggested fixture: defect mentioning '(V2 - V1) - (Vl - Vf) < toler'
- **Branch 25** @ line 250 — *split-surface-init* — **UNCOVERED**
  - What it tests: Initialize split tool with surface geometry and bounds
  - Repair action: init-split-tool
  - Suggested fixture: defect mentioning 'SplitSurf->Init(surf, Uf, Ul, Vf, Vl)'
- **Branch 26** @ line 251 — *split-direction-configuration* — **UNCOVERED**
  - What it tests: Configure split tool with U or V split values based on direction flag
  - Repair action: set-split-values-by-direction
  - Suggested fixture: defect mentioning 'if (isUSplit)', 'SetUSplitValues(split)', 'SetVSplitValues(split)'
- **Branch 27** @ line 260 — *split-surface-execution* — **UNCOVERED**
  - What it tests: Execute surface splitting operation
  - Repair action: perform-split
  - Suggested fixture: defect mentioning 'SplitSurf->Perform(mySegmentMode)'
- **Branch 28** @ line 261 — *split-result-validation* — **UNCOVERED**
  - What it tests: Verify split operation completed successfully
  - Repair action: return-false-if-split-failed
  - Suggested fixture: defect mentioning '!SplitSurf->Status(ShapeExtend_DONE)'
- **Branch 29** @ line 268 — *shell-composition* — **UNCOVERED**
  - What it tests: Compose split surface fragments back into coherent shell
  - Repair action: compose-shell-from-grid
  - Suggested fixture: defect mentioning 'ShapeFix_ComposeShell CompShell', 'CompShell.Init(Grid)'
- **Branch 30** @ line 279 — *recursive-face-split* — **UNCOVERED**
  - What it tests: Recursively split composed faces to handle nested closures
  - Repair action: loop-recursive-split-faces
  - Suggested fixture: defect mentioning 'for (TopExp_Explorer exp(res, TopAbs_FACE);', 'if (SplitSurface())'

#### `ShapeUpgrade_ConvertCurve2dToBezier.Build` — lines 270–300
(9 branches, 1 covered.)

- **Branch 1** @ line 276 — *split-value-iteration* — **UNCOVERED**
  - What it tests: Iterate across split parameter values to construct output curves
  - Repair action: loop-over-split-values
  - Suggested fixture: defect mentioning 'for (int i = 2; i <= nb; i++)'
- **Branch 2** @ line 279 — *segment-index-mapping* — **UNCOVERED**
  - What it tests: Find corresponding segment index for each split value
  - Repair action: locate-segment-j-by-params
  - Suggested fixture: defect mentioning 'for (; j <= mySplitParams->Length(); j++)', 'mySplitParams->Value(j) + prec > par'
- **Branch 3** @ line 281 — *segment-parameter-lower-bound* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: Segment parameter range includes current split point
  - Repair action: break-segment-search
- **Branch 4** @ line 285 — *segment-parameter-reset* — **UNCOVERED**
  - What it tests: Previous segment boundary does not overlap current split value
  - Repair action: reset-prev-parameter
  - Suggested fixture: defect mentioning 'prevPar = 0'
- **Branch 5** @ line 291 — *bezier-segment-extraction* — **UNCOVERED**
  - What it tests: Extract and copy Bezier segment for result geometry
  - Repair action: copy-segment-bezier
  - Suggested fixture: defect mentioning 'down_cast<Geom2d_BezierCurve>(mySegments->Value(j - 1)->Copy())'
- **Branch 6** @ line 293 — *parameter-normalization* — **UNCOVERED**
  - What it tests: Compute normalized parameter range within segment domain
  - Repair action: calculate-segment-ufactor
  - Suggested fixture: defect mentioning 'double uFact = mySplitParams->Value(j) - mySplitParams->Value(j - 1)'
- **Branch 7** @ line 295 — *output-curve-length* — **UNCOVERED**
  - What it tests: Map global split range to local segment parameter range
  - Repair action: compute-local-param-length
  - Suggested fixture: defect mentioning 'double length = (par - pp) / uFact'
- **Branch 8** @ line 296 — *segment-trimming* — **UNCOVERED**
  - What it tests: Trim Bezier arc to exact output domain
  - Repair action: segment-bezier-to-range
  - Suggested fixture: defect mentioning 'bes->Segment(prevPar, prevPar + length)'
- **Branch 9** @ line 297 — *parameter-advance* — **UNCOVERED**
  - What it tests: Track consumed parameter space within current segment
  - Repair action: increment-prev-param
  - Suggested fixture: defect mentioning 'prevPar += length'

#### `ShapeUpgrade_ConvertCurve2dToBezier.Compute` — lines 57–265
(20 branches, 0 covered.)

- **Branch 1** @ line 65 — *bspline-to-line-approximation* — **UNCOVERED**
  - What it tests: Straight-line approximation of BSpline/Bezier curves below tolerance
  - Repair action: convert-to-line2d-bezier
  - Suggested fixture: defect mentioning 'ConvertToLine2d', 'IsKind(Geom2d_BSplineCurve)', 'aDeviation'
- **Branch 2** @ line 90 — *trimmed-curve-unwrap* — **UNCOVERED**
  - What it tests: Trimmed curve requires basis curve extraction and recursive processing
  - Repair action: extract-basis-curve-recurse
  - Suggested fixture: defect mentioning 'Geom2d_TrimmedCurve', 'BasisCurve', 'converter.Compute()'
- **Branch 3** @ line 108 — *bezier-direct-handling* — **UNCOVERED**
  - What it tests: Full-domain Bezier vs. trimmed Bezier segment repair
  - Repair action: segment-bezier-or-keep
  - Suggested fixture: defect mentioning 'First < precision && Last > 1', 'Segment(First, Last)'
- **Branch 4** @ line 114 — *bezier-parameter-bounds* — **UNCOVERED**
  - What it tests: Bezier within unit parameter domain [0,1]
  - Repair action: keep-full-bezier
  - Suggested fixture: defect mentioning 'First < precision', 'Last > 1 - precision'
- **Branch 5** @ line 119 — *bezier-trim-needed* — **UNCOVERED**
  - What it tests: Bezier outside unit domain requires segmentation
  - Repair action: trim-bezier-copy
  - Suggested fixture: defect mentioning 'bezier->Copy()', 'besNew->Segment', 'ShapeExtend_DONE2'
- **Branch 6** @ line 128 — *line-to-bezier-conversion* — **UNCOVERED**
  - What it tests: 2D line curve conversion to Bezier representation
  - Repair action: make-bezier2d-from-line
  - Suggested fixture: defect mentioning 'Geom2d_Line', 'MakeBezier2d'
- **Branch 7** @ line 143 — *conic-approximation* — **UNCOVERED**
  - What it tests: Conic curve (circle, ellipse, parabola, hyperbola) to BSpline conversion
  - Repair action: approximate-conic-with-bspline
  - Suggested fixture: defect mentioning 'Geom2d_Conic', 'Geom2dConvert_ApproxCurve', 'HasResult()'
- **Branch 8** @ line 148 — *conic-approximation-fallback* — **UNCOVERED**
  - What it tests: Approximation failure triggers fallback to direct BSpline conversion
  - Repair action: convert-to-bspline-quasiangular
  - Suggested fixture: defect mentioning '!approx.HasResult()', 'CurveToBSplineCurve', 'Convert_QuasiAngular'
- **Branch 9** @ line 162 — *non-bspline-conversion* — **UNCOVERED**
  - What it tests: Non-BSpline curves (except Conic) conversion to BSpline
  - Repair action: convert-general-curve-to-bspline
  - Suggested fixture: defect mentioning '!IsKind(Geom2d_BSplineCurve)', 'CurveToBSplineCurve'
- **Branch 10** @ line 166 — *bspline-direct-cast* — **UNCOVERED**
  - What it tests: BSpline curve already in target form
  - Repair action: use-bspline-as-is
  - Suggested fixture: defect mentioning 'down_cast<Geom2d_BSplineCurve>'
- **Branch 11** @ line 173 — *parameter-precision-clamp-first* — **UNCOVERED**
  - What it tests: Curve First parameter near BSpline basis curve first parameter
  - Repair action: snap-to-basis-first
  - Suggested fixture: defect mentioning 'std::abs(First - bf) < precision', 'First = bf'
- **Branch 12** @ line 177 — *parameter-precision-clamp-last* — **UNCOVERED**
  - What it tests: Curve Last parameter near BSpline basis curve last parameter
  - Repair action: snap-to-basis-last
  - Suggested fixture: defect mentioning 'std::abs(Last - bl) < precision'
- **Branch 13** @ line 181 — *domain-underflow* — **UNCOVERED**
  - What it tests: Edge parameter range exceeds pcurve lower bound
  - Repair action: clamp-to-basis-bounds
  - Suggested fixture: defect mentioning 'First < bf', 'Warning: range exceeds pcurve domain'
- **Branch 14** @ line 189 — *domain-overflow* — **UNCOVERED**
  - What it tests: Edge parameter range exceeds pcurve upper bound
  - Repair action: clamp-to-basis-bounds
  - Suggested fixture: defect mentioning 'Last > bl', 'mySplitValues->SetValue'
- **Branch 15** @ line 201 — *bspline-to-bezier-arc-split* — **UNCOVERED**
  - What it tests: BSpline decomposition into Bezier arcs at knot boundaries
  - Repair action: split-bspline-at-knots
  - Suggested fixture: defect mentioning 'Geom2dConvert_BSplineCurveToBezierCurve', 'tool.NbArcs()'
- **Branch 16** @ line 214 — *arc-precision-filter* — **UNCOVERED**
  - What it tests: Skip arc segments when knot spacing below precision threshold
  - Repair action: skip-small-arcs
  - Suggested fixture: defect mentioning 'nextKnot - mySplitParams->Value', '> precision'
- **Branch 17** @ line 217 — *bezier-arc-line-approximation* — **UNCOVERED**
  - What it tests: Individual Bezier arc approximable as line with deviation check
  - Repair action: convert-bezier-arc-to-line
  - Suggested fixture: defect mentioning 'aCrv2d->IsKind(Geom2d_BezierCurve)', 'ConvertToLine2d'
- **Branch 18** @ line 230 — *arc-line-deviation-validation* — **UNCOVERED**
  - What it tests: Bezier arc approximation error within tolerance
  - Repair action: use-line-approximation
  - Suggested fixture: defect mentioning 'aDeviation <= Precision::Approximation()', 'MakeBezier2d(aBSpline2d)'
- **Branch 19** @ line 238 — *arc-geometry-retained* — **UNCOVERED**
  - What it tests: Non-line-approximable arc kept as original geometry
  - Repair action: keep-bezier-arc-unchanged
  - Suggested fixture: defect mentioning 'mySegments->Append(aCrv2d)'
- **Branch 20** @ line 243 — *split-value-insertion* — **UNCOVERED**
  - What it tests: Insert internal knot values into split sequence respecting user-specified boundaries
  - Repair action: inject-knot-points-in-range
  - Suggested fixture: defect mentioning 'mySplitValues->InsertBefore', 'valknot <= First', 'valknot >= Last'

#### `ShapeUpgrade_RemoveLocations.MakeNewShape` — lines 178–314
(25 branches, 0 covered.)

- **Branch 1** @ line 184 — *location-nullification-conditional* — **UNCOVERED**
  - What it tests: Preserve original location when removal not requested but location exists
  - Repair action: null-location-if-keep
  - Suggested fixture: defect mentioning 'if (!theRemoveLoc && !theShape.Location().IsIdentity())'
- **Branch 2** @ line 189 — *shape-cache-lookup* — **UNCOVERED**
  - What it tests: Check if shape already processed and cached
  - Repair action: return-cached-result
  - Suggested fixture: defect mentioning 'isBound = myMapNewShapes.IsBound(aShape)'
- **Branch 3** @ line 190 — *cached-shape-restoration* — **UNCOVERED**
  - What it tests: Restore cached shape with original orientation and location
  - Repair action: use-cached-shape-with-properties
  - Suggested fixture: defect mentioning 'aNewShape = myMapNewShapes.Find(aShape)', 'aNewShape.Orientation(theShape.Orientation())'
- **Branch 4** @ line 199 — *early-return-non-edge* — **UNCOVERED**
  - What it tests: Non-edge shapes from cache can return immediately after location restoration
  - Repair action: return-early-if-not-edge
  - Suggested fixture: defect mentioning 'if (shtype != TopAbs_EDGE)', 'return true'
- **Branch 5** @ line 207 — *removal-flag-decision* — **UNCOVERED**
  - What it tests: Recalculate removal flag based on shape type hierarchy
  - Repair action: compute-isremove-loc
  - Suggested fixture: defect mentioning 'isRemoveLoc = theRemoveLoc', 'myLevelRemoving == TopAbs_SHAPE'
- **Branch 6** @ line 215 — *ancestor-shape-binding* — **UNCOVERED**
  - What it tests: Bind ancestor shape context for Face type (used by Edge rebuild)
  - Repair action: set-ancestor-for-faces
  - Suggested fixture: defect mentioning 'if (shtype == TopAbs_FACE)', 'anAncShape = aShape'
- **Branch 7** @ line 219 — *rebuild-trigger-condition* — **UNCOVERED**
  - What it tests: Determine if shape geometry needs rebuilding (location or type-specific)
  - Repair action: assess-rebuild-need
  - Suggested fixture: defect mentioning 'isRemoveLoc && (!aShape.Location().IsIdentity()', 'shtype == TopAbs_EDGE'
- **Branch 8** @ line 224 — *face-geometry-rebuild* — **UNCOVERED**
  - What it tests: Face with location: rebuild surface by applying location transformation
  - Repair action: transform-face-surface
  - Suggested fixture: defect mentioning 'shtype == TopAbs_FACE', 'RebuildShape(oldFace, anewFace)'
- **Branch 9** @ line 229 — *face-rebuild-success* — **UNCOVERED**
  - What it tests: Face rebuild completed, cache new face geometry
  - Repair action: bind-rebuilt-face
  - Suggested fixture: defect mentioning 'if (aRebuild)', 'myMapNewShapes.Bind(oldFace, aNewShape)'
- **Branch 10** @ line 235 — *edge-geometry-rebuild* — **UNCOVERED**
  - What it tests: Edge with location or parent face context: rebuild curve geometry
  - Repair action: transform-edge-curve
  - Suggested fixture: defect mentioning 'shtype == TopAbs_EDGE', 'RebuildShape(oldEdge, anewEdge, F, newFace, isBound)'
- **Branch 11** @ line 241 — *edge-parent-face-lookup* — **UNCOVERED**
  - What it tests: Find parent face in cache for edge curve reconstruction on surface
  - Repair action: get-or-use-ancestor-face
  - Suggested fixture: defect mentioning 'if (!anAncShape.IsNull())', 'myMapNewShapes.IsBound(F)'
- **Branch 12** @ line 250 — *edge-cached-reuse* — **UNCOVERED**
  - What it tests: Edge already cached from prior processing
  - Repair action: reuse-cached-edge
  - Suggested fixture: defect mentioning 'if (isBound)', 'anewEdge = TopoDS::Edge(aNewShape)'
- **Branch 13** @ line 257 — *vertex-geometry-rebuild* — **UNCOVERED**
  - What it tests: Vertex with location: rebuild point geometry without location
  - Repair action: transform-vertex-point
  - Suggested fixture: defect mentioning 'shtype == TopAbs_VERTEX', 'RebuildShape(aV, aVnew)'
- **Branch 14** @ line 262 — *vertex-rebuild-success* — **UNCOVERED**
  - What it tests: Vertex rebuild completed successfully
  - Repair action: use-rebuilt-vertex
  - Suggested fixture: defect mentioning 'if (aRebuild)', 'aNewShape = aVnew'
- **Branch 15** @ line 272 — *uncached-shape-processing* — **UNCOVERED**
  - What it tests: Shape not in cache requires full processing including sub-shapes
  - Repair action: build-new-shape-from-scratch
  - Suggested fixture: defect mentioning 'if (!isBound)'
- **Branch 16** @ line 276 — *empty-copy-on-no-rebuild* — **UNCOVERED**
  - What it tests: No geometry rebuild performed: use empty copy of original shape
  - Repair action: make-empty-copy
  - Suggested fixture: defect mentioning 'if (!aRebuild)', 'aNewShape = theShape.EmptyCopied()'
- **Branch 17** @ line 278 — *topology-preservation* — **UNCOVERED**
  - What it tests: Preserve closed flag through shape copy (topology-safe operation)
  - Repair action: copy-closed-flag
  - Suggested fixture: defect mentioning 'aNewShape.Closed(theShape.Closed())'
- **Branch 18** @ line 282 — *location-removal-from-copy* — **UNCOVERED**
  - What it tests: Remove location from copied shape when not preserving
  - Repair action: set-null-location
  - Suggested fixture: defect mentioning 'if (!oldLoc.IsIdentity())', 'aNewShape.Location(nullloc)'
- **Branch 19** @ line 288 — *subshape-iteration* — **UNCOVERED**
  - What it tests: Iterate through sub-shapes, recursively processing each
  - Repair action: loop-subshapes-recurse
  - Suggested fixture: defect mentioning 'TopoDS_Iterator aIt(aShape, false, isRemoveLoc)', 'for (; aIt.More(); aIt.Next())'
- **Branch 20** @ line 293 — *subshape-recursive-rebuild* — **UNCOVERED**
  - What it tests: Recursively rebuild each sub-shape with inherited removal flag
  - Repair action: recurse-make-new-shape
  - Suggested fixture: defect mentioning 'MakeNewShape(subshape, anAncShape, anewsubshape, isRemoveLoc)'
- **Branch 21** @ line 295 — *subshape-addition* — **UNCOVERED**
  - What it tests: Add rebuilt sub-shape to parent container
  - Repair action: add-subshape-to-builder
  - Suggested fixture: defect mentioning 'aB.Add(aNewShape, anewsubshape)'
- **Branch 22** @ line 297 — *orientation-restoration* — **UNCOVERED**
  - What it tests: Restore original orientation after sub-shape modifications if any rebuild occurred
  - Repair action: restore-orientation
  - Suggested fixture: defect mentioning 'if (isDone)', 'aNewShape.Orientation(orient)'
- **Branch 23** @ line 302 — *no-rebuild-fallback* — **UNCOVERED**
  - What it tests: No sub-shapes modified: revert to original shape
  - Repair action: use-original-shape
  - Suggested fixture: defect mentioning 'if (!isDone)', 'aNewShape = aShape'
- **Branch 24** @ line 305 — *shape-caching* — **UNCOVERED**
  - What it tests: Cache final rebuilt (or original) shape for future lookups
  - Repair action: bind-final-shape
  - Suggested fixture: defect mentioning 'myMapNewShapes.Bind(aShape, aNewShape)'
- **Branch 25** @ line 306 — *location-restoration-conditional* — **UNCOVERED**
  - What it tests: Restore original location after processing if location preservation requested
  - Repair action: reapply-location
  - Suggested fixture: defect mentioning 'if (!theRemoveLoc && !oldLoc.IsIdentity())', 'aNewShape.Location(oldLoc)'

#### `ShapeUpgrade_RemoveLocations.Remove` — lines 48–58
(2 branches, 0 covered.)

- **Branch 1** @ line 52 — *location-removal-level-check* — **UNCOVERED**
  - What it tests: Determine if shape location should be removed based on shape type and removal level
  - Repair action: compute-removal-flag
  - Suggested fixture: defect mentioning 'myLevelRemoving == TopAbs_SHAPE', 'shtype != TopAbs_COMPOUND', 'myLevelRemoving <= shtype'
- **Branch 2** @ line 55 — *make-new-shape-delegation* — **UNCOVERED**
  - What it tests: Delegate to recursive shape reconstruction with location handling
  - Repair action: call-make-new-shape
  - Suggested fixture: defect mentioning 'MakeNewShape(theShape, S, myShape, isRemoveLoc)'


### `ShapeUpgrade_RemoveInternalWires.cxx, ShapeFix_FixSmallSolid.cxx`

7 methods, 35 branches, 11 covered.

#### `ShapeFix_FixSmallSolid.IsSmall` — lines 569–593
(3 branches, 2 covered.)

- **Branch 1** @ line 574 — *volume_threshold_exceeded* — COVERED by: in014
  - What it tests: volume threshold criterion is used and solid volume exceeds threshold
  - Repair action: return false (solid not small)
- **Branch 2** @ line 582 — *width_factor_threshold_enabled* — **UNCOVERED**
  - What it tests: width factor threshold criterion is enabled and configured
  - Repair action: calculate area and check width factor ratio
  - Suggested fixture: defect mentioning 'if (IsUsedWidthFactorThreshold() && myWidthFactorThreshold < Precision::Infinite())'
- **Branch 3** @ line 585 — *width_factor_threshold_exceeded* — COVERED by: in014
  - What it tests: width factor ratio (volume/area) exceeds threshold
  - Repair action: return false (solid not small)

#### `ShapeFix_FixSmallSolid.Merge` — lines 437–553
(8 branches, 3 covered.)

- **Branch 1** @ line 441 — *missing_threshold_configuration* — **UNCOVERED**
  - What it tests: no smallness criterion is set or shape invalid
  - Repair action: return shape unchanged
  - Suggested fixture: defect mentioning 'if (!IsThresholdsSet() || !IsValidInput(theShape))', 'return theShape'
- **Branch 2** @ line 456 — *small_solid_partition* — **UNCOVERED**
  - What it tests: solid meets smallness criteria during initial classification
  - Repair action: append to small solids list for later merging
  - Suggested fixture: defect mentioning 'if (IsSmall(aSolid))', 'aSmallSolids.Append(aSolid)'
- **Branch 3** @ line 462 — *non_small_solid_face_mapping* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: solid does not meet smallness criteria
  - Repair action: map faces to shells for merging target identification
- **Branch 4** @ line 473 — *iteration_termination* — **UNCOVERED**
  - What it tests: small solids list is not empty
  - Repair action: attempt to merge small solids in iteration loop
  - Suggested fixture: defect mentioning 'while (!aSmallSolids.IsEmpty())', 'FindMostSharedShell'
- **Branch 5** @ line 490 — *mergeable_small_solid* — **UNCOVERED**
  - What it tests: small solid has adjacent non-small solid
  - Repair action: queue shells for merging and remove small solid from context
  - Suggested fixture: defect mentioning 'if (FindMostSharedShell(...))', 'theContext->Remove(aSmallSolid)'
- **Branch 6** @ line 507 — *non_mergeable_small_solid* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: small solid has no adjacent non-small solid
  - Repair action: advance iterator for next small solid
- **Branch 7** @ line 514 — *merge_queue_empty* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: no shells queued for merging in current iteration
  - Repair action: exit merge loop (no more progress possible)
- **Branch 8** @ line 537 — *shells_to_add_present* — **UNCOVERED**
  - What it tests: shells exist to append (not merge) to base shell
  - Repair action: call AddShells to composite new shell with base
  - Suggested fixture: defect mentioning 'if (aShellsToBeAddedPtr != nullptr)', 'AddShells(aNewShell, *aShellsToBeAddedPtr)'

#### `ShapeFix_FixSmallSolid.Remove` — lines 94–117
(2 branches, 0 covered.)

- **Branch 1** @ line 98 — *missing_threshold_configuration* — **UNCOVERED**
  - What it tests: no smallness criterion is set or shape invalid
  - Repair action: return shape unchanged
  - Suggested fixture: defect mentioning 'if (!IsThresholdsSet() || !IsValidInput(theShape))', 'return theShape'
- **Branch 2** @ line 108 — *small_solid_detection* — **UNCOVERED**
  - What it tests: solid meets smallness criteria
  - Repair action: remove from context and send warning
  - Suggested fixture: defect mentioning 'if (IsSmall(aSolid))', 'theContext->Remove(aSolid)'

#### `ShapeUpgrade_RemoveInternalWires.Perform()` — lines 70–91
(2 branches, 0 covered.)

- **Branch 1** @ line 73 — *null_shape* — **UNCOVERED**
  - What it tests: myShape is null
  - Repair action: early return with FAIL1 status
  - Suggested fixture: defect mentioning 'if (myShape.IsNull())', 'myStatus |= ShapeExtend::EncodeStatus(ShapeExtend_FAIL1)'
- **Branch 2** @ line 84 — *face_processing_mode* — **UNCOVERED**
  - What it tests: myRemoveFacesMode is true
  - Repair action: call removeSmallFaces() to process affected faces
  - Suggested fixture: defect mentioning 'if (myRemoveFacesMode)', 'removeSmallFaces()'

#### `ShapeUpgrade_RemoveInternalWires.Perform(const NCollection_Sequence)` — lines 95–137
(6 branches, 0 covered.)

- **Branch 1** @ line 98 — *null_shape* — **UNCOVERED**
  - What it tests: myShape is null
  - Repair action: early return with FAIL1 status
  - Suggested fixture: defect mentioning 'if (myShape.IsNull())', 'myStatus |= ShapeExtend::EncodeStatus(ShapeExtend_FAIL1)'
- **Branch 2** @ line 110 — *shape_type_is_face* — **UNCOVERED**
  - What it tests: shape in sequence is a face
  - Repair action: call removeSmallWire with empty wire selector
  - Suggested fixture: defect mentioning 'if (aS.ShapeType() == TopAbs_FACE)', 'removeSmallWire(aS, TopoDS_Wire())'
- **Branch 3** @ line 114 — *shape_type_is_wire* — **UNCOVERED**
  - What it tests: shape in sequence is a wire
  - Repair action: build wire-to-faces map if needed and process matching faces
  - Suggested fixture: defect mentioning 'else if (aS.ShapeType() == TopAbs_WIRE)', 'aWireFaces.Contains(aS)'
- **Branch 4** @ line 116 — *empty_map_detection* — **UNCOVERED**
  - What it tests: wire-to-faces map not yet built
  - Repair action: construct map from shape topology on first wire encounter
  - Suggested fixture: defect mentioning 'if (!aWireFaces.Extent())', 'TopExp::MapShapesAndAncestors'
- **Branch 5** @ line 120 — *unmapped_wire* — **UNCOVERED**
  - What it tests: wire exists in the map
  - Repair action: iterate faces and call removeSmallWire with wire selector
  - Suggested fixture: defect mentioning 'if (aWireFaces.Contains(aS))', 'removeSmallWire(liter.Value(), aS)'
- **Branch 6** @ line 131 — *face_processing_mode* — **UNCOVERED**
  - What it tests: myRemoveFacesMode is true
  - Repair action: call removeSmallFaces() to process faces sharing removed edges
  - Suggested fixture: defect mentioning 'if (myRemoveFacesMode)', 'removeSmallFaces()'

#### `ShapeUpgrade_RemoveInternalWires.removeSmallFaces` — lines 191–296
(10 branches, 3 covered.)

- **Branch 1** @ line 205 — *unmapped_edge* — **UNCOVERED**
  - What it tests: edge from removed wire not in edge-faces map
  - Repair action: set FAIL2 status and continue iteration
  - Suggested fixture: defect mentioning 'if (!myEdgeFaces.Contains(aEdge))', 'myStatus |= ShapeExtend::EncodeStatus(ShapeExtend_FAIL2)'
- **Branch 2** @ line 217 — *null_result_after_context_apply* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: context application nullifies a face
  - Repair action: skip face processing
- **Branch 3** @ line 228 — *face_not_in_removed_set* — **UNCOVERED**
  - What it tests: face not found in removed edges set
  - Repair action: check if face is outer boundary and add to candidates
  - Suggested fixture: defect mentioning 'if (!isFind)', 'isOuter', 'aFaceCandidates.Add(aF)'
- **Branch 4** @ line 237 — *outer_wire_edge_match* — **UNCOVERED**
  - What it tests: edge is part of face outer wire
  - Repair action: add face to removal candidates
  - Suggested fixture: defect mentioning 'if (isOuter)', 'aFaceCandidates.Add(aF)'
- **Branch 5** @ line 260 — *seam_edge_skip* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: edge is a seam for its surface
  - Repair action: skip seam edge in boundary analysis
- **Branch 6** @ line 265 — *edge_not_in_remove_set* — **UNCOVERED**
  - What it tests: edge not marked for removal
  - Repair action: check if edge is shared with non-candidate faces and increment counter
  - Suggested fixture: defect mentioning 'if (!myRemoveEdges.IsBound(aE))', 'nbNotRemoved++'
- **Branch 7** @ line 272 — *null_adjacent_face* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: adjacent face disappears after context apply
  - Repair action: skip this adjacent face
- **Branch 8** @ line 276 — *non_removal_witness* — **UNCOVERED**
  - What it tests: adjacent face neither matches current nor is candidate
  - Repair action: increment not-removed counter (prevents current face removal)
  - Suggested fixture: defect mentioning 'if (!aF.IsSame(aF2) && !aFaceCandidates.Contains(aF2))', 'nbNotRemoved++'
- **Branch 9** @ line 284 — *orphaned_outer_wire* — **UNCOVERED**
  - What it tests: outer wire has no edges shared with non-removal-candidate faces
  - Repair action: mark face for removal
  - Suggested fixture: defect mentioning 'if (!nbNotRemoved)', 'Context()->Remove(aF)', 'myRemovedFaces.Append(aF)'
- **Branch 10** @ line 292 — *faces_removed_status* — **UNCOVERED**
  - What it tests: any faces were actually removed
  - Repair action: set DONE2 status
  - Suggested fixture: defect mentioning 'if (myRemovedFaces.Length())', 'myStatus |= ShapeExtend::EncodeStatus(ShapeExtend_DONE2)'

#### `ShapeUpgrade_RemoveInternalWires.removeSmallWire` — lines 141–187
(4 branches, 3 covered.)

- **Branch 1** @ line 149 — *non_wire_subshape* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: iterator value is not a wire or is outer wire
  - Repair action: skip to next subshape
- **Branch 2** @ line 155 — *explicit_wire_filter* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: caller specified a target wire and current wire doesn't match
  - Repair action: skip processing this wire
- **Branch 3** @ line 160 — *small_area_wire* — **UNCOVERED**
  - What it tests: wire area less than threshold
  - Repair action: mark wire for removal and track contained edges
  - Suggested fixture: defect mentioning 'if (anArea < myMinArea - Precision::Confusion())', 'Context()->Remove(aW)'
- **Branch 4** @ line 165 — *edge_tracking_mode* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: myRemoveFacesMode is true when wire removed
  - Repair action: build edge-to-faces mapping for later face removal analysis


### `multiple`

14 methods, 81 branches, 21 covered.

#### `BRepLib.BoundingVertex` — lines 3016–3123
(10 branches, 1 covered.)

- **Branch 1** @ line 3018 — *count_validation* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: At least 2 vertices in list
  - Repair action: Early return if fewer than 2 vertices
- **Branch 2** @ line 3020 — *two_vertex_case* — **UNCOVERED**
  - What it tests: Exactly 2 vertices (special case)
  - Repair action: Use 2-vertex bounding sphere algorithm
  - Suggested fixture: defect mentioning 'else if (aNb == 2)'
- **Branch 3** @ line 3029 — *radius_comparison* — **UNCOVERED**
  - What it tests: Which vertex has larger tolerance
  - Repair action: Determine max/min radius for sphere calc
  - Suggested fixture: defect mentioning 'm = 0', 'aR[0] < aR[1]'
- **Branch 4** @ line 3035 — *distance_based_collapse* — **UNCOVERED**
  - What it tests: Spheres overlap or are very close
  - Repair action: Use larger sphere center if overlap detected
  - Suggested fixture: defect mentioning 'if (aD <= dR || aD < aEps)', 'theNewCenter = aP[m]'
- **Branch 5** @ line 3037 — *two_sphere_bounding* — **UNCOVERED**
  - What it tests: Compute bounding sphere for two separated spheres
  - Repair action: Calculate smallest enclosing sphere
  - Suggested fixture: defect mentioning 'aRr = 0.5 * (aR[m] + aR[n] + aD)'
- **Branch 6** @ line 3045 — *sphere_center_compute* — **UNCOVERED**
  - What it tests: Compute center of bounding sphere
  - Repair action: Place sphere center between vertex centers
  - Suggested fixture: defect mentioning 'aXYZr = 0.5 * (aP[m].XYZ() + aP[n].XYZ()'
- **Branch 7** @ line 3054 — *many_vertices_case* — **UNCOVERED**
  - What it tests: More than 2 vertices (general case)
  - Repair action: Use stable multi-vertex algorithm
  - Suggested fixture: defect mentioning 'else { // if (aNb>2)'
- **Branch 8** @ line 3062 — *point_sorting* — **UNCOVERED**
  - What it tests: Sort points for stable centroid computation
  - Repair action: Order points to make sum independent of input order
  - Suggested fixture: defect mentioning 'std::sort(aPoints.begin()', 'BRepLib_ComparePoints'
- **Branch 9** @ line 3067 — *centroid_computation* — **UNCOVERED**
  - What it tests: Compute centroid of all vertices
  - Repair action: Average all vertex positions
  - Suggested fixture: defect mentioning 'aXYZ += aPoints(i).XYZ()', 'Divide((double)aNb)'
- **Branch 10** @ line 3079 — *max_distance_search* — **UNCOVERED**
  - What it tests: Find maximum distance from centroid
  - Repair action: Search for vertex farthest from center
  - Suggested fixture: defect mentioning 'aDi = aDi + aTi', 'if (aDi > aDmax)'

#### `ShapeAnalysis_Edge.BoundUV` — lines 61–89
(6 branches, 6 covered.)

- **Branch 1** @ line 64 — *surface_retrieval* — COVERED by: a017, tfa031
  - What it tests: Extract geometric surface from face with location
  - Repair action: Get surface from face, extract location transform
- **Branch 2** @ line 65 — *pcurve_delegation* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Delegates to overload with surface and location
  - Repair action: Call 2nd overload with surface instead of face
- **Branch 3** @ line 77 — *pcurve_evaluation* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1194 more)
  - What it tests: P-curve exists and can be evaluated
  - Repair action: Get parametric curve on surface
- **Branch 4** @ line 78 — *pcurve_validation* — COVERED by: in014
  - What it tests: P-curve is valid (not null)
  - Repair action: Return false if P-curve missing
- **Branch 5** @ line 81 — *parameter_evaluation* — COVERED by: a081, a086, a098, a103, ad026, ad064, ad080, ad086 (+117 more)
  - What it tests: Evaluate p-curve at start parameter
  - Repair action: Extract first boundary point from p-curve
- **Branch 6** @ line 82 — *parameter_evaluation* — COVERED by: a099, ad086, ad089, ad090, ad101, gb003, gn024, gn033 (+35 more)
  - What it tests: Evaluate p-curve at end parameter
  - Repair action: Extract last boundary point from p-curve

#### `ShapeAnalysis_Edge.PCurve_overload1` — lines 177–188
(2 branches, 2 covered.)

- **Branch 1** @ line 181 — *surface_extraction* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Extract surface from face with location
  - Repair action: Get geometric surface and transform location
- **Branch 2** @ line 182 — *pcurve_delegation* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Delegation to surface-based overload
  - Repair action: Call PCurve with surface instead of face

#### `ShapeAnalysis_Edge.PCurve_overload2` — lines 199–208
(4 branches, 1 covered.)

- **Branch 1** @ line 200 — *pcurve_retrieval* — **UNCOVERED**
  - What it tests: Get parametric curve from BRep topology
  - Repair action: Retrieve p-curve on surface with location
  - Suggested fixture: defect mentioning 'BRep_Tool::CurveOnSurface'
- **Branch 2** @ line 201 — *orientation_handling* — COVERED by: a007, a024, a026, a101, ad047, ad057, ad082, ad086 (+186 more)
  - What it tests: Check orient flag and edge orientation
  - Repair action: Swap parameters if edge is reversed
- **Branch 3** @ line 202 — *parameter_swap* — **UNCOVERED**
  - What it tests: Swap start/end parameters for reversed edge
  - Repair action: Reverse parameter order for REVERSED orientation
  - Suggested fixture: defect mentioning 'double tmp = cf', 'cf = cl', 'cl = tmp'
- **Branch 4** @ line 205 — *pcurve_validity* — **UNCOVERED**
  - What it tests: P-curve is valid (not null)
  - Repair action: Return false if p-curve is null
  - Suggested fixture: defect mentioning '!C2d.IsNull()'

#### `ShapeFix_IntersectionTool.FindVertAndSplitEdge` — lines 979–1025
(7 branches, 1 covered.)

- **Branch 1** @ line 987 — *bounding_box_void_check* — **UNCOVERED**
  - What it tests: Wire bounding boxes are valid
  - Repair action: Skip wire pair if bbox is void/empty
  - Suggested fixture: defect mentioning 'aBox1.IsVoid()', 'aBox2.IsVoid()'
- **Branch 2** @ line 989 — *bbox_intersection_test* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wires can potentially intersect
  - Repair action: Skip pair if no bbox overlap
- **Branch 3** @ line 995 — *degenerate_edge_skip* — **UNCOVERED**
  - What it tests: Edge is not degenerate
  - Repair action: Skip if edge is degenerate (zero-length)
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated'
- **Branch 4** @ line 1000 — *edge_bbox_binding* — **UNCOVERED**
  - What it tests: Edge bounding boxes have been computed
  - Repair action: Skip if bbox not in cache
  - Suggested fixture: defect mentioning 'boxes1.IsBound(edge1)', 'boxes2.IsBound(edge2)'
- **Branch 5** @ line 1003 — *detailed_bbox_test* — **UNCOVERED**
  - What it tests: Detailed bounding box overlap check
  - Repair action: Test if 2D boxes actually overlap
  - Suggested fixture: defect mentioning 'B1.IsOut(B2)', 'intersection is possible'
- **Branch 6** @ line 1006 — *pcurve_retrieval_1* — **UNCOVERED**
  - What it tests: Get p-curve from first edge
  - Repair action: Retrieve parametric curve for edge1
  - Suggested fixture: defect mentioning 'sae.PCurve(edge1, face'
- **Branch 7** @ line 1008 — *pcurve_retrieval_2* — **UNCOVERED**
  - What it tests: Get p-curve from second edge
  - Repair action: Retrieve parametric curve for edge2
  - Suggested fixture: defect mentioning 'sae.PCurve(edge2, face'

#### `ShapeFix_IntersectionTool.SplitEdge1` — lines 278–358
(8 branches, 1 covered.)

- **Branch 1** @ line 289 — *edge_bounds_validation* — **UNCOVERED**
  - What it tests: num parameter is within wire edge count
  - Repair action: Validate edge index before access
  - Suggested fixture: defect mentioning 'Standard_ASSERT_RETURN', 'num > 0', 'num <= sewd->NbEdges()'
- **Branch 2** @ line 292 — *edge_split_execution* — **UNCOVERED**
  - What it tests: SplitEdge call succeeds on edge
  - Repair action: Split single edge at parameter with vertex
  - Suggested fixture: defect mentioning '!SplitEdge(edge, param'
- **Branch 3** @ line 298 — *context_update* — **UNCOVERED**
  - What it tests: Topology context exists and needs update
  - Repair action: Replace edge in context with new edges
  - Suggested fixture: defect mentioning 'myContext.IsNull()', 'myContext->Replace'
- **Branch 4** @ line 306 — *wire_data_update* — **UNCOVERED**
  - What it tests: Update wire data structure
  - Repair action: Replace original edge with two split edges
  - Suggested fixture: defect mentioning 'sewd->Set(newE1, num)', 'sewd->Add(newE2'
- **Branch 5** @ line 310 — *edge_position* — **UNCOVERED**
  - What it tests: Is split edge at end of wire or middle
  - Repair action: Add newE2 at correct position (end or mid)
  - Suggested fixture: defect mentioning 'num == sewd->NbEdges()', 'sewd->Add', 'num + 1'
- **Branch 6** @ line 316 — *bounding_box_computation* — COVERED by: a095, a107, ad086, bo003, fi006, gn010, gs002, hea013 (+31 more)
  - What it tests: Compute bounding box for first new edge
  - Repair action: Get p-curve bounds and create 2D bbox
- **Branch 7** @ line 322 — *bspline_range_handling* — **UNCOVERED**
  - What it tests: Handle B-spline with extended range
  - Repair action: Load full curve if cf/cl outside natural range
  - Suggested fixture: defect mentioning 'Geom2d_BSplineCurve', 'cf < aFirst', 'cl > aLast'
- **Branch 8** @ line 333 — *bounding_box_computation_2* — **UNCOVERED**
  - What it tests: Compute bounding box for second new edge
  - Repair action: Get p-curve bounds and create 2D bbox
  - Suggested fixture: defect mentioning 'sae.PCurve(newE2'

#### `ShapeUpgrade_FaceDivide.Perform` — lines 80–94
(4 branches, 1 covered.)

- **Branch 1** @ line 82 — *null_input* — COVERED by: in014
  - What it tests: Face object is null/uninitialized
  - Repair action: early return false if myFace is null
- **Branch 2** @ line 86 — *context_missing* — **UNCOVERED**
  - What it tests: ReShape context is not set
  - Repair action: initialize new ReShape context if missing
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'SetContext'
- **Branch 3** @ line 91 — *surface_splitting* — **UNCOVERED**
  - What it tests: Surface decomposition failure path
  - Repair action: invoke surface split with area constraint
  - Suggested fixture: defect mentioning 'SplitSurface(theArea)'
- **Branch 4** @ line 92 — *curve_splitting* — **UNCOVERED**
  - What it tests: Edge/wire decomposition failure path
  - Repair action: invoke curve split on all edges
  - Suggested fixture: defect mentioning 'SplitCurves()'

#### `ShapeUpgrade_FaceDivide.SplitCurves` — lines 207–253
(5 branches, 2 covered.)

- **Branch 1** @ line 209 — *missing_wire_tool* — **UNCOVERED**
  - What it tests: WireDivide tool initialization failure
  - Repair action: return false if wire tool unavailable
  - Suggested fixture: defect mentioning 'GetWireDivideTool()', 'IsNull()'
- **Branch 2** @ line 220 — *invalid_applied_shape* — COVERED by: tsh018
  - What it tests: Applied context shape is not a FACE
  - Repair action: set FAIL3 status and return false
- **Branch 3** @ line 232 — *non_wire_iterator* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face sub-entity is not a WIRE
  - Repair action: skip non-wire entities in face boundary
- **Branch 4** @ line 240 — *wire_split_failure* — **UNCOVERED**
  - What it tests: SplitWire::Perform reports FAIL status
  - Repair action: set FAIL1 status on wire split failure
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_FAIL)', 'ShapeExtend_FAIL1'
- **Branch 5** @ line 244 — *wire_split_success* — **UNCOVERED**
  - What it tests: Wire was successfully split
  - Repair action: record split wire in context and set DONE1 status
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE)', 'Context()->Replace', 'ShapeExtend_DONE1'

#### `ShapeUpgrade_FaceDivide.SplitSurface` — lines 99–202
(14 branches, 1 covered.)

- **Branch 1** @ line 101 — *missing_tool* — **UNCOVERED**
  - What it tests: SplitSurface tool initialization failure
  - Repair action: return false if tool unavailable
  - Suggested fixture: defect mentioning 'GetSplitSurfaceTool()', 'IsNull()'
- **Branch 2** @ line 107 — *invalid_shape_type* — COVERED by: tsh018
  - What it tests: Result not a FACE topology
  - Repair action: set FAIL3 status and return false
- **Branch 3** @ line 121 — *infinite_bounds* — **UNCOVERED**
  - What it tests: UV bounds are infinite (unbounded surface)
  - Repair action: return false without modification
  - Suggested fixture: defect mentioning 'Precision::IsInfinite', 'GetFaceUVBounds'
- **Branch 4** @ line 130 — *non_periodic_u* — **UNCOVERED**
  - What it tests: U-parameter surface is non-periodic
  - Repair action: adjust U bounds with small extension if within surface bounds
  - Suggested fixture: defect mentioning 'IsUPeriodic()', 'Uf -= std::min'
- **Branch 5** @ line 133 — *u_bound_adjustment_lower* — **UNCOVERED**
  - What it tests: Lower U parameter has clearance from surface limit
  - Repair action: extend lower U bound towards surface lower limit
  - Suggested fixture: defect mentioning 'Uf > aSUf'
- **Branch 6** @ line 137 — *u_bound_adjustment_upper* — **UNCOVERED**
  - What it tests: Upper U parameter has clearance from surface limit
  - Repair action: extend upper U bound towards surface upper limit
  - Suggested fixture: defect mentioning 'Ul < aSUl'
- **Branch 7** @ line 142 — *non_periodic_v* — **UNCOVERED**
  - What it tests: V-parameter surface is non-periodic
  - Repair action: adjust V bounds with small extension if within surface bounds
  - Suggested fixture: defect mentioning 'IsVPeriodic()', 'Vf -= std::min'
- **Branch 8** @ line 145 — *v_bound_adjustment_lower* — **UNCOVERED**
  - What it tests: Lower V parameter has clearance from surface limit
  - Repair action: extend lower V bound towards surface lower limit
  - Suggested fixture: defect mentioning 'Vf > aSVf'
- **Branch 9** @ line 149 — *v_bound_adjustment_upper* — **UNCOVERED**
  - What it tests: Upper V parameter has clearance from surface limit
  - Repair action: extend upper V bound towards surface upper limit
  - Suggested fixture: defect mentioning 'Vl < aSVl'
- **Branch 10** @ line 159 — *no_split_performed* — **UNCOVERED**
  - What it tests: Surface splitting produced no change
  - Repair action: return false if SplitSurf has no DONE status
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE)'
- **Branch 11** @ line 166 — *surface_modified* — **UNCOVERED**
  - What it tests: Surface was modified (requires vertex copying)
  - Repair action: copy all vertices to prevent tolerance increase
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE3)'
- **Branch 12** @ line 170 — *vertex_already_recorded* — **UNCOVERED**
  - What it tests: Vertex already in ReShape context
  - Repair action: skip vertex copy if already recorded
  - Suggested fixture: defect mentioning 'IsRecorded(exp.Current())'
- **Branch 13** @ line 188 — *wire_tool_available* — **UNCOVERED**
  - What it tests: WireDivide tool is available for parameter transfer
  - Repair action: set transfer param tool if available
  - Suggested fixture: defect mentioning 'GetWireDivideTool()', 'SetTransferParamTool'
- **Branch 14** @ line 193 — *composite_shell_failure* — **UNCOVERED**
  - What it tests: ComposeShell reports FAIL or no DONE status
  - Repair action: set FAIL2 status on composition failure
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_FAIL)', 'ShapeExtend_FAIL2'

#### `ShapeUpgrade_FaceDivideArea.Perform` — lines 58–146
(9 branches, 3 covered.)

- **Branch 1** @ line 66 — *max_area_auto_compute* — **UNCOVERED**
  - What it tests: User did not specify max area (myMaxArea==-1)
  - Repair action: compute max area by dividing total by part count
  - Suggested fixture: defect mentioning 'myMaxArea == -1', 'myNbParts'
- **Branch 2** @ line 72 — *area_below_threshold* — COVERED by: gp013, tb001, tb007, tb018, tb019, twi040
  - What it tests: Face area is below max area threshold
  - Repair action: return false without splitting (no action needed)
- **Branch 3** @ line 84 — *split_tool_null* — **UNCOVERED**
  - What it tests: SplitSurfaceArea tool is null
  - Repair action: return false if tool not available
  - Suggested fixture: defect mentioning 'down_cast<ShapeUpgrade_SplitSurfaceArea>', 'IsNull()'
- **Branch 4** @ line 89 — *splitting_by_number* — **UNCOVERED**
  - What it tests: User specified splitting by count (not area)
  - Repair action: enable square splitting mode with UV split counts
  - Suggested fixture: defect mentioning 'myIsSplittingByNumber', 'SetSplittingIntoSquares'
- **Branch 5** @ line 94 — *parent_perform_failure* — COVERED by: tfa051
  - What it tests: Parent FaceDivide::Perform fails
  - Repair action: return false on parent failure
- **Branch 6** @ line 100 — *result_not_shell* — **UNCOVERED**
  - What it tests: Result is still single FACE (not subdivided)
  - Repair action: return false if result was not split into compound
  - Suggested fixture: defect mentioning 'aResult.ShapeType() == TopAbs_FACE'
- **Branch 7** @ line 106 — *recursive_split_needed* — **UNCOVERED**
  - What it tests: User wants recursive splitting by area (not by count)
  - Repair action: recursively split each result face that exceeds max area
  - Suggested fixture: defect mentioning '!myIsSplittingByNumber'
- **Branch 8** @ line 118 — *recursive_face_oversized* — COVERED by: hea001
  - What it tests: Individual result face still exceeds max area
  - Repair action: recursively invoke Perform on face to split further
- **Branch 9** @ line 133 — *recursive_changes_applied* — **UNCOVERED**
  - What it tests: Recursive splitting produced changes
  - Repair action: rebuild result compound with recursively split faces
  - Suggested fixture: defect mentioning 'isModified', 'Context()->Replace'

#### `ShapeUpgrade_ShellSewing.Apply` — lines 83–113
(3 branches, 0 covered.)

- **Branch 1** @ line 84 — *null_input_or_empty_shells* — **UNCOVERED**
  - What it tests: Input is null or no shells were collected
  - Repair action: return input shape unchanged
  - Suggested fixture: defect mentioning 'shape.IsNull()', 'myShells.Extent() == 0'
- **Branch 2** @ line 99 — *inverted_solid* — **UNCOVERED**
  - What it tests: Solid has inverted orientation (inside-out)
  - Repair action: reverse solid and record in context
  - Suggested fixture: defect mentioning 'bsc3d.State() == TopAbs_IN', 'sd.Reversed()'
- **Branch 3** @ line 107 — *solid_inversion_applied* — **UNCOVERED**
  - What it tests: At least one solid needed reversal
  - Repair action: re-apply context to update shell topology
  - Suggested fixture: defect mentioning 'ns != 0', 'Apply(res, TopAbs_SHELL'

#### `ShapeUpgrade_ShellSewing.ApplySewing` — lines 118–138
(4 branches, 0 covered.)

- **Branch 1** @ line 119 — *null_input* — **UNCOVERED**
  - What it tests: Input shape is null
  - Repair action: return empty shape
  - Suggested fixture: defect mentioning 'shape.IsNull()', 'return shape'
- **Branch 2** @ line 125 — *tolerance_not_specified* — **UNCOVERED**
  - What it tests: Caller passed zero or negative tolerance
  - Repair action: compute mean tolerance from shape
  - Suggested fixture: defect mentioning 't <= 0.', 'Tolerance(shape)'
- **Branch 3** @ line 132 — *prepare_success* — **UNCOVERED**
  - What it tests: Sewing preparation found shells to fix
  - Repair action: apply sewing modifications
  - Suggested fixture: defect mentioning 'Prepare(t)', 'return Apply'
- **Branch 4** @ line 137 — *prepare_failed* — **UNCOVERED**
  - What it tests: No shells needed sewing or preparation failed
  - Repair action: return empty shape (no result to return)
  - Suggested fixture: defect mentioning 'return TopoDS_Shape()'

#### `ShapeUpgrade_ShellSewing.Init` — lines 37–53
(3 branches, 2 covered.)

- **Branch 1** @ line 38 — *null_input* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Input shape is null
  - Repair action: return immediately without processing
- **Branch 2** @ line 42 — *direct_shell* — **UNCOVERED**
  - What it tests: Input is already a SHELL (not compound)
  - Repair action: add shell directly to collection
  - Suggested fixture: defect mentioning 'TopAbs_SHELL', 'myShells.Add'
- **Branch 3** @ line 48 — *extract_shells* — COVERED by: tsh018
  - What it tests: Input is compound or solid (contains shells)
  - Repair action: iterate and extract all constituent shells

#### `ShapeUpgrade_ShellSewing.Prepare` — lines 58–78
(2 branches, 0 covered.)

- **Branch 1** @ line 69 — *sewing_performed* — **UNCOVERED**
  - What it tests: BRepBuilderAPI_Sewing produced non-null result
  - Repair action: replace shell in context with sewn result
  - Suggested fixture: defect mentioning 'ss.SewedShape()', 'myReShape->Replace'
- **Branch 2** @ line 71 — *sewing_produced_null* — **UNCOVERED**
  - What it tests: Sewing operation returned null shape
  - Repair action: skip replacement if sewing failed
  - Suggested fixture: defect mentioning 'newsh.IsNull()'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_CheckSmallFace.cxx`

16 methods, 133 branches, 21 covered.

#### `CheckPin` — lines 849–958
(13 branches, 1 covered.)

- **Branch 1** @ line 852 — *ELEMENTARY_SURFACE* — **UNCOVERED**
  - What it tests: Surface is elementary (plane, cone, sphere, cylinder, etc.)
  - Repair action: Return false, pin detection not applicable to elementary surfaces
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_ElementarySurface))'
- **Branch 2** @ line 858 — *PRECISION_UNDEFINED* — **UNCOVERED**
  - What it tests: Precision value negative or unset
  - Repair action: Use default tolerance 1e-4 instead of myPrecision
  - Suggested fixture: defect mentioning 'toler < 0', 'toler = 1.e-4'
- **Branch 3** @ line 870 — *BSPLINE_SURFACE* — **UNCOVERED**
  - What it tests: Surface is B-spline, extract pole array
  - Repair action: Get nbu, nbv pole counts from BSpline surface
  - Suggested fixture: defect mentioning 'bs->NbUPoles', 'bs->NbVPoles'
- **Branch 4** @ line 875 — *BEZIER_SURFACE* — **UNCOVERED**
  - What it tests: Surface is Bezier, extract pole array
  - Repair action: Get nbu, nbv pole counts from Bezier surface
  - Suggested fixture: defect mentioning 'bz->NbUPoles', 'bz->NbVPoles'
- **Branch 5** @ line 880 — *NO_POLES_AVAILABLE* — **UNCOVERED**
  - What it tests: Neither BSpline nor Bezier surface, or pole count is zero
  - Repair action: Return false, cannot detect pin without pole information
  - Suggested fixture: defect mentioning 'nbu == 0 || nbv == 0'
- **Branch 6** @ line 901 — *PIN_BOTTOM_U_ROW* — **UNCOVERED**
  - What it tests: Bottom U-directional isoline is singular (pin at v_min)
  - Repair action: Set sens=1 (U-direction), whatrow=nbu, record IsoStat result
  - Suggested fixture: defect mentioning 'IsoStat(allpoles, 1, 1', 'sens = 1'
- **Branch 7** @ line 908 — *PIN_TOP_U_ROW* — **UNCOVERED**
  - What it tests: Top U-directional isoline is singular (pin at v_max)
  - Repair action: Set sens=1 (U-direction), whatrow=nbu
  - Suggested fixture: defect mentioning 'IsoStat(allpoles, 1, nbu', 'whatrow = nbu'
- **Branch 8** @ line 915 — *PIN_LEFT_V_ROW* — **UNCOVERED**
  - What it tests: Left V-directional isoline is singular (pin at u_min)
  - Repair action: Set sens=2 (V-direction), whatrow=1
  - Suggested fixture: defect mentioning 'IsoStat(allpoles, 2, 1', 'whatrow = 1'
- **Branch 9** @ line 922 — *PIN_RIGHT_V_ROW* — **UNCOVERED**
  - What it tests: Right V-directional isoline is singular (pin at u_max)
  - Repair action: Set sens=2 (V-direction), whatrow=nbv
  - Suggested fixture: defect mentioning 'IsoStat(allpoles, 2, nbv', 'whatrow = nbv'
- **Branch 10** @ line 929 — *NO_PIN_DETECTED* — COVERED by: in014
  - What it tests: No singularity found on any boundary
  - Repair action: Return false, surface is non-degenerate
- **Branch 11** @ line 934 — *PIN_SMOOTH_TYPE* — **UNCOVERED**
  - What it tests: Pin is smooth (stat == 1): poles converge gradually
  - Repair action: Record status DONE1, check for equal poles at other end
  - Suggested fixture: defect mentioning 'case 1:', 'ShapeExtend_DONE1'
- **Branch 12** @ line 939 — *PIN_SHARP_TYPE* — **UNCOVERED**
  - What it tests: Pin is sharp (stat == 2): poles collapse abruptly
  - Repair action: Record status DONE2
  - Suggested fixture: defect mentioning 'case 2:', 'ShapeExtend_DONE2'
- **Branch 13** @ line 947 — *MULTIPLE_EQUAL_POLES* — **UNCOVERED**
  - What it tests: Smooth pin with multiple identical poles at boundaries
  - Repair action: Record status DONE3, detect multiple collapses
  - Suggested fixture: defect mentioning 'CheckPoles', 'ShapeExtend_DONE3'

#### `CheckPinEdges` — lines 1208–1341
(13 branches, 3 covered.)

- **Branch 1** @ line 1226 — *TOLERANCE_SELECTION* — **UNCOVERED**
  - What it tests: Input tolerance toler is -1 (use vertex tolerance)
  - Repair action: Extract tolerance from shared vertex, else use toler parameter
  - Suggested fixture: defect mentioning 'if (toler == -1)', 'BRep_Tool::Tolerance'
- **Branch 2** @ line 1235 — *SHARED_VERTEX_AT_START_C1* — **UNCOVERED**
  - What it tests: Shared vertex coincides with start of first curve
  - Repair action: Set paramc1 = cf1 (first curve start parameter)
  - Suggested fixture: defect mentioning 'pv.Distance(p1) <= tol', 'paramc1 = cf1'
- **Branch 3** @ line 1239 — *SHARED_VERTEX_AT_END_C1* — **UNCOVERED**
  - What it tests: Shared vertex coincides with end of first curve
  - Repair action: Set paramc1 = cl1 (first curve end parameter)
  - Suggested fixture: defect mentioning 'else if (pv.Distance(p2) <= tol)', 'paramc1 = cl1'
- **Branch 4** @ line 1243 — *SHARED_VERTEX_AT_START_C2* — **UNCOVERED**
  - What it tests: Shared vertex coincides with start of second curve
  - Repair action: Set paramc2 = cf2
  - Suggested fixture: defect mentioning 'pv.Distance(pp1) <= tol', 'paramc2 = cf2'
- **Branch 5** @ line 1247 — *SHARED_VERTEX_AT_END_C2* — **UNCOVERED**
  - What it tests: Shared vertex coincides with end of second curve
  - Repair action: Set paramc2 = cl2
  - Suggested fixture: defect mentioning 'else if (pv.Distance(pp2) <= tol)', 'paramc2 = cl2'
- **Branch 6** @ line 1270 — *SHORTEST_EDGE_SELECTION* — **UNCOVERED**
  - What it tests: First curve is shorter than second (p1.Distance(p2) < pp1.Distance(pp2))
  - Repair action: Use first curve for projection test point
  - Suggested fixture: defect mentioning 'p1.Distance(p2) < pp1.Distance(pp2)', 'C3 = C1'
- **Branch 7** @ line 1273 — *POINT_ALONG_CURVE_FROM_START* — **UNCOVERED**
  - What it tests: Shared vertex at start of curve (paramc1 == cf1)
  - Repair action: Compute test point inward: C1->Value(cf1 + (coef1-3)*d1)
  - Suggested fixture: defect mentioning 'if (paramc1 == cf1)', 'proj = C1->Value'
- **Branch 8** @ line 1279 — *POINT_ALONG_CURVE_FROM_END* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Shared vertex at end of curve (paramc1 != cf1)
  - Repair action: Compute test point inward: C1->Value(paramc1 - 3*d1)
- **Branch 9** @ line 1306 — *PROJECTION_OUT_OF_RANGE* — **UNCOVERED**
  - What it tests: Projected point parameter outside curve domain [f, l]
  - Repair action: Return false, projection is invalid
  - Suggested fixture: defect mentioning 'if (param < f || param > l)'
- **Branch 10** @ line 1310 — *PROJECTION_DISTANCE_EXCESSIVE* — COVERED by: in014
  - What it tests: Distance from test point to curve > tolerance
  - Repair action: Return false, curves diverge too much
- **Branch 11** @ line 1314 — *ANGLE_AND_CURVATURE_MATCH* — **UNCOVERED**
  - What it tests: Curves meet within tolerance, check angle continuity at shared vertex
  - Repair action: Compute 2nd derivatives and angle between curves
  - Suggested fixture: defect mentioning 'if (dist <= tol)', 'C1->D2', 'C2->D2'
- **Branch 12** @ line 1322 — *ANGLE_COMPUTATION_FAILURE* — COVERED by: in014
  - What it tests: Exception during angle computation (degenerate tangent)
  - Repair action: Return false, cannot assess pin pattern
- **Branch 13** @ line 1336 — *PIN_ANGLE_THRESHOLD* — **UNCOVERED**
  - What it tests: Angle continuity satisfied: angle1 <= 0.001 AND angle2 <= 0.01 OR supplementary angles match
  - Repair action: Return true, confirm pin pair has proper angle match
  - Suggested fixture: defect mentioning 'angle1 <= 0.001 && angle2 <= 0.01', 'M_PI - angle2'

#### `CheckPinFace` — lines 1069–1197
(14 branches, 3 covered.)

- **Branch 1** @ line 1105 — *FIRST_EDGE_SELECTION* — **UNCOVERED**
  - What it tests: Processing first edge in sequence, extract vertices and length
  - Repair action: Store edge, measure distance d1, compute length-to-tolerance ratio coef1
  - Suggested fixture: defect mentioning 'if (i == 1)', 'theFirstEdge'
- **Branch 2** @ line 1118 — *DEGENERATE_EDGE* — COVERED by: in014
  - What it tests: Edge has zero length (d1 == 0)
  - Repair action: Return false, cannot establish pin coefficient
- **Branch 3** @ line 1122 — *EDGE_LENGTH_RATIO* — **UNCOVERED**
  - What it tests: Edge length d1 is at least tol (ratio >= 1)
  - Repair action: Compute coef1 = d1/tol for this edge
  - Suggested fixture: defect mentioning 'd1 / tol >= 1', 'coef1 = d1 / tol'
- **Branch 4** @ line 1130 — *PIN_COEFFICIENT_LOW* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: First edge length too small (coef1 <= 3, i.e., d1 <= 3*tol)
  - Repair action: Continue to next edge, this edge is too short for pin analysis
- **Branch 5** @ line 1113 — *TOLERANCE_OVERRIDE* — **UNCOVERED**
  - What it tests: Input tolerance toler is positive (override mode)
  - Repair action: Use toler instead of vertex tolerance
  - Suggested fixture: defect mentioning 'if (toler > 0)', 'tol = toler'
- **Branch 6** @ line 1144 — *TOLERANCE_SELECTION_SECOND* — **UNCOVERED**
  - What it tests: For subsequent edges, toler == -1 (use vertex tolerance)
  - Repair action: Extract tolerance from vertices of second edge
  - Suggested fixture: defect mentioning 'if (toler == -1)'
- **Branch 7** @ line 1152 — *SECOND_EDGE_LENGTH_CHECK* — **UNCOVERED**
  - What it tests: Second edge length exceeds tolerance (non-degenerate)
  - Repair action: Continue, this edge is not a pin candidate
  - Suggested fixture: defect mentioning 'p1.Distance(p2) > tol'
- **Branch 8** @ line 1158 — *DEGENERATE_SECOND_EDGE* — **UNCOVERED**
  - What it tests: Second edge has zero length (d2 == 0)
  - Repair action: Return false, cannot form pin pair
  - Suggested fixture: defect mentioning 'd2 == 0'
- **Branch 9** @ line 1162 — *SECOND_EDGE_RATIO* — **UNCOVERED**
  - What it tests: Second edge length ratio (coef2 = d2/tol)
  - Repair action: Compute coef2 for second edge
  - Suggested fixture: defect mentioning 'd2 / tol >= 1', 'coef2 = d2 / tol'
- **Branch 10** @ line 1170 — *SECOND_EDGE_TOO_SHORT* — **UNCOVERED**
  - What it tests: Second edge ratio too small (coef2 <= 3)
  - Repair action: Continue, need both edges to be suitably short
  - Suggested fixture: defect mentioning 'coef2 <= 3'
- **Branch 11** @ line 1174 — *COEFFICIENT_RATIO_FIRST_DOMINATES* — **UNCOVERED**
  - What it tests: First edge dominates second by >10x (coef1 > coef2 * 10)
  - Repair action: Continue, coefficients too imbalanced
  - Suggested fixture: defect mentioning 'coef1 > coef2 * 10'
- **Branch 12** @ line 1178 — *COEFFICIENT_RATIO_SECOND_DOMINATES* — **UNCOVERED**
  - What it tests: Second edge dominates first by >10x (coef2 > coef1 * 10)
  - Repair action: Make second edge the new first, continue searching
  - Suggested fixture: defect mentioning 'coef2 > coef1 * 10', 'theFirstEdge = theSecondEdge'
- **Branch 13** @ line 1185 — *PIN_EDGE_PAIR_VALIDATION* — COVERED by: twi058
  - What it tests: CheckPinEdges confirms geometric pin pattern (angles, projection)
  - Repair action: If true, bind edges to map, record DONE status, set done=true
- **Branch 14** @ line 1196 — *MULTIPLE_PIN_PAIRS* — **UNCOVERED**
  - What it tests: Continuing search after finding one pin pair
  - Repair action: Update theFirstEdge, coef1 for next iteration
  - Suggested fixture: defect mentioning 'theFirstEdge = theSecondEdge', 'coef1 = coef2'

#### `CheckSplittingVertices` — lines 681–791
(9 branches, 1 covered.)

- **Branch 1** @ line 700 — *EMPTY_WIRE* — **UNCOVERED**
  - What it tests: Checks if face has zero vertices (malformed wire)
  - Repair action: Return 0 (no splitting vertices), skip processing
  - Suggested fixture: defect mentioning 'nbv == 0', 'TopAbs_VERTEX'
- **Branch 2** @ line 717 — *TOLERANCE_UNDEFINED* — **UNCOVERED**
  - What it tests: Vertex tolerance not set, uses BRep tool to extract it
  - Repair action: Fall back to stored vertex tolerance instead of myPrecision
  - Suggested fixture: defect mentioning 'myPrecision', 'BRep_Tool::Tolerance'
- **Branch 3** @ line 741 — *MISSING_3D_CURVE* — **UNCOVERED**
  - What it tests: Edge lacks 3D curve definition (degenerate edge)
  - Repair action: Skip this edge, continue to next (C3D.IsNull check)
  - Suggested fixture: defect mentioning 'C3D.IsNull', 'BRep_Tool::Curve'
- **Branch 4** @ line 745 — *VERTEX_AT_EDGE_ENDPOINT* — **UNCOVERED**
  - What it tests: Vertex is endpoint of edge (not an interior split point)
  - Repair action: Skip edge, continue checking next edge
  - Suggested fixture: defect mentioning 'V.IsSame(V1)', 'TopExp::Vertices'
- **Branch 5** @ line 753 — *PROJECTION_FAILURE* — **UNCOVERED**
  - What it tests: Cannot project vertex to edge curve (numerical failure)
  - Repair action: Skip edge, continue
  - Suggested fixture: defect mentioning 'SAC.Project', 'dist == 0.0'
- **Branch 6** @ line 759 — *VERTEX_ON_EDGE_INTERIOR* — **UNCOVERED**
  - What it tests: Vertex distance to edge curve is less than vertex tolerance
  - Repair action: Mark vertex as splitting point, record edge and parameter
  - Suggested fixture: defect mentioning 'dist < unt', 'issplit = true'
- **Branch 7** @ line 763 — *PARAMETER_AT_BOUNDARY* — **UNCOVERED**
  - What it tests: Projection parameter at or beyond curve parameter bounds
  - Repair action: Reject split, not truly interior (param >= cl || param <= cf)
  - Suggested fixture: defect mentioning 'param >= cl', 'param <= cf'
- **Branch 8** @ line 769 — *PARAMETER_NEAR_ENDPOINT* — COVERED by: tfa060
  - What it tests: Projection very close to endpoint (within eps=1e-6 of param change)
  - Repair action: Reject split, consider as endpoint artifact
- **Branch 9** @ line 786 — *SPLITTING_VERTICES_FOUND* — **UNCOVERED**
  - What it tests: One or more splitting vertices identified
  - Repair action: Record status DONE in myStatusSplitVert
  - Suggested fixture: defect mentioning 'nbp != 0', 'myStatusSplitVert'

#### `CheckStripFace` — lines 659–677
(2 branches, 1 covered.)

- **Branch 1** @ line 662 — *STRIP_SINGLE_WIDTH* — COVERED by: tfa047
  - What it tests: Detects if face is a single-width strip with identical opposing edges
  - Repair action: Accept face as valid strip, pass for further processing
- **Branch 2** @ line 676 — *STRIP_OPPOSING_EDGES* — **UNCOVERED**
  - What it tests: Attempts to find opposing edges with minimal distance (dmax) for multi-strip detection
  - Repair action: Return strip edge pair E1, E2 if found within tolerance
  - Suggested fixture: defect mentioning 'FindStripEdges', 'dmax'

#### `CheckTwisted` — lines 975–1059
(7 branches, 4 covered.)

- **Branch 1** @ line 978 — *ELEMENTARY_SURFACE* — **UNCOVERED**
  - What it tests: Surface is elementary (plane, cone, sphere, cylinder)
  - Repair action: Return false, twist detection not applicable
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_ElementarySurface))'
- **Branch 2** @ line 984 — *PRECISION_UNDEFINED* — **UNCOVERED**
  - What it tests: Precision parameter not set
  - Repair action: Use default tolerance 1e-4 instead of myPrecision
  - Suggested fixture: defect mentioning 'toler < 0', 'toler = 1.e-4'
- **Branch 3** @ line 1001 — *PARAMETER_RANGE_ERROR* — COVERED by: n048
  - What it tests: V-parameter increment computed from U-range (line 1001 bug: dv uses umax-umin not vmax-vmin)
  - Repair action: Grid sampling with incorrect V-step (potential defect in code)
- **Branch 4** @ line 1012 — *NORMAL_INVERSION_CHECK* — **UNCOVERED**
  - What it tests: Computes surface normal at each grid point via cross product D1(u,v)
  - Repair action: Store normal components (nx, ny, nz) for comparison
  - Suggested fixture: defect mentioning 'D1(u, v', 'V1.Crossed(V2)'
- **Branch 5** @ line 1033 — *TWIST_V_INVERSION* — COVERED by: m189, tfa014
  - What it tests: Normal flips when moving along V-parameter (first negative dot product check)
  - Repair action: Return true with paramu, paramv at flip location, record DONE status
- **Branch 6** @ line 1040 — *TWIST_U_INVERSION* — COVERED by: m189, tfa014
  - What it tests: Normal flips when moving along U-parameter (second negative dot product check)
  - Repair action: Return true with paramu, paramv at flip location
- **Branch 7** @ line 1058 — *NO_TWIST_DETECTED* — COVERED by: in014
  - What it tests: All normals maintain consistent direction within grid
  - Repair action: Return false, surface is topologically consistent

#### `ShapeAnalysis_CheckSmallFace.CheckPin` — lines 849–958
(11 branches, 0 covered.)

- **Branch 1** @ line 870 — *null_geometry* — **UNCOVERED**
  - What it tests: Null pointer guard: bs
  - Repair action: handle missing curve/surface
  - Suggested fixture: defect mentioning 'bs.IsNull()'
- **Branch 2** @ line 875 — *null_geometry* — **UNCOVERED**
  - What it tests: Null pointer guard: bz
  - Repair action: handle missing curve/surface
  - Suggested fixture: defect mentioning 'bz.IsNull()'
- **Branch 3** @ line 880 — *pole_count* — **UNCOVERED**
  - What it tests: BSpline/Bezier poles exist
  - Repair action: skip non-polled surfaces
  - Suggested fixture: defect mentioning 'nbu', 'nbv'
- **Branch 4** @ line 886 — *null_geometry* — **UNCOVERED**
  - What it tests: Null pointer guard: bs
  - Repair action: handle missing curve/surface
  - Suggested fixture: defect mentioning 'bs.IsNull()'
- **Branch 5** @ line 890 — *null_geometry* — **UNCOVERED**
  - What it tests: Null pointer guard: bz
  - Repair action: handle missing curve/surface
  - Suggested fixture: defect mentioning 'bz.IsNull()'
- **Branch 6** @ line 901 — *pole_singularity* — **UNCOVERED**
  - What it tests: Pole row convergence (sharp pin indicator)
  - Repair action: record pin location and direction
  - Suggested fixture: defect mentioning 'IsoStat'
- **Branch 7** @ line 908 — *pole_singularity* — **UNCOVERED**
  - What it tests: Pole row convergence (sharp pin indicator)
  - Repair action: record pin location and direction
  - Suggested fixture: defect mentioning 'IsoStat'
- **Branch 8** @ line 915 — *pole_singularity* — **UNCOVERED**
  - What it tests: Pole row convergence (sharp pin indicator)
  - Repair action: record pin location and direction
  - Suggested fixture: defect mentioning 'IsoStat'
- **Branch 9** @ line 922 — *pole_singularity* — **UNCOVERED**
  - What it tests: Pole row convergence (sharp pin indicator)
  - Repair action: record pin location and direction
  - Suggested fixture: defect mentioning 'IsoStat'
- **Branch 10** @ line 936 — *singularity_classification* — **UNCOVERED**
  - What it tests: Smooth (stat=1) vs Sharp (stat=2) pin
  - Repair action: set appropriate status code
  - Suggested fixture: defect mentioning 'case 1:', 'case 2:'
- **Branch 11** @ line 939 — *singularity_classification* — **UNCOVERED**
  - What it tests: Smooth (stat=1) vs Sharp (stat=2) pin
  - Repair action: set appropriate status code
  - Suggested fixture: defect mentioning 'case 1:', 'case 2:'

#### `ShapeAnalysis_CheckSmallFace.CheckPinEdges` — lines 1208–1341
(2 branches, 2 covered.)

- **Branch 1** @ line 1310 — *geometric_distance* — COVERED by: a001, a011, a019, a032, a073, a095, a096, a097 (+500 more)
  - What it tests: Distance vs tolerance threshold
  - Repair action: classify sliver vs pin
- **Branch 2** @ line 1314 — *geometric_distance* — COVERED by: a001, a011, a019, a032, a073, a095, a096, a097 (+500 more)
  - What it tests: Distance vs tolerance threshold
  - Repair action: classify sliver vs pin

#### `ShapeAnalysis_CheckSmallFace.CheckPinFace` — lines 1069–1197
(4 branches, 2 covered.)

- **Branch 1** @ line 1130 — *pin_sharpness_threshold* — COVERED by: ad086, m038, twi058
  - What it tests: Edge ratio vs 3x threshold
  - Repair action: exclude blunt edges
- **Branch 2** @ line 1170 — *pin_sharpness_threshold* — COVERED by: ad086, m038, twi058
  - What it tests: Edge ratio vs 3x threshold
  - Repair action: exclude blunt edges
- **Branch 3** @ line 1174 — *edge_ratio_imbalance* — **UNCOVERED**
  - What it tests: Pin edge proportions (coef1 vs coef2)
  - Repair action: skip asymmetric pin pairs
  - Suggested fixture: defect mentioning 'coef1 > coef2 * 10', 'coef2 > coef1 * 10'
- **Branch 4** @ line 1178 — *edge_ratio_imbalance* — **UNCOVERED**
  - What it tests: Pin edge proportions (coef1 vs coef2)
  - Repair action: skip asymmetric pin pairs
  - Suggested fixture: defect mentioning 'coef1 > coef2 * 10', 'coef2 > coef1 * 10'

#### `ShapeAnalysis_CheckSmallFace.CheckSingleStrip` — lines 520–651
(13 branches, 1 covered.)

- **Branch 1** @ line 531 — *FIRST_VERTEX_CACHE* — **UNCOVERED**
  - What it tests: No vertex cached yet (V1 is null)
  - Repair action: Cache first vertex as V1
  - Suggested fixture: defect mentioning 'V1.IsNull()'
- **Branch 2** @ line 535 — *VERTEX_DUPLICATE_SKIP* — **UNCOVERED**
  - What it tests: Current vertex is same as cached V1
  - Repair action: Skip duplicate, continue
  - Suggested fixture: defect mentioning 'V1.IsSame(V)'
- **Branch 3** @ line 539 — *SECOND_VERTEX_CACHE* — **UNCOVERED**
  - What it tests: V1 cached but V2 not yet (V2 is null)
  - Repair action: Cache second distinct vertex as V2
  - Suggested fixture: defect mentioning 'V2.IsNull()'
- **Branch 4** @ line 543 — *SECOND_VERTEX_DUPLICATE_SKIP* — **UNCOVERED**
  - What it tests: Current vertex matches cached V2
  - Repair action: Skip duplicate, continue
  - Suggested fixture: defect mentioning 'V2.IsSame(V)'
- **Branch 5** @ line 549 — *TOO_MANY_DISTINCT_VERTICES* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Third distinct vertex found
  - Repair action: Return false (not a simple strip)
- **Branch 6** @ line 565 — *NEGATIVE_TOLERANCE_VERTEX_OVERRIDE* — **UNCOVERED**
  - What it tests: Input tolerance is negative
  - Repair action: Use max vertex tolerance
  - Suggested fixture: defect mentioning 'tol < 0'
- **Branch 7** @ line 581 — *CLOSED_EDGE_SELF_LOOP* — **UNCOVERED**
  - What it tests: Edge connects vertex to itself
  - Repair action: Validate edge as null-length small loop
  - Suggested fixture: defect mentioning 'VA.IsSame(VB)'
- **Branch 8** @ line 585 — *DEGENERATED_EDGE_CHECK* — **UNCOVERED**
  - What it tests: Edge is marked degenerated in BRep
  - Repair action: Skip curve fetch for degenerated edges
  - Suggested fixture: defect mentioning '!BRep_Tool::Degenerated(E)'
- **Branch 9** @ line 589 — *CLOSED_EDGE_NO_3D_CURVE* — **UNCOVERED**
  - What it tests: Self-loop edge has no 3D curve
  - Repair action: Skip (continue) as null-length edge
  - Suggested fixture: defect mentioning 'C3D.IsNull()'
- **Branch 10** @ line 600 — *CLOSED_EDGE_NOT_SMALL* — **UNCOVERED**
  - What it tests: Self-loop edge bounding box exceeds tolerance
  - Repair action: Return false (edge not null-length)
  - Suggested fixture: defect mentioning '!MinMaxSmall(minx, miny, minz'
- **Branch 11** @ line 609 — *TOO_MANY_MAJOR_EDGES* — **UNCOVERED**
  - What it tests: More than 2 edges between distinct vertices
  - Repair action: Return false
  - Suggested fixture: defect mentioning 'if (nb > 2)'
- **Branch 12** @ line 621 — *SECOND_EDGE_INVALID_ENDPOINT_PAIRING_V1* — **UNCOVERED**
  - What it tests: Second major edge connects V1 to non-V2 vertex
  - Repair action: Return false (topological inconsistency)
  - Suggested fixture: defect mentioning 'V1.IsSame(VA) && !V2.IsSame(VB)'
- **Branch 13** @ line 625 — *SECOND_EDGE_INVALID_ENDPOINT_PAIRING_V2* — **UNCOVERED**
  - What it tests: Second major edge connects V1-reversed to non-V2 vertex
  - Repair action: Return false (topological inconsistency)
  - Suggested fixture: defect mentioning 'V1.IsSame(VB) && !V2.IsSame(VA)'

#### `ShapeAnalysis_CheckSmallFace.CheckSplittingVertices` — lines 687–791
(6 branches, 2 covered.)

- **Branch 1** @ line 700 — *pole_count* — **UNCOVERED**
  - What it tests: BSpline/Bezier poles exist
  - Repair action: skip non-polled surfaces
  - Suggested fixture: defect mentioning 'nbu', 'nbv'
- **Branch 2** @ line 741 — *null_geometry* — **UNCOVERED**
  - What it tests: Null pointer guard: ?
  - Repair action: handle missing curve/surface
  - Suggested fixture: defect mentioning '?.IsNull()'
- **Branch 3** @ line 745 — *endpoint_exclusion* — **UNCOVERED**
  - What it tests: Skip edge endpoints (non-split vertices)
  - Repair action: exclude trivial edge incidences
  - Suggested fixture: defect mentioning 'V.IsSame(V1)', 'V.IsSame(V2)'
- **Branch 4** @ line 754 — *geometric_distance* — COVERED by: a001, a011, a019, a032, a073, a095, a096, a097 (+500 more)
  - What it tests: Distance vs tolerance threshold
  - Repair action: classify sliver vs pin
- **Branch 5** @ line 759 — *geometric_distance* — COVERED by: a001, a011, a019, a032, a073, a095, a096, a097 (+500 more)
  - What it tests: Distance vs tolerance threshold
  - Repair action: classify sliver vs pin
- **Branch 6** @ line 769 — *edge_split_proximity* — **UNCOVERED**
  - What it tests: Interior point vs near-endpoint
  - Repair action: exclude pseudo-splits
  - Suggested fixture: defect mentioning 'eps = 1.e-06', 'std::abs(fpar)'

#### `ShapeAnalysis_CheckSmallFace.CheckSpotFace` — lines 235–255
(4 branches, 0 covered.)

- **Branch 1** @ line 238 — *SPOT_FACE_DETECTION_FAILED* — **UNCOVERED**
  - What it tests: IsSpotFace returns 0 (not a spot)
  - Repair action: Return false (no spot defect found)
  - Suggested fixture: defect mentioning 'stat = IsSpotFace(F, spot'
- **Branch 2** @ line 239 — *STAT_ZERO_BRANCH* — **UNCOVERED**
  - What it tests: IsSpotFace status is 0
  - Repair action: Return false early
  - Suggested fixture: defect mentioning '!stat'
- **Branch 3** @ line 245 — *SPOT_TYPE_ONE_VERTICES_DIFFER* — **UNCOVERED**
  - What it tests: IsSpotFace status is 1 (vertices differ)
  - Repair action: Encode ShapeExtend_DONE1 status
  - Suggested fixture: defect mentioning 'case 1:'
- **Branch 4** @ line 248 — *SPOT_TYPE_TWO_VERTICES_IDENTICAL* — **UNCOVERED**
  - What it tests: IsSpotFace status is 2 (vertices identical)
  - Repair action: Encode ShapeExtend_DONE2 status
  - Suggested fixture: defect mentioning 'case 2:'

#### `ShapeAnalysis_CheckSmallFace.CheckStripEdges` — lines 351–433
(8 branches, 0 covered.)

- **Branch 1** @ line 355 — *NEGATIVE_TOLERANCE_COMPUTE_FROM_EDGES* — **UNCOVERED**
  - What it tests: Input tolerance is negative
  - Repair action: Compute from edge tolerances
  - Suggested fixture: defect mentioning 'tol < 0'
- **Branch 2** @ line 358 — *EDGE_TOLERANCE_EXCEEDS_COMPUTED* — **UNCOVERED**
  - What it tests: Half sum of edge tolerances exceeds computed tolerance
  - Repair action: Update toler to edge tolerance average
  - Suggested fixture: defect mentioning 'toler < tole / 2.'
- **Branch 3** @ line 374 — *EDGE_MISSING_3D_CURVE* — **UNCOVERED**
  - What it tests: Either E1 or E2 has null 3D curve
  - Repair action: Return false
  - Suggested fixture: defect mentioning 'C1.IsNull() || C2.IsNull()'
- **Branch 4** @ line 399 — *DUAL_CURVE_PROJECTION_LOOP* — **UNCOVERED**
  - What it tests: Iterate twice: first E1->E2, then E2->E1
  - Repair action: Swap curves and bounds for second iteration
  - Suggested fixture: defect mentioning 'numcur = 0; numcur < 2'
- **Branch 5** @ line 417 — *PROJECTION_PARAMETER_OUT_OF_BOUNDS* — **UNCOVERED**
  - What it tests: Projected point parameter outside target edge domain
  - Repair action: Return false (edges not parallel)
  - Suggested fixture: defect mentioning 'para < f || para > l'
- **Branch 6** @ line 421 — *PROJECTION_DISTANCE_TRACKING* — **UNCOVERED**
  - What it tests: Track maximum projection distance across samples
  - Repair action: Update dmax if dist exceeds current max
  - Suggested fixture: defect mentioning 'if (dist > dmax)'
- **Branch 7** @ line 425 — *PROJECTION_DISTANCE_EXCEEDS_TOLERANCE* — **UNCOVERED**
  - What it tests: Single point projection distance exceeds tolerance
  - Repair action: Return false (edges too far apart)
  - Suggested fixture: defect mentioning 'dist > toler'
- **Branch 8** @ line 432 — *FINAL_DISTANCE_CHECK* — **UNCOVERED**
  - What it tests: Final dmax must be strictly less than tolerance
  - Repair action: Return true if dmax < toler, false otherwise
  - Suggested fixture: defect mentioning 'return (dmax < toler)'

#### `ShapeAnalysis_CheckSmallFace.FindStripEdges` — lines 442–512
(9 branches, 1 covered.)

- **Branch 1** @ line 449 — *SEAM_EDGE_SKIP* — **UNCOVERED**
  - What it tests: Current edge matches cached E1 (seam edge after first pass)
  - Repair action: Skip seam edge, continue to next
  - Suggested fixture: defect mentioning 'nb == 1 && E.IsSame(E1)'
- **Branch 2** @ line 459 — *TOLERANCE_AUTO_COMPUTE_FROM_VERTICES* — **UNCOVERED**
  - What it tests: Input tolerance is non-positive
  - Repair action: Compute from edge endpoint vertex tolerances
  - Suggested fixture: defect mentioning 'toler <= 0'
- **Branch 3** @ line 474 — *EDGE_MIDPOINT_NULL_LENGTH_TEST* — **UNCOVERED**
  - What it tests: Edge midpoint and both endpoints are within tolerance
  - Repair action: Mark edge as null-length, skip (continue)
  - Suggested fixture: defect mentioning 'pp.Distance(p1) < toler && pp.Distance(p2) < toler'
- **Branch 4** @ line 480 — *ENDPOINT_DISTANCE_VS_NULL_LENGTH* — **UNCOVERED**
  - What it tests: Endpoint distance within tolerance AND no 3D curve
  - Repair action: Skip edge (null length edge)
  - Suggested fixture: defect mentioning 'dist <= toler && isNullLength'
- **Branch 5** @ line 485 — *FIRST_SIGNIFICANT_EDGE_FOUND* — **UNCOVERED**
  - What it tests: Edge count becomes 1
  - Repair action: Store as E1
  - Suggested fixture: defect mentioning 'if (nb == 1)'
- **Branch 6** @ line 489 — *SECOND_SIGNIFICANT_EDGE_FOUND* — **UNCOVERED**
  - What it tests: Edge count becomes 2
  - Repair action: Store as E2
  - Suggested fixture: defect mentioning 'else if (nb == 2)'
- **Branch 7** @ line 493 — *TOO_MANY_SIGNIFICANT_EDGES* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Edge count exceeds 2
  - Repair action: Return false (not a strip)
- **Branch 8** @ line 499 — *BOTH_EDGES_FOUND_VALIDATION* — **UNCOVERED**
  - What it tests: Both E1 and E2 are non-null
  - Repair action: Validate edges with CheckStripEdges
  - Suggested fixture: defect mentioning '!E1.IsNull() && !E2.IsNull()'
- **Branch 9** @ line 638 — *INSUFFICIENT_EDGES_AFTER_SCAN* — **UNCOVERED**
  - What it tests: Fewer than 2 significant edges found
  - Repair action: Return false (not a strip)
  - Suggested fixture: defect mentioning 'if (nb < 2)'

#### `ShapeAnalysis_CheckSmallFace.IsSpotFace` — lines 136–230
(10 branches, 0 covered.)

- **Branch 1** @ line 148 — *INVALID_WIRE_TYPE* — **UNCOVERED**
  - What it tests: Wire iterator shape is not TopAbs_WIRE type
  - Repair action: Skip non-wire shapes during face wire scan
  - Suggested fixture: defect mentioning 'itw.Value().ShapeType() != TopAbs_WIRE'
- **Branch 2** @ line 159 — *NO_WIRES_ON_FACE* — **UNCOVERED**
  - What it tests: Face contains no valid wires
  - Repair action: Return true (spot face) when no wires found
  - Suggested fixture: defect mentioning '!isWir'
- **Branch 3** @ line 171 — *FIRST_VERTEX_INIT* — **UNCOVERED**
  - What it tests: First vertex in face is null/uninitialized
  - Repair action: Cache first vertex as reference point
  - Suggested fixture: defect mentioning 'V0.IsNull()'
- **Branch 4** @ line 177 — *MULTIPLE_DISTINCT_VERTICES* — **UNCOVERED**
  - What it tests: Found different vertex from cached V0
  - Repair action: Mark face as having non-identical vertices
  - Suggested fixture: defect mentioning '!V0.IsSame(V)'
- **Branch 5** @ line 187 — *NEGATIVE_TOLERANCE_OVERRIDE* — **UNCOVERED**
  - What it tests: User provides negative tolerance (compute from vertices)
  - Repair action: Extract max vertex tolerance and use it
  - Suggested fixture: defect mentioning 'tol < 0'
- **Branch 6** @ line 190 — *VERTEX_TOLERANCE_EXCEEDS_FACE_TOLERANCE* — **UNCOVERED**
  - What it tests: Vertex tolerance exceeds current tolerance accumulator
  - Repair action: Update face tolerance to vertex tolerance
  - Suggested fixture: defect mentioning 'tolv > toler'
- **Branch 7** @ line 198 — *BOUNDING_BOX_NOT_SMALL* — **UNCOVERED**
  - What it tests: Vertex min/max box is larger than tolerance
  - Repair action: Return 0 (not a spot face)
  - Suggested fixture: defect mentioning '!MinMaxSmall(minx, miny, minz'
- **Branch 8** @ line 211 — *EDGE_HAS_NO_3D_CURVE* — **UNCOVERED**
  - What it tests: Edge has no 3D curve representation
  - Repair action: Skip edge in endpoint/midpoint verification
  - Suggested fixture: defect mentioning 'C3D.IsNull()'
- **Branch 9** @ line 217 — *EDGE_MIDPOINT_DEVIATES_FROM_ENDPOINT* — **UNCOVERED**
  - What it tests: Edge midpoint distance from start point exceeds tolerance
  - Repair action: Return 0 (edge non-trivial, not a spot face)
  - Suggested fixture: defect mentioning 'debut.SquareDistance(milieu) > toler'
- **Branch 10** @ line 229 — *RETURN_SPOT_TYPE_CODE* — **UNCOVERED**
  - What it tests: All tests pass; face is a spot; return same/multi-vertex variant
  - Repair action: Return 2 if all vertices identical, 1 if vertices differ
  - Suggested fixture: defect mentioning 'return (same ? 2 : 1)'

#### `ShapeAnalysis_CheckSmallFace.IsStripSupport` — lines 260–343
(8 branches, 0 covered.)

- **Branch 1** @ line 263 — *NEGATIVE_TOLERANCE_DEFAULT* — **UNCOVERED**
  - What it tests: Input tolerance is negative (auto-compute)
  - Repair action: Use hardcoded 1e-7 tolerance
  - Suggested fixture: defect mentioning 'toler < 0'
- **Branch 2** @ line 270 — *FACE_SURFACE_IS_NULL* — **UNCOVERED**
  - What it tests: Face has no underlying surface
  - Repair action: Return false
  - Suggested fixture: defect mentioning 'surf.IsNull()'
- **Branch 3** @ line 278 — *SURFACE_TYPE_NOT_BSPLINE_BEZIER* — **UNCOVERED**
  - What it tests: Surface is neither BSpline nor Bezier
  - Repair action: Skip pole-based analysis, return false
  - Suggested fixture: defect mentioning 'bs.IsNull() || !bz.IsNull()'
- **Branch 4** @ line 284 — *BEZIER_VS_BSPLINE_DETECTION* — **UNCOVERED**
  - What it tests: Determine if surface is Bezier (vs BSpline)
  - Repair action: Set cbz flag and choose pole-extraction logic
  - Suggested fixture: defect mentioning 'cbz = (!bz.IsNull())'
- **Branch 5** @ line 308 — *POLES_NOT_SMALL_IN_V_DIRECTION* — **UNCOVERED**
  - What it tests: For fixed U, poles in V direction exceed tolerance spread
  - Repair action: Set issmall=false, break U-loop
  - Suggested fixture: defect mentioning '!MinMaxSmall(minx, miny, minz', '// small in V ?'
- **Branch 6** @ line 314 — *STRIP_SMALL_IN_V_CONFIRMED* — **UNCOVERED**
  - What it tests: All U lines have V poles within tolerance
  - Repair action: Encode DONE2, return true (small in V direction)
  - Suggested fixture: defect mentioning 'if (issmall)', 'myStatusStrip = ShapeExtend::EncodeStatus(ShapeExtend_DONE2)'
- **Branch 7** @ line 329 — *POLES_NOT_SMALL_IN_U_DIRECTION* — **UNCOVERED**
  - What it tests: For fixed V, poles in U direction exceed tolerance spread
  - Repair action: Set issmall=false, break V-loop
  - Suggested fixture: defect mentioning '!MinMaxSmall(minx, miny, minz', '// small in U ?'
- **Branch 8** @ line 335 — *STRIP_SMALL_IN_U_CONFIRMED* — **UNCOVERED**
  - What it tests: All V lines have U poles within tolerance
  - Repair action: Encode DONE1, return true (small in U direction)
  - Suggested fixture: defect mentioning 'if (issmall)', 'myStatusStrip = ShapeExtend::EncodeStatus(ShapeExtend_DONE1)'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_Curve.cxx`

11 methods, 104 branches, 5 covered.

#### `ShapeAnalysis_Curve.FillBndBox` — lines 794–848
(7 branches, 0 covered.)

- **Branch 1** @ line 795 — *bounding_box_exact_mode* — **UNCOVERED**
  - What it tests: Exact=false (fast approximation mode)
  - Repair action: Use simple uniform sampling without extrema search
  - Suggested fixture: defect mentioning '!Exact'
- **Branch 2** @ line 797 — *segment_count_edge_case* — **UNCOVERED**
  - What it tests: NPoints < 2 (degenerate point count)
  - Repair action: Set nseg=1 for single interval
  - Suggested fixture: defect mentioning 'NPoints < 2'
- **Branch 3** @ line 810 — *continuity_interval_detection* — **UNCOVERED**
  - What it tests: C2 continuity intervals on adapted curve
  - Repair action: Extract interval boundaries for adaptive sampling
  - Suggested fixture: defect mentioning 'NbIntervals(GeomAbs_C2)'
- **Branch 4** @ line 812 — *single_vs_multi_interval_strategy* — **UNCOVERED**
  - What it tests: nbInt < 2 (single C2 interval)
  - Repair action: Use NPoints-1 samples instead of knot intervals
  - Suggested fixture: defect mentioning 'nbInt < 2'
- **Branch 5** @ line 814 — *interval_extraction_mode* — **UNCOVERED**
  - What it tests: Multi-interval case (nbSamples == nbInt)
  - Repair action: Call Intervals() to get knot/discontinuity points
  - Suggested fixture: defect mentioning 'nbSamples == nbInt', 'anAC.Intervals'
- **Branch 6** @ line 831 — *extrema_search_x_direction* — **UNCOVERED**
  - What it tests: SearchForExtremum in X direction (vec=(1,0))
  - Repair action: Add extremal point to box if found within interval
  - Suggested fixture: defect mentioning 'gp_Vec2d(1, 0)'
- **Branch 7** @ line 842 — *extrema_search_y_direction* — **UNCOVERED**
  - What it tests: SearchForExtremum in Y direction (vec=(0,1))
  - Repair action: Add extremal point to box if found within interval
  - Suggested fixture: defect mentioning 'gp_Vec2d(0, 1)'

#### `ShapeAnalysis_Curve.GetSamplePoints` — lines 1262–1313
(10 branches, 0 covered.)

- **Branch 1** @ line 1263 — *degenerate_curve_parameter_span* — **UNCOVERED**
  - What it tests: adelta = LastParameter - FirstParameter
  - Repair action: Return false if adelta == 0 (degenerate curve)
  - Suggested fixture: defect mentioning '!adelta'
- **Branch 2** @ line 1269 — *sampling_density_multiplier* — **UNCOVERED**
  - What it tests: aK = ceil((last-first)/adelta) for wrapping count
  - Repair action: Use aK to scale default point counts for wrapped curves
  - Suggested fixture: defect mentioning '(last - first) / adelta'
- **Branch 3** @ line 1271 — *line_curve_minimal_sampling* — **UNCOVERED**
  - What it tests: curve is Geom_Line
  - Repair action: Use nbp=2 (only start/end endpoints needed)
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_Line))', 'nbp = 2'
- **Branch 4** @ line 1275 — *circle_curve_high_sampling* — **UNCOVERED**
  - What it tests: curve is Geom_Circle
  - Repair action: Use nbp=360*aK (angular density for smooth circle sampling)
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_Circle))', '360 * aK'
- **Branch 5** @ line 1279 — *bspline_adaptive_sampling* — **UNCOVERED**
  - What it tests: curve is Geom_BSplineCurve
  - Repair action: Set nbp = NbKnots * Degree * aK (knot-based adaptive)
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_BSplineCurve))', 'NbKnots() * Degree'
- **Branch 6** @ line 1284 — *bspline_minimum_sample_guard* — **UNCOVERED**
  - What it tests: nbp < 2 after bspline calculation
  - Repair action: Set nbp=2 (at least endpoints)
  - Suggested fixture: defect mentioning 'nbp < 2.0'
- **Branch 7** @ line 1289 — *bezier_curve_degree_based* — **UNCOVERED**
  - What it tests: curve is Geom_BezierCurve
  - Repair action: Use nbp = 3 + NbPoles (degree-aware sampling)
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_BezierCurve))', '3 + aB->NbPoles()'
- **Branch 8** @ line 1294 — *offset_curve_delegation* — **UNCOVERED**
  - What it tests: curve is Geom_OffsetCurve
  - Repair action: Recursively call GetSamplePoints on BasisCurve
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_OffsetCurve))', 'BasisCurve()'
- **Branch 9** @ line 1299 — *trimmed_curve_delegation* — **UNCOVERED**
  - What it tests: curve is Geom_TrimmedCurve
  - Repair action: Recursively call GetSamplePoints on BasisCurve
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_TrimmedCurve))'
- **Branch 10** @ line 1306 — *uniform_sampling_step* — **UNCOVERED**
  - What it tests: Compute uniform parameter step across [first, last]
  - Repair action: Generate nbp-1 interior points + last endpoint
  - Suggested fixture: defect mentioning 'step = (last - first) / (nbp - 1)'

#### `ShapeAnalysis_Curve.IsPlanar` — lines 1175–1254
(12 branches, 1 covered.)

- **Branch 1** @ line 1179 — *precision_parameter_default* — **UNCOVERED**
  - What it tests: preci > 0.0 (custom precision supplied)
  - Repair action: Use supplied preci; else use Precision::Confusion()
  - Suggested fixture: defect mentioning 'preci > 0.0'
- **Branch 2** @ line 1180 — *normal_vector_initialization* — **UNCOVERED**
  - What it tests: Normal has zero magnitude (not pre-supplied)
  - Repair action: Compute normal from curve properties
  - Suggested fixture: defect mentioning 'Normal.SquareModulus() == 0'
- **Branch 3** @ line 1182 — *line_curve_type* — **UNCOVERED**
  - What it tests: curve is Geom_Line
  - Repair action: Extract direction N1; if noNorm set to perpendicular; else validate alignment
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_Line))'
- **Branch 4** @ line 1195 — *conic_curve_type* — **UNCOVERED**
  - What it tests: curve is Geom_Conic (circle, ellipse, etc.)
  - Repair action: Extract axis normal N1; if noNorm set Normal=N1; else validate coplanarity
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_Conic))'
- **Branch 5** @ line 1205 — *conic_axis_alignment* — **UNCOVERED**
  - What it tests: Cross product of N1 and Normal has near-zero magnitude
  - Repair action: Return true if vectors are parallel/antiparallel
  - Suggested fixture: defect mentioning 'aVecMul.SquareModulus() < Precision::SquareConfusion()'
- **Branch 6** @ line 1209 — *trimmed_curve_unwrapping* — **UNCOVERED**
  - What it tests: curve is Geom_TrimmedCurve
  - Repair action: Recursively call IsPlanar on basis curve
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_TrimmedCurve))', 'BasisCurve()'
- **Branch 7** @ line 1216 — *offset_curve_unwrapping* — **UNCOVERED**
  - What it tests: curve is Geom_OffsetCurve
  - Repair action: Recursively call IsPlanar on basis curve
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_OffsetCurve))'
- **Branch 8** @ line 1223 — *bspline_curve_control_points* — **UNCOVERED**
  - What it tests: curve is Geom_BSplineCurve
  - Repair action: Delegate to IsPlanar(Poles, Normal, precision)
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_BSplineCurve))', 'Poles()'
- **Branch 9** @ line 1229 — *bezier_curve_control_points* — **UNCOVERED**
  - What it tests: curve is Geom_BezierCurve
  - Repair action: Delegate to IsPlanar(Poles, Normal, precision)
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_BezierCurve))'
- **Branch 10** @ line 1235 — *complex_composite_curve* — **UNCOVERED**
  - What it tests: curve is ShapeExtend_ComplexCurve (piecewise composition)
  - Repair action: Collect control poles from all sub-curves; validate planarity of aggregate
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(ShapeExtend_ComplexCurve))', 'NbCurves()'
- **Branch 11** @ line 1241 — *complex_curve_pole_aggregation* — **UNCOVERED**
  - What it tests: Iterate over all sub-curves in complex curve
  - Repair action: Append control poles from each sub-curve
  - Suggested fixture: defect mentioning 'AppendControlPoles', 'Complex->Curve(i)'
- **Branch 12** @ line 1253 — *unsupported_curve_type* — COVERED by: in014
  - What it tests: None of recognized curve types match
  - Repair action: Return false (cannot determine planarity)

#### `ShapeAnalysis_Curve.NextProject[1/2]` — lines 513–557
(5 branches, 0 covered.)

- **Branch 1** @ line 514 — *parameter-range-normalization* — **UNCOVERED**
  - What it tests: detect reversed curve bounds and normalize uMin/uMax
  - Repair action: set uMin = min(cf, cl), uMax = max(cf, cl)
  - Suggested fixture: defect mentioning 'uMin = (cf < cl ? cf : cl)'
- **Branch 2** @ line 518 — *bounded-curve-endpoint-snap* — **UNCOVERED**
  - What it tests: whether curve is bounded (Geom_BoundedCurve subclass)
  - Repair action: check distance to endpoints, snap if within tolerance
  - Suggested fixture: defect mentioning 'if (C3D->IsKind(STANDARD_TYPE(Geom_BoundedCurve))'
- **Branch 3** @ line 526 — *endpoint-proximity-early-exit* — **UNCOVERED**
  - What it tests: whether point is within prec distance of lower bound
  - Repair action: return lower bound endpoint distance immediately
  - Suggested fixture: defect mentioning 'if (distmin <= prec)'
- **Branch 4** @ line 533 — *endpoint-proximity-early-exit* — **UNCOVERED**
  - What it tests: whether point is within prec distance of upper bound
  - Repair action: return upper bound endpoint distance immediately
  - Suggested fixture: defect mentioning 'if (distmin <= prec)'
- **Branch 5** @ line 541 — *curve-closure-check* — **UNCOVERED**
  - What it tests: whether curve is NOT topologically closed
  - Repair action: expand parameter range by delta = min(Resolution, 0.1*(uMax-uMin))
  - Suggested fixture: defect mentioning 'if (!C3D->IsClosed())'

#### `ShapeAnalysis_Curve.NextProject[2/2]` — lines 567–579
(2 branches, 0 covered.)

- **Branch 1** @ line 571 — *newton-iteration-from-previous-param* — **UNCOVERED**
  - What it tests: whether Extrema_LocateExtPC succeeds from paramPrev seed
  - Repair action: use Newton iteration starting from paramPrev; extract parameter and point
  - Suggested fixture: defect mentioning 'Extrema_LocateExtPC aProjector(P3D, C3D, paramPrev'
- **Branch 2** @ line 572 — *newton-convergence-check* — **UNCOVERED**
  - What it tests: whether Newton iteration converged (IsDone)
  - Repair action: return Newton result if IsDone(), else fallback to Project
  - Suggested fixture: defect mentioning 'if (aProjector.IsDone())'

#### `ShapeAnalysis_Curve.ProjectAct` — lines 271–497
(25 branches, 0 covered.)

- **Branch 1** @ line 277 — *extrema-computation-exception-guard* — **UNCOVERED**
  - What it tests: whether Extrema_ExtPC completes successfully without crash
  - Repair action: catch Standard_Failure, set OK=false on exception
  - Suggested fixture: defect mentioning 'try { ... OCC_CATCH_SIGNALS ... catch (const Standard_Failure&)'
- **Branch 2** @ line 280 — *extrema-result-validation* — **UNCOVERED**
  - What it tests: whether Extrema_ExtPC produced at least one solution
  - Repair action: skip if no extrema points found, fallback to curve-type dispatch
  - Suggested fixture: defect mentioning 'if (aCurveExtrema.IsDone() && (aCurveExtrema.NbExt() > 0))'
- **Branch 3** @ line 284 — *extrema-minimum-filtering* — **UNCOVERED**
  - What it tests: whether current extrema point is a minimum (not maximum)
  - Repair action: skip non-minimum extrema points in loop
  - Suggested fixture: defect mentioning 'if (!aCurveExtrema.IsMin(i))'
- **Branch 4** @ line 290 — *extrema-best-selection* — **UNCOVERED**
  - What it tests: whether current extrema is better (smaller) than previous best
  - Repair action: update aMinExtremaDistance and aMinExtremaIndex if current is better
  - Suggested fixture: defect mentioning 'if (aCurrentDistance < aMinExtremaDistance)'
- **Branch 5** @ line 297 — *extrema-result-extraction* — **UNCOVERED**
  - What it tests: whether a valid minimum extrema point was found
  - Repair action: extract parameter and value from best extrema point, set OK=true
  - Suggested fixture: defect mentioning 'if (aMinExtremaIndex != 0)'
- **Branch 6** @ line 329 — *old-solution-memo-check* — **UNCOVERED**
  - What it tests: whether Extrema previously succeeded and distance < tolerance
  - Repair action: save old solution for fallback comparison; check if curve is closed
  - Suggested fixture: defect mentioning 'if (OK)'
- **Branch 7** @ line 340 — *closed-curve-periodicity-detection* — **UNCOVERED**
  - What it tests: whether curve is topologically closed (periodic)
  - Repair action: set anIsClosedCurve=true, compute period = uMax - uMin
  - Suggested fixture: defect mentioning 'if (theCurve.IsClosed())'
- **Branch 8** @ line 347 — *extrema-failure-fallback-dispatch* — **UNCOVERED**
  - What it tests: whether Extrema_ExtPC failed or tolerance check failed
  - Repair action: dispatch on curve type (Circle, Hyperbola, Parabola, Line, Ellipse) or fallback to ProjectOnSegments
  - Suggested fixture: defect mentioning 'if (!OK)'
- **Branch 9** @ line 357 — *circle-projection-dispatch* — **UNCOVERED**
  - What it tests: whether curve is a circle (GeomAbs_Circle)
  - Repair action: use aCirc.Position().Location() as center; handle zero-radius; use ElCLib::Parameter
  - Suggested fixture: defect mentioning 'case GeomAbs_Circle:'
- **Branch 10** @ line 360 — *degenerate-circle-fallback* — **UNCOVERED**
  - What it tests: whether circle radius is zero or point is at center
  - Repair action: snap to first parameter + radius offset on X-axis
  - Suggested fixture: defect mentioning 'if (aCirc.Radius() <= gp::Resolution()'
- **Branch 11** @ line 376 — *hyperbola-projection-dispatch* — **UNCOVERED**
  - What it tests: whether curve is a hyperbola (GeomAbs_Hyperbola)
  - Repair action: use ElCLib::Parameter(hyperbola, point) for parameter
  - Suggested fixture: defect mentioning 'case GeomAbs_Hyperbola:'
- **Branch 12** @ line 382 — *parabola-projection-dispatch* — **UNCOVERED**
  - What it tests: whether curve is a parabola (GeomAbs_Parabola)
  - Repair action: use ElCLib::Parameter(parabola, point) for parameter
  - Suggested fixture: defect mentioning 'case GeomAbs_Parabola:'
- **Branch 13** @ line 388 — *line-projection-dispatch* — **UNCOVERED**
  - What it tests: whether curve is a line (GeomAbs_Line)
  - Repair action: use ElCLib::Parameter(line, point) for parameter
  - Suggested fixture: defect mentioning 'case GeomAbs_Line:'
- **Branch 14** @ line 394 — *ellipse-projection-dispatch* — **UNCOVERED**
  - What it tests: whether curve is an ellipse (GeomAbs_Ellipse)
  - Repair action: use ElCLib::Parameter(ellipse, point); set periodic (period=2*pi)
  - Suggested fixture: defect mentioning 'case GeomAbs_Ellipse:'
- **Branch 15** @ line 402 — *bspline-fallback-sampling* — **UNCOVERED**
  - What it tests: whether curve is not a standard conic (BSpline, Bezier, etc.)
  - Repair action: use iterative ProjectOnSegments with segment counts [25, 40, 20, 25, 40]
  - Suggested fixture: defect mentioning 'default:', 'ProjectOnSegments'
- **Branch 16** @ line 408 — *initial-grid-sampling* — **UNCOVERED**
  - What it tests: initial ProjectOnSegments(25 segments) result quality
  - Repair action: sample curve at 25 points, find closest; return if <= tolerance
  - Suggested fixture: defect mentioning 'ProjectOnSegments(theCurve, thePoint, 25,'
- **Branch 17** @ line 421 — *newton-refinement-attempt* — **UNCOVERED**
  - What it tests: whether Extrema_LocateExtPC refines initial projection successfully
  - Repair action: use Newton iteration from current theProjParam; compare with aModMin
  - Suggested fixture: defect mentioning 'Extrema_LocateExtPC aProjector'
- **Branch 18** @ line 427 — *newton-convergence-check* — **UNCOVERED**
  - What it tests: whether Newton iteration converged (IsDone)
  - Repair action: extract refined parameter and point; compare distance with aModMin
  - Suggested fixture: defect mentioning 'if (aProjector.IsDone())'
- **Branch 19** @ line 432 — *newton-improvement-validation* — **UNCOVERED**
  - What it tests: whether Newton result is better than best previous distance
  - Repair action: return Newton result if it improves aModMin
  - Suggested fixture: defect mentioning 'if (aDistNewton < aModMin)'
- **Branch 20** @ line 449 — *iterative-refinement-segments* — **UNCOVERED**
  - What it tests: successive ProjectOnSegments iterations with segment counts [40, 20, 25, 40]
  - Repair action: narrow parameter range each iteration; return if distance <= tolerance
  - Suggested fixture: defect mentioning 'for (const int aSegmentCount : {40, 20, 25, 40})'
- **Branch 21** @ line 459 — *convergence-exit-criterion* — **UNCOVERED**
  - What it tests: whether iterative sampling found projection within tolerance
  - Repair action: return aProjDistance if <= tolerance, else continue narrowing range
  - Suggested fixture: defect mentioning 'if (aProjDistance <= theTolerance)'
- **Branch 22** @ line 468 — *fallback-selection-final* — **UNCOVERED**
  - What it tests: whether iterative sampling produced worse result than Extrema
  - Repair action: revert to original aComputedParam/aComputedProj if sampling degraded
  - Suggested fixture: defect mentioning 'if (aProjDistance > aModMin)'
- **Branch 23** @ line 480 — *closed-curve-parameter-wrapping* — **UNCOVERED**
  - What it tests: whether parameter is outside bounds on a periodic curve
  - Repair action: adjust parameter by period using AdjustByPeriod to wrap into [uMin, uMax]
  - Suggested fixture: defect mentioning 'if (anIsClosedCurve && (theProjParam < uMin || theProjParam > uMax))'
- **Branch 24** @ line 485 — *solution-comparison-fallback* — **UNCOVERED**
  - What it tests: whether saved old Extrema solution is better than final result
  - Repair action: restore old solution if its square distance is less than new result
  - Suggested fixture: defect mentioning 'if (anIsHaveOldSolution)'
- **Branch 25** @ line 490 — *multi-solution-selection* — **UNCOVERED**
  - What it tests: which solution (old vs. new) has smaller square distance
  - Repair action: compare anOldDist < aNewDist and keep better one
  - Suggested fixture: defect mentioning 'if (anOldDist < aNewDist)'

#### `ShapeAnalysis_Curve.Project[1/3]` — lines 132–143
(1 branches, 0 covered.)

- **Branch 1** @ line 135 — *parameter-range-guard* — **UNCOVERED**
  - What it tests: whether curve first param < last param (normal orientation)
  - Repair action: Project with (cf, cl) if normal, else (cl, cf) if reversed
  - Suggested fixture: defect mentioning 'if (uMin < uMax)'

#### `ShapeAnalysis_Curve.Project[2/3]` — lines 155–201
(5 branches, 0 covered.)

- **Branch 1** @ line 157 — *parameter-range-normalization* — **UNCOVERED**
  - What it tests: detect reversed curve bounds and normalize uMin/uMax
  - Repair action: set uMin = min(cf, cl), uMax = max(cf, cl)
  - Suggested fixture: defect mentioning 'uMin = (cf < cl ? cf : cl)'
- **Branch 2** @ line 161 — *bounded-curve-endpoint-snap* — **UNCOVERED**
  - What it tests: whether curve is bounded (Geom_BoundedCurve subclass)
  - Repair action: check distance to endpoints, snap if within tolerance
  - Suggested fixture: defect mentioning 'C3D->IsKind(STANDARD_TYPE(Geom_BoundedCurve))'
- **Branch 3** @ line 169 — *endpoint-proximity-early-exit* — **UNCOVERED**
  - What it tests: whether point is within prec distance of lower bound
  - Repair action: return lower bound endpoint distance immediately
  - Suggested fixture: defect mentioning 'if (distmin <= prec)'
- **Branch 4** @ line 176 — *endpoint-proximity-early-exit* — **UNCOVERED**
  - What it tests: whether point is within prec distance of upper bound
  - Repair action: return upper bound endpoint distance immediately
  - Suggested fixture: defect mentioning 'if (distmin <= prec)'
- **Branch 5** @ line 184 — *curve-closure-check* — **UNCOVERED**
  - What it tests: whether curve is NOT topologically closed
  - Repair action: expand parameter range by delta = min(Resolution, 0.1*(uMax-uMin))
  - Suggested fixture: defect mentioning 'if (!C3D->IsClosed())'

#### `ShapeAnalysis_Curve.Project[3/3]` — lines 212–261
(5 branches, 0 covered.)

- **Branch 1** @ line 217 — *infinite-bounds-fallback* — **UNCOVERED**
  - What it tests: whether both parameter bounds are infinite
  - Repair action: skip endpoint checks, use ProjectAct directly on infinite curve
  - Suggested fixture: defect mentioning 'if (Precision::IsInfinite(uMin) && Precision::IsInfinite(uMax))'
- **Branch 2** @ line 231 — *endpoint-proximity-early-exit* — **UNCOVERED**
  - What it tests: whether point is within prec distance of lower bound
  - Repair action: return lower bound distance, skip interior projection
  - Suggested fixture: defect mentioning 'if (distmin_L <= prec)'
- **Branch 3** @ line 238 — *endpoint-proximity-early-exit* — **UNCOVERED**
  - What it tests: whether point is within prec distance of upper bound
  - Repair action: return upper bound distance, skip interior projection
  - Suggested fixture: defect mentioning 'if (distmin_H <= prec)'
- **Branch 4** @ line 246 — *interior-projection-validation* — **UNCOVERED**
  - What it tests: whether ProjectAct result is significantly better than endpoints
  - Repair action: return interior projection if within epsilon of endpoints or better
  - Suggested fixture: defect mentioning 'if (distProj < distmin_L + Precision::Confusion()'
- **Branch 5** @ line 252 — *endpoint-selection-comparison* — **UNCOVERED**
  - What it tests: which endpoint (lower or upper) is closer to projection point
  - Repair action: return lower endpoint if distmin_L < distmin_H, else upper
  - Suggested fixture: defect mentioning 'if (distmin_L < distmin_H)'

#### `ShapeAnalysis_Curve.SelectForwardSeam` — lines 854–970
(14 branches, 0 covered.)

- **Branch 1** @ line 860 — *curve_type_cast_to_line* — **UNCOVERED**
  - What it tests: C1 is a Geom2d_Line
  - Repair action: Use line directly
  - Suggested fixture: defect mentioning 'down_cast<Geom2d_Line>(C1)', 'L1.IsNull()'
- **Branch 2** @ line 864 — *curve_type_fallback_bounded* — **UNCOVERED**
  - What it tests: C1 is a BoundedCurve (not a Line)
  - Repair action: Create synthetic line from start->end vector
  - Suggested fixture: defect mentioning 'down_cast<Geom2d_BoundedCurve>(C1)'
- **Branch 3** @ line 872 — *degenerate_bounded_curve* — **UNCOVERED**
  - What it tests: BoundedCurve C1 with degenerate endpoint vector
  - Repair action: Return 0 (invalid seam selection)
  - Suggested fixture: defect mentioning 'SquareMagnitude() < gp::Resolution()'
- **Branch 4** @ line 879 — *curve_type_cast_to_line_c2* — **UNCOVERED**
  - What it tests: C2 is a Geom2d_Line
  - Repair action: Use line directly
  - Suggested fixture: defect mentioning 'down_cast<Geom2d_Line>(C2)'
- **Branch 5** @ line 883 — *curve_type_fallback_bounded_c2* — **UNCOVERED**
  - What it tests: C2 is a BoundedCurve (not a Line)
  - Repair action: Create synthetic line from start->end vector
  - Suggested fixture: defect mentioning 'down_cast<Geom2d_BoundedCurve>(C2)'
- **Branch 6** @ line 891 — *degenerate_bounded_curve_c2* — **UNCOVERED**
  - What it tests: BoundedCurve C2 with degenerate endpoint vector
  - Repair action: Return 0 (invalid seam selection)
  - Suggested fixture: defect mentioning 'SquareMagnitude() < gp::Resolution()'
- **Branch 7** @ line 905 — *direction_x_positive* — **UNCOVERED**
  - What it tests: Direction X > 0 (V-direction seam)
  - Repair action: Set UdirPos=true, analyze X locations
  - Suggested fixture: defect mentioning 'theDir.X() > 0.', 'UdirPos = true'
- **Branch 8** @ line 909 — *direction_x_negative* — **UNCOVERED**
  - What it tests: Direction X < 0 (V-direction opposite)
  - Repair action: Set UdirNeg=true
  - Suggested fixture: defect mentioning 'theDir.X() < 0.', 'UdirNeg = true'
- **Branch 9** @ line 913 — *direction_y_positive* — **UNCOVERED**
  - What it tests: Direction Y > 0 (U-direction seam)
  - Repair action: Set VdirPos=true, analyze Y locations
  - Suggested fixture: defect mentioning 'theDir.Y() > 0.', 'VdirPos = true'
- **Branch 10** @ line 917 — *direction_y_negative* — **UNCOVERED**
  - What it tests: Direction Y < 0 (U-direction opposite)
  - Repair action: Set VdirNeg=true
  - Suggested fixture: defect mentioning 'theDir.Y() < 0.', 'VdirNeg = true'
- **Branch 11** @ line 922 — *vdir_positive_seam_selection* — **UNCOVERED**
  - What it tests: VdirPos=true: select based on max X location
  - Repair action: Return curve index: 1 if loc1.X() > loc2.X(), else 2
  - Suggested fixture: defect mentioning 'VdirPos', 'theLoc1.X() > theLoc2.X()'
- **Branch 12** @ line 934 — *vdir_negative_seam_selection* — **UNCOVERED**
  - What it tests: VdirNeg=true: select based on min X location
  - Repair action: Return curve index: 2 if loc1.X() > loc2.X(), else 1
  - Suggested fixture: defect mentioning 'VdirNeg'
- **Branch 13** @ line 945 — *udir_positive_seam_selection* — **UNCOVERED**
  - What it tests: UdirPos=true: select based on min Y location
  - Repair action: Return curve index: 1 if loc1.Y() < loc2.Y(), else 2
  - Suggested fixture: defect mentioning 'UdirPos', 'theLoc1.Y() < theLoc2.Y()'
- **Branch 14** @ line 957 — *udir_negative_seam_selection* — **UNCOVERED**
  - What it tests: UdirNeg=true: select based on max Y location
  - Repair action: Return curve index: 2 if loc1.Y() < loc2.Y(), else 1
  - Suggested fixture: defect mentioning 'UdirNeg'

#### `ShapeAnalysis_Curve.ValidateRange` — lines 590–733
(18 branches, 4 covered.)

- **Branch 1** @ line 598 — *bounded_curve_validation* — **UNCOVERED**
  - What it tests: Curve type check: bounded non-closed curve parameter range enforcement
  - Repair action: Clamp First/Last to curve bounds [cf, cl]
  - Suggested fixture: defect mentioning 'IsKind(Geom_BoundedCurve)', 'IsClosed()'
- **Branch 2** @ line 600 — *parameter_boundary_violation* — **UNCOVERED**
  - What it tests: First < cf (below curve lower bound)
  - Repair action: Set First = cf
  - Suggested fixture: defect mentioning 'First < cf'
- **Branch 3** @ line 604 — *parameter_boundary_violation* — **UNCOVERED**
  - What it tests: First > cl (above curve upper bound)
  - Repair action: Set First = cl
  - Suggested fixture: defect mentioning 'First > cl'
- **Branch 4** @ line 608 — *parameter_boundary_violation* — **UNCOVERED**
  - What it tests: Last < cf (below curve lower bound)
  - Repair action: Set Last = cf
  - Suggested fixture: defect mentioning 'Last < cf'
- **Branch 5** @ line 612 — *parameter_boundary_violation* — **UNCOVERED**
  - What it tests: Last > cl (above curve upper bound)
  - Repair action: Set Last = cl
  - Suggested fixture: defect mentioning 'Last > cl'
- **Branch 6** @ line 619 — *periodic_curve_adjustment* — **UNCOVERED**
  - What it tests: Periodic curve detected via IsPeriodic()
  - Repair action: ElCLib::AdjustPeriodic normalizes parameter range
  - Suggested fixture: defect mentioning 'IsPeriodic', 'ElCLib::AdjustPeriodic'
- **Branch 7** @ line 625 — *parameter_order_validation* — **UNCOVERED**
  - What it tests: First < Last (normal order)
  - Repair action: No repair needed for correct order
  - Suggested fixture: defect mentioning 'First < Last'
- **Branch 8** @ line 629 — *closed_curve_endpoint_detection* — **UNCOVERED**
  - What it tests: Curve is closed and First >= Last (reversed)
  - Repair action: Detect endpoint aliasing and fix parameter mapping
  - Suggested fixture: defect mentioning 'IsClosed()', 'First >= Last'
- **Branch 9** @ line 636 — *endpoint_aliasing_near_cf* — COVERED by: tb007
  - What it tests: Last near cf (distance < PConfusion), should be cl
  - Repair action: Set Last = cl
- **Branch 10** @ line 641 — *endpoint_aliasing_near_cl* — **UNCOVERED**
  - What it tests: First near cl (distance < PConfusion), should be cf
  - Repair action: Set First = cf
  - Suggested fixture: defect mentioning 'std::abs(First - cl)'
- **Branch 11** @ line 652 — *endpoint_3d_distance_validation* — **UNCOVERED**
  - What it tests: Distance between value(First) and value(cf) < preci
  - Repair action: Set First = cf for geometric proximity
  - Suggested fixture: defect mentioning 'Value(First).Distance(Value(cf))'
- **Branch 12** @ line 656 — *endpoint_3d_distance_validation* — **UNCOVERED**
  - What it tests: Distance between value(Last) and value(cl) < preci
  - Repair action: Set Last = cl for geometric proximity
  - Suggested fixture: defect mentioning 'Value(Last).Distance(Value(cl))'
- **Branch 13** @ line 660 — *parameter_order_swap* — **UNCOVERED**
  - What it tests: First > Last after 3D validation
  - Repair action: Swap First and Last parameters
  - Suggested fixture: defect mentioning 'First > Last', 'tmp = First'
- **Branch 14** @ line 669 — *bspline_endpoint_closure* — **UNCOVERED**
  - What it tests: BSpline with geometrically closed endpoints (distance <= preci)
  - Repair action: Map endpoint parameters similarly to IsClosed() case
  - Suggested fixture: defect mentioning 'IsKind(Geom_BSplineCurve)', 'StartPoint().Distance(EndPoint())'
- **Branch 15** @ line 701 — *bspline_parameter_reversal* — **UNCOVERED**
  - What it tests: BSpline with First > Last (reversed parametrization)
  - Repair action: Call ReversedParameter() and Reverse() on curve
  - Suggested fixture: defect mentioning 'ReversedParameter', 'theCurve->Reverse()'
- **Branch 16** @ line 708 — *degenerate_range_detection* — COVERED by: gp039
  - What it tests: First == Last (zero-length range)
  - Repair action: Reset to full curve bounds [cf, cl], return false
- **Branch 17** @ line 718 — *non_bspline_parameter_reversal* — COVERED by: a024, a034, ad027, ad047, ad086, bo005, gb003, gs001 (+50 more)
  - What it tests: Non-BSpline curve with First > Last
  - Repair action: Call ReversedParameter() and Reverse()
- **Branch 18** @ line 725 — *degenerate_range_epsilon_expansion* — COVERED by: gp039, tb007
  - What it tests: Degenerate range First == Last on non-BSpline
  - Repair action: Expand by PConfusion() on each side


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_Edge.cxx`

6 methods, 43 branches, 2 covered.

#### `ShapeAnalysis_Edge.CheckCurve3dWithPCurve` — lines 382–425
(5 branches, 0 covered.)

- **Branch 1** @ line 385 — *planar_surface_check* — **UNCOVERED**
  - What it tests: Surface is a Plane, not a generic surface
  - Repair action: return false immediately (no need to check)
  - Suggested fixture: defect mentioning 'surface->IsKind(STANDARD_TYPE(Geom_Plane)'
- **Branch 2** @ line 392 — *pcurve_missing* — **UNCOVERED**
  - What it tests: PCurve cannot be extracted from surface
  - Repair action: encode FAIL1 status and return false
  - Suggested fixture: defect mentioning '!PCurve(edge, surface', 'ShapeExtend_FAIL1'
- **Branch 3** @ line 400 — *curve3d_missing* — **UNCOVERED**
  - What it tests: 3D curve cannot be extracted from edge
  - Repair action: encode FAIL2 status and return false
  - Suggested fixture: defect mentioning '!Curve3d(edge, c3d', 'ShapeExtend_FAIL2'
- **Branch 4** @ line 409 — *null_vertices* — **UNCOVERED**
  - What it tests: Edge has null first or last vertex
  - Repair action: return false (malformed edge)
  - Suggested fixture: defect mentioning 'aFirstVert.IsNull() || aLastVert.IsNull'
- **Branch 5** @ line 419 — *curve_endpoint_mismatch* — **UNCOVERED**
  - What it tests: 3D curve endpoints don't match surface pcurve endpoints
  - Repair action: delegate to CheckPoints with extracted points
  - Suggested fixture: defect mentioning 'CheckPoints(c3d->Value(f3d)', 'return CheckPoints'

#### `ShapeAnalysis_Edge.CheckPoints` — lines 435–446
(2 branches, 0 covered.)

- **Branch 1** @ line 437 — *points_coincident* — **UNCOVERED**
  - What it tests: Both endpoints match within tolerance
  - Repair action: return false (no mismatch detected)
  - Suggested fixture: defect mentioning 'P1A.SquareDistance(P2A) <= preci1', 'P1B.SquareDistance(P2B) <= preci2'
- **Branch 2** @ line 441 — *reversed_endpoint_mapping* — **UNCOVERED**
  - What it tests: Curves are reversed relative to each other
  - Repair action: encode DONE1 status and return true
  - Suggested fixture: defect mentioning 'P1A.Distance(P2B) + (P1B.Distance(P2A))', 'ShapeExtend_DONE1'

#### `ShapeAnalysis_Edge.CheckSameParameter` — lines 708–838
(12 branches, 0 covered.)

- **Branch 1** @ line 710 — *degenerate_edge* — **UNCOVERED**
  - What it tests: Edge is marked as degenerate
  - Repair action: return false immediately
  - Suggested fixture: defect mentioning 'if (BRep_Tool::Degenerated(edge)'
- **Branch 2** @ line 725 — *curve3d_missing* — **UNCOVERED**
  - What it tests: Cannot extract 3D curve from edge
  - Repair action: encode FAIL1 status and return false
  - Suggested fixture: defect mentioning 'if (aC3D.IsNull())'
- **Branch 3** @ line 731 — *curve_location_not_identity* — **UNCOVERED**
  - What it tests: 3D curve has non-identity location transformation
  - Repair action: transform curve and update parameters
  - Suggested fixture: defect mentioning 'if (!aCurveLoc.IsIdentity())'
- **Branch 4** @ line 744 — *face_pcurve_filtering* — **UNCOVERED**
  - What it tests: Input face is provided (not null)
  - Repair action: filter pcurves to match input face surface and location
  - Suggested fixture: defect mentioning 'if (!face.IsNull())'
- **Branch 5** @ line 762 — *no_more_pcurves* — **UNCOVERED**
  - What it tests: Iterator exhausted (aPC is null)
  - Repair action: break from pcurve iteration loop
  - Suggested fixture: defect mentioning 'if (aPC.IsNull())'
- **Branch 6** @ line 771 — *face_surface_mismatch* — **UNCOVERED**
  - What it tests: Pcurve surface/location don't match input face
  - Repair action: continue to next pcurve iteration
  - Suggested fixture: defect mentioning 'if (!aFaceSurf.IsNull()) { if (aFaceSurf != aS'
- **Branch 7** @ line 795 — *validation_failed* — **UNCOVERED**
  - What it tests: Curve validation on surface reports failure
  - Repair action: encode FAIL2 status
  - Suggested fixture: defect mentioning 'if (!aValidateEdge.IsDone())'
- **Branch 8** @ line 803 — *planar_projection_fallback* — **UNCOVERED**
  - What it tests: No pcurves found and face surface exists (planar check)
  - Repair action: check deviation for projection onto plane
  - Suggested fixture: defect mentioning 'if (!IsPCurveFound && !aFaceSurf.IsNull())'
- **Branch 9** @ line 807 — *plane_projection_exists* — **UNCOVERED**
  - What it tests: Plane projection pcurve can be extracted
  - Repair action: validate edge projection on plane surface
  - Suggested fixture: defect mentioning 'if (!aPC.IsNull())'
- **Branch 10** @ line 821 — *plane_validation_failed* — **UNCOVERED**
  - What it tests: Plane projection validation reports failure
  - Repair action: encode FAIL2 status
  - Suggested fixture: defect mentioning 'if (!aValidateEdgeOnPlane.IsDone())'
- **Branch 11** @ line 828 — *tolerance_exceeded* — **UNCOVERED**
  - What it tests: Computed deviation exceeds edge tolerance
  - Repair action: encode DONE1 status
  - Suggested fixture: defect mentioning 'if (maxdev > TE->Tolerance())'
- **Branch 12** @ line 832 — *same_parameter_flag_check* — **UNCOVERED**
  - What it tests: Edge SameParameter flag is false
  - Repair action: encode DONE2 status (parameter mismatch)
  - Suggested fixture: defect mentioning 'if (!SameParameter)'

#### `ShapeAnalysis_Edge.CheckVerticesWithCurve3d` — lines 453–493
(6 branches, 0 covered.)

- **Branch 1** @ line 463 — *curve3d_missing* — **UNCOVERED**
  - What it tests: Cannot extract 3D curve from edge
  - Repair action: encode FAIL1 status and return false
  - Suggested fixture: defect mentioning '!Curve3d(edge, c3d', 'ShapeExtend_FAIL1'
- **Branch 2** @ line 470 — *first_vertex_check_selector* — **UNCOVERED**
  - What it tests: vtx parameter indicates which vertex to check (vtx != 2)
  - Repair action: check first vertex position against curve start
  - Suggested fixture: defect mentioning 'if (vtx != 2)'
- **Branch 3** @ line 475 — *first_vertex_distance_mismatch* — **UNCOVERED**
  - What it tests: Vertex position deviates from curve start beyond tolerance
  - Repair action: encode DONE1 status and return true
  - Suggested fixture: defect mentioning 'p1v.Distance(p13d) >', 'myStatus |= ShapeExtend_DONE1'
- **Branch 4** @ line 481 — *second_vertex_check_selector* — **UNCOVERED**
  - What it tests: vtx parameter indicates which vertex to check (vtx != 1)
  - Repair action: check second vertex position against curve end
  - Suggested fixture: defect mentioning 'if (vtx != 1)'
- **Branch 5** @ line 486 — *second_vertex_distance_mismatch* — **UNCOVERED**
  - What it tests: Vertex position deviates from curve end beyond tolerance
  - Repair action: encode DONE2 status and return true
  - Suggested fixture: defect mentioning 'p2v.Distance(p23d) >', 'myStatus |= ShapeExtend_DONE2'
- **Branch 6** @ line 475 — *tolerance_selection* — **UNCOVERED**
  - What it tests: Whether to use provided tolerance or vertex tolerance
  - Repair action: use BRep_Tool::Tolerance(V) if preci < 0, else use preci
  - Suggested fixture: defect mentioning 'preci < 0 ? BRep_Tool::Tolerance'

#### `ShapeAnalysis_Edge.CheckVerticesWithPCurve` — lines 516–564
(8 branches, 0 covered.)

- **Branch 1** @ line 526 — *pcurve_missing* — **UNCOVERED**
  - What it tests: Cannot extract PCurve from surface location
  - Repair action: encode FAIL1 status and return false
  - Suggested fixture: defect mentioning '!PCurve(edge, surf, loc', 'ShapeExtend_FAIL1'
- **Branch 2** @ line 533 — *first_vertex_check_selector* — **UNCOVERED**
  - What it tests: vtx parameter != 2 (check first vertex)
  - Repair action: evaluate surface at pcurve start point
  - Suggested fixture: defect mentioning 'if (vtx != 2)'
- **Branch 3** @ line 537 — *location_identity_check* — **UNCOVERED**
  - What it tests: Surface location is non-identity transformation
  - Repair action: apply transformation to surface point
  - Suggested fixture: defect mentioning 'if (!loc.IsIdentity())'
- **Branch 4** @ line 542 — *first_vertex_distance_mismatch* — **UNCOVERED**
  - What it tests: Vertex position deviates from surface point beyond tolerance
  - Repair action: encode DONE1 status
  - Suggested fixture: defect mentioning 'p1v.Distance(p12d) >', 'myStatus |= ShapeExtend_DONE1'
- **Branch 5** @ line 548 — *second_vertex_check_selector* — **UNCOVERED**
  - What it tests: vtx parameter != 1 (check second vertex)
  - Repair action: evaluate surface at pcurve end point
  - Suggested fixture: defect mentioning 'if (vtx != 1)'
- **Branch 6** @ line 552 — *location_identity_check* — **UNCOVERED**
  - What it tests: Surface location is non-identity transformation
  - Repair action: apply transformation to surface point
  - Suggested fixture: defect mentioning 'if (!loc.IsIdentity())'
- **Branch 7** @ line 557 — *second_vertex_distance_mismatch* — **UNCOVERED**
  - What it tests: Vertex position deviates from surface point beyond tolerance
  - Repair action: encode DONE2 status
  - Suggested fixture: defect mentioning 'p2v.Distance(p22d) >', 'myStatus |= ShapeExtend_DONE2'
- **Branch 8** @ line 542 — *tolerance_selection* — **UNCOVERED**
  - What it tests: Whether to use provided tolerance or vertex tolerance
  - Repair action: use BRep_Tool::Tolerance(V) if preci < 0, else use preci
  - Suggested fixture: defect mentioning 'preci < 0 ? BRep_Tool::Tolerance'

#### `ShapeAnalysis_Edge.GetEndTangent2d` — lines 290–366
(10 branches, 2 covered.)

- **Branch 1** @ line 293 — *missing_pcurve* — COVERED by: in014
  - What it tests: PCurve extraction fails
  - Repair action: return false with zero vector
- **Branch 2** @ line 300 — *delta_precision_check* — **UNCOVERED**
  - What it tests: Parameter delta smaller than confusion threshold
  - Repair action: reset dpnew to 0, fall back to derivative method
  - Suggested fixture: defect mentioning 'std::abs(delta) < Precision::PConfusion'
- **Branch 3** @ line 310 — *curve_end_selection* — **UNCOVERED**
  - What it tests: Different handling for curve end vs start
  - Repair action: compute tangent direction differently for end vs start
  - Suggested fixture: defect mentioning 'atend2', 'par1 = cl', 'par1 = cf'
- **Branch 4** @ line 326 — *zero_tangent_magnitude* — **UNCOVERED**
  - What it tests: Computed difference vector has zero magnitude
  - Repair action: reset dpnew to 0, try derivative method instead
  - Suggested fixture: defect mentioning 'v.SquareMagnitude() < Precision::PConfusion'
- **Branch 5** @ line 333 — *fallback_to_derivatives* — **UNCOVERED**
  - What it tests: dpnew is zero or smaller than confusion
  - Repair action: use D1, D2, D3 derivatives to find non-null tangent
  - Suggested fixture: defect mentioning 'if (dpnew <= Precision::Confusion'
- **Branch 6** @ line 338 — *d1_null_fallback* — **UNCOVERED**
  - What it tests: First derivative is null
  - Repair action: try second derivative (D2)
  - Suggested fixture: defect mentioning 'c2d->D1(par', 'if (v.SquareMagnitude() < Precision::PConfusion'
- **Branch 7** @ line 342 — *d2_null_fallback* — **UNCOVERED**
  - What it tests: Second derivative is null
  - Repair action: try third derivative (D3)
  - Suggested fixture: defect mentioning 'c2d->D2(par'
- **Branch 8** @ line 346 — *d3_null_fallback* — **UNCOVERED**
  - What it tests: Third derivative is null
  - Repair action: compute straight vector between opposite ends
  - Suggested fixture: defect mentioning 'c2d->D3(par'
- **Branch 9** @ line 351 — *zero_end_straight* — COVERED by: in014
  - What it tests: Straight vector between opposite ends is zero
  - Repair action: return false (curve is degenerate)
- **Branch 10** @ line 358 — *reversed_orientation_correction* — **UNCOVERED**
  - What it tests: Edge orientation is REVERSED
  - Repair action: reverse computed tangent vector
  - Suggested fixture: defect mentioning 'if (edge.Orientation() == TopAbs_REVERSED'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_Edge.cxx, src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_Curve.cxx`

5 methods, 33 branches, 4 covered.

#### `ShapeAnalysis_Curve.GetSamplePoints (Geom2d_Curve)` — lines 1321–1420
(3 branches, 0 covered.)

- **Branch 1** @ line 1325 — *geom2d_adaptor_construction* — **UNCOVERED**
  - What it tests: Creates 2D adaptor for curve to compute default sample count
  - Repair action: Uses Geom2dInt_Geom2dCurveTool::NbSamples for curve-specific sampling
  - Suggested fixture: defect mentioning 'Geom2dAdaptor_Curve C(curve, first, last)', 'Geom2dInt_Geom2dCurveTool::NbSamples'
- **Branch 2** @ line 1327 — *rational_bspline_multiplier* — **UNCOVERED**
  - What it tests: Detects complex curves (rational splines) that need finer sampling
  - Repair action: Multiplies sample count by 4 when nbs > 2 (handles rational degree-3 circles)
  - Suggested fixture: defect mentioning 'if (nbs > 2)', 'nbs *= 4'
- **Branch 3** @ line 1331 — *uniform_parameter_sampling_2d* — **UNCOVERED**
  - What it tests: Distributes sample points uniformly across 2D curve parameter range
  - Repair action: Creates nbs-1 interior samples plus endpoint with step = (last-first)/(nbs-1)
  - Suggested fixture: defect mentioning 'step = (last - first) / (double)(nbs - 1)', 'C.Value(first + step * i)'

#### `ShapeAnalysis_Curve.GetSamplePoints (Geom_Curve)` — lines 1262–1313
(9 branches, 1 covered.)

- **Branch 1** @ line 1264 — *zero_curve_parameter_range* — COVERED by: in014
  - What it tests: Detects if curve parameter range is zero (degenerate curve)
  - Repair action: Returns false when curve parameter span is zero
- **Branch 2** @ line 1310 — *line_geometry_detection* — **UNCOVERED**
  - What it tests: Optimizes sampling for linear curves
  - Repair action: Uses only 2 sample points for lines (minimal sampling)
  - Suggested fixture: defect mentioning 'curve->IsKind(STANDARD_TYPE(Geom_Line))', 'nbp = 2'
- **Branch 3** @ line 1314 — *circle_geometry_detection* — **UNCOVERED**
  - What it tests: Optimizes sampling for circular curves
  - Repair action: Uses 360*aK sample points for circles (per-degree sampling)
  - Suggested fixture: defect mentioning 'curve->IsKind(STANDARD_TYPE(Geom_Circle))', 'nbp = 360 * aK'
- **Branch 4** @ line 1318 — *bspline_geometry_detection* — **UNCOVERED**
  - What it tests: Optimizes sampling for B-spline curves using knot/degree info
  - Repair action: Uses nbp = NbKnots * Degree * aK with floor of 2 minimum
  - Suggested fixture: defect mentioning 'curve->IsKind(STANDARD_TYPE(Geom_BSplineCurve))', 'NbKnots() * Degree()'
- **Branch 5** @ line 1323 — *bspline_minimum_points* — **UNCOVERED**
  - What it tests: Validates minimum sampling point count for B-splines
  - Repair action: Clamps nbp to 2 when computed value is less than 2
  - Suggested fixture: defect mentioning 'if (nbp < 2.0)', 'nbp = 2'
- **Branch 6** @ line 1328 — *bezier_geometry_detection* — **UNCOVERED**
  - What it tests: Optimizes sampling for Bezier curves using pole count
  - Repair action: Uses nbp = 3 + NbPoles (proportional to control points)
  - Suggested fixture: defect mentioning 'curve->IsKind(STANDARD_TYPE(Geom_BezierCurve))', '3 + aB->NbPoles()'
- **Branch 7** @ line 1333 — *offset_curve_unwrapping* — **UNCOVERED**
  - What it tests: Detects offset curves and recurses to basis curve
  - Repair action: Delegates sampling to basis curve instead of offset curve
  - Suggested fixture: defect mentioning 'curve->IsKind(STANDARD_TYPE(Geom_OffsetCurve))', 'BasisCurve()'
- **Branch 8** @ line 1338 — *trimmed_curve_unwrapping* — **UNCOVERED**
  - What it tests: Detects trimmed curves and recurses to basis curve
  - Repair action: Delegates sampling to basis curve instead of trimmed curve
  - Suggested fixture: defect mentioning 'curve->IsKind(STANDARD_TYPE(Geom_TrimmedCurve))', 'BasisCurve()'
- **Branch 9** @ line 1346 — *uniform_parameter_sampling* — **UNCOVERED**
  - What it tests: Distributes sample points uniformly across parameter range
  - Repair action: Creates nbp-1 interior samples plus endpoint, spacing = (last-first)/(nbp-1)
  - Suggested fixture: defect mentioning 'step = (last - first) / (double)(nbp - 1)', 'seq.Append(GAC.Value'

#### `ShapeAnalysis_Curve.IsClosed` — lines 1425–1446
(4 branches, 1 covered.)

- **Branch 1** @ line 1427 — *curve_closed_property_flag* — **UNCOVERED**
  - What it tests: Checks if curve reports itself as closed
  - Repair action: Returns true immediately if curve's IsClosed() flag is set
  - Suggested fixture: defect mentioning 'if (theCurve->IsClosed())', 'return true'
- **Branch 2** @ line 1430 — *precision_lower_bound* — **UNCOVERED**
  - What it tests: Ensures precision threshold meets minimum confusion tolerance
  - Repair action: Uses max(preci, Precision::Confusion()) to avoid overly small tolerances
  - Suggested fixture: defect mentioning 'prec = std::max(preci, Precision::Confusion())'
- **Branch 3** @ line 1433 — *infinite_parameter_endpoints* — COVERED by: in014
  - What it tests: Detects curves with infinite parameter bounds
  - Repair action: Returns false when first or last parameter is infinite
- **Branch 4** @ line 1438 — *endpoint_distance_tolerance* — **UNCOVERED**
  - What it tests: Validates that curve endpoints are within tolerance distance
  - Repair action: Returns true if square distance between endpoints <= prec^2
  - Suggested fixture: defect mentioning 'aClosedVal = theCurve->Value(f).SquareDistance(theCurve->Value(l))', 'return (aClosedVal <= preci2)'

#### `ShapeAnalysis_Edge.CheckOverlapping` — lines 898–995
(12 branches, 2 covered.)

- **Branch 1** @ line 903 — *edge_length_comparison* — **UNCOVERED**
  - What it tests: Selects which edge is shorter for downstream sampling strategy
  - Repair action: Swaps edge order based on length comparison (aLength1 >= aLength2)
  - Suggested fixture: defect mentioning 'aLength1 >= aLength2', 'aFirstEdge', 'aSecEdge'
- **Branch 2** @ line 920 — *overlap_detection_branch_1* — **UNCOVERED**
  - What it tests: Detects if edges are overlapping across entire edge domain
  - Repair action: Returns early with DONE3 status when overlap found on whole edges
  - Suggested fixture: defect mentioning 'if (isOverlap)', 'ShapeExtend_DONE3', 'return isOverlap'
- **Branch 3** @ line 925 — *domain_distance_validation* — **UNCOVERED**
  - What it tests: Checks if domain distance parameter is zero (disables local overlap checking)
  - Repair action: Returns false when theDomainDist==0.0, skipping segment-based analysis
  - Suggested fixture: defect mentioning 'if (theDomainDist == 0.0)', 'return isOverlap'
- **Branch 4** @ line 936 — *distance_computation_status* — **UNCOVERED**
  - What it tests: Validates that extrema distance computation succeeded
  - Repair action: Only processes results when aMinDist.IsDone() is true
  - Suggested fixture: defect mentioning 'if (aMinDist.IsDone())', 'aresTol = aMinDist.Value()'
- **Branch 5** @ line 939 — *tolerance_threshold_check* — COVERED by: in014
  - What it tests: Validates computed distance against tolerance threshold
  - Repair action: Returns false when aresTol >= theTolOverlap (no overlapping)
- **Branch 6** @ line 948 — *support_point_type_vertex* — **UNCOVERED**
  - What it tests: Detects if minimum distance point is at edge vertex
  - Repair action: Maps support vertex to arc length: 0 for first, aLength for last
  - Suggested fixture: defect mentioning 'if (aType1 == BRepExtrema_IsVertex)', 'aV1.IsSame(aSupportShape1)'
- **Branch 7** @ line 953 — *support_vertex_endpoint_classification* — **UNCOVERED**
  - What it tests: Distinguishes between first and last vertex of edge
  - Repair action: Sets aLengthP to 0.0 for first vertex, aLength for last vertex
  - Suggested fixture: defect mentioning 'if (aV1.IsSame(aSupportShape1))', 'aLengthP = 0.0'
- **Branch 8** @ line 962 — *support_point_type_edge* — **UNCOVERED**
  - What it tests: Detects if minimum distance point is on edge interior
  - Repair action: Converts parameter-space distance to arc-length distance
  - Suggested fixture: defect mentioning 'else if (aType1 == BRepExtrema_IsOnEdge)', 'GCPnts_AbscissaPoint::Length'
- **Branch 9** @ line 970 — *unknown_support_type* — COVERED by: ad050, ad101, bo006, fi002, gn003, gn037, hea011, le014 (+20 more)
  - What it tests: Handles unexpected support type values
  - Repair action: Skips solution when support type is neither vertex nor edge
- **Branch 10** @ line 975 — *domain_lower_bound_clipping* — **UNCOVERED**
  - What it tests: Validates start of search domain is non-negative
  - Repair action: Clamps aStartLength to 0 if negative, adjusts aEndLength to aDomainTol
  - Suggested fixture: defect mentioning 'if (aStartLength < 0.0)', 'aStartLength = 0'
- **Branch 11** @ line 980 — *domain_upper_bound_clipping* — **UNCOVERED**
  - What it tests: Validates end of search domain is within edge length
  - Repair action: Clamps aEndLength to aLength if exceeds, adjusts aStartLength backward
  - Suggested fixture: defect mentioning 'if (aEndLength > aLength)', 'aEndLength = aLength'
- **Branch 12** @ line 991 — *overlap_detection_branch_2* — **UNCOVERED**
  - What it tests: Detects overlapping in local domain region around extrema point
  - Repair action: Sets DONE4 status and returns true when local overlap confirmed
  - Suggested fixture: defect mentioning 'if (isOverlap)', 'ShapeExtend_DONE4'

#### `ShapeAnalysis_Edge.CheckPCurveRange` — lines 1002–1033
(5 branches, 0 covered.)

- **Branch 1** @ line 1004 — *curve_periodicity_detection* — **UNCOVERED**
  - What it tests: Checks if 2D curve is periodic to determine validation logic
  - Repair action: Sets IsPeriodic flag and retrieves period if periodic
  - Suggested fixture: defect mentioning 'thePC->IsPeriodic()', 'aPeriod = thePC->Period()'
- **Branch 2** @ line 1011 — *trimmed_curve_unwrapping* — **UNCOVERED**
  - What it tests: Detects if input is a trimmed curve and unwraps to basis curve
  - Repair action: Extracts first/last parameters and periodicity from basis curve
  - Suggested fixture: defect mentioning 'STANDARD_TYPE(Geom2d_TrimmedCurve)', 'BasisCurve()'
- **Branch 3** @ line 1017 — *trimmed_basis_periodicity_update* — **UNCOVERED**
  - What it tests: Re-evaluates periodicity of basis curve after unwrapping
  - Repair action: Updates IsPeriodic and aPeriod from basis curve properties
  - Suggested fixture: defect mentioning 'if (IsPeriodic)', 'aPeriod = aC->Period()'
- **Branch 4** @ line 1022 — *periodic_curve_range_overflow* — **UNCOVERED**
  - What it tests: Validates parameter range for periodic curves (exceeds one period)
  - Repair action: Invalidates when range exceeds one period (theLast - theFirst > aPeriod + eps)
  - Suggested fixture: defect mentioning 'if (IsPeriodic && (theLast - theFirst > aPeriod + eps))', 'isValid = false'
- **Branch 5** @ line 1026 — *non_periodic_curve_bounds* — **UNCOVERED**
  - What it tests: Validates parameter range for non-periodic curves (exceeds bounds)
  - Repair action: Invalidates when theFirst < fp or theLast > lp (beyond curve domain)
  - Suggested fixture: defect mentioning 'else if (!IsPeriodic && (theFirst < fp - eps || theLast > lp + eps))', 'isValid = false'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_FreeBoundsProperties.cxx`

6 methods, 26 branches, 10 covered.

#### `ShapeAnalysis_FreeBoundsProperties.CheckContours` — lines 277–293
(2 branches, 0 covered.)

- **Branch 1** @ line 281 — *empty_sequence* — **UNCOVERED**
  - What it tests: Process closed free bounds contour properties
  - Repair action: Call FillProperties on each closed free bound
  - Suggested fixture: defect mentioning 'myClosedFreeBounds->Length()', 'FillProperties'
- **Branch 2** @ line 286 — *empty_sequence* — **UNCOVERED**
  - What it tests: Process open free bounds contour properties
  - Repair action: Call FillProperties on each open free bound
  - Suggested fixture: defect mentioning 'myOpenFreeBounds->Length()', 'FillProperties'

#### `ShapeAnalysis_FreeBoundsProperties.CheckNotches_1` — lines 235–250
(2 branches, 2 covered.)

- **Branch 1** @ line 238 — *empty_sequence* — COVERED by: hea005
  - What it tests: Iterate closed free bounds if any exist
  - Repair action: Call CheckNotches on each closed free bound
- **Branch 2** @ line 243 — *empty_sequence* — COVERED by: hea005
  - What it tests: Iterate open free bounds if any exist
  - Repair action: Call CheckNotches on each open free bound

#### `ShapeAnalysis_FreeBoundsProperties.CheckNotches_2` — lines 254–273
(3 branches, 3 covered.)

- **Branch 1** @ line 259 — *single_edge_wire* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Only process wires with more than one edge
  - Repair action: Skip notch detection if wire has single edge
- **Branch 2** @ line 261 — *multi_edge_notch* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: Iterate through each edge position in wire
  - Repair action: Call CheckNotches for notch at each edge position
- **Branch 3** @ line 265 — *notch_detection_success* — COVERED by: hea005
  - What it tests: Collect detected notches with their max distance
  - Repair action: Add notch to fbData if CheckNotches returns true

#### `ShapeAnalysis_FreeBoundsProperties.CheckNotches_3` — lines 297–387
(11 branches, 2 covered.)

- **Branch 1** @ line 303 — *tolerance_normalization* — COVERED by: gp013, tb001, tb007, tb018, tb019, tfa006, twi040
  - What it tests: Use minimum tolerance from stored or precision constant
  - Repair action: Set tol to max of myTolerance and Precision::Confusion()
- **Branch 2** @ line 308 — *invalid_index* — **UNCOVERED**
  - What it tests: Validate edge index is within bounds
  - Repair action: Return false if num <= 0 or num > NbEdges
  - Suggested fixture: defect mentioning 'num <= 0', 'num > wdt->NbEdges()'
- **Branch 3** @ line 313 — *index_wrapping* — **UNCOVERED**
  - What it tests: Handle circular wire indexing for n1
  - Repair action: Use num if positive, else use NbEdges for n1
  - Suggested fixture: defect mentioning 'n1 = (num > 0', 'wdt->NbEdges'
- **Branch 4** @ line 314 — *index_wrapping* — **UNCOVERED**
  - What it tests: Handle circular wire indexing for n2 (next edge)
  - Repair action: Set n2 to n1+1 or wrap to 1 if at end
  - Suggested fixture: defect mentioning 'n2 = (n1 < wdt->NbEdges', 'n1 + 1'
- **Branch 5** @ line 322 — *small_edge_skip* — **UNCOVERED**
  - What it tests: Detect if edge n2 is too small to be significant
  - Repair action: Skip small edge and advance to n2+1 if CheckSmall true
  - Suggested fixture: defect mentioning 'saw->CheckSmall', 'n2 + 1'
- **Branch 6** @ line 335 — *missing_3d_curve* — COVERED by: in014
  - What it tests: Require both edges have valid 3D curve representation
  - Repair action: Return false if Curve3d fails on either edge
- **Branch 7** @ line 344 — *edge_orientation_reversal* — **UNCOVERED**
  - What it tests: Adjust vector direction if edge E1 is reversed
  - Repair action: Reverse vec1 if E1.Orientation() == TopAbs_REVERSED
  - Suggested fixture: defect mentioning 'E1.Orientation', 'vec1.Reverse'
- **Branch 8** @ line 348 — *edge_orientation_reversal* — **UNCOVERED**
  - What it tests: Adjust vector direction if edge E2 is reversed
  - Repair action: Reverse vec2 if E2.Orientation() == TopAbs_REVERSED
  - Suggested fixture: defect mentioning 'E2.Orientation', 'vec2.Reverse'
- **Branch 9** @ line 354 — *acute_angle_notch* — **UNCOVERED**
  - What it tests: Detect notch when angle between edges near π (near straight)
  - Repair action: Measure max distance if angle > 95% * π
  - Suggested fixture: defect mentioning 'angl > 0.95 * M_PI', 'distMax'
- **Branch 10** @ line 363 — *curve_parameter_order* — **UNCOVERED**
  - What it tests: Normalize curve parameter range orientation
  - Repair action: Swap p1/p2 if First2 >= Last2 to maintain p1 < p2
  - Suggested fixture: defect mentioning 'First2 < Last2', 'p1 = First2'
- **Branch 11** @ line 376 — *projection_miss* — **UNCOVERED**
  - What it tests: Handle case where point projection onto curve fails
  - Repair action: Set distance to 0 if NbPoints() == 0
  - Suggested fixture: defect mentioning 'ppc.NbPoints()', 'LowerDistance'

#### `ShapeAnalysis_FreeBoundsProperties.DispatchBounds` — lines 188–231
(5 branches, 3 covered.)

- **Branch 1** @ line 189 — *uninitialized_data* — COVERED by: in014
  - What it tests: Check if shape is loaded before processing free bounds
  - Repair action: Return early if IsLoaded() fails
- **Branch 2** @ line 195 — *tolerance_variant* — COVERED by: hea003, hea004, hea005
  - What it tests: Handle tolerance > 0 branch with explicit tolerance
  - Repair action: Construct ShapeAnalysis_FreeBounds with myTolerance parameter
- **Branch 3** @ line 201 — *tolerance_variant* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Handle zero or default tolerance case
  - Repair action: Construct ShapeAnalysis_FreeBounds without explicit tolerance
- **Branch 4** @ line 212 — *empty_sequence* — **UNCOVERED**
  - What it tests: Process closed bounds from compound sequence
  - Repair action: Append each wire to myClosedFreeBounds with wrapping
  - Suggested fixture: defect mentioning 'tmpSeq->Length()', 'myClosedFreeBounds'
- **Branch 5** @ line 222 — *empty_sequence* — **UNCOVERED**
  - What it tests: Process open bounds from compound sequence
  - Repair action: Append each wire to myOpenFreeBounds with wrapping
  - Suggested fixture: defect mentioning 'tmpSeq2->Length()', 'myOpenFreeBounds'

#### `ShapeAnalysis_FreeBoundsProperties.FillProperties` — lines 391–423
(3 branches, 0 covered.)

- **Branch 1** @ line 401 — *zero_length_contour* — **UNCOVERED**
  - What it tests: Guard against division by zero when contour length is 0
  - Repair action: Skip ratio/width calculation if length == 0
  - Suggested fixture: defect mentioning 'length != 0', 'k = area'
- **Branch 2** @ line 405 — *zero_coefficient* — **UNCOVERED**
  - What it tests: Guard against division by zero when k coefficient is 0
  - Repair action: Skip r/aver calculation if k == 0
  - Suggested fixture: defect mentioning 'k != 0', 'aux = 1'
- **Branch 3** @ line 408 — *negative_discriminant* — **UNCOVERED**
  - What it tests: Handle case where sqrt argument becomes negative
  - Repair action: Skip sqrt and r calculation if aux < 0
  - Suggested fixture: defect mentioning 'aux >= 0', 'sqrt(aux)'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_ShapeContents.cxx`

2 methods, 78 branches, 15 covered.

#### `ShapeAnalysis_ShapeContents.Clear` — lines 58–100
(39 branches, 0 covered.)

- **Branch 1** @ line 59 — *counter_reset* — **UNCOVERED**
  - What it tests: Solids counter initialization
  - Repair action: Reset myNbSolids to 0
  - Suggested fixture: defect mentioning 'myNbSolids = 0'
- **Branch 2** @ line 60 — *counter_reset* — **UNCOVERED**
  - What it tests: Shells counter initialization
  - Repair action: Reset myNbShells to 0
  - Suggested fixture: defect mentioning 'myNbShells = 0'
- **Branch 3** @ line 61 — *counter_reset* — **UNCOVERED**
  - What it tests: Faces counter initialization
  - Repair action: Reset myNbFaces to 0
  - Suggested fixture: defect mentioning 'myNbFaces = 0'
- **Branch 4** @ line 62 — *counter_reset* — **UNCOVERED**
  - What it tests: Wires counter initialization
  - Repair action: Reset myNbWires to 0
  - Suggested fixture: defect mentioning 'myNbWires = 0'
- **Branch 5** @ line 63 — *counter_reset* — **UNCOVERED**
  - What it tests: Edges counter initialization
  - Repair action: Reset myNbEdges to 0
  - Suggested fixture: defect mentioning 'myNbEdges = 0'
- **Branch 6** @ line 64 — *counter_reset* — **UNCOVERED**
  - What it tests: Vertices counter initialization
  - Repair action: Reset myNbVertices to 0
  - Suggested fixture: defect mentioning 'myNbVertices = 0'
- **Branch 7** @ line 65 — *counter_reset* — **UNCOVERED**
  - What it tests: Solids with voids counter initialization
  - Repair action: Reset myNbSolidsWithVoids to 0
  - Suggested fixture: defect mentioning 'myNbSolidsWithVoids = 0'
- **Branch 8** @ line 66 — *counter_reset* — **UNCOVERED**
  - What it tests: Big splines counter initialization
  - Repair action: Reset myNbBigSplines to 0
  - Suggested fixture: defect mentioning 'myNbBigSplines = 0'
- **Branch 9** @ line 67 — *counter_reset* — **UNCOVERED**
  - What it tests: C0 surfaces counter initialization
  - Repair action: Reset myNbC0Surfaces to 0
  - Suggested fixture: defect mentioning 'myNbC0Surfaces = 0'
- **Branch 10** @ line 68 — *counter_reset* — **UNCOVERED**
  - What it tests: C0 curves counter initialization
  - Repair action: Reset myNbC0Curves to 0
  - Suggested fixture: defect mentioning 'myNbC0Curves = 0'
- **Branch 11** @ line 69 — *counter_reset* — **UNCOVERED**
  - What it tests: Offset surfaces counter initialization
  - Repair action: Reset myNbOffsetSurf to 0
  - Suggested fixture: defect mentioning 'myNbOffsetSurf = 0'
- **Branch 12** @ line 70 — *counter_reset* — **UNCOVERED**
  - What it tests: Indirect surfaces counter initialization
  - Repair action: Reset myNbIndirectSurf to 0
  - Suggested fixture: defect mentioning 'myNbIndirectSurf = 0'
- **Branch 13** @ line 71 — *counter_reset* — **UNCOVERED**
  - What it tests: Offset curves counter initialization
  - Repair action: Reset myNbOffsetCurves to 0
  - Suggested fixture: defect mentioning 'myNbOffsetCurves = 0'
- **Branch 14** @ line 72 — *counter_reset* — **UNCOVERED**
  - What it tests: Trimmed 2d curves counter initialization
  - Repair action: Reset myNbTrimmedCurve2d to 0
  - Suggested fixture: defect mentioning 'myNbTrimmedCurve2d = 0'
- **Branch 15** @ line 73 — *counter_reset* — **UNCOVERED**
  - What it tests: Trimmed 3d curves counter initialization
  - Repair action: Reset myNbTrimmedCurve3d to 0
  - Suggested fixture: defect mentioning 'myNbTrimmedCurve3d = 0'
- **Branch 16** @ line 74 — *counter_reset* — **UNCOVERED**
  - What it tests: BSpline surfaces counter initialization
  - Repair action: Reset myNbBSplibeSurf to 0
  - Suggested fixture: defect mentioning 'myNbBSplibeSurf = 0'
- **Branch 17** @ line 75 — *counter_reset* — **UNCOVERED**
  - What it tests: Bezier surfaces counter initialization
  - Repair action: Reset myNbBezierSurf to 0
  - Suggested fixture: defect mentioning 'myNbBezierSurf = 0'
- **Branch 18** @ line 76 — *counter_reset* — **UNCOVERED**
  - What it tests: Trimmed surfaces counter initialization
  - Repair action: Reset myNbTrimSurf to 0
  - Suggested fixture: defect mentioning 'myNbTrimSurf = 0'
- **Branch 19** @ line 77 — *counter_reset* — **UNCOVERED**
  - What it tests: Wires with seam counter initialization
  - Repair action: Reset myNbWireWitnSeam to 0
  - Suggested fixture: defect mentioning 'myNbWireWitnSeam = 0'
- **Branch 20** @ line 78 — *counter_reset* — **UNCOVERED**
  - What it tests: Wires with multiple seams counter initialization
  - Repair action: Reset myNbWireWithSevSeams to 0
  - Suggested fixture: defect mentioning 'myNbWireWithSevSeams = 0'
- **Branch 21** @ line 79 — *counter_reset* — **UNCOVERED**
  - What it tests: Faces with multiple wires counter initialization
  - Repair action: Reset myNbFaceWithSevWires to 0
  - Suggested fixture: defect mentioning 'myNbFaceWithSevWires = 0'
- **Branch 22** @ line 80 — *counter_reset* — **UNCOVERED**
  - What it tests: Edges without p-curve counter initialization
  - Repair action: Reset myNbNoPCurve to 0
  - Suggested fixture: defect mentioning 'myNbNoPCurve = 0'
- **Branch 23** @ line 81 — *counter_reset* — **UNCOVERED**
  - What it tests: Free faces counter initialization
  - Repair action: Reset myNbFreeFaces to 0
  - Suggested fixture: defect mentioning 'myNbFreeFaces = 0'
- **Branch 24** @ line 82 — *counter_reset* — **UNCOVERED**
  - What it tests: Free wires counter initialization
  - Repair action: Reset myNbFreeWires to 0
  - Suggested fixture: defect mentioning 'myNbFreeWires = 0'
- **Branch 25** @ line 83 — *counter_reset* — **UNCOVERED**
  - What it tests: Free edges counter initialization
  - Repair action: Reset myNbFreeEdges to 0
  - Suggested fixture: defect mentioning 'myNbFreeEdges = 0'
- **Branch 26** @ line 85 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared solids counter initialization
  - Repair action: Reset myNbSharedSolids to 0
  - Suggested fixture: defect mentioning 'myNbSharedSolids = 0'
- **Branch 27** @ line 86 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared shells counter initialization
  - Repair action: Reset myNbSharedShells to 0
  - Suggested fixture: defect mentioning 'myNbSharedShells = 0'
- **Branch 28** @ line 87 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared faces counter initialization
  - Repair action: Reset myNbSharedFaces to 0
  - Suggested fixture: defect mentioning 'myNbSharedFaces = 0'
- **Branch 29** @ line 88 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared wires counter initialization
  - Repair action: Reset myNbSharedWires to 0
  - Suggested fixture: defect mentioning 'myNbSharedWires = 0'
- **Branch 30** @ line 89 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared free wires counter initialization
  - Repair action: Reset myNbSharedFreeWires to 0
  - Suggested fixture: defect mentioning 'myNbSharedFreeWires = 0'
- **Branch 31** @ line 90 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared free edges counter initialization
  - Repair action: Reset myNbSharedFreeEdges to 0
  - Suggested fixture: defect mentioning 'myNbSharedFreeEdges = 0'
- **Branch 32** @ line 91 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared edges counter initialization
  - Repair action: Reset myNbSharedEdges to 0
  - Suggested fixture: defect mentioning 'myNbSharedEdges = 0'
- **Branch 33** @ line 92 — *counter_reset* — **UNCOVERED**
  - What it tests: Shared vertices counter initialization
  - Repair action: Reset myNbSharedVertices to 0
  - Suggested fixture: defect mentioning 'myNbSharedVertices = 0'
- **Branch 34** @ line 94 — *collection_clear* — **UNCOVERED**
  - What it tests: Big spline collection clearing
  - Repair action: Clear myBigSplineSec sequence
  - Suggested fixture: defect mentioning 'myBigSplineSec->Clear()'
- **Branch 35** @ line 95 — *collection_clear* — **UNCOVERED**
  - What it tests: Indirect surface collection clearing
  - Repair action: Clear myIndirectSec sequence
  - Suggested fixture: defect mentioning 'myIndirectSec->Clear()'
- **Branch 36** @ line 96 — *collection_clear* — **UNCOVERED**
  - What it tests: Offset surface collection clearing
  - Repair action: Clear myOffsetSurfaceSec sequence
  - Suggested fixture: defect mentioning 'myOffsetSurfaceSec->Clear()'
- **Branch 37** @ line 97 — *collection_clear* — **UNCOVERED**
  - What it tests: Trimmed 3d surface collection clearing
  - Repair action: Clear myTrimmed3dSec sequence
  - Suggested fixture: defect mentioning 'myTrimmed3dSec->Clear()'
- **Branch 38** @ line 98 — *collection_clear* — **UNCOVERED**
  - What it tests: Offset curve collection clearing
  - Repair action: Clear myOffsetCurveSec sequence
  - Suggested fixture: defect mentioning 'myOffsetCurveSec->Clear()'
- **Branch 39** @ line 99 — *collection_clear* — **UNCOVERED**
  - What it tests: Trimmed 2d surface collection clearing
  - Repair action: Clear myTrimmed2dSec sequence
  - Suggested fixture: defect mentioning 'myTrimmed2dSec->Clear()'

#### `ShapeAnalysis_ShapeContents.Perform` — lines 113–358
(39 branches, 15 covered.)

- **Branch 1** @ line 120 — *shape_type_solid_enum* — **UNCOVERED**
  - What it tests: Iterate all solids in shape
  - Repair action: Process each solid with shell counting
  - Suggested fixture: defect mentioning 'TopAbs_SOLID'
- **Branch 2** @ line 126 — *shape_type_shell_within_solid* — **UNCOVERED**
  - What it tests: Count shells within each solid
  - Repair action: Increment nbs per shell
  - Suggested fixture: defect mentioning 'TopAbs_SHELL'
- **Branch 3** @ line 130 — *topology_solid_with_voids* — **UNCOVERED**
  - What it tests: Solids with multiple shells (voids)
  - Repair action: Increment myNbSolidsWithVoids when nbs > 1
  - Suggested fixture: defect mentioning 'nbs > 1'
- **Branch 4** @ line 142 — *shape_type_shell_enum* — COVERED by: a002, a003, a004, a006, a007, a009, a014, a017 (+748 more)
  - What it tests: Iterate all top-level shells
  - Repair action: Process each shell independently
- **Branch 5** @ line 148 — *shape_type_face_within_shell* — COVERED by: a017, a022, a026, a064, a102, ad004, ad015, ad026 (+262 more)
  - What it tests: Count faces within each shell
  - Repair action: Increment nbfaceshell per face
- **Branch 6** @ line 163 — *shape_type_face_enum* — COVERED by: a002, a003, a004, a006, a007, a009, a014, a017 (+748 more)
  - What it tests: Iterate all faces in shape
  - Repair action: Analyze each face for defects
- **Branch 7** @ line 171 — *surface_type_trimmed* — **UNCOVERED**
  - What it tests: Check for RectangularTrimmedSurface wrapper
  - Repair action: Increment myNbTrimSurf and unwrap basis
  - Suggested fixture: defect mentioning 'Geom_RectangularTrimmedSurface', 'trsu'
- **Branch 8** @ line 180 — *surface_continuity_c0* — **UNCOVERED**
  - What it tests: Surface C0 discontinuity (at least in U or V)
  - Repair action: Increment myNbC0Surfaces
  - Suggested fixture: defect mentioning 'IsCNu', 'IsCNv'
- **Branch 9** @ line 185 — *surface_type_bspline* — **UNCOVERED**
  - What it tests: BSpline surface type detection
  - Repair action: Increment myNbBSplibeSurf
  - Suggested fixture: defect mentioning 'Geom_BSplineSurface', 'bsps'
- **Branch 10** @ line 189 — *surface_bspline_pole_count_excessive* — COVERED by: ls032
  - What it tests: BSpline with > 8192 total poles (NbUPoles * NbVPoles)
  - Repair action: Increment myNbBigSplines and optionally collect
- **Branch 11** @ line 192 — *collection_mode_bigspline* — **UNCOVERED**
  - What it tests: BigSplineMode flag check for collection
  - Repair action: Append face to myBigSplineSec if enabled
  - Suggested fixture: defect mentioning 'myBigSplineMode'
- **Branch 12** @ line 198 — *surface_type_elementary* — COVERED by: a005, a017, a020, a025, a036, a064, a066, a068 (+171 more)
  - What it tests: Elementary surface (e.g., plane, cylinder) detection
  - Repair action: Check orientation for indirect surfaces
- **Branch 13** @ line 201 — *surface_orientation_indirect* — **UNCOVERED**
  - What it tests: Elementary surface with non-direct (inverse) orientation
  - Repair action: Increment myNbIndirectSurf and optionally collect
  - Suggested fixture: defect mentioning 'Direct()'
- **Branch 14** @ line 204 — *collection_mode_indirect* — **UNCOVERED**
  - What it tests: IndirectMode flag check for collection
  - Repair action: Append face to myIndirectSec if enabled
  - Suggested fixture: defect mentioning 'myIndirectMode'
- **Branch 15** @ line 210 — *surface_type_offset* — COVERED by: gn021
  - What it tests: Offset surface type detection
  - Repair action: Increment myNbOffsetSurf and optionally collect
- **Branch 16** @ line 213 — *collection_mode_offsetsurf* — **UNCOVERED**
  - What it tests: OffsetSurfaceMode flag check
  - Repair action: Append face to myOffsetSurfaceSec if enabled
  - Suggested fixture: defect mentioning 'myOffsetSurfaceMode'
- **Branch 17** @ line 218 — *surface_type_bezier* — **UNCOVERED**
  - What it tests: Bezier surface type (else branch after offset)
  - Repair action: Increment myNbBezierSurf
  - Suggested fixture: defect mentioning 'Geom_BezierSurface'
- **Branch 18** @ line 224 — *shape_type_wire_within_face* — COVERED by: a002, a003, a013, a014, a017, a018, a019, a020 (+747 more)
  - What it tests: Iterate all wires in current face
  - Repair action: Count and analyze wires
- **Branch 19** @ line 229 — *shape_type_edge_within_wire* — COVERED by: a103, ad015, ad045, ad050, ad086, ad099, ad101, ad102 (+214 more)
  - What it tests: Iterate all edges in current wire
  - Repair action: Check for seams, curves, p-curves
- **Branch 20** @ line 233 — *edge_topology_seam* — COVERED by: ad086, tsh007
  - What it tests: Edge is seam (closed with respect to face)
  - Repair action: Increment nbseam counter
- **Branch 21** @ line 237 — *edge_curve_3d_presence* — COVERED by: a081, pmi022, pmi023, pmi024, pmi090
  - What it tests: 3D curve exists on edge
  - Repair action: Check for trimmed 3D curve type
- **Branch 22** @ line 240 — *curve_3d_type_trimmed* — **UNCOVERED**
  - What it tests: 3D curve is TrimmedCurve wrapper
  - Repair action: Increment myNbTrimmedCurve3d and optionally collect
  - Suggested fixture: defect mentioning 'Geom_TrimmedCurve'
- **Branch 23** @ line 243 — *collection_mode_trimmed3d* — **UNCOVERED**
  - What it tests: Trimmed3dMode flag check for collection
  - Repair action: Append face to myTrimmed3dSec if enabled
  - Suggested fixture: defect mentioning 'myTrimmed3dMode'
- **Branch 24** @ line 249 — *edge_curve_2d_absence* — **UNCOVERED**
  - What it tests: P-curve (2D curve) missing on edge
  - Repair action: Increment myNbNoPCurve
  - Suggested fixture: defect mentioning 'BRep_Tool::CurveOnSurface', 'c2d.IsNull()'
- **Branch 25** @ line 254 — *curve_2d_type_offset* — **UNCOVERED**
  - What it tests: P-curve is OffsetCurve wrapper (else-if after IsNull)
  - Repair action: Increment myNbOffsetCurves and optionally collect
  - Suggested fixture: defect mentioning 'Geom2d_OffsetCurve'
- **Branch 26** @ line 257 — *collection_mode_offsetcurve* — **UNCOVERED**
  - What it tests: OffsetCurveMode flag check
  - Repair action: Append face to myOffsetCurveSec if enabled
  - Suggested fixture: defect mentioning 'myOffsetCurveMode'
- **Branch 27** @ line 262 — *curve_2d_type_trimmed* — **UNCOVERED**
  - What it tests: P-curve is TrimmedCurve wrapper (else-if)
  - Repair action: Increment myNbTrimmedCurve2d and optionally collect
  - Suggested fixture: defect mentioning 'Geom2d_TrimmedCurve'
- **Branch 28** @ line 265 — *collection_mode_trimmed2d* — **UNCOVERED**
  - What it tests: Trimmed2dMode flag check for collection
  - Repair action: Append face to myTrimmed2dSec if enabled
  - Suggested fixture: defect mentioning 'myTrimmed2dMode'
- **Branch 29** @ line 271 — *wire_seam_maximum_tracking* — **UNCOVERED**
  - What it tests: Track maximum seams per wire
  - Repair action: Update maxseam if nbseam > maxseam
  - Suggested fixture: defect mentioning 'maxseam = nbseam'
- **Branch 30** @ line 276 — *wire_seam_single* — **UNCOVERED**
  - What it tests: Wire has exactly one seam
  - Repair action: Increment myNbWireWitnSeam
  - Suggested fixture: defect mentioning 'maxseam == 1'
- **Branch 31** @ line 280 — *wire_seam_multiple* — **UNCOVERED**
  - What it tests: Wire has multiple seams (> 1)
  - Repair action: Increment myNbWireWithSevSeams
  - Suggested fixture: defect mentioning 'maxseam > 1'
- **Branch 32** @ line 284 — *face_wire_multiplicity* — **UNCOVERED**
  - What it tests: Face has multiple wires (> 1)
  - Repair action: Increment myNbFaceWithSevWires
  - Suggested fixture: defect mentioning 'nbwires > 1'
- **Branch 33** @ line 305 — *shape_type_edge_enum_free* — COVERED by: tsh018
  - What it tests: Iterate free edges (not contained in faces)
  - Repair action: Process each free edge for offset curves
- **Branch 34** @ line 314 — *curve_3d_type_offset_free* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+580 more)
  - What it tests: Free edge has 3D offset curve
  - Repair action: Increment myNbOffsetCurves and optionally collect
- **Branch 35** @ line 317 — *collection_mode_offsetcurve_free* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+580 more)
  - What it tests: OffsetCurveMode flag for free edge collection
  - Repair action: Append edge to myOffsetCurveSec if enabled
- **Branch 36** @ line 322 — *curve_3d_continuity_c0* — **UNCOVERED**
  - What it tests: 3D curve on free edge is C0 (not C1)
  - Repair action: Increment myNbC0Curves
  - Suggested fixture: defect mentioning 'IsCN(1)'
- **Branch 37** @ line 330 — *shape_type_vertex_enum* — **UNCOVERED**
  - What it tests: Iterate all vertices in shape
  - Repair action: Count vertices and track shared
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX'
- **Branch 38** @ line 340 — *shape_type_edge_free_enum* — COVERED by: tsh018
  - What it tests: Iterate free edges (not in any face) by topology
  - Repair action: Count and dedup via mapsh
- **Branch 39** @ line 350 — *shape_type_wire_free_enum* — COVERED by: tsh018
  - What it tests: Iterate free wires (not in any face)
  - Repair action: Count and dedup via mapsh


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_Surface.cxx`

17 methods, 147 branches, 18 covered.

#### `ShapeAnalysis_Surface.ComputeBoundIsos` — lines 613–623
(6 branches, 1 covered.)

- **Branch 1** @ line 614 — *cache_check* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Boundary isocurves already cached
  - Repair action: Return early if myIsos flag is set
- **Branch 2** @ line 618 — *cache_initialization* — **UNCOVERED**
  - What it tests: Mark cache as valid before computing
  - Repair action: Set myIsos=true to prevent recomputation
  - Suggested fixture: defect mentioning 'myIsos = true'
- **Branch 3** @ line 619 — *u_boundary_iso_u_first* — **UNCOVERED**
  - What it tests: Compute U-isocurve at first U boundary
  - Repair action: Call ComputeIso(mySurf, true, myUF)
  - Suggested fixture: defect mentioning 'myIsoUF = ComputeIso(mySurf, true, myUF)'
- **Branch 4** @ line 620 — *u_boundary_iso_u_last* — **UNCOVERED**
  - What it tests: Compute U-isocurve at last U boundary
  - Repair action: Call ComputeIso(mySurf, true, myUL)
  - Suggested fixture: defect mentioning 'myIsoUL = ComputeIso(mySurf, true, myUL)'
- **Branch 5** @ line 621 — *v_boundary_iso_v_first* — **UNCOVERED**
  - What it tests: Compute V-isocurve at first V boundary
  - Repair action: Call ComputeIso(mySurf, false, myVF)
  - Suggested fixture: defect mentioning 'myIsoVF = ComputeIso(mySurf, false, myVF)'
- **Branch 6** @ line 622 — *v_boundary_iso_v_last* — **UNCOVERED**
  - What it tests: Compute V-isocurve at last V boundary
  - Repair action: Call ComputeIso(mySurf, false, myVL)
  - Suggested fixture: defect mentioning 'myIsoVL = ComputeIso(mySurf, false, myVL)'

#### `ShapeAnalysis_Surface.ComputeSingularities` — lines 181–294
(9 branches, 1 covered.)

- **Branch 1** @ line 184 — *singularity_cache_guard* — **UNCOVERED**
  - What it tests: Skip recomputation if singularities already cached
  - Repair action: early return when myNbDeg >= 0 (already computed)
  - Suggested fixture: defect mentioning 'if (myNbDeg >= 0)', 'return;'
- **Branch 2** @ line 190 — *null_surface_guard* — **UNCOVERED**
  - What it tests: Null surface protection before analysis
  - Repair action: return silently if surface is null
  - Suggested fixture: defect mentioning 'if (mySurf.IsNull())'
- **Branch 3** @ line 201 — *conic_surface_singularity* — **UNCOVERED**
  - What it tests: Detect and characterize conical surface singularities (apex)
  - Repair action: compute apex position and degeneration line for cone
  - Suggested fixture: defect mentioning 'Geom_ConicalSurface', 'vApex = -conicS->RefRadius'
- **Branch 4** @ line 214 — *toroidal_surface_singularities* — **UNCOVERED**
  - What it tests: Detect toroidal surface singular curves (two poles if inner radius < outer)
  - Repair action: compute both poles or single pole depending on radius ratio
  - Suggested fixture: defect mentioning 'Geom_ToroidalSurface', 'std::acos(std::min(1., majorR / minorR))'
- **Branch 5** @ line 231 — *toroid_branch_count* — **UNCOVERED**
  - What it tests: Conditional pole count for toroid: 1 if majorR > minorR, else 2
  - Repair action: set myNbDeg=1 or 2 based on radius relationship
  - Suggested fixture: defect mentioning 'majorR > minorR ? 1 : 2'
- **Branch 6** @ line 233 — *spherical_surface_singularities* — **UNCOVERED**
  - What it tests: Detect spherical surface polar singularities (north and south poles)
  - Repair action: compute both poles at v-limits with zero precision
  - Suggested fixture: defect mentioning 'Geom_SphericalSurface', 'sv2', 'sv1'
- **Branch 7** @ line 247 — *bounded_surface_boundary_singularities* — COVERED by: gn021
  - What it tests: Generic handling of bounded, revolution, and offset surfaces
  - Repair action: compute 4 pseudo-singular points at boundary curves (edges)
- **Branch 8** @ line 277 — *corner_distance_computation* — **UNCOVERED**
  - What it tests: Compute precision estimate from corner distances for generic bounded surfaces
  - Repair action: measure max distance between edge midpoint and corners
  - Suggested fixture: defect mentioning 'Corner1.Distance(Corner2)', 'myP3d[i].Distance(Corner'
- **Branch 9** @ line 293 — *singularity_sorting* — **UNCOVERED**
  - What it tests: Sort computed singularities for consistent ordering
  - Repair action: invoke SortSingularities() after populating arrays
  - Suggested fixture: defect mentioning 'SortSingularities()'

#### `ShapeAnalysis_Surface.DegeneratedValues` — lines 374–413
(7 branches, 0 covered.)

- **Branch 1** @ line 382 — *lazy_singularity_init* — **UNCOVERED**
  - What it tests: Trigger singularity computation if not yet cached
  - Repair action: call ComputeSingularities() if myNbDeg < 0
  - Suggested fixture: defect mentioning 'if (myNbDeg < 0)', 'ComputeSingularities()'
- **Branch 2** @ line 390 — *singularity_precision_filter* — **UNCOVERED**
  - What it tests: Skip singularities with precision exceeding input tolerance
  - Repair action: loop condition: && myPreci[i] <= preci (stop when precision too coarse)
  - Suggested fixture: defect mentioning 'myPreci[i] <= preci'
- **Branch 3** @ line 392 — *distance_to_singularity* — **UNCOVERED**
  - What it tests: Compute 3D distance from input point to singularity location
  - Repair action: compute myGap = myP3d[i].Distance(P3d)
  - Suggested fixture: defect mentioning 'myGap = myP3d[i].Distance(P3d)'
- **Branch 4** @ line 394 — *proximity_check* — **UNCOVERED**
  - What it tests: Determine if input point is near current singularity
  - Repair action: check if myGap <= preci (within tolerance)
  - Suggested fixture: defect mentioning 'if (myGap <= preci)'
- **Branch 5** @ line 396 — *minimum_distance_tracking* — **UNCOVERED**
  - What it tests: Track singular point with smallest gap from input
  - Repair action: update indMin and gapMin if current gap is smaller
  - Suggested fixture: defect mentioning 'if (gapMin > myGap)', 'indMin = i'
- **Branch 6** @ line 403 — *singularity_found_check* — **UNCOVERED**
  - What it tests: Verify at least one singularity matched within tolerance
  - Repair action: return false if indMin remains -1 (no match found)
  - Suggested fixture: defect mentioning 'if (indMin >= 0)'
- **Branch 7** @ line 405 — *singular_parameter_extraction* — **UNCOVERED**
  - What it tests: Extract parametric bounds of matched singularity
  - Repair action: copy firstP2d, lastP2d, firstPar, lastPar from arrays at indMin
  - Suggested fixture: defect mentioning 'firstP2d = myFirstP2d[indMin]', 'lastPar = myLastPar[indMin]'

#### `ShapeAnalysis_Surface.Init` — lines 124–150
(5 branches, 0 covered.)

- **Branch 1** @ line 126 — *idempotent_init* — **UNCOVERED**
  - What it tests: Surface object identity check — returns early if same surface already set
  - Repair action: skip initialization if surface already assigned
  - Suggested fixture: defect mentioning 'if (mySurf == theSurface)'
- **Branch 2** @ line 131 — *null_surface_guard* — **UNCOVERED**
  - What it tests: Null-reference protection — prevents crash when surface is null
  - Repair action: emit warning and early return on null input
  - Suggested fixture: defect mentioning 'if (theSurface.IsNull())', 'Bug 33895'
- **Branch 3** @ line 137 — *state_reset* — **UNCOVERED**
  - What it tests: Reset singularity cache on new surface assignment
  - Repair action: set myNbDeg=-1 to force recomputation of singularities
  - Suggested fixture: defect mentioning 'myNbDeg = -1'
- **Branch 4** @ line 142 — *surface_bounds_extraction* — **UNCOVERED**
  - What it tests: Extraction of parametric bounds (U/V ranges) from surface
  - Repair action: compute myUF, myUL, myVF, myVL from surface geometry
  - Suggested fixture: defect mentioning 'mySurf->Bounds(myUF, myUL, myVF, myVL)'
- **Branch 5** @ line 143 — *adaptor_factory* — **UNCOVERED**
  - What it tests: Geometric adaptor creation for surface evaluation
  - Repair action: construct GeomAdaptor_Surface wrapper for later queries
  - Suggested fixture: defect mentioning 'myAdSur = new GeomAdaptor_Surface(mySurf)'

#### `ShapeAnalysis_Surface.IsDegenerated` — lines 553–575
(6 branches, 2 covered.)

- **Branch 1** @ line 554 — *surface_evaluation* — **UNCOVERED**
  - What it tests: Evaluate 3D points from 2D parameters
  - Repair action: Call Value() for endpoints and midpoint
  - Suggested fixture: defect mentioning 'Value(p2d1)', 'Value(p2d2)', 'Value(0.5'
- **Branch 2** @ line 557 — *3d_distance_check* — COVERED by: in014
  - What it tests: Check if 3D curve span exceeds tolerance
  - Repair action: Return false if max3d > tol (not degenerate)
- **Branch 3** @ line 564 — *resolution_sanity_check* — **UNCOVERED**
  - What it tests: Verify surface resolution is well-defined
  - Repair action: Return false if resolution is zero or confused
  - Suggested fixture: defect mentioning 'RU = SA.UResolution', 'RV = SA.VResolution', 'if (RU < Precision'
- **Branch 4** @ line 571 — *normalized_parameter_distance* — COVERED by: le021, twi064
  - What it tests: Compare 2D parameter distance normalized by resolution
  - Repair action: Compute du/RU and dv/RV ratios
- **Branch 5** @ line 573 — *ratio_based_threshold* — **UNCOVERED**
  - What it tests: Apply ratio factor to tolerance for degeneracy judgment
  - Repair action: Scale max3d by ratio parameter
  - Suggested fixture: defect mentioning 'max3d *= ratio'
- **Branch 6** @ line 574 — *parametric_vs_geometric* — **UNCOVERED**
  - What it tests: Degenerate if normalized parameter distance exceeds geometric threshold
  - Repair action: Return true if du²+dv² > (max3d·ratio)²
  - Suggested fixture: defect mentioning 'return du * du + dv * dv > max3d * max3d'

#### `ShapeAnalysis_Surface.IsUClosed` — lines 662–864
(21 branches, 0 covered.)

- **Branch 1** @ line 663 — *precision_normalization* — **UNCOVERED**
  - What it tests: Precision value is reasonable
  - Repair action: Use minimum of input precision and Precision::Confusion()
  - Suggested fixture: defect mentioning 'prec = std::max(preci, Precision::Confusion())'
- **Branch 2** @ line 665 — *cache_check* — **UNCOVERED**
  - What it tests: Closedness value already computed (myUCloseVal >= 0)
  - Repair action: Skip computation if cached
  - Suggested fixture: defect mentioning 'if (myUCloseVal < 0)'
- **Branch 3** @ line 674 — *native_closure* — **UNCOVERED**
  - What it tests: Surface is natively U-closed
  - Repair action: Set distances to zero and return true
  - Suggested fixture: defect mentioning 'if (mySurf->IsUClosed())', 'myUCloseVal = 0.', 'return true'
- **Branch 4** @ line 691 — *surface_type_dispatch* — **UNCOVERED**
  - What it tests: Route analysis based on surface type
  - Repair action: Use type-specific algorithms (Plane, Extrusion, BSpline, etc.)
  - Suggested fixture: defect mentioning 'switch (surftype)'
- **Branch 5** @ line 693 — *plane_surface* — **UNCOVERED**
  - What it tests: Planar surface never U-closes
  - Repair action: Set myUCloseVal to RealLast() (infinite distance)
  - Suggested fixture: defect mentioning 'case GeomAbs_Plane:', 'myUCloseVal = RealLast()'
- **Branch 6** @ line 697 — *surface_of_extrusion* — **UNCOVERED**
  - What it tests: Linear extrusion: U-closure matches basis curve endpoints
  - Repair action: Compute closure from basis curve first and last points
  - Suggested fixture: defect mentioning 'case GeomAbs_SurfaceOfExtrusion', 'crv->FirstParameter()', 'crv->LastParameter()'
- **Branch 7** @ line 705 — *infinite_parameter_range* — **UNCOVERED**
  - What it tests: Basis curve has infinite parameter range
  - Repair action: Set myUCloseVal to RealLast() (undefined closure)
  - Suggested fixture: defect mentioning 'if (!Precision::IsInfinite(f) && !Precision::IsInfinite(l))'
- **Branch 8** @ line 719 — *bspline_surface* — **UNCOVERED**
  - What it tests: B-spline surface: check periodicity and pole arrangement
  - Repair action: Multiple analysis paths based on periodicity, rationality, multiplicity
  - Suggested fixture: defect mentioning 'case GeomAbs_BSplineSurface'
- **Branch 9** @ line 723 — *bspline_periodic* — **UNCOVERED**
  - What it tests: B-spline is U-periodic
  - Repair action: Set closure to 0 (perfect closure)
  - Suggested fixture: defect mentioning 'if (bs->IsUPeriodic())', 'myUCloseVal = 0'
- **Branch 10** @ line 728 — *bspline_too_few_poles* — **UNCOVERED**
  - What it tests: B-spline has fewer than 3 U-poles
  - Repair action: Set to RealLast() (degenerate/non-closeable)
  - Suggested fixture: defect mentioning 'else if (nbup < 3)', 'myUCloseVal = RealLast()'
- **Branch 11** @ line 732 — *bspline_rational_or_boundary_multiplicity* — **UNCOVERED**
  - What it tests: B-spline is rational or boundary knot multiplicity ≠ degree+1
  - Repair action: Sample multiple V-knots and find max closure distance
  - Suggested fixture: defect mentioning 'else if (bs->IsURational()', 'UMultiplicity', 'UDegree() + 1'
- **Branch 12** @ line 746 — *bspline_knot_sampling* — **UNCOVERED**
  - What it tests: Iterate through V-knots to find maximum U-closure distance
  - Repair action: Evaluate at multiple V-parameter points, track max and min distances
  - Suggested fixture: defect mentioning 'for (int i = 2; i <= nbvk', 'bs->VKnot(i'
- **Branch 13** @ line 752 — *bspline_max_distance_update* — **UNCOVERED**
  - What it tests: Current sample distance exceeds cached maximum
  - Repair action: Update myUCloseVal and anUmidVal (midpoint distance)
  - Suggested fixture: defect mentioning 'if (aDist > myUCloseVal)', 'anUmidVal'
- **Branch 14** @ line 766 — *bspline_normal_configuration* — **UNCOVERED**
  - What it tests: B-spline has normal boundary multiplicity (degree+1)
  - Repair action: Sample poles to find closure distance, more efficient than curves
  - Suggested fixture: defect mentioning 'else {', 'nbup', 'nbvp'
- **Branch 15** @ line 769 — *bspline_pole_sampling* — **UNCOVERED**
  - What it tests: Compare U-boundary poles at each V-index
  - Repair action: Find max distance between Pole(1,i) and Pole(nbup,i)
  - Suggested fixture: defect mentioning 'bs->Pole(1, 1).SquareDistance(bs->Pole(nbup, 1))'
- **Branch 16** @ line 790 — *bezier_surface* — **UNCOVERED**
  - What it tests: Bezier surface: similar pole-based analysis
  - Repair action: Sample poles at U boundaries, find max closure distance
  - Suggested fixture: defect mentioning 'case GeomAbs_BezierSurface'
- **Branch 17** @ line 794 — *bezier_too_few_poles* — **UNCOVERED**
  - What it tests: Bezier has fewer than 3 U-poles
  - Repair action: Set to RealLast() (degenerate/non-closeable)
  - Suggested fixture: defect mentioning 'if (nbup < 3)', 'myUCloseVal = RealLast()'
- **Branch 18** @ line 822 — *other_surface_types* — **UNCOVERED**
  - What it tests: Generic surface (OtherSurface, Offset, RectangularTrimmed)
  - Repair action: Sample 101 points on V-parameter, evaluate at U boundaries
  - Suggested fixture: defect mentioning 'default:', 'nbpoints = 101'
- **Branch 19** @ line 831 — *generic_surface_sampling* — **UNCOVERED**
  - What it tests: Iterate through V-parameter samples
  - Repair action: Find max and min U-closure distances across samples
  - Suggested fixture: defect mentioning 'for (int i = 1; i < nbpoints', 'vparam = vf + (vl - vf)'
- **Branch 20** @ line 857 — *midpoint_sanity_check* — **UNCOVERED**
  - What it tests: Verify that closure is not contradicted by midpoint distance
  - Repair action: If midpoint distance is high relative to endpoint distance, declare not closed
  - Suggested fixture: defect mentioning 'if (anUmidVal > 0. && myUCloseVal > sqrt(anUmidVal))', 'myUCloseVal = RealLast()'
- **Branch 21** @ line 863 — *tolerance_comparison* — **UNCOVERED**
  - What it tests: Final comparison of closure distance against tolerance
  - Repair action: Return true if myUCloseVal <= prec
  - Suggested fixture: defect mentioning 'return (myUCloseVal <= prec)'

#### `ShapeAnalysis_Surface.IsVClosed` — lines 869–1059
(12 branches, 1 covered.)

- **Branch 1** @ line 872 — *cached_closure_check* — **UNCOVERED**
  - What it tests: myVCloseVal < 0 guards first computation vs cached result
  - Repair action: skip recomputation if already cached
  - Suggested fixture: defect mentioning 'myVCloseVal < 0', 'caching strategy'
- **Branch 2** @ line 881 — *native_periodic_surface* — **UNCOVERED**
  - What it tests: surface is natively V-periodic (plane, cylinder, etc.)
  - Repair action: return true immediately, set gap=0
  - Suggested fixture: defect mentioning 'mySurf->IsVClosed()', 'periodic detection'
- **Branch 3** @ line 893 — *trimmed_surface_override* — **UNCOVERED**
  - What it tests: RectangularTrimmedSurface should be treated as other surface type
  - Repair action: force OtherSurface type path analysis
  - Suggested fixture: defect mentioning 'RectangularTrimmedSurface', 'type override'
- **Branch 4** @ line 900 — *geometric_closure_impossible* — **UNCOVERED**
  - What it tests: Plane/Cone/Cylinder/Sphere/Extrusion cannot close in V
  - Repair action: mark closure value as RealLast (impossible)
  - Suggested fixture: defect mentioning 'GeomAbs_Plane', 'closure impossible'
- **Branch 5** @ line 908 — *revolution_surface_closure* — **UNCOVERED**
  - What it tests: SurfaceOfRevolution closure depends on basis curve endpoints
  - Repair action: compute gap from basis curve endpoint distance
  - Suggested fixture: defect mentioning 'SurfaceOfRevolution', 'BasisCurve'
- **Branch 6** @ line 921 — *bspline_vpperiodic* — **UNCOVERED**
  - What it tests: BSpline with V-periodic flag
  - Repair action: set closure gap to 0, skip delta computation
  - Suggested fixture: defect mentioning 'IsVPeriodic()', 'bspline periodic'
- **Branch 7** @ line 926 — *bspline_insufficient_poles* — **UNCOVERED**
  - What it tests: BSpline has < 3 V-poles (degenerate)
  - Repair action: mark closure as impossible (RealLast)
  - Suggested fixture: defect mentioning 'nbvp < 3', 'pole count check'
- **Branch 8** @ line 930 — *bspline_rational_or_openend* — **UNCOVERED**
  - What it tests: BSpline is rational or has open ends (not C2 continuous)
  - Repair action: sample at knot positions using surface evaluation
  - Suggested fixture: defect mentioning 'IsVRational', 'VMultiplicity'
- **Branch 9** @ line 962 — *bspline_clamped_continuous* — **UNCOVERED**
  - What it tests: BSpline is clamped and continuous (C2)
  - Repair action: directly sample pole endpoints instead of evaluating
  - Suggested fixture: defect mentioning 'bs->Pole', 'pole sampling'
- **Branch 10** @ line 985 — *bezier_surface_closure* — **UNCOVERED**
  - What it tests: Bezier surface with < 3 poles or normal pole distribution
  - Repair action: sample endpoints vs interior poles
  - Suggested fixture: defect mentioning 'GeomAbs_BezierSurface', 'nbvp < 3'
- **Branch 11** @ line 1017 — *generic_surface_adaptive_sampling* — COVERED by: gp008
  - What it tests: Trimmed/Offset/other surfaces requiring explicit sampling
  - Repair action: sample 101 U-parameter values to find maximum V-closure gap
- **Branch 12** @ line 1052 — *closure_validity_midpoint_check* — **UNCOVERED**
  - What it tests: midpoint distance suggests closure is false positive
  - Repair action: reject closure if midpoint distance is too large
  - Suggested fixture: defect mentioning 'aVmidVal > 0', 'midpoint validation'

#### `ShapeAnalysis_Surface.NextValueOfUV` — lines 1168–1241
(5 branches, 2 covered.)

- **Branch 1** @ line 1181 — *bspline_c0_discontinuity_u* — COVERED by: gs048
  - What it tests: BSpline has C0 discontinuity (knot) near previous U parameter
  - Repair action: skip Newton and use full ValueOfUV (restart search)
- **Branch 2** @ line 1201 — *bspline_c0_discontinuity_v* — COVERED by: gs048
  - What it tests: BSpline has C0 discontinuity (knot) near previous V parameter
  - Repair action: skip Newton and use full ValueOfUV (restart search)
- **Branch 3** @ line 1218 — *newton_convergence_success* — **UNCOVERED**
  - What it tests: Newton converged (res != 0)
  - Repair action: check solution quality before returning
  - Suggested fixture: defect mentioning 'res != 0', 'newton success'
- **Branch 4** @ line 1221 — *low_quality_newton_solution* — **UNCOVERED**
  - What it tests: res == 2 (ill-conditioned) or gap exceeds maxpreci
  - Repair action: try UVFromIso and compare against Newton result
  - Suggested fixture: defect mentioning 'res == 2', 'maxpreci check'
- **Branch 5** @ line 1237 — *fallback_full_projection* — **UNCOVERED**
  - What it tests: surface type not handled by Newton (default case)
  - Repair action: fall back to full ValueOfUV search
  - Suggested fixture: defect mentioning 'default: break', 'fallback projection'

#### `ShapeAnalysis_Surface.ProjectDegenerated` — lines 417–459
(7 branches, 1 covered.)

- **Branch 1** @ line 422 — *lazy_singularity_init* — **UNCOVERED**
  - What it tests: Trigger singularity computation if not yet cached
  - Repair action: call ComputeSingularities() if myNbDeg < 0
  - Suggested fixture: defect mentioning 'if (myNbDeg < 0)', 'ComputeSingularities()'
- **Branch 2** @ line 431 — *singularity_precision_filter* — **UNCOVERED**
  - What it tests: Skip singularities with precision exceeding input tolerance
  - Repair action: loop condition: && myPreci[i] <= preci
  - Suggested fixture: defect mentioning 'myPreci[i] <= preci'
- **Branch 3** @ line 433 — *squared_distance_to_singular_point* — **UNCOVERED**
  - What it tests: Use squared distance to singular point for efficiency
  - Repair action: compute gap2 = myP3d[i].SquareDistance(P3d)
  - Suggested fixture: defect mentioning 'gap2 = myP3d[i].SquareDistance(P3d)'
- **Branch 4** @ line 434 — *fallback_to_3d_projection* — **UNCOVERED**
  - What it tests: If initial 3D distance is too large, refine via surface projection
  - Repair action: recompute gap2 using projected 3D point if gap2 > preci²
  - Suggested fixture: defect mentioning 'if (gap2 > preci * preci)', 'myP3d[i].SquareDistance(Value(result))'
- **Branch 5** @ line 439 — *proximity_and_minimum_tracking* — **UNCOVERED**
  - What it tests: Track singular point with smallest squared distance within tolerance
  - Repair action: update indMin and gapMin if gap2 <= preci² and gap2 is smaller
  - Suggested fixture: defect mentioning 'if (gap2 <= preci * preci && gapMin > gap2)'
- **Branch 6** @ line 445 — *no_degeneration_found* — COVERED by: in014
  - What it tests: No singularity matched within tolerance
  - Repair action: return false if indMin remains negative
- **Branch 7** @ line 450 — *uiso_vs_viso_projection* — **UNCOVERED**
  - What it tests: Project onto correct coordinate based on singularity orientation
  - Repair action: set X (keep Y) if !myUIsoDeg, else set Y (keep X)
  - Suggested fixture: defect mentioning 'if (!myUIsoDeg[indMin])', 'result.SetX(neighbour.X())', 'result.SetY(neighbour.Y())'

#### `ShapeAnalysis_Surface.ProjectDegenerated.2` — lines 469–545
(9 branches, 2 covered.)

- **Branch 1** @ line 470 — *uninitialized_singularities* — **UNCOVERED**
  - What it tests: Singular points not yet computed (myNbDeg < 0)
  - Repair action: Lazy initialization via ComputeSingularities()
  - Suggested fixture: defect mentioning 'myNbDeg < 0', 'ComputeSingularities'
- **Branch 2** @ line 475 — *traversal_direction* — COVERED by: a007, a008, a024, a025, a028, a035, a036, a082 (+212 more)
  - What it tests: Traverse sequence forward or backward based on direct flag
  - Repair action: Set step=1 or step=-1 and adjust loop bounds
- **Branch 3** @ line 480 — *tolerance_filtering* — **UNCOVERED**
  - What it tests: Only consider singularities within precision tolerance
  - Repair action: Skip singularities with myPreci[i] > preci
  - Suggested fixture: defect mentioning 'myPreci[i] <= preci'
- **Branch 4** @ line 483 — *distance_thresholding* — **UNCOVERED**
  - What it tests: Exact vs approximate proximity to singularity
  - Repair action: Fallback to surface-evaluated distance if 3D gap exceeds tolerance
  - Suggested fixture: defect mentioning 'if (gap2 > prec2)', 'Value(pnt2d(j))'
- **Branch 5** @ line 493 — *no_singularity_found* — COVERED by: in014
  - What it tests: No singularity matched the tolerance criteria
  - Repair action: Return false; no degenerate edge detected
- **Branch 6** @ line 502 — *degenerate_extent_detection* — **UNCOVERED**
  - What it tests: Find extent of degenerate region within point sequence
  - Repair action: Loop until gap exceeds tolerance, then break
  - Suggested fixture: defect mentioning 'for (k = j + step', 'myP3d[indMin].SquareDistance'
- **Branch 7** @ line 513 — *full_sequence_degenerate* — **UNCOVERED**
  - What it tests: Entire pcurve lies on singularity point
  - Repair action: Redistribute points evenly in non-degenerate parameter space
  - Suggested fixture: defect mentioning 'if (k < 1 || k > nbrPnt)', 'distribute evenly'
- **Branch 8** @ line 515 — *iso_direction_dispatch* — **UNCOVERED**
  - What it tests: Singularity is U-iso or V-iso degenerate
  - Repair action: Fix X coord (U-iso) or Y coord (V-iso) based on myUIsoDeg[indMin]
  - Suggested fixture: defect mentioning 'myUIsoDeg[indMin]', 'SetX', 'SetY'
- **Branch 9** @ line 533 — *partial_degenerate_fix* — **UNCOVERED**
  - What it tests: Partial degenerate: part of sequence on singularity
  - Repair action: Fix non-degenerate param for degenerate portion, preserve k point
  - Suggested fixture: defect mentioning 'for (j = k - step', 'SetX(pk.X())', 'SetY(pk.Y())'

#### `ShapeAnalysis_Surface.Singularity` — lines 332–350
(3 branches, 1 covered.)

- **Branch 1** @ line 334 — *lazy_singularity_init* — **UNCOVERED**
  - What it tests: Trigger singularity computation if not yet cached
  - Repair action: call ComputeSingularities() if myNbDeg < 0
  - Suggested fixture: defect mentioning 'if (myNbDeg < 0)', 'ComputeSingularities()'
- **Branch 2** @ line 338 — *bounds_check* — COVERED by: in014
  - What it tests: Validate singularity index in valid range [1, myNbDeg]
  - Repair action: return false if num out of bounds
- **Branch 3** @ line 342 — *singularity_extraction* — **UNCOVERED**
  - What it tests: Retrieve cached singularity data for valid index
  - Repair action: copy arrays with 0-based offset: myP3d[num - 1], etc.
  - Suggested fixture: defect mentioning 'P3d = myP3d[num - 1]', 'preci = myPreci[num - 1]'

#### `ShapeAnalysis_Surface.SortSingularities` — lines 1846–1883
(11 branches, 3 covered.)

- **Branch 1** @ line 1847 — *selection_sort_outer_loop* — COVERED by: ad086, gp005, gs006, p023, ps002, ps010, ps015, tfa003 (+7 more)
  - What it tests: outer loop iterates through singularity array
  - Repair action: find minimum precision in remaining array
- **Branch 2** @ line 1851 — *selection_sort_inner_loop* — COVERED by: ad086, ps002, tfa055, tfa056, tfa062, twi009, twi024, twi044
  - What it tests: inner loop searches for minimum in subarray
  - Repair action: compare precisions to find minimum
- **Branch 3** @ line 1853 — *precision_comparison* — **UNCOVERED**
  - What it tests: current minimum vs candidate precision
  - Repair action: update minimum if candidate is smaller
  - Suggested fixture: defect mentioning 'minPreci > myPreci[j]', 'precision min'
- **Branch 4** @ line 1859 — *swap_condition* — **UNCOVERED**
  - What it tests: minimum element differs from current position
  - Repair action: swap singularity data if minimum found elsewhere
  - Suggested fixture: defect mentioning 'minIndex != i', 'swap condition'
- **Branch 5** @ line 1861 — *precision_swap* — **UNCOVERED**
  - What it tests: exchange precision values between positions
  - Repair action: reorder precisions array
  - Suggested fixture: defect mentioning 'myPreci[minIndex] = myPreci[i]', 'precision swap'
- **Branch 6** @ line 1863 — *point3d_swap* — **UNCOVERED**
  - What it tests: exchange 3D point coordinates between positions
  - Repair action: reorder 3D singularity points
  - Suggested fixture: defect mentioning 'gp_Pnt tmpP3d = myP3d', '3D point swap'
- **Branch 7** @ line 1866 — *point2d_start_swap* — **UNCOVERED**
  - What it tests: exchange first 2D parameters between positions
  - Repair action: reorder first 2D points (edge start)
  - Suggested fixture: defect mentioning 'myFirstP2d[minIndex]', '2D start swap'
- **Branch 8** @ line 1869 — *point2d_end_swap* — **UNCOVERED**
  - What it tests: exchange last 2D parameters between positions
  - Repair action: reorder last 2D points (edge end)
  - Suggested fixture: defect mentioning 'myLastP2d[minIndex]', '2D end swap'
- **Branch 9** @ line 1872 — *parameter_start_swap* — **UNCOVERED**
  - What it tests: exchange first curve parameter between positions
  - Repair action: reorder first parameters
  - Suggested fixture: defect mentioning 'myFirstPar[minIndex]', 'param start swap'
- **Branch 10** @ line 1875 — *parameter_end_swap* — **UNCOVERED**
  - What it tests: exchange last curve parameter between positions
  - Repair action: reorder last parameters
  - Suggested fixture: defect mentioning 'myLastPar[minIndex]', 'param end swap'
- **Branch 11** @ line 1878 — *isodeg_flag_swap* — COVERED by: ps014
  - What it tests: exchange U-isoline degeneracy flag between positions
  - Repair action: reorder degeneracy classification

#### `ShapeAnalysis_Surface.SurfaceNewton` — lines 1069–1157
(6 branches, 0 covered.)

- **Branch 1** @ line 1093 — *degenerate_surface_normal* — **UNCOVERED**
  - What it tests: surface normal has zero or infinite magnitude
  - Repair action: break iteration; fall back to standard projection
  - Suggested fixture: defect mentioning 'nrm2 < 1e-10', 'degenerate normal'
- **Branch 2** @ line 1104 — *singular_hessian_matrix* — **UNCOVERED**
  - What it tests: discriminant D is near zero (singular Hessian)
  - Repair action: break Newton iteration; surface is locally singular
  - Suggested fixture: defect mentioning 'fabs(D) < 1e-10', 'singular hessian'
- **Branch 3** @ line 1115 — *step_out_of_bounds* — **UNCOVERED**
  - What it tests: Newton step leaves parameter domain
  - Repair action: terminate iteration (point escapes valid range)
  - Suggested fixture: defect mentioning 'U < UF || U > UL', 'bounds violation'
- **Branch 4** @ line 1135 — *divergence_detection* — **UNCOVERED**
  - What it tests: residual rs2 increased from first iteration
  - Repair action: terminate Newton (diverging)
  - Suggested fixture: defect mentioning 'rs2 > rsfirst', 'divergence guard'
- **Branch 5** @ line 1141 — *tolerance_validation* — **UNCOVERED**
  - What it tests: tangential component of residual exceeds tolerance
  - Repair action: terminate iteration; sufficient convergence achieved
  - Suggested fixture: defect mentioning 'rs2 - rsn * rsn / nrm2 > Tol2', 'convergence test'
- **Branch 6** @ line 1152 — *solution_quality_assessment* — **UNCOVERED**
  - What it tests: nrm2 relative to ru2*rv2 indicates ill-conditioned surface
  - Repair action: return 2 for low-quality solution, 1 for good solution
  - Suggested fixture: defect mentioning 'nrm2 < 0.01 * ru2 * rv2', 'quality flag'

#### `ShapeAnalysis_Surface.UIso` — lines 628–640
(3 branches, 0 covered.)

- **Branch 1** @ line 629 — *boundary_u_first_cache* — **UNCOVERED**
  - What it tests: Requested U-iso matches first U boundary
  - Repair action: Ensure cache is populated and return myIsoUF
  - Suggested fixture: defect mentioning 'if (U == myUF)', 'ComputeBoundIsos()', 'return myIsoUF'
- **Branch 2** @ line 634 — *boundary_u_last_cache* — **UNCOVERED**
  - What it tests: Requested U-iso matches last U boundary
  - Repair action: Ensure cache is populated and return myIsoUL
  - Suggested fixture: defect mentioning 'if (U == myUL)', 'ComputeBoundIsos()', 'return myIsoUL'
- **Branch 3** @ line 639 — *interior_u_iso_compute* — **UNCOVERED**
  - What it tests: Requested U-iso is not at a boundary
  - Repair action: Compute fresh isocurve on demand without caching
  - Suggested fixture: defect mentioning 'return ComputeIso(mySurf, true, U)'

#### `ShapeAnalysis_Surface.UVFromIso` — lines 1523–1841
(17 branches, 1 covered.)

- **Branch 1** @ line 1538 — *already_near_solution* — **UNCOVERED**
  - What it tests: initial (U,V) is already within preci/10
  - Repair action: return early, no isoline search needed
  - Suggested fixture: defect mentioning 'theMin < preci / 10', 'early return'
- **Branch 2** @ line 1543 — *missing_isoline_cache* — **UNCOVERED**
  - What it tests: isolines not yet computed (myIsoUF etc. null)
  - Repair action: return current distance without refinement
  - Suggested fixture: defect mentioning 'IsNull()', 'cache missing'
- **Branch 3** @ line 1568 — *non_offset_surface_isoline_path* — **UNCOVERED**
  - What it tests: surface is not OffsetSurface (standard case)
  - Repair action: use geometric curves (myIsoUF/UL/VF/VL + UIso/VIso)
  - Suggested fixture: defect mentioning 'GetType() == GeomAbs_OffsetSurface', 'surface type branch'
- **Branch 4** @ line 1573 — *boundary_isoline_umin* — **UNCOVERED**
  - What it tests: U-boundary at UMin, Vmin-Vmax sweep
  - Repair action: project point onto UMin isoline
  - Suggested fixture: defect mentioning 'case 0: par = myUF', 'UMin boundary'
- **Branch 5** @ line 1578 — *boundary_isoline_umax* — **UNCOVERED**
  - What it tests: U-boundary at UMax, Vmin-Vmax sweep
  - Repair action: project point onto UMax isoline
  - Suggested fixture: defect mentioning 'case 1: par = myUL', 'UMax boundary'
- **Branch 6** @ line 1583 — *interior_isoline_u* — **UNCOVERED**
  - What it tests: interior isoline at current U parameter
  - Repair action: project point onto U isoline
  - Suggested fixture: defect mentioning 'case 2: par = U; iso = UIso', 'interior isoline'
- **Branch 7** @ line 1588 — *boundary_isoline_vmin* — **UNCOVERED**
  - What it tests: V-boundary at VMin, Umin-Umax sweep
  - Repair action: project point onto VMin isoline
  - Suggested fixture: defect mentioning 'case 3: par = myVF', 'VMin boundary'
- **Branch 8** @ line 1593 — *boundary_isoline_vmax* — **UNCOVERED**
  - What it tests: V-boundary at VMax, Umin-Umax sweep
  - Repair action: project point onto VMax isoline
  - Suggested fixture: defect mentioning 'case 4: par = myVL', 'VMax boundary'
- **Branch 9** @ line 1597 — *interior_isoline_v* — **UNCOVERED**
  - What it tests: interior isoline at current V parameter
  - Repair action: project point onto V isoline
  - Suggested fixture: defect mentioning 'case 5: par = V; iso = VIso', 'V interior'
- **Branch 10** @ line 1606 — *infinite_parameter_skip* — **UNCOVERED**
  - What it tests: isoline parameter is infinite
  - Repair action: skip isoline evaluation
  - Suggested fixture: defect mentioning 'IsInfinite(par)', 'infinite skip'
- **Branch 11** @ line 1608 — *bounding_box_prune* — **UNCOVERED**
  - What it tests: isoline bounding box far from target point
  - Repair action: skip isoline if distance > current theMin
  - Suggested fixture: defect mentioning 'anIsoBox->Distance > theMin', 'spatial prune'
- **Branch 12** @ line 1629 — *offset_surface_adaptor_path* — **UNCOVERED**
  - What it tests: surface is OffsetSurface (requires adaptor curves)
  - Repair action: use Adaptor3d_Curve and GeomAdaptor_Curve instead
  - Suggested fixture: defect mentioning 'else (OffsetSurface branch)', 'adaptor branch'
- **Branch 13** @ line 1691 — *iterative_refinement_non_offset* — **UNCOVERED**
  - What it tests: non-offset surface iterative U/V alternation
  - Repair action: alternate between U and V isolines up to 5 iterations
  - Suggested fixture: defect mentioning 'MaxIters = 5', 'iterative refinement'
- **Branch 14** @ line 1693 — *convergence_condition* — **UNCOVERED**
  - What it tests: (U,V) converged or max iterations or solution good
  - Repair action: continue iteration or exit based on condition
  - Suggested fixture: defect mentioning '((PrevU != UU)', 'convergence test'
- **Branch 15** @ line 1697 — *isoline_toggle_logic* — COVERED by: le011, lh012
  - What it tests: alternate between U and V isoline searches
  - Repair action: toggle UV boolean each iteration pair
- **Branch 16** @ line 1761 — *iterative_refinement_offset* — **UNCOVERED**
  - What it tests: OffsetSurface iterative U/V alternation with adaptors
  - Repair action: same iteration as non-offset but using ProjectAct
  - Suggested fixture: defect mentioning 'else (offset loop)', 'offset iterative'
- **Branch 17** @ line 1807 — *adaptor_projectact_fallback* — **UNCOVERED**
  - What it tests: second pass uses ProjectAct for robustness
  - Repair action: refine projection using active (robust) method
  - Suggested fixture: defect mentioning 'ProjectAct', 'robust projection'

#### `ShapeAnalysis_Surface.VIso` — lines 645–657
(3 branches, 0 covered.)

- **Branch 1** @ line 646 — *boundary_v_first_cache* — **UNCOVERED**
  - What it tests: Requested V-iso matches first V boundary
  - Repair action: Ensure cache is populated and return myIsoVF
  - Suggested fixture: defect mentioning 'if (V == myVF)', 'ComputeBoundIsos()', 'return myIsoVF'
- **Branch 2** @ line 651 — *boundary_v_last_cache* — **UNCOVERED**
  - What it tests: Requested V-iso matches last V boundary
  - Repair action: Ensure cache is populated and return myIsoVL
  - Suggested fixture: defect mentioning 'if (V == myVL)', 'ComputeBoundIsos()', 'return myIsoVL'
- **Branch 3** @ line 656 — *interior_v_iso_compute* — **UNCOVERED**
  - What it tests: Requested V-iso is not at a boundary
  - Repair action: Compute fresh isocurve on demand without caching
  - Suggested fixture: defect mentioning 'return ComputeIso(mySurf, false, V)'

#### `ShapeAnalysis_Surface.ValueOfUV` — lines 1246–1518
(17 branches, 3 covered.)

- **Branch 1** @ line 1260 — *exception_catch_wrapper* — **UNCOVERED**
  - What it tests: general exception handler for all geometry operations
  - Repair action: return fallback UV at domain center or zero
  - Suggested fixture: defect mentioning 'catch (Standard_Failure', 'exception handling'
- **Branch 2** @ line 1264 — *plane_projection* — **UNCOVERED**
  - What it tests: plane geometry, direct ElSLib parameters
  - Repair action: use plane parameters directly
  - Suggested fixture: defect mentioning 'GeomAbs_Plane', 'ElSLib::Parameters'
- **Branch 3** @ line 1269 — *cylinder_periodic_u* — COVERED by: gn014, n030
  - What it tests: cylinder with periodicity in U
  - Repair action: adjust U to domain via AdjustByPeriod
- **Branch 4** @ line 1275 — *cone_periodic_u* — **UNCOVERED**
  - What it tests: cone with periodicity in U
  - Repair action: adjust U to domain via AdjustByPeriod
  - Suggested fixture: defect mentioning 'GeomAbs_Cone', 'periodic adjustment'
- **Branch 5** @ line 1281 — *sphere_periodic_both* — **UNCOVERED**
  - What it tests: sphere (periodic in both U and V)
  - Repair action: use ElSLib parameters with periodic adjustment
  - Suggested fixture: defect mentioning 'GeomAbs_Sphere', 'ElSLib'
- **Branch 6** @ line 1287 — *torus_periodic_both* — **UNCOVERED**
  - What it tests: torus with double periodicity
  - Repair action: adjust both U and V to domain
  - Suggested fixture: defect mentioning 'GeomAbs_Torus', 'double periodicity'
- **Branch 7** @ line 1303 — *conic_extrusion_infinite_bounds* — **UNCOVERED**
  - What it tests: SurfaceOfExtrusion with infinite U bounds
  - Repair action: attempt Newton from domain center; fallback to fixed bounds
  - Suggested fixture: defect mentioning 'IsInfinite(uf) && IsInfinite(ul)', 'conic extrusion'
- **Branch 8** @ line 1327 — *extrema_cache_initialization* — **UNCOVERED**
  - What it tests: first call requires extrema tool setup
  - Repair action: initialize extrema for current domain with extension
  - Suggested fixture: defect mentioning '!myExtOK', 'extrema setup'
- **Branch 9** @ line 1343 — *offset_surface_extension_skip* — COVERED by: gn021
  - What it tests: OffsetSurface cannot safely extend (may throw)
  - Repair action: skip domain extension to avoid exceptions
- **Branch 10** @ line 1355 — *extrema_failure* — **UNCOVERED**
  - What it tests: extrema solver failed or found no solutions
  - Repair action: fall back to UVFromIso edge/isoline search
  - Suggested fixture: defect mentioning 'nPSurf > 0', 'extrema success test'
- **Branch 11** @ line 1357 — *multiple_extrema_candidates* — **UNCOVERED**
  - What it tests: extrema found multiple solutions
  - Repair action: select minimum distance candidate
  - Suggested fixture: defect mentioning 'dist2Min > dist2', 'minimum selection'
- **Branch 12** @ line 1376 — *surface_value_recompute_workaround* — COVERED by: gn007, gp040, m002, m164, pmi013, wr046, wr048
  - What it tests: SurfaceOfRevolution extrema distance unreliable
  - Repair action: recompute surface point to get true distance
- **Branch 13** @ line 1389 — *large_projection_error* — **UNCOVERED**
  - What it tests: extrema distance > preci (significant error)
  - Repair action: refine with Newton or isoline search
  - Suggested fixture: defect mentioning 'disSurf > preci', 'refinement trigger'
- **Branch 14** @ line 1402 — *near_tolerance_tangency_check* — **UNCOVERED**
  - What it tests: distance near 10*preci and surface is C1+
  - Repair action: check if point is on surface (tangent case)
  - Suggested fixture: defect mentioning 'disSurf < 10 * preci', 'tangency check'
- **Branch 15** @ line 1421 — *isoline_refinement* — **UNCOVERED**
  - What it tests: point not on surface, refine via UVFromIso
  - Repair action: search edges and isolines for better projection
  - Suggested fixture: defect mentioning '!possLockal', 'UVFromIso call'
- **Branch 16** @ line 1427 — *isoline_vs_extrema_selection* — **UNCOVERED**
  - What it tests: compare extrema vs isoline search results
  - Repair action: use better result, update gap
  - Suggested fixture: defect mentioning 'disSurf > DistMinOnIso', 'result selection'
- **Branch 17** @ line 1449 — *extrema_complete_failure* — **UNCOVERED**
  - What it tests: extrema returned zero solutions
  - Repair action: use UVFromIso as fallback, skip extrema result
  - Suggested fixture: defect mentioning 'nPSurf > 0 else', 'complete fallback'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_TransferParametersProj.cxx`

7 methods, 58 branches, 8 covered.

#### `ShapeAnalysis_TransferParametersProj.CopyNMVertex_edge_to_edge` — lines 565–711
(11 branches, 0 covered.)

- **Branch 1** @ line 567 — *VERTEX_ORIENTATION_CHECK* — **UNCOVERED**
  - What it tests: Vertex is internal or external (special orientation)
  - Repair action: Return empty vertex if not internal/external
  - Suggested fixture: defect mentioning 'theV.Orientation()', 'TopAbs_INTERNAL', 'TopAbs_EXTERNAL'
- **Branch 2** @ line 598 — *POINT_ON_SOURCE_CURVE* — **UNCOVERED**
  - What it tests: Vertex representation matches source edge curve
  - Repair action: Extract and cache parameter; skip other representations
  - Suggested fixture: defect mentioning 'IsPointOnCurve(C1, fromLoc)', 'aOldPar = pr->Parameter()'
- **Branch 3** @ line 604 — *POINT_ON_SURFACE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Vertex has point-on-surface representation
  - Repair action: Copy representation to target vertex
  - Suggested fixture: defect mentioning 'IsPointOnSurface()', 'BRep_PointOnSurface'
- **Branch 4** @ line 614 — *POINT_ON_CURVE_ON_SURFACE* — **UNCOVERED**
  - What it tests: Vertex point lies on source edge's PCurve-on-surface
  - Repair action: Match representation and continue; skip if found
  - Suggested fixture: defect mentioning 'IsPointOnCurveOnSurface()', 'pr->IsPointOnCurveOnSurface'
- **Branch 5** @ line 623 — *SOURCE_PCURVE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Source edge contains matching PCurve representation
  - Repair action: Verify point lies on source PCurve; mark found
  - Suggested fixture: defect mentioning 'fromGC->IsCurveOnSurface()', 'ac2d1, surface1, aL'
- **Branch 6** @ line 645 — *GENERIC_POINT_ON_CURVE* — **UNCOVERED**
  - What it tests: Vertex has generic point-on-curve representation
  - Repair action: Copy point-on-curve representation to target
  - Suggested fixture: defect mentioning 'IsPointOnCurve()', 'BRep_PointOnCurve'
- **Branch 7** @ line 651 — *GENERIC_PCURVE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Vertex has generic PCurve-on-surface representation
  - Repair action: Copy PCurve representation to target
  - Suggested fixture: defect mentioning 'IsPointOnCurveOnSurface()', 'BRep_PointOnCurveOnSurface'
- **Branch 8** @ line 663 — *NO_VALID_SOURCE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Source vertex has no matching representation or edges differ
  - Repair action: Project vertex point onto target edge 3D curve
  - Suggested fixture: defect mentioning '!hasRepr', 'fabs(f1 - f2)', 'fabs(l1 - l2)'
- **Branch 9** @ line 669 — *PROJECTION_DISTANCE_EXCEEDS_TOLERANCE* — **UNCOVERED**
  - What it tests: Projection distance larger than vertex tolerance
  - Repair action: Update vertex tolerance to projection distance
  - Suggested fixture: defect mentioning 'aTol < adist', 'aTol = adist'
- **Branch 10** @ line 687 — *TOLERANCE_UPDATE_VIA_PCURVE* — **UNCOVERED**
  - What it tests: Target edge PCurve representation requires tolerance increase
  - Repair action: Check 3D deviation and update tolerance if needed
  - Suggested fixture: defect mentioning 'toGC->IsCurveOnSurface()', 'ac2d1->Value', 'adist > aTol'
- **Branch 11** @ line 706 — *TOLERANCE_UPDATE_REQUIRED* — **UNCOVERED**
  - What it tests: Vertex tolerance updated during PCurve validation
  - Repair action: Rebuild vertex with increased tolerance
  - Suggested fixture: defect mentioning 'needUpdate', 'aB.UpdateVertex(anewV, aTol)'

#### `ShapeAnalysis_TransferParametersProj.CopyNMVertex_face_to_face` — lines 718–802
(6 branches, 0 covered.)

- **Branch 1** @ line 720 — *VERTEX_ORIENTATION_CHECK* — **UNCOVERED**
  - What it tests: Vertex is internal or external (special orientation)
  - Repair action: Return empty vertex if not internal/external
  - Suggested fixture: defect mentioning 'theV.Orientation()', 'TopAbs_INTERNAL', 'TopAbs_EXTERNAL'
- **Branch 2** @ line 750 — *PCURVE_ON_SURFACE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Vertex has PCurve-on-surface representation
  - Repair action: Copy representation to target vertex
  - Suggested fixture: defect mentioning 'IsPointOnCurveOnSurface()', 'BRep_PointOnCurveOnSurface'
- **Branch 3** @ line 756 — *POINT_ON_CURVE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Vertex has point-on-curve representation
  - Repair action: Copy representation to target vertex
  - Suggested fixture: defect mentioning 'IsPointOnCurve()', 'BRep_PointOnCurve'
- **Branch 4** @ line 762 — *POINT_ON_SURFACE_FROM_SOURCE* — **UNCOVERED**
  - What it tests: Vertex point lies on source surface
  - Repair action: Extract 2D parameters; cache if matching source surface
  - Suggested fixture: defect mentioning 'IsPointOnSurface()', 'pr->IsPointOnSurface(fromSurf, fromLoc)'
- **Branch 5** @ line 783 — *SURFACE_MISMATCH_OR_NO_REPRESENTATION* — **UNCOVERED**
  - What it tests: Source and target surfaces differ or no valid representation
  - Repair action: Project vertex point onto target surface and extract UV
  - Suggested fixture: defect mentioning '!hasRepr', 'fromSurf != toSurf', 'aSurfTool->ValueOfUV'
- **Branch 6** @ line 791 — *PROJECTION_GAP_EXCEEDS_TOLERANCE* — **UNCOVERED**
  - What it tests: Surface projection gap larger than vertex tolerance
  - Repair action: Update tolerance to gap + margin
  - Suggested fixture: defect mentioning 'aTol < aSurfTool->Gap()', 'aTol = aSurfTool->Gap() + 0.1'

#### `ShapeAnalysis_TransferParametersProj.Init` — lines 70–103
(3 branches, 1 covered.)

- **Branch 1** @ line 78 — *NULL_CURVE_3D* — **UNCOVERED**
  - What it tests: 3D curve missing from edge
  - Repair action: Set linear fallback parameters (0, 1); skip projection
  - Suggested fixture: defect mentioning 'myCurve.IsNull()', 'myFirst = 0', 'myLast = 1'
- **Branch 2** @ line 85 — *NULL_FACE* — **UNCOVERED**
  - What it tests: Face input is null or invalid
  - Repair action: Skip 2D curve extraction; leave myInitOK=false
  - Suggested fixture: defect mentioning 'F.IsNull()', 'return;'
- **Branch 3** @ line 92 — *MISSING_PCURVE* — COVERED by: p023
  - What it tests: 2D curve (pcurve) not found on face
  - Repair action: Skip adaptor construction; leave myInitOK=false

#### `ShapeAnalysis_TransferParametersProj.Perform` — lines 110–176
(5 branches, 0 covered.)

- **Branch 1** @ line 112 — *PROJECTION_BYPASS_CONDITION* — **UNCOVERED**
  - What it tests: Initialization failed or tolerance within threshold
  - Repair action: Fall back to linear transfer; skip projection method
  - Suggested fixture: defect mentioning '!myInitOK', '!myForceProj', 'myPrecision < myMaxTolerance'
- **Branch 2** @ line 134 — *PARAMETER_BEYOND_RANGE* — **UNCOVERED**
  - What it tests: Segment parameter exceeds last boundary
  - Repair action: Subtract epsilon to keep within valid range
  - Suggested fixture: defect mentioning 'prevPar > lastPar', 'prevPar -= preci'
- **Branch 3** @ line 146 — *CLOSED_CURVE_WRAPPING* — **UNCOVERED**
  - What it tests: Periodic curve requiring parameter normalization
  - Repair action: Adjust tail knots backward from last parameter
  - Suggested fixture: defect mentioning 'myCurve->IsClosed()', 'resKnots->Value(j) < maxPar'
- **Branch 4** @ line 165 — *KNOT_BELOW_MINIMUM* — **UNCOVERED**
  - What it tests: Knot parameter below curve start
  - Repair action: Clamp to first parameter
  - Suggested fixture: defect mentioning 'resKnots->Value(j) < first', 'SetValue(j, first)'
- **Branch 5** @ line 169 — *KNOT_ABOVE_MAXIMUM* — **UNCOVERED**
  - What it tests: Knot parameter exceeds curve end
  - Repair action: Clamp to last parameter
  - Suggested fixture: defect mentioning 'resKnots->Value(j) > last', 'SetValue(j, last)'

#### `ShapeAnalysis_TransferParametersProj.Perform_single_knot` — lines 223–252
(5 branches, 1 covered.)

- **Branch 1** @ line 224 — *PROJECTION_BYPASS_CONDITION* — **UNCOVERED**
  - What it tests: Initialization failed or tolerance within threshold
  - Repair action: Use parent class linear transfer method
  - Suggested fixture: defect mentioning '!myInitOK', '!myForceProj', 'myPrecision < myMaxTolerance'
- **Branch 2** @ line 231 — *PARAMETER_SPACE_SELECTION_2D* — **UNCOVERED**
  - What it tests: 2D transfer uses surface adaptor parametric range
  - Repair action: Call PreformSegment with 2D curve-on-surface bounds
  - Suggested fixture: defect mentioning 'To2d', 'myAC3d.FirstParameter()', 'myAC3d.LastParameter()'
- **Branch 3** @ line 235 — *PARAMETER_SPACE_SELECTION_3D* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: 3D transfer uses edge 3D curve parametric range
  - Repair action: Call PreformSegment with 3D curve bounds
- **Branch 4** @ line 243 — *RESULT_BELOW_MINIMUM* — **UNCOVERED**
  - What it tests: Computed parameter below curve start
  - Repair action: Clamp result to first parameter
  - Suggested fixture: defect mentioning 'res < first', 'res = first'
- **Branch 5** @ line 247 — *RESULT_ABOVE_MAXIMUM* — **UNCOVERED**
  - What it tests: Computed parameter exceeds curve end
  - Repair action: Clamp result to last parameter
  - Suggested fixture: defect mentioning 'res > last', 'res = last'

#### `ShapeAnalysis_TransferParametersProj.PreformSegment` — lines 184–218
(4 branches, 1 covered.)

- **Branch 1** @ line 186 — *PROJECTION_BYPASS_CONDITION* — **UNCOVERED**
  - What it tests: Initialization failed or tolerance within threshold
  - Repair action: Return linear parameter without projection
  - Suggested fixture: defect mentioning '!myInitOK', '!myForceProj', 'myPrecision < myMaxTolerance'
- **Branch 2** @ line 197 — *SPACE_TO_SURFACE_TRANSFER* — **UNCOVERED**
  - What it tests: 2D transfer mode: project from 3D curve to parametric
  - Repair action: Project 3D point onto 2D curve-on-surface adaptor
  - Suggested fixture: defect mentioning 'To2d', 'Adaptor3d_CurveOnSurface', 'sac.Project'
- **Branch 3** @ line 206 — *SURFACE_TO_SPACE_TRANSFER* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: 3D transfer mode: project from 2D curve to 3D
  - Repair action: Project surface parameter onto 3D curve adaptor
- **Branch 4** @ line 213 — *LINEAR_VS_PROJECTED_COMPARISON* — **UNCOVERED**
  - What it tests: Linear deviation within tolerance or superior to projected
  - Repair action: Use linear parameter instead of projection
  - Suggested fixture: defect mentioning 'linDev <= projDev', 'linDev < myPrecision', 'ppar = linPar'

#### `ShapeAnalysis_TransferParametersProj.TransferRange` — lines 289–535
(24 branches, 5 covered.)

- **Branch 1** @ line 290 — *PROJECTION_BYPASS_CONDITION* — **UNCOVERED**
  - What it tests: Initialization failed or tolerance within threshold
  - Repair action: Use parent linear transfer; return early
  - Suggested fixture: defect mentioning '!myInitOK', '!myForceProj', 'myPrecision < myMaxTolerance'
- **Branch 2** @ line 306 — *PARAMETER_ORDER_NORMALIZED* — **UNCOVERED**
  - What it tests: Swap parameters if previous > current
  - Repair action: Normalize firstPar <= lastPar
  - Suggested fixture: defect mentioning 'prevPar < currPar', 'firstPar = prevPar', 'lastPar = currPar'
- **Branch 3** @ line 319 — *INFINITE_COORDINATE_FIRST_2D* — COVERED by: a002, a005, a006, a010, a011, a016, a020, a025 (+754 more)
  - What it tests: 2D curve evaluation yields infinite values at segment start
  - Repair action: Mark samerange false and return early
- **Branch 4** @ line 326 — *INFINITE_COORDINATE_LAST_2D* — COVERED by: a002, a005, a008, a013, a030, a031, a032, a034 (+339 more)
  - What it tests: 2D curve evaluation yields infinite values at segment end
  - Repair action: Mark samerange false and return early
- **Branch 5** @ line 333 — *ZERO_PARAMETRIC_RANGE* — COVERED by: a105, ad005, ad027, ad031, ad032, ad035, ad042, ad044 (+64 more)
  - What it tests: Parametric range of 2D adaptor is degenerate
  - Repair action: Skip linear interpolation; use defaults alpha/beta
- **Branch 6** @ line 342 — *INFINITE_COORDINATE_FIRST_3D* — COVERED by: a002, a005, a006, a010, a011, a016, a020, a025 (+754 more)
  - What it tests: 3D curve evaluation yields infinite values at segment start
  - Repair action: Mark samerange false and return early
- **Branch 7** @ line 349 — *INFINITE_COORDINATE_LAST_3D* — COVERED by: a002, a005, a008, a013, a030, a031, a032, a034 (+339 more)
  - What it tests: 3D curve evaluation yields infinite values at segment end
  - Repair action: Mark samerange false and return early
- **Branch 8** @ line 356 — *ZERO_PARAMETRIC_RANGE_3D* — **UNCOVERED**
  - What it tests: 3D curve parametric range is degenerate
  - Repair action: Use default alpha=0, beta=1
  - Suggested fixture: defect mentioning 'myLast - myFirst', 'fact > Epsilon'
- **Branch 9** @ line 381 — *3D_CURVE_REPRESENTATION_PRESENT* — **UNCOVERED**
  - What it tests: Edge contains 3D geometric curve
  - Repair action: Adjust 3D curve range via projection or linear interpolation
  - Suggested fixture: defect mentioning 'toGC->IsCurve3D()', 'ppar1 = firstPar'
- **Branch 10** @ line 383 — *3D_CURVE_2D_TRANSFER_NEEDED* — **UNCOVERED**
  - What it tests: Transfer is 2D-sourced but 3D curve must be adjusted
  - Repair action: Project source 2D points onto target 3D curve
  - Suggested fixture: defect mentioning 'Is2d', 'C3d = toGC->Curve3D()'
- **Branch 11** @ line 391 — *NULL_3D_CURVE* — **UNCOVERED**
  - What it tests: 3D curve reference is null
  - Repair action: Skip processing; continue to next representation
  - Suggested fixture: defect mentioning 'C3d.IsNull()', 'continue;'
- **Branch 12** @ line 407 — *COLLAPSED_PROJECTION_RANGE* — **UNCOVERED**
  - What it tests: Projected parameters too close (degenerate)
  - Repair action: Use linear interpolation instead
  - Suggested fixture: defect mentioning 'std::abs(ppar1 - ppar2) < preci'
- **Branch 13** @ line 413 — *LINEAR_VS_PROJECTED_FIRST_3D* — **UNCOVERED**
  - What it tests: Linear point closer to endpoint than projection
  - Repair action: Use linear parameter for segment start
  - Suggested fixture: defect mentioning 'useLinearFirst', 'd01 <= dist1', 'd01 < myPrecision'
- **Branch 14** @ line 417 — *LINEAR_VS_PROJECTED_LAST_3D* — **UNCOVERED**
  - What it tests: Linear point closer to endpoint than projection
  - Repair action: Use linear parameter for segment end
  - Suggested fixture: defect mentioning 'useLinearLast', 'd02 <= dist2', 'd02 < myPrecision'
- **Branch 15** @ line 422 — *PARAMETER_ORDER_INVERSION* — **UNCOVERED**
  - What it tests: Projected parameters in reverse order
  - Repair action: Swap ppar1 and ppar2 to restore ordering
  - Suggested fixture: defect mentioning 'ppar1 > ppar2', 'tmpP = ppar2'
- **Branch 16** @ line 428 — *DEGENERATE_PROJECTION_RANGE* — **UNCOVERED**
  - What it tests: Adjusted range too small (less than epsilon)
  - Repair action: Expand range by epsilon in appropriate direction
  - Suggested fixture: defect mentioning 'ppar2 - ppar1 < preci', 'ppar2 += 2 * preci'
- **Branch 17** @ line 447 — *RANGE_MODIFICATION_DETECTED* — **UNCOVERED**
  - What it tests: Projected range differs from input
  - Repair action: Mark edge as non-same-range
  - Suggested fixture: defect mentioning 'ppar1 != firstPar', 'samerange = false'
- **Branch 18** @ line 452 — *PCURVE_ON_SURFACE_REPRESENTATION* — **UNCOVERED**
  - What it tests: Edge contains 2D curve-on-surface representation
  - Repair action: Adjust PCurve range via projection
  - Suggested fixture: defect mentioning 'toGC->IsCurveOnSurface()', 'AC2d = new Geom2dAdaptor_Curve'
- **Branch 19** @ line 476 — *PROJECTION_AT_DOMAIN_START* — **UNCOVERED**
  - What it tests: Projected point very close to PCurve start
  - Repair action: Mark for linear interpolation; may override projection
  - Suggested fixture: defect mentioning 'isFirstOnEnd = (ppar1 - first)', 'len < Precision::PConfusion()'
- **Branch 20** @ line 478 — *COLLAPSED_PCURVE_PROJECTION* — **UNCOVERED**
  - What it tests: Projected parameters collapse to single point
  - Repair action: Use linear interpolation for both endpoints
  - Suggested fixture: defect mentioning 'useLinear = std::abs', 'linFirst'
- **Branch 21** @ line 492 — *LINEAR_VS_PROJECTED_FIRST_PCURVE* — **UNCOVERED**
  - What it tests: Linear point closer to endpoint than projection (2D)
  - Repair action: Use linear parameter for PCurve start
  - Suggested fixture: defect mentioning 'localLinearFirst', 'd01 <= dist1', 'ppar1 = linFirst'
- **Branch 22** @ line 496 — *LINEAR_VS_PROJECTED_LAST_PCURVE* — **UNCOVERED**
  - What it tests: Linear point closer to endpoint than projection (2D)
  - Repair action: Use linear parameter for PCurve end
  - Suggested fixture: defect mentioning 'localLinearLast', 'd02 <= dist2', 'ppar2 = linLast'
- **Branch 23** @ line 507 — *PERIODIC_PCURVE_PARAMETER_WRAP* — **UNCOVERED**
  - What it tests: PCurve is periodic; parameters may need wrapping
  - Repair action: Apply CorrectParameter to normalize periodic domain
  - Suggested fixture: defect mentioning 'CorrectParameter(C2d, ppar1)'
- **Branch 24** @ line 528 — *PCURVE_RANGE_CHANGED* — **UNCOVERED**
  - What it tests: PCurve range modification detected
  - Repair action: Mark edge as non-same-range
  - Suggested fixture: defect mentioning 'ppar1 != firstPar || ppar2 != lastPar', 'samerange = false'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_TransferParametersProj.cxx; src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Edge.cxx; src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_IntersectionTool.cxx`

4 methods, 54 branches, 13 covered.

#### `ShapeAnalysis_TransferParametersProj.CopyNMVertex` — lines 565–711
(14 branches, 1 covered.)

- **Branch 1** @ line 567 — *ORIENTATION_VALIDATION* — **UNCOVERED**
  - What it tests: Vertex orientation must not be INTERNAL or EXTERNAL
  - Repair action: Return empty vertex if orientation invalid
  - Suggested fixture: defect mentioning 'theV.Orientation() != TopAbs_INTERNAL', 'TopAbs_EXTERNAL'
- **Branch 2** @ line 594 — *NULL_REPRESENTATION* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Skip null point representations in vertex
  - Repair action: Continue to next representation
- **Branch 3** @ line 598 — *CURVE_POINT_MATCH* — **UNCOVERED**
  - What it tests: Point lies on source edge curve
  - Repair action: Extract parameter and skip (don't copy)
  - Suggested fixture: defect mentioning 'IsPointOnCurve(C1', 'aOldPar = pr->Parameter()'
- **Branch 4** @ line 604 — *SURFACE_POINT_COPY* — **UNCOVERED**
  - What it tests: Point is on surface (not edge)
  - Repair action: Create surface point representation in target
  - Suggested fixture: defect mentioning 'IsPointOnSurface()', 'BRep_PointOnSurface'
- **Branch 5** @ line 614 — *CURVE_ON_SURFACE_MATCH* — **UNCOVERED**
  - What it tests: Point on curve-on-surface: find matching surface curve
  - Repair action: Mark found and optionally set aOldPar if not hasRepr
  - Suggested fixture: defect mentioning 'IsPointOnCurveOnSurface()', 'found = true'
- **Branch 6** @ line 623 — *CURVE_REPRESENTATION_SKIP* — **UNCOVERED**
  - What it tests: Skip if curve representation is null or not curve-on-surface
  - Repair action: Continue to next curve
  - Suggested fixture: defect mentioning 'fromGC.IsNull()', '!fromGC->IsCurveOnSurface()'
- **Branch 7** @ line 631 — *PARAMETRIC_LOCATION_MATCH* — **UNCOVERED**
  - What it tests: Point's 2D/surface pair matches source surface curve
  - Repair action: Set found=true, update aOldPar if needed
  - Suggested fixture: defect mentioning 'IsPointOnCurveOnSurface(ac2d1', 'found = true'
- **Branch 8** @ line 634 — *PARAMETER_TRANSFER* — **UNCOVERED**
  - What it tests: Check if parameter was already established from on-curve point
  - Repair action: Use existing parameter or extracted one
  - Suggested fixture: defect mentioning 'if (!hasRepr)', 'aOldPar = pr->Parameter()'
- **Branch 9** @ line 645 — *POINT_ON_CURVE_COPY* — **UNCOVERED**
  - What it tests: Point is simple on-curve (not on-surface)
  - Repair action: Copy point-on-curve representation
  - Suggested fixture: defect mentioning 'IsPointOnCurve()', 'BRep_PointOnCurve'
- **Branch 10** @ line 651 — *POINT_ON_CURVE_ON_SURFACE_COPY* — **UNCOVERED**
  - What it tests: Point is on curve-on-surface
  - Repair action: Copy point-on-curve-on-surface representation
  - Suggested fixture: defect mentioning 'IsPointOnCurveOnSurface()', 'BRep_PointOnCurveOnSurface'
- **Branch 11** @ line 663 — *PARAMETER_PROJECTION_FALLBACK* — **UNCOVERED**
  - What it tests: No on-curve representation or domain mismatch between edges
  - Repair action: Project vertex to target curve to find parameter
  - Suggested fixture: defect mentioning '!hasRepr', 'fabs(f1 - f2)', 'sae.Project'
- **Branch 12** @ line 669 — *TOLERANCE_MISMATCH* — **UNCOVERED**
  - What it tests: Projection distance exceeds original tolerance
  - Repair action: Update tolerance to projection distance
  - Suggested fixture: defect mentioning 'aTol < adist', 'aTol = adist'
- **Branch 13** @ line 687 — *TARGET_SURFACE_CURVE_SKIP* — **UNCOVERED**
  - What it tests: Skip null or non-surface curves in target edge
  - Repair action: Continue to next curve representation
  - Suggested fixture: defect mentioning 'toGC.IsNull()', '!toGC->IsCurveOnSurface()'
- **Branch 14** @ line 700 — *TOLERANCE_VERIFICATION_FAILURE* — **UNCOVERED**
  - What it tests: 3D point distance to surface exceeds tolerance
  - Repair action: Update vertex tolerance and mark needUpdate
  - Suggested fixture: defect mentioning 'adist > aTol', 'aTol = adist', 'needUpdate = true'

#### `ShapeFix_Edge.FixAddPCurve` — lines 476–614
(14 branches, 5 covered.)

- **Branch 1** @ line 479 — *PCURVE_EXISTS_NON_SEAM* — COVERED by: in014
  - What it tests: PCurve already exists (non-seam case)
  - Repair action: Skip repair, return false
- **Branch 2** @ line 480 — *SEAM_CURVE_EXISTS* — COVERED by: in014
  - What it tests: Seam curve already exists
  - Repair action: Skip repair, return false
- **Branch 3** @ line 486 — *PLANE_SURFACE_SKIP* — COVERED by: in014
  - What it tests: Surface is planar (no PCurve computed for planes)
  - Repair action: Skip repair, return false
- **Branch 4** @ line 502 — *MISSING_3D_CURVE* — **UNCOVERED**
  - What it tests: Edge has no 3D curve representation
  - Repair action: Set FAIL1 status and return false
  - Suggested fixture: defect mentioning 'c3d.IsNull()', 'ShapeExtend_FAIL1'
- **Branch 5** @ line 519 — *PCURVE_PROJECTION_NEEDED* — **UNCOVERED**
  - What it tests: PCurve does not exist (must project)
  - Repair action: Project 3D curve to surface PCurve
  - Suggested fixture: defect mentioning '!sae.HasPCurve(edge', 'myProjector->Perform'
- **Branch 6** @ line 524 — *VERTEX_TOLERANCE_READ* — **UNCOVERED**
  - What it tests: Extract vertex tolerances for projection bounds
  - Repair action: Use vertex tolerances or defaults (-1)
  - Suggested fixture: defect mentioning 'V1.IsNull()', 'TolFirst = BRep_Tool::Tolerance'
- **Branch 7** @ line 536 — *PROJECTION_STATUS_ANALYSIS* — COVERED by: twi066, twi067, twi078
  - What it tests: Check projection completion status
  - Repair action: Set DONE2 status if DONE4 indicated
- **Branch 8** @ line 543 — *PCURVE_EXTRACTION* — **UNCOVERED**
  - What it tests: PCurve already exists (else branch of check)
  - Repair action: Extract existing PCurve and parameter range
  - Suggested fixture: defect mentioning 'sae.PCurve(edge', 'a1, b1'
- **Branch 9** @ line 550 — *SEAM_PCURVE_DUPLICATION* — **UNCOVERED**
  - What it tests: Seam edge needs dual PCurve
  - Repair action: Create second PCurve via Copy
  - Suggested fixture: defect mentioning 'if (isSeam)', 'c2d2 = c2d->Copy()'
- **Branch 10** @ line 564 — *U_CLOSURE_NON_V_CLOSURE* — **UNCOVERED**
  - What it tests: Surface u-closed but not v-closed
  - Repair action: Translate PCurve in U direction
  - Suggested fixture: defect mentioning 'IsUClosed(prec) && !sas->IsVClosed', 'gp_Vec2d tranvec(ul - uf'
- **Branch 11** @ line 571 — *V_CLOSURE_NON_U_CLOSURE* — **UNCOVERED**
  - What it tests: Surface v-closed but not u-closed
  - Repair action: Translate PCurve in V direction
  - Suggested fixture: defect mentioning 'IsVClosed(prec) && !sas->IsUClosed', 'gp_Vec2d tranvec(0'
- **Branch 12** @ line 576 — *DOUBLY_CLOSED_SURFACE* — **UNCOVERED**
  - What it tests: Surface u-closed AND v-closed (e.g., torus sphere)
  - Repair action: Use TranslatePCurve for complex closure
  - Suggested fixture: defect mentioning 'IsUClosed() && sas->IsVClosed()', 'TranslatePCurve'
- **Branch 13** @ line 593 — *3D_CURVE_RECOMPUTATION* — **UNCOVERED**
  - What it tests: Projection altered the 3D curve (DONE3 status)
  - Repair action: Update 3D curve range on edge
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE3)', 'B.UpdateEdge'
- **Branch 14** @ line 601 — *EXCEPTION_HANDLING* — COVERED by: ad086, gp029, m027, pf009, sw009, twi066
  - What it tests: Catch all exceptions during PCurve computation
  - Repair action: Set FAIL2 status and return true (partial success)

#### `ShapeFix_IntersectionTool.SplitEdge` — lines 94–190
(10 branches, 3 covered.)

- **Branch 1** @ line 98 — *VERTEX_ENDPOINT_CHECK* — **UNCOVERED**
  - What it tests: Split vertex is already an endpoint of edge
  - Repair action: Cannot split at endpoint, return false
  - Suggested fixture: defect mentioning 'V1.IsSame(vert)', 'V2.IsSame(vert)'
- **Branch 2** @ line 107 — *PARAMETER_AT_BOUNDARY* — **UNCOVERED**
  - What it tests: Split parameter too close to edge domain bounds
  - Repair action: Reject split (parameter at boundary), return false
  - Suggested fixture: defect mentioning 'std::abs(a - param)', '0.01 * preci'
- **Branch 3** @ line 114 — *SAME_PARAMETER_3D_EVALUATION* — **UNCOVERED**
  - What it tests: Edge has 3D curve with SameParameter property
  - Repair action: Evaluate 3D point directly from curve
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter', '!BRep_Tool::Degenerated'
- **Branch 4** @ line 118 — *MISSING_3D_CURVE* — COVERED by: in014
  - What it tests: Edge missing 3D curve (degenerate or no curve)
  - Repair action: Cannot evaluate, return false
- **Branch 5** @ line 123 — *LOCATION_TRANSFORMATION* — COVERED by: a017, a067, ad086, gp016
  - What it tests: 3D point requires location transformation
  - Repair action: Apply location transformation to point
- **Branch 6** @ line 128 — *CURVE_ON_SURFACE_EVALUATION* — COVERED by: ad086, bo006, ls031, n009, tb013, twi046, twi083, u039 (+1 more)
  - What it tests: Edge parameterization differs from 3D (use surface PCurve)
  - Repair action: Evaluate point via 2D curve on surface
- **Branch 7** @ line 139 — *VERTEX_DISTANCE_TOLERANCE* — **UNCOVERED**
  - What it tests: New vertex position differs from original
  - Repair action: Update vertex tolerance to compensate distance
  - Suggested fixture: defect mentioning 'P1.Distance(P2) > preci', 'B.UpdateVertex'
- **Branch 8** @ line 151 — *PARAMETER_ORDER* — **UNCOVERED**
  - What it tests: Determine canonical parameter range (a < b)
  - Repair action: Assign first/last based on parameter order
  - Suggested fixture: defect mentioning 'if (a < b)', 'first = a'
- **Branch 9** @ line 167 — *EDGE_ORIENTATION_HANDLING* — **UNCOVERED**
  - What it tests: Preserve original edge orientation through split
  - Repair action: Apply original orientation to output edges
  - Suggested fixture: defect mentioning 'orient = edge.Orientation()', 'newE1.Orientation(orient)'
- **Branch 10** @ line 182 — *ORIENTATION_SWAP_FOR_REVERSED* — **UNCOVERED**
  - What it tests: Edge is REVERSED, so split parts must be swapped
  - Repair action: Swap newE1/newE2 to maintain edge semantics
  - Suggested fixture: defect mentioning 'if (orient == TopAbs_REVERSED)', 'tmp = newE2'

#### `ShapeFix_IntersectionTool.SplitEdge2` — lines 376–491
(16 branches, 4 covered.)

- **Branch 1** @ line 379 — *PARAMETER_BISECTION* — **UNCOVERED**
  - What it tests: Two problematic parameters define split zone
  - Repair action: Use midpoint as split parameter
  - Suggested fixture: defect mentioning 'param = (param1 + param2) / 2'
- **Branch 2** @ line 380 — *DELEGATE_SPLIT* — COVERED by: in014
  - What it tests: Attempt base SplitEdge with bisected parameter
  - Repair action: If fails, return false early
- **Branch 3** @ line 389 — *NEWEDGE1_PCURVE_EXTRACTION* — **UNCOVERED**
  - What it tests: Extract PCurve from first split segment
  - Repair action: Get 2D curve and parameter bounds
  - Suggested fixture: defect mentioning 'sae.PCurve(newE1', 'Crv1'
- **Branch 4** @ line 391 — *NEWEDGE2_PCURVE_EXTRACTION* — **UNCOVERED**
  - What it tests: Extract PCurve from second split segment
  - Repair action: Get 2D curve and parameter bounds
  - Suggested fixture: defect mentioning 'sae.PCurve(newE2', 'Crv2'
- **Branch 5** @ line 393 — *ENDPOINT_PARAMETER_TEST* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: First edge's end parameter matches split point
  - Repair action: Determine cut direction based on parameter relationship
- **Branch 6** @ line 395 — *DIRECTIONAL_CUT_BOTH_EDGES* — **UNCOVERED**
  - What it tests: Cut directions for both edges when domain aligned
  - Repair action: CutEdge from start of newE1 (param1) and end of newE2 (param2)
  - Suggested fixture: defect mentioning '(lp1 - fp1) * (lp1 - param1) > 0', 'CutEdge'
- **Branch 7** @ line 401 — *DIRECTIONAL_CUT_REVERSED* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Parameter ordering reversed relative to domain
  - Repair action: Swap param1/param2 in cut operations
- **Branch 8** @ line 408 — *STARTPOINT_PARAMETER_TEST* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: First edge's start parameter matches split point
  - Repair action: Alternate cut direction logic
- **Branch 9** @ line 410 — *DIRECTIONAL_CUT_FROM_END* — **UNCOVERED**
  - What it tests: Cut from end of newE1 (param1) and start of newE2 (param2)
  - Repair action: CutEdge from end of newE1, start of newE2
  - Suggested fixture: defect mentioning 'CutEdge(newE1, lp1, param1'
- **Branch 10** @ line 415 — *DIRECTIONAL_CUT_REVERSED_START* — **UNCOVERED**
  - What it tests: Reversed parameter order for start-point alignment
  - Repair action: Swap param1/param2 for start-aligned edges
  - Suggested fixture: defect mentioning 'CutEdge(newE1, lp1, param2'
- **Branch 11** @ line 437 — *WIRE_DATA_ELEMENT_UPDATE* — **UNCOVERED**
  - What it tests: Replace original edge with first split edge in wire
  - Repair action: Update wire structure sewd
  - Suggested fixture: defect mentioning 'sewd->Set(newE1, num)'
- **Branch 12** @ line 438 — *SECOND_EDGE_APPEND_POSITION* — **UNCOVERED**
  - What it tests: Determine insertion position for second split edge
  - Repair action: Append at end or insert after first edge
  - Suggested fixture: defect mentioning 'if (num == sewd->NbEdges())', 'sewd->Add'
- **Branch 13** @ line 448 — *BOUNDING_BOX_INVALIDATION* — **UNCOVERED**
  - What it tests: Clear cached bounding box for original edge
  - Repair action: Remove box entry for original edge
  - Suggested fixture: defect mentioning 'boxes.UnBind(edge)'
- **Branch 14** @ line 453 — *FIRST_EDGE_BBOX_COMPUTATION* — **UNCOVERED**
  - What it tests: Extract PCurve for first new edge to compute bbox
  - Repair action: Create bounding box from 2D curve bounds
  - Suggested fixture: defect mentioning 'sae.PCurve(newE1', 'Bnd_Box2d box'
- **Branch 15** @ line 459 — *BSPLINE_CURVE_BBOX_HANDLING* — **UNCOVERED**
  - What it tests: BSpline PCurve with extended bounds needs full-curve bbox
  - Repair action: Load gac without parameter restriction
  - Suggested fixture: defect mentioning 'Geom2d_BSplineCurve', 'cf < aFirst || cl > aLast'
- **Branch 16** @ line 471 — *SECOND_EDGE_BBOX_COMPUTATION* — **UNCOVERED**
  - What it tests: Extract PCurve for second new edge to compute bbox
  - Repair action: Create bounding box from 2D curve bounds
  - Suggested fixture: defect mentioning 'sae.PCurve(newE2', 'Bnd_Box2d box'


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_Wire.cxx`

25 methods, 235 branches, 77 covered.

#### `ShapeAnalysis_Wire.CheckClosed` — lines 471–499
(4 branches, 0 covered.)

- **Branch 1** @ line 473 — *wire_not_initialized* — **UNCOVERED**
  - What it tests: Wire uninitialized or has fewer than 1 edge
  - Repair action: Returns false; skips closure checks
  - Suggested fixture: defect mentioning 'IsReady', 'NbEdges < 1'
- **Branch 2** @ line 478 — *closure_vertex_gap* — **UNCOVERED**
  - What it tests: Last edge end vertex doesn't match first edge start vertex (or within precision)
  - Repair action: Adjusts vertices or extends curves to close loop
  - Suggested fixture: defect mentioning 'CheckConnected(1, prec)', 'ShapeExtend_DONE1', 'ShapeExtend_FAIL1'
- **Branch 3** @ line 488 — *degenerate_closure* — **UNCOVERED**
  - What it tests: First edge has degenerate geometry at its endpoints
  - Repair action: Splits or removes degenerate edge at closure point
  - Suggested fixture: defect mentioning 'CheckDegenerated(1)', 'ShapeExtend_DONE2', 'ShapeExtend_FAIL2'
- **Branch 4** @ line 498 — *closure_status_ok* — **UNCOVERED**
  - What it tests: Wire is properly closed (both tests passed or not needed)
  - Repair action: Returns true if StatusClosed has DONE flag
  - Suggested fixture: defect mentioning 'StatusClosed', 'ShapeExtend_DONE'

#### `ShapeAnalysis_Wire.CheckConnected` — lines 694–761
(9 branches, 0 covered.)

- **Branch 1** @ line 699 — *uninitialized_state* — **UNCOVERED**
  - What it tests: Wire not loaded or has 0-1 edges
  - Repair action: Return false immediately
  - Suggested fixture: defect mentioning '!IsLoaded()', 'NbEdges() < 1'
- **Branch 2** @ line 703 — *edge_indexing* — **UNCOVERED**
  - What it tests: num > 0 selects specific edge pair; num=0 selects last edge
  - Repair action: Set n2 to num or NbEdges; n1 to n2-1 or NbEdges if n2==1
  - Suggested fixture: defect mentioning 'num > 0 ? num : NbEdges()', 'n2 > 1 ? n2 - 1'
- **Branch 3** @ line 712 — *invalid_vertex* — **UNCOVERED**
  - What it tests: Last vertex of E1 or first vertex of E2 is null
  - Repair action: Return FAIL2 status
  - Suggested fixture: defect mentioning 'V1.IsNull() || V2.IsNull()'
- **Branch 4** @ line 717 — *already_connected* — **UNCOVERED**
  - What it tests: Two vertices are identical (edges already connected)
  - Repair action: Return false (no repair needed)
  - Suggested fixture: defect mentioning 'V1.IsSame(V2)'
- **Branch 5** @ line 725 — *negligible_gap* — **UNCOVERED**
  - What it tests: Distance <= machine resolution (3D)
  - Repair action: Set status to DONE1; gap is negligible
  - Suggested fixture: defect mentioning 'myMin3d <= gp::Resolution()'
- **Branch 6** @ line 729 — *small_gap_within_tolerance* — **UNCOVERED**
  - What it tests: Distance <= object precision tolerance
  - Repair action: Set status to DONE2; within tolerance
  - Suggested fixture: defect mentioning 'myMin3d <= myPrecision'
- **Branch 7** @ line 733 — *gap_within_spec* — **UNCOVERED**
  - What it tests: Distance <= specified precision argument
  - Repair action: Set status to DONE3; within requested tolerance
  - Suggested fixture: defect mentioning 'myMin3d <= prec'
- **Branch 8** @ line 738 — *single_edge_loop* — **UNCOVERED**
  - What it tests: Wire has one edge (n1 == n2); gap cannot be closed
  - Repair action: Return FAIL1 status
  - Suggested fixture: defect mentioning 'n1 == n2', 'ShapeExtend_FAIL1'
- **Branch 9** @ line 742 — *vertex_orientation_mismatch* — **UNCOVERED**
  - What it tests: Check if reversing E2 creates connection (dist > myPrecision after flip)
  - Repair action: If dist still too large, return FAIL1; else FAIL2
  - Suggested fixture: defect mentioning 'sae.LastVertex(E2)', 'dist > myPrecision'

#### `ShapeAnalysis_Wire.CheckCurveGap` — lines 1197–1241
(6 branches, 2 covered.)

- **Branch 1** @ line 1199 — *GUARD_STATE* — COVERED by: in014
  - What it tests: Wire initialization state (IsReady/IsLoaded)
  - Repair action: Return false; skip processing uninitialized wire
- **Branch 2** @ line 1208 — *CURVE3D_EXTRACT* — **UNCOVERED**
  - What it tests: Curve3d extraction from edge
  - Repair action: Fail (ShapeExtend_FAIL1) if Curve3d unavailable
  - Suggested fixture: defect mentioning 'SAE.Curve3d', 'ShapeExtend_FAIL1'
- **Branch 3** @ line 1210 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 4** @ line 1214 — *PCURVE_EXTRACT* — **UNCOVERED**
  - What it tests: PCurve extraction from edge
  - Repair action: Fail (ShapeExtend_FAIL1) if PCurve unavailable
  - Suggested fixture: defect mentioning 'SAE.PCurve', 'ShapeExtend_FAIL1'
- **Branch 5** @ line 1216 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 6** @ line 1225 — *ITERATION_SCAN* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: Enumerate points or segments in collection
  - Repair action: Process each entity; collect defect instances

#### `ShapeAnalysis_Wire.CheckCurveGaps` — lines 564–589
(3 branches, 0 covered.)

- **Branch 1** @ line 568 — *uninitialized_state* — **UNCOVERED**
  - What it tests: Wire not ready or has zero edges
  - Repair action: Return false immediately
  - Suggested fixture: defect mentioning 'IsReady()', 'NbEdges() < 1'
- **Branch 2** @ line 575 — *curve_gap_detection_failure* — **UNCOVERED**
  - What it tests: Individual curve gap check fails with FAIL1 status
  - Repair action: Skip distance accumulation for failed curve gaps
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL1)', 'CheckCurveGap(i)'
- **Branch 3** @ line 578 — *max_distance_tracking* — **UNCOVERED**
  - What it tests: Accumulate maximum 3D curve gap distance
  - Repair action: Update maxdist with current curve gap distance
  - Suggested fixture: defect mentioning 'maxdist < dist', 'MinDistance3d()'

#### `ShapeAnalysis_Wire.CheckDegenerated` — lines 897–1112
(20 branches, 8 covered.)

- **Branch 1** @ line 899 — *GUARD_STATE* — COVERED by: in014
  - What it tests: Wire initialization state (IsReady/IsLoaded)
  - Repair action: Return false; skip processing uninitialized wire
- **Branch 2** @ line 904 — *CONDITIONAL_SELECT* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Conditional assignment (edge index, parameter)
  - Repair action: Select value based on condition
- **Branch 3** @ line 905 — *CONDITIONAL_SELECT* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Conditional assignment (edge index, parameter)
  - Repair action: Select value based on condition
- **Branch 4** @ line 914 — *EDGE_DEGENERACY* — **UNCOVERED**
  - What it tests: Whether edge is marked as degenerate (0-length)
  - Repair action: Validate/remove degenerate edge; check pcurve
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'HasPCurve'
- **Branch 5** @ line 917 — *PCURVE_PRESENCE* — COVERED by: a002, a003, a013, a014, a017, a018, a019, a020 (+747 more)
  - What it tests: PCurve existence on face
  - Repair action: Skip edge if pcurve absent; mark FAIL status
- **Branch 6** @ line 932 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 7** @ line 939 — *EDGE_DEGENERACY* — **UNCOVERED**
  - What it tests: Whether edge is marked as degenerate (0-length)
  - Repair action: Validate/remove degenerate edge; check pcurve
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'HasPCurve'
- **Branch 8** @ line 943 — *EDGE_DEGENERACY* — **UNCOVERED**
  - What it tests: Whether edge is marked as degenerate (0-length)
  - Repair action: Validate/remove degenerate edge; check pcurve
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'HasPCurve'
- **Branch 9** @ line 945 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 10** @ line 955 — *NULL_ENTITY* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+591 more)
  - What it tests: Vertex/Edge/Curve nullness
  - Repair action: Return false; skip if entity extraction failed
- **Branch 11** @ line 970 — *CONDITIONAL_SELECT* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Conditional assignment (edge index, parameter)
  - Repair action: Select value based on condition
- **Branch 12** @ line 982 — *NULL_ENTITY* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+591 more)
  - What it tests: Vertex/Edge/Curve nullness
  - Repair action: Return false; skip if entity extraction failed
- **Branch 13** @ line 996 — *EDGE_DEGENERACY* — **UNCOVERED**
  - What it tests: Whether edge is marked as degenerate (0-length)
  - Repair action: Validate/remove degenerate edge; check pcurve
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'HasPCurve'
- **Branch 14** @ line 1018 — *ITERATION_SCAN* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: Enumerate points or segments in collection
  - Repair action: Process each entity; collect defect instances
- **Branch 15** @ line 1046 — *EDGE_DEGENERACY* — **UNCOVERED**
  - What it tests: Whether edge is marked as degenerate (0-length)
  - Repair action: Validate/remove degenerate edge; check pcurve
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'HasPCurve'
- **Branch 16** @ line 1048 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 17** @ line 1074 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 18** @ line 1083 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 19** @ line 1093 — *EDGE_DEGENERACY* — **UNCOVERED**
  - What it tests: Whether edge is marked as degenerate (0-length)
  - Repair action: Validate/remove degenerate edge; check pcurve
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'HasPCurve'
- **Branch 20** @ line 1095 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'

#### `ShapeAnalysis_Wire.CheckEdgeCurves` — lines 270–356
(8 branches, 7 covered.)

- **Branch 1** @ line 272 — *wire_not_initialized* — **UNCOVERED**
  - What it tests: Detects uninitialized wire or missing face context
  - Repair action: Returns false; skips all curve checks
  - Suggested fixture: defect mentioning 'IsReady'
- **Branch 2** @ line 284 — *3d_pcurve_mismatch* — COVERED by: twi062, twi065
  - What it tests: 3D curve differs from 2D parametric curve projection on face
  - Repair action: Rebuilds 3D curve from 2D or vice versa
- **Branch 3** @ line 294 — *vertex_pcurve_mismatch* — COVERED by: twi060, twi065
  - What it tests: Edge vertices don't match 2D parametric curve endpoints
  - Repair action: Updates vertices to match curve parameters
- **Branch 4** @ line 304 — *vertex_3d_curve_mismatch* — COVERED by: twi059, twi065
  - What it tests: Edge vertices don't match 3D curve endpoints
  - Repair action: Adjusts vertices to match 3D curve
- **Branch 5** @ line 314 — *seam_edge_issue* — COVERED by: twi065, twi071
  - What it tests: Detects seam edges on periodic surfaces needing special handling
  - Repair action: Splits or merges seam edges
- **Branch 6** @ line 324 — *gap_3d* — COVERED by: twi065, twi072
  - What it tests: Gap between current edge endpoint and next edge start in 3D
  - Repair action: Extends curves or widens tolerance
- **Branch 7** @ line 334 — *gap_2d* — COVERED by: twi065, twi073
  - What it tests: Gap between current edge endpoint and next edge start in 2D parameters
  - Repair action: Adjusts 2D curve parameters or endpoints
- **Branch 8** @ line 345 — *same_parameter_violation* — COVERED by: twi065
  - What it tests: 3D and 2D curve parameters don't correspond (SameParameter property)
  - Repair action: Rebuilds 2D curve or transfers parameters

#### `ShapeAnalysis_Wire.CheckGap2d` — lines 1157–1192
(5 branches, 2 covered.)

- **Branch 1** @ line 1158 — *NULL_ENTITY* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+591 more)
  - What it tests: Vertex/Edge/Curve nullness
  - Repair action: Return false; skip if entity extraction failed
- **Branch 2** @ line 1160 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 3** @ line 1166 — *GUARD_STATE* — COVERED by: in014
  - What it tests: Wire initialization state (IsReady/IsLoaded)
  - Repair action: Return false; skip processing uninitialized wire
- **Branch 4** @ line 1177 — *PCURVE_EXTRACT* — **UNCOVERED**
  - What it tests: PCurve extraction from edge
  - Repair action: Fail (ShapeExtend_FAIL1) if PCurve unavailable
  - Suggested fixture: defect mentioning 'SAE.PCurve', 'ShapeExtend_FAIL1'
- **Branch 5** @ line 1179 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'

#### `ShapeAnalysis_Wire.CheckGap3d` — lines 1125–1152
(3 branches, 1 covered.)

- **Branch 1** @ line 1128 — *GUARD_STATE* — COVERED by: in014
  - What it tests: Wire initialization state (IsReady/IsLoaded)
  - Repair action: Return false; skip processing uninitialized wire
- **Branch 2** @ line 1139 — *CURVE3D_EXTRACT* — **UNCOVERED**
  - What it tests: Curve3d extraction from edge
  - Repair action: Fail (ShapeExtend_FAIL1) if Curve3d unavailable
  - Suggested fixture: defect mentioning 'SAE.Curve3d', 'ShapeExtend_FAIL1'
- **Branch 3** @ line 1141 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'

#### `ShapeAnalysis_Wire.CheckGaps2d` — lines 534–559
(3 branches, 0 covered.)

- **Branch 1** @ line 536 — *uninitialized_state* — **UNCOVERED**
  - What it tests: Wire not ready or has zero edges
  - Repair action: Return false immediately
  - Suggested fixture: defect mentioning 'IsReady()', 'NbEdges() < 1'
- **Branch 2** @ line 547 — *gap_detection_failure* — **UNCOVERED**
  - What it tests: Individual edge gap check fails with FAIL1 status
  - Repair action: Skip distance accumulation for failed edges
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL1)', '!LastCheckStatus'
- **Branch 3** @ line 550 — *max_distance_tracking* — **UNCOVERED**
  - What it tests: Accumulate maximum 2D gap distance across edges
  - Repair action: Update maxdist with current edge distance
  - Suggested fixture: defect mentioning 'maxdist < dist', 'MinDistance2d()'

#### `ShapeAnalysis_Wire.CheckGaps3d` — lines 504–529
(5 branches, 0 covered.)

- **Branch 1** @ line 506 — *wire_not_loaded* — **UNCOVERED**
  - What it tests: Wire not loaded into memory or has fewer than 1 edge
  - Repair action: Returns false; skips all gap measurements
  - Suggested fixture: defect mentioning 'IsLoaded', 'NbEdges < 1'
- **Branch 2** @ line 515 — *gap_3d_at_edge* — **UNCOVERED**
  - What it tests: 3D gap detected between edge i and next edge
  - Repair action: Measures gap distance; recorded in myStatus
  - Suggested fixture: defect mentioning 'CheckGap3d(i)', 'myStatus'
- **Branch 3** @ line 517 — *gap_measurement_ok* — **UNCOVERED**
  - What it tests: Gap distance measured successfully (no FAIL1 from detailed check)
  - Repair action: Updates maxdist with measured distance
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL1) == false', 'MinDistance3d'
- **Branch 4** @ line 520 — *max_gap_update* — **UNCOVERED**
  - What it tests: Current gap is larger than previous maximum
  - Repair action: Records new maximum gap distance
  - Suggested fixture: defect mentioning 'maxdist < dist'
- **Branch 5** @ line 528 — *gaps_3d_summary* — **UNCOVERED**
  - What it tests: Gap measurements completed for all edges
  - Repair action: Returns true if StatusGaps3d has DONE flag; sets min/max distance
  - Suggested fixture: defect mentioning 'StatusGaps3d', 'myMin3d = myMax3d = maxdist', 'ShapeExtend_DONE'

#### `ShapeAnalysis_Wire.CheckIntersectingEdges` — lines 1365–1543
(19 branches, 11 covered.)

- **Branch 1** @ line 1370 — *GUARD_STATE* — COVERED by: in014
  - What it tests: Wire initialization state (IsReady/IsLoaded)
  - Repair action: Return false; skip processing uninitialized wire
- **Branch 2** @ line 1376 — *CONDITIONAL_SELECT* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Conditional assignment (edge index, parameter)
  - Repair action: Select value based on condition
- **Branch 3** @ line 1377 — *CONDITIONAL_SELECT* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: Conditional assignment (edge index, parameter)
  - Repair action: Select value based on condition
- **Branch 4** @ line 1384 — *NULL_ENTITY* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+591 more)
  - What it tests: Vertex/Edge/Curve nullness
  - Repair action: Return false; skip if entity extraction failed
- **Branch 5** @ line 1386 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 6** @ line 1389 — *VERTEX_MATCHING* — **UNCOVERED**
  - What it tests: Consecutive edge endpoint continuity
  - Repair action: Detect gap/discontinuity if vertices mismatch
  - Suggested fixture: defect mentioning 'BRepTools::Compare', 'LastVertex', 'FirstVertex'
- **Branch 7** @ line 1391 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 8** @ line 1402 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 9** @ line 1407 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 10** @ line 1410 — *PARAM_RANGE_DEGEN* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+77 more)
  - What it tests: Parameter interval collapse (start==end)
  - Repair action: Skip if parameter range is degenerate
- **Branch 11** @ line 1412 — *PARAM_RANGE_DEGEN* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+77 more)
  - What it tests: Parameter interval collapse (start==end)
  - Repair action: Skip if parameter range is degenerate
- **Branch 12** @ line 1448 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 13** @ line 1463 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 14** @ line 1464 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 15** @ line 1468 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 16** @ line 1474 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 17** @ line 1482 — *INTERSECTION_POSITION* — **UNCOVERED**
  - What it tests: Intersection point location (endpoint vs interior)
  - Repair action: Record self-int only if at interior point
  - Suggested fixture: defect mentioning 'PositionOnCurve', 'IntRes2d_Middle'
- **Branch 18** @ line 1490 — *INTERSECTION_POSITION* — **UNCOVERED**
  - What it tests: Intersection point location (endpoint vs interior)
  - Repair action: Record self-int only if at interior point
  - Suggested fixture: defect mentioning 'PositionOnCurve', 'IntRes2d_Middle'
- **Branch 19** @ line 1532 — *VERTEX_MATCHING* — **UNCOVERED**
  - What it tests: Consecutive edge endpoint continuity
  - Repair action: Detect gap/discontinuity if vertices mismatch
  - Suggested fixture: defect mentioning 'BRepTools::Compare', 'LastVertex', 'FirstVertex'

#### `ShapeAnalysis_Wire.CheckIntersectingEdges_1arg` — lines 1365–1543
(17 branches, 8 covered.)

- **Branch 1** @ line 1370 — *wire-not-ready-or-insufficient-edges* — **UNCOVERED**
  - What it tests: Wire is not ready or has fewer than 2 edges
  - Repair action: Return false, skip intersection check
  - Suggested fixture: defect mentioning 'IsReady', 'NbEdges < 2'
- **Branch 2** @ line 1384 — *null-vertex-at-edge-junction* — **UNCOVERED**
  - What it tests: Either endpoint vertex is null/invalid
  - Repair action: Set FAIL1 status and return false
  - Suggested fixture: defect mentioning 'V1.IsNull', 'V2.IsNull', 'ShapeExtend_FAIL1'
- **Branch 3** @ line 1389 — *vertices-not-coincident-at-junction* — COVERED by: twi066
  - What it tests: Adjacent edge endpoints do not match
  - Repair action: Set FAIL2 status and return false
- **Branch 4** @ line 1400 — *pcurve-extraction-failure-edge1* — COVERED by: twi065
  - What it tests: Cannot extract 2D parametric curve from first edge on face
  - Repair action: Set FAIL3 status and return false
- **Branch 5** @ line 1405 — *pcurve-extraction-failure-edge2* — COVERED by: twi052, twi065
  - What it tests: Cannot extract 2D parametric curve from second edge on face
  - Repair action: Set FAIL3 status and return false
- **Branch 6** @ line 1410 — *degenerate-pcurve-zero-range* — COVERED by: tb007
  - What it tests: PCurve parameter range [a,b] is essentially zero
  - Repair action: Return false, curve too degenerate
- **Branch 7** @ line 1440 — *intersection-computation-order-wrap* — **UNCOVERED**
  - What it tests: Wraparound intersection (num==1) requires reversed curve order
  - Repair action: Call Inter.Perform with C2,C1 order for arc-wrap case
  - Suggested fixture: defect mentioning 'num == 1', 'Inter.Perform'
- **Branch 8** @ line 1448 — *intersection-computation-failed* — **UNCOVERED**
  - What it tests: 2D intersection algorithm failed to complete
  - Repair action: Return false, intersection unreliable
  - Suggested fixture: defect mentioning 'Inter.IsDone', 'Geom2dInt_GInter'
- **Branch 9** @ line 1468 — *intersection-point-vs-segment-type* — **UNCOVERED**
  - What it tests: Discriminate between point intersections and segment overlaps
  - Repair action: Extract IntRes2d_IntersectionPoint or convert segment endpoint
  - Suggested fixture: defect mentioning 'i <= NbPoints', 'Inter.Point', 'Inter.Segment'
- **Branch 10** @ line 1475 — *segment-incomplete-missing-endpoints* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Overlap segment has missing first or last point
  - Repair action: Skip this segment, continue iteration
- **Branch 11** @ line 1482 — *intersection-at-segment-midpoint* — **UNCOVERED**
  - What it tests: Intersection point is at interior of overlap segment
  - Repair action: Use segment endpoint instead of first point
  - Suggested fixture: defect mentioning 'IntRes2d_Middle', 'Seg.LastPoint'
- **Branch 12** @ line 1490 — *intersection-not-on-curve-interior* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Both transitions indicate boundary (not interior) position
  - Repair action: Skip intersection, continue iteration
- **Branch 13** @ line 1495 — *param-order-depends-on-num-value* — **UNCOVERED**
  - What it tests: Parameter assignment is conditional on num==1 wraparound
  - Repair action: Extract param1/param2 in reversed order for wraparound
  - Suggested fixture: defect mentioning 'num == 1', 'ParamOnSecond', 'ParamOnFirst'
- **Branch 14** @ line 1499 — *intersection-param-out-of-curve-range* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+13 more)
  - What it tests: Computed intersection falls outside [a,b] curve domain
  - Repair action: Skip intersection point, continue iteration
- **Branch 15** @ line 1516 — *lacking-gap-detection-via-endpoint-distance* — **UNCOVERED**
  - What it tests: Endpoint distance in 2D space indicates a lacking edge case
  - Repair action: Set isLacking flag for tolerance recomputation
  - Suggested fixture: defect mentioning 'isLacking < 0', 'end1.SquareDistance', 'tol2d'
- **Branch 16** @ line 1527 — *intersection-significant-distance-or-lacking* — **UNCOVERED**
  - What it tests: Intersection gap exceeds tolerance OR a lacking edge exists
  - Repair action: Record intersection point and 3D error estimate
  - Suggested fixture: defect mentioning 'dist2 > tolt', 'isLacking', 'points2d.Append'
- **Branch 17** @ line 1532 — *wire-closure-check-vs-endpoint-distance* — COVERED by: ad086, m006, m008, m011, m026, m027, m030, m031 (+4 more)
  - What it tests: Wire closes properly at endpoints OR gap is significant
  - Repair action: Allow recording if wire does NOT close OR distance is large

#### `ShapeAnalysis_Wire.CheckIntersectingEdges_2arg` — lines 1563–1693
(12 branches, 4 covered.)

- **Branch 1** @ line 1565 — *wire-not-ready* — **UNCOVERED**
  - What it tests: Wire is not ready for analysis
  - Repair action: Return false, skip intersection check
  - Suggested fixture: defect mentioning 'IsReady'
- **Branch 2** @ line 1579 — *pcurve-extraction-failure-edge1* — COVERED by: twi065
  - What it tests: Cannot extract 2D parametric curve from first edge
  - Repair action: Set FAIL3 status and return false
- **Branch 3** @ line 1585 — *pcurve-extraction-failure-edge2* — COVERED by: twi052, twi065
  - What it tests: Cannot extract 2D parametric curve from second edge
  - Repair action: Set FAIL3 status and return false
- **Branch 4** @ line 1591 — *degenerate-pcurve-zero-range* — COVERED by: tb007
  - What it tests: PCurve parameter range is essentially zero for either edge
  - Repair action: Return false, curve too degenerate
- **Branch 5** @ line 1619 — *intersection-computation-failed* — **UNCOVERED**
  - What it tests: 2D intersection algorithm failed
  - Repair action: Return false, intersection unreliable
  - Suggested fixture: defect mentioning 'Inter.IsDone'
- **Branch 6** @ line 1631 — *intersection-point-vs-segment-type* — **UNCOVERED**
  - What it tests: Discriminate between point intersections and segment overlaps
  - Repair action: Extract point or convert segment endpoint
  - Suggested fixture: defect mentioning 'i <= NbPoints', 'Inter.Point', 'Inter.Segment'
- **Branch 7** @ line 1638 — *segment-incomplete-missing-endpoints* — **UNCOVERED**
  - What it tests: Overlap segment has missing endpoints
  - Repair action: Skip segment, continue iteration
  - Suggested fixture: defect mentioning 'HasFirstPoint', 'HasLastPoint'
- **Branch 8** @ line 1645 — *intersection-at-segment-midpoint* — **UNCOVERED**
  - What it tests: Intersection is at interior of overlap segment
  - Repair action: Use segment endpoint instead of first point
  - Suggested fixture: defect mentioning 'IntRes2d_Middle', 'Seg.LastPoint'
- **Branch 9** @ line 1652 — *intersection-not-on-curve-interior* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Both transitions indicate boundary (not interior) position
  - Repair action: Skip intersection, continue iteration
- **Branch 10** @ line 1665 — *intersection-near-edge1-vertex* — **UNCOVERED**
  - What it tests: First intersection point is within vertex tolerance of edge1 endpoint
  - Repair action: Set OK1 flag, skip later reporting
  - Suggested fixture: defect mentioning 'j <= 2', 'vertexPoints', 'vertexTolers'
- **Branch 11** @ line 1674 — *intersection-near-edge2-vertex* — **UNCOVERED**
  - What it tests: Second intersection point is within vertex tolerance of edge2 endpoint
  - Repair action: Set OK2 flag, skip later reporting
  - Suggested fixture: defect mentioning 'j <= 4', 'vertexPoints', 'vertexTolers'
- **Branch 12** @ line 1683 — *intersection-away-from-all-vertices* — **UNCOVERED**
  - What it tests: Either intersection point is not at vertex (OK1 or OK2 false)
  - Repair action: Record true intersection point (not at junction) and error
  - Suggested fixture: defect mentioning '!OK1 || !OK2', 'points2d.Append'

#### `ShapeAnalysis_Wire.CheckLacking` — lines 455–466
(3 branches, 0 covered.)

- **Branch 1** @ line 456 — *wire_not_initialized* — **UNCOVERED**
  - What it tests: Wire uninitialized, not loaded, or has fewer than 2 edges
  - Repair action: Returns false; skips gap checks
  - Suggested fixture: defect mentioning 'IsReady', 'NbEdges < 2'
- **Branch 2** @ line 462 — *gap_at_edge* — **UNCOVERED**
  - What it tests: Gap after edge i detected by lower-level CheckLacking(i)
  - Repair action: Inserts gap-closing curve if missing
  - Suggested fixture: defect mentioning 'CheckLacking(i)', 'myStatus'
- **Branch 3** @ line 465 — *any_gap_found* — **UNCOVERED**
  - What it tests: At least one gap was found or fixed
  - Repair action: Returns true if StatusLacking has DONE flag set
  - Suggested fixture: defect mentioning 'StatusLacking', 'ShapeExtend_DONE'

#### `ShapeAnalysis_Wire.CheckLacking_parameterized` — lines 1715–1793
(10 branches, 2 covered.)

- **Branch 1** @ line 1717 — *wire-not-ready* — **UNCOVERED**
  - What it tests: Wire is not ready for analysis
  - Repair action: Return false, skip check
  - Suggested fixture: defect mentioning 'IsReady'
- **Branch 2** @ line 1732 — *null-vertex-at-edge-junction* — COVERED by: tfa037, twi066
  - What it tests: Either endpoint vertex is null
  - Repair action: Set FAIL1 status and return false
- **Branch 3** @ line 1737 — *vertices-not-coincident-at-junction* — COVERED by: twi066
  - What it tests: Adjacent edge endpoints do not match
  - Repair action: Set FAIL2 status and return false
- **Branch 4** @ line 1746 — *pcurve-extraction-failure* — **UNCOVERED**
  - What it tests: Cannot extract 2D parametric curve from edge on face
  - Repair action: Set FAIL3 status and return false
  - Suggested fixture: defect mentioning 'sae.PCurve', 'FAIL3'
- **Branch 5** @ line 1753 — *edge-orientation-reversal-affects-tangent* — **UNCOVERED**
  - What it tests: Edge is reversed, requiring tangent vector flip
  - Repair action: Reverse v1 tangent for orientation
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'v1.Reverse'
- **Branch 6** @ line 1757 — *pcurve-extraction-failure-edge2* — **UNCOVERED**
  - What it tests: Cannot extract 2D parametric curve from second edge
  - Repair action: Set FAIL3 status and return false
  - Suggested fixture: defect mentioning 'sae.PCurve', 'FAIL3'
- **Branch 7** @ line 1764 — *edge-orientation-reversal-affects-tangent-2* — **UNCOVERED**
  - What it tests: Second edge is reversed, requiring tangent vector flip
  - Repair action: Reverse v2 tangent for orientation
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'v2.Reverse'
- **Branch 8** @ line 1773 — *tolerance-override-explicit-vs-computed* — **UNCOVERED**
  - What it tests: Explicit tolerance is given but differs from computed vertex tolerance
  - Repair action: Use explicit tolerance if smaller, vertex tolerance otherwise
  - Suggested fixture: defect mentioning 'Tolerance > gp::Resolution', 'tol = (Tolerance ... tol)'
- **Branch 9** @ line 1777 — *gap-too-small-not-lacking* — **UNCOVERED**
  - What it tests: Gap in 2D space is below tolerance threshold
  - Repair action: Return false, gap too small to report as lacking
  - Suggested fixture: defect mentioning 'myMax2d < tol2d * tol2d'
- **Branch 10** @ line 1786 — *small-gap-or-sharp-angle-discontinuity* — **UNCOVERED**
  - What it tests: Gap is near-zero OR tangent directions form nearly 180-degree angle
  - Repair action: Set DONE2 status to mark sharp discontinuity
  - Suggested fixture: defect mentioning 'myMax2d < Precision::PConfusion', '0.9 * M_PI'

#### `ShapeAnalysis_Wire.CheckLoop` — lines 2234–2312
(13 branches, 2 covered.)

- **Branch 1** @ line 2236 — *empty_wire* — **UNCOVERED**
  - What it tests: Wire not loaded or has fewer than 2 edges
  - Repair action: return false
  - Suggested fixture: defect mentioning 'IsLoaded', 'NbEdges'
- **Branch 2** @ line 2249 — *null_vertices* — **UNCOVERED**
  - What it tests: Edge has null vertices (TopExp::Vertices extraction failed)
  - Repair action: encode FAIL2 status, return false
  - Suggested fixture: defect mentioning 'aV1.IsNull', 'aV2.IsNull', 'TopExp::Vertices'
- **Branch 3** @ line 2255 — *seam_edge* — **UNCOVERED**
  - What it tests: Edge is marked as seam in wire
  - Repair action: add to aMapSeemEdges (skip other checks)
  - Suggested fixture: defect mentioning 'IsSeam', 'aMapSeemEdges.Add'
- **Branch 4** @ line 2259 — *degenerated_edge* — **UNCOVERED**
  - What it tests: Edge is topologically degenerated
  - Repair action: add to aMapSmallEdges
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'aMapSmallEdges.Add'
- **Branch 5** @ line 2263 — *small_loop_edge* — COVERED by: a032, ad045, ad086, bo008, bo030, gb001, gb004, gn009 (+347 more)
  - What it tests: Self-loop edge (v1==v2) and CheckSmall returns true
  - Repair action: add to aMapSmallEdges
- **Branch 6** @ line 2268 — *unbound_vertex_v1* — **UNCOVERED**
  - What it tests: Vertex v1 not yet in aMapVertexEdges map
  - Repair action: bind empty list for v1
  - Suggested fixture: defect mentioning '!aMapVertexEdges.IsBound', 'aV1'
- **Branch 7** @ line 2273 — *unbound_vertex_v2* — **UNCOVERED**
  - What it tests: Vertex v2 not yet in aMapVertexEdges map
  - Repair action: bind empty list for v2
  - Suggested fixture: defect mentioning '!aMapVertexEdges.IsBound', 'aV2'
- **Branch 8** @ line 2278 — *self_loop_defect* — **UNCOVERED**
  - What it tests: Edge is a self-loop (v1 same as v2)
  - Repair action: append edge twice to v1 list, check for multi-vertex loops
  - Suggested fixture: defect mentioning 'isSame', 'alshape.Append'
- **Branch 9** @ line 2283 — *multi_vertex_loop_v1* — **UNCOVERED**
  - What it tests: Self-loop has >2 incident edges and isMultiVertex returns true
  - Repair action: add v1 to aMapLoopVertices
  - Suggested fixture: defect mentioning 'alshape.Extent() > 2', 'isMultiVertex', 'aMapLoopVertices.Add'
- **Branch 10** @ line 2288 — *non_self_loop_defect* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Edge connects two different vertices (v1 != v2)
  - Repair action: append edge to both v1 and v2 lists, check for multi-vertex loops
- **Branch 11** @ line 2292 — *multi_vertex_loop_v1_nonselfloop* — **UNCOVERED**
  - What it tests: Non-self-loop edge makes v1 have >2 incident edges and isMultiVertex true
  - Repair action: add v1 to aMapLoopVertices
  - Suggested fixture: defect mentioning 'alshape.Extent() > 2', 'isMultiVertex', 'aMapLoopVertices.Add'
- **Branch 12** @ line 2298 — *multi_vertex_loop_v2* — **UNCOVERED**
  - What it tests: Non-self-loop edge makes v2 have >2 incident edges and isMultiVertex true
  - Repair action: add v2 to aMapLoopVertices
  - Suggested fixture: defect mentioning 'alshape2.Extent() > 2', 'isMultiVertex', 'aMapLoopVertices.Add'
- **Branch 13** @ line 2305 — *loop_vertices_found* — **UNCOVERED**
  - What it tests: Loop vertex map has entries (defects found)
  - Repair action: encode DONE1 status, return true
  - Suggested fixture: defect mentioning 'aMapLoopVertices.Extent', 'ShapeExtend_DONE1'

#### `ShapeAnalysis_Wire.CheckNotchedEdges` — lines 1868–2000
(17 branches, 5 covered.)

- **Branch 1** @ line 1870 — *wire-not-ready* — **UNCOVERED**
  - What it tests: Wire is not ready for analysis
  - Repair action: Return false, skip check
  - Suggested fixture: defect mentioning 'IsReady'
- **Branch 2** @ line 1880 — *degenerate-edge-in-pair* — **UNCOVERED**
  - What it tests: Either edge is degenerate (zero length)
  - Repair action: Return false, cannot analyze degenerate edge
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated'
- **Branch 3** @ line 1889 — *null-vertex-at-edge-junction* — COVERED by: tfa037, twi066
  - What it tests: Either endpoint vertex is null
  - Repair action: Set FAIL1 status and return false
- **Branch 4** @ line 1894 — *vertices-not-coincident-at-junction* — COVERED by: twi066
  - What it tests: Adjacent edge endpoints do not match
  - Repair action: Set FAIL2 status and return false
- **Branch 5** @ line 1904 — *pcurve-extraction-failure-edge1* — COVERED by: twi065
  - What it tests: Cannot extract 2D parametric curve from first edge
  - Repair action: Set FAIL3 status and return false
- **Branch 6** @ line 1910 — *edge-orientation-affects-endpoint-and-tangent* — **UNCOVERED**
  - What it tests: First edge is reversed, requiring different endpoint and tangent
  - Repair action: Evaluate curve at a1 (start) for REVERSED; at b1 (end) for FORWARD
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'c2d1->D1'
- **Branch 7** @ line 1920 — *pcurve-extraction-failure-edge2* — COVERED by: twi052, twi065
  - What it tests: Cannot extract 2D parametric curve from second edge
  - Repair action: Set FAIL3 status and return false
- **Branch 8** @ line 1925 — *edge-orientation-affects-endpoint-and-tangent-2* — **UNCOVERED**
  - What it tests: Second edge is reversed, requiring different endpoint and tangent
  - Repair action: Evaluate curve at b2 (end) for REVERSED; at a2 (start) for FORWARD
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'c2d2->D1'
- **Branch 9** @ line 1935 — *zero-magnitude-tangent-vector* — **UNCOVERED**
  - What it tests: Either tangent vector is too small for angle calculation
  - Repair action: Return false, tangent magnitude insufficient
  - Suggested fixture: defect mentioning 'gp::Resolution', 'v2.Magnitude', 'v1.Magnitude'
- **Branch 10** @ line 1940 — *excessive-angle-or-gap-at-junction* — **UNCOVERED**
  - What it tests: Tangent angle > 0.1 rad OR point distance exceeds tolerance
  - Repair action: Return false, junction angle or gap too large
  - Suggested fixture: defect mentioning 'v2.Angle', 'p2d1.Distance'
- **Branch 11** @ line 1962 — *projection-of-opposite-endpoint-to-first-edge* — **UNCOVERED**
  - What it tests: End of second edge projects onto first edge interior
  - Repair action: Compute projection distance dist1 for later comparison
  - Suggested fixture: defect mentioning 'ProjectInside', 'p2d2'
- **Branch 12** @ line 1963 — *projection-of-opposite-endpoint-to-second-edge* — **UNCOVERED**
  - What it tests: End of first edge projects onto second edge interior
  - Repair action: Compute projection distance dist2 for later comparison
  - Suggested fixture: defect mentioning 'ProjectInside', 'p2d1'
- **Branch 13** @ line 1965 — *endpoint-not-projectable-to-opposite-edge* — **UNCOVERED**
  - What it tests: Both endpoints are too far from opposite edge to project
  - Repair action: Return false, edges do not form a notch
  - Suggested fixture: defect mentioning 'dist1 > Tolerance', 'dist2 > Tolerance'
- **Branch 14** @ line 1970 — *first-edge-projects-closer-short-edge-selection* — **UNCOVERED**
  - What it tests: First edge is shorter/closer, making it the 'short' edge of notch
  - Repair action: Designate Ad2 as shortAD, Ad1 as longAD, set shortNum=n2
  - Suggested fixture: defect mentioning 'dist1 < dist2', 'shortNum = n2'
- **Branch 15** @ line 1979 — *second-edge-projects-closer-short-edge-selection* — **UNCOVERED**
  - What it tests: Second edge is shorter/closer, making it the 'short' edge of notch
  - Repair action: Designate Ad1 as shortAD, Ad2 as longAD, set shortNum=n1
  - Suggested fixture: defect mentioning 'dist1 >= dist2', 'shortNum = n1'
- **Branch 16** @ line 1990 — *validate-short-edge-points-near-long-edge* — **UNCOVERED**
  - What it tests: Multiple points along short edge must project close to long edge
  - Repair action: Loop 23 times sampling short edge; check all projections within tolerance
  - Suggested fixture: defect mentioning 'for i = 1', 'i < 23', 'sac.Project'
- **Branch 17** @ line 1993 — *short-edge-point-projection-fails-tolerance* — COVERED by: in014
  - What it tests: A point along short edge is too far from long edge to project
  - Repair action: Return false, edges do not form consistent notch

#### `ShapeAnalysis_Wire.CheckOrder` — lines 597–689
(12 branches, 0 covered.)

- **Branch 1** @ line 598 — *missing_pcurve* — **UNCOVERED**
  - What it tests: 2D mode without face context (theMode3D=false, theModeBoth=false, myFace=null)
  - Repair action: Return FAIL2 status; cannot proceed without face data
  - Suggested fixture: defect mentioning '!theMode3D || theModeBoth', 'myFace.IsNull()'
- **Branch 2** @ line 615 — *invalid_vertex* — **UNCOVERED**
  - What it tests: First or last vertex of edge is null
  - Repair action: Return FAIL2 status and abort order analysis
  - Suggested fixture: defect mentioning 'V1.IsNull() || V2.IsNull()'
- **Branch 3** @ line 633 — *pcurve_unavailable* — **UNCOVERED**
  - What it tests: PCurve extraction fails for edge on face
  - Repair action: Either fail in 2D-only mode or defer to 3D mode if theModeBoth enabled
  - Suggested fixture: defect mentioning '!EA.PCurve()', '!theMode3D && !theModeBoth'
- **Branch 4** @ line 637 — *fallback_mode_selection* — **UNCOVERED**
  - What it tests: PCurve missing but theModeBoth allows 3D fallback
  - Repair action: Set isAll2dEdgesOk=false to trigger mode switch later
  - Suggested fixture: defect mentioning 'isAll2dEdgesOk = false'
- **Branch 5** @ line 653 — *edge_ordering_mode* — **UNCOVERED**
  - What it tests: 3D-only mode (theMode3D && !theModeBoth)
  - Repair action: Add edge using only 3D vertex coordinates
  - Suggested fixture: defect mentioning 'theMode3D && !theModeBoth', 'sawo.Add(aP1XYZ'
- **Branch 6** @ line 656 — *edge_ordering_mode* — **UNCOVERED**
  - What it tests: 2D-only mode (!theMode3D && !theModeBoth)
  - Repair action: Add edge using only 2D parameter coordinates
  - Suggested fixture: defect mentioning '!theMode3D && !theModeBoth', 'sawo.Add(aP1XY'
- **Branch 7** @ line 659 — *mixed_dimension_mode* — **UNCOVERED**
  - What it tests: Both 2D and 3D available (theModeBoth)
  - Repair action: Add edge with both 3D and 2D coordinates
  - Suggested fixture: defect mentioning 'sawo.Add(aP1XYZ, aP2XYZ, aP1XY'
- **Branch 8** @ line 664 — *fallback_mode_trigger* — **UNCOVERED**
  - What it tests: theModeBoth enabled and some edges lack valid PCurves
  - Repair action: Switch wire ordering to 3D-only mode and re-perform analysis
  - Suggested fixture: defect mentioning 'theModeBoth && !isAll2dEdgesOk', 'sawo.SetMode(true'
- **Branch 9** @ line 668 — *ordering_status_ok* — **UNCOVERED**
  - What it tests: WireOrder analysis returns status 0 (success)
  - Repair action: Set status to ShapeExtend_OK
  - Suggested fixture: defect mentioning 'case 0:', 'ShapeExtend_OK'
- **Branch 10** @ line 671 — *ordering_status_fixable* — **UNCOVERED**
  - What it tests: WireOrder returns status 1 (reordering needed)
  - Repair action: Set status to ShapeExtend_DONE1 and reorder edges
  - Suggested fixture: defect mentioning 'case 1:', 'ShapeExtend_DONE1'
- **Branch 11** @ line 673 — *ordering_status_reversed* — **UNCOVERED**
  - What it tests: WireOrder returns status -1 (reversed orientation)
  - Repair action: Set status to ShapeExtend_DONE3; reverse wire
  - Suggested fixture: defect mentioning 'case -1:', 'ShapeExtend_DONE3'
- **Branch 12** @ line 676 — *ordering_status_shifted* — **UNCOVERED**
  - What it tests: WireOrder returns status 3 (shifted only, no reorder needed)
  - Repair action: Set status to ShapeExtend_DONE5
  - Suggested fixture: defect mentioning 'case 3:', 'ShapeExtend_DONE5'

#### `ShapeAnalysis_Wire.CheckOuterBound` — lines 1806–1833
(3 branches, 0 covered.)

- **Branch 1** @ line 1808 — *wire-not-ready* — **UNCOVERED**
  - What it tests: Wire is not ready for analysis
  - Repair action: Return false, skip check
  - Suggested fixture: defect mentioning 'IsReady'
- **Branch 2** @ line 1814 — *wire-construction-method-apimake* — **UNCOVERED**
  - What it tests: Caller requests API-compliant wire construction (APIMake=true)
  - Repair action: Use WireAPIMake() for construction instead of Wire()
  - Suggested fixture: defect mentioning 'APIMake', 'WireAPIMake'
- **Branch 3** @ line 1827 — *wire-is-already-outer-bound* — **UNCOVERED**
  - What it tests: Wire is the outer boundary (not an inner hole)
  - Repair action: Return false, wire is already outer bound
  - Suggested fixture: defect mentioning 'ShapeAnalysis::IsOuterBound'

#### `ShapeAnalysis_Wire.CheckSeam` — lines 844–883
(5 branches, 0 covered.)

- **Branch 1** @ line 848 — *uninitialized_state* — **UNCOVERED**
  - What it tests: Wire not ready (not initialized with data)
  - Repair action: Return false immediately
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 854 — *not_a_seam_edge* — **UNCOVERED**
  - What it tests: Edge is not a seam on the current face
  - Repair action: Return false (no seam processing needed)
  - Suggested fixture: defect mentioning '!ShapeAnalysis_Edge().IsSeam()'
- **Branch 3** @ line 865 — *pcurve_missing_forward* — **UNCOVERED**
  - What it tests: Forward or reversed PCurve cannot be extracted
  - Repair action: Return false (seam edge malformed)
  - Suggested fixture: defect mentioning 'C1.IsNull() || C2.IsNull()'
- **Branch 4** @ line 871 — *seam_curve_ordering_error* — **UNCOVERED**
  - What it tests: SelectForwardSeam returns value != 2 (wrong seam direction)
  - Repair action: Return false (cannot determine forward seam orientation)
  - Suggested fixture: defect mentioning 'SelectForwardSeam(C1, C2)', 'theCurveIndice != 2'
- **Branch 5** @ line 875 — *seam_detected_success* — **UNCOVERED**
  - What it tests: All checks pass; seam edge properly characterized
  - Repair action: Set DONE1 status; return true to signal valid seam
  - Suggested fixture: defect mentioning 'myStatus = ShapeExtend::EncodeStatus(ShapeExtend_DONE1)'

#### `ShapeAnalysis_Wire.CheckSelfIntersectingEdge` — lines 1273–1342
(8 branches, 5 covered.)

- **Branch 1** @ line 1277 — *GUARD_STATE* — COVERED by: in014
  - What it tests: Wire initialization state (IsReady/IsLoaded)
  - Repair action: Return false; skip processing uninitialized wire
- **Branch 2** @ line 1289 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 3** @ line 1292 — *PARAM_RANGE_DEGEN* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+77 more)
  - What it tests: Parameter interval collapse (start==end)
  - Repair action: Skip if parameter range is degenerate
- **Branch 4** @ line 1303 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 5** @ line 1310 — *NULL_ENTITY* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+591 more)
  - What it tests: Vertex/Edge/Curve nullness
  - Repair action: Return false; skip if entity extraction failed
- **Branch 6** @ line 1312 — *DEFECT_MARKER* — **UNCOVERED**
  - What it tests: Encode defect status in result
  - Repair action: Mark FAIL/DONE status based on condition
  - Suggested fixture: defect mentioning 'myStatus', 'ShapeExtend_FAIL', 'EncodeStatus'
- **Branch 7** @ line 1321 — *INTERSECTION_VALIDITY* — COVERED by: ad077, ad085, ad086, ad099, ad117, fi001, gn011, gn024 (+40 more)
  - What it tests: Intersection algorithm completion & result count
  - Repair action: Only process intersection if valid; extract points
- **Branch 8** @ line 1326 — *INTERSECTION_POSITION* — **UNCOVERED**
  - What it tests: Intersection point location (endpoint vs interior)
  - Repair action: Record self-int only if at interior point
  - Suggested fixture: defect mentioning 'PositionOnCurve', 'IntRes2d_Middle'

#### `ShapeAnalysis_Wire.CheckSelfIntersection` — lines 373–450
(8 branches, 2 covered.)

- **Branch 1** @ line 375 — *wire_not_initialized* — **UNCOVERED**
  - What it tests: Uninitialized wire or missing face
  - Repair action: Returns false; skips all intersection checks
  - Suggested fixture: defect mentioning 'IsReady'
- **Branch 2** @ line 382 — *self_intersecting_edge* — **UNCOVERED**
  - What it tests: Single edge loops back and intersects itself
  - Repair action: Splits edge at self-intersection point
  - Suggested fixture: defect mentioning 'CheckSelfIntersectingEdge', 'ShapeExtend_DONE1', 'ShapeExtend_FAIL1'
- **Branch 3** @ line 392 — *pairwise_edge_intersection* — **UNCOVERED**
  - What it tests: Adjacent edge i intersects with edge i+1 (topology issue)
  - Repair action: Rebuilds curves or adjusts parameters to remove overlap
  - Suggested fixture: defect mentioning 'CheckIntersectingEdges', 'ShapeExtend_DONE2', 'ShapeExtend_FAIL2'
- **Branch 4** @ line 413 — *missing_2d_curve* — COVERED by: a024, a071, a097, ad046, ad086, ad099, gb004, gn002 (+142 more)
  - What it tests: Edge has no 2D parametric curve on face
  - Repair action: Skips bounding-box check for edge (null c2d)
- **Branch 5** @ line 426 — *closed_wire_assumption* — COVERED by: twi064, twi066
  - What it tests: Wire is closed; skips last-to-first check to avoid double-counting
  - Repair action: Limits pairwise checks to avoid closed-wire redundancy
- **Branch 6** @ line 432 — *bounding_box_overlap* — **UNCOVERED**
  - What it tests: 2D bounding boxes overlap (coarse filter before detailed check)
  - Repair action: Proceeds to detailed intersection test if boxes overlap
  - Suggested fixture: defect mentioning 'IsOut', 'CheckIntersectingEdges', 'num1, num2'
- **Branch 7** @ line 440 — *intersection_found* — **UNCOVERED**
  - What it tests: Detailed check confirmed edge-edge intersection
  - Repair action: Sets FAIL3 status; caller handles split/rebuild
  - Suggested fixture: defect mentioning 'isFail', 'ShapeExtend_FAIL3'
- **Branch 8** @ line 444 — *intersection_repaired* — **UNCOVERED**
  - What it tests: Intersection was detected and handled
  - Repair action: Sets DONE3 status for downstream reporting
  - Suggested fixture: defect mentioning 'isDone', 'ShapeExtend_DONE3'

#### `ShapeAnalysis_Wire.CheckSmall` — lines 766–835
(11 branches, 4 covered.)

- **Branch 1** @ line 770 — *uninitialized_state* — **UNCOVERED**
  - What it tests: Wire not loaded or has 0-1 edges
  - Repair action: Return false immediately
  - Suggested fixture: defect mentioning '!IsLoaded()', 'NbEdges() <= 1'
- **Branch 2** @ line 775 — *degenerated_edge* — **UNCOVERED**
  - What it tests: Edge flagged as degenerate but lacks PCurve on face
  - Repair action: Return false (degenerate without pcurve is valid)
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(E)', '!sae.HasPCurve'
- **Branch 3** @ line 777 — *degenerated_with_pcurve* — COVERED by: tfa037, twi066
  - What it tests: Degenerate edge has PCurve (inconsistent geometry)
  - Repair action: Set FAIL1 status and return false
- **Branch 4** @ line 783 — *invalid_vertex* — **UNCOVERED**
  - What it tests: First or last vertex is null
  - Repair action: Return FAIL2 status
  - Suggested fixture: defect mentioning 'V1.IsNull() || V2.IsNull()'
- **Branch 5** @ line 792 — *edge_too_large* — COVERED by: in014
  - What it tests: 3D distance between vertices exceeds small tolerance
  - Repair action: Return false (edge is not small)
- **Branch 6** @ line 798 — *zero_length_with_3d_curve* — **UNCOVERED**
  - What it tests: Edge has 3D curve; check midpoint to verify zero-length
  - Repair action: Evaluate curve midpoint; verify endpoints and midpoint are collocated
  - Suggested fixture: defect mentioning 'sae.Curve3d(E', 'c3d->Value((cf + cl) / 2)'
- **Branch 7** @ line 804 — *zero_length_with_2d_curve* — **UNCOVERED**
  - What it tests: No 3D curve; fall back to 2D curve and surface eval
  - Repair action: Evaluate 2D curve on surface at midpoint
  - Suggested fixture: defect mentioning 'sae.PCurve(E', 'mySurf->Value(p2m)'
- **Branch 8** @ line 811 — *no_curve_fallback* — COVERED by: tfa037, twi066
  - What it tests: Neither 3D nor 2D curve available
  - Repair action: Set FAIL1 status; use first vertex as midpoint
- **Branch 9** @ line 814 — *small_edge_not_closed* — **UNCOVERED**
  - What it tests: Curve midpoint distance to endpoints exceeds tolerance
  - Repair action: Return false (edge has non-zero length)
  - Suggested fixture: defect mentioning 'aMidpoint.Distance(p1) > prec'
- **Branch 10** @ line 818 — *truly_small_closed_edge* — COVERED by: tfa037, twi066, twi067
  - What it tests: Vertices are identical (V1 == V2)
  - Repair action: Set DONE1 status
- **Branch 11** @ line 818 — *truly_small_open_edge* — **UNCOVERED**
  - What it tests: Vertices are distinct but edge is zero-length
  - Repair action: Set DONE2 status
  - Suggested fixture: defect mentioning 'ShapeExtend_DONE2'

#### `ShapeAnalysis_Wire.CheckTail` — lines 2356–2599
(23 branches, 6 covered.)

- **Branch 1** @ line 2358 — *unready_or_degenerated_edges* — **UNCOVERED**
  - What it tests: Wire not ready or either input edge is degenerated
  - Repair action: return false
  - Suggested fixture: defect mentioning 'IsReady', 'BRep_Tool::Degenerated'
- **Branch 2** @ line 2376 — *curve_extraction_failed* — COVERED by: in014
  - What it tests: Cannot extract 3D curve from edge
  - Repair action: return false
- **Branch 3** @ line 2384 — *common_end_too_far* — **UNCOVERED**
  - What it tests: Common ends of the two edges are too far apart (>aTol2)
  - Repair action: return false
  - Suggested fixture: defect mentioning 'SquareDistance', 'aSqTol2'
- **Branch 4** @ line 2391 — *angle_check_enabled* — **UNCOVERED**
  - What it tests: Angle check is enabled (theMaxSine >= 0)
  - Repair action: perform angle/direction validation
  - Suggested fixture: defect mentioning 'if (theMaxSine >= 0)', 'aSqMaxSine'
- **Branch 5** @ line 2399 — *edge_too_short* — **UNCOVERED**
  - What it tests: Edge curve length < 0.5*Confusion (too short for derivative)
  - Repair action: return false
  - Suggested fixture: defect mentioning 'GCPnts_AbscissaPoint::Length', '0.5 * Precision::Confusion'
- **Branch 6** @ line 2409 — *abscissa_point_failed* — COVERED by: in014
  - What it tests: AbscissaPoint calculation fails (IsDone false)
  - Repair action: return false
- **Branch 7** @ line 2419 — *direction_vector_too_small* — **UNCOVERED**
  - What it tests: Direction vector modulus < 0.1*Confusion (degenerate)
  - Repair action: return false
  - Suggested fixture: defect mentioning 'aDN < 0.1 * Precision::Confusion'
- **Branch 8** @ line 2431 — *edges_not_aligned* — **UNCOVERED**
  - What it tests: Edges point opposite directions or angle > maxSine
  - Repair action: return false
  - Suggested fixture: defect mentioning 'aDs[0] * aDs[1] < 0', 'CrossSquareMagnitude'
- **Branch 9** @ line 2454 — *whole_edge_in_tail* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Tail endpoint distance <= aTol2 (whole edge in tail zone)
  - Repair action: continue to next edge (mark as whole)
- **Branch 10** @ line 2459 — *partial_tail_defect* — **UNCOVERED**
  - What it tests: Tail endpoint distance > aTol2 (partial tail, needs cutting)
  - Repair action: binary search for tail bounds
  - Suggested fixture: defect mentioning 'isWholes[aEI] = false', 'for(;;)'
- **Branch 11** @ line 2471 — *tail_bound_convergence* — **UNCOVERED**
  - What it tests: Distance at midpoint <= aTol2 (converging toward start)
  - Repair action: move aParam1 forward
  - Suggested fixture: defect mentioning 'if (aDist <= aTol2)', 'aParam1 = aParam'
- **Branch 12** @ line 2478 — *tail_bound_at_aTol3* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: Distance at midpoint in [aTol2, aTol3] (convergence criterion met)
  - Repair action: break binary search loop
- **Branch 13** @ line 2503 — *tail_sampling_violation* — COVERED by: ad086, gb001, gb002, gb003, gb004, gn010, gn024, gn025 (+55 more)
  - What it tests: Any sampled point along tail bound exceeds aTol4
  - Repair action: return false (tail defect too large)
- **Branch 14** @ line 2511 — *both_edges_removable* — **UNCOVERED**
  - What it tests: Both edges are whole tails and endpoints close (<=aSqTol3)
  - Repair action: assign both edges for removal, return true
  - Suggested fixture: defect mentioning 'isWholes[0] && isWholes[1]', 'theEdge11 = theEdge1'
- **Branch 15** @ line 2520 — *one_or_both_edges_partial* — **UNCOVERED**
  - What it tests: At least one edge is not whole (needs cutting)
  - Repair action: determine which edge to remove vs cut
  - Suggested fixture: defect mentioning 'if (isWholes[0] || isWholes[1])', 'aFI = isWholes[0] ? 0 : 1'
- **Branch 16** @ line 2524 — *swapcut_strategy* — **UNCOVERED**
  - What it tests: Other edge has smaller distance and is whole (better to remove it)
  - Repair action: swap which edge to remove
  - Suggested fixture: defect mentioning 'aDists[1 - aFI] < aDists[aFI]', 'aFI = 1 - aFI'
- **Branch 17** @ line 2538 — *cut_at_edge_end* — **UNCOVERED**
  - What it tests: Cut point at or near edge end (within PConfusion)
  - Repair action: remove entire edge (aResults=2)
  - Suggested fixture: defect mentioning 'std::abs(aParams[aEI] - aLs[aEI][1 - aVIs[aEI]]) <= Precision::PConfusion'
- **Branch 18** @ line 2543 — *cut_at_edge_start* — **UNCOVERED**
  - What it tests: Cut point at or near edge start (within PConfusion)
  - Repair action: no part kept (aResults=0)
  - Suggested fixture: defect mentioning 'std::abs(aParams[aEI] - aLs[aEI][aVIs[aEI]]) <= Precision::PConfusion'
- **Branch 19** @ line 2552 — *skip_already_decided* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge already decided (aResults != 1)
  - Repair action: continue to next edge
- **Branch 20** @ line 2578 — *tail_part_zero_length* — **UNCOVERED**
  - What it tests: Tail part after cutting has zero length (Mass <= Confusion)
  - Repair action: remove entire edge instead (aResults=2)
  - Suggested fixture: defect mentioning 'aLinProps.Mass() <= Precision::Confusion()', 'aResults[aEI] = 2'
- **Branch 21** @ line 2586 — *keep_part_zero_length* — **UNCOVERED**
  - What it tests: Kept part after cutting has zero length
  - Repair action: remove entire edge (aResults=0)
  - Suggested fixture: defect mentioning 'aLinProps.Mass() <= Precision::Confusion()', 'aResults[aEI] = 0'
- **Branch 22** @ line 2592 — *both_parts_valid* — **UNCOVERED**
  - What it tests: Both parts have non-zero length (cut is valid)
  - Repair action: keep both cut parts
  - Suggested fixture: defect mentioning '*aEParts[aEI][0] = aEParts2[0]', '*aEParts[aEI][1] = aEParts2[1]'
- **Branch 23** @ line 2598 — *has_valid_cuts* — **UNCOVERED**
  - What it tests: At least one edge produced valid result (sum != 0)
  - Repair action: return true
  - Suggested fixture: defect mentioning 'aResults[0] + aResults[1] != 0'

#### `ShapeAnalysis_Wire.Perform` — lines 220–231
(8 branches, 8 covered.)

- **Branch 1** @ line 222 — *wire_ordering* — COVERED by: twi064
  - What it tests: Detects edges in wrong order (overlapping/reversed connectivity)
  - Repair action: Reorders edges to form valid closed loop via CheckOrder
- **Branch 2** @ line 223 — *small_edge* — COVERED by: tfa010, tfa046, tfa047, tfa048, tfa049, tfa050, twi057, twi058 (+1 more)
  - What it tests: Detects edges shorter than tolerance threshold
  - Repair action: Removes or splits small edges via CheckSmall
- **Branch 3** @ line 224 — *vertex_discontinuity* — COVERED by: twi064
  - What it tests: Detects gap between edge endpoints and next edge start
  - Repair action: Adjusts vertices/tolerance via CheckConnected
- **Branch 4** @ line 225 — *curve_parameter_mismatch* — COVERED by: twi064, twi065
  - What it tests: Detects 3D/2D curve mismatch or seam edges
  - Repair action: Rebuilds curves or fixes seams via CheckEdgeCurves
- **Branch 5** @ line 226 — *degenerate_edge* — COVERED by: twi064
  - What it tests: Detects zero-length or collapsed edges
  - Repair action: Splits or removes degenerate edges via CheckDegenerated
- **Branch 6** @ line 227 — *self_intersection* — COVERED by: twi064
  - What it tests: Detects edge self-intersections or edge-edge overlaps
  - Repair action: Splits at intersections via CheckSelfIntersection
- **Branch 7** @ line 228 — *missing_segment* — COVERED by: twi064, twi067
  - What it tests: Detects topological gaps (missing connecting edges)
  - Repair action: Inserts gap-closing curves via CheckLacking
- **Branch 8** @ line 229 — *open_wire* — COVERED by: twi064, twi066
  - What it tests: Detects start/end vertex mismatch in presumed closed wire
  - Repair action: Closes loop or extends edges via CheckClosed


### `src/ModelingAlgorithms/TKShHealing/ShapeAnalysis/ShapeAnalysis_WireOrder.cxx`

6 methods, 34 branches, 10 covered.

#### `ShapeAnalysis_WireOrder.Add (2D overload)` — lines 135–144
(2 branches, 0 covered.)

- **Branch 1** @ line 136 — *mode_guard* — **UNCOVERED**
  - What it tests: Detection of 2D-only mode constraint
  - Repair action: Only appends 2D edge points when mode is Mode2D
  - Suggested fixture: defect mentioning 'myMode == Mode2D', 'gp_XY', '2D coordinates'
- **Branch 2** @ line 138 — *coordinate_lifting* — **UNCOVERED**
  - What it tests: Conversion of 2D points to 3D with Z=0
  - Repair action: Embeds 2D coordinates as 3D with zero Z-component
  - Suggested fixture: defect mentioning 'SetCoord', 'Z = 0.0', '2D->3D embedding'

#### `ShapeAnalysis_WireOrder.Add (ModeBoth overload)` — lines 152–161
(3 branches, 0 covered.)

- **Branch 1** @ line 153 — *mode_guard* — **UNCOVERED**
  - What it tests: Detection of dual-mode 3D+2D constraint
  - Repair action: Only appends both 3D and 2D coordinates in ModeBoth
  - Suggested fixture: defect mentioning 'myMode == ModeBoth', 'dual coordinates', 'parallel storage'
- **Branch 2** @ line 155 — *coordinate_storage* — **UNCOVERED**
  - What it tests: Storage of 3D start/end points in ModeBoth
  - Repair action: Appends 3D points sequentially
  - Suggested fixture: defect mentioning 'myXYZ', 'gp_XYZ', '3D edge points'
- **Branch 3** @ line 158 — *coordinate_storage* — **UNCOVERED**
  - What it tests: Storage of 2D start/end points in ModeBoth
  - Repair action: Appends 2D points sequentially in parallel array
  - Suggested fixture: defect mentioning 'myXY', 'gp_XY', '2D edge points'

#### `ShapeAnalysis_WireOrder.Gap` — lines 747–758
(3 branches, 2 covered.)

- **Branch 1** @ line 748 — *total_vs_pair_gap* — **UNCOVERED**
  - What it tests: Global gap vs pairwise gap selection
  - Repair action: Returns total gap for num=0, pairwise gap otherwise
  - Suggested fixture: defect mentioning 'if (num == 0)', 'myGap', 'total gap'
- **Branch 2** @ line 752 — *cyclic_indexing* — COVERED by: a012, ad004, ad005, ad026, ad027, ad031, ad032, ad035 (+29 more)
  - What it tests: Wraparound gap calculation at wire end
  - Repair action: Maps num=1 to last edge for cyclic gap calc
- **Branch 3** @ line 755 — *index_negation* — COVERED by: ps013
  - What it tests: Edge reversal handling in gap distance
  - Repair action: Handles both forward and reversed edge indices

#### `ShapeAnalysis_WireOrder.Perform` — lines 206–690
(20 branches, 7 covered.)

- **Branch 1** @ line 210 — *empty_input* — COVERED by: ad015, ad050, ad086, sw007, tfa002, tfa045, tsh023, tsh037 (+2 more)
  - What it tests: Detection of wire with zero edges
  - Repair action: Early return when no edges added
- **Branch 2** @ line 226 — *coordinate_extraction* — COVERED by: gp002, gs021, n009, n043, twi099
  - What it tests: Edge begin/end point indexing (start/end pairs)
  - Repair action: Extracts 3D coordinates from input sequence
- **Branch 3** @ line 230 — *mode_dispatch* — **UNCOVERED**
  - What it tests: ModeBoth coordinate extraction
  - Repair action: Extracts both 3D and 2D coordinates when in ModeBoth
  - Suggested fixture: defect mentioning 'myMode == ModeBoth', '2D extraction', 'parallel load'
- **Branch 4** @ line 257 — *iteration_control* — COVERED by: ad004, ad026, ad052, ad053, ad077, ad086, ad099, m141 (+10 more)
  - What it tests: Main loop for constructing edge chains
  - Repair action: Iterates until all edges are chained
- **Branch 5** @ line 292 — *tail_joint_selection* — **UNCOVERED**
  - What it tests: Tail connection joint type (direct vs reversed)
  - Repair action: Chooses joint type 0 or 2 based on distance
  - Suggested fixture: defect mentioning 'aTailJoinType', 'aSeqTailEdgeHead', 'aSeqTailEdgeTail'
- **Branch 6** @ line 302 — *head_joint_selection* — **UNCOVERED**
  - What it tests: Head connection joint type (direct vs reversed)
  - Repair action: Chooses joint type 1 or 3 based on distance
  - Suggested fixture: defect mentioning 'aHeadJointType', 'aSeqHeadEdgeTail', 'aSeqHeadEdgeHead'
- **Branch 7** @ line 314 — *tolerance_tie_break* — COVERED by: tb017, wr025
  - What it tests: Tie-breaking when head/tail distances within tolerance
  - Repair action: Selects joint with lowest type number when distances equal
- **Branch 8** @ line 341 — *modeboth_2d_check* — **UNCOVERED**
  - What it tests: ModeBoth 2D distance calculation
  - Repair action: Performs parallel 2D distance check in ModeBoth mode
  - Suggested fixture: defect mentioning 'myMode == ModeBoth', '2D distance', 'joint mask'
- **Branch 9** @ line 384 — *joint_consensus* — **UNCOVERED**
  - What it tests: Joint type consensus between 3D and 2D (ModeBoth)
  - Repair action: Selects joint only when both 3D and 2D agree
  - Suggested fixture: defect mentioning 'aFullMask = aJointMask3D & aJointMask2D', 'consensus', 'dual-mode agreement'
- **Branch 10** @ line 396 — *connected_state* — COVERED by: ad086, bo004, bo022, gp034, n040, os004, pmi069, pmi105 (+8 more)
  - What it tests: Connected edge detection in ModeBoth
  - Repair action: Sets connected flag when joint masks overlap
- **Branch 11** @ line 427 — *distance_or_joint_priority* — **UNCOVERED**
  - What it tests: Decision: accept by distance OR by joint type
  - Repair action: Selects edge based on distance/joint type priority
  - Suggested fixture: defect mentioning 'aBestMin3D > aTol2', 'aCurJointType < aBestJointType', 'priority rule'
- **Branch 12** @ line 445 — *edge_found_check* — **UNCOVERED**
  - What it tests: Verification that best edge candidate exists
  - Repair action: Processes found edge or breaks loop
  - Suggested fixture: defect mentioning 'if (isFound)', 'edge found', 'iteration continuation'
- **Branch 13** @ line 451 — *append_vs_close* — **UNCOVERED**
  - What it tests: Decision: append edge to chain OR close loop
  - Repair action: Compares edge distance vs loop-close distance
  - Suggested fixture: defect mentioning 'aBestMin3D <= RealSmall()', 'aBestMin3D < aCloseDist', 'append vs close'
- **Branch 14** @ line 453 — *joint_execution* — **UNCOVERED**
  - What it tests: Four joint types dispatch (0=tail, 1=head, 2=reverse, 3=reverse+head)
  - Repair action: Executes edge append/prepend and reversal per joint type
  - Suggested fixture: defect mentioning 'switch (aBestJointType)', 'case 0', 'case 1'
- **Branch 15** @ line 472 — *modeboth_2d_update* — **UNCOVERED**
  - What it tests: ModeBoth 2D coordinate update per joint type
  - Repair action: Updates 2D head/tail markers per joint action
  - Suggested fixture: defect mentioning 'myMode == ModeBoth', '2D update', 'parallel state'
- **Branch 16** @ line 519 — *loop_merging_mode* — **UNCOVERED**
  - What it tests: Keep-loops vs merge-loops decision
  - Repair action: Either preserves loops independently or merges them
  - Suggested fixture: defect mentioning 'myKeepLoops', 'loop merging', 'independent loops'
- **Branch 17** @ line 542 — *loop_pairing* — **UNCOVERED**
  - What it tests: Iteration over loop gaps for closest pair finding
  - Repair action: Searches all gaps in current loop for best attachment
  - Suggested fixture: defect mentioning 'for (int aLoopIt = 1', 'aLoops.Value()', 'loop iteration'
- **Branch 18** @ line 586 — *direct_vs_reverse* — COVERED by: ps001, ps002
  - What it tests: Direct vs reversed loop connection decision
  - Repair action: Chooses orientation based on distance comparison
- **Branch 19** @ line 642 — *order_change_detection* — COVERED by: a032, ls010, twi007, twi028, twi038, twi078, wr039
  - What it tests: Detection of any reordering vs original order
  - Repair action: Sets status=1/-1 if any edge changed position or reversal
- **Branch 20** @ line 656 — *cyclic_shift_detection* — **UNCOVERED**
  - What it tests: Distinction between reordering vs cyclic shift
  - Repair action: Detects forward or reverse cyclic permutation
  - Suggested fixture: defect mentioning 'isShiftForward', 'isShiftReverse', 'cyclic permutation'

#### `ShapeAnalysis_WireOrder.SetMode` — lines 75–102
(4 branches, 0 covered.)

- **Branch 1** @ line 78 — *mode_selection* — **UNCOVERED**
  - What it tests: Detection of ModeBoth mode selection path
  - Repair action: Sets mode to ModeBoth instead of Mode3D/Mode2D
  - Suggested fixture: defect mentioning 'theModeBoth', 'ModeBoth', 'mode type dispatch'
- **Branch 2** @ line 84 — *mode_selection* — **UNCOVERED**
  - What it tests: Detection of Mode3D vs Mode2D branch
  - Repair action: Sets mode to Mode3D based on boolean flag
  - Suggested fixture: defect mentioning 'theMode3D', 'Mode3D', 'mode type dispatch'
- **Branch 3** @ line 93 — *state_invalidation* — **UNCOVERED**
  - What it tests: Mode change detection triggering reset
  - Repair action: Clears accumulated edge data when mode changes
  - Suggested fixture: defect mentioning 'myMode', 'aNewMode', 'Clear()'
- **Branch 4** @ line 101 — *tolerance_clamping* — **UNCOVERED**
  - What it tests: Negative or zero tolerance fallback
  - Repair action: Clamps tolerance to 1.e-08 minimum
  - Suggested fixture: defect mentioning 'theTolerance', '> 0.0', 'tolerance validation'

#### `ShapeAnalysis_WireOrder.XY` — lines 729–742
(2 branches, 1 covered.)

- **Branch 1** @ line 730 — *mode_dispatch* — **UNCOVERED**
  - What it tests: ModeBoth mode detection for XY extraction
  - Repair action: Uses stored 2D coordinates in ModeBoth vs extracted from 3D
  - Suggested fixture: defect mentioning 'myMode == ModeBoth', 'XY extraction', 'mode dispatch'
- **Branch 2** @ line 732 — *index_negation* — COVERED by: ad044, ls035, ps013, tsh012, twi062, twi097
  - What it tests: Edge reversal encoding (positive=forward, negative=reversed)
  - Repair action: Swaps start/end when edge index is negative


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_ComposeShell.cxx`

14 methods, 223 branches, 80 covered.

#### `ShapeFix_ComposeShell.BreakWires` — lines 2279–2385
(8 branches, 4 covered.)

- **Branch 1** @ line 2290 — *EXTERNAL/INTERNAL wire filter for split candidates* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wire orientation is EXTERNAL or INTERNAL
  - Repair action: Collect vertices from EXTERNAL/INTERNAL wires for splitting others
- **Branch 2** @ line 2300 — *EXTERNAL edge endpoint collection* — **UNCOVERED**
  - What it tests: Individual edge within INTERNAL wire has EXTERNAL orientation
  - Repair action: Add edge endpoints to split-vertex set
  - Suggested fixture: defect mentioning 'ori_edge == TopAbs_EXTERNAL', 'splitVertices.Add'
- **Branch 3** @ line 2314 — *Vertex-only wire skip* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wire is a single vertex (no edge content)
  - Repair action: Skip from wire-breaking loop, continue to next
- **Branch 4** @ line 2330 — *No split vertices found in wire* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: No edge endpoint in wire matches any split-vertex
  - Repair action: Keep wire intact, continue to next wire
- **Branch 5** @ line 2337 — *Closed wire permutation for split alignment* — COVERED by: ad086, ad091, gp011, gp012, gp016, gp023, gp026, gp029 (+30 more)
  - What it tests: Closed wire and first split vertex is not at start
  - Repair action: Calculate shift to rotate wire so split starts at index 1
- **Branch 6** @ line 2370 — *INTERNAL wire with EXTERNAL edge orientation mismatch* — **UNCOVERED**
  - What it tests: Wire is INTERNAL but contains an EXTERNAL-oriented edge
  - Repair action: Change edge to FORWARD, mark as new sub-wire
  - Suggested fixture: defect mentioning 'ori == TopAbs_INTERNAL', 'edge.Orientation() == TopAbs_EXTERNAL'
- **Branch 7** @ line 2356 — *Wire segment accumulation and flush on split-vertex* — **UNCOVERED**
  - What it tests: Current edge starts at split-vertex or is first edge
  - Repair action: Finalize accumulated segment, insert into sequence, start new segment
  - Suggested fixture: defect mentioning 'splitVertices.Contains(V)', 'seqw.InsertBefore'
- **Branch 8** @ line 2378 — *New sub-wires created* — **UNCOVERED**
  - What it tests: At least one sub-wire was created (nbnew > 0)
  - Repair action: Update original wire with final accumulated segment
  - Suggested fixture: defect mentioning 'if (nbnew)', 'seqw.SetValue'

#### `ShapeFix_ComposeShell.CollectWires` — lines 2512–2881
(29 branches, 7 covered.)

- **Branch 1** @ line 2521 — *Vertex-only wire passthrough* — COVERED by: a004, a011, a067, ad038, ad086, ad098, ad101, gs009 (+42 more)
  - What it tests: Wire is vertex or INTERNAL orientation
  - Repair action: Add to output without modification, remove from input
- **Branch 2** @ line 2537 — *Short segment classification* — **UNCOVERED**
  - What it tests: Wire segment is short in 3D (below size threshold)
  - Repair action: Mark in shorts array for priority during connection
  - Suggested fixture: defect mentioning 'IsShortSegment', 'shorts.SetValue'
- **Branch 3** @ line 2539 — *Short segment removal - EXTERNAL wire case* — COVERED by: m026, m109, os002, pmi053, sw003, tfa005, twi021, twi064 (+2 more)
  - What it tests: Short segment with EXTERNAL orientation or degenerated edge
  - Repair action: Change to INTERNAL orientation (mark for skipping)
- **Branch 4** @ line 2584 — *First segment selection priority* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: No wire started yet (sbwd.IsNull()), pick first non-short, non-external wire
  - Repair action: Initialize wire collection, record first vertex/tangent/patch
- **Branch 5** @ line 2590 — *First segment reject - EXTERNAL orientation* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: First candidate is EXTERNAL (seam edge)
  - Repair action: Skip this segment, look for next
- **Branch 6** @ line 2594 — *First segment orientation reversal* — **UNCOVERED**
  - What it tests: First segment is FORWARD oriented
  - Repair action: Mark for reversal before adding to collection
  - Suggested fixture: defect mentioning 'reverse = true'
- **Branch 7** @ line 2607 — *Segment connectivity on same patch check* — **UNCOVERED**
  - What it tests: Current segment overlaps patch range with previous
  - Repair action: Weight segment higher (samepatch=true) vs off-patch candidates
  - Suggested fixture: defect mentioning 'IsSamePatch', 'samepatch'
- **Branch 8** @ line 2611 — *Off-patch segment filtering* — **UNCOVERED**
  - What it tests: Not same patch AND (wire can close OR samepatch already found)
  - Repair action: Skip this segment, lower priority
  - Suggested fixture: defect mentioning '!sp && (canBeClosed || (index && samepatch))'
- **Branch 9** @ line 2629 — *Vertex-based segment connection attempt* — **UNCOVERED**
  - What it tests: Segment start or end vertex matches previous wire endpoint
  - Repair action: Evaluate connection quality (weighting by patch, orientation, tangent)
  - Suggested fixture: defect mentioning 'endV.IsSame', 'j ? seg.LastVertex() : seg.FirstVertex()'
- **Branch 10** @ line 2639 — *Avoid returning by same edge* — **UNCOVERED**
  - What it tests: Next segment's start/end edge is same as previous wire's last/first edge
  - Repair action: Lowest priority unless no other connection exists
  - Suggested fixture: defect mentioning 'lastEdge.IsSame', 'weigth = (sp ? 16 : 0)'
- **Branch 11** @ line 2665 — *Missing 2D tangent on edge* — **UNCOVERED**
  - What it tests: Cannot compute 2D tangent from edge curve
  - Repair action: Set status FAIL2, continue with other edges
  - Suggested fixture: defect mentioning '!sae.GetEndTangent2d', 'ShapeExtend_FAIL2'
- **Branch 12** @ line 2675 — *Periodic surface tangent adjustment* — **UNCOVERED**
  - What it tests: myClosedMode with U or V periodicity, tangent point needs shift
  - Repair action: Adjust tangent point by period to align with previous endpoint
  - Suggested fixture: defect mentioning 'myClosedMode', 'AdjustByPeriod', 'shiftu'
- **Branch 13** @ line 2690 — *Short segment tangent angle priority* — **UNCOVERED**
  - What it tests: Segment is short (priority weighting)
  - Repair action: Use PI as angle to override standard angle weighting
  - Suggested fixture: defect mentioning 'shorts(i) > 0 ? M_PI : endTan.Angle(lVec)'
- **Branch 14** @ line 2691 — *Anti-backtrack angle rejection* — **UNCOVERED**
  - What it tests: Tangent nearly opposite (M_PI radians), myClosedMode, non-short segment
  - Repair action: Set angle to 0 to prevent returning by same path
  - Suggested fixture: defect mentioning 'M_PI - ang < ::Precision::Angular()', 'ang = 0'
- **Branch 15** @ line 2701 — *2D coincidence check for connection validity* — COVERED by: a031, a038, ad086, ad094, ad101, bo001, bo002, bo003 (+96 more)
  - What it tests: Tangent points lie within edge/vertex tolerance in 2D
  - Repair action: Mark as connected (higher weight) vs disconnected (distance-based)
- **Branch 16** @ line 2705 — *Connection weight evaluation and prioritization* — **UNCOVERED**
  - What it tests: Multi-factor comparison: same-patch, connection, orientation, distance, angle
  - Repair action: Update best candidate if weight or tail metrics improve
  - Suggested fixture: defect mentioning 'w1 + tail1 <= weigth + tail2', 'index = i'
- **Branch 17** @ line 2729 — *Misoriented segment repair* — **UNCOVERED**
  - What it tests: Selected segment has wrong orientation relative to wire sequence
  - Repair action: Set myInvertEdgeStatus flag for post-processing
  - Suggested fixture: defect mentioning 'if (misoriented)', 'myInvertEdgeStatus = true'
- **Branch 18** @ line 2738 — *Patch index extension for same-patch segments* — **UNCOVERED**
  - What it tests: New segment is on same patch, extends patch range
  - Repair action: Update iumin/iumax/ivmin/ivmax to encompass new segment
  - Suggested fixture: defect mentioning 'samepatch', 'IsSamePatch(..., true)'
- **Branch 19** @ line 2752 — *Closed-mode seam-crossing detection* — **UNCOVERED**
  - What it tests: myClosedMode && segment may cross seam boundary
  - Repair action: Re-query patch index to detect seam position
  - Suggested fixture: defect mentioning 'myClosedMode', 'seg.GetPatchIndex'
- **Branch 20** @ line 2758 — *Wire segment reversal before addition* — COVERED by: a024, a034, ad027, ad047, ad086, bo005, gb003, gs001 (+50 more)
  - What it tests: Segment needs reversal to match wire direction
  - Repair action: Create reversed wire data, add to collection
- **Branch 21** @ line 2770 — *EXTERNAL wire orientation update* — **UNCOVERED**
  - What it tests: Added segment has EXTERNAL orientation
  - Repair action: Convert to FORWARD/REVERSED based on reverse flag
  - Suggested fixture: defect mentioning 'seg.Orientation() == TopAbs_EXTERNAL'
- **Branch 22** @ line 2785 — *First wire segment endpoint capture* — **UNCOVERED**
  - What it tests: endV.IsNull(), first segment added
  - Repair action: Record first edge, vertex, and 2D tangent for closure detection
  - Suggested fixture: defect mentioning 'endV.IsNull()', 'firstEdge', 'firstV'
- **Branch 23** @ line 2794 — *Short segment tangent update suppression* — **UNCOVERED**
  - What it tests: Segment is short OR wire starting (short segments don't update endpoint)
  - Repair action: Skip tangent/endpoint update for short segments
  - Suggested fixture: defect mentioning 'doupdate = (index && (shorts(index) <= 0 || endV.IsNull()))'
- **Branch 24** @ line 2814 — *Periodic surface endpoint adjustment* — COVERED by: ad084, ad086, fi001, in014, tfa070
  - What it tests: myUClosed/myVClosed with shift from earlier connection
  - Repair action: Apply shift to endpoint for periodic wrapping
- **Branch 25** @ line 2825 — *Wire closure detection at first vertex* — **UNCOVERED**
  - What it tests: Current endpoint matches first vertex
  - Repair action: Set canBeClosed=true, prepare to finalize wire
  - Suggested fixture: defect mentioning 'endV.IsSame(firstV)'
- **Branch 26** @ line 2827 — *Seam-edge closure without endpoint match* — **UNCOVERED**
  - What it tests: Seam surface (cylinder), endpoint near first point but vertex mismatch
  - Repair action: Accept as closed if 2D points coincide within tolerance
  - Suggested fixture: defect mentioning '!lastEdge.IsSame(firstEdge)', 'IsCoincided'
- **Branch 27** @ line 2830 — *Unclosed wire endpoint mismatch warning* — **UNCOVERED**
  - What it tests: Wire closed but endpoint vertex does not match first vertex
  - Repair action: Log FAIL5 status, continue (non-critical)
  - Suggested fixture: defect mentioning '!endV.IsSame(sae.FirstVertex(firstEdge))', 'ShapeExtend_FAIL5'
- **Branch 28** @ line 2853 — *3D-short segment merging candidate filter* — **UNCOVERED**
  - What it tests: Segment marked as 3D-short, not vertex-only, not INTERNAL/EXTERNAL
  - Repair action: Look for host wire containing same vertex for insertion
  - Suggested fixture: defect mentioning 'shorts(i) == 1', 'wires.Length()'
- **Branch 29** @ line 2880 — *Same-vertex insertion point in host wire* — **UNCOVERED**
  - What it tests: Host wire edge starts with short segment's first vertex
  - Repair action: Mark for insertion into that position
  - Suggested fixture: defect mentioning 'V.IsSame(sae.FirstVertex(sbwd->Edge(k)))'

#### `ShapeFix_ComposeShell.ComputeCode` — lines 654–832
(14 branches, 4 covered.)

- **Branch 1** @ line 661 — *closed_segment_detection* — COVERED by: a025, a095, ad086, gn020, gp030, gs040, hea008, hea012 (+6 more)
  - What it tests: Segment starts at end of edge and ends at start (special closed)
  - Repair action: Set special=1 flag for closed segment handling
- **Branch 2** @ line 667 — *zero_length_segment_closed* — **UNCOVERED**
  - What it tests: Segment has zero length in closed mode
  - Repair action: Set special=1 for handling
  - Suggested fixture: defect mentioning 'begPar == endPar', 'myClosedMode'
- **Branch 3** @ line 687 — *wraparound_iteration* — **UNCOVERED**
  - What it tests: Edge index wraps around wire (i > nb)
  - Repair action: Reset to wire start (i = 1) for circular iteration
  - Suggested fixture: defect mentioning 'i > nb', 'i = 1'
- **Branch 4** @ line 695 — *missing_pcurve* — COVERED by: a024, ad046, ad050, ad086, ad099, ad101, fi002, gb004 (+130 more)
  - What it tests: Edge has no 2D curve on face
  - Repair action: Set FAIL3 status; skip edge from analysis
- **Branch 5** @ line 706 — *near_zero_dpar* — COVERED by: tb007
  - What it tests: Parameter span negligible relative to tolerance
  - Repair action: Use single point (NPOINTS=1) instead of sample
- **Branch 6** @ line 714 — *closed_mode_u_direction* — **UNCOVERED**
  - What it tests: Closed mode handling for U-direction lines
  - Repair action: Adjust X coordinate by period for wraparound
  - Suggested fixture: defect mentioning 'myClosedMode', 'myUClosed', 'AdjustByPeriod'
- **Branch 7** @ line 726 — *closed_mode_v_direction* — **UNCOVERED**
  - What it tests: Closed mode handling for V-direction lines
  - Repair action: Adjust Y coordinate by period for wraparound
  - Suggested fixture: defect mentioning 'myVClosed', 'AdjustByPeriod'
- **Branch 8** @ line 742 — *undefined_point_position* — **UNCOVERED**
  - What it tests: Point-to-line position is undefined
  - Repair action: Skip point from tangency analysis
  - Suggested fixture: defect mentioning 'PointLinePosition', 'pos == IOR_UNDEF'
- **Branch 9** @ line 749 — *deviation_exceeds_tolerance* — **UNCOVERED**
  - What it tests: Point deviation from line exceeds tolerance
  - Repair action: Mark as non-tangency; set code from position
  - Suggested fixture: defect mentioning 'IsCoincided', 'code = pos'
- **Branch 10** @ line 767 — *end_index_reached* — **UNCOVERED**
  - What it tests: Edge iteration reached end segment
  - Repair action: Break if not special; set special=-1 if special
  - Suggested fixture: defect mentioning 'i == endInd'
- **Branch 11** @ line 785 — *periodic_u_full_wrap* — **UNCOVERED**
  - What it tests: U-periodic segment deviation approximates full period
  - Repair action: Classify as IOR_BOTH with sign marking
  - Suggested fixture: defect mentioning 'myUPeriod', 'IOR_BOTH'
- **Branch 12** @ line 800 — *periodic_v_full_wrap* — **UNCOVERED**
  - What it tests: V-periodic segment deviation approximates full period
  - Repair action: Classify as IOR_BOTH with sign marking
  - Suggested fixture: defect mentioning 'myVPeriod', 'IOR_BOTH'
- **Branch 13** @ line 818 — *tangency_classification* — **UNCOVERED**
  - What it tests: All sampled points are tangent to line
  - Repair action: Return IOR_UNDEF (tangency)
  - Suggested fixture: defect mentioning 'if (i)', 'code = IOR_UNDEF'
- **Branch 14** @ line 822 — *parity_error_both_sides* — COVERED by: twi066
  - What it tests: Parity error: intersection marked BOTH sides
  - Repair action: Downgrade to LEFT; set FAIL2 status

#### `ShapeFix_ComposeShell.DispatchWires` — lines 3277–3584
(32 branches, 13 covered.)

- **Branch 1** @ line 3281 — *CLOSED_SURFACE_MODE* — **UNCOVERED**
  - What it tests: Surface is closed (periodic in U/V)
  - Repair action: Pre-process wires via FixShifted to resolve seam pcurves
  - Suggested fixture: defect mentioning 'myClosedMode'
- **Branch 2** @ line 3291 — *WIRE_VERTEX_SKIP* — **UNCOVERED**
  - What it tests: Wire segment is a VERTEX, not a WIRE
  - Repair action: Skip processing, continue
  - Suggested fixture: defect mentioning 'IsVertex()'
- **Branch 3** @ line 3300 — *SEAM_EDGE_REVERSED* — COVERED by: ad086, tsh007
  - What it tests: Edge is REVERSED orientation and marked as seam (IsClosed)
  - Repair action: Extract both pcurves and check for offset/alignment
- **Branch 4** @ line 3312 — *SEAM_PCURVE_IDENTITY* — COVERED by: ad086, ad091, gp011, gp012, gp016, gp023, gp026, gp029 (+30 more)
  - What it tests: Both sides of seam are same or have endpoint collision
  - Repair action: Compute shift in U/V period to separate pcurves
- **Branch 5** @ line 3315 — *U_PERIOD_WRAP* — **UNCOVERED**
  - What it tests: U-direction has periodicity and endpoints close in U
  - Repair action: Apply U-period shift to second pcurve
  - Suggested fixture: defect mentioning 'myUClosed', 'std::abs', 'myUPeriod'
- **Branch 6** @ line 3319 — *V_PERIOD_WRAP* — **UNCOVERED**
  - What it tests: V-direction has periodicity and endpoints close in V
  - Repair action: Apply V-period shift to second pcurve
  - Suggested fixture: defect mentioning 'myVClosed', 'myVPeriod'
- **Branch 7** @ line 3331 — *WIRE_VERTEX_SKIP_2* — **UNCOVERED**
  - What it tests: Wire segment is VERTEX in second loop
  - Repair action: Skip and continue
  - Suggested fixture: defect mentioning 'IsVertex()'
- **Branch 8** @ line 3339 — *DEGENERATE_SINGLE_EDGE* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+41 more)
  - What it tests: Wire has single degenerated edge only
  - Repair action: Remove wire from processing, continue
- **Branch 9** @ line 3346 — *FIXSHIFTED_PROCESSING* — **UNCOVERED**
  - What it tests: Apply FixShifted to resolve shifted/offset pcurves
  - Repair action: Invoke ShapeFix_Wire::FixShifted()
  - Suggested fixture: defect mentioning 'sfw.FixShifted()'
- **Branch 10** @ line 3352 — *DEGENERATE_PCURVE_CLEAR* — COVERED by: ad086, m026, m109, os002, pmi053, sw003, tfa005, twi021 (+3 more)
  - What it tests: Degenerated edges need pcurve recomputation
  - Repair action: Clear pcurves via ShapeBuild_Edge::RemovePCurve
- **Branch 11** @ line 3358 — *DEGENERATE_FIX* — **UNCOVERED**
  - What it tests: Apply degenerated edge fixing
  - Repair action: Invoke ShapeFix_Wire::FixDegenerated()
  - Suggested fixture: defect mentioning 'sfw.FixDegenerated()'
- **Branch 12** @ line 3367 — *EMPTY_WIRE_SEQUENCE* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: No wires to process after all filters
  - Repair action: Return early, no faces to create
- **Branch 13** @ line 3391 — *U_PERIOD_ADJUSTMENT* — **UNCOVERED**
  - What it tests: Wire center point needs U-wrapping for periodic surface
  - Repair action: Compute U-shift and adjust point coordinates
  - Suggested fixture: defect mentioning 'myUClosed', 'AdjustToPeriod'
- **Branch 14** @ line 3396 — *V_PERIOD_ADJUSTMENT* — **UNCOVERED**
  - What it tests: Wire center point needs V-wrapping for periodic surface
  - Repair action: Compute V-shift and adjust point coordinates
  - Suggested fixture: defect mentioning 'myVClosed', 'AdjustToPeriod'
- **Branch 15** @ line 3408 — *PARAMETRIC_TRANSFORM_NEEDED* — **UNCOVERED**
  - What it tests: Wire requires transformation to local patch coordinates
  - Repair action: Compute GlobalToLocalTransformation if needed
  - Suggested fixture: defect mentioning 'needT', 'GlobalToLocalTransformation'
- **Branch 16** @ line 3409 — *SHIFT_TRANSLATION_APPLY* — **UNCOVERED**
  - What it tests: Both U and V shifts need to be applied
  - Repair action: Compose translation transform with parametric transform
  - Suggested fixture: defect mentioning 'ush != 0. || vsh != 0.', 'SetTranslation'
- **Branch 17** @ line 3416 — *WIRE_VERTEX_SKIP_3* — **UNCOVERED**
  - What it tests: Wire is VERTEX, skip edge processing
  - Repair action: Skip edge loop, continue
  - Suggested fixture: defect mentioning 'IsVertex()'
- **Branch 18** @ line 3438 — *EDGE_ALREADY_COPIED* — **UNCOVERED**
  - What it tests: Edge was already processed and recorded in reshape context
  - Repair action: Retrieve recorded edge from reshape context
  - Suggested fixture: defect mentioning 'rs.IsRecorded', 'rs.Value'
- **Branch 19** @ line 3446 — *NON_MANIFOLD_EDGE* — **UNCOVERED**
  - What it tests: Edge has non-manifold orientation
  - Repair action: Temporarily set FORWARD, copy, then restore orientation
  - Suggested fixture: defect mentioning 'ismanifold', 'Orientation(TopAbs_FORWARD)'
- **Branch 20** @ line 3467 — *PCURVE_TRANSFORM_NEEDED* — **UNCOVERED**
  - What it tests: Pcurve needs parametric space transformation
  - Repair action: Transform pcurve via parametric transformation matrix
  - Suggested fixture: defect mentioning 'needT', 'TransformPCurve'
- **Branch 21** @ line 3471 — *SEAM_EDGE_UPDATE* — COVERED by: ad086, tsh007
  - What it tests: Edge is seam (closed on face)
  - Repair action: Update both forward and reverse pcurves
- **Branch 22** @ line 3481 — *SEAM_FORWARD_ORIENTATION* — **UNCOVERED**
  - What it tests: Seam edge has FORWARD orientation
  - Repair action: Set forward pcurve first, then reverse
  - Suggested fixture: defect mentioning 'TopAbs_FORWARD', 'UpdateEdge'
- **Branch 23** @ line 3484 — *SEAM_REVERSE_ORIENTATION* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Seam edge has REVERSED orientation
  - Repair action: Set reverse pcurve first, then forward
- **Branch 24** @ line 3489 — *SEAM_MISSING_SECOND_PCURVE* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Seam edge missing reverse pcurve
  - Repair action: Update with single forward pcurve only
- **Branch 25** @ line 3494 — *NON_SEAM_PCURVE_UPDATE* — **UNCOVERED**
  - What it tests: Non-seam edge pcurve update
  - Repair action: UpdateEdge with single pcurve
  - Suggested fixture: defect mentioning 'UpdateEdge'
- **Branch 26** @ line 3499 — *RANGE_MISMATCH* — COVERED by: twi082, twi090
  - What it tests: Transformed pcurve has different range than original
  - Repair action: Mark edge SameRange = false to recompute
- **Branch 27** @ line 3506 — *MISSING_3D_CURVE* — COVERED by: twi047
  - What it tests: Edge lacks 3D curve or has non-matching SameRange
  - Repair action: Compute or update 3D curve via FixAddCurve3d
- **Branch 28** @ line 3509 — *NON_MANIFOLD_3D_FIX* — **UNCOVERED**
  - What it tests: Non-manifold edge needs special 3D curve handling
  - Repair action: Copy edge with FORWARD orientation for 3D curve fix
  - Suggested fixture: defect mentioning 'ismanifold', 'Oriented(TopAbs_FORWARD)'
- **Branch 29** @ line 3521 — *3D_CURVE_AVAILABLE* — COVERED by: gn017, twi046, twi047, twi059, twi062, twi065
  - What it tests: 3D curve extracted after fix attempt
  - Repair action: Update edge with extracted 3D curve and set range
- **Branch 30** @ line 3545 — *PATCH_ALREADY_USED* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wire already assigned to a patch
  - Repair action: Skip, continue to next wire
- **Branch 31** @ line 3554 — *PATCH_MISMATCH* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wire on different patch than current batch
  - Repair action: Skip wire, defer to next batch iteration
- **Branch 32** @ line 3563 — *INTERNAL_VERTEX_HOLE* — **UNCOVERED**
  - What it tests: Hole is a VERTEX with INTERNAL orientation
  - Repair action: Add INTERNAL vertex to loop collection
  - Suggested fixture: defect mentioning 'TopAbs_INTERNAL', 'loops.Append'

#### `ShapeFix_ComposeShell.Init` — lines 100–202
(10 branches, 4 covered.)

- **Branch 1** @ line 111 — *thin_face_closed_detection* — COVERED by: n010
  - What it tests: Elementary vs non-elementary surface closure detection
  - Repair action: Validate U/V closure on thin faces via 3D distance check
- **Branch 2** @ line 120 — *infinite_bounds_detection* — **UNCOVERED**
  - What it tests: Surface with infinite parametric bounds
  - Repair action: Use BRepTools::UVBounds to establish finite UV range
  - Suggested fixture: defect mentioning 'IsInfinite', 'UVBounds'
- **Branch 3** @ line 125 — *u_closure_validation* — COVERED by: ad003, ad030, ad042, ad045, ad078, ad086, gb004, gp013 (+79 more)
  - What it tests: U-direction closed surface gap detection
  - Repair action: Check 3D distance at surface edges; disable closure if gap exists
- **Branch 4** @ line 142 — *v_closure_validation* — COVERED by: ad003, ad030, ad042, ad045, ad078, ad086, gp013, gp031 (+30 more)
  - What it tests: V-direction closed surface gap detection
  - Repair action: Check 3D distance at surface edges; disable closure if gap exists
- **Branch 5** @ line 173 — *resolution_computation_u* — **UNCOVERED**
  - What it tests: U-direction resolution across grid patches
  - Repair action: Track minimum resolution via adaptor geometry analysis
  - Suggested fixture: defect mentioning 'UResolution', 'GeomAdaptor_Surface', 'NbUPatches'
- **Branch 6** @ line 176 — *resolution_computation_v* — **UNCOVERED**
  - What it tests: V-direction resolution across grid patches
  - Repair action: Track minimum resolution via adaptor geometry analysis
  - Suggested fixture: defect mentioning 'VResolution', 'NbVPatches'
- **Branch 7** @ line 184 — *u_resolution_accumulation* — **UNCOVERED**
  - What it tests: Minimum U-resolution across all patches
  - Repair action: Update myUResolution with minimum positive value
  - Suggested fixture: defect mentioning 'ures > 0', 'myUResolution'
- **Branch 8** @ line 188 — *v_resolution_accumulation* — **UNCOVERED**
  - What it tests: Minimum V-resolution across all patches
  - Repair action: Update myVResolution with minimum positive value
  - Suggested fixture: defect mentioning 'vres > 0', 'myVResolution'
- **Branch 9** @ line 194 — *u_resolution_default_fallback* — COVERED by: ad046, ad086, fi007, gn034, gn037, gn038, gp001, gp005 (+67 more)
  - What it tests: U-resolution uninitialized (RealLast)
  - Repair action: Assign default parametric precision
- **Branch 10** @ line 198 — *v_resolution_default_fallback* — **UNCOVERED**
  - What it tests: V-resolution uninitialized (RealLast)
  - Repair action: Assign default parametric precision
  - Suggested fixture: defect mentioning 'RealLast'

#### `ShapeFix_ComposeShell.LoadWires` — lines 500–640
(12 branches, 5 covered.)

- **Branch 1** @ line 507 — *non_wire_topology* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face contains non-wire shapes after context apply
  - Repair action: Check if vertex; skip if other type
- **Branch 2** @ line 509 — *isolated_vertex* — **UNCOVERED**
  - What it tests: Degenerate wire that is a single vertex
  - Repair action: Create wire segment from vertex
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX', 'SetVertex'
- **Branch 3** @ line 522 — *non_manifold_wire_detection* — COVERED by: a024, a030, a032, a082, a098, a107, ad005, ad082 (+184 more)
  - What it tests: Wire orientation is INTERNAL/EXTERNAL (non-manifold)
  - Repair action: Mark segment as INTERNAL orientation; process separately
- **Branch 4** @ line 534 — *non_manifold_wire_handling* — **UNCOVERED**
  - What it tests: Non-manifold wire segmentation
  - Repair action: Create INTERNAL segment from full wire data
  - Suggested fixture: defect mentioning 'isNonManifold', 'TopAbs_INTERNAL'
- **Branch 5** @ line 539 — *empty_wire_protection* — **UNCOVERED**
  - What it tests: Wire has no edges despite being a wire
  - Repair action: Skip wire segment creation for edge-free wires
  - Suggested fixture: defect mentioning 'nbEdges', 'if (nbEdges)'
- **Branch 6** @ line 557 — *manifold_nonmanifold_split* — COVERED by: a024, a026, ad047, ad057, ad086, bo001, bo002, bo003 (+142 more)
  - What it tests: Edge orientation classification (FORWARD/REVERSED vs other)
  - Repair action: Route manifold edges to sbwdM; non-manifold to sbwdNM
- **Branch 7** @ line 570 — *non_manifold_edges_exist* — **UNCOVERED**
  - What it tests: Wire contains any non-manifold edges
  - Repair action: Create INTERNAL segment for non-manifold edges
  - Suggested fixture: defect mentioning 'nbNMEdges', 'TopAbs_INTERNAL'
- **Branch 8** @ line 578 — *manifold_edges_exist* — COVERED by: ad086, gp030, twi028, twi034, twi040, twi043, twi051, twi052 (+4 more)
  - What it tests: Wire contains any manifold edges
  - Repair action: Create REVERSED segment; apply reordering
- **Branch 9** @ line 586 — *periodic_torus_reordering* — **UNCOVERED**
  - What it tests: Surface is both U and V periodic (torus-like)
  - Repair action: Reorder edges in 2D before 3D reordering
  - Suggested fixture: defect mentioning 'IsUPeriodic', 'IsVPeriodic'
- **Branch 10** @ line 604 — *wire_order_analysis* — **UNCOVERED**
  - What it tests: Edge ordering status from ShapeAnalysis_WireOrder
  - Repair action: Check sawo.Status(); trigger FixReorder if invalid
  - Suggested fixture: defect mentioning 'sawo.Status()', 'sawo.Perform()'
- **Branch 11** @ line 610 — *reorder_fixation_status* — **UNCOVERED**
  - What it tests: StatusReorder(DONE3) indicates reordering was applied
  - Repair action: Set stat = -1 to mark modification
  - Suggested fixture: defect mentioning 'StatusReorder', 'DONE3'
- **Branch 12** @ line 615 — *wire_orientation_flip* — COVERED by: a024, a034, ad027, ad047, ad086, bo005, gb003, gs001 (+50 more)
  - What it tests: Reordering changed wire outer/inner bound classification
  - Repair action: Reverse wire data if IsOuterBound changed

#### `ShapeFix_ComposeShell.MakeFacesOnPatch` — lines 2981–3271
(26 branches, 15 covered.)

- **Branch 1** @ line 2985 — *SINGLE_LOOP* — COVERED by: tfa011, tfa058, tfa059, tsh011, twi024
  - What it tests: Fast-path for single loop (no holes)
  - Repair action: Create face, optionally fix edge orientation via ShapeFix_Face
- **Branch 2** @ line 2990 — *INVALID_LOOP_TYPE* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Loop is not a WIRE
  - Repair action: Skip/return early, mark as unprocesable
- **Branch 3** @ line 2997 — *EDGE_ORIENTATION_INVERT* — COVERED by: ad086, tfa004, tfa005, tfa011, tfa019, tfa037, tfa038, tfa039 (+3 more)
  - What it tests: Edge orientation flag set on input
  - Repair action: Invoke ShapeFix_Face::FixOrientation to repair wire orientation
- **Branch 4** @ line 3026 — *INVALID_LOOP_TYPE* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Loop i is not a WIRE
  - Repair action: Skip this loop, continue to next
- **Branch 5** @ line 3027 — *INVALID_ORIENTATION* — **UNCOVERED**
  - What it tests: Wire has invalid orientation (not FORWARD or REVERSED)
  - Repair action: Skip this loop
  - Suggested fixture: defect mentioning 'Orientation() != TopAbs_FORWARD', '!= TopAbs_REVERSED'
- **Branch 6** @ line 3034 — *EMPTY_WIRE* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wire has no edges
  - Repair action: Skip this loop, continue
- **Branch 7** @ line 3040 — *DEGENERATE_EDGE* — COVERED by: a004, a010, a021, a101, a106, ad005, ad015, ad026 (+102 more)
  - What it tests: First edge has invalid orientation, scan for valid one
  - Repair action: Iterate to next edge with valid orientation
- **Branch 8** @ line 3052 — *NO_VALID_EDGES* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: No edges found with valid orientation
  - Repair action: Skip this loop entirely
- **Branch 9** @ line 3058 — *NULL_PCURVE* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge has no pcurve on surface
  - Repair action: Skip this loop
- **Branch 10** @ line 3067 — *SELF_CONTAINMENT_CHECK* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Skip comparing wire to itself
  - Repair action: Skip when i==j
- **Branch 11** @ line 3072 — *INVALID_LOOP_TYPE* — **UNCOVERED**
  - What it tests: Candidate parent wire not valid WIRE type
  - Repair action: Skip this parent candidate
  - Suggested fixture: defect mentioning 'aShape2.ShapeType() != TopAbs_WIRE'
- **Branch 12** @ line 3092 — *EMPTY_PARENT_WIRE* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Parent wire has no edges after filtering by orientation
  - Repair action: Skip this parent wire
- **Branch 13** @ line 3101 — *TANGENTIAL_CONTAINMENT* — **UNCOVERED**
  - What it tests: Point lies ON or UNKNOWN state relative to parent boundary
  - Repair action: Resolve via edge-walking to find definitive containment state
  - Suggested fixture: defect mentioning 'TopAbs_ON', 'TopAbs_UNKNOWN', 'while (stPoint'
- **Branch 14** @ line 3111 — *EDGE_WALK_EXHAUSTION* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: Reached end of wire during tangency resolution
  - Repair action: Break tangency loop
- **Branch 15** @ line 3126 — *SEAM_PCURVE_MISSING* — **UNCOVERED**
  - What it tests: Seam edge has no pcurve
  - Repair action: Skip pcurve update, use previous
  - Suggested fixture: defect mentioning 'c2d.IsNull()'
- **Branch 16** @ line 3133 — *WINDING_NUMBER_MISMATCH* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: Wire contains candidate as hole/inside vs outside
  - Repair action: Break parent search, identify as root
- **Branch 17** @ line 3159 — *NO_ROOT_FOUND* — COVERED by: a011, a013, a030, a069, a082, a097, a098, a102 (+107 more)
  - What it tests: No root loops identified (topology error case)
  - Repair action: Promote all remaining loops as roots
- **Branch 18** @ line 3181 — *BADLY_ORIENTED_ROOT* — **UNCOVERED**
  - What it tests: Root wire encloses infinite point (backwards orientation)
  - Repair action: Mark for reversal (though reversal not applied here)
  - Suggested fixture: defect mentioning 'PerformInfinitePoint() == TopAbs_IN', 'reverse = true'
- **Branch 19** @ line 3196 — *HOLE_INVALID_TYPE* — **UNCOVERED**
  - What it tests: Hole candidate is not WIRE
  - Repair action: Skip and continue
  - Suggested fixture: defect mentioning 'loops(j).ShapeType() == TopAbs_WIRE'
- **Branch 20** @ line 3200 — *EMPTY_HOLE_WIRE* — **UNCOVERED**
  - What it tests: Hole wire has no edges
  - Repair action: Skip, continue to next hole candidate
  - Suggested fixture: defect mentioning '!ew.More()'
- **Branch 21** @ line 3207 — *HOLE_NULL_PCURVE* — **UNCOVERED**
  - What it tests: Hole edge has no pcurve
  - Repair action: Skip this hole candidate
  - Suggested fixture: defect mentioning 'cw.IsNull()'
- **Branch 22** @ line 3213 — *VERTEX_HOLE* — COVERED by: ad086
  - What it tests: Hole is a VERTEX, not wire
  - Repair action: Project vertex to surface and compute containment
- **Branch 23** @ line 3224 — *HOLE_WRONG_SIDE* — **UNCOVERED**
  - What it tests: Hole is on wrong side of root (outside when should be inside)
  - Repair action: Mark as hole, add to holes sequence, remove from loops
  - Suggested fixture: defect mentioning '(state == TopAbs_OUT) == reverse', 'holes.Append'
- **Branch 24** @ line 3238 — *VERTEX_IN_HOLE_SET* — **UNCOVERED**
  - What it tests: Hole candidate in final set is VERTEX
  - Repair action: Copy vertex to new face with parameter transfer
  - Suggested fixture: defect mentioning 'TopAbs_VERTEX', 'CopyNMVertex', 'Context()->Replace'
- **Branch 25** @ line 3253 — *ORPHANED_LOOPS_AT_END* — **UNCOVERED**
  - What it tests: Unprocessed loops remain after all roots exhausted
  - Repair action: Promote remaining loops as additional roots
  - Suggested fixture: defect mentioning 'i == roots.Length()', 'loops.Length() > 0'
- **Branch 26** @ line 3262 — *ORPHANED_INVALID_LOOP_TYPE* — COVERED by: a024, a030, a098, a107, ad005, ad082, ad086, ad118 (+58 more)
  - What it tests: Orphaned loop is not valid WIRE with proper orientation
  - Repair action: Filter invalid types before promoting as roots

#### `ShapeFix_ComposeShell.Perform` — lines 207–255
(2 branches, 1 covered.)

- **Branch 1** @ line 215 — *empty_wire_sequence* — **UNCOVERED**
  - What it tests: Face contains no loadable wires
  - Repair action: Return FAIL6 status; abort pipeline
  - Suggested fixture: defect mentioning 'LoadWires', 'seqw.Length() == 0', 'FAIL6'
- **Branch 2** @ line 236 — *face_count_classification* — COVERED by: bo002, bo022, tfa060
  - What it tests: Single vs multi-face output from wires
  - Repair action: If multi-face: wrap in shell; if single: use face directly

#### `ShapeFix_ComposeShell.SplitByGrid` — lines 2131–2275
(8 branches, 1 covered.)

- **Branch 1** @ line 2144 — *Closed mode periodic surface processing* — **UNCOVERED**
  - What it tests: myClosedMode is true (periodic surface handling)
  - Repair action: Adjust wire segment patch indices to extended periodic range [0,2)
  - Suggested fixture: defect mentioning 'myClosedMode', 'AdjustToPeriod', 'GetPatchIndex'
- **Branch 2** @ line 2165 — *U-axis periodicity in closed mode* — **UNCOVERED**
  - What it tests: myUClosed && myClosedMode, wire extends beyond period
  - Repair action: Shift wire U-coordinates, compute min/max patch indices in periodic range
  - Suggested fixture: defect mentioning 'myUClosed', 'shiftU', 'Ul1 - pprec'
- **Branch 3** @ line 2170 — *V-axis periodicity in closed mode* — **UNCOVERED**
  - What it tests: myVClosed && myClosedMode, wire extends beyond V period
  - Repair action: Shift wire V-coordinates, compute min/max patch indices
  - Suggested fixture: defect mentioning 'myVClosed', 'shiftV', 'Vl1 - pprec'
- **Branch 4** @ line 2201 — *Non-closed mode patch assignment* — **UNCOVERED**
  - What it tests: myClosedMode is false (single-patch processing)
  - Repair action: Use global face UV bounds to set uniform patch indices for all wires
  - Suggested fixture: defect mentioning '!myClosedMode', 'Uf + pprec', 'BRepTools::UVBounds'
- **Branch 5** @ line 2235 — *Non-closed periodic surface U-seam wrapping* — COVERED by: ad086, gb003, gn019, gn031, gn033, gp005, gp011, gp012 (+47 more)
  - What it tests: !myClosedMode && myUClosed, split line within period wraps around
  - Repair action: Iterate split-by-line with periodic shifts for each wrap
- **Branch 6** @ line 2258 — *Non-closed periodic surface V-seam wrapping* — **UNCOVERED**
  - What it tests: !myClosedMode && myVClosed, V-const line wraps around period
  - Repair action: Iterate split-by-line with periodic V shifts
  - Suggested fixture: defect mentioning '!myClosedMode && myVClosed', 'sh +='
- **Branch 7** @ line 2229 — *U-patch skip for non-closed surfaces* — **UNCOVERED**
  - What it tests: Starting patch index: skip first if myUClosed, else start at 2
  - Repair action: Avoid duplicate seam processing or handle first patch specially
  - Suggested fixture: defect mentioning 'myUClosed ? 1 : 2', 'NbUPatches()'
- **Branch 8** @ line 2254 — *V-patch skip for non-closed surfaces* — **UNCOVERED**
  - What it tests: Starting V patch index: skip first if myVClosed, else start at 2
  - Repair action: Skip or handle first patch based on closure
  - Suggested fixture: defect mentioning 'myVClosed ? 1 : 2', 'NbVPatches()'

#### `ShapeFix_ComposeShell.SplitByLine` — lines 1440–1914
(32 branches, 15 covered.)

- **Branch 1** @ line 1452 — *Non-manifold wire as single vertex* — COVERED by: ad086, tsh037
  - What it tests: Wire contains only a single vertex requiring non-manifold handling
  - Repair action: Replace vertex with corrected position on line, mark as tangent split
- **Branch 2** @ line 1461 — *Vertex undefined position on line* — COVERED by: in014
  - What it tests: Single vertex point position code is undefined relative to cutting line
  - Repair action: Return false, skip processing this vertex segment
- **Branch 3** @ line 1486 — *Closed surface U-axis perpendicular to line* — **UNCOVERED**
  - What it tests: Surface is closed in U and cutting line is perpendicular to U-axis
  - Repair action: Enable periodic shift handling for U-axis wrapping
  - Suggested fixture: defect mentioning 'myUClosed', 'line.Direction().X()', 'closedDir = -1'
- **Branch 4** @ line 1490 — *Closed surface V-axis perpendicular to line* — **UNCOVERED**
  - What it tests: Surface is closed in V and cutting line is perpendicular to V-axis
  - Repair action: Enable periodic shift handling for V-axis wrapping
  - Suggested fixture: defect mentioning 'myVClosed', 'line.Direction().Y()', 'closedDir = 1'
- **Branch 5** @ line 1509 — *Missing or invalid 2D parametric curve* — COVERED by: a024, ad046, ad050, ad086, ad099, ad101, fi002, gb004 (+130 more)
  - What it tests: Edge lacks valid PCurve representation on face
  - Repair action: Skip this edge, continue to next edge
- **Branch 6** @ line 1535 — *Closed mode with U-periodic curve outside line region* — **UNCOVERED**
  - What it tests: Curve bounding box on U-axis requires shift to align with line
  - Repair action: Translate curve by period and adjust end point coordinates
  - Suggested fixture: defect mentioning 'AdjustToPeriod', 'closedDir < 0', 'shift != 0'
- **Branch 7** @ line 1555 — *Closed mode with V-periodic curve outside line region* — **UNCOVERED**
  - What it tests: Curve bounding box on V-axis requires shift to align with line
  - Repair action: Translate curve by period and adjust end point coordinates
  - Suggested fixture: defect mentioning 'AdjustToPeriod', 'closedDir > 0', 'shift != 0'
- **Branch 8** @ line 1587 — *Point-to-point edge junction tangent discontinuity* — COVERED by: twi068
  - What it tests: Consecutive edges have different line-position codes or undefined code
  - Repair action: Record intersection at edge junction in intersection arrays
- **Branch 9** @ line 1589 — *Periodic surface crossing boundary avoidance* — **UNCOVERED**
  - What it tests: Distance between edge endpoints crosses periodic boundary
  - Repair action: Skip junction intersection if crossing period threshold
  - Suggested fixture: defect mentioning 'halfPeriod', 'std::abs(dev - prevDev)', 'closedDir'
- **Branch 10** @ line 1616 — *Curve-line intersection found* — **UNCOVERED**
  - What it tests: 2D curve intersects with cutting line at discrete points
  - Repair action: Extract intersection points and add to intersection arrays
  - Suggested fixture: defect mentioning 'Inter.IsDone()', 'Inter.NbPoints()', 'IntLinePar.Append'
- **Branch 11** @ line 1622 — *Intersection point in middle of curve* — **UNCOVERED**
  - What it tests: Intersection at interior curve point not at edge start/end
  - Repair action: Collect intersection point parameters and indices
  - Suggested fixture: defect mentioning 'PositionOnCurve() == IntRes2d_Middle', 'ParamOnFirst', 'ParamOnSecond'
- **Branch 12** @ line 1623 — *Both adjacent segments defined (non-tangent intersection)* — **UNCOVERED**
  - What it tests: Code is not IOR_UNDEF for both previous and current segment
  - Repair action: Include intersection point even if at tangency zone
  - Suggested fixture: defect mentioning 'code != IOR_UNDEF && prevCode != IOR_UNDEF'
- **Branch 13** @ line 1629 — *Curve-line tangent or overlap segment* — **UNCOVERED**
  - What it tests: 2D curve has tangent or overlapping segment with line
  - Repair action: Extract segment endpoints and add to intersection arrays
  - Suggested fixture: defect mentioning 'Inter.NbSegments()', 'FirstPoint', 'LastPoint'
- **Branch 14** @ line 1664 — *Intersection parameter clamping below edge range* — COVERED by: ad014, fi003, gn011, gn024, gn026, gp005, gp007, gs010 (+20 more)
  - What it tests: Intersection parameter computed by intersector is less than edge start
  - Repair action: Clamp parameter value to edge start point
- **Branch 15** @ line 1668 — *Intersection parameter clamping above edge range* — COVERED by: ad014, fi003, gn011, gn024, gn026, gp005, gp007, gs010 (+20 more)
  - What it tests: Intersection parameter computed by intersector exceeds edge end
  - Repair action: Clamp parameter value to edge end point
- **Branch 16** @ line 1679 — *Out-of-order intersection points on reversed edge* — COVERED by: a002, a007, a024, a025, a037, ad014, ad027, ad038 (+23 more)
  - What it tests: Intersection parameters not sorted correctly on reversed-orientation edge
  - Repair action: Swap adjacent intersection point pairs to restore order
- **Branch 17** @ line 1696 — *Wire closure point tangent discontinuity* — COVERED by: ad086, ad101, os009, os010, os011, pf006, tfa005, twi034 (+6 more)
  - What it tests: Wire is closed (not EXTERNAL/INTERNAL) with position code change at closure
  - Repair action: Record intersection at wire closure point
- **Branch 18** @ line 1700 — *Closure point periodic boundary avoidance* — COVERED by: a085, a102, ad064, ad084, ad094, ad098, bo005, bo006 (+271 more)
  - What it tests: Wire closure crossing periodic boundary in closed-mode surface
  - Repair action: Skip closure intersection if crossing period threshold
- **Branch 19** @ line 1709 — *No intersections found after complete analysis* — COVERED by: in014
  - What it tests: Wire has no intersection points with cutting line
  - Repair action: Return false, wire cannot be split
- **Branch 20** @ line 1725 — *Duplicate intersection points in closed mode* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+32 more)
  - What it tests: Same edge with identical parameter appears at wire start and end
  - Repair action: Remove duplicate intersection entry
- **Branch 21** @ line 1743 — *Duplicate at edge junction in closed mode* — COVERED by: a084, ad001, ad002, ad003, ad004, ad014, ad026, ad027 (+149 more)
  - What it tests: Intersection at junction of consecutive edges in closed loop
  - Repair action: Check parameter match and remove if duplicate at connection point
- **Branch 22** @ line 1785 — *External wire (seam/joint line)* — COVERED by: a004, a012, a013, a014, a033, a104, ad004, ad052 (+27 more)
  - What it tests: Wire has EXTERNAL orientation indicating it is another cutting line
  - Repair action: Mark all intersection points as double (both-sided) tangent
- **Branch 23** @ line 1796 — *Non-internal wire tangency merging* — **UNCOVERED**
  - What it tests: Wire is neither EXTERNAL nor INTERNAL, requires tangency analysis
  - Repair action: Analyze tangential segments and merge consecutive ones
  - Suggested fixture: defect mentioning 'TopAbs_INTERNAL', 'tangency merging'
- **Branch 24** @ line 1805 — *Consecutive tangential segments both undefined* — **UNCOVERED**
  - What it tests: Both previous and current segment codes are IOR_UNDEF (tangent)
  - Repair action: Mark for removal to consolidate tangent region
  - Suggested fixture: defect mentioning 'SegmentCodes(j) == IOR_UNDEF', 'SegmentCodes(i) == IOR_UNDEF'
- **Branch 25** @ line 1810 — *Seam edge overlap with spur edge* — **UNCOVERED**
  - What it tests: In closed mode, seam edge overlaps spur; check monotonicity
  - Repair action: Skip removal if parameter ordering indicates non-monotonic overlap
  - Suggested fixture: defect mentioning 'ACIS22539', 'myClosedMode', 'IntLinePar(i) - IntLinePar(j)'
- **Branch 26** @ line 1825 — *All split points removed after tangency analysis* — COVERED by: in014
  - What it tests: After merging tangencies, no intersection points remain
  - Repair action: Return false, wire cannot be split
- **Branch 27** @ line 1842 — *Closed mode with IOR_BOTH requiring left/right disambiguation* — **UNCOVERED**
  - What it tests: Segment code indicates both-sided crossing in periodic mode
  - Repair action: Resolve to left or right based on position bit
  - Suggested fixture: defect mentioning '(codej & IOR_BOTH) == IOR_BOTH', 'IOR_POS', 'IOR_LEFT : IOR_RIGHT'
- **Branch 28** @ line 1861 — *Previous segment tangential (start of tangent zone)* — **UNCOVERED**
  - What it tests: Previous segment code is IOR_UNDEF (tangent)
  - Repair action: Mark intersection as end or beginning of tangential segment
  - Suggested fixture: defect mentioning 'codej == IOR_UNDEF', 'ITP_ENDSEG', 'ITP_BEGSEG'
- **Branch 29** @ line 1872 — *Current segment tangential (within tangent zone)* — **UNCOVERED**
  - What it tests: Current segment code is IOR_UNDEF (tangent)
  - Repair action: Mark intersection as start or end of tangential segment
  - Suggested fixture: defect mentioning 'codei == IOR_UNDEF', 'ITP_BEGSEG', 'ITP_ENDSEG'
- **Branch 30** @ line 1884 — *Single-point loop or self-closure* — **UNCOVERED**
  - What it tests: Iteration index equals previous, creating circular reference
  - Repair action: Classify as tangent or crossing based on both-sided condition
  - Suggested fixture: defect mentioning 'i == j', 'ITP_INTER', 'ITP_TANG'
- **Branch 31** @ line 1888 — *Equal segment codes or non-manifold wire* — **UNCOVERED**
  - What it tests: Both adjacent segments have same code or wire is non-manifold
  - Repair action: Classify intersection as tangency in-point
  - Suggested fixture: defect mentioning 'codei == codej', 'isnonmanifold', 'ITP_TANG'
- **Branch 32** @ line 1892 — *Standard crossing with code change* — COVERED by: ad086, fi004, gn033, gp008, gp028, gs009, gs012, gs038 (+17 more)
  - What it tests: Segments have different codes indicating line crossing
  - Repair action: Classify intersection as standard line crossing

#### `ShapeFix_ComposeShell.SplitByLine(sequence)` — lines 1918–2127
(10 branches, 0 covered.)

- **Branch 1** @ line 1951 — *Null-length tangential segment boundary merge* — **UNCOVERED**
  - What it tests: Two consecutive split points are coincident with matching tangency boundaries
  - Repair action: Merge endpoints into single point with combined orientation code
  - Suggested fixture: defect mentioning 'ITP_ENDSEG', 'ITP_BEGSEG', 'IOR_BOTH'
- **Branch 2** @ line 1977 — *Crossing intersection parity tracking* — **UNCOVERED**
  - What it tests: Intersection point type is clear crossing (ITP_INTER)
  - Repair action: Increment parity counter (0=out, 1=in, toggle)
  - Suggested fixture: defect mentioning 'code & ITP_INTER', 'parity++'
- **Branch 3** @ line 1981 — *Tangential segment start-point handling* — **UNCOVERED**
  - What it tests: Beginning of tangential segment, track half-parity for side-specific state
  - Repair action: Increment tangency nesting level, set/check half-parity orientation
  - Suggested fixture: defect mentioning 'ITP_BEGSEG', 'tanglevel++', 'halfparity'
- **Branch 4** @ line 1993 — *Tangential segment end-point handling* — **UNCOVERED**
  - What it tests: End of tangential segment, decrement nesting level
  - Repair action: Decrement tanglevel, manage parity transition if half-parity switch
  - Suggested fixture: defect mentioning 'ITP_ENDSEG', 'tanglevel--'
- **Branch 5** @ line 2025 — *First/last vertices cannot merge edge constraint* — **UNCOVERED**
  - What it tests: Edge is not the first or last on split line
  - Repair action: Allow vertex merging only for interior edges (not line endpoints)
  - Suggested fixture: defect mentioning 'canbeMerged', 'i - 1 > 1', 'SplitLinePar.Length()'
- **Branch 6** @ line 2028 — *Max tolerance override for vertex merging* — **UNCOVERED**
  - What it tests: Max tolerance is not defined or less than confusion precision
  - Repair action: Use infinite tolerance to preserve vertex identity
  - Suggested fixture: defect mentioning 'aMaxTol <= 2. * Precision::Confusion()', 'MaxTolerance()'
- **Branch 7** @ line 2044 — *Vertex identity merging after short-segment removal* — **UNCOVERED**
  - What it tests: Two split vertices are distinct but will be removed
  - Repair action: Create combined vertex, replace both in context
  - Suggested fixture: defect mentioning 'V1.IsSame(V2)', 'CombineVertex', 'Context()->Replace'
- **Branch 8** @ line 2078 — *Patch index assignment for U-cut split edges* — **UNCOVERED**
  - What it tests: Edge created from U-const line (isCutByU==true)
  - Repair action: Set U patch indices from grid boundaries, V from line parameter
  - Suggested fixture: defect mentioning 'isCutByU', 'DefineIUMin', 'DefineIVMin'
- **Branch 9** @ line 2096 — *Patch index assignment for V-cut split edges* — **UNCOVERED**
  - What it tests: Edge created from V-const line (isCutByU==false)
  - Repair action: Set V patch indices from grid, U from line parameter with shift
  - Suggested fixture: defect mentioning '!isCutByU', 'DefineIVMin', 'DefineIVMax'
- **Branch 10** @ line 2111 — *Parity error on line processing completion* — **UNCOVERED**
  - What it tests: Final parity is odd (inside shell boundary)
  - Repair action: Set status FAIL4 (indicates missed intersection or topology error)
  - Suggested fixture: defect mentioning 'parity % 2', 'ShapeExtend_FAIL4'

#### `ShapeFix_ComposeShell.SplitByLine(wire)` — lines 1433–1914
(15 branches, 3 covered.)

- **Branch 1** @ line 1452 — *Non-manifold vertex in wire* — COVERED by: a032, a082, ad086, ad092, ad100, ad103, ad104, ad107 (+129 more)
  - What it tests: Wire is a vertex (not edge-based wire)
  - Repair action: Handle non-manifold vertex by creating new vertex with fixed tolerance, merge context
- **Branch 2** @ line 1483 — *Closed periodic surface mode* — **UNCOVERED**
  - What it tests: Closed mode with U or V periodicity and line direction aligned with period
  - Repair action: Adjust closing direction flag and period shift for periodic handling
  - Suggested fixture: defect mentioning 'myClosedMode', 'myUClosed', 'myVClosed'
- **Branch 3** @ line 1509 — *Missing PCurve on face* — COVERED by: a024, ad046, ad050, ad086, ad099, ad101, fi002, gb004 (+130 more)
  - What it tests: Edge has no valid 2D curve representation on face
  - Repair action: Skip edge from intersection computation, continue to next edge
- **Branch 4** @ line 1522 — *Long PCurve spanning multiple periods* — **UNCOVERED**
  - What it tests: PCurve extends beyond single period on closed surface
  - Repair action: Iterate with period shifts to process all intersection spans
  - Suggested fixture: defect mentioning 'nbIter', 'shiftNext', 'myUPeriod'
- **Branch 5** @ line 1587 — *Wire side-crossing detection at edge junction* — **UNCOVERED**
  - What it tests: Two consecutive edges switch from one side to other relative to split line
  - Repair action: Record intersection at vertex between edges
  - Suggested fixture: defect mentioning 'code != prevCode', 'IntLinePar.Append'
- **Branch 6** @ line 1622 — *Intersection point at curve middle vs tangency* — **UNCOVERED**
  - What it tests: Intersection is in middle of segment or both sides have definite orientation
  - Repair action: Include intersection point in split sequence
  - Suggested fixture: defect mentioning 'IntRes2d_Middle', 'PositionOnCurve'
- **Branch 7** @ line 1696 — *Closed wire end-vertex intersection detection* — **UNCOVERED**
  - What it tests: Last edge endpoint may intersect line, wire is closed non-internal
  - Repair action: Record closing-point intersection if orientation changes across closure
  - Suggested fixture: defect mentioning 'iedge == nbe', 'wire.Orientation() != TopAbs_EXTERNAL'
- **Branch 8** @ line 1723 — *Duplicate intersection points from periodic wrapping* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+33 more)
  - What it tests: Same edge/parameter pair appears on different period iterations
  - Repair action: Remove duplicate intersection records to avoid degenerate splits
- **Branch 9** @ line 1785 — *External wire (seam edge) special case* — **UNCOVERED**
  - What it tests: Wire represents seam/joint edge with double intersection
  - Repair action: Mark all points as tangential with both-sides orientation
  - Suggested fixture: defect mentioning 'TopAbs_EXTERNAL', 'ITP_TANG', 'IOR_BOTH'
- **Branch 10** @ line 1805 — *Consecutive tangential segments with special seam geometry* — **UNCOVERED**
  - What it tests: Two tangential segments are consecutive (undefined code), seam overlap case
  - Repair action: Remove middle point if not representing genuine tangential overlap
  - Suggested fixture: defect mentioning 'SegmentCodes(j) == IOR_UNDEF', 'ACIS22539', 'myClosedMode'
- **Branch 11** @ line 1860 — *Tangential segment boundary classification* — **UNCOVERED**
  - What it tests: Intersection point is start or end of tangential segment
  - Repair action: Mark with ITP_BEGSEG or ITP_ENDSEG based on parameter ordering
  - Suggested fixture: defect mentioning 'codej == IOR_UNDEF', 'ITP_ENDSEG', 'ITP_BEGSEG'
- **Branch 12** @ line 1884 — *Single-point internal wire crossing* — **UNCOVERED**
  - What it tests: Closed wire with only one intersection (j == i), non-manifold context
  - Repair action: Classify as tangency (ITP_TANG) for internal, intersection for manifold
  - Suggested fixture: defect mentioning 'i == j', 'isnonmanifold', 'ITP_INTER'
- **Branch 13** @ line 1888 — *Same-side tangential crossing* — **UNCOVERED**
  - What it tests: Before/after segments both on same side (tangential inpoint)
  - Repair action: Mark as ITP_TANG (no crossing, just touches)
  - Suggested fixture: defect mentioning 'codei == codej', 'isnonmanifold'
- **Branch 14** @ line 2005 — *Tangency nesting level underflow* — **UNCOVERED**
  - What it tests: More tangency-end than tangency-start points detected
  - Repair action: Log warning, set status FAIL4 (non-critical recovery)
  - Suggested fixture: defect mentioning 'tanglevel < 0', 'ShapeExtend_FAIL4'
- **Branch 15** @ line 2037 — *Degenerate edge segment on split line* — **UNCOVERED**
  - What it tests: Two consecutive split points lie within vertex tolerance distance
  - Repair action: Merge vertices, skip edge creation, continue without edge
  - Suggested fixture: defect mentioning 'SplitLinePar(i) - SplitLinePar(i-1)', 'CombineVertex'

#### `ShapeFix_ComposeShell.SplitEdges` — lines 260–270
(0 branches, 0 covered.)


#### `ShapeFix_ComposeShell.SplitWire` — lines 949–1429
(25 branches, 8 covered.)

- **Branch 1** @ line 969 — *seam_edge_redistribution* — **UNCOVERED**
  - What it tests: Edge was already split during context application
  - Repair action: Redistribute splitting points across sub-edges
  - Suggested fixture: defect mentioning 'ApplyContext', 'nsplit != 1'
- **Branch 2** @ line 973 — *edge_dismissed_by_context* — **UNCOVERED**
  - What it tests: Edge redistribution failed (nsplit <= 0)
  - Repair action: Skip edge; decrement loop index
  - Suggested fixture: defect mentioning 'nsplit <= 0', 'i--'
- **Branch 3** @ line 992 — *no_split_points_on_edge* — **UNCOVERED**
  - What it tests: Current edge has no split indices
  - Repair action: Add edge unsplit; set patch code if non-external
  - Suggested fixture: defect mentioning 'stop == start', 'AddEdge'
- **Branch 4** @ line 1010 — *non_manifold_vertex_on_edge* — COVERED by: a011, a024, a030, a098, a107, ad005, ad038, ad082 (+68 more)
  - What it tests: Edge has INTERNAL/EXTERNAL vertices
  - Repair action: Collect for later embedding in split edges
- **Branch 5** @ line 1033 — *missing_3d_curve* — COVERED by: gn017, twi046, twi047, twi059, twi062, twi065
  - What it tests: Edge has no 3D curve representation
  - Repair action: Use parametric fallback; nullify c3d
- **Branch 6** @ line 1041 — *missing_pcurve_on_face* — COVERED by: a024, ad046, ad086, ad099, gb004, gn019, gn030, gn033 (+112 more)
  - What it tests: Edge has no 2D curve on the face
  - Repair action: Set FAIL2 status; continue with undefined PCurve
- **Branch 7** @ line 1048 — *non_manifold_vertex_projection* — **UNCOVERED**
  - What it tests: Non-manifold vertices on edge need parameter location
  - Repair action: Project non-manifold vertices to curve; cache parameters
  - Suggested fixture: defect mentioning 'aNMVertices.Length()', 'aNMVertParams'
- **Branch 8** @ line 1121 — *periodic_pcurve_parameter_shift* — **UNCOVERED**
  - What it tests: Periodic curve parameter out of edge range
  - Repair action: Adjust by period to fall within [firstPar, lastPar]
  - Suggested fixture: defect mentioning 'isPeriodic', 'AdjustByPeriod'
- **Branch 9** @ line 1136 — *split_point_at_edge_end* — **UNCOVERED**
  - What it tests: Split parameter coincides with edge end
  - Repair action: Use lastV; set doCut=false
  - Suggested fixture: defect mentioning 'currPar - lastPar', 'lastV'
- **Branch 10** @ line 1141 — *split_point_at_previous_vertex* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Split parameter coincides with previous vertex
  - Repair action: Use prevV; skip split (continue)
- **Branch 11** @ line 1151 — *split_coincides_with_last_vertex* — **UNCOVERED**
  - What it tests: Split point within tolerance of last vertex
  - Repair action: Use lastV via tolerance check; validate by curve 3D
  - Suggested fixture: defect mentioning 'currPnt.Distance(lastVPnt)', 'CheckByCurve3d'
- **Branch 12** @ line 1185 — *split_coincides_with_prev_vertex* — **UNCOVERED**
  - What it tests: Split point within tolerance of previous vertex
  - Repair action: Use prevV via tolerance check
  - Suggested fixture: defect mentioning 'currPnt.Distance(prevVPnt)'
- **Branch 13** @ line 1226 — *degenerated_edge_protection* — COVERED by: m026, m109, os002, pmi053, sw003, tfa005, twi021, twi064 (+2 more)
  - What it tests: Edge is degenerated and both vertices are same
  - Repair action: Use prevV to avoid multiple splits on degen edge
- **Branch 14** @ line 1238 — *new_vertex_creation* — **UNCOVERED**
  - What it tests: Split point does not coincide with existing vertices
  - Repair action: Create new vertex; add to context
  - Suggested fixture: defect mentioning 'V.IsNull()', 'MakeVertex'
- **Branch 15** @ line 1244 — *adjacent_split_collapse* — **UNCOVERED**
  - What it tests: Split point adjusted to edge end; skip remaining splits
  - Repair action: Fill remaining vertices with lastV; break if unsplit
  - Suggested fixture: defect mentioning '!doCut'
- **Branch 16** @ line 1263 — *vertex_copy_for_splitting* — **UNCOVERED**
  - What it tests: First split on edge requires vertex copying
  - Repair action: Create empty copies of edge vertices; register in context
  - Suggested fixture: defect mentioning '!splitted', 'EmptyCopied'
- **Branch 17** @ line 1301 — *manifold_status_tracking* — **UNCOVERED**
  - What it tests: Edge manifold vs non-manifold classification
  - Repair action: Preserve or normalize edge orientation during split
  - Suggested fixture: defect mentioning 'ismanifold', 'TopAbs_FORWARD'
- **Branch 18** @ line 1316 — *non_manifold_vertex_binding* — COVERED by: a025, ad086, ad103, ad115, bo008, bo022, gn014, gn015 (+50 more)
  - What it tests: Non-manifold vertex parameter matches edge boundary
  - Repair action: Redirect non-manifold vertex to edge endpoint
- **Branch 19** @ line 1330 — *non_manifold_vertex_inside_split* — **UNCOVERED**
  - What it tests: Non-manifold vertex falls inside current split segment
  - Repair action: Add non-manifold vertex to new edge; remove from tracking
  - Suggested fixture: defect mentioning 'apar > prevPar && apar < currPar'
- **Branch 20** @ line 1346 — *non_manifold_edge_tangency* — **UNCOVERED**
  - What it tests: Non-manifold edge has zero code (tangency)
  - Repair action: Set to EXTERNAL orientation
  - Suggested fixture: defect mentioning 'code == IOR_UNDEF', 'TopAbs_EXTERNAL'
- **Branch 21** @ line 1358 — *same_range_correction* — COVERED by: m026, m109, os002, pmi053, sw003, tfa005, twi021, twi064 (+4 more)
  - What it tests: Edge is not degenerated and 3D/2D parametrization mismatch
  - Repair action: Disable SameRange flag on new edge
- **Branch 22** @ line 1363 — *external_wire_zero_code* — **UNCOVERED**
  - What it tests: External wire with tangency (code=0)
  - Repair action: Assign binary code based on cut direction
  - Suggested fixture: defect mentioning 'code == 0', 'isCutByU'
- **Branch 23** @ line 1380 — *context_replacement_split* — **UNCOVERED**
  - What it tests: Edge was split into multiple sub-edges
  - Repair action: Build replacement wire; register in context
  - Suggested fixture: defect mentioning 'splitted', 'Context()->Replace'
- **Branch 24** @ line 1388 — *split_orientation_handling* — COVERED by: a024, a026, a032, a082, ad047, ad057, ad086, ad092 (+257 more)
  - What it tests: Original edge orientation guide for adding to result wire
  - Repair action: Add sub-edges in correct order per original orientation
- **Branch 25** @ line 1401 — *internal_wire_tangency_case* — **UNCOVERED**
  - What it tests: Non-manifold wire (INTERNAL) with tangency to grid
  - Repair action: Create EXTERNAL edge copy; register replacement
  - Suggested fixture: defect mentioning 'anWireOrient == TopAbs_INTERNAL', 'code == 0', 'TopAbs_EXTERNAL'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Edge.cxx`

10 methods, 61 branches, 13 covered.

#### `ShapeFix_Edge.FixAddCurve3d` — lines 619–638
(4 branches, 1 covered.)

- **Branch 1** @ line 622 — *Degenerated_edge* — **UNCOVERED**
  - What it tests: Edge is topologically degenerate
  - Repair action: Skip processing, return false
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated'
- **Branch 2** @ line 622 — *Curve3d_already_present* — **UNCOVERED**
  - What it tests: Edge already has 3D curve
  - Repair action: Skip processing, return false
  - Suggested fixture: defect mentioning 'HasCurve3d'
- **Branch 3** @ line 626 — *Not_same_range* — **UNCOVERED**
  - What it tests: Edge PCurves and 3D curve have different parameter ranges
  - Repair action: Normalize all curves to same range via TempSameRange
  - Suggested fixture: defect mentioning 'BRep_Tool::SameRange', 'TempSameRange'
- **Branch 4** @ line 631 — *BuildCurve3d_failed* — COVERED by: tfa037, twi066
  - What it tests: Cannot build 3D curve from PCurves
  - Repair action: Fail with FAIL1 status

#### `ShapeFix_Edge.FixAddPCurve_1stOverload` — lines 117–125
(1 branches, 1 covered.)

- **Branch 1** @ line 123 — *Surface_location_extract* — COVERED by: ad086
  - What it tests: Extract surface and location from TopoDS_Face
  - Repair action: Transform face to surface + location form for processing

#### `ShapeFix_Edge.FixAddPCurve_2ndOverload` — lines 470–614
(13 branches, 5 covered.)

- **Branch 1** @ line 479 — *PCurve_already_present* — **UNCOVERED**
  - What it tests: Non-seam edge already has PCurve on surface
  - Repair action: Skip processing, return false
  - Suggested fixture: defect mentioning 'HasPCurve', 'isSeam'
- **Branch 2** @ line 480 — *Seam_already_present* — **UNCOVERED**
  - What it tests: Seam edge already exists on surface
  - Repair action: Skip processing, return false
  - Suggested fixture: defect mentioning 'IsSeam', 'isSeam'
- **Branch 3** @ line 486 — *Plane_surface_no_pcurve* — **UNCOVERED**
  - What it tests: Surface is a Plane (no PCurve computation needed)
  - Repair action: Skip processing, return false
  - Suggested fixture: defect mentioning 'Geom_Plane', 'STANDARD_TYPE'
- **Branch 4** @ line 502 — *Missing_3d_curve* — **UNCOVERED**
  - What it tests: Edge has no 3D curve
  - Repair action: Fail with FAIL1 status
  - Suggested fixture: defect mentioning 'BRep_Tool::Curve', 'IsNull'
- **Branch 5** @ line 519 — *PCurve_missing_needs_projection* — **UNCOVERED**
  - What it tests: Edge lacks PCurve, must project 3D curve to 2D
  - Repair action: Project 3D curve to surface using ShapeExtend_Projector
  - Suggested fixture: defect mentioning 'myProjector->Perform', 'ShapeExtend_DONE4'
- **Branch 6** @ line 543 — *PCurve_exists_use_existing* — COVERED by: a024, ad046, ad086, ad099, gb004, gn019, gn030, gn033 (+112 more)
  - What it tests: PCurve already found on surface
  - Repair action: Retrieve existing PCurve parameters
- **Branch 7** @ line 550 — *Seam_requires_dual_representation* — **UNCOVERED**
  - What it tests: Edge is seam (needs two PCurves)
  - Repair action: Create translated duplicate PCurve for seam
  - Suggested fixture: defect mentioning 'isSeam', 'c2d->Copy'
- **Branch 8** @ line 564 — *Seam_on_uclosed_surface* — COVERED by: n010
  - What it tests: Surface is U-closed but not V-closed, seam parallel to V
  - Repair action: Translate PCurve by U period
- **Branch 9** @ line 571 — *Seam_on_vclosed_surface* — COVERED by: n010
  - What it tests: Surface is V-closed but not U-closed, seam parallel to U
  - Repair action: Translate PCurve by V period
- **Branch 10** @ line 576 — *Seam_on_doubly_closed_surface* — COVERED by: a064, a105, gn014, gn015, gp001, gp013, gp021, gp027 (+27 more)
  - What it tests: Surface closed in both U and V (torus, etc)
  - Repair action: Use TranslatePCurve to intelligently shift PCurve
- **Branch 11** @ line 586 — *Non_seam_pcurve_added* — **UNCOVERED**
  - What it tests: Non-seam edge, PCurve added successfully
  - Repair action: Update edge with single PCurve
  - Suggested fixture: defect mentioning 'UpdateEdge', 'B.Range'
- **Branch 12** @ line 593 — *Curve3d_needs_update* — **UNCOVERED**
  - What it tests: Projector set DONE3 flag (3D curve update needed)
  - Repair action: Update edge 3D curve and SameRange flag
  - Suggested fixture: defect mentioning 'ShapeExtend_DONE3', 'B.SameRange'
- **Branch 13** @ line 601 — *Exception_during_projection* — COVERED by: ad086, gp029, m027, pf009, sw009, twi066
  - What it tests: Projection threw Standard_Failure exception
  - Repair action: Catch exception, set FAIL2 status, continue

#### `ShapeFix_Edge.FixRemoveCurve3d` — lines 104–113
(1 branches, 1 covered.)

- **Branch 1** @ line 108 — *Curve3d_with_invalid_vertex* — COVERED by: twi046, twi059, twi065
  - What it tests: Edge has 3D curve with vertices that fail consistency check
  - Repair action: Remove 3D curve from edge

#### `ShapeFix_Edge.FixRemovePCurve` — lines 90–99
(1 branches, 1 covered.)

- **Branch 1** @ line 94 — *PCurve_with_invalid_vertex* — COVERED by: ad086, twi060, twi065
  - What it tests: Edge has PCurve with vertices that fail consistency check
  - Repair action: Remove PCurve from edge

#### `ShapeFix_Edge.FixReversed2d` — lines 744–786
(5 branches, 1 covered.)

- **Branch 1** @ line 752 — *pcurve_3d_mismatch_fail1* — COVERED by: twi062, twi065
  - What it tests: 3D curve vs PCurve alignment check FAIL1
  - Repair action: Record FAIL1 status
- **Branch 2** @ line 756 — *pcurve_3d_mismatch_fail2* — **UNCOVERED**
  - What it tests: 3D curve vs PCurve alignment check FAIL2
  - Repair action: Record FAIL2 status
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_FAIL2)'
- **Branch 3** @ line 760 — *pcurve_alignment_not_done* — **UNCOVERED**
  - What it tests: Whether PCurve alignment completed
  - Repair action: Abort repair if DONE status not set
  - Suggested fixture: defect mentioning '!EA.Status(ShapeExtend_DONE)'
- **Branch 4** @ line 769 — *pcurve_parameter_reversal* — **UNCOVERED**
  - What it tests: Parameter order correction (f,l -> newl,newf)
  - Repair action: Reverse PCurve and update parameter range
  - Suggested fixture: defect mentioning 'ReversedParameter(l)', 'ReversedParameter(f)', 'c2d->Reverse()'
- **Branch 5** @ line 779 — *range_mismatch_after_reversal* — **UNCOVERED**
  - What it tests: Whether B-spline range changed due to numerical accuracy
  - Repair action: Clear SameRange/SameParameter flags if range differs
  - Suggested fixture: defect mentioning 'first != newf || last != newl', 'B.SameRange(edge, false)', 'B.SameParameter(edge, false)'

#### `ShapeFix_Edge.FixSameParameter` — lines 796–936
(16 branches, 2 covered.)

- **Branch 1** @ line 804 — *degenerated_edge* — **UNCOVERED**
  - What it tests: Edge degeneracy check
  - Repair action: Mark SameParameter true; fix SameRange if needed; return false
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(edge)', 'TempSameRange'
- **Branch 2** @ line 807 — *same_range_mismatch* — **UNCOVERED**
  - What it tests: Whether 3D curve range matches PCurve ranges
  - Repair action: Enforce SameRange if not already set
  - Suggested fixture: defect mentioning '!BRep_Tool::SameRange(edge)', 'TempSameRange'
- **Branch 3** @ line 826 — *initial_same_parameter_state* — **UNCOVERED**
  - What it tests: Whether edge initially had SameParameter property
  - Repair action: Branch logic for repairing non-SP edges vs SP edges
  - Suggested fixture: defect mentioning 'wasSP = BRep_Tool::SameParameter(edge)'
- **Branch 4** @ line 831 — *same_range_enforcement* — **UNCOVERED**
  - What it tests: SameRange requirement for non-SP edge
  - Repair action: TempSameRange if not already set
  - Suggested fixture: defect mentioning '!BRep_Tool::SameRange(edge)', 'TempSameRange'
- **Branch 5** @ line 837 — *non_sp_edge_repair_attempt* — COVERED by: twi044
  - What it tests: Whether edge was originally non-SameParameter
  - Repair action: Create copy and attempt BRepLib::SameParameter
- **Branch 6** @ line 850 — *same_parameter_algorithm_fail* — **UNCOVERED**
  - What it tests: Whether BRepLib::SameParameter succeeded on copy
  - Repair action: Record FAIL2 if SameParameter not achieved
  - Suggested fixture: defect mentioning 'BRepLib::SameParameter(copyedge', '!SP', 'ShapeExtend_FAIL2'
- **Branch 7** @ line 858 — *exception_in_same_parameter* — **UNCOVERED**
  - What it tests: Exception handling for BRepLib::SameParameter
  - Repair action: Catch exception and record FAIL2 status
  - Suggested fixture: defect mentioning 'catch (Standard_Failure const&', 'ShapeExtend_FAIL2'
- **Branch 8** @ line 875 — *pcurve_face_context* — **UNCOVERED**
  - What it tests: Whether to check PCurves with face or empty
  - Repair action: Use provided face if wasSP; use empty face otherwise
  - Suggested fixture: defect mentioning 'aFace = face', 'anEmptyFace', '!wasSP'
- **Branch 9** @ line 882 — *pcurve_deviation_check* — **UNCOVERED**
  - What it tests: Maximum deviation between PCurve and 3D curve
  - Repair action: Record maxdev and check for FAIL2 status
  - Suggested fixture: defect mentioning 'CheckSameParameter(edge, aFace', 'ShapeExtend_FAIL1'
- **Branch 10** @ line 889 — *brlib_variant_comparison* — **UNCOVERED**
  - What it tests: Whether BRepLib variant achieved SameParameter
  - Repair action: Compare tolerance/deviation and select best variant
  - Suggested fixture: defect mentioning 'if (SP)', 'BRLTol = BRep_Tool::Tolerance(copyedge)', 'ShapeExtend_DONE3'
- **Branch 11** @ line 894 — *tolerance_deviation_max* — **UNCOVERED**
  - What it tests: Whether tolerance or deviation controls selection
  - Repair action: Use max of tolerance and deviation
  - Suggested fixture: defect mentioning 'BRLTol < BRLDev', 'BRLTol = BRLDev'
- **Branch 12** @ line 900 — *best_variant_selection* — **UNCOVERED**
  - What it tests: Whether BRepLib result is better than original
  - Repair action: Copy PCurves and tolerances from copyedge if better
  - Suggested fixture: defect mentioning 'BRLTol < maxdev', 'ShapeBuild_Edge().CopyPCurves', 'ShapeExtend_DONE5'
- **Branch 13** @ line 915 — *first_vertex_tolerance_restore* — **UNCOVERED**
  - What it tests: Whether first vertex exists and needs tolerance update
  - Repair action: Set first vertex tolerance to max(maxdev, TolFV)
  - Suggested fixture: defect mentioning '!V1.IsNull()', 'SFST.SetTolerance(V1'
- **Branch 14** @ line 919 — *last_vertex_tolerance_restore* — **UNCOVERED**
  - What it tests: Whether last vertex exists and needs tolerance update
  - Repair action: Set last vertex tolerance to max(maxdev, TolLV)
  - Suggested fixture: defect mentioning '!V2.IsNull()', 'SFST.SetTolerance(V2'
- **Branch 15** @ line 924 — *deviation_exceeds_tolerance* — COVERED by: twi048, twi059, twi061
  - What it tests: Whether max deviation exceeds edge tolerance
  - Repair action: Update edge tolerance and recursively fix vertices
- **Branch 16** @ line 931 — *non_sp_edge_final_status* — **UNCOVERED**
  - What it tests: Whether non-SP edge repair ultimately failed
  - Repair action: Set DONE2 status if initially non-SP and still not SP
  - Suggested fixture: defect mentioning '!wasSP && !SP', 'ShapeExtend_DONE2'

#### `ShapeFix_Edge.FixVertexTolerance(edge)` — lines 689–731
(6 branches, 0 covered.)

- **Branch 1** @ line 694 — *context_null* — **UNCOVERED**
  - What it tests: Whether context exists for shape transformation
  - Repair action: Apply context transform; return false if invalid
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'Context()->Apply(edge)'
- **Branch 2** @ line 697 — *invalid_shape_type* — **UNCOVERED**
  - What it tests: Edge type validation after context apply
  - Repair action: Skip repair for non-EDGE shapes
  - Suggested fixture: defect mentioning 'aShape.IsNull()', 'ShapeType() != TopAbs_EDGE'
- **Branch 3** @ line 705 — *vertex_tolerance_check_fail* — **UNCOVERED**
  - What it tests: Tolerance consistency at vertices (no face)
  - Repair action: Abort if CheckVertexTolerance without face reports no issues
  - Suggested fixture: defect mentioning 'CheckVertexTolerance(anEdgeCopy, toler'
- **Branch 4** @ line 709 — *tolerance_status_done1* — **UNCOVERED**
  - What it tests: First vertex tolerance repair occurred
  - Repair action: Set DONE1 status flag
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE1)'
- **Branch 5** @ line 713 — *tolerance_status_done2* — **UNCOVERED**
  - What it tests: Second vertex tolerance repair occurred
  - Repair action: Set DONE2 status flag
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE2)'
- **Branch 6** @ line 720 — *context_vs_direct_update* — **UNCOVERED**
  - What it tests: Whether to use context or direct BRep_Builder
  - Repair action: CopyVertex via context or UpdateVertex directly
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'CopyVertex', 'UpdateVertex'

#### `ShapeFix_Edge.FixVertexTolerance(edge,face)` — lines 642–685
(6 branches, 0 covered.)

- **Branch 1** @ line 647 — *context_null* — **UNCOVERED**
  - What it tests: Whether context exists for shape transformation
  - Repair action: Apply context transform to edge; return false if result invalid
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'Context()->Apply(edge)'
- **Branch 2** @ line 650 — *invalid_shape_type* — **UNCOVERED**
  - What it tests: Edge type validation after context apply
  - Repair action: Skip repair; return false for non-EDGE shapes
  - Suggested fixture: defect mentioning 'aShape.IsNull()', 'ShapeType() != TopAbs_EDGE'
- **Branch 3** @ line 659 — *vertex_tolerance_check_fail* — **UNCOVERED**
  - What it tests: Tolerance consistency at vertices
  - Repair action: Abort if CheckVertexTolerance reports no issues
  - Suggested fixture: defect mentioning 'CheckVertexTolerance(anEdgeCopy, face'
- **Branch 4** @ line 663 — *tolerance_status_done1* — **UNCOVERED**
  - What it tests: First vertex tolerance repair occurred
  - Repair action: Set DONE1 status flag
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE1)'
- **Branch 5** @ line 667 — *tolerance_status_done2* — **UNCOVERED**
  - What it tests: Second vertex tolerance repair occurred
  - Repair action: Set DONE2 status flag
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE2)'
- **Branch 6** @ line 674 — *context_vs_direct_update* — **UNCOVERED**
  - What it tests: Whether to use context or direct BRep_Builder
  - Repair action: CopyVertex via context or UpdateVertex directly
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'CopyVertex', 'UpdateVertex'

#### `ShapeFix_Edge.FixVertexTolerance_1stOverload` — lines 643–685
(8 branches, 1 covered.)

- **Branch 1** @ line 647 — *Context_apply_missing* — **UNCOVERED**
  - What it tests: Context available (transformation context in wire fixing)
  - Repair action: Apply context to get transformed edge copy
  - Suggested fixture: defect mentioning 'Context().IsNull', 'Context()->Apply'
- **Branch 2** @ line 650 — *Context_result_null* — **UNCOVERED**
  - What it tests: Context transform returned null shape
  - Repair action: Fail, return false
  - Suggested fixture: defect mentioning 'aShape.IsNull'
- **Branch 3** @ line 650 — *Context_result_wrong_type* — **UNCOVERED**
  - What it tests: Context returned non-edge shape
  - Repair action: Fail, return false
  - Suggested fixture: defect mentioning 'TopAbs_EDGE'
- **Branch 4** @ line 659 — *Vertex_tolerance_out_of_range* — COVERED by: twi061
  - What it tests: Vertex tolerance does not cover curve endpoints
  - Repair action: Update vertex tolerances to correct values
- **Branch 5** @ line 663 — *Tolerance_update_status_done1* — **UNCOVERED**
  - What it tests: First vertex tolerance was adjusted
  - Repair action: Set DONE1 status flag
  - Suggested fixture: defect mentioning 'ShapeExtend_DONE1'
- **Branch 6** @ line 667 — *Tolerance_update_status_done2* — **UNCOVERED**
  - What it tests: Second vertex tolerance was adjusted
  - Repair action: Set DONE2 status flag
  - Suggested fixture: defect mentioning 'ShapeExtend_DONE2'
- **Branch 7** @ line 674 — *Context_update_vertices* — **UNCOVERED**
  - What it tests: Context available for vertex updates
  - Repair action: Update vertices via context CopyVertex
  - Suggested fixture: defect mentioning 'Context()->CopyVertex'
- **Branch 8** @ line 681 — *Direct_vertex_tolerance_update* — **UNCOVERED**
  - What it tests: No context available, direct update
  - Repair action: Update vertices directly via BRep_Builder
  - Suggested fixture: defect mentioning 'B.UpdateVertex'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_EdgeConnect.cxx`

2 methods, 30 branches, 5 covered.

#### `ShapeFix_EdgeConnect.Add` — lines 49–119
(6 branches, 1 covered.)

- **Branch 1** @ line 55 — *first_vertex_already_bound* — **UNCOVERED**
  - What it tests: First vertex mapping exists; check if second is also bound to different shared vertex
  - Repair action: merge_vertex_lists
  - Suggested fixture: defect mentioning 'myVertices.IsBound(theFirstVertex)'
- **Branch 2** @ line 59 — *both_vertices_already_bound_to_different_shared* — **UNCOVERED**
  - What it tests: Both vertices are bound; they map to different shared vertices
  - Repair action: concatenate_and_rebind_lists
  - Suggested fixture: defect mentioning 'myVertices.IsBound(theSecondVertex)', '!theFirstShared.IsSame(theSecondShared)'
- **Branch 3** @ line 63 — *conflict_resolution_two_connected_components* — **UNCOVERED**
  - What it tests: Two separate edge connection components meet; merge and rebind all edges
  - Repair action: rebind_and_append_list
  - Suggested fixture: defect mentioning 'NCollection_List<TopoDS_Shape>::Iterator', 'Rebind shared vertex'
- **Branch 4** @ line 83 — *first_bound_second_unbound* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: First vertex is bound, second is not; bind second to first's shared vertex
  - Repair action: bind_second_vertex_append_edge
- **Branch 5** @ line 95 — *second_bound_first_unbound* — **UNCOVERED**
  - What it tests: Second vertex is bound but first is not
  - Repair action: bind_first_vertex_prepend_edge
  - Suggested fixture: defect mentioning 'myVertices.IsBound(theSecondVertex)', 'first vertex and first edge'
- **Branch 6** @ line 106 — *neither_vertex_bound_new_chain* — **UNCOVERED**
  - What it tests: Neither vertex is bound; create new binding and list
  - Repair action: create_new_edge_chain
  - Suggested fixture: defect mentioning 'None is bound', 'Create new bindings', 'theNewList.Bind'

#### `ShapeFix_EdgeConnect.Build` — lines 157–353
(24 branches, 4 covered.)

- **Branch 11** @ line 178 — *iterate_edge_pairs_for_vertex* — **UNCOVERED**
  - What it tests: Process edge-vertex pairs from list; accumulate curve positions
  - Repair action: accumulate_endpoint_positions
  - Suggested fixture: defect mentioning 'theLIterator.Initialize(theList)', 'theVertex.IsSame'
- **Branch 12** @ line 186 — *edge_has_forward_orientation* — **UNCOVERED**
  - What it tests: Orient edge forward to get consistent start/end vertices
  - Repair action: normalize_edge_direction
  - Suggested fixture: defect mentioning 'theEdge.Orientation(TopAbs_FORWARD)', 'TopExp::Vertices'
- **Branch 13** @ line 188 — *vertex_at_edge_start* — **UNCOVERED**
  - What it tests: Target vertex matches edge start point
  - Repair action: sample_start_curve_point
  - Suggested fixture: defect mentioning 'use_start', 'theVertex.IsSame(theStart)'
- **Branch 14** @ line 189 — *vertex_at_edge_end* — **UNCOVERED**
  - What it tests: Target vertex matches edge end point
  - Repair action: sample_end_curve_point
  - Suggested fixture: defect mentioning 'use_end', 'theVertex.IsSame(theEnd)'
- **Branch 15** @ line 197 — *curve_representation_exists* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge has valid geometric curve representation
  - Repair action: evaluate_curve_endpoints
- **Branch 16** @ line 206 — *accumulate_from_start_point* — **UNCOVERED**
  - What it tests: use_start flag indicates vertex at edge start
  - Repair action: sample_first_parameter_position
  - Suggested fixture: defect mentioning 'if (use_start)', 'GC->D0(theFParam'
- **Branch 17** @ line 211 — *accumulate_from_end_point* — **UNCOVERED**
  - What it tests: use_end flag indicates vertex at edge end
  - Repair action: sample_last_parameter_position
  - Suggested fixture: defect mentioning 'if (use_end)', 'GC->D0(theLParam'
- **Branch 18** @ line 224 — *position_strategy_mean_vs_bounds* — **UNCOVERED**
  - What it tests: Preprocessor flag controls averaging strategy
  - Repair action: compute_average_coordinate
  - Suggested fixture: defect mentioning 'POSITION_USES_MEAN_POINT', '#define', '#else'
- **Branch 19** @ line 228 — *single_vs_multiple_positions* — **UNCOVERED**
  - What it tests: Multiple positions exist; compute mean
  - Repair action: average_positions
  - Suggested fixture: defect mentioning 'if (theNbPos > 1)', 'thePosition /= theNbPos'
- **Branch 20** @ line 235 — *first_position_init_bounds* — **UNCOVERED**
  - What it tests: First position initializes bounding box
  - Repair action: initialize_bounds
  - Suggested fixture: defect mentioning 'if (i == 1)', 'theLBound = theRBound'
- **Branch 21** @ line 240 — *update_x_lower_bound* — **UNCOVERED**
  - What it tests: Current X coordinate below current lower bound
  - Repair action: update_x_minimum
  - Suggested fixture: defect mentioning 'val < theLBound.X()', 'SetX'
- **Branch 22** @ line 244 — *update_x_upper_bound* — **UNCOVERED**
  - What it tests: Current X coordinate above current upper bound
  - Repair action: update_x_maximum
  - Suggested fixture: defect mentioning 'val > theRBound.X()', 'SetX'
- **Branch 23** @ line 248 — *update_y_lower_bound* — **UNCOVERED**
  - What it tests: Current Y coordinate below current lower bound
  - Repair action: update_y_minimum
  - Suggested fixture: defect mentioning 'val < theLBound.Y()', 'SetY'
- **Branch 24** @ line 253 — *update_y_upper_bound* — **UNCOVERED**
  - What it tests: Current Y coordinate above current upper bound
  - Repair action: update_y_maximum
  - Suggested fixture: defect mentioning 'val > theRBound.Y()', 'SetY'
- **Branch 25** @ line 257 — *update_z_lower_bound* — **UNCOVERED**
  - What it tests: Current Z coordinate below current lower bound
  - Repair action: update_z_minimum
  - Suggested fixture: defect mentioning 'val < theLBound.Z()', 'SetZ'
- **Branch 26** @ line 262 — *update_z_upper_bound* — **UNCOVERED**
  - What it tests: Current Z coordinate above current upper bound
  - Repair action: update_z_maximum
  - Suggested fixture: defect mentioning 'val > theRBound.Z()', 'SetZ'
- **Branch 27** @ line 267 — *centroid_from_bounds* — **UNCOVERED**
  - What it tests: Multiple positions; compute centroid from bounding box
  - Repair action: midpoint_of_bounding_box
  - Suggested fixture: defect mentioning 'if (theNbPos > 1)', 'thePosition = (theLBound + theRBound)'
- **Branch 28** @ line 279 — *max_deviation_exceeds_current* — **UNCOVERED**
  - What it tests: Current position deviation larger than running maximum
  - Repair action: update_max_deviation
  - Suggested fixture: defect mentioning 'if (theDeviation > theMaxDev)', 'theMaxDev = theDeviation'
- **Branch 29** @ line 285 — *tolerance_below_precision_threshold* — COVERED by: gp013, tb001, tb007, tb018, tb019, twi040
  - What it tests: Computed max deviation smaller than numerical precision
  - Repair action: set_minimum_tolerance
- **Branch 30** @ line 304 — *vertex_at_old_start_position* — **UNCOVERED**
  - What it tests: Second pass: vertex at original edge start
  - Repair action: select_old_start_for_removal
  - Suggested fixture: defect mentioning 'use_start', 'theOldVertex = theStart'
- **Branch 31** @ line 309 — *old_vertex_mismatch_with_new* — **UNCOVERED**
  - What it tests: Old and new vertices are different; need replacement
  - Repair action: replace_old_vertex_with_shared
  - Suggested fixture: defect mentioning '!theOldVertex.IsSame(theNewVertex)'
- **Branch 32** @ line 321 — *new_vertex_forward_orientation* — **UNCOVERED**
  - What it tests: Replacement vertex at start needs forward orientation
  - Repair action: orient_shared_vertex_forward
  - Suggested fixture: defect mentioning 'if (use_start)', 'Oriented(TopAbs_FORWARD)'
- **Branch 33** @ line 327 — *new_vertex_reversed_orientation* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Replacement vertex at end needs reversed orientation
  - Repair action: orient_shared_vertex_reversed
- **Branch 34** @ line 338 — *closed_edge_double_vertex_replacement* — COVERED by: ad086, twi019
  - What it tests: Edge has same vertex at both start and end; replace both
  - Repair action: replace_closed_edge_vertices


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Face.cxx`

15 methods, 155 branches, 18 covered.

#### `ShapeFix_Face.Add` — lines 225–235
(1 branches, 1 covered.)

- **Branch 1** @ line 227 — *Null wire guard* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Reject null wires before adding
  - Repair action: Return early if wire.IsNull() to prevent invalid topology

#### `ShapeFix_Face.ClearModes` — lines 132–145
(2 branches, 0 covered.)

- **Branch 1** @ line 133 — *Mode reset* — **UNCOVERED**
  - What it tests: Initialize all wire-fixing modes to disabled
  - Repair action: Set all mode flags to -1 (disabled) except AutoCorrectPrecisionMode
  - Suggested fixture: defect mentioning 'myFixWireMode = -1'
- **Branch 2** @ line 143 — *Mode reset exception* — **UNCOVERED**
  - What it tests: AutoCorrectPrecisionMode defaults to enabled
  - Repair action: Set AutoCorrectPrecisionMode to 1 (enabled) while others are -1
  - Suggested fixture: defect mentioning 'myAutoCorrectPrecisionMode = 1'

#### `ShapeFix_Face.FixAddNaturalBound` — lines 876–1106
(21 branches, 5 covered.)

- **Branch 1** @ line 878 — *Null surface guard* — COVERED by: in014
  - What it tests: Detect if surface is missing (invalid state)
  - Repair action: Return false early if mySurf is null, preventing downstream errors
- **Branch 2** @ line 883 — *Context application* — **UNCOVERED**
  - What it tests: Check if context tracking is enabled
  - Repair action: If context exists, apply it to get potentially modified face
  - Suggested fixture: defect mentioning 'if (!Context().IsNull())', 'Context()->Apply(myFace)'
- **Branch 3** @ line 895 — *Wire type filtering* — **UNCOVERED**
  - What it tests: Check if shape is a valid wire (correct type and orientation)
  - Repair action: Collect valid wires; collect non-wire shapes separately
  - Suggested fixture: defect mentioning 'if (wi.Value().ShapeType() == TopAbs_WIRE', 'TopAbs_FORWARD', 'TopAbs_REVERSED'
- **Branch 4** @ line 908 — *Empty face UV bounds check* — **UNCOVERED**
  - What it tests: Check if face is empty (no wires) and surface has finite bounds
  - Repair action: Create new face with natural bounds if empty and bounds finite
  - Suggested fixture: defect mentioning 'if (ws.IsEmpty() && !IsSurfaceUVInfinite'
- **Branch 5** @ line 915 — *Context replacement (empty face)* — **UNCOVERED**
  - What it tests: Check if context exists when creating new face
  - Repair action: Register new face in context to track topology changes
  - Suggested fixture: defect mentioning 'if (!Context().IsNull())', 'Context()->Replace(myFace, aNewFace)'
- **Branch 6** @ line 942 — *Natural bound necessity check* — COVERED by: in014
  - What it tests: Check if surface actually needs natural bounds added
  - Repair action: Call isNeedAddNaturalBound(ws); return false if bounds not needed
- **Branch 7** @ line 967 — *U-direction closed surface* — **UNCOVERED**
  - What it tests: Check if surface is closed in U direction
  - Repair action: If U-closed, cut intervals in intU based on wire bounds
  - Suggested fixture: defect mentioning 'if (mySurf->IsUClosed())', 'CutInterval(intU'
- **Branch 8** @ line 971 — *V-direction closed surface* — **UNCOVERED**
  - What it tests: Check if surface is closed in V direction
  - Repair action: If V-closed, cut intervals in intV based on wire bounds
  - Suggested fixture: defect mentioning 'if (mySurf->IsVClosed())', 'CutInterval(intV'
- **Branch 9** @ line 980 — *U-closed shift computation* — **UNCOVERED**
  - What it tests: Check if surface is U-closed for shift calculation
  - Repair action: If U-closed, compute shift.X() = FindBestInterval(intU)
  - Suggested fixture: defect mentioning 'if (mySurf->IsUClosed())', 'shift.SetX'
- **Branch 10** @ line 984 — *V-closed shift computation* — **UNCOVERED**
  - What it tests: Check if surface is V-closed for shift calculation
  - Repair action: If V-closed, compute shift.Y() = FindBestInterval(intV)
  - Suggested fixture: defect mentioning 'if (mySurf->IsVClosed())', 'shift.SetY'
- **Branch 11** @ line 995 — *U-direction wire adjustment* — **UNCOVERED**
  - What it tests: Check if U-closed for per-wire U adjustment
  - Repair action: If U-closed, adjust wire U coordinates relative to center
  - Suggested fixture: defect mentioning 'if (mySurf->IsUClosed())', 'AdjustByPeriod'
- **Branch 12** @ line 999 — *V-direction wire adjustment* — **UNCOVERED**
  - What it tests: Check if V-closed for per-wire V adjustment
  - Repair action: If V-closed, adjust wire V coordinates relative to center
  - Suggested fixture: defect mentioning 'if (mySurf->IsVClosed())', 'AdjustByPeriod'
- **Branch 13** @ line 1014 — *Natural bounds wire type filter* — **UNCOVERED**
  - What it tests: Check if shape from natural bounds is a wire
  - Repair action: Skip non-wire shapes when collecting natural boundary wires
  - Suggested fixture: defect mentioning 'if (wi.Value().ShapeType() != TopAbs_WIRE)'
- **Branch 14** @ line 1020 — *Natural bounds shift check* — **UNCOVERED**
  - What it tests: Check if shift is effectively zero (no adjustment needed)
  - Repair action: Skip shifting natural bound wire if shift modulus near zero
  - Suggested fixture: defect mentioning 'if (shift.XY().Modulus() < ::Precision::PConfusion())'
- **Branch 15** @ line 1030 — *Sphere degenerated merge* — **UNCOVERED**
  - What it tests: Check if surface is sphere AND exactly one natural bound added
  - Repair action: On sphere with exactly one new boundary, merge touching wires at degenerated points
  - Suggested fixture: defect mentioning 'if (mySurf->Adaptor3d()->GetType() == GeomAbs_Sphere'
- **Branch 16** @ line 1039 — *Degenerated edge detection* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Check if edge in wire is degenerated
  - Repair action: Skip non-degenerated edges; process only degenerated edges
- **Branch 17** @ line 1049 — *Boundary degenerated search* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Find matching degenerated edge in natural boundary
  - Repair action: Skip non-degenerated boundary edges while searching for matching degenerated point
- **Branch 18** @ line 1053 — *Vertex matching* — **UNCOVERED**
  - What it tests: Check if degenerated edge vertices match boundary degenerated edge
  - Repair action: If vertex matches, merge the hole wire into boundary at that position
  - Suggested fixture: defect mentioning 'if (BRepTools::Compare(V, sae.FirstVertex(bnd->Edge(k))))'
- **Branch 19** @ line 1058 — *No boundary match fallback* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Check if matching degenerated point not found in boundary
  - Repair action: If no match found in boundary, skip merging this hole (continue)
- **Branch 20** @ line 1092 — *Face orientation handling* — **UNCOVERED**
  - What it tests: Check if face should be reversed (myFwd = false)
  - Repair action: If myFwd false, set resulting shape orientation to REVERSED
  - Suggested fixture: defect mentioning 'if (!myFwd)', 'S.Orientation(TopAbs_REVERSED)'
- **Branch 21** @ line 1096 — *Context update (final)* — **UNCOVERED**
  - What it tests: Check if context exists for final face replacement
  - Repair action: Register final reconstructed face in context
  - Suggested fixture: defect mentioning 'if (!Context().IsNull())', 'Context()->Replace(myFace, S)'

#### `ShapeFix_Face.FixLoopWire` — lines 2479–2642
(11 branches, 1 covered.)

- **Branch 1** @ line 2485 — *NoLoopDetected* — **UNCOVERED**
  - What it tests: Wire loop check finds no loops/self-intersections
  - Repair action: Return false (no fix needed)
  - Suggested fixture: defect mentioning 'FixWireTool()->Analyzer()->CheckLoop()'
- **Branch 2** @ line 2506 — *DuplicateEdgeInLoop* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge already processed in another loop
  - Repair action: Skip edge to avoid duplicates
- **Branch 3** @ line 2513 — *SeamEdgeLoop* — **UNCOVERED**
  - What it tests: Edge is a seam edge (needs both directions)
  - Repair action: Add edge twice (forward and reversed)
  - Suggested fixture: defect mentioning 'aMapSeemEdges.Contains(Edge)'
- **Branch 4** @ line 2526 — *SingleSmallEdgeWire* — **UNCOVERED**
  - What it tests: Reconstructed wire is single small edge
  - Repair action: Skip trivial single-edge wire
  - Suggested fixture: defect mentioning 'aWireData->NbEdges() == 1 && aMapSmallEdges'
- **Branch 5** @ line 2534 — *ClosedWireFromLoop* — **UNCOVERED**
  - What it tests: Reconstructed wire is closed (start == end vertex)
  - Repair action: Reorder and add to results
  - Suggested fixture: defect mentioning 'aV1.IsSame(aV2)', 'FixReorder()'
- **Branch 6** @ line 2550 — *SingleOpenWire* — **UNCOVERED**
  - What it tests: Only one open (non-closed) wire from loops
  - Repair action: Add directly to results
  - Suggested fixture: defect mentioning 'aSeqWires.Length() == 1'
- **Branch 7** @ line 2568 — *TwoCommonVertices* — **UNCOVERED**
  - What it tests: Two wires share both endpoints
  - Repair action: Merge wires and reorder
  - Suggested fixture: defect mentioning '(aV1.IsSame(aV21) || aV1.IsSame(aV22))', 'asewd->Add(aWire2)'
- **Branch 8** @ line 2586 — *FewWiresRemaining* — **UNCOVERED**
  - What it tests: After merging, fewer than 3 wires remain
  - Repair action: Add remaining wires directly
  - Suggested fixture: defect mentioning 'if (aSeqWires.Length() < 3)'
- **Branch 9** @ line 2607 — *SingleCommonVertex* — **UNCOVERED**
  - What it tests: Two wires share one endpoint
  - Repair action: Merge and reorder wires
  - Suggested fixture: defect mentioning '(aV1.IsSame(aV21) || aV1.IsSame(aV22)) ||'
- **Branch 10** @ line 2627 — *NonPlanarSurfaceLoop* — **UNCOVERED**
  - What it tests: Wire on non-planar surface (not closed in 2D)
  - Repair action: Validate wire closure in 2D parameter space
  - Suggested fixture: defect mentioning 'mySurf && mySurf->Adaptor3d()->GetType() != GeomAbs_Plane'
- **Branch 11** @ line 2637 — *Wire2DUnclosed* — **UNCOVERED**
  - What it tests: Wire is open in 2D parameter space
  - Repair action: Return false (invalid wire)
  - Suggested fixture: defect mentioning 'isClosed2D(tmpFace, awire)', 'isClosed = false'

#### `ShapeFix_Face.FixMissingSeam` — lines 1723–2326
(26 branches, 7 covered.)

- **Branch 1** @ line 1725 — *null_surface* — COVERED by: in014
  - What it tests: Surface handle is null/invalid
  - Repair action: early_return_false
- **Branch 2** @ line 1730 — *open_surface* — COVERED by: in014
  - What it tests: Surface not closed in U or V direction
  - Repair action: early_return_false
- **Branch 3** @ line 1742 — *non_periodic_bspline* — **UNCOVERED**
  - What it tests: BSpline surface exists but is not periodic in either direction
  - Repair action: early_return_false
  - Suggested fixture: defect mentioning 'STANDARD_TYPE(Geom_BSplineSurface)', '!BSpl->IsUPeriodic() && !BSpl->IsVPeriodic()'
- **Branch 4** @ line 1759 — *infinite_u_bounds* — **UNCOVERED**
  - What it tests: U parametric bounds are infinite at start
  - Repair action: normalize_u_bounds
  - Suggested fixture: defect mentioning '::Precision::IsInfinite(SUF)', 'SUF = fU1'
- **Branch 5** @ line 1763 — *infinite_u_bounds* — **UNCOVERED**
  - What it tests: U parametric bounds are infinite at end
  - Repair action: normalize_u_bounds
  - Suggested fixture: defect mentioning '::Precision::IsInfinite(SUL)', 'SUL = fU2'
- **Branch 6** @ line 1767 — *degenerate_u_range* — **UNCOVERED**
  - What it tests: U range collapses after normalization
  - Repair action: expand_u_bounds
  - Suggested fixture: defect mentioning 'std::abs(SUL - SUF) < ::Precision::PConfusion()', 'SUL += 1000'
- **Branch 7** @ line 1779 — *infinite_v_bounds* — **UNCOVERED**
  - What it tests: V parametric bounds are infinite at start
  - Repair action: normalize_v_bounds
  - Suggested fixture: defect mentioning '::Precision::IsInfinite(SVF)', 'SVF = fV1'
- **Branch 8** @ line 1783 — *infinite_v_bounds* — **UNCOVERED**
  - What it tests: V parametric bounds are infinite at end
  - Repair action: normalize_v_bounds
  - Suggested fixture: defect mentioning '::Precision::IsInfinite(SVL)', 'SVL = fV2'
- **Branch 9** @ line 1787 — *degenerate_v_range* — **UNCOVERED**
  - What it tests: V range collapses after normalization
  - Repair action: expand_v_bounds
  - Suggested fixture: defect mentioning 'std::abs(SVL - SVF) < ::Precision::PConfusion()', 'SVL += 1000'
- **Branch 10** @ line 1838 — *no_valid_wire* — COVERED by: in014
  - What it tests: First wire w1 remains null after checking all wires
  - Repair action: early_return_false
- **Branch 11** @ line 1841 — *degenerated_torus* — **UNCOVERED**
  - What it tests: Surface is toroidal with major radius < minor radius
  - Repair action: mark_degenerated_torus
  - Suggested fixture: defect mentioning 'Geom_ToroidalSurface', 'MajorRadius() < MinorRadius()'
- **Branch 12** @ line 1848 — *single_wire_periodic_u* — **UNCOVERED**
  - What it tests: Only one wire found, open in U, degenerated torus
  - Repair action: insert_degenerated_edge_torus
  - Suggested fixture: defect mentioning 'anIsDegeneratedTor', 'M_PI + aPhi', 'aPhi = std::acos(-aRa / aRi)'
- **Branch 13** @ line 1858 — *single_wire_sphere_u* — **UNCOVERED**
  - What it tests: Only one wire, open in U direction on spherical surface
  - Repair action: insert_degenerated_edge_sphere
  - Suggested fixture: defect mentioning 'Geom_SphericalSurface', 'ismodeu', '0.5 * M_PI'
- **Branch 14** @ line 1865 — *single_wire_bspline_v* — **UNCOVERED**
  - What it tests: Only one wire, open in V, BSpline surface with pole detection
  - Repair action: insert_degenerated_edge_pole
  - Suggested fixture: defect mentioning 'ismodev && Geom_BSplineSurface', 'SVF', 'SVL'
- **Branch 15** @ line 1885 — *single_wire_bspline_u* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+919 more)
  - What it tests: Only one wire, open in U, BSpline surface with pole detection
  - Repair action: insert_degenerated_edge_pole
- **Branch 16** @ line 1910 — *single_wire_unhandled* — COVERED by: bo006, in014, ls031, n009, tb013, twi046, twi083, u039 (+1 more)
  - What it tests: Only one wire but surface type/defect pattern not matching known cases
  - Repair action: early_return_false
- **Branch 17** @ line 1950 — *orientation_mismatch_open_surface* — **UNCOVERED**
  - What it tests: Surface closed only in one direction; wire orientations must be checked
  - Repair action: reverse_both_wires_if_needed
  - Suggested fixture: defect mentioning '!vclosed || !uclosed || anIsDegeneratedTor', 'deltaOther * isneg < 0', 'w1.Reverse()'
- **Branch 18** @ line 1999 — *doubly_closed_surface_shift* — **UNCOVERED**
  - What it tests: Both U and V closed; non-degenerate torus; check if wires need period shift
  - Repair action: shift_wire_by_period
  - Suggested fixture: defect mentioning 'uclosed && vclosed && !anIsDegeneratedTor', 'ShapeAnalysis::AdjustByPeriod', 'm1[coord][1] - m1[coord][0] <= period'
- **Branch 19** @ line 2076 — *seam_position_not_found* — COVERED by: in014
  - What it tests: PCurve extraction fails for edge in wires
  - Repair action: early_return_false
- **Branch 20** @ line 2110 — *seam_position_u_optimize* — **UNCOVERED**
  - What it tests: U-closed surface; find edge endpoint closest to seam origin
  - Repair action: update_seam_position_u
  - Suggested fixture: defect mentioning 'uclosed && ismodeu', 'foundU == 1', 'std::abs(pos1.X()) < std::abs(uf)'
- **Branch 21** @ line 2126 — *seam_position_v_optimize* — **UNCOVERED**
  - What it tests: V-closed surface; find edge endpoint closest to seam origin
  - Repair action: update_seam_position_v
  - Suggested fixture: defect mentioning 'vclosed && !ismodeu', 'foundV == 1', 'std::abs(pos1.Y()) < std::abs(vf)'
- **Branch 22** @ line 2161 — *seam_endpoints_aligned_u* — **UNCOVERED**
  - What it tests: Endpoints of edges from both wires match in U direction
  - Repair action: confirm_seam_position_u
  - Suggested fixture: defect mentioning 'std::abs(pos2.X() - pos1.X()) < ::Precision::PConfusion()', 'foundU = 2'
- **Branch 23** @ line 2173 — *seam_endpoints_aligned_v* — **UNCOVERED**
  - What it tests: Endpoints of edges from both wires match in V direction
  - Repair action: confirm_seam_position_v
  - Suggested fixture: defect mentioning 'std::abs(pos2.Y() - pos1.Y()) < ::Precision::PConfusion()', 'foundV = 2'
- **Branch 24** @ line 2197 — *seam_u_out_of_bounds* — **UNCOVERED**
  - What it tests: Computed seam U position outside surface bounds
  - Repair action: adjust_seam_u_to_period
  - Suggested fixture: defect mentioning 'uf < SUF || uf > SUL', 'ShapeAnalysis::AdjustToPeriod'
- **Branch 25** @ line 2201 — *seam_v_out_of_bounds* — **UNCOVERED**
  - What it tests: Computed seam V position outside surface bounds
  - Repair action: adjust_seam_v_to_period
  - Suggested fixture: defect mentioning 'vf < SVF || vf > SVL', 'ShapeAnalysis::AdjustToPeriod'
- **Branch 26** @ line 2250 — *small_wire_removal* — COVERED by: ad086, tfa006, tfa007, tfa008, tfa040, tfa041, tfa042, tfa043 (+6 more)
  - What it tests: Seam insertion creates small/degenerate wires that must be removed
  - Repair action: remove_small_wires_and_faces

#### `ShapeFix_Face.FixOrientation` — lines 1168–1646
(19 branches, 2 covered.)

- **Branch 1** @ line 1171 — *ContextModified* — **UNCOVERED**
  - What it tests: Context is set and has modifications to apply
  - Repair action: Apply context modifications to face
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Apply'
- **Branch 2** @ line 1182 — *InvalidWireOrientation* — **UNCOVERED**
  - What it tests: Wire has invalid orientation (not FORWARD or REVERSED)
  - Repair action: Skip wire or collect as sub-shape
  - Suggested fixture: defect mentioning 'wi.Value().Orientation() != TopAbs_FORWARD'
- **Branch 3** @ line 1198 — *SingleEdgeWire* — **UNCOVERED**
  - What it tests: Wire contains only one edge (no next edge)
  - Repair action: Calculate edge length for length-based filtering
  - Suggested fixture: defect mentioning '!ei.More()', 'length = 0'
- **Branch 4** @ line 1226 — *VerySmallWire* — **UNCOVERED**
  - What it tests: Wire has zero or negligible length (below precision)
  - Repair action: Collect very small wire for removal
  - Suggested fixture: defect mentioning 'length > ::Precision::Confusion()'
- **Branch 5** @ line 1246 — *NoValidWires* — **UNCOVERED**
  - What it tests: Face has no valid wires after filtering
  - Repair action: Return false (no orientation fix applied)
  - Suggested fixture: defect mentioning 'if (nb <= 0)'
- **Branch 6** @ line 1254 — *SingleWireSimpleOrientation* — **UNCOVERED**
  - What it tests: Face has only one wire; check outer bound
  - Repair action: Reverse wire if not outer bound
  - Suggested fixture: defect mentioning 'if (nb == 1)', '!ShapeAnalysis::IsOuterBound'
- **Branch 7** @ line 1279 — *MultipleWiresWithSurface* — **UNCOVERED**
  - What it tests: Multiple wires present and surface available
  - Repair action: Complex containment analysis via classification
  - Suggested fixture: defect mentioning 'else if (!mySurf.IsNull())', 'nbAll = allSubShapes.Length()'
- **Branch 8** @ line 1317 — *NoPCurveOnSurface* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge has no 2D curve representation on surface
  - Repair action: Skip edge from bounding box calculation
- **Branch 9** @ line 1324 — *BSplineOutOfBounds* — **UNCOVERED**
  - What it tests: BSpline curve parameter range vs actual bounds
  - Repair action: Load full BSpline or load within range
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom2d_BSplineCurve))'
- **Branch 10** @ line 1347 — *PeriodicWrapAround* — **UNCOVERED**
  - What it tests: Wire crosses periodic surface boundary (U or V)
  - Repair action: Shift wire to align with reference wire
  - Suggested fixture: defect mentioning 'mySurf->IsUClosed()', 'AdjustByPeriod'
- **Branch 11** @ line 1389 — *VertexInClassification* — **UNCOVERED**
  - What it tests: Isolated vertex encountered during classification
  - Repair action: Classify vertex individually with periodic shifts
  - Suggested fixture: defect mentioning 'aSh2.ShapeType() == TopAbs_VERTEX'
- **Branch 12** @ line 1410 — *InnerWireClassification* — **UNCOVERED**
  - What it tests: Nested wire classification via point-in-polygon test
  - Repair action: Determine if wire is inside/outside reference
  - Suggested fixture: defect mentioning 'aSh2.ShapeType() == TopAbs_WIRE'
- **Branch 13** @ line 1432 — *WirePartialClassification* — **UNCOVERED**
  - What it tests: Different edges of wire classify differently (inconsistent)
  - Repair action: Mark as UNKNOWN (error condition)
  - Suggested fixture: defect mentioning '!(stb == ste)', 'sta = TopAbs_UNKNOWN'
- **Branch 14** @ line 1453 — *PeriodicShiftNeeded* — **UNCOVERED**
  - What it tests: Wire is outside but shifts to inside via periodicity
  - Repair action: Apply 2D shift and toggle classification
  - Suggested fixture: defect mentioning 'stb == staout && CheckShift', 'Shift2dWire'
- **Branch 15** @ line 1477 — *ToroidalDiagonalShift* — COVERED by: a002, a005, a030, a071, a083, a099, a101, a102 (+114 more)
  - What it tests: Toroidal surface needs diagonal U,V shifts
  - Repair action: Try diagonal combinations (toroidal wrap)
- **Branch 16** @ line 1514 — *WireOrientationAmbiguous* — **UNCOVERED**
  - What it tests: Wire classification failed (sta == UNKNOWN)
  - Repair action: Send warning, keep wire as-is
  - Suggested fixture: defect mentioning 'if (sta == TopAbs_UNKNOWN)'
- **Branch 17** @ line 1523 — *WireOutsideWithInfinityIn* — **UNCOVERED**
  - What it tests: Wire is OUT but infinite point is IN
  - Repair action: Reverse wire
  - Suggested fixture: defect mentioning 'sta == TopAbs_OUT', 'staout == TopAbs_IN'
- **Branch 18** @ line 1547 — *WireInsideWithInfinityOut* — **UNCOVERED**
  - What it tests: Wire is IN but infinite point is OUT (outer loop)
  - Repair action: Mark for later reversal or keep
  - Suggested fixture: defect mentioning 'staout == TopAbs_OUT'
- **Branch 19** @ line 1605 — *AllWiresReversedWithNaturalBounds* — **UNCOVERED**
  - What it tests: All wires reversed AND natural bounds being added
  - Repair action: Cancel fix (done = false)
  - Suggested fixture: defect mentioning 'isAddNaturalBounds && nb == aSeqReversed.Length()'

#### `ShapeFix_Face.FixPeriodicDegenerated` — lines 3102–3259
(10 branches, 0 covered.)

- **Branch 1** @ line 3107 — *context_applied* — **UNCOVERED**
  - What it tests: whether context is not null
  - Repair action: apply context transformations to face
  - Suggested fixture: defect mentioning 'Context().IsNull()'
- **Branch 2** @ line 3122 — *invalid_wire_in_face* — **UNCOVERED**
  - What it tests: sub-shape has invalid type or orientation
  - Repair action: skip malformed sub-shape
  - Suggested fixture: defect mentioning 'aSubSh.ShapeType() != TopAbs_WIRE'
- **Branch 3** @ line 3136 — *surface_type_check* — **UNCOVERED**
  - What it tests: face has wrong wire count (not 1) or surface is not conical
  - Repair action: return false, method only handles single-wire conical faces
  - Suggested fixture: defect mentioning 'aNbWires != 1', 'aSurface.IsNull()', 'Geom_ConicalSurface'
- **Branch 4** @ line 3176 — *degenerate_cone_angle* — **UNCOVERED**
  - What it tests: cone semi-angle is too small (nearly zero)
  - Repair action: return false, invalid conical surface
  - Suggested fixture: defect mentioning 'fabs(aSemiAngle) <= Precision::Confusion()'
- **Branch 5** @ line 3198 — *apex_position_invalid* — **UNCOVERED**
  - What it tests: apex V parameter is too close to or inside wire loop V bounds
  - Repair action: return false, apex positioning inconsistent
  - Suggested fixture: defect mentioning 'fabs(anApexV - aMinLoopV)', 'fabs(anApexV - aMaxLoopV)', 'anApexV < aMaxLoopV && anApexV > aMinLoopV'
- **Branch 6** @ line 3207 — *apex_below_wire* — **UNCOVERED**
  - What it tests: apex V parameter is below (less than) minimum loop V
  - Repair action: create apex curve below wire, potentially reverse wire if U not decreasing
  - Suggested fixture: defect mentioning 'anApexV < aMinLoopV'
- **Branch 7** @ line 3210 — *wire_u_direction_below* — **UNCOVERED**
  - What it tests: U parameter direction relationship when apex below
  - Repair action: reverse wire if U not decreasing
  - Suggested fixture: defect mentioning '!isUDecrease', 'aSoleWire.Reverse()'
- **Branch 8** @ line 3217 — *apex_above_wire* — **UNCOVERED**
  - What it tests: apex V parameter is above (greater than) maximum loop V
  - Repair action: create apex curve above wire, potentially reverse wire if U is decreasing
  - Suggested fixture: defect mentioning 'anApexV > aMaxLoopV'
- **Branch 9** @ line 3220 — *wire_u_direction_above* — **UNCOVERED**
  - What it tests: U parameter direction relationship when apex above
  - Repair action: reverse wire if U is decreasing
  - Suggested fixture: defect mentioning 'if (isUDecrease)'
- **Branch 10** @ line 3256 — *context_replace_result* — **UNCOVERED**
  - What it tests: context replacement after apex degeneration fix
  - Repair action: replace original face with new face in context
  - Suggested fixture: defect mentioning 'Context()->Replace(myFace, myResult)'

#### `ShapeFix_Face.FixSmallAreaWire` — lines 2332–2394
(5 branches, 0 covered.)

- **Branch 1** @ line 2333 — *ContextModified* — **UNCOVERED**
  - What it tests: Context is set and has modifications
  - Repair action: Apply context modifications to face
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Apply'
- **Branch 2** @ line 2350 — *InvalidShapeType* — **UNCOVERED**
  - What it tests: Shape is not a wire or has invalid orientation
  - Repair action: Skip non-wire or degenerate shapes
  - Suggested fixture: defect mentioning 'aShape.ShapeType() != TopAbs_WIRE'
- **Branch 3** @ line 2359 — *NullAreaWire* — **UNCOVERED**
  - What it tests: Wire bounds a null/zero area (degenerate)
  - Repair action: Skip wire and increment removal counter
  - Suggested fixture: defect mentioning 'anAnalyzer->CheckSmallArea(aWire)'
- **Branch 4** @ line 2372 — *NoSmallWireDetected* — **UNCOVERED**
  - What it tests: No small/null area wires found
  - Repair action: Return false (no fix applied)
  - Suggested fixture: defect mentioning 'if (nbRemoved <= 0)'
- **Branch 5** @ line 2377 — *AllWiresRemoved* — **UNCOVERED**
  - What it tests: All wires removed, face becomes empty
  - Repair action: Remove face from context (or return false)
  - Suggested fixture: defect mentioning 'if (nbWires <= 0)', 'Context()->Remove'

#### `ShapeFix_Face.FixSplitFace` — lines 2908–3010
(10 branches, 0 covered.)

- **Branch 1** @ line 2912 — *context_applied* — **UNCOVERED**
  - What it tests: whether context is not null
  - Repair action: apply context transformations to face
  - Suggested fixture: defect mentioning 'Context().IsNull()'
- **Branch 2** @ line 2920 — *invalid_wire_in_map* — **UNCOVERED**
  - What it tests: sub-shape has invalid type or orientation
  - Repair action: skip malformed shape
  - Suggested fixture: defect mentioning 'aShape.ShapeType() != TopAbs_WIRE', 'aShape.Orientation()'
- **Branch 3** @ line 2927 — *wire_in_split_map* — **UNCOVERED**
  - What it tests: wire is bound in MapWires (has interior wires to add)
  - Repair action: extract and process interior wires for this wire
  - Suggested fixture: defect mentioning 'MapWires.IsBound(wire)'
- **Branch 4** @ line 2932 — *empty_wire_edge_count* — **UNCOVERED**
  - What it tests: wire has zero edges
  - Repair action: skip empty wire
  - Suggested fixture: defect mentioning 'NbEdges == 0'
- **Branch 5** @ line 2943 — *unclosed_wire* — **UNCOVERED**
  - What it tests: wire first and last vertices are not the same (open wire)
  - Repair action: return false immediately, cannot split open wire
  - Suggested fixture: defect mentioning '!V1.IsSame(V2)'
- **Branch 6** @ line 2961 — *interior_wire_containment* — **UNCOVERED**
  - What it tests: interior wire is inside or outside outer wire
  - Repair action: reverse interior wire if outside; add with correct orientation
  - Suggested fixture: defect mentioning 'staout == TopAbs_IN', 'Reversed()'
- **Branch 7** @ line 2973 — *face_orientation* — **UNCOVERED**
  - What it tests: whether myFwd flag indicates forward orientation
  - Repair action: reverse face orientation if not forward
  - Suggested fixture: defect mentioning 'if (!myFwd)'
- **Branch 8** @ line 2981 — *wire_map_mismatch* — **UNCOVERED**
  - What it tests: count of wires matches count of wires in map (all wires processed)
  - Repair action: return false if counts don't match (incomplete split)
  - Suggested fixture: defect mentioning 'NbWires != NbWiresNew'
- **Branch 9** @ line 2986 — *split_result_multiple_faces* — **UNCOVERED**
  - What it tests: whether split produced multiple faces (length > 1)
  - Repair action: create compound of faces, update context, set result
  - Suggested fixture: defect mentioning 'faces.Length() > 1'
- **Branch 10** @ line 2996 — *context_replacement* — **UNCOVERED**
  - What it tests: context is not null for replacement
  - Repair action: replace original face with compound result
  - Suggested fixture: defect mentioning 'Context()->Replace(myFace, myResult)'

#### `ShapeFix_Face.FixWiresTwoCoincEdges` — lines 2830–2901
(8 branches, 1 covered.)

- **Branch 1** @ line 2831 — *context_applied* — **UNCOVERED**
  - What it tests: whether context is not null (transformation required)
  - Repair action: apply pending context transformations to face before processing
  - Suggested fixture: defect mentioning 'Context().IsNull()'
- **Branch 2** @ line 2846 — *invalid_wire_type* — **UNCOVERED**
  - What it tests: wire has invalid shape type or orientation
  - Repair action: skip malformed wire, do not add to result
  - Suggested fixture: defect mentioning 'ShapeType() != TopAbs_WIRE', 'Orientation() != TopAbs_FORWARD'
- **Branch 3** @ line 2854 — *insufficient_wires* — **UNCOVERED**
  - What it tests: face has fewer than 2 wires (no coincident edges to fix)
  - Repair action: return false, no repair possible
  - Suggested fixture: defect mentioning 'nbWires < 2'
- **Branch 4** @ line 2861 — *invalid_wire_type_in_iteration* — **UNCOVERED**
  - What it tests: wire shape type or orientation check in processing loop
  - Repair action: add malformed wire unchanged to result face
  - Suggested fixture: defect mentioning 'B.Add(face, wi.Value())'
- **Branch 5** @ line 2870 — *two_edge_wire_coincident* — **UNCOVERED**
  - What it tests: wire contains exactly 2 edges that are coincident
  - Repair action: remove coincident two-edge wire from result if edges are identical
  - Suggested fixture: defect mentioning 'sewd->NbEdges() == 2', 'E1 == E2'
- **Branch 6** @ line 2876 — *two_edge_wire_distinct* — **UNCOVERED**
  - What it tests: two-edge wire has distinct edges (not coincident)
  - Repair action: add wire unchanged to result
  - Suggested fixture: defect mentioning '!(E1 == E2)'
- **Branch 7** @ line 2885 — *non_two_edge_wire* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: wire does not have exactly 2 edges
  - Repair action: add wire unchanged to result
- **Branch 8** @ line 2890 — *fix_completed* — **UNCOVERED**
  - What it tests: whether any wires were removed (isFixed flag)
  - Repair action: update face orientation, replace in context, set myFace result
  - Suggested fixture: defect mentioning 'if (isFixed)'

#### `ShapeFix_Face.Init(face)` — lines 209–221
(3 branches, 0 covered.)

- **Branch 1** @ line 211 — *State reset* — **UNCOVERED**
  - What it tests: Clear status before initialization
  - Repair action: Set myStatus to 0 to reset all previous repair status bits
  - Suggested fixture: defect mentioning 'myStatus = 0'
- **Branch 2** @ line 214 — *Null surface check* — **UNCOVERED**
  - What it tests: Check if surface is null (invalid geometry)
  - Repair action: Only create ShapeAnalysis_Surface if surface is not null, else mySurf remains null
  - Suggested fixture: defect mentioning 'if (!aSurface.IsNull())', 'new ShapeAnalysis_Surface'
- **Branch 3** @ line 218 — *Orientation detection* — **UNCOVERED**
  - What it tests: Extract orientation from input face
  - Repair action: Set myFwd based on whether face orientation is not REVERSED
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'myFwd'

#### `ShapeFix_Face.Init(surface)` — lines 192–205
(2 branches, 0 covered.)

- **Branch 1** @ line 194 — *State reset* — **UNCOVERED**
  - What it tests: Clear status before initialization
  - Repair action: Set myStatus to 0 to reset all previous repair status bits
  - Suggested fixture: defect mentioning 'myStatus = 0'
- **Branch 2** @ line 201 — *Orientation handling* — **UNCOVERED**
  - What it tests: Handle forward vs reversed face orientation
  - Repair action: If fwd=false, set face orientation to REVERSED; otherwise keep FORWARD
  - Suggested fixture: defect mentioning 'if (!fwd)', 'TopAbs_REVERSED'

#### `ShapeFix_Face.Perform` — lines 345–769
(27 branches, 1 covered.)

- **Branch 1** @ line 350 — *Wire fixer null check* — COVERED by: in014
  - What it tests: Detect if wire fixer is unavailable
  - Repair action: Return false early if theAdvFixWire is null, preventing segfault
- **Branch 2** @ line 365 — *Wire mode check* — **UNCOVERED**
  - What it tests: Check if wire fixing is enabled (myFixWireMode check)
  - Repair action: Only perform wire fixes if NeedFix(myFixWireMode) is true
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixWireMode))'
- **Branch 3** @ line 387 — *Auto-precision correction* — **UNCOVERED**
  - What it tests: Check if auto precision mode is enabled for small features
  - Repair action: Auto-adjust precision to handle very small edges if myAutoCorrectPrecisionMode set
  - Suggested fixture: defect mentioning 'if (myAutoCorrectPrecisionMode)', 'LeastEdgeSize'
- **Branch 4** @ line 403 — *Shape type filter* — **UNCOVERED**
  - What it tests: Filter non-WIRE shapes in face iteration
  - Repair action: Skip non-wire shapes (other topology types) by adding directly without fixing
  - Suggested fixture: defect mentioning 'if (iter.Value().ShapeType() != TopAbs_WIRE)'
- **Branch 5** @ line 410 — *Empty wire check* — **UNCOVERED**
  - What it tests: Detect wires with zero edges (degenerate)
  - Repair action: Handle degenerate wires: keep if non-manifold, else mark DONE5 and discard
  - Suggested fixture: defect mentioning 'if (theAdvFixWire->NbEdges() == 0)', 'WireData()->NbNonManifoldEdges()'
- **Branch 6** @ line 423 — *Wire perform result* — **UNCOVERED**
  - What it tests: Check if wire fixing succeeded and produced changes
  - Repair action: If Perform() returns true and fixed status is set, replace old wire with fixed one in context
  - Suggested fixture: defect mentioning 'if (theAdvFixWire->Perform(theProgress))', 'StatusSmall', 'StatusConnected'
- **Branch 7** @ line 437 — *Context replacement* — **UNCOVERED**
  - What it tests: Track if context needs updating for fixed wires
  - Repair action: If context exists and wire was fixed, replace old wire with new in context map
  - Suggested fixture: defect mentioning 'if (!Context().IsNull())', 'Context()->Replace(wire, w)'
- **Branch 8** @ line 447 — *Reordered wire tracking* — **UNCOVERED**
  - What it tests: Detect wires reordered without edge fixing
  - Repair action: Track reordered wires separately for context update even if no edges fixed
  - Suggested fixture: defect mentioning 'else if (!wire.IsSame(w))', 'aMapReorderedWires.Bind'
- **Branch 9** @ line 464 — *Face reconstruction* — **UNCOVERED**
  - What it tests: Check if any wire was fixed in first pass
  - Repair action: If wires were fixed, rebuild tmpFace and update context/myFace
  - Suggested fixture: defect mentioning 'if (fixed)', 'myStatus |= ShapeExtend::EncodeStatus(ShapeExtend_DONE1)'
- **Branch 10** @ line 486 — *Periodic degenerated fix* — **UNCOVERED**
  - What it tests: Check if periodic degenerated mode is enabled
  - Repair action: Call FixPeriodicDegenerated() to handle degenerated edges on periodic surfaces
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixPeriodicDegenerated))'
- **Branch 11** @ line 492 — *Missing seam fix* — **UNCOVERED**
  - What it tests: Check if missing seam mode is enabled
  - Repair action: Call FixMissingSeam() and mark DONE3 if seams added to surface
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixMissingSeamMode))', 'FixMissingSeam()'
- **Branch 12** @ line 502 — *Multiple face iteration* — **UNCOVERED**
  - What it tests: Handle faces potentially generated by FixMissingSeam
  - Repair action: Loop through all resulting faces for second-pass wire fixing
  - Suggested fixture: defect mentioning 'TopExp_Explorer exp(myResult, TopAbs_FACE)'
- **Branch 13** @ line 509 — *Second-pass wire mode* — **UNCOVERED**
  - What it tests: Check if wire fixing enabled for second pass
  - Repair action: Perform second pass wire fixes with different mode flags disabled
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixWireMode))', 'FixSmallMode() = false'
- **Branch 14** @ line 541 — *Empty wire in second pass* — **UNCOVERED**
  - What it tests: Detect empty wires in second pass fixing
  - Repair action: Same handling as first pass: keep non-manifold, discard degenerate empty wires
  - Suggested fixture: defect mentioning 'if (theAdvFixWire->NbEdges() == 0)'
- **Branch 15** @ line 554 — *Second-pass wire fixing* — **UNCOVERED**
  - What it tests: Check if second pass wire fixing succeeded
  - Repair action: Apply second-pass fixes (lacking, self-intersection checks) and replace if needed
  - Suggested fixture: defect mentioning 'if (theAdvFixWire->Perform())', 'StatusLacking', 'StatusSelfIntersection'
- **Branch 16** @ line 576 — *Removed segment detection* — **UNCOVERED**
  - What it tests: Check if wire fixing removed any segments
  - Repair action: If segments removed, flag NeedCheckSplitWire to split resulting wire
  - Suggested fixture: defect mentioning 'if (theAdvFixWire->StatusRemovedSegment())', 'NeedCheckSplitWire = true'
- **Branch 17** @ line 583 — *Loop wire fix* — **UNCOVERED**
  - What it tests: Check if loop wire fixing enabled and needed
  - Repair action: Split problematic loop wires into multiple wires, mark DONE7
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixLoopWiresMode) && FixLoopWire(aLoopWires))'
- **Branch 18** @ line 629 — *Split wire check* — **UNCOVERED**
  - What it tests: Detect need to split wires after segment removal
  - Repair action: If segments were removed, split wires and update face
  - Suggested fixture: defect mentioning 'if (NeedCheckSplitWire)', 'SplitWire(tmpFace, wire, aWires)'
- **Branch 19** @ line 650 — *Wire orientation filter* — **UNCOVERED**
  - What it tests: Check wire orientation validity during split
  - Repair action: Skip wires with invalid orientation (not FORWARD or REVERSED)
  - Suggested fixture: defect mentioning 'if (iter.Value().Orientation() != TopAbs_FORWARD', 'TopAbs_REVERSED)'
- **Branch 20** @ line 676 — *Coincident edge wires fix* — **UNCOVERED**
  - What it tests: Check if wires have coincident edge issues
  - Repair action: Call FixWiresTwoCoincEdges() unconditionally, mark DONE7
  - Suggested fixture: defect mentioning 'if (FixWiresTwoCoincEdges())'
- **Branch 21** @ line 680 — *Intersecting wires fix* — **UNCOVERED**
  - What it tests: Check if intersecting wires mode enabled
  - Repair action: If enabled, call FixIntersectingWires() and mark DONE6
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixIntersectingWiresMode))', 'FixIntersectingWires()'
- **Branch 22** @ line 692 — *Orientation fix* — **UNCOVERED**
  - What it tests: Check if orientation mode enabled
  - Repair action: Call FixOrientation() with MapWires and mark DONE2
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixOrientationMode))', 'FixOrientation(MapWires)'
- **Branch 23** @ line 704 — *Natural bound adding* — **UNCOVERED**
  - What it tests: Check if natural bounds need adding
  - Repair action: Call FixAddNaturalBound(); if true, set NeedSplit=false (avoid split after bounds)
  - Suggested fixture: defect mentioning 'if (FixAddNaturalBound())', 'NeedSplit = false'
- **Branch 24** @ line 711 — *Face split condition* — **UNCOVERED**
  - What it tests: Check preconditions for face split (mode enabled, NeedSplit flag, multiple wires)
  - Repair action: If all conditions met, call FixSplitFace() to split face at wire boundaries
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixSplitFaceMode) && NeedSplit && MapWires.Extent() > 1)'
- **Branch 25** @ line 731 — *Small-area wire fix* — **UNCOVERED**
  - What it tests: Check if small-area wire mode enabled
  - Repair action: Call FixSmallAreaWire(isRemoveFace) to remove tiny wires or whole face
  - Suggested fixture: defect mentioning 'if (NeedFix(myFixSmallAreaWireMode, false))', 'FixSmallAreaWire(isRemoveFace)'
- **Branch 26** @ line 743 — *Context reordered wire tracking* — **UNCOVERED**
  - What it tests: Check if context exists and reordered wires map is populated
  - Repair action: Update context with reordered wire replacements if map not empty
  - Suggested fixture: defect mentioning 'if (aMapReorderedWires.Extent())', 'Context()->Replace(aCurW, aFixW)'
- **Branch 27** @ line 764 — *No changes fallback* — **UNCOVERED**
  - What it tests: Check if any repairs were performed (Status DONE check)
  - Repair action: If no changes made, return original face; else use context-applied result
  - Suggested fixture: defect mentioning 'else if (!Status(ShapeExtend_DONE))', 'myResult = aInitFace'

#### `ShapeFix_Face.SplitEdge` — lines 2653–2729
(5 branches, 0 covered.)

- **Branch 1** @ line 2657 — *EdgeSplitFailed* — **UNCOVERED**
  - What it tests: ShapeFix_SplitTool failed to split edge
  - Repair action: Return false (split not performed)
  - Suggested fixture: defect mentioning '!aTool.SplitEdge()'
- **Branch 2** @ line 2663 — *ContextExists* — **UNCOVERED**
  - What it tests: Modification context is available
  - Repair action: Register edge replacement in context
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Replace'
- **Branch 3** @ line 2675 — *EdgeAtWireEnd* — **UNCOVERED**
  - What it tests: Split edge is last edge in wire
  - Repair action: Append second split edge
  - Suggested fixture: defect mentioning 'num == sewd->NbEdges()', 'sewd->Add(newE2)'
- **Branch 4** @ line 2690 — *NoPCurveOnNewEdge* — **UNCOVERED**
  - What it tests: New edge has no 2D curve on surface
  - Repair action: Skip bounding box calculation for edge
  - Suggested fixture: defect mentioning '!sae.PCurve(newE1,', 'continue (implicit)'
- **Branch 5** @ line 2696 — *BSplinePCurveOutOfBounds* — **UNCOVERED**
  - What it tests: BSpline 2D curve has parameter range issues
  - Repair action: Load full curve or bounded range
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom2d_BSplineCurve))'

#### `ShapeFix_Face.isNeedAddNaturalBound` — lines 1123–1161
(5 branches, 0 covered.)

- **Branch 1** @ line 1125 — *FixMode_NotEnabled* — **UNCOVERED**
  - What it tests: AddNaturalBound mode is disabled (not needed)
  - Repair action: Skip natural bound addition
  - Suggested fixture: defect mentioning 'NeedFix(myFixAddNaturalBoundMode)'
- **Branch 2** @ line 1130 — *SurfaceNotPeriodicUV* — **UNCOVERED**
  - What it tests: Surface is not UV-periodic (e.g., open surface)
  - Repair action: Cannot add natural bounds to non-periodic surface
  - Suggested fixture: defect mentioning '!IsSurfaceUVPeriodic(mySurf->Adaptor3d())'
- **Branch 3** @ line 1135 — *OuterBoundExists* — **UNCOVERED**
  - What it tests: Face already has an outer bound (outer wire present)
  - Repair action: Skip adding natural bounds when outer bound exists
  - Suggested fixture: defect mentioning 'ShapeAnalysis::IsOuterBound(myFace)'
- **Branch 4** @ line 1149 — *DegeneratedEdgePresent* — **UNCOVERED**
  - What it tests: Wire contains degenerated edge (collapsed to point)
  - Repair action: Skip natural bounds for degenerated geometry
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(anEdge)'
- **Branch 5** @ line 1153 — *SeamEdgePresent* — **UNCOVERED**
  - What it tests: Wire contains closed/seam edge (periodic boundary)
  - Repair action: Skip natural bounds for seam edge wires
  - Suggested fixture: defect mentioning 'BRep_Tool::IsClosed(anEdge, myFace)'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_FaceConnect.cxx`

1 methods, 37 branches, 27 covered.

#### `ShapeFix_FaceConnect.Build` — lines 113–882
(37 branches, 27 covered.)

- **Branch 1** @ line 139 — *EDGE_BINDING_STATE* — COVERED by: a018, ad086, bo001, bo002, bo003, bo004, bo005, bo006 (+20 more)
  - What it tests: Whether edge is already bound in free edges map (shared vs. first occurrence)
  - Repair action: UnBind existing edge or Bind new edge-face pair
- **Branch 2** @ line 151 — *DEGENERATE_EDGE_FILTER* — COVERED by: ad086, bo002, gp005, gs006, gs028, gs034, sw003, tb013 (+9 more)
  - What it tests: Filter out degenerate edges from processing in problematic faces
  - Repair action: Skip degenerate edges; only process non-degenerate edges in bad-connectivity faces
- **Branch 3** @ line 157 — *FREE_EDGE_LIST_CREATION* — COVERED by: a011, a018, ad038, ad086, lh002, lh005, lh016, ls017 (+4 more)
  - What it tests: First vs. subsequent free edge discovered in a face
  - Repair action: Create new list on first occurrence, append on subsequent
- **Branch 4** @ line 170 — *EDGE_RESULT_MAP_INITIALIZATION* — COVERED by: a018, a019, a029, a074, a101, a102, ad003, ad026 (+41 more)
  - What it tests: First discovery of free edge requiring sewing
  - Repair action: Initialize free and shared edge result maps
- **Branch 5** @ line 242 — *FIRST_FACE_CONNECTIVITY* — COVERED by: gp034
  - What it tests: Whether first face has free edges eligible for sewing
  - Repair action: Process face pair only if first face has free edges
- **Branch 6** @ line 257 — *SECOND_FACE_CONNECTIVITY* — COVERED by: xp012
  - What it tests: Whether second face has free edges eligible for sewing
  - Repair action: Process second face in pair only if it has free edges
- **Branch 7** @ line 264 — *DUPLICATE_PAIR_DETECTION* — **UNCOVERED**
  - What it tests: Whether face pair was already processed in reverse order
  - Repair action: Skip pair to avoid duplicate sewing operations
  - Suggested fixture: defect mentioning 'theProcessed', 'already processed', 'pair skip'
- **Branch 8** @ line 280 — *SELF_CONNECTED_FACE* — COVERED by: gs044
  - What it tests: Whether first and second faces are identical (self-connection anomaly)
  - Repair action: Mark as self-connected (numFacesToSew=1) vs. normal pair (2)
- **Branch 9** @ line 310 — *SEWER_EXCEPTION_HANDLING* — COVERED by: a026, a104, ad086, ad103, ad106, ad113, ad115, gp033 (+51 more)
  - What it tests: Geometry processing failure during sewing operation
  - Repair action: Catch exception, mark sewing failed, skip edge modifications
- **Branch 10** @ line 318 — *SEWER_NULL_SHAPE_RESULT* — **UNCOVERED**
  - What it tests: Sewer produced null shape instead of valid result
  - Repair action: Mark sewing failure when result is null
  - Suggested fixture: defect mentioning 'SewedShape', 'IsNull', 'sewer failure'
- **Branch 11** @ line 323 — *SEWING_SUCCESS_PATH* — **UNCOVERED**
  - What it tests: Overall sewing operation success/failure
  - Repair action: Process modified edges if sewing succeeded; skip if failed
  - Suggested fixture: defect mentioning 'sewing_ok', 'IsModified', 'sewing results'
- **Branch 12** @ line 330 — *EDGE_MODIFICATION_STATE* — COVERED by: sw001, sw002, sw003, sw004
  - What it tests: Whether sewer modified a specific edge
  - Repair action: Extract modified edges; skip unmodified ones
- **Branch 13** @ line 336 — *EDGE_SHARING_DETECTION* — COVERED by: a011, ad038, ad086, bo005, bo022, bo028, gp013, gs025 (+37 more)
  - What it tests: Whether modified edge is first or second occurrence (sharing)
  - Repair action: Move to shared edges if already seen; otherwise bind as new result
- **Branch 14** @ line 347 — *MODIFIED_EDGE_REMOVAL* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+32 more)
  - What it tests: Whether edge was modified during sewing (iterator management)
  - Repair action: Remove from free list if modified; advance iterator if not
- **Branch 15** @ line 381 — *EMPTY_WIRE_GUARD* — COVERED by: sw007, tfa045, tsh023, tsh053, twi001
  - What it tests: Wire contains no new edges after sewing
  - Repair action: Process vertex replacement only if wire is non-empty
- **Branch 16** @ line 410 — *VERTEX_DISTANCE_TRACKING_V1* — COVERED by: ad086, gb004, gp024, gp034, gs014, gs026, gs028, gs037 (+44 more)
  - What it tests: First occurrence of vertex distance or closer vertex to V1
  - Repair action: Initialize and update minimum distance to old vertex 1
- **Branch 17** @ line 418 — *VERTEX_DISTANCE_TRACKING_V2* — COVERED by: ad086, gb004, gp024, gp034, gs014, gs026, gs028, gs037 (+44 more)
  - What it tests: First occurrence of vertex distance or closer vertex to V2
  - Repair action: Initialize and update minimum distance to old vertex 2
- **Branch 18** @ line 424 — *VERTEX_1_REPLACEMENT_NEEDED* — **UNCOVERED**
  - What it tests: First vertex changed during sewing operation
  - Repair action: Record vertex 1 replacement for later topology fix
  - Suggested fixture: defect mentioning 'theOldV1', 'theNewV1', 'IsSame'
- **Branch 19** @ line 426 — *VERTEX_1_REPLACEMENT_LIST_STATE* — COVERED by: a011, a018, a019, a029, a074, a101, a102, ad003 (+45 more)
  - What it tests: First vs. subsequent replacement of vertex 1
  - Repair action: Create new list on first occurrence, append on subsequent
- **Branch 20** @ line 432 — *VERTEX_1_DUPLICATE_PREVENTION* — COVERED by: bo028, hea011, le015, lh034, lh044, ls015, ls016, m051 (+8 more)
  - What it tests: Vertex 1 replacement already in list
  - Repair action: Skip duplicate or append new replacement
- **Branch 21** @ line 442 — *VERTEX_2_REPLACEMENT_NEEDED* — **UNCOVERED**
  - What it tests: Second vertex changed during sewing operation
  - Repair action: Record vertex 2 replacement for later topology fix
  - Suggested fixture: defect mentioning 'theOldV2', 'theNewV2', 'IsSame'
- **Branch 22** @ line 444 — *VERTEX_2_REPLACEMENT_LIST_STATE* — COVERED by: a011, a018, a019, a029, a074, a101, a102, ad003 (+45 more)
  - What it tests: First vs. subsequent replacement of vertex 2
  - Repair action: Create new list on first occurrence, append on subsequent
- **Branch 23** @ line 450 — *VERTEX_2_DUPLICATE_PREVENTION* — COVERED by: bo028, hea011, le015, lh034, lh044, ls015, ls016, m051 (+8 more)
  - What it tests: Vertex 2 replacement already in list
  - Repair action: Skip duplicate or append new replacement
- **Branch 24** @ line 461 — *EDGE_REPLACEMENT_EXECUTION* — COVERED by: ad086, twi038, twi090
  - What it tests: Whether any edges need replacement in topology
  - Repair action: Execute ReShape on edges; otherwise skip entire replacement phase
- **Branch 25** @ line 465 — *RESHAPE_NO_OP_STATUS* — **UNCOVERED**
  - What it tests: ReShape reported operation completed with no changes
  - Repair action: Debug warning; continue with face fixes
  - Suggested fixture: defect mentioning 'ShapeExtend_OK', 'Edges not replaced', 'reshape status'
- **Branch 26** @ line 472 — *RESHAPE_FAILURE_STATUS* — **UNCOVERED**
  - What it tests: ReShape failed on edge replacement
  - Repair action: Debug error; skip face/wire post-processing
  - Suggested fixture: defect mentioning 'ShapeExtend_FAIL1', 'ReShape failed', 'reshape error'
- **Branch 27** @ line 481 — *RESHAPE_SUCCESS_POST_PROCESSING* — COVERED by: bo006, ls031, n009, tb013, tfa062, tsh043, twi038, twi040 (+5 more)
  - What it tests: ReShape succeeded on edges (normal case)
  - Repair action: Perform wire/face orientation fixes and vertex replacement
- **Branch 28** @ line 564 — *FACE_ORIENTATION_CORRECTION* — COVERED by: ad047, ad086, bo024, gs001, p005, pmi083, tfa012, tfa034 (+63 more)
  - What it tests: Face has incorrect orientation needing correction
  - Repair action: Apply orientation fix; update face if corrected
- **Branch 29** @ line 570 — *VERTEX_REPLACEMENT_EXECUTION* — **UNCOVERED**
  - What it tests: Whether any vertices need replacement in topology
  - Repair action: Process vertex replacement maps; otherwise skip
  - Suggested fixture: defect mentioning 'theRepVertices', 'IsEmpty', 'vertex replacement'
- **Branch 30** @ line 576 — *TRANSITIVE_VERTEX_MAPPING* — COVERED by: a001, a005, a007, a014, a018, a023, a028, a032 (+31 more)
  - What it tests: Vertex has prior replacement in mapping (transitive case)
  - Repair action: Map transitively and unbind new mapping, or create new mapping
- **Branch 31** @ line 581 — *TRANSITIVE_VERTEX_UPDATE* — **UNCOVERED**
  - What it tests: Transitive replacement is different from original
  - Repair action: Update mapping and add to replacement list
  - Suggested fixture: defect mentioning 'IsSame', 'transitive update', 'newVertices'
- **Branch 32** @ line 589 — *VERTEX_POSITION_BOUNDS_X* — COVERED by: a095, ad086, bo003, gs002, n021, n042, pmi074, pmi112 (+9 more)
  - What it tests: Vertex X-coordinate bounding box computation
  - Repair action: Track lower/upper X bounds for position averaging
- **Branch 33** @ line 596 — *VERTEX_POSITION_BOUNDS_Y* — COVERED by: a095, ad086, bo003, gs002, n021, n042, pmi074, pmi112 (+9 more)
  - What it tests: Vertex Y-coordinate bounding box computation
  - Repair action: Track lower/upper Y bounds for position averaging
- **Branch 34** @ line 603 — *VERTEX_POSITION_BOUNDS_Z* — COVERED by: a095, ad086, bo003, gs002, n021, n042, pmi074, pmi112 (+9 more)
  - What it tests: Vertex Z-coordinate bounding box computation
  - Repair action: Track lower/upper Z bounds for position averaging
- **Branch 35** @ line 619 — *VERTEX_TOLERANCE_PROPAGATION* — COVERED by: a032, ad045, ad086, bo008, bo030, gb001, gb004, gn009 (+364 more)
  - What it tests: First vs. updated maximum vertex tolerance
  - Repair action: Compute and track maximum tolerance from all contributing vertices
- **Branch 36** @ line 627 — *FINAL_VERTEX_TOLERANCE_CHECK* — **UNCOVERED**
  - What it tests: Final tolerance from target vertex exceeds accumulated max
  - Repair action: Update maximum tolerance for UpdateVertex
  - Suggested fixture: defect mentioning 'theTolerance', 'curtoler', 'final tolerance'
- **Branch 37** @ line 639 — *VERTEX_RESHAPE_FAILURE* — COVERED by: a078, a095, ad045, ad086, ad103, bo001, bo002, bo003 (+181 more)
  - What it tests: ReShape failed on vertex replacement
  - Repair action: Debug error; vertex topology fix failed


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_FixSmallFace.cxx`

10 methods, 95 branches, 29 covered.

#### `ShapeFix_FixSmallFace.ComputeSharedEdgeForStripFace` — lines 422–673
(26 branches, 9 covered.)

- **Branch 1** @ line 442 — *v1_v3_distance_within_tolerance* — **UNCOVERED**
  - What it tests: Distance between V1 and V3 is within tolerance
  - Repair action: merge V1/V3 as first vertex pair of shared edge
  - Suggested fixture: defect mentioning 'if ((dev <= BRep_Tool::Tolerance(V1))', 'theFirstVer = V1'
- **Branch 2** @ line 444 — *v1_v3_vertices_identical* — **UNCOVERED**
  - What it tests: V1 and V3 point to same vertex
  - Repair action: reuse V1 without creating new averaged vertex
  - Suggested fixture: defect mentioning 'if (V1.IsSame(V3))', 'theFirstVer = V1'
- **Branch 3** @ line 450 — *v1_v3_vertices_different* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V1 and V3 are distinct vertices within tolerance
  - Repair action: create new vertex averaging V1 and V3 positions
- **Branch 4** @ line 458 — *v1_orientation_forward* — **UNCOVERED**
  - What it tests: V1 has FORWARD orientation
  - Repair action: replace V1 with FORWARD-oriented averaged vertex
  - Suggested fixture: defect mentioning 'if (V1.Orientation() == TopAbs_FORWARD)', 'Oriented(TopAbs_FORWARD)'
- **Branch 5** @ line 462 — *v1_orientation_not_forward* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V1 has non-FORWARD orientation
  - Repair action: replace V1 with REVERSED-oriented averaged vertex
- **Branch 6** @ line 466 — *v3_orientation_forward* — **UNCOVERED**
  - What it tests: V3 has FORWARD orientation
  - Repair action: replace V3 with FORWARD-oriented averaged vertex
  - Suggested fixture: defect mentioning 'if (V3.Orientation() == TopAbs_FORWARD)', 'Oriented(TopAbs_FORWARD)'
- **Branch 7** @ line 470 — *v3_orientation_not_forward* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V3 has non-FORWARD orientation
  - Repair action: replace V3 with REVERSED-oriented averaged vertex
- **Branch 8** @ line 475 — *v1_equals_v2_or_v3_equals_v4* — **UNCOVERED**
  - What it tests: First or second vertex of either edge is degenerate
  - Repair action: reuse first vertex for second vertex pair
  - Suggested fixture: defect mentioning 'if (V1.IsSame(V2) || V3.IsSame(V4))', 'theSecondVer = theFirstVer'
- **Branch 9** @ line 481 — *v2_not_equals_v4* — **UNCOVERED**
  - What it tests: V2 and V4 are distinct vertices
  - Repair action: create averaged vertex for V2/V4 as second vertex pair
  - Suggested fixture: defect mentioning 'if (!V2.IsSame(V4))', 'theBuilder.UpdateVertex(theSecondVer'
- **Branch 10** @ line 494 — *v2_equals_v4* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V2 and V4 are same vertex
  - Repair action: reuse V2 directly without averaging
- **Branch 11** @ line 499 — *v2_different_from_second_ver* — **UNCOVERED**
  - What it tests: V2 differs from computed theSecondVer
  - Repair action: replace V2 and V4 with averaged vertex
  - Suggested fixture: defect mentioning 'if (!V2.IsSame(theSecondVer))', 'Context()->Replace'
- **Branch 12** @ line 523 — *v1_v4_distance_within_tolerance* — **UNCOVERED**
  - What it tests: Distance between V1 and V4 within tolerance (alt vertex pairing)
  - Repair action: merge V1/V4 as first vertex pair
  - Suggested fixture: defect mentioning 'if ((dev <= BRep_Tool::Tolerance(V1))', 'theFirstVer = V1'
- **Branch 13** @ line 525 — *v1_v4_vertices_identical* — **UNCOVERED**
  - What it tests: V1 and V4 point to same vertex
  - Repair action: reuse V1 without creating new vertex
  - Suggested fixture: defect mentioning 'if (V1.IsSame(V4))', 'theFirstVer = V1'
- **Branch 14** @ line 531 — *v1_v4_vertices_different* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V1 and V4 are distinct vertices within tolerance
  - Repair action: create new vertex averaging V1 and V4
- **Branch 15** @ line 540 — *v1_orientation_forward_alt* — **UNCOVERED**
  - What it tests: V1 has FORWARD orientation in alt pairing
  - Repair action: replace V1 with FORWARD-oriented vertex
  - Suggested fixture: defect mentioning 'if (V1.Orientation() == TopAbs_FORWARD)', 'Oriented(TopAbs_FORWARD)'
- **Branch 16** @ line 544 — *v1_orientation_not_forward_alt* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V1 has non-FORWARD orientation in alt pairing
  - Repair action: replace V1 with REVERSED-oriented vertex
- **Branch 17** @ line 548 — *v4_orientation_forward* — **UNCOVERED**
  - What it tests: V4 has FORWARD orientation
  - Repair action: replace V4 with FORWARD-oriented vertex
  - Suggested fixture: defect mentioning 'if (V4.Orientation() == TopAbs_FORWARD)', 'Oriented(TopAbs_FORWARD)'
- **Branch 18** @ line 552 — *v4_orientation_not_forward* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V4 has non-FORWARD orientation
  - Repair action: replace V4 with REVERSED-oriented vertex
- **Branch 19** @ line 557 — *degenerate_edge_alt_pairing* — **UNCOVERED**
  - What it tests: E1 or E2 degenerates to single vertex in alt pairing
  - Repair action: reuse first vertex for second vertex pair
  - Suggested fixture: defect mentioning 'if (V1.IsSame(V2) || V3.IsSame(V4))', 'theSecondVer = theFirstVer'
- **Branch 20** @ line 564 — *v2_not_equals_v3_alt* — **UNCOVERED**
  - What it tests: V2 and V3 are distinct in alt pairing
  - Repair action: create averaged vertex from V2 and V3
  - Suggested fixture: defect mentioning 'if (!V2.IsSame(V3))', 'theBuilder.UpdateVertex(theSecondVer'
- **Branch 21** @ line 572 — *v2_equals_v3_alt* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: V2 and V3 are same vertex
  - Repair action: reuse V2 without averaging
- **Branch 22** @ line 581 — *v2_different_from_second_ver_alt* — **UNCOVERED**
  - What it tests: V2 differs from computed theSecondVer in alt pairing
  - Repair action: replace V2 and V3 with averaged vertex
  - Suggested fixture: defect mentioning 'if (!V2.IsSame(theSecondVer))', 'Context()->Replace'
- **Branch 23** @ line 601 — *no_vertex_pairing_matches* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Neither V1-V3 nor V1-V4 vertex pairs within tolerance
  - Repair action: return null edge to signal computational failure
- **Branch 24** @ line 609 — *null_vertex_after_computation* — **UNCOVERED**
  - What it tests: Computed vertex is null (theFirstVer or theSecondVer)
  - Repair action: return null edge without creating shared edge
  - Suggested fixture: defect mentioning 'if (theFirstVer.IsNull() || theSecondVer.IsNull())', 'return theNewEdge'
- **Branch 25** @ line 620 — *f1_not_null_and_curve_range_mismatch* — **UNCOVERED**
  - What it tests: F1 exists and E1's 2D curve parameter range differs from 3D
  - Repair action: reparameterize 2D curve to match 3D curve parameter range
  - Suggested fixture: defect mentioning 'if (!F1.IsNull())', 'GeomLib::SameRange'
- **Branch 26** @ line 637 — *tolerance_selection_order* — **UNCOVERED**
  - What it tests: First vertex tolerance less than or equal to second
  - Repair action: use second vertex tolerance as edge max deviation
  - Suggested fixture: defect mentioning 'if ((BRep_Tool::Tolerance(theFirstVer))', 'maxdev ='

#### `ShapeFix_FixSmallFace.FixFace` — lines 921–947
(4 branches, 1 covered.)

- **Branch 1** @ line 923 — *face_empty_copy* — **UNCOVERED**
  - What it tests: Create empty topological copy of input face
  - Repair action: Build reference face for ShapeFix_Face to repair into
  - Suggested fixture: defect mentioning 'EmptyCopied()', 'theFixedFace'
- **Branch 2** @ line 939 — *face_wire_topology* — COVERED by: ad086, tfa004, tfa005, tfa011, tfa019, tfa037, tfa038, tfa039 (+1 more)
  - What it tests: Delegated to ShapeFix_Face analyzer/fixer
  - Repair action: Initialize ShapeFix_Face with input face and perform full face repair
- **Branch 3** @ line 940 — *context_propagation* — **UNCOVERED**
  - What it tests: Context needs to be shared with subordinate fixer
  - Repair action: Set context on ShapeFix_Face before initialization
  - Suggested fixture: defect mentioning 'SetContext(Context())'
- **Branch 4** @ line 945 — *face_repair_completion* — **UNCOVERED**
  - What it tests: ShapeFix_Face::Perform() completes face repair
  - Repair action: Extract and return fixed face from sff
  - Suggested fixture: defect mentioning 'sff->Face()', 'return theFixedFace'

#### `ShapeFix_FixSmallFace.FixShape` — lines 950–974
(6 branches, 0 covered.)

- **Branch 1** @ line 952 — *null_shape* — **UNCOVERED**
  - What it tests: Input myShape is null
  - Repair action: Return empty FixSh shape
  - Suggested fixture: defect mentioning 'myShape.IsNull()', 'return FixSh'
- **Branch 2** @ line 963 — *shape_iteration* — **UNCOVERED**
  - What it tests: Iterate over all faces in myShape
  - Repair action: Process each face with FixFace method
  - Suggested fixture: defect mentioning 'TopExp_Explorer expf(myShape, TopAbs_FACE)'
- **Branch 3** @ line 967 — *context_face_application* — **UNCOVERED**
  - What it tests: Apply accumulated context transformations to face before fixing
  - Repair action: Update face reference from context before repair
  - Suggested fixture: defect mentioning 'Context()->Apply(F)', 'TopoDS::Face(tmpFace)'
- **Branch 4** @ line 969 — *individual_face_repair* — **UNCOVERED**
  - What it tests: Each face is repaired individually via FixFace
  - Repair action: Call FixFace(F) and get newF
  - Suggested fixture: defect mentioning 'FixFace(F)', 'newF'
- **Branch 5** @ line 970 — *face_replacement_in_context* — **UNCOVERED**
  - What it tests: Repaired face needs replacement in context tracking
  - Repair action: Store replacement mapping F->newF in context
  - Suggested fixture: defect mentioning 'Context()->Replace(F, newF)'
- **Branch 6** @ line 972 — *shape_reconstruction* — **UNCOVERED**
  - What it tests: All face replacements completed, rebuild shape from context
  - Repair action: Apply all accumulated context transformations to myShape
  - Suggested fixture: defect mentioning 'Context()->Apply(myShape)', 'FixSh = '

#### `ShapeFix_FixSmallFace.FixSplitFace` — lines 676–707
(4 branches, 1 covered.)

- **Branch 1** @ line 677 — *null_shape* — **UNCOVERED**
  - What it tests: Input shape is null
  - Repair action: Return null shape early
  - Suggested fixture: defect mentioning 'myShape.IsNull()'
- **Branch 2** @ line 681 — *shape_topology_type* — COVERED by: tsh018
  - What it tests: Dispatch by shape type (COMPOUND, COMPSOLID, SOLID, SHELL, FACE)
  - Repair action: Process only shapes that match topology filter
- **Branch 3** @ line 693 — *splitting_required* — **UNCOVERED**
  - What it tests: Face requires splitting (CheckSplittingVertices result)
  - Repair action: Replace original face with compound of split faces
  - Suggested fixture: defect mentioning 'SplitOneFace(F', 'Replace(F', 'CompSplittedFaces'
- **Branch 4** @ line 700 — *completion_status* — **UNCOVERED**
  - What it tests: At least one face was split during pass
  - Repair action: Set DONE3 status, apply context changes to myShape
  - Suggested fixture: defect mentioning 'done == true', 'EncodeStatus', 'Context()->Apply'

#### `ShapeFix_FixSmallFace.FixSpotFace` — lines 81–135
(5 branches, 3 covered.)

- **Branch 1** @ line 87 — *shape_type_mismatch* — COVERED by: tsh018
  - What it tests: Top-level shape is not compound/compsolid/solid/shell/face type
  - Repair action: skip entire repair process if shape type is unsupported
- **Branch 2** @ line 95 — *null_face_after_context_apply* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face becomes null after context apply operation
  - Repair action: skip processing this face and continue to next
- **Branch 3** @ line 99 — *spot_face_not_detected* — COVERED by: tfa046
  - What it tests: Face does not match spot face detection criteria
  - Repair action: skip repair for non-spot faces
- **Branch 4** @ line 111 — *shape_null_after_repair* — **UNCOVERED**
  - What it tests: Shape becomes null after spot face repair (after ReplaceVertices+RemoveFaces)
  - Repair action: return null shape immediately to avoid further processing
  - Suggested fixture: defect mentioning 'if (myShape.IsNull())', 'return myShape'
- **Branch 5** @ line 109 — *repair_completion_flag* — **UNCOVERED**
  - What it tests: At least one spot face was successfully repaired
  - Repair action: call FixShape() to fix wire topology and pcurves
  - Suggested fixture: defect mentioning 'if (done)', 'FixShape()'

#### `ShapeFix_FixSmallFace.FixStripFace` — lines 247–310
(8 branches, 3 covered.)

- **Branch 1** @ line 248 — *shape_null_input* — **UNCOVERED**
  - What it tests: Input shape is null
  - Repair action: return null shape immediately
  - Suggested fixture: defect mentioning 'if (myShape.IsNull())', 'return myShape'
- **Branch 2** @ line 252 — *shape_type_mismatch* — COVERED by: tsh018
  - What it tests: Top-level shape is not compound/compsolid/solid/shell/face
  - Repair action: skip entire repair process
- **Branch 3** @ line 264 — *null_face_after_context_apply* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face becomes null after context apply
  - Repair action: skip processing this face and continue
- **Branch 4** @ line 270 — *strip_face_not_detected* — COVERED by: tfa048
  - What it tests: Face does not match strip face detection criteria
  - Repair action: skip repair for non-strip faces
- **Branch 5** @ line 272 — *strip_edges_replacement_failed* — **UNCOVERED**
  - What it tests: ReplaceInCaseOfStrip returns false (edges not replaced)
  - Repair action: skip RemoveFacesInCaseOfStrip if replacement fails
  - Suggested fixture: defect mentioning 'if (ReplaceInCaseOfStrip', 'RemoveFacesInCaseOfStrip'
- **Branch 6** @ line 288 — *empty_shell_detection* — **UNCOVERED**
  - What it tests: Shell contains no faces after strip removal
  - Repair action: remove empty shell from shape
  - Suggested fixture: defect mentioning '!ex_sh.More()', 'Context()->Remove(Sh)'
- **Branch 7** @ line 298 — *shape_null_after_shell_removal* — **UNCOVERED**
  - What it tests: Shape becomes null after empty shell removal
  - Repair action: return null shape
  - Suggested fixture: defect mentioning 'if (myShape.IsNull())', 'return myShape'
- **Branch 8** @ line 296 — *repair_completion_flag* — **UNCOVERED**
  - What it tests: Strip face repair was completed
  - Repair action: call FixShape() to fix wires and pcurves
  - Suggested fixture: defect mentioning 'if (done)', 'FixShape()'

#### `ShapeFix_FixSmallFace.RemoveFacesInCaseOfSpot` — lines 235–244
(1 branches, 0 covered.)

- **Branch 1** @ line 236 — *spot_edge_removal_loop* — **UNCOVERED**
  - What it tests: Face contains edges that must be removed to delete spot
  - Repair action: iterate and remove all edges in face
  - Suggested fixture: defect mentioning 'TopExp_Explorer iter_vert', 'TopAbs_EDGE'

#### `ShapeFix_FixSmallFace.ReplaceInCaseOfStrip` — lines 316–408
(15 branches, 7 covered.)

- **Branch 1** @ line 317 — *null_edge_input* — COVERED by: in014
  - What it tests: One or both edges E1/E2 are null
  - Repair action: return false immediately to signal replacement failure
- **Branch 2** @ line 331 — *other_face_same_as_strip_face* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Candidate face in shape is same as strip face F
  - Repair action: skip this candidate face and continue searching
- **Branch 3** @ line 330 — *null_face_in_shape_iteration* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face in shape becomes null after context apply
  - Repair action: skip null face and continue iteration
- **Branch 4** @ line 338 — *edge_matches_e1* — **UNCOVERED**
  - What it tests: Found edge in other face that matches strip edge E1
  - Repair action: record adjacent face F1 as neighbor sharing E1
  - Suggested fixture: defect mentioning 'tempE.IsSame(E1)', 'F1 = tempF'
- **Branch 5** @ line 342 — *edge_matches_e2* — **UNCOVERED**
  - What it tests: Found edge in other face that matches strip edge E2
  - Repair action: record adjacent face F2 as neighbor sharing E2
  - Suggested fixture: defect mentioning 'tempE.IsSame(E2)', 'F2 = tempF'
- **Branch 6** @ line 354 — *no_adjacent_faces_found* — **UNCOVERED**
  - What it tests: Neither E1 nor E2 found in any other face
  - Repair action: return true without creating shared edge (strip face has no neighbors)
  - Suggested fixture: defect mentioning 'if (F1.IsNull() && F2.IsNull())', 'return true'
- **Branch 7** @ line 360 — *only_e2_has_neighbor* — **UNCOVERED**
  - What it tests: Only E2 found in another face (F1 is null, F2 is not)
  - Repair action: swap edge assignments so E1tmp has neighbor F1
  - Suggested fixture: defect mentioning 'if (F1.IsNull())', 'E1tmp = E2'
- **Branch 8** @ line 368 — *shared_edge_computation_failed* — COVERED by: in014
  - What it tests: ComputeSharedEdgeForStripFace returns null edge
  - Repair action: return false to signal edge replacement failure
- **Branch 9** @ line 372 — *e1_orientation_reversed* — **UNCOVERED**
  - What it tests: E1 has REVERSED orientation
  - Repair action: replace E1 with REVERSED shared edge
  - Suggested fixture: defect mentioning 'if (E1.Orientation() == TopAbs_REVERSED)', 'TopAbs_REVERSED'
- **Branch 10** @ line 375 — *face_orientation_match* — **UNCOVERED**
  - What it tests: F and F1 have same orientation when E1 is reversed
  - Repair action: replace E2 with non-reversed shared edge
  - Suggested fixture: defect mentioning 'if (F.Orientation() == F1.Orientation())', 'theSharedEdge'
- **Branch 11** @ line 379 — *face_orientation_mismatch* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: F and F1 have opposite orientations when E1 is reversed
  - Repair action: replace E2 with REVERSED shared edge
- **Branch 12** @ line 384 — *e1_orientation_forward* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: E1 has FORWARD (non-reversed) orientation
  - Repair action: replace E1 with non-reversed shared edge
- **Branch 13** @ line 387 — *face_orientation_match_forward* — **UNCOVERED**
  - What it tests: F and F1 have same orientation when E1 is forward
  - Repair action: replace E2 with REVERSED shared edge
  - Suggested fixture: defect mentioning 'if (F.Orientation() == F1.Orientation())', 'TopAbs_REVERSED'
- **Branch 14** @ line 391 — *face_orientation_mismatch_forward* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: F and F1 have opposite orientations when E1 is forward
  - Repair action: replace E2 with non-reversed shared edge
- **Branch 15** @ line 401 — *remove_short_edges* — **UNCOVERED**
  - What it tests: Edge in face is neither E1tmp nor E2tmp
  - Repair action: remove short edges not involved in replacement
  - Suggested fixture: defect mentioning '!shortedge.IsSame(E1tmp)', 'Context()->Remove(shortedge)'

#### `ShapeFix_FixSmallFace.ReplaceVerticesInCaseOfSpot` — lines 138–232
(8 branches, 1 covered.)

- **Branch 1** @ line 153 — *wire_iteration_empty* — **UNCOVERED**
  - What it tests: Face has no wire subshapes
  - Repair action: skip vertex replacement and return true (tolerate faceless faces)
  - Suggested fixture: defect mentioning 'TopoDS_Iterator itw', '!isWir'
- **Branch 2** @ line 155 — *non_wire_subshape* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face contains non-wire topological entities
  - Repair action: skip non-wire sub-entities and continue iteration
- **Branch 3** @ line 160 — *null_wire_in_face* — **UNCOVERED**
  - What it tests: Wire shape is null despite iterator returning it
  - Repair action: skip null wire and record that face has at least one valid wire
  - Suggested fixture: defect mentioning 'w1.IsNull()', 'isWir = true'
- **Branch 4** @ line 166 — *no_valid_wires_in_face* — **UNCOVERED**
  - What it tests: Face iteration completed without finding any valid wire
  - Repair action: return true immediately (no vertex replacement possible)
  - Suggested fixture: defect mentioning 'if (!isWir)', 'return true'
- **Branch 5** @ line 175 — *vertex_tolerance_tracking* — **UNCOVERED**
  - What it tests: Current vertex has higher tolerance than accumulated max
  - Repair action: update max tolerance for new shared vertex deviation calc
  - Suggested fixture: defect mentioning 'theMaxTol <=', 'theMaxTol ='
- **Branch 6** @ line 189 — *single_vertex_face* — **UNCOVERED**
  - What it tests: Face contains only one distinct vertex
  - Repair action: skip averaging calculation (thePosition already initialized to vertex)
  - Suggested fixture: defect mentioning 'if (theNbPos > 1)', 'thePosition /='
- **Branch 7** @ line 217 — *vertex_orientation_forward* — **UNCOVERED**
  - What it tests: Current vertex has FORWARD orientation
  - Repair action: create FORWARD-oriented copy of shared vertex
  - Suggested fixture: defect mentioning 'TopAbs_FORWARD', 'tmpVertexFwd'
- **Branch 8** @ line 223 — *vertex_orientation_reversed* — **UNCOVERED**
  - What it tests: Current vertex has non-FORWARD orientation
  - Repair action: create REVERSED-oriented copy of shared vertex
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'tmpVertexRev'

#### `ShapeFix_FixSmallFace.SplitOneFace` — lines 710–918
(18 branches, 4 covered.)

- **Branch 1** @ line 720 — *splitting_vertices_absent* — COVERED by: m015, tfa010
  - What it tests: Face has CheckSplittingVertices result == 0
  - Repair action: Return false, no splitting needed
- **Branch 2** @ line 724 — *vertex_container_null* — **UNCOVERED**
  - What it tests: theAllVert compound is null after split analysis
  - Repair action: Return false early
  - Suggested fixture: defect mentioning 'theAllVert.IsNull()'
- **Branch 3** @ line 732 — *vertex_extraction_failed* — **UNCOVERED**
  - What it tests: First vertex cannot be extracted from theAllVert
  - Repair action: Return false
  - Suggested fixture: defect mentioning 'V.IsNull()'
- **Branch 4** @ line 752 — *edge_no_3d_curve* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge has no 3D curve (C3D is null)
  - Repair action: Skip edge, continue to next
- **Branch 5** @ line 756 — *vertex_on_edge_endpoint* — **UNCOVERED**
  - What it tests: Splitting vertex V is endpoint of current edge E
  - Repair action: Skip edge, continue searching
  - Suggested fixture: defect mentioning 'V.IsSame(V1)', 'V.IsSame(V2)'
- **Branch 6** @ line 763 — *projection_distance_zero* — **UNCOVERED**
  - What it tests: Projection distance to edge is exactly zero (numerical precision)
  - Repair action: Skip projection, continue
  - Suggested fixture: defect mentioning 'dist == 0', 'Projection on same curve'
- **Branch 7** @ line 767 — *vertex_near_edge* — COVERED by: twi084, twi085, twi086
  - What it tests: Vertex projects onto edge within tolerance
  - Repair action: Create new vertex at projection, split edge at parameter
- **Branch 8** @ line 777 — *edge_orientation_forward* — **UNCOVERED**
  - What it tests: Original edge has FORWARD orientation
  - Repair action: Build split edges with V1->new->V2 sequence
  - Suggested fixture: defect mentioning 'V1.Orientation() == TopAbs_FORWARD'
- **Branch 9** @ line 784 — *edge_orientation_reversed* — COVERED by: ad035, ad086, ad114, ad119, bo006, gn033, gp018, gs009 (+64 more)
  - What it tests: Original edge has REVERSED orientation
  - Repair action: Build split edges with V2->new->V1 sequence
- **Branch 10** @ line 810 — *split_edge_creation_failed* — **UNCOVERED**
  - What it tests: No suitable projection found (theNewVertex remains null)
  - Repair action: Return false, splitting incomplete
  - Suggested fixture: defect mentioning 'theNewVertex.IsNull()'
- **Branch 11** @ line 834 — *multiple_wires_on_face* — **UNCOVERED**
  - What it tests: Face has more than one wire (hole detected)
  - Repair action: Return false, cannot handle faces with holes
  - Suggested fixture: defect mentioning 'itw.More()', 'more than one wire'
- **Branch 12** @ line 875 — *wire_split_at_original_vertex* — **UNCOVERED**
  - What it tests: Control vertex matches original splitting vertex V
  - Repair action: Add split edge (FORWARD), swap wire buffers w1/w2
  - Suggested fixture: defect mentioning 'thecontrol.IsSame(V)', 'theSplitEdge', 'wtemp = w1'
- **Branch 13** @ line 882 — *wire_split_at_new_vertex* — **UNCOVERED**
  - What it tests: Control vertex matches newly created vertex
  - Repair action: Add split edge (REVERSED), swap wire buffers
  - Suggested fixture: defect mentioning 'thecontrol.IsSame(theNewVertex)'
- **Branch 14** @ line 890 — *wire_buffer_invalid* — **UNCOVERED**
  - What it tests: Either w1 or w2 is null after splitting
  - Repair action: Return false, wire construction incomplete
  - Suggested fixture: defect mentioning 'w1.IsNull()', 'w2.IsNull()'
- **Branch 15** @ line 906 — *recursive_split_f1_required* — **UNCOVERED**
  - What it tests: First face F1 has further splitting needed
  - Repair action: Recursively call SplitOneFace(F1)
  - Suggested fixture: defect mentioning 'SplitOneFace(F1'
- **Branch 16** @ line 910 — *recursive_split_f2_required* — **UNCOVERED**
  - What it tests: Second face F2 has further splitting needed
  - Repair action: Recursively call SplitOneFace(F2)
  - Suggested fixture: defect mentioning 'SplitOneFace(F2'
- **Branch 17** @ line 906 — *f1_no_further_split* — **UNCOVERED**
  - What it tests: F1 splitting recursion returns false
  - Repair action: Add F1 directly to theSplittedFaces compound
  - Suggested fixture: defect mentioning '!SplitOneFace(F1)', 'Add(theSplittedFaces, F1)'
- **Branch 18** @ line 910 — *f2_no_further_split* — **UNCOVERED**
  - What it tests: F2 splitting recursion returns false
  - Repair action: Add F2 directly to theSplittedFaces compound
  - Suggested fixture: defect mentioning '!SplitOneFace(F2)', 'Add(theSplittedFaces, F2)'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_IntersectionTool.cxx`

9 methods, 170 branches, 38 covered.

#### `ShapeFix_IntersectionTool.FixIntersectingWires` — lines 1836–2530
(51 branches, 5 covered.)

- **Branch 1** @ line 1838 — *NULL_OR_EMPTY_INPUT* — **UNCOVERED**
  - What it tests: Null face or null context
  - Repair action: REJECT_OPERATION
  - Suggested fixture: defect mentioning 'myContext.IsNull()', 'face.IsNull()'
- **Branch 2** @ line 1847 — *NON_WIRE_SHAPE_IN_FACE* — **UNCOVERED**
  - What it tests: Non-WIRE shapes or improper orientation in face boundary
  - Repair action: PRESERVE_NON_WIRE_SHAPES
  - Suggested fixture: defect mentioning 'ShapeType() != TopAbs_WIRE', 'Orientation() != TopAbs_FORWARD'
- **Branch 3** @ line 1857 — *INSUFFICIENT_WIRES* — **UNCOVERED**
  - What it tests: Fewer than 2 wires in face (no intersections possible)
  - Repair action: SKIP_INTERSECTION_FIX
  - Suggested fixture: defect mentioning 'SeqWir.Length() < 2'
- **Branch 4** @ line 1900 — *DISJOINT_WIRE_BBOXES* — **UNCOVERED**
  - What it tests: Wire bounding boxes do not overlap in 2D parameter space
  - Repair action: SKIP_WIRE_PAIR
  - Suggested fixture: defect mentioning 'aBox1.IsOut(aBox2)'
- **Branch 5** @ line 1917 — *SAME_EDGE_BOTH_WIRES* — **UNCOVERED**
  - What it tests: Edge appears in both wires (shared edge, not intersection)
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning 'edge1.IsSame(edge2)'
- **Branch 6** @ line 1920 — *DEGENERATE_EDGE* — **UNCOVERED**
  - What it tests: One or both edges are degenerate (zero length)
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(edge1)', 'BRep_Tool::Degenerated(edge2)'
- **Branch 7** @ line 1923 — *MISSING_EDGE_BBOX* — **UNCOVERED**
  - What it tests: Edge bounding box not computed (data structure error)
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning '!boxes1.IsBound(edge1)', '!boxes2.IsBound(edge2)'
- **Branch 8** @ line 1928 — *DISJOINT_EDGE_BBOXES* — **UNCOVERED**
  - What it tests: 2D edge bounding boxes do not overlap
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning 'B1.IsOut(B2)'
- **Branch 9** @ line 1933 — *MISSING_PCURVE* — **UNCOVERED**
  - What it tests: Cannot extract 2D parametric curve from edge on face
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning '!sae.PCurve(edge1, face, Crv1'
- **Branch 10** @ line 1936 — *MISSING_PCURVE_SECOND* — **UNCOVERED**
  - What it tests: Cannot extract 2D curve for second edge
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning '!sae.PCurve(edge2, face, Crv2'
- **Branch 11** @ line 1945 — *INTERSECTION_COMPUTATION_FAILED* — **UNCOVERED**
  - What it tests: 2D curve intersection algorithm failed to complete
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning '!Inter.IsDone()'
- **Branch 12** @ line 1949 — *MULTIPLE_INTERSECTION_POINTS* — **UNCOVERED**
  - What it tests: Found 2 or more isolated intersection points (high complexity)
  - Repair action: SKIP_EDGE_PAIR
  - Suggested fixture: defect mentioning 'Inter.NbPoints() > 0 && Inter.NbPoints() < 3'
- **Branch 13** @ line 1953 — *POINT_INTERIOR_BOTH_EDGES* — **UNCOVERED**
  - What it tests: Intersection point lies in interior of both edges (true cross-intersection)
  - Repair action: CREATE_VERTEX_AND_SPLIT_BOTH
  - Suggested fixture: defect mentioning 'IntRes2d_Middle && Tr2.PositionOnCurve() == IntRes2d_Middle'
- **Branch 14** @ line 1981 — *POINT_INTERIOR_EDGE1_ENDPOINT_EDGE2* — **UNCOVERED**
  - What it tests: Edge1 intersects at interior, Edge2 endpoint is intersection point
  - Repair action: FIND_VERTEX_ON_EDGE2_AND_SPLIT_EDGE1
  - Suggested fixture: defect mentioning 'IntRes2d_Middle && Tr2.PositionOnCurve() != IntRes2d_Middle'
- **Branch 15** @ line 1998 — *POINT_ENDPOINT_EDGE1_INTERIOR_EDGE2* — **UNCOVERED**
  - What it tests: Edge1 endpoint intersects, Edge2 interior is intersection point
  - Repair action: FIND_VERTEX_ON_EDGE1_AND_SPLIT_EDGE2
  - Suggested fixture: defect mentioning 'Tr1.PositionOnCurve() != IntRes2d_Middle && Tr2.PositionOnCurve() == IntRes2d_Middle'
- **Branch 16** @ line 2015 — *POINT_BOTH_ENDPOINTS* — **UNCOVERED**
  - What it tests: Both edges have endpoint at intersection (existing vertex nearby)
  - Repair action: UNION_VERTICES
  - Suggested fixture: defect mentioning 'Tr1.PositionOnCurve() != IntRes2d_Middle && Tr2.PositionOnCurve() != IntRes2d_Middle'
- **Branch 17** @ line 2025 — *EDGE_SEGMENT_OVERLAP* — **UNCOVERED**
  - What it tests: Edges overlap along a curve segment (collinear portion)
  - Repair action: ANALYZE_SEGMENT_OVERLAP
  - Suggested fixture: defect mentioning 'Inter.NbSegments() == 1'
- **Branch 18** @ line 2027 — *SEGMENT_WITHOUT_ENDPOINTS* — **UNCOVERED**
  - What it tests: Intersection segment exists but lacks defined start or end
  - Repair action: SKIP_SEGMENT
  - Suggested fixture: defect mentioning 'HasFirstPoint()', 'HasLastPoint()'
- **Branch 19** @ line 2053 — *SEGMENT_ENDPOINT_NEAR_EDGE1_START* — **UNCOVERED**
  - What it tests: Segment endpoints close to Edge1 start vertex (parametric proximity check)
  - Repair action: MARK_EDGE1_NEEDS_CUT
  - Suggested fixture: defect mentioning 'maxdist < MaxTolVert', 'pdist < std::abs(b1 - a1) * 0.01', 'edge1.Orientation()'
- **Branch 20** @ line 2067 — *SEGMENT_ENDPOINT_NEAR_EDGE1_END* — **UNCOVERED**
  - What it tests: Segment endpoints close to Edge1 end vertex
  - Repair action: CONDITIONAL_UPDATE_EDGE1_VERTEX
  - Suggested fixture: defect mentioning '(IsModified1 && maxdist < newtol) || !IsModified1'
- **Branch 21** @ line 2080 — *EDGE1_OVERLAP_TRIM_NEEDED* — **UNCOVERED**
  - What it tests: Edge1 contains segment and requires trimming at one end
  - Repair action: COMPUTE_TRIM_POINT_AND_CUT_EDGE1
  - Suggested fixture: defect mentioning 'IsModified1', 'CutEdge(edge1'
- **Branch 22** @ line 2085 — *CUT_POINT_SELECTION_EDGE1* — **UNCOVERED**
  - What it tests: Determine which edge1 endpoint is closer to segment (start or end parameter)
  - Repair action: SELECT_ENDPOINT_AND_TRIM_POINT
  - Suggested fixture: defect mentioning 'dista > distb', 'pend = a1', 'pend = b1'
- **Branch 23** @ line 2091 — *SEGMENT_TRIM_POINT_SELECTION* — **UNCOVERED**
  - What it tests: Choose which segment endpoint to use as cut point on Edge1
  - Repair action: SELECT_FIRST_OR_SECOND_SEGMENT_POINT
  - Suggested fixture: defect mentioning 'std::abs(pend - p11) > std::abs(pend - p12)', 'cut = p12', 'cut = p11'
- **Branch 24** @ line 2098 — *CUT_EDGE_OPERATION_FAILED* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: CutEdge operation returned false (geometric or topological error)
  - Repair action: ROLLBACK_EDGE1_MODIFICATION
- **Branch 25** @ line 2102 — *VERTEX_TOLERANCE_UPDATE_NEEDED* — **UNCOVERED**
  - What it tests: New tolerance for vertex exceeds current tolerance
  - Repair action: UPGRADE_VERTEX_TOLERANCE
  - Suggested fixture: defect mentioning 'newtol > BRep_Tool::Tolerance(NewV)', 'UpdateVertex'
- **Branch 26** @ line 2115 — *SEGMENT_ENDPOINT_NEAR_EDGE2_START* — **UNCOVERED**
  - What it tests: Segment endpoints close to Edge2 start vertex
  - Repair action: MARK_EDGE2_NEEDS_CUT
  - Suggested fixture: defect mentioning 'edge2.Orientation()', 'b2 - p21', 'b2 - p22'
- **Branch 27** @ line 2129 — *SEGMENT_ENDPOINT_NEAR_EDGE2_END* — **UNCOVERED**
  - What it tests: Segment endpoints close to Edge2 end vertex
  - Repair action: CONDITIONAL_UPDATE_EDGE2_VERTEX
  - Suggested fixture: defect mentioning 'IsModified2'
- **Branch 28** @ line 2142 — *EDGE2_OVERLAP_TRIM_NEEDED* — **UNCOVERED**
  - What it tests: Edge2 contains segment and requires trimming
  - Repair action: CUT_EDGE2_AND_UPDATE_TOLERANCE
  - Suggested fixture: defect mentioning 'IsModified2', 'CutEdge(edge2'
- **Branch 29** @ line 2169 — *EITHER_EDGE_WAS_TRIMMED* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: At least one edge (Edge1 or Edge2) was cut by segment overlap
  - Repair action: REPROCESS_SAME_EDGE_PAIR
- **Branch 30** @ line 2178 — *LARGE_SEGMENT_OVERLAP* — **UNCOVERED**
  - What it tests: Segment spans more than 50% of edge parameter range (significant collinear portion)
  - Repair action: SPLIT_INTO_THREE_EDGES_WITH_SEGMENT_MIDDLE
  - Suggested fixture: defect mentioning 'std::abs(p12 - p11) > std::abs(b1 - a1) / 2', 'std::abs(p22 - p21) > std::abs(b2 - a2) / 2'
- **Branch 31** @ line 2190 — *LARGE_SEGMENT_TOLERANCE_EXCEEDS_LIMIT* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: New vertex tolerance for large segment exceeds global max (safety check)
  - Repair action: ABORT_LARGE_SEGMENT_SPLIT
- **Branch 32** @ line 2200 — *SEGMENT_START_MATCHES_EDGE1_VERTEX* — **UNCOVERED**
  - What it tests: Segment start point matches an Edge1 endpoint (reuse existing vertex)
  - Repair action: REUSE_EDGE1_VERTEX_FOR_SEGMENT_START
  - Suggested fixture: defect mentioning 'P01.Distance(PV1) <', 'NewV1 = V1', 'akey1++'
- **Branch 33** @ line 2207 — *SEGMENT_START_MATCHES_EDGE1_OTHER_END* — **UNCOVERED**
  - What it tests: Segment start matches other end of Edge1
  - Repair action: REUSE_ALTERNATE_EDGE1_VERTEX
  - Suggested fixture: defect mentioning 'P01.Distance(PV2) <', 'NewV1 = V2'
- **Branch 34** @ line 2215 — *SEGMENT_END_MATCHES_EDGE1_VERTEX* — **UNCOVERED**
  - What it tests: Segment end point matches an Edge1 endpoint
  - Repair action: REUSE_EDGE1_VERTEX_FOR_SEGMENT_END
  - Suggested fixture: defect mentioning 'P02.Distance(PV1) <', 'NewV2 = V1', 'akey2++'
- **Branch 35** @ line 2222 — *SEGMENT_END_MATCHES_EDGE1_OTHER_END* — **UNCOVERED**
  - What it tests: Segment end matches other end of Edge1
  - Repair action: REUSE_EDGE1_END_FOR_SEGMENT_END
  - Suggested fixture: defect mentioning 'P02.Distance(PV2) <', 'NewV2 = V2'
- **Branch 36** @ line 2229 — *SEGMENT_MATCHES_BOTH_EDGE1_ENDPOINTS* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Segment endpoints match both ends of Edge1 (Edge1 spans segment)
  - Repair action: ABORT_SPLIT_AMBIGUOUS_GEOMETRY
- **Branch 37** @ line 2240 — *SPLIT_EDGE1_AT_SEGMENT_START* — **UNCOVERED**
  - What it tests: Segment start needs new vertex (akey1==0) and segment end matches (akey2>0)
  - Repair action: SPLIT_EDGE1_ONCE_AT_FIRST_PARAM
  - Suggested fixture: defect mentioning 'akey1 == 0 && akey2 > 0', 'SplitEdge1(sewd1, face, num1, p11'
- **Branch 38** @ line 2247 — *SPLIT_EDGE1_AT_SEGMENT_END* — **UNCOVERED**
  - What it tests: Segment start matches (akey1>0) and end needs new vertex (akey2==0)
  - Repair action: SPLIT_EDGE1_ONCE_AT_SECOND_PARAM
  - Suggested fixture: defect mentioning 'akey1 > 0 && akey2 == 0', 'SplitEdge1(sewd1, face, num1, p12'
- **Branch 39** @ line 2253 — *SPLIT_EDGE1_AT_BOTH_SEGMENT_ENDPOINTS* — **UNCOVERED**
  - What it tests: Both segment endpoints need new vertices on Edge1 (create 3-part edge)
  - Repair action: SPLIT_EDGE1_TWICE_AND_EXTRACT_MIDDLE
  - Suggested fixture: defect mentioning 'akey1 == 0 && akey2 == 0', 'SplitEdge1(sewd1, face, num1, p11', 'SplitEdge1(sewd1, face, num1split2, p12'
- **Branch 40** @ line 2261 — *SECOND_SEGMENT_POINT_OUTSIDE_SPLIT_EDGE_RANGE* — **UNCOVERED**
  - What it tests: After first split, second point falls outside new edge parameter range (must split next edge)
  - Repair action: ADVANCE_TO_NEXT_EDGE_FOR_SECOND_SPLIT
  - Suggested fixture: defect mentioning '(a - p12) * (b - p12) > 0', 'num1split2++'
- **Branch 41** @ line 2275 — *EDGE2_VERTEX_REPLACEMENT_START* — **UNCOVERED**
  - What it tests: Segment start point matches Edge2 first vertex (replace with shared vertex)
  - Repair action: REPLACE_EDGE2_START_VERTEX_WITH_SHARED
  - Suggested fixture: defect mentioning 'P01.Distance(PV12) < tolV1', 'CopyReplaceVertices(edge2, NewV1, V22)'
- **Branch 42** @ line 2285 — *EDGE2_VERTEX_REPLACEMENT_END* — **UNCOVERED**
  - What it tests: Segment start point matches Edge2 last vertex
  - Repair action: REPLACE_EDGE2_END_VERTEX_WITH_SHARED
  - Suggested fixture: defect mentioning 'P01.Distance(PV22) < tolV1', 'CopyReplaceVertices(edge2, V12, NewV1)'
- **Branch 43** @ line 2295 — *EDGE2_VERTEX_REPLACEMENT_END_AT_SEGMENT_END_START* — **UNCOVERED**
  - What it tests: Segment end point matches Edge2 first vertex
  - Repair action: REPLACE_EDGE2_START_WITH_SEGMENT_END_VERTEX
  - Suggested fixture: defect mentioning 'P02.Distance(PV12) < tolV2', 'NewV2'
- **Branch 44** @ line 2305 — *EDGE2_VERTEX_REPLACEMENT_END_AT_SEGMENT_END_END* — **UNCOVERED**
  - What it tests: Segment end point matches Edge2 last vertex
  - Repair action: REPLACE_EDGE2_END_WITH_SEGMENT_END_VERTEX
  - Suggested fixture: defect mentioning 'P02.Distance(PV22) < tolV2', 'CopyReplaceVertices(edge2, V12, NewV2)'
- **Branch 45** @ line 2316 — *SPLIT_EDGE2_BASED_ON_ENDPOINT_MATCHES* — **UNCOVERED**
  - What it tests: Determine split pattern for Edge2 based on endpoint matching flags (akey1, akey2)
  - Repair action: EXECUTE_APPROPRIATE_EDGE2_SPLIT
  - Suggested fixture: defect mentioning 'akey1 == 0 && akey2 > 0', 'akey1 > 0 && akey2 == 0', 'akey1 == 0 && akey2 == 0'
- **Branch 46** @ line 2349 — *SEGMENT_EDGE_ORIENTATION_MISMATCH* — **UNCOVERED**
  - What it tests: Middle segment edge from Edge1 and extracted Edge2 segment have opposite orientation
  - Repair action: REVERSE_EXTRACTED_SEGMENT_EDGE
  - Suggested fixture: defect mentioning '!sae.FirstVertex(SegE).IsSame(sae.FirstVertex(tmpE))', 'SegE.Reverse()'
- **Branch 47** @ line 2357 — *SMALL_SEGMENT_OVERLAP* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Segment spans less than 50% of edge parameter range (small collinear portion)
  - Repair action: SPLIT_BOTH_EDGES_AT_SEGMENT_MIDPOINT
- **Branch 48** @ line 2372 — *SPLIT_EDGE2_SMALL_SEGMENT* — **UNCOVERED**
  - What it tests: Create split on Edge2 using both segment endpoints and shared vertex
  - Repair action: SPLIT_EDGE2_WITH_ENDPOINTS
  - Suggested fixture: defect mentioning 'SplitEdge2(sewd2, face, num2, p21, p22'
- **Branch 49** @ line 2376 — *SPLIT_EDGE1_SMALL_SEGMENT* — **UNCOVERED**
  - What it tests: Create split on Edge1 using both segment endpoints and shared vertex
  - Repair action: SPLIT_EDGE1_WITH_ENDPOINTS
  - Suggested fixture: defect mentioning 'SplitEdge2(sewd1, face, num1, p11, p12'
- **Branch 50** @ line 2388 — *MODIFICATION_MADE_TO_EITHER_WIRE* — **UNCOVERED**
  - What it tests: Any modification was made to either wire (split, vertex update, or vertex union)
  - Repair action: RECOMPUTE_WIRE_BOXES_AND_MARK_MODIFIED
  - Suggested fixture: defect mentioning 'hasModifWire', 'isDone = true', 'CreateBoxes2d'
- **Branch 51** @ line 2408 — *FINAL_FACE_WAS_MODIFIED* — **UNCOVERED**
  - What it tests: Overall operation made changes to face topology
  - Repair action: RECONSTRUCT_FACE_WITH_MODIFIED_WIRES
  - Suggested fixture: defect mentioning 'isDone', 'emptyCopied', 'EmptyCopied()'

#### `ShapeFix_IntersectionTool.FixSelfIntersectWire` — lines 1034–1832
(43 branches, 29 covered.)

- **Branch 1** @ line 1035 — *Null context or null face* — COVERED by: a002, a003, a013, a014, a016, a017, a018, a019 (+801 more)
  - What it tests: Early exit guard for invalid input (null context or face)
  - Repair action: Return false; skip all wire processing
- **Branch 2** @ line 1065 — *Split limit exceeded (NbSplit >= 30)* — COVERED by: a082, a095, ad027, ad064, ad086, ad099, bo006, fi006 (+32 more)
  - What it tests: Prevent infinite/excessive splitting loops
  - Repair action: Stop processing further edge pairs
- **Branch 3** @ line 1077 — *Edge is self-referential (edge1.IsSame(edge2))* — COVERED by: a001, a004, a011, a012, a014, a019, a020, a022 (+290 more)
  - What it tests: Same edge cannot intersect itself at different points
  - Repair action: Skip this edge pair
- **Branch 4** @ line 1081 — *Degenerate edge (edge1 or edge2 is degenerate)* — COVERED by: a003, a004, a012, a019, a020, a023, a034, a065 (+294 more)
  - What it tests: Degenerate edges cannot participate in meaningful intersection repair
  - Repair action: Skip degenerate edges
- **Branch 5** @ line 1085 — *Missing bounding box (edge not in 2D box cache)* — COVERED by: a004, a006, a010, a012, a013, a017, a019, a020 (+413 more)
  - What it tests: Cannot determine intersection without bounding box
  - Repair action: Skip if no bounding box available
- **Branch 6** @ line 1091 — *Bounding boxes disjoint (B1.IsOut(B2))* — COVERED by: a004, a012, a019, a020, a023, a034, a065, a068 (+183 more)
  - What it tests: 2D bounding boxes do not overlap; no intersection possible
  - Repair action: Skip pair; continue to next
- **Branch 7** @ line 1096 — *Cannot extract pcurve from edge1* — COVERED by: a024, a104, ad027, ad032, ad043, ad046, ad081, ad086 (+212 more)
  - What it tests: Edge1 must have parametric curve on face
  - Repair action: Return false; abort entire operation
- **Branch 8** @ line 1100 — *Cannot extract pcurve from edge2* — COVERED by: a024, a104, ad027, ad032, ad043, ad046, ad081, ad086 (+212 more)
  - What it tests: Edge2 must have parametric curve on face
  - Repair action: Return false; abort entire operation
- **Branch 9** @ line 1110 — *Intersection computation failed (Inter.IsDone() == false)* — COVERED by: a004, a012, a019, a020, a023, a034, a065, a068 (+240 more)
  - What it tests: 2D intersection algorithm did not succeed
  - Repair action: Skip this edge pair
- **Branch 10** @ line 1115 — *Point intersection (0 < NbPoints < 3) with both in middle of curves* — **UNCOVERED**
  - What it tests: Both curves intersect at interior points (not at endpoints)
  - Repair action: Analyze distances to endpoints; perform selective edge cutting and/or splitting with new vertex
  - Suggested fixture: defect mentioning 'PositionOnCurve', 'IntRes2d_Middle', 'point intersection'
- **Branch 11** @ line 1138 — *Intersection point near edge1's first or last vertex (distmin < MaxTolVert)* — **UNCOVERED**
  - What it tests: Intersection may snap to edge1's endpoint
  - Repair action: Update vertex tolerance and cut edge at intersection
  - Suggested fixture: defect mentioning 'distmin', 'MaxTolVert', 'near vertex'
- **Branch 12** @ line 1173 — *Intersection point near edge2's first or last vertex (distmin < MaxTolVert)* — **UNCOVERED**
  - What it tests: Intersection may snap to edge2's endpoint
  - Repair action: Update vertex tolerance and cut edge at intersection
  - Suggested fixture: defect mentioning 'distmin', 'MaxTolVert', 'near vertex'
- **Branch 13** @ line 1199 — *Edge1 was cut but edge2 was not (ModifE1 && !ModifE2)* — COVERED by: a096
  - What it tests: Asymmetric modification: one edge cut, other not
  - Repair action: Split edge2 using existing vertex from edge1; decrement num2
- **Branch 14** @ line 1208 — *Edge2 was cut but edge1 was not (!ModifE1 && ModifE2)* — COVERED by: a096
  - What it tests: Asymmetric modification: edge2 cut, edge1 not
  - Repair action: Split edge1 using existing vertex from edge2; decrement num1 and break
- **Branch 15** @ line 1217 — *Neither edge was cut (!ModifE1 && !ModifE2); new vertex required* — COVERED by: gp020, gp034, twi033
  - What it tests: Intersection cannot be snapped to existing vertices
  - Repair action: Create new vertex at midpoint; split both edges; update MaxTolVert
- **Branch 16** @ line 1241 — *Point intersection: edge1 middle, edge2 endpoint (Tr1.Middle && !Tr2.Middle)* — **UNCOVERED**
  - What it tests: One curve middle, other at endpoint
  - Repair action: Find vertex from edge2 and split edge1 using it
  - Suggested fixture: defect mentioning 'FindVertAndSplitEdge', 'asymmetric positions', 'edge2 endpoint'
- **Branch 17** @ line 1260 — *Point intersection: edge1 endpoint, edge2 middle (!Tr1.Middle && Tr2.Middle)* — **UNCOVERED**
  - What it tests: One curve endpoint, other at interior
  - Repair action: Find vertex from edge1 and split edge2 using it
  - Suggested fixture: defect mentioning 'FindVertAndSplitEdge', 'asymmetric positions', 'edge1 endpoint'
- **Branch 18** @ line 1279 — *Point intersection: both at endpoints (!Tr1.Middle && !Tr2.Middle)* — COVERED by: n014, os009
  - What it tests: Intersection only at edge endpoints (vertex-to-vertex touch)
  - Repair action: Union (merge/consolidate) vertices between edge1 and edge2
- **Branch 19** @ line 1289 — *Segment intersection (1D overlap on both curves)* — COVERED by: a019, ad038, ad077, ad085, ad086, ad099, ad117, bo003 (+69 more)
  - What it tests: Curves overlap for a non-trivial segment
  - Repair action: Analyze segment endpoints; perform distance checks and conditional edge cutting/splitting
- **Branch 20** @ line 1311 — *Segment endpoints too far from edge endpoints (MaxTolVert exceeded)* — COVERED by: a004, a012, a019, a020, a023, a034, a065, a068 (+165 more)
  - What it tests: Segment cannot be bridged to wire vertices
  - Repair action: Skip segment; too large to repair safely
- **Branch 21** @ line 1335 — *Segment near edge1's first or last vertex; edge1 can be trimmed* — COVERED by: a025, a084, ad086, fi005, fi008, gn016, gn019, gn024 (+49 more)
  - What it tests: Segment endpoint is near edge1 endpoint or segment is near edge start
  - Repair action: Mark IsModified1 = true; prepare to cut edge1
- **Branch 22** @ line 1354 — *Segment near other endpoint of edge1; overwrite IsModified1 with better fit* — **UNCOVERED**
  - What it tests: Check if other endpoint provides closer fit
  - Repair action: Update NewV and IsModified1 if maxdist is smaller
  - Suggested fixture: defect mentioning 'maxdist', 'newtol', 'IsModified1'
- **Branch 23** @ line 1363 — *IsModified1 = true after segment analysis; cut and update edge1* — **UNCOVERED**
  - What it tests: Edge1 needs trimming after segment analysis
  - Repair action: CutEdge on edge1; update vertex tolerance if needed
  - Suggested fixture: defect mentioning 'CutEdge', 'IsModified1', 'newtol'
- **Branch 24** @ line 1419 — *Segment near edge2's first or last vertex; edge2 can be trimmed* — COVERED by: a025, a084, ad086, fi005, fi008, gn016, gn019, gn024 (+50 more)
  - What it tests: Segment endpoint near edge2 endpoint or segment near edge start
  - Repair action: Mark IsModified2 = true; prepare to cut edge2
- **Branch 25** @ line 1437 — *Segment near other endpoint of edge2; refine IsModified2 with better fit* — **UNCOVERED**
  - What it tests: Check if other endpoint provides closer match
  - Repair action: Update NewV and IsModified2 if maxdist is smaller
  - Suggested fixture: defect mentioning 'maxdist', 'newtol', 'IsModified2'
- **Branch 26** @ line 1446 — *IsModified2 = true after segment analysis; cut and update edge2* — **UNCOVERED**
  - What it tests: Edge2 needs trimming after segment analysis
  - Repair action: CutEdge on edge2; update vertex tolerance if needed
  - Suggested fixture: defect mentioning 'CutEdge', 'IsModified2', 'newtol'
- **Branch 27** @ line 1483 — *Segment: edge1 modified, edge2 not (IsModified1 && !IsModified2)* — COVERED by: a096
  - What it tests: Asymmetric segment handling
  - Repair action: Split edge2 using NewV and segment parameters; decrement num2
- **Branch 28** @ line 1492 — *Segment: edge2 modified, edge1 not (!IsModified1 && IsModified2)* — COVERED by: a096
  - What it tests: Asymmetric segment handling
  - Repair action: Split edge1 using NewV and segment parameters; decrement num1 and break
- **Branch 29** @ line 1501 — *Segment: neither edge modified (!IsModified1 && !IsModified2); small segment within tolerance* — COVERED by: gp020, gp034, twi033
  - What it tests: Segment is within MaxTolVert; can be bridged by single vertex
  - Repair action: Create new vertex at segment center; split both edges; update MaxTolVert
- **Branch 30** @ line 1515 — *Segment: neither modified, but tolerance tolV too large (tolV >= MaxTolVert)* — COVERED by: a005, a100, a102, ad086, ad103, gn030, gn032, gp001 (+35 more)
  - What it tests: Segment is too large to bridge with single vertex
  - Repair action: Create two intermediate vertices at segment endpoints (P01, P02); perform complex multi-edge split and removal
- **Branch 31** @ line 1548 — *Complex segment split: tolerance check on P01 or P02 exceeds MaxTolVert* — **UNCOVERED**
  - What it tests: Bridging vertices would exceed tolerance budget
  - Repair action: Skip segment; too large to fix safely
  - Suggested fixture: defect mentioning 'tolV1', 'tolV2', 'MaxTolVert'
- **Branch 32** @ line 1607 — *Complex segment split: akey count > 1 (ambiguous endpoint matching)* — COVERED by: a004, a012, a019, a020, a023, a034, a065, a068 (+221 more)
  - What it tests: P01 or P02 matches multiple edge endpoints (degenerate case)
  - Repair action: Skip segment; conflicting vertex assignments
- **Branch 33** @ line 1622 — *Complex segment: both P01, P02 at edge1 interior, one P01/P02 at edge2 endpoint (akey1==0 && akey2>0)* — **UNCOVERED**
  - What it tests: Asymmetric bridging pattern for large segment
  - Repair action: SplitEdge1 at p11 with NewV1; adjust dnum1
  - Suggested fixture: defect mentioning 'akey1==0', 'akey2>0', 'large segment'
- **Branch 34** @ line 1631 — *Complex segment: P01 at edge1 endpoint, P02 at edge1 interior (akey1>0 && akey2==0)* — **UNCOVERED**
  - What it tests: Asymmetric bridging pattern for large segment
  - Repair action: SplitEdge1 at p12 with NewV2; adjust dnum1
  - Suggested fixture: defect mentioning 'akey1>0', 'akey2==0', 'large segment'
- **Branch 35** @ line 1640 — *Complex segment: both P01, P02 at edge1 interior (akey1==0 && akey2==0)* — COVERED by: twi065
  - What it tests: Segment interior to both edges; requires two split points per edge
  - Repair action: SplitEdge1 twice: at p11 with NewV1, then at p12 with NewV2 (or next edge if p12 external)
- **Branch 36** @ line 1676 — *Complex segment: P01 close to edge2 first vertex, replace with NewV1* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+33 more)
  - What it tests: Vertex consolidation for segment boundary point
  - Repair action: Replace V12 with NewV1 in edge2; update context; set akey1=1
- **Branch 37** @ line 1698 — *Complex segment: P01 close to edge2 last vertex, replace with NewV1* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+33 more)
  - What it tests: Vertex consolidation for segment boundary point
  - Repair action: Replace V22 with NewV1 in edge2; update context; set akey1=2
- **Branch 38** @ line 1720 — *Complex segment: P02 close to edge2 first vertex, replace with NewV2* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+33 more)
  - What it tests: Vertex consolidation for segment boundary point
  - Repair action: Replace V12 with NewV2 in edge2; update context; set akey2=1
- **Branch 39** @ line 1742 — *Complex segment: P02 close to edge2 last vertex, replace with NewV2* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+33 more)
  - What it tests: Vertex consolidation for segment boundary point
  - Repair action: Replace V22 with NewV2 in edge2; update context; set akey2=2
- **Branch 40** @ line 1766 — *Complex segment edge2 split: P01 interior, P02 at endpoint (akey1==0 && akey2>0)* — **UNCOVERED**
  - What it tests: Asymmetric bridging for edge2 in large segment case
  - Repair action: SplitEdge1 at p21 with NewV1 on edge2
  - Suggested fixture: defect mentioning 'akey1==0', 'akey2>0', 'SplitEdge1'
- **Branch 41** @ line 1776 — *Complex segment edge2 split: P01 at endpoint, P02 interior (akey1>0 && akey2==0)* — **UNCOVERED**
  - What it tests: Asymmetric bridging for edge2 in large segment case
  - Repair action: SplitEdge1 at p22 with NewV2 on edge2
  - Suggested fixture: defect mentioning 'akey1>0', 'akey2==0', 'SplitEdge1'
- **Branch 42** @ line 1786 — *Complex segment edge2 split: both P01, P02 interior (akey1==0 && akey2==0)* — COVERED by: twi052, twi065
  - What it tests: Segment interior to edge2; dual split points required
  - Repair action: SplitEdge1 twice on edge2: at p21 with NewV1, then at p22 with NewV2 (or next edge if p22 external)
- **Branch 43** @ line 1817 — *Complex segment: segment edges removed and indices adjusted* — COVERED by: ad093, ad119, m024, tfa063, tfa066, tsh043, tsh046, twi098
  - What it tests: After all splits, the overlapping segment region is no longer needed
  - Repair action: Remove numseg2 and numseg1 from wire; increment NbRemoved by 2

#### `ShapeFix_IntersectionTool.UnionVertexes` — lines 502–880
(29 branches, 3 covered.)

- **Branch 1** @ line 521 — *vertex-pair-selection* — COVERED by: a106, ad110, ad111, ad112, ad113, ad114, ad115, ad116 (+2 more)
  - What it tests: Closest vertex-pair distance ordering (d11 < d12 && d11 < d21 && d11 < d22) selects V1F-V2F pair
  - Repair action: Union vertices V1F and V2F; update tolerance and replace edge2
- **Branch 2** @ line 524 — *duplicate-vertex-guard* — **UNCOVERED**
  - What it tests: Check V2F not already same as V1F before union
  - Repair action: Skip union if vertices are identical
  - Suggested fixture: defect mentioning '!V2F.IsSame(V1F)', 'd11 < tolv'
- **Branch 3** @ line 541 — *edge-index-boundary* — **UNCOVERED**
  - What it tests: Previous edge index wraps to NbEdges when num2==1
  - Repair action: Set num21 = sewd->NbEdges() for wraparound
  - Suggested fixture: defect mentioning 'num2 > 1', 'num21'
- **Branch 4** @ line 549 — *edge-index-boundary* — **UNCOVERED**
  - What it tests: Next edge index wraps to 1 when num2==NbEdges
  - Repair action: Set num22 = 1 for wraparound
  - Suggested fixture: defect mentioning 'num2 < sewd->NbEdges()', 'num22'
- **Branch 5** @ line 563 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge first-vertex matches old V2F
  - Repair action: Replace V2F with V1F in previous edge front
  - Suggested fixture: defect mentioning 'V21F.IsSame(V2F)', 'edge21'
- **Branch 6** @ line 567 — *bounding-box-preservation* — **UNCOVERED**
  - What it tests: Check if old edge21 had bounding box before update
  - Repair action: Copy bounding box to new edge if exists
  - Suggested fixture: defect mentioning 'boxes.IsBound(edge21)', 'boxes.Bind(NewE'
- **Branch 7** @ line 574 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge last-vertex matches old V2F
  - Repair action: Replace V2F with V1F in previous edge back
  - Suggested fixture: defect mentioning 'V21L.IsSame(V2F)'
- **Branch 8** @ line 585 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge first-vertex matches old V2F
  - Repair action: Replace V2F with V1F in next edge front
  - Suggested fixture: defect mentioning 'V22F.IsSame(V2F)', 'edge22'
- **Branch 9** @ line 596 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge last-vertex matches old V2F
  - Repair action: Replace V2F with V1F in next edge back
  - Suggested fixture: defect mentioning 'V22L.IsSame(V2F)'
- **Branch 10** @ line 610 — *vertex-pair-selection* — COVERED by: a017, gs039, lh013, pf014, tsh041
  - What it tests: Distance ordering (d12 < d21 && d12 < d22) selects V1F-V2L pair
  - Repair action: Union vertices V1F and V2L; reverse edge2 orientation
- **Branch 11** @ line 613 — *duplicate-vertex-guard* — **UNCOVERED**
  - What it tests: Check V2L not already same as V1F before union
  - Repair action: Skip union if vertices are identical
  - Suggested fixture: defect mentioning '!V2L.IsSame(V1F)', 'd12 < tolv'
- **Branch 12** @ line 631 — *edge-index-boundary* — **UNCOVERED**
  - What it tests: Previous edge index wraps for V1F-V2L case
  - Repair action: Set num21 = sewd->NbEdges() or num2-1
  - Suggested fixture: defect mentioning 'num21', 'V1F and V2L'
- **Branch 13** @ line 639 — *edge-index-boundary* — **UNCOVERED**
  - What it tests: Next edge index wraps for V1F-V2L case
  - Repair action: Set num22 = 1 or num2+1
  - Suggested fixture: defect mentioning 'num22'
- **Branch 14** @ line 653 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge first-vertex matches old V2L
  - Repair action: Replace V2L with V1F in previous edge front
  - Suggested fixture: defect mentioning 'V21F.IsSame(V2L)'
- **Branch 15** @ line 664 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge last-vertex matches old V2L
  - Repair action: Replace V2L with V1F in previous edge back
  - Suggested fixture: defect mentioning 'V21L.IsSame(V2L)'
- **Branch 16** @ line 675 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge first-vertex matches old V2L
  - Repair action: Replace V2L with V1F in next edge front
  - Suggested fixture: defect mentioning 'V22F.IsSame(V2L)'
- **Branch 17** @ line 686 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge last-vertex matches old V2L
  - Repair action: Replace V2L with V1F in next edge back
  - Suggested fixture: defect mentioning 'V22L.IsSame(V2L)'
- **Branch 18** @ line 700 — *vertex-pair-selection* — **UNCOVERED**
  - What it tests: Distance ordering (d21 < d22) selects V1L-V2F pair
  - Repair action: Union vertices V1L and V2F
  - Suggested fixture: defect mentioning 'd21', 'V1L and V2F'
- **Branch 19** @ line 703 — *duplicate-vertex-guard* — **UNCOVERED**
  - What it tests: Check V2F not already same as V1L before union
  - Repair action: Skip union if vertices are identical
  - Suggested fixture: defect mentioning '!V2F.IsSame(V1L)', 'd21 < tolv'
- **Branch 20** @ line 742 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge first-vertex matches old V2F (V1L union case)
  - Repair action: Replace V2F with V1L in previous edge front
  - Suggested fixture: defect mentioning 'V21F.IsSame(V2F)', 'V1L'
- **Branch 21** @ line 753 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge last-vertex matches old V2F
  - Repair action: Replace V2F with V1L in previous edge back
  - Suggested fixture: defect mentioning 'V21L.IsSame(V2F)'
- **Branch 22** @ line 764 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge first-vertex matches old V2F
  - Repair action: Replace V2F with V1L in next edge front
  - Suggested fixture: defect mentioning 'V22F.IsSame(V2F)'
- **Branch 23** @ line 775 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge last-vertex matches old V2F
  - Repair action: Replace V2F with V1L in next edge back
  - Suggested fixture: defect mentioning 'V22L.IsSame(V2F)'
- **Branch 24** @ line 789 — *vertex-pair-selection* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Default case (else) selects V1L-V2L pair
  - Repair action: Union vertices V1L and V2L
- **Branch 25** @ line 792 — *duplicate-vertex-guard* — **UNCOVERED**
  - What it tests: Check V2L not already same as V1L before union
  - Repair action: Skip union if vertices are identical
  - Suggested fixture: defect mentioning '!V2L.IsSame(V1L)', 'd22 < tolv'
- **Branch 26** @ line 831 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge first-vertex matches old V2L (V1L union case)
  - Repair action: Replace V2L with V1L in previous edge front
  - Suggested fixture: defect mentioning 'V21F.IsSame(V2L)'
- **Branch 27** @ line 842 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if previous edge last-vertex matches old V2L
  - Repair action: Replace V2L with V1L in previous edge back
  - Suggested fixture: defect mentioning 'V21L.IsSame(V2L)'
- **Branch 28** @ line 853 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge first-vertex matches old V2L
  - Repair action: Replace V2L with V1L in next edge front
  - Suggested fixture: defect mentioning 'V22F.IsSame(V2L)'
- **Branch 29** @ line 864 — *adjacent-edge-vertex-match* — **UNCOVERED**
  - What it tests: Check if next edge last-vertex matches old V2L
  - Repair action: Replace V2L with V1L in next edge back
  - Suggested fixture: defect mentioning 'V22L.IsSame(V2L)'

#### `ShapeFix_IntersectionTool::CutEdge` — lines 199–262
(7 branches, 0 covered.)

- **Branch 1** @ line 200 — *cut-range-trivial* — **UNCOVERED**
  - What it tests: cut and endpoint parameters are too close
  - Repair action: return false (no cut needed)
  - Suggested fixture: defect mentioning 'std::abs(cut - pend) < 10. * Precision::PConfusion()'
- **Branch 2** @ line 208 — *cut-range-too-small* — **UNCOVERED**
  - What it tests: cutting range magnitude is too small
  - Repair action: return false (invalid cut)
  - Suggested fixture: defect mentioning 'aRange < 10. * Precision::PConfusion()'
- **Branch 3** @ line 214 — *curve-property-sameparameter-trimmed* — **UNCOVERED**
  - What it tests: edge uses parametric curve with trimmed line
  - Repair action: extract and handle trimmed basis curve case
  - Suggested fixture: defect mentioning '!BRep_Tool::SameParameter(edge)'
- **Branch 4** @ line 221 — *curve-type-trimmedline* — **UNCOVERED**
  - What it tests: 2D curve is trimmed and basis is line
  - Repair action: compute cut in 3D space and apply range
  - Suggested fixture: defect mentioning 'Geom2d_TrimmedCurve', 'Geom2d_Line'
- **Branch 5** @ line 228 — *cut-location-boundary* — **UNCOVERED**
  - What it tests: cutting from parameter at 2D curve beginning
  - Repair action: adjust 3D range with scaled cut offset
  - Suggested fixture: defect mentioning 'std::abs(pend - lp) < Precision::PConfusion()'
- **Branch 6** @ line 234 — *cut-location-opposite* — **UNCOVERED**
  - What it tests: cutting from parameter at 2D curve end
  - Repair action: adjust 3D range from opposite direction
  - Suggested fixture: defect mentioning 'std::abs(pend - fp) < Precision::PConfusion()'
- **Branch 7** @ line 249 — *cut-range-equals-full* — **UNCOVERED**
  - What it tests: cutting range equals full edge parameter span
  - Repair action: return false (would remove entire edge)
  - Suggested fixture: defect mentioning 'std::abs(std::abs(a - b) - aRange) < Precision::PConfusion()'

#### `ShapeFix_IntersectionTool::FindVertAndSplitEdge` — lines 979–1025
(5 branches, 0 covered.)

- **Branch 1** @ line 994 — *vertex-selection-distance* — **UNCOVERED**
  - What it tests: V1 is closer to edge1 point than V2
  - Repair action: select V1 for split; check if already endpoint
  - Suggested fixture: defect mentioning 'if (pi1.Distance(PV1) < pi1.Distance(PV2))'
- **Branch 2** @ line 996 — *vertex-already-endpoint-check* — **UNCOVERED**
  - What it tests: selected vertex V1 is already endpoint of edge1
  - Repair action: set NeedSplit false (no split required)
  - Suggested fixture: defect mentioning 'if (V1.IsSame(V11) || V1.IsSame(V12))'
- **Branch 3** @ line 1005 — *vertex-already-endpoint-check-v2* — **UNCOVERED**
  - What it tests: V2 is endpoint of edge1
  - Repair action: set NeedSplit false
  - Suggested fixture: defect mentioning 'if (V2.IsSame(V11) || V2.IsSame(V12))'
- **Branch 4** @ line 1012 — *split-requirement-check* — **UNCOVERED**
  - What it tests: split is needed or temporary key override is set
  - Repair action: perform SplitEdge1 if condition met
  - Suggested fixture: defect mentioning 'if (NeedSplit || aTmpKey)'
- **Branch 5** @ line 1014 — *split-edge1-call-success* — **UNCOVERED**
  - What it tests: SplitEdge1 succeeds
  - Repair action: update vertex tolerance and decrement edge index
  - Suggested fixture: defect mentioning 'if (SplitEdge1(sewd, face, num1, param1, V, tolV, boxes))'

#### `ShapeFix_IntersectionTool::SplitEdge` — lines 94–190
(9 branches, 0 covered.)

- **Branch 1** @ line 100 — *vertex-already-endpoint* — **UNCOVERED**
  - What it tests: vertex matches first or last vertex of edge
  - Repair action: return false (cannot split at existing endpoint)
  - Suggested fixture: defect mentioning 'V1.IsSame(vert) || V2.IsSame(vert)'
- **Branch 2** @ line 107 — *parameter-at-boundary* — **UNCOVERED**
  - What it tests: split parameter too close to edge boundaries
  - Repair action: return false (invalid split location)
  - Suggested fixture: defect mentioning 'std::abs(a - param) < 0.01 * preci'
- **Branch 3** @ line 114 — *curve-property-sameparameter* — **UNCOVERED**
  - What it tests: edge has SameParameter flag and is non-degenerate
  - Repair action: extract 3D curve and evaluate point at parameter
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter(edge) && !BRep_Tool::Degenerated(edge)'
- **Branch 4** @ line 118 — *curve-missing* — **UNCOVERED**
  - What it tests: 3D curve is null
  - Repair action: return false (cannot evaluate)
  - Suggested fixture: defect mentioning 'c3d.IsNull()'
- **Branch 5** @ line 123 — *location-transformation* — **UNCOVERED**
  - What it tests: edge has non-identity location transform
  - Repair action: apply transformation to 3D point
  - Suggested fixture: defect mentioning '!L.IsIdentity()', 'P1.Transformed(L.Transformation())'
- **Branch 6** @ line 130 — *curve-property-pcurve* — **UNCOVERED**
  - What it tests: edge uses parametric curve (non-SameParameter case)
  - Repair action: use surface and 2D curve to evaluate point
  - Suggested fixture: defect mentioning 'BRep_Tool::Surface(face, L)', 'sas->Value(c2d->Value(param))'
- **Branch 7** @ line 139 — *vertex-tolerance-insufficient* — **UNCOVERED**
  - What it tests: distance between edge point and vertex exceeds precision
  - Repair action: update vertex tolerance to match distance
  - Suggested fixture: defect mentioning 'P1.Distance(P2) > preci'
- **Branch 8** @ line 151 — *parameter-range-order* — **UNCOVERED**
  - What it tests: parameter range order (ascending vs descending)
  - Repair action: assign first and last correctly
  - Suggested fixture: defect mentioning 'if (a < b)'
- **Branch 9** @ line 182 — *edge-orientation* — **UNCOVERED**
  - What it tests: edge orientation is reversed
  - Repair action: swap newE1 and newE2 to preserve orientation
  - Suggested fixture: defect mentioning 'if (orient == TopAbs_REVERSED)'

#### `ShapeFix_IntersectionTool::SplitEdge1` — lines 278–358
(5 branches, 0 covered.)

- **Branch 1** @ line 279 — *edge-index-invalid* — **UNCOVERED**
  - What it tests: edge index is out of valid range
  - Repair action: assert failure and return false
  - Suggested fixture: defect mentioning 'Standard_ASSERT_RETURN(num > 0 && num <= sewd->NbEdges())'
- **Branch 2** @ line 283 — *split-failed* — **UNCOVERED**
  - What it tests: underlying SplitEdge fails
  - Repair action: return false (split not performed)
  - Suggested fixture: defect mentioning '!SplitEdge(edge, param, vert, face, newE1, newE2, preci)'
- **Branch 3** @ line 292 — *context-not-null* — **UNCOVERED**
  - What it tests: context object is initialized
  - Repair action: replace edge in context with wire
  - Suggested fixture: defect mentioning '!myContext.IsNull()'
- **Branch 4** @ line 304 — *edge-position-last* — **UNCOVERED**
  - What it tests: split edge is at end of wire
  - Repair action: append newE2 to wire
  - Suggested fixture: defect mentioning 'if (num == sewd->NbEdges())'
- **Branch 5** @ line 326 — *curve-type-bspline-out-of-range* — **UNCOVERED**
  - What it tests: 2D curve is B-spline with range outside basis curve
  - Repair action: load adaptor without range limits
  - Suggested fixture: defect mentioning 'Geom2d_BSplineCurve', 'cf < aFirst || cl > aLast'

#### `ShapeFix_IntersectionTool::SplitEdge2` — lines 376–491
(7 branches, 0 covered.)

- **Branch 1** @ line 380 — *split-failed* — **UNCOVERED**
  - What it tests: split at midpoint parameter fails
  - Repair action: return false (split not performed)
  - Suggested fixture: defect mentioning '!SplitEdge(edge, param, vert, face, newE1, newE2, preci)'
- **Branch 2** @ line 393 — *parameter-mapping-split-location* — **UNCOVERED**
  - What it tests: split point matches newE1 last parameter
  - Repair action: determine correct parameter assignments for cutting
  - Suggested fixture: defect mentioning 'if (lp1 == param)'
- **Branch 3** @ line 395 — *parameter-alignment* — **UNCOVERED**
  - What it tests: parameter arithmetic direction matches curve orientation
  - Repair action: cut with param1 or param2 based on direction
  - Suggested fixture: defect mentioning '(lp1 - fp1) * (lp1 - param1) > 0'
- **Branch 4** @ line 408 — *parameter-mapping-reversed* — **UNCOVERED**
  - What it tests: split point matches newE1 first parameter
  - Repair action: handle reversed parameter mapping
  - Suggested fixture: defect mentioning '(fp1 - lp1) * (fp1 - param1) > 0'
- **Branch 5** @ line 426 — *context-not-null* — **UNCOVERED**
  - What it tests: context object is initialized
  - Repair action: replace edge in context
  - Suggested fixture: defect mentioning '!myContext.IsNull()'
- **Branch 6** @ line 438 — *edge-position-last* — **UNCOVERED**
  - What it tests: split edge at end of wire
  - Repair action: append newE2 to wire
  - Suggested fixture: defect mentioning 'if (num == sewd->NbEdges())'
- **Branch 7** @ line 459 — *curve-type-bspline-out-of-range* — **UNCOVERED**
  - What it tests: 2D curve is B-spline with range outside basis
  - Repair action: load adaptor without range constraints
  - Suggested fixture: defect mentioning 'Geom2d_BSplineCurve'

#### `ShapeFix_IntersectionTool::UnionVertexes` — lines 502–880
(14 branches, 1 covered.)

- **Branch 1** @ line 521 — *vertex-pairing-case1* — **UNCOVERED**
  - What it tests: d11 (V1F-V2F) is smallest distance among all vertex pairs
  - Repair action: merge V1F and V2F if within tolerance
  - Suggested fixture: defect mentioning 'if (d11 < d12 && d11 < d21 && d11 < d22)'
- **Branch 2** @ line 524 — *vertex-identity-check* — **UNCOVERED**
  - What it tests: V1F and V2F are distinct and close
  - Repair action: update tolerance and replace vertices in adjacent edges
  - Suggested fixture: defect mentioning '!V2F.IsSame(V1F) && d11 < tolv'
- **Branch 3** @ line 541 — *circular-edge-indexing-predecessor* — **UNCOVERED**
  - What it tests: edge has predecessor in circular wire
  - Repair action: compute predecessor index, handling wraparound
  - Suggested fixture: defect mentioning 'if (num2 > 1)'
- **Branch 4** @ line 549 — *circular-edge-indexing-successor* — **UNCOVERED**
  - What it tests: edge has successor in circular wire
  - Repair action: compute successor index, handling wraparound
  - Suggested fixture: defect mentioning 'if (num2 < sewd->NbEdges())'
- **Branch 5** @ line 563 — *vertex-merge-predecessor-first* — **UNCOVERED**
  - What it tests: predecessor edge first vertex matches old vertex
  - Repair action: replace first vertex with merged vertex
  - Suggested fixture: defect mentioning 'if (V21F.IsSame(V2F))'
- **Branch 6** @ line 574 — *vertex-merge-predecessor-last* — **UNCOVERED**
  - What it tests: predecessor edge last vertex matches old vertex
  - Repair action: replace last vertex with merged vertex
  - Suggested fixture: defect mentioning 'if (V21L.IsSame(V2F))'
- **Branch 7** @ line 585 — *vertex-merge-successor-first* — **UNCOVERED**
  - What it tests: successor edge first vertex matches old vertex
  - Repair action: replace first vertex with merged vertex
  - Suggested fixture: defect mentioning 'if (V22F.IsSame(V2F))'
- **Branch 8** @ line 596 — *vertex-merge-successor-last* — **UNCOVERED**
  - What it tests: successor edge last vertex matches old vertex
  - Repair action: replace last vertex with merged vertex
  - Suggested fixture: defect mentioning 'if (V22L.IsSame(V2F))'
- **Branch 9** @ line 610 — *vertex-pairing-case2* — **UNCOVERED**
  - What it tests: d12 (V1F-V2L) is smallest distance
  - Repair action: merge V1F and V2L with cascading updates
  - Suggested fixture: defect mentioning 'else if (d12 < d21 && d12 < d22)'
- **Branch 10** @ line 613 — *vertex-identity-check-case2* — **UNCOVERED**
  - What it tests: V1F and V2L are distinct and close
  - Repair action: perform vertex union and update adjacent edges
  - Suggested fixture: defect mentioning '!V2L.IsSame(V1F) && d12 < tolv'
- **Branch 11** @ line 700 — *vertex-pairing-case3* — **UNCOVERED**
  - What it tests: d21 (V1L-V2F) is smallest distance
  - Repair action: merge V1L and V2F with edge updates
  - Suggested fixture: defect mentioning 'else if (d21 < d22)'
- **Branch 12** @ line 703 — *vertex-identity-check-case3* — **UNCOVERED**
  - What it tests: V1L and V2F are distinct and close
  - Repair action: union vertices and update all adjacent edges
  - Suggested fixture: defect mentioning '!V2F.IsSame(V1L) && d21 < tolv'
- **Branch 13** @ line 792 — *vertex-pairing-case4* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: d22 (V1L-V2L) is smallest or only remaining distance
  - Repair action: merge V1L and V2L with full edge replacement
- **Branch 14** @ line 792 — *vertex-identity-check-case4* — **UNCOVERED**
  - What it tests: V1L and V2L are distinct and close enough
  - Repair action: perform final vertex union case
  - Suggested fixture: defect mentioning '!V2L.IsSame(V1L) && d22 < tolv'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Shape.cxx + ShapeFix_WireVertex.cxx`

3 methods, 40 branches, 17 covered.

#### `ShapeFix_Shape.Perform` — lines 84–303
(17 branches, 11 covered.)

- **Branch 1** @ line 88 — *Face tool initialization* — **UNCOVERED**
  - What it tests: FixFaceTool non-null and shape is single FACE
  - Repair action: Save/set FixSmallAreaWireMode for single-face context
  - Suggested fixture: defect mentioning 'FixFaceTool', 'FixSmallAreaWireMode', 'ShapeType'
- **Branch 2** @ line 105 — *Shape caching/identity* — **UNCOVERED**
  - What it tests: Shape already in fixing context or cache map
  - Repair action: Return early with cached result via Context->Apply()
  - Suggested fixture: defect mentioning 'IsNewShape', 'myMapFixingShape', 'aShapeNullLoc'
- **Branch 3** @ line 118 — *Vertex position error* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+77 more)
  - What it tests: NeedFix(myFixVertexPositionMode) enabled
  - Repair action: Call ShapeFix::FixVertexPosition on shape
- **Branch 4** @ line 132 — *Compound/assembly with sub-shapes* — COVERED by: a085, ad002, ad038, ad055, ad086, ad107, ad112, ls017 (+10 more)
  - What it tests: TopAbs_COMPOUND or TopAbs_COMPSOLID shape type
  - Repair action: Recursive Perform() on each child with modified mode flags
- **Branch 5** @ line 142 — *Abort during compound iteration* — **UNCOVERED**
  - What it tests: Progress scope indicator More() returns false in compound loop
  - Repair action: Abort execution and return false (user cancelled)
  - Suggested fixture: defect mentioning 'aPSSubShape.More', 'aborted execution'
- **Branch 6** @ line 160 — *Solid-level shape defects* — **UNCOVERED**
  - What it tests: TopAbs_SOLID shape type and NeedFix(myFixSolidMode)
  - Repair action: Invoke myFixSolid->Perform() with context
  - Suggested fixture: defect mentioning 'TopAbs_SOLID', 'myFixSolid', 'DONE4'
- **Branch 7** @ line 176 — *Shell-level topology defects* — **UNCOVERED**
  - What it tests: TopAbs_SHELL shape type and NeedFix(myFixShellMode)
  - Repair action: Invoke FixShellTool->Perform() with context
  - Suggested fixture: defect mentioning 'TopAbs_SHELL', 'FixShellTool', 'DONE4'
- **Branch 8** @ line 193 — *Face with wire/edge defects* — COVERED by: tsh018
  - What it tests: TopAbs_FACE shape type and NeedFix(myFixFaceMode)
  - Repair action: Invoke FixFaceTool->Perform() with ModifyTopologyMode=true
- **Branch 9** @ line 199 — *Topology modification setting for face* — COVERED by: gp027, n005, ps001, tfa012, twi022
  - What it tests: Save original FixWireTool->ModifyTopologyMode before setting true
  - Repair action: Enable topology modification during face fix, then restore
- **Branch 10** @ line 212 — *Wire vertex/parameter defects* — COVERED by: twi066, twi067, twi078
  - What it tests: TopAbs_WIRE shape type and NeedFix(myFixWireMode)
  - Repair action: Invoke FixWireTool->Perform() with topology and closure settings
- **Branch 11** @ line 221 — *Wire closure state mismatch* — COVERED by: a102, ad055, ad077, ad086, ad101, bo001, bo002, bo003 (+268 more)
  - What it tests: S.Closed() check - is wire topologically closed?
  - Repair action: Set ClosedWireMode=false for open wires only
- **Branch 12** @ line 238 — *Edge vertex tolerance defects* — COVERED by: tfa037, twi048, twi059, twi061, twi066, twi067
  - What it tests: TopAbs_EDGE shape type (fallback case)
  - Repair action: Call FixEdgeTool->FixVertexTolerance() without context
- **Branch 13** @ line 252 — *Abort after shape type fix* — **UNCOVERED**
  - What it tests: Progress scope More() after shape type dispatch
  - Repair action: Abort execution if user cancelled during fix
  - Suggested fixture: defect mentioning 'aPS.More', 'aborted execution'
- **Branch 14** @ line 259 — *Parameterization mismatch (same parameter correction)* — COVERED by: ad086, gp022, n004, n005, n006, sw009, twi044, twi065
  - What it tests: NeedFix(myFixSameParameterMode) enabled
  - Repair action: Call SameParameter() to fix edge parameterization consistency
- **Branch 15** @ line 262 — *Abort after same-parameter fix* — COVERED by: ad119, fi001, fi002, fi003, fi004, fi005, fi006, fi007 (+1 more)
  - What it tests: Progress scope More() after SameParameter() call
  - Repair action: Abort execution if user cancelled during same-parameter fix
- **Branch 16** @ line 267 — *Vertex tolerance (multi-face context)* — COVERED by: ad086, bo030, gn031, gp002, gp016, gp038, m053, n001 (+21 more)
  - What it tests: NeedFix(myFixVertexTolMode) enabled
  - Repair action: Conditionally fix vertex tolerances in multi-face shapes
- **Branch 17** @ line 271 — *Multi-face vs single-face vertex tolerance* — COVERED by: m093
  - What it tests: Count faces (nbF > 1) - is vertex shared across multiple faces?
  - Repair action: Only fix vertex tolerances for multi-face vertices (bug 0025455)

#### `ShapeFix_WireVertex.Fix` — lines 142–293
(13 branches, 1 covered.)

- **Branch 1** @ line 151 — *Wire analysis not performed* — **UNCOVERED**
  - What it tests: myAnalyzer.IsDone() - has wire been analyzed?
  - Repair action: Return 0 (skip fixing) if analysis not completed
  - Suggested fixture: defect mentioning 'IsDone', 'return 0'
- **Branch 2** @ line 160 — *Count vertices needing fix* — **UNCOVERED**
  - What it tests: First pass: count all vertices with stat > 0
  - Repair action: Determine if any vertices need reconstruction
  - Suggested fixture: defect mentioning 'myAnalyzer.Status(i) > 0', 'nbfix++'
- **Branch 3** @ line 169 — *No defects found (early exit)* — **UNCOVERED**
  - What it tests: nbfix == 0 after counting
  - Repair action: Return 0 - no vertices need fixing
  - Suggested fixture: defect mentioning 'nbfix == 0', 'return 0'
- **Branch 4** @ line 182 — *First pass: extract vertex/parameter data* — **UNCOVERED**
  - What it tests: Loop i=1 to nb to collect original vertices and edges
  - Repair action: Store VI, VJ (vertices) and EF (edges) for later reconstruction
  - Suggested fixture: defect mentioning 'NCollection_HArray1', 'VI, VJ, EF'
- **Branch 5** @ line 207 — *Curve-based parameter for previous edge* — **UNCOVERED**
  - What it tests: stat < 4 - does previous edge parameter come from curve?
  - Repair action: Use curve endpoint parameter (cl) for vertex at edge_i end
  - Suggested fixture: defect mentioning 'stat < 4', 'upre = cl'
- **Branch 6** @ line 212 — *Curve-based parameter for following edge* — **UNCOVERED**
  - What it tests: stat < 3 || stat == 4 - does following edge use curve endpoint?
  - Repair action: Use curve endpoint parameter (cf) for vertex at edge_j start
  - Suggested fixture: defect mentioning 'stat < 3 || stat == 4', 'ufol = cf'
- **Branch 7** @ line 223 — *Second pass - no fixes after count* — **UNCOVERED**
  - What it tests: nbfix == 0 check after first pass (defensive)
  - Repair action: Return nbfix if no vertices need fixing
  - Suggested fixture: defect mentioning 'nbfix == 0', 'return nbfix'
- **Branch 8** @ line 233 — *Remove old vertices from edges* — **UNCOVERED**
  - What it tests: Loop i=1 to nb to strip old vertices before re-adding
  - Repair action: Call B.Remove() on both endpoints to allow new vertex attachment
  - Suggested fixture: defect mentioning 'Vertices(E1, VA, VB)', 'B.Remove', 'E1.Free'
- **Branch 9** @ line 260 — *Vertex position reconstruction* — **UNCOVERED**
  - What it tests: stat > 2 - does vertex need coordinate update?
  - Repair action: UpdateVertex at new position from myAnalyzer.Position(i)
  - Suggested fixture: defect mentioning 'stat > 2', 'UpdateVertex', 'gp_Pnt(myAnalyzer.Position'
- **Branch 10** @ line 266 — *Vertex parameter/tolerance update* — **UNCOVERED**
  - What it tests: stat > 0 - does vertex need parameter updates?
  - Repair action: UpdateVertex with upre and ufol parameters at both edge ends
  - Suggested fixture: defect mentioning 'stat > 0', 'UpdateVertex(V1, upre, E1', 'UpdateVertex(V1, ufol, E2'
- **Branch 11** @ line 275 — *Re-attach following edge endpoint* — COVERED by: a030, a098, a107, ad005, ad082, ad086, ad118, lh028 (+20 more)
  - What it tests: Add V1 to E2 after vertex orientation set to FORWARD
  - Repair action: Attach updated vertex to following edge
- **Branch 12** @ line 277 — *Re-attach previous edge endpoint with reverse* — **UNCOVERED**
  - What it tests: Set V1 to REVERSED and add to E1
  - Repair action: Attach updated vertex (reversed) to previous edge
  - Suggested fixture: defect mentioning 'V1.Orientation(TopAbs_REVERSED)', 'B.Add(E1, V1)'
- **Branch 13** @ line 287 — *Update wire data with reconstructed edges* — **UNCOVERED**
  - What it tests: Final pass i=1 to nb to sync reconstructed edges back
  - Repair action: Call sbwd->Set() to update ShapeExtend_WireData with new edges
  - Suggested fixture: defect mentioning 'sbwd->Set', 'EF->Value(i)'

#### `ShapeFix_WireVertex.FixSame` — lines 83–137
(10 branches, 5 covered.)

- **Branch 1** @ line 86 — *Wire analysis not performed* — **UNCOVERED**
  - What it tests: myAnalyzer.IsDone() check - has wire been analyzed?
  - Repair action: Return 0 (skip fixing) if analysis not completed
  - Suggested fixture: defect mentioning 'IsDone', 'return 0'
- **Branch 2** @ line 97 — *Wire edge pair iteration* — **UNCOVERED**
  - What it tests: Loop through all nb consecutive edge pairs in wire
  - Repair action: Process each (edge_i, edge_{i+1}) pair for vertex fixing
  - Suggested fixture: defect mentioning 'for i=1', 'j=i+1', 'nb edges'
- **Branch 3** @ line 101 — *Non-defective vertex status* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: myAnalyzer.Status(i) != 1 && != 2 (not SameCoord or Close)
  - Repair action: Skip pair - vertex already correct or needs different fix
- **Branch 4** @ line 112 — *Vertex already merged (same instance)* — **UNCOVERED**
  - What it tests: V1 == V2 - are the two edge endpoints identical objects?
  - Repair action: Set flag and skip - vertex merge already done
  - Suggested fixture: defect mentioning 'V1 == V2', 'SetSameVertex', 'deja fait'
- **Branch 5** @ line 117 — *Close vertex with tolerance update needed* — COVERED by: gn017, twi046, twi047, twi059, twi062, twi065
  - What it tests: stat == 2 (Close defect type requiring tolerance adjustment)
  - Repair action: Update vertex tolerances from curve 3D endpoints
- **Branch 6** @ line 118 — *SameCoord defect (tolerance already OK)* — **UNCOVERED**
  - What it tests: stat == 1 (vertices already same coordinate, different object)
  - Repair action: Simple merge without updating tolerances
  - Suggested fixture: defect mentioning 'stat == 1', 'no UpdateVertex'
- **Branch 7** @ line 123 — *Previous edge endpoint parameter extraction* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1118 more)
  - What it tests: Get curve 3D endpoint parameter (cl) from previous edge
  - Repair action: Update V1 tolerance at edge_i endpoint using cl parameter
- **Branch 8** @ line 124 — *Following edge endpoint parameter extraction* — COVERED by: a008, a024, ad038, bo001, bo007, gs037, le011, le017 (+27 more)
  - What it tests: Get curve 3D endpoint parameter (cf) from following edge
  - Repair action: Update V1 tolerance at edge_j endpoint using cf parameter
- **Branch 9** @ line 128 — *Vertex orientation alignment for merge* — **UNCOVERED**
  - What it tests: Set V1 orientation to match E2 before adding to E2
  - Repair action: Orient vertex correctly before adding to following edge
  - Suggested fixture: defect mentioning 'V1.Orientation', 'E2.Orientation'
- **Branch 10** @ line 131 — *Reverse and add to previous edge* — COVERED by: ad103, n010
  - What it tests: Reverse V1 orientation and add to E1
  - Repair action: Add reversed vertex to previous edge


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Shell.cxx, src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Solid.cxx`

4 methods, 53 branches, 8 covered.

#### `ShapeFix_Shell.FixFaceOrientation` — lines 1428–1653
(20 branches, 2 covered.)

- **Branch 1** @ line 1442 — *duplicate_faces_in_shell* — **UNCOVERED**
  - What it tests: Same face appears multiple times in shell iteration
  - Repair action: Track unique faces; set done=true if duplicates found
  - Suggested fixture: defect mentioning 'aMapAdded.Add(iter.Value())', 'Lface.Length() < nbF'
- **Branch 2** @ line 1460 — *free_boundary_edge* — **UNCOVERED**
  - What it tests: Edge shared by only 1 face (free boundary), non-degenerate
  - Repair action: Set isFreeBoundaries=true, mark shell as non-closed
  - Suggested fixture: defect mentioning 'aFaceCount == 1', '!BRep_Tool::Degenerated(E)'
- **Branch 3** @ line 1469 — *multi_connected_edge* — **UNCOVERED**
  - What it tests: Edge shared by > 2 faces (non-manifold/over-connected)
  - Repair action: Record multi-connected edges for later handling
  - Suggested fixture: defect mentioning 'aFaceCount > 2', 'aMapMultiConnectEdges.Add'
- **Branch 4** @ line 1474 — *closed_flag_inconsistency* — **UNCOVERED**
  - What it tests: IsClosed() flag contradicts actual boundary state
  - Repair action: Correct Closed() flag and warn user
  - Suggested fixture: defect mentioning 'BRep_Tool::IsClosed(myShell)', 'myShell.Closed'
- **Branch 5** @ line 1486 — *improperly_connected_shell* — **UNCOVERED**
  - What it tests: GetShells() finds shell splitting or face ungrouping
  - Repair action: Decompose into multiple candidate shells, set done=true
  - Suggested fixture: defect mentioning 'GetShells(Lface, aMapMultiConnectEdges)', 'aSeqShells.Append'
- **Branch 6** @ line 1498 — *multiple_shells_generated* — **UNCOVERED**
  - What it tests: Decomposition produced > 1 shell from original
  - Repair action: Mark done=true; decide on compounding vs non-manifold
  - Suggested fixture: defect mentioning 'aSeqShells.Length() > 1', 'done = true'
- **Branch 7** @ line 1513 — *multiconexity_face_assignment* — **UNCOVERED**
  - What it tests: Faces with only multi-connected boundaries need assignment
  - Repair action: Attempt to add them to shells with multi-edge holes
  - Suggested fixture: defect mentioning 'AddMultiConexityFaces', 'aIsDone'
- **Branch 8** @ line 1522 — *moebius_like_face* — **UNCOVERED**
  - What it tests: Faces that cannot be properly oriented (Moebius strips)
  - Repair action: Extract to separate shells or fail with compounds
  - Suggested fixture: defect mentioning '!aErrFaces.IsEmpty()', 'Mebius faces'
- **Branch 9** @ line 1534 — *moebius_with_good_shells* — **UNCOVERED**
  - What it tests: Unorientable faces exist AND some proper shells remain
  - Repair action: Create compound: add proper shell + individual error-face shells
  - Suggested fixture: defect mentioning 'aNumMultShell', 'aErrFaces.Length()'
- **Branch 10** @ line 1536 — *single_good_shell_plus_moebius* — **UNCOVERED**
  - What it tests: One valid shell + multiple unorientable faces
  - Repair action: Build compound: 1 good shell + 1 shell per error-face
  - Suggested fixture: defect mentioning 'aNumMultShell == 1', 'B.MakeShell(aSh)'
- **Branch 11** @ line 1548 — *multiple_good_shells_plus_moebius* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Multiple valid shells AND unorientable faces coexist
  - Repair action: Create compound with all good shells + error-face shells
- **Branch 12** @ line 1572 — *multiple_disconnected_shells* — **UNCOVERED**
  - What it tests: More than 1 valid shell (topologically disconnected)
  - Repair action: Try merging open shells to create closed shell
  - Suggested fixture: defect mentioning 'aNumMultShell > 1', 'CreateClosedShell'
- **Branch 13** @ line 1578 — *open_vs_closed_shells* — **UNCOVERED**
  - What it tests: Shell is not closed (has boundaries)
  - Repair action: Separate open shells for potential merging
  - Suggested fixture: defect mentioning '!BRep_Tool::IsClosed(aShell)', 'OpenShells.Append'
- **Branch 14** @ line 1584 — *multiple_open_shells* — **UNCOVERED**
  - What it tests: More than 1 open shell after decomposition
  - Repair action: Attempt to create single closed shell from them
  - Suggested fixture: defect mentioning 'OpenShells.Length() > 1', 'CreateClosedShell'
- **Branch 15** @ line 1594 — *ungrouped_faces* — **UNCOVERED**
  - What it tests: Faces remain unassigned to any shell
  - Repair action: Create individual single-face shells for each
  - Suggested fixture: defect mentioning 'Lface.Length()', 'B.MakeShell(OneShell)'
- **Branch 16** @ line 1606 — *multiple_shell_combination_mode* — **UNCOVERED**
  - What it tests: Multiple shells exist and NonManifold flag is true
  - Repair action: Merge into single non-manifold shell
  - Suggested fixture: defect mentioning 'NonManifold && aSeqShells.Length() > 1', 'CreateNonManifoldShells'
- **Branch 17** @ line 1612 — *cumulative_changes* — **UNCOVERED**
  - What it tests: Any decomposition or multi-face assignment occurred
  - Repair action: Mark done=true if multiple shells or multiconexity fix
  - Suggested fixture: defect mentioning 'aSeqShells.Length() > 1 || aIsDone', 'done ='
- **Branch 18** @ line 1614 — *single_shell_result* — **UNCOVERED**
  - What it tests: Final result is exactly 1 shell
  - Repair action: Store as myShell; return as single entity
  - Suggested fixture: defect mentioning 'aSeqShells.Length() == 1', 'myNbShells = 1'
- **Branch 19** @ line 1620 — *multiple_shell_compound* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Result is > 1 shell (multi-component)
  - Repair action: Build compound shape from all shells
- **Branch 20** @ line 1632 — *fix_completed_and_logged* — **UNCOVERED**
  - What it tests: Actual structural changes made (done=true)
  - Repair action: Update context, encode DONE2, send success message
  - Suggested fixture: defect mentioning 'if (done)', 'Context()->Replace', 'SendWarning'

#### `ShapeFix_Shell.Perform` — lines 102–174
(9 branches, 2 covered.)

- **Branch 1** @ line 104 — *missing_reshape_context* — **UNCOVERED**
  - What it tests: Context is null before face-fixing phase
  - Repair action: Create new ShapeBuild_ReShape context
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'SetContext'
- **Branch 2** @ line 110 — *face_geometry_defects* — **UNCOVERED**
  - What it tests: NeedFix(myFixFaceMode) indicates faces have geometric issues
  - Repair action: Iterate through faces and call myFixFace->Perform() on each
  - Suggested fixture: defect mentioning 'NeedFix(myFixFaceMode)', 'myFixFace->Perform()'
- **Branch 3** @ line 125 — *face_fix_success* — **UNCOVERED**
  - What it tests: Individual face repair succeeded
  - Repair action: Mark status as DONE1 if any face fixed
  - Suggested fixture: defect mentioning 'if (myFixFace->Perform())', 'ShapeExtend_DONE1'
- **Branch 4** @ line 133 — *user_abort_signal* — COVERED by: in014
  - What it tests: User interrupted progress scope during face iteration
  - Repair action: Halt algorithm and return false
- **Branch 5** @ line 140 — *face_orientation_defects* — COVERED by: ad086, tfa034, tsh008
  - What it tests: NeedFix(myFixOrientationMode) indicates orientation issues
  - Repair action: Call FixFaceOrientation to reorient faces in shell
- **Branch 6** @ line 150 — *closed_shell_with_free_edges* — **UNCOVERED**
  - What it tests: Shell marked closed but has free (non-manifold) edges
  - Repair action: Clear closed flag and send warning
  - Suggested fixture: defect mentioning 'aCurShell.Closed()', 'HasFreeEdges()'
- **Branch 7** @ line 154 — *free_edge_detection* — **UNCOVERED**
  - What it tests: ShapeAnalysis_Shell detects free edges in closed shell
  - Repair action: Unset Closed() flag as inconsistent
  - Suggested fixture: defect mentioning 'aSas.HasFreeEdges()', 'aCurShell.Closed(false)'
- **Branch 8** @ line 165 — *cumulative_fix_status* — **UNCOVERED**
  - What it tests: Any face was successfully fixed in loop
  - Repair action: Encode DONE1 status in myStatus
  - Suggested fixture: defect mentioning 'if (status)', 'ShapeExtend_DONE1'
- **Branch 9** @ line 169 — *orientation_fix_flag* — **UNCOVERED**
  - What it tests: DONE2 status already set (orientation stage succeeded)
  - Repair action: Propagate status and return true
  - Suggested fixture: defect mentioning 'Status(ShapeExtend_DONE2)', 'status = true'

#### `ShapeFix_Solid.Perform` — lines 461–644
(20 branches, 4 covered.)

- **Branch 1** @ line 464 — *missing_reshape_context* — **UNCOVERED**
  - What it tests: Context is null before shell-fixing phase
  - Repair action: Create new ShapeBuild_ReShape context
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'SetContext'
- **Branch 2** @ line 483 — *shell_geometry_defects* — **UNCOVERED**
  - What it tests: NeedFix(myFixShellMode) indicates shells have issues
  - Repair action: Iterate shells and call myFixShell->Perform() on each
  - Suggested fixture: defect mentioning 'NeedFix(myFixShellMode)', 'myFixShell->Perform'
- **Branch 3** @ line 495 — *shell_fix_success* — **UNCOVERED**
  - What it tests: Individual shell repair succeeded
  - Repair action: Mark status DONE1 and accumulate shell count
  - Suggested fixture: defect mentioning 'if (myFixShell->Perform())', 'myFixShell->NbShells()'
- **Branch 4** @ line 504 — *user_abort_signal* — COVERED by: in014
  - What it tests: User interrupted progress scope during shell iteration
  - Repair action: Halt algorithm and return false
- **Branch 5** @ line 514 — *skip_orientation_fix* — **UNCOVERED**
  - What it tests: Shell orientation fixing is disabled
  - Repair action: Skip orientation phase; return current status
  - Suggested fixture: defect mentioning '!NeedFix(myFixShellOrientationMode)', 'return status'
- **Branch 6** @ line 520 — *single_shell_geometry* — **UNCOVERED**
  - What it tests: Solid contains exactly 1 shell
  - Repair action: Attempt closed-shell->solid conversion
  - Suggested fixture: defect mentioning 'NbShells == 1', 'SolidFromShell'
- **Branch 7** @ line 525 — *shell_exists_validation* — **UNCOVERED**
  - What it tests: Shell entity found in solid topology
  - Repair action: Extract and analyze shell for closure/boundary state
  - Suggested fixture: defect mentioning 'if (aExp.More())', 'TopoDS::Shell'
- **Branch 8** @ line 541 — *closed_shell_detection* — **UNCOVERED**
  - What it tests: Shell has no free edges (topologically closed)
  - Repair action: Mark isClosed=true for solid conversion logic
  - Suggested fixture: defect mentioning 'isClosed = (!numedge)', 'aShtmp.Closed(isClosed)'
- **Branch 9** @ line 545 — *closed_or_open_solid_mode* — **UNCOVERED**
  - What it tests: Shell is closed OR myCreateOpenSolidMode is enabled
  - Repair action: Proceed to solid creation from shell
  - Suggested fixture: defect mentioning 'if (isClosed || myCreateOpenSolidMode)', 'SolidFromShell'
- **Branch 10** @ line 556 — *shell_orientation_corrected* — **UNCOVERED**
  - What it tests: SolidFromShell set DONE2 status (shell was reversed)
  - Repair action: Replace temporary shape with corrected solid
  - Suggested fixture: defect mentioning 'ShapeExtend_DONE2', 'Context()->Replace'
- **Branch 11** @ line 567 — *open_shell_no_solid* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Shell is open AND myCreateOpenSolidMode is disabled
  - Repair action: Fail with DONE3 status; extract shell instead
- **Branch 12** @ line 577 — *multiple_shells_in_solid* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Solid contains > 1 shell (compound-like topology)
  - Repair action: Call CreateSolids() to decompose/reorient
- **Branch 13** @ line 581 — *solids_created_from_multi_shell* — **UNCOVERED**
  - What it tests: CreateSolids() successfully decomposed into solids
  - Repair action: Retrieve created solids from map for analysis
  - Suggested fixture: defect mentioning 'if(CreateSolids(aResShape', 'aMapSolids.Extent()'
- **Branch 14** @ line 584 — *single_solid_result* — **UNCOVERED**
  - What it tests: CreateSolids produced exactly 1 solid
  - Repair action: Use as mySolid; check if open-shell mode applies
  - Suggested fixture: defect mentioning 'aMapSolids.Extent() == 1', 'TopAbs_SHELL && myCreateOpenSolidMode'
- **Branch 15** @ line 587 — *open_shell_with_open_solid_mode* — **UNCOVERED**
  - What it tests: Result is shell + myCreateOpenSolidMode enabled
  - Repair action: Wrap shell in solid container
  - Suggested fixture: defect mentioning 'aResShape.ShapeType() == TopAbs_SHELL && myCreateOpenSolidMode', 'B.MakeSolid(solid)'
- **Branch 16** @ line 598 — *open_shell_failure* — **UNCOVERED**
  - What it tests: Result is open shell but mode disabled
  - Repair action: Report failure; cannot create solid from open shell
  - Suggested fixture: defect mentioning 'aResSol.ShapeType() == TopAbs_SHELL', 'SendFail'
- **Branch 17** @ line 606 — *multiple_solids_created* — **UNCOVERED**
  - What it tests: CreateSolids produced > 1 solid
  - Repair action: Build compound; warn about disconnected topology
  - Suggested fixture: defect mentioning 'else if(aMapSolids.Extent() >1)', 'aB.MakeCompound'
- **Branch 18** @ line 617 — *multi_solid_with_open_mode* — **UNCOVERED**
  - What it tests: Shell result + myCreateOpenSolidMode in multi-solid path
  - Repair action: Wrap each shell in solid, add to compound
  - Suggested fixture: defect mentioning 'aResShape.ShapeType() == TopAbs_SHELL && myCreateOpenSolidMode', 'B.Add(solid, aResSh)'
- **Branch 19** @ line 626 — *multi_solid_open_shell_failure* — **UNCOVERED**
  - What it tests: Multi-solid result with open shell but mode disabled
  - Repair action: Report failure per problematic shell
  - Suggested fixture: defect mentioning 'aResShape.ShapeType() == TopAbs_SHELL', 'SendFail'
- **Branch 20** @ line 634 — *user_abort_in_solid_creation* — COVERED by: in014
  - What it tests: User interrupted progress during multi-solid construction
  - Repair action: Halt and return false

#### `ShapeFix_Solid.SolidFromShell` — lines 656–703
(4 branches, 0 covered.)

- **Branch 1** @ line 658 — *shell_free_flag_state* — **UNCOVERED**
  - What it tests: Shell Free() flag is false (shell is constrained)
  - Repair action: Set Free(true) to allow reorientation
  - Suggested fixture: defect mentioning '!sh.Free()', 'sh.Free(true)'
- **Branch 2** @ line 668 — *exception_in_classifier* — **UNCOVERED**
  - What it tests: BRepClass3d_SolidClassifier throws exception
  - Repair action: Catch exception and return solid as-is
  - Suggested fixture: defect mentioning 'catch (Standard_Failure const& anException)', 'return solid'
- **Branch 3** @ line 675 — *shell_orientation_inverted* — **UNCOVERED**
  - What it tests: Classifier returns IN state (shell has wrong orientation)
  - Repair action: Reverse shell and rebuild solid; mark DONE2
  - Suggested fixture: defect mentioning 'bsc3d.State() == TopAbs_IN', 'sh.Reverse()'
- **Branch 4** @ line 680 — *shell_free_flag_pre_reverse* — **UNCOVERED**
  - What it tests: Shell Free() is false before reversal
  - Repair action: Set Free(true) again before reversing
  - Suggested fixture: defect mentioning '!sh.Free()', 'sh.Free(true)'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Wire.cxx`

26 methods, 327 branches, 60 covered.

#### `ShapeFix_Wire.ClearModes` — lines 168–202
(8 branches, 4 covered.)

- **Branch 1** @ line 169 — *Mode initialization* — COVERED by: a071, a097, gn002, gn038, gs005, gs028, gs057, gs058 (+32 more)
  - What it tests: Default topology mode disabled
  - Repair action: Set myTopoMode = false
- **Branch 2** @ line 170 — *Mode initialization* — COVERED by: a017, a020, a023, a078, a089, ad064, ad084, ad086 (+51 more)
  - What it tests: Geometry analysis enabled by default
  - Repair action: Set myGeomMode = true
- **Branch 3** @ line 171 — *Mode initialization* — **UNCOVERED**
  - What it tests: Closed wire mode enabled
  - Repair action: Set myClosedMode = true
  - Suggested fixture: defect mentioning 'myClosedMode'
- **Branch 4** @ line 175 — *Mode initialization* — COVERED by: a014, a024, a098, ad001, ad003, ad031, ad038, ad046 (+127 more)
  - What it tests: Remove loop mode set to auto (no preference)
  - Repair action: Set myRemoveLoopMode = -1
- **Branch 5** @ line 177 — *Mode initialization* — **UNCOVERED**
  - What it tests: Reversed 2D curve mode auto
  - Repair action: Set myFixReversed2dMode = -1
  - Suggested fixture: defect mentioning 'myFixReversed2dMode'
- **Branch 6** @ line 178 — *Mode initialization* — **UNCOVERED**
  - What it tests: Remove PCurve mode auto
  - Repair action: Set myFixRemovePCurveMode = -1
  - Suggested fixture: defect mentioning 'myFixRemovePCurveMode'
- **Branch 7** @ line 191 — *Mode initialization* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1263 more)
  - What it tests: Tail fix mode disabled by default
  - Repair action: Set myFixTailMode = 0
- **Branch 8** @ line 193 — *Mode initialization* — **UNCOVERED**
  - What it tests: Reorder mode auto
  - Repair action: Set myFixReorderMode = -1
  - Suggested fixture: defect mentioning 'myFixReorderMode'

#### `ShapeFix_Wire.FixClosed` — lines 1305–1343
(4 branches, 0 covered.)

- **Branch 1** @ line 1307 — *missing-wire-or-empty* — **UNCOVERED**
  - What it tests: Wire not loaded or has no edges
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsLoaded() || NbEdges() < 1'
- **Branch 2** @ line 1312 — *open-closing-gap* — **UNCOVERED**
  - What it tests: Gap between end vertex of last edge and start of first edge
  - Repair action: FixConnected(1, prec) to bridge closure gap; update DONE1/FAIL1
  - Suggested fixture: defect mentioning 'FixConnected(1, prec)', 'LastFixStatus(ShapeExtend_DONE)'
- **Branch 3** @ line 1322 — *degenerate-closure-edge* — **UNCOVERED**
  - What it tests: Closure edge is degenerated (zero-length); remove/repair
  - Repair action: FixDegenerated(1); update DONE2/FAIL2
  - Suggested fixture: defect mentioning 'FixDegenerated(1)'
- **Branch 4** @ line 1332 — *missing-closure-edge* — **UNCOVERED**
  - What it tests: No edge at closure position or edge has gap
  - Repair action: FixLacking(1) to insert synthetic closure edge
  - Suggested fixture: defect mentioning 'FixLacking(1)'

#### `ShapeFix_Wire.FixConnected` — lines 558–596
(7 branches, 2 covered.)

- **Branch 1** @ line 560 — *Precondition check* — COVERED by: in014
  - What it tests: Wire not loaded
  - Repair action: Return false if not loaded
- **Branch 2** @ line 565 — *Closed vs open wire mode* — **UNCOVERED**
  - What it tests: Wire is closed (loop) or open
  - Repair action: Set loop stop = 0 (closed) or 1 (open)
  - Suggested fixture: defect mentioning 'myClosedMode', 'aStop'
- **Branch 3** @ line 567 — *Per-edge connectivity check* — COVERED by: ad086, twi003
  - What it tests: Each adjacent edge pair may be disconnected
  - Repair action: Call FixConnected(aI, prec, false) per pair
- **Branch 4** @ line 572 — *Context refresh needed* — **UNCOVERED**
  - What it tests: Previous edge modified by context, needs update
  - Repair action: Apply context to fetch updated edge
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'Context()->Apply'
- **Branch 5** @ line 576 — *Refresh validity check* — **UNCOVERED**
  - What it tests: Edge boundary wrap-around for closed wires
  - Repair action: Calculate N1Next = (aI-1 > 1) ? aI-2 : NbEdges
  - Suggested fixture: defect mentioning 'aN1Next', 'NbEdges'
- **Branch 6** @ line 583 — *Refreshed edge validity* — **UNCOVERED**
  - What it tests: Context apply returned valid refreshed edge
  - Repair action: Update wire with refreshed edge if valid
  - Suggested fixture: defect mentioning 'aRefresh.IsNull()', 'aWireSBWD->Set'
- **Branch 7** @ line 590 — *Context finalization* — **UNCOVERED**
  - What it tests: Context exists and connectivity changes applied
  - Repair action: UpdateWire() to commit context changes
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'UpdateWire'

#### `ShapeFix_Wire.FixConnected_int` — lines 1477–1611
(11 branches, 0 covered.)

- **Branch 1** @ line 1479 — *unloaded_or_no_edges* — **UNCOVERED**
  - What it tests: Wire not loaded or zero edges
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!IsLoaded()', 'NbEdges() <= 0'
- **Branch 2** @ line 1486 — *connection_check_fail* — **UNCOVERED**
  - What it tests: CheckConnected analysis returns FAIL status
  - Repair action: set FAIL1 status but continue
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 3** @ line 1490 — *no_connection_defect* — **UNCOVERED**
  - What it tests: No DONE status from analyzer
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 4** @ line 1507 — *disconnected_edges_absolute* — **UNCOVERED**
  - What it tests: DONE1 status: vertices are absolutely confused
  - Repair action: replace one vertex with other or same
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_DONE1)', 'V2.IsSame(sae.LastVertex(E2))'
- **Branch 5** @ line 1511 — *degenerate_edge_detection* — **UNCOVERED**
  - What it tests: Edge degenerates to single point
  - Repair action: use E2 endpoint for both vertices
  - Suggested fixture: defect mentioning 'V2.IsSame(sae.LastVertex(E2))'
- **Branch 6** @ line 1530 — *disconnected_edges_small_gap* — **UNCOVERED**
  - What it tests: DONE2: small gap exists
  - Repair action: combine vertices with tolerance factor
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_DONE2)'
- **Branch 7** @ line 1549 — *single_edge_rebuild_free* — **UNCOVERED**
  - What it tests: Single edge in wire and free
  - Repair action: modify edge to make self-loop with BRep_Builder
  - Suggested fixture: defect mentioning 'sbwd->NbEdges() < 2', 'E2.Free()', 'myTopoMode'
- **Branch 8** @ line 1561 — *single_edge_rebuild_shared* — **UNCOVERED**
  - What it tests: Single edge shared or not in topoMode
  - Repair action: create new edge with combined vertices
  - Suggested fixture: defect mentioning 'CopyReplaceVertices(E2, V, V)'
- **Branch 9** @ line 1571 — *multi_edge_both_free* — **UNCOVERED**
  - What it tests: Multiple edges and both free
  - Repair action: modify E2 start and optionally E1 end
  - Suggested fixture: defect mentioning 'E2.Free() && E1.Free() && myTopoMode'
- **Branch 10** @ line 1585 — *multi_edge_rebuild* — **UNCOVERED**
  - What it tests: Multiple edges and shared or not topoMode
  - Repair action: create new edges replacing vertices
  - Suggested fixture: defect mentioning 'CopyReplaceVertices(E2, V', 'CopyReplaceVertices(E1'
- **Branch 11** @ line 1605 — *wire_update* — **UNCOVERED**
  - What it tests: theUpdateWire flag and context available
  - Repair action: update wire from context replacements
  - Suggested fixture: defect mentioning 'theUpdateWire && !Context().IsNull()'

#### `ShapeFix_Wire.FixDegenerated` — lines 1035–1075
(3 branches, 1 covered.)

- **Branch 1** @ line 1037 — *missing-wire-data* — **UNCOVERED**
  - What it tests: Wire not loaded; gate check
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 1045 — *closed-vs-open-loop* — **UNCOVERED**
  - What it tests: Iterate over closed or open wire (different ranges)
  - Repair action: Set stop=0 for closed, 1 for open; iterate backwards
  - Suggested fixture: defect mentioning 'myClosedMode ? 0 : 1', 'for (int i = NbEdges()'
- **Branch 3** @ line 1051 — *degenerate-duplication* — COVERED by: m026, m109, os002, pmi053, sw003, tfa005, twi021, twi064 (+2 more)
  - What it tests: Multiple consecutive or cyclic degenerate edges (redundant)
  - Repair action: Remove duplicate degenerate edges; update prevcoded

#### `ShapeFix_Wire.FixDegenerated_int` — lines 2131–2204
(6 branches, 0 covered.)

- **Branch 1** @ line 2133 — *not_ready* — **UNCOVERED**
  - What it tests: Wire not ready
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 2141 — *degenerated_check_fail* — **UNCOVERED**
  - What it tests: CheckDegenerated analysis FAIL1 status
  - Repair action: set FAIL1 status but continue
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL1)'
- **Branch 3** @ line 2147 — *false_degenerated_edge* — **UNCOVERED**
  - What it tests: Edge marked degenerated but no singularity
  - Repair action: remove the spurious edge
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL2)', 'WireData()->Remove'
- **Branch 4** @ line 2153 — *no_degenerated_detected* — **UNCOVERED**
  - What it tests: No DONE status from analyzer
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 5** @ line 2175 — *degenerated_vertex_lack* — **UNCOVERED**
  - What it tests: Need to add new degenerated edge
  - Repair action: insert new edge at position
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_DONE1)', 'sbwd->Add(degEdge'
- **Branch 6** @ line 2188 — *degenerated_vertex_replace* — **UNCOVERED**
  - What it tests: Replace existing edge with degenerated
  - Repair action: replace edge at position
  - Suggested fixture: defect mentioning 'sbwd->Set(degEdge, n2)'

#### `ShapeFix_Wire.FixDummySeam` — lines 4214–4289
(12 branches, 0 covered.)

- **Branch 1** @ line 4218 — *calculate_adjacent_edges* — **UNCOVERED**
  - What it tests: wrap around wire boundary for adjacent edges
  - Repair action: set num1 to next edge (with wraparound)
  - Suggested fixture: defect mentioning 'num1 = (num == NbEdges()) ? 1 : num + 1'
- **Branch 2** @ line 4222 — *combine_vertices* — **UNCOVERED**
  - What it tests: merge vertices from seam edges
  - Repair action: create combined vertex with weighted tolerance
  - Suggested fixture: defect mentioning 'sbv.CombineVertex'
- **Branch 3** @ line 4231 — *vertex_overlap* — **UNCOVERED**
  - What it tests: seam start vertex same as either end
  - Repair action: use combined vertex as replacement
  - Suggested fixture: defect mentioning 'Vs.IsSame(V1)', 'Vs.IsSame(V2)'
- **Branch 4** @ line 4235 — *create_new_seam* — **UNCOVERED**
  - What it tests: replace seam edge with new orientation
  - Repair action: copy E2 with new vertices and reverse pcurves
  - Suggested fixture: defect mentioning 'CopyReplaceVertices', 'CopyReversePcurves'
- **Branch 5** @ line 4238 — *reset_range_flags* — **UNCOVERED**
  - What it tests: seam edge range and parameter flags
  - Repair action: reset SameRange/SameParameter
  - Suggested fixture: defect mentioning 'B.SameRange', 'B.SameParameter'
- **Branch 6** @ line 4241 — *context_replacement* — **UNCOVERED**
  - What it tests: context tracking enabled
  - Repair action: replace or remove edges based on toRemove flag
  - Suggested fixture: defect mentioning '!Context().IsNull()'
- **Branch 7** @ line 4243 — *remove_both_edges* — **UNCOVERED**
  - What it tests: old pcurves exist, remove seam
  - Repair action: remove both seam edges
  - Suggested fixture: defect mentioning 'toRemove', 'Context()->Remove'
- **Branch 8** @ line 4248 — *replace_seam_edges* — **UNCOVERED**
  - What it tests: no old pcurves, replace with new seam
  - Repair action: replace E2 and reverse E1
  - Suggested fixture: defect mentioning 'Context()->Replace(E2, newEdge)'
- **Branch 9** @ line 4257 — *update_adjacent_prev* — **UNCOVERED**
  - What it tests: update previous edge vertex
  - Repair action: replace previous edge with new vertex
  - Suggested fixture: defect mentioning 'sewd->Set(tmpE1, prev)'
- **Branch 10** @ line 4268 — *update_adjacent_next* — **UNCOVERED**
  - What it tests: update next edge vertex
  - Repair action: replace next edge with new vertex
  - Suggested fixture: defect mentioning 'sewd->Set(tmpE1, next)'
- **Branch 11** @ line 4277 — *edge_order_determination* — **UNCOVERED**
  - What it tests: determine n1 < n2 for removal
  - Repair action: sort edge indices
  - Suggested fixture: defect mentioning 'num < num1'
- **Branch 12** @ line 4287 — *remove_higher_index* — **UNCOVERED**
  - What it tests: remove higher index first
  - Repair action: remove n2 then n1
  - Suggested fixture: defect mentioning 'sewd->Remove(n2)', 'sewd->Remove(n1)'

#### `ShapeFix_Wire.FixEdgeCurves` — lines 601–1030
(12 branches, 9 covered.)

- **Branch 1** @ line 603 — *missing-wire-data* — **UNCOVERED**
  - What it tests: Wire data not loaded; gate check before processing
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsLoaded()'
- **Branch 2** @ line 619 — *reversed-2d-curves* — COVERED by: ad086, gs018, twi062
  - What it tests: 2D/3D curve orientations inconsistent when fix mode enabled
  - Repair action: FixReversed2d on each edge; update status DONE1/FAIL1
- **Branch 3** @ line 636 — *pcurve-removal-needed* — COVERED by: ad086
  - What it tests: Remove PCurve when parameterization is wrong
  - Repair action: FixRemovePCurve per edge; update DONE2/FAIL2
- **Branch 4** @ line 652 — *missing-pcurve* — COVERED by: ad086
  - What it tests: PCurve missing; attempt to reconstruct from 3D+surface
  - Repair action: FixAddPCurve with singularity check; split if over-pole
- **Branch 5** @ line 673 — *edge-crossing-singularity* — COVERED by: a004, a013, a014, a077, ad086, bo005, bo006, bo022 (+134 more)
  - What it tests: Edge 3D curve crosses surface singularity; split required
  - Repair action: Split edge at singularity points; recompute wire
- **Branch 6** @ line 830 — *degenerate-pole-over-uclosed* — COVERED by: n010
  - What it tests: Curve passes over U-closed pole; PCurve needs adjustment
  - Repair action: Remove PCurve and reproject with AdjustOverDegenMode=false
- **Branch 7** @ line 866 — *spurious-3d-curve* — COVERED by: twi046
  - What it tests: 3D curve present but pcurve provides better parameterization
  - Repair action: FixRemoveCurve3d per edge; update DONE4/FAIL4
- **Branch 8** @ line 881 — *missing-3d-curve* — COVERED by: twi047
  - What it tests: No 3D curve; cannot be derived from PCurve alone (no surface)
  - Repair action: FixAddCurve3d or remove edge if pcurve missing; update DONE5/FAIL5
- **Branch 9** @ line 922 — *seam-edge-parameterization* — **UNCOVERED**
  - What it tests: Seam edge needs special handling (split/merge on periodic surface)
  - Repair action: FixSeam per edge; update DONE6/FAIL6
  - Suggested fixture: defect mentioning 'FixSeamMode', 'FixSeam(i)'
- **Branch 10** @ line 939 — *shifted-curve* — **UNCOVERED**
  - What it tests: PCurve or 3D curve systematically offset from correct parameter
  - Repair action: FixShifted on full wire; update DONE7/FAIL7
  - Suggested fixture: defect mentioning 'FixShiftedMode', 'FixShifted()'
- **Branch 11** @ line 953 — *same-parameter-mismatch* — COVERED by: ad086
  - What it tests: SameRange property broken; 2D/3D param ranges differ
  - Repair action: Correct SameRange flag or recompute PCurve; FixSameParameter
- **Branch 12** @ line 1009 — *vertex-tolerance-inconsistency* — COVERED by: twi048, twi059, twi061
  - What it tests: Vertex tolerance too loose relative to edge endpoints
  - Repair action: FixVertexTolerance per edge; update context

#### `ShapeFix_Wire.FixIntersectingEdges (218 lines)` — lines 3272–3489
(24 branches, 2 covered.)

- **Branch 1** @ line 3274 — *uninitialized_wire* — COVERED by: in014
  - What it tests: Wire not ready for analysis
  - Repair action: reject_early_return
- **Branch 2** @ line 3282 — *null_analyzer* — **UNCOVERED**
  - What it tests: No shape analyzer available
  - Repair action: reject_early_return
  - Suggested fixture: defect mentioning 'theAdvAnalyzer.IsNull()'
- **Branch 3** @ line 3287 — *check_fail_status* — **UNCOVERED**
  - What it tests: Intersection check between two edges reported FAIL
  - Repair action: status_fail1
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 4** @ line 3291 — *check_done_status* — **UNCOVERED**
  - What it tests: No intersection found between edges
  - Repair action: reject_early_return
  - Suggested fixture: defect mentioning '!theAdvAnalyzer->LastCheckStatus(ShapeExtend_DONE)'
- **Branch 5** @ line 3304 — *same_edge_check* — **UNCOVERED**
  - What it tests: Two edge indices refer to the same edge
  - Repair action: reject_return_false
  - Suggested fixture: defect mentioning 'n1 == n2'
- **Branch 6** @ line 3337 — *vertex_selection_loop* — **UNCOVERED**
  - What it tests: Iterate through all 4 edge vertices for nearest
  - Repair action: nested_loop_distance_minimization
  - Suggested fixture: defect mentioning 'for (aVC1 = 1; aVC1 <= 2', 'for (aVC2 = 3; aVC2 <= 4'
- **Branch 7** @ line 3342 — *distance_and_coherence_check* — **UNCOVERED**
  - What it tests: Intersection point distance vs vertex-to-vertex coherence
  - Repair action: select_nearest_vertex_pair
  - Suggested fixture: defect mentioning 'aVtxIPDist > aVtxVtxDist'
- **Branch 8** @ line 3366 — *min_distance_below_resolution* — **UNCOVERED**
  - What it tests: Intersection point lies within vertex tolerance
  - Repair action: skip_continue
  - Suggested fixture: defect mentioning 'aMinDist < gp::Resolution()'
- **Branch 9** @ line 3372 — *curves_available* — **UNCOVERED**
  - What it tests: Both edges have valid 3D curves
  - Repair action: analyze_local_deviation
  - Suggested fixture: defect mentioning '!aCurve1.IsNull() && !aCurve2.IsNull()'
- **Branch 10** @ line 3380 — *points_sampling_loop* — **UNCOVERED**
  - What it tests: Sample 17 points along each edge near intersection
  - Repair action: compute_max_edge_tolerances
  - Suggested fixture: defect mentioning 'for (aPointsC = 2; aPointsC < 19'
- **Branch 11** @ line 3386 — *local_deviation_exceeds_tol1* — **UNCOVERED**
  - What it tests: Edge1 local deviation greater than current tolerance
  - Repair action: update_max_edge_tol1
  - Suggested fixture: defect mentioning 'd1 > tole1 && d1 > aMaxEdgeTol1'
- **Branch 12** @ line 3395 — *local_deviation_exceeds_tol2* — **UNCOVERED**
  - What it tests: Edge2 local deviation greater than current tolerance
  - Repair action: update_max_edge_tol2
  - Suggested fixture: defect mentioning 'd2 > tole2 && d2 > aMaxEdgeTol2'
- **Branch 13** @ line 3400 — *no_deviation_found* — **UNCOVERED**
  - What it tests: No significant local deviations detected
  - Repair action: skip_continue
  - Suggested fixture: defect mentioning 'aMaxEdgeTol1 == 0.0 && aMaxEdgeTol2 == 0.0'
- **Branch 14** @ line 3406 — *vertex_separation_sufficient* — **UNCOVERED**
  - What it tests: Vertices far enough to not need tolerance increase
  - Repair action: zero_computed_tolerances
  - Suggested fixture: defect mentioning 'aNecessaryVtxTole > std::max(aMaxEdgeTol1'
- **Branch 15** @ line 3417 — *find_nearest_vertex* — **UNCOVERED**
  - What it tests: Identify which of 4 vertices to increase tolerance on
  - Repair action: minimize_tolerance_selection
  - Suggested fixture: defect mentioning 'for (int j = 1; j <= 4', 'newtol < finTol'
- **Branch 16** @ line 3426 — *tolerance_within_limits* — **UNCOVERED**
  - What it tests: Final tolerance below maximum allowed
  - Repair action: status_done1_and_update_vertex
  - Suggested fixture: defect mentioning 'finTol <= MaxTolerance()'
- **Branch 17** @ line 3429 — *vertex_tolerance_improvement* — **UNCOVERED**
  - What it tests: New tolerance better than previous for this vertex
  - Repair action: conditional_edge_or_vertex_update
  - Suggested fixture: defect mentioning 'newTolers(rank) < finTol'
- **Branch 18** @ line 3431 — *edge_tolerance_better_choice* — **UNCOVERED**
  - What it tests: Edge tolerance increase is better than vertex tolerance
  - Repair action: set_new_edge_tolerances
  - Suggested fixture: defect mentioning 'std::max(aMaxEdgeTol1, aMaxEdgeTol2) < finTol'
- **Branch 19** @ line 3442 — *tolerance_exceeds_max* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Required tolerance exceeds maximum allowed
  - Repair action: status_fail2
- **Branch 20** @ line 3450 — *edge1_tolerance_update* — **UNCOVERED**
  - What it tests: Edge1 requires tolerance increase
  - Repair action: update_edge1_and_vertices
  - Suggested fixture: defect mentioning 'aNewTolEdge1 > 0'
- **Branch 21** @ line 3454 — *edge1_vertex_tolerance_comparison* — **UNCOVERED**
  - What it tests: Proposed edge tolerance vs vertex tolerance
  - Repair action: max_and_assign_vertex_tol
  - Suggested fixture: defect mentioning 'aNewTolEdge1 > std::max(vertexTolers(i)'
- **Branch 22** @ line 3461 — *edge2_tolerance_update* — **UNCOVERED**
  - What it tests: Edge2 requires tolerance increase
  - Repair action: update_edge2_and_vertices
  - Suggested fixture: defect mentioning 'aNewTolEdge2 > 0'
- **Branch 23** @ line 3465 — *edge2_vertex_tolerance_comparison* — **UNCOVERED**
  - What it tests: Proposed edge2 tolerance vs vertex tolerance
  - Repair action: max_and_assign_vertex_tol
  - Suggested fixture: defect mentioning 'aNewTolEdge2 > std::max(vertexTolers(i)'
- **Branch 24** @ line 3474 — *vertex_tolerance_final_update* — **UNCOVERED**
  - What it tests: Apply calculated tolerance to each vertex
  - Repair action: update_all_vertices
  - Suggested fixture: defect mentioning 'for (i = 1; i <= 4', 'B.UpdateVertex'

#### `ShapeFix_Wire.FixIntersectingEdges (299 lines)` — lines 2967–3265
(30 branches, 5 covered.)

- **Branch 1** @ line 2969 — *uninitialized_wire_or_insufficient_edges* — COVERED by: in014
  - What it tests: Wire not ready or has fewer than 2 edges
  - Repair action: reject_early_return
- **Branch 2** @ line 2979 — *null_analyzer* — **UNCOVERED**
  - What it tests: No shape analyzer available
  - Repair action: reject_early_return
  - Suggested fixture: defect mentioning 'theAdvAnalyzer.IsNull()'
- **Branch 3** @ line 2984 — *check_fail_status* — **UNCOVERED**
  - What it tests: Intersection check reported FAIL
  - Repair action: status_fail1
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 4** @ line 2988 — *check_done_status* — **UNCOVERED**
  - What it tests: No intersection found (DONE not set)
  - Repair action: reject_early_return
  - Suggested fixture: defect mentioning '!theAdvAnalyzer->LastCheckStatus(ShapeExtend_DONE)'
- **Branch 5** @ line 3003 — *context_presence* — **UNCOVERED**
  - What it tests: Transformation context available
  - Repair action: apply_context_transform
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Apply'
- **Branch 6** @ line 3040 — *intersection_point_ordering* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Intersection point is farther from endpoints than previous
  - Repair action: skip_continue
- **Branch 7** @ line 3055 — *tolerance_increase_candidate* — **UNCOVERED**
  - What it tests: Edge tolerance increase preferable over topological edit
  - Repair action: attempt_tolerance_increase_with_local_deviation
  - Suggested fixture: defect mentioning 'newtol > tol', 'ComputeLocalDeviation'
- **Branch 8** @ line 3062 — *local_deviation_acceptable* — **UNCOVERED**
  - What it tests: Local deviation tolerances within limits
  - Repair action: update_edge_tolerances
  - Suggested fixture: defect mentioning 'maxte < MaxTolerance() && maxte < newtol'
- **Branch 9** @ line 3064 — *edge_tolerance_modification_needed* — **UNCOVERED**
  - What it tests: One or both edges need tolerance increase
  - Repair action: copy_and_update_edges
  - Suggested fixture: defect mentioning 'BRep_Tool::Tolerance(E1) < te1 || BRep_Tool::Tolerance(E2) < te2'
- **Branch 10** @ line 3072 — *context_edge_copy* — **UNCOVERED**
  - What it tests: Copy edges through context for modification
  - Repair action: copy_vertices_and_edges
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'CopyReplaceVertices'
- **Branch 11** @ line 3082 — *shared_start_end_vertex* — **UNCOVERED**
  - What it tests: Edge pair shares same start/end vertex
  - Repair action: copy_single_vertex
  - Suggested fixture: defect mentioning 'Vp.IsSame(Vn)'
- **Branch 12** @ line 3109 — *update_edge_and_vertices* — **UNCOVERED**
  - What it tests: Set new tolerance on edges and vertices
  - Repair action: brepbuilder_update
  - Suggested fixture: defect mentioning 'B.UpdateEdge(E1, 1.000001 * te1)'
- **Branch 13** @ line 3116 — *tolerance_update_success* — **UNCOVERED**
  - What it tests: Tolerance increase completed
  - Repair action: status_done6
  - Suggested fixture: defect mentioning 'myLastFixStatus |= ShapeExtend::EncodeStatus(ShapeExtend_DONE6)'
- **Branch 14** @ line 3123 — *may_edit_or_tolerance_acceptable* — **UNCOVERED**
  - What it tests: Topology edit allowed OR new tolerance acceptable
  - Repair action: branch_to_edit_or_increase
  - Suggested fixture: defect mentioning 'locMayEdit || newtol <= MaxTolerance()'
- **Branch 15** @ line 3127 — *topology_edit_enabled* — **UNCOVERED**
  - What it tests: Attempt edge cutting and splitting
  - Repair action: attempt_edge_cut
  - Suggested fixture: defect mentioning 'locMayEdit', 'aTool.CutEdge'
- **Branch 16** @ line 3134 — *edge1_cut_result* — **UNCOVERED**
  - What it tests: Edge1 cut succeeded or matched vertex
  - Repair action: conditional_set_done3
  - Suggested fixture: defect mentioning '!aTool.CutEdge(E1', 'V1.IsSame(Vp)'
- **Branch 17** @ line 3142 — *edge1_cut_fail* — **UNCOVERED**
  - What it tests: Edge1 cut failed and vertices do not match
  - Repair action: disable_topology_edit
  - Suggested fixture: defect mentioning 'locMayEdit = false'
- **Branch 18** @ line 3147 — *edge1_cut_success* — **UNCOVERED**
  - What it tests: Edge1 successfully cut
  - Repair action: flag_cut_edge1
  - Suggested fixture: defect mentioning 'cutEdge1 = true'
- **Branch 19** @ line 3150 — *edge2_cut_result* — **UNCOVERED**
  - What it tests: Edge2 cut succeeded or matched vertex
  - Repair action: conditional_set_done4
  - Suggested fixture: defect mentioning '!aTool.CutEdge(E2', 'V2.IsSame(Vn)'
- **Branch 20** @ line 3167 — *range_check_and_same_parameter* — **UNCOVERED**
  - What it tests: Intersection closer and both edges have same parameter
  - Repair action: set_done2_and_update_vertex
  - Suggested fixture: defect mentioning 'newRange1 <= prevRange1 && newRange2 <= prevRange2', 'BRep_Tool::SameParameter'
- **Branch 21** @ line 3172 — *rad_less_than_tol* — **UNCOVERED**
  - What it tests: Intersection radius smaller than current tolerance
  - Repair action: increase_tolerance_to_radius
  - Suggested fixture: defect mentioning 'tol <= rad'
- **Branch 22** @ line 3180 — *cut_line_handling* — **UNCOVERED**
  - What it tests: Cut was performed on planar/linear geometry
  - Repair action: set_done2_update_tol
  - Suggested fixture: defect mentioning 'IsCutLine'
- **Branch 23** @ line 3192 — *no_cut_line_increase_tol* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: No cut performed, must increase tolerance
  - Repair action: increase_tolerance
- **Branch 24** @ line 3202 — *tolerance_exceeds_max* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Required tolerance exceeds maximum allowed
  - Repair action: status_fail2
- **Branch 25** @ line 3206 — *no_fix_achieved* — COVERED by: in014
  - What it tests: No successful repair action taken
  - Repair action: reject_return_false
- **Branch 26** @ line 3211 — *context_vertex_update* — **UNCOVERED**
  - What it tests: Context available, apply vertex updates
  - Repair action: context_copy_vertices
  - Suggested fixture: defect mentioning 'isChangedEdge', 'Context()->CopyVertex'
- **Branch 27** @ line 3220 — *same_vertex_update* — **UNCOVERED**
  - What it tests: Both edges share the same vertex
  - Repair action: update_single_vertex
  - Suggested fixture: defect mentioning 'V1.IsSame(V2)'
- **Branch 28** @ line 3238 — *edge_cut_same_parameter* — **UNCOVERED**
  - What it tests: Edge1 was cut, apply same-parameter fix
  - Repair action: fix_same_parameter_e1
  - Suggested fixture: defect mentioning 'cutEdge1', 'myFixEdge->FixSameParameter'
- **Branch 29** @ line 3246 — *edge2_cut_and_not_cutline* — **UNCOVERED**
  - What it tests: Edge2 cut but not a simple cut line
  - Repair action: fix_same_parameter_e2
  - Suggested fixture: defect mentioning 'cutEdge2 && !IsCutLine'
- **Branch 30** @ line 3254 — *either_edge_cut* — **UNCOVERED**
  - What it tests: One or both edges were cut
  - Repair action: status_done7
  - Suggested fixture: defect mentioning 'cutEdge1 || cutEdge2', 'EncodeStatus(ShapeExtend_DONE7)'

#### `ShapeFix_Wire.FixIntersectingEdges(const int num)` — lines 2967–3265
(24 branches, 2 covered.)

- **Branch 1** @ line 2969 — *not_ready* — **UNCOVERED**
  - What it tests: wire not ready or < 2 edges
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()', 'NbEdges() < 2'
- **Branch 2** @ line 2984 — *check_failed* — **UNCOVERED**
  - What it tests: intersection analysis failed
  - Repair action: encode FAIL1 status
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 3** @ line 2988 — *analysis_incomplete* — **UNCOVERED**
  - What it tests: no intersection detected
  - Repair action: return false
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 4** @ line 3040 — *skip_redundant_intersection* — **UNCOVERED**
  - What it tests: intersection point further than previous
  - Repair action: continue to next point
  - Suggested fixture: defect mentioning 'newRange1 > prevRange1', 'newRange2 > prevRange2'
- **Branch 5** @ line 3055 — *try_edge_tolerance* — COVERED by: gs037, twi041
  - What it tests: deviation acceptable by edge tolerance
  - Repair action: update edge/vertex tolerances
- **Branch 6** @ line 3062 — *tolerance_within_max* — **UNCOVERED**
  - What it tests: tolerance acceptable vs MaxTolerance
  - Repair action: increase edge tolerance, encode DONE6
  - Suggested fixture: defect mentioning 'maxte < MaxTolerance()'
- **Branch 7** @ line 3072 — *context_enabled* — **UNCOVERED**
  - What it tests: context not null for edge copying
  - Repair action: copy edges and vertices
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'CopyVertex', 'CopyReplaceVertices'
- **Branch 8** @ line 3082 — *seam_edge* — **UNCOVERED**
  - What it tests: vertex appears on both edges (seam)
  - Repair action: copy vertex once and reuse
  - Suggested fixture: defect mentioning 'Vp.IsSame(Vn)'
- **Branch 9** @ line 3123 — *topo_mode_or_tolerance* — **UNCOVERED**
  - What it tests: topo mode enabled or tolerance acceptable
  - Repair action: attempt edge cutting
  - Suggested fixture: defect mentioning 'locMayEdit', 'MaxTolerance()'
- **Branch 10** @ line 3127 — *try_edge_cutting* — **UNCOVERED**
  - What it tests: topological mode enabled
  - Repair action: cut edge at intersection point
  - Suggested fixture: defect mentioning 'aTool.CutEdge', 'IsCutLine'
- **Branch 11** @ line 3134 — *cut_edge1_failed* — **UNCOVERED**
  - What it tests: edge1 cut failed
  - Repair action: check if at vertex boundary, set DONE3
  - Suggested fixture: defect mentioning '!aTool.CutEdge(E1'
- **Branch 12** @ line 3136 — *edge1_coincident_vertex* — **UNCOVERED**
  - What it tests: cut point at V1/Vp boundary
  - Repair action: encode DONE3, allow tolerance increase
  - Suggested fixture: defect mentioning 'V1.IsSame(Vp)'
- **Branch 13** @ line 3150 — *cut_edge2_failed* — **UNCOVERED**
  - What it tests: edge2 cut failed
  - Repair action: check if at vertex boundary, set DONE4
  - Suggested fixture: defect mentioning '!aTool.CutEdge(E2'
- **Branch 14** @ line 3152 — *edge2_coincident_vertex* — **UNCOVERED**
  - What it tests: cut point at V2/Vn boundary
  - Repair action: encode DONE4, allow tolerance increase
  - Suggested fixture: defect mentioning 'V2.IsSame(Vn)'
- **Branch 15** @ line 3167 — *same_parameter_edges* — **UNCOVERED**
  - What it tests: both edges have SameParameter property
  - Repair action: relocate vertex to intersection point, encode DONE2
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter'
- **Branch 16** @ line 3172 — *update_vertex_tolerance* — **UNCOVERED**
  - What it tests: intersection error larger than vertex tolerance
  - Repair action: increase vertex tolerance, encode DONE1
  - Suggested fixture: defect mentioning 'tol <= rad'
- **Branch 17** @ line 3180 — *cutline_approach* — **UNCOVERED**
  - What it tests: cutline approach taken for intersection
  - Repair action: relocate vertex to intersection, encode DONE2
  - Suggested fixture: defect mentioning 'IsCutLine'
- **Branch 18** @ line 3192 — *tolerance_increase_fallback* — **UNCOVERED**
  - What it tests: tolerance increase fallback after no other fix
  - Repair action: increase vertex tolerance, encode DONE1
  - Suggested fixture: defect mentioning 'tol < newtol'
- **Branch 19** @ line 3202 — *tolerance_exceeds_max* — COVERED by: twi066
  - What it tests: tolerance exceeds MaxTolerance
  - Repair action: encode FAIL2
- **Branch 20** @ line 3206 — *no_fix_applied* — **UNCOVERED**
  - What it tests: no repair status set
  - Repair action: return false
  - Suggested fixture: defect mentioning '!LastFixStatus(ShapeExtend_DONE)'
- **Branch 21** @ line 3220 — *vertices_coincident* — **UNCOVERED**
  - What it tests: edge vertices are the same
  - Repair action: copy single vertex once
  - Suggested fixture: defect mentioning 'V1.IsSame(V2)'
- **Branch 22** @ line 3238 — *post_cut_same_parameter* — **UNCOVERED**
  - What it tests: edges were cut, need SameParameter fix
  - Repair action: call FixSameParameter
  - Suggested fixture: defect mentioning 'cutEdge1', 'myFixEdge->FixSameParameter'
- **Branch 23** @ line 3246 — *post_cut_edge2_not_cutline* — **UNCOVERED**
  - What it tests: edge2 cut but not via cutline
  - Repair action: apply SameParameter fix to edge2
  - Suggested fixture: defect mentioning 'cutEdge2 && !IsCutLine'
- **Branch 24** @ line 3254 — *cuts_applied* — **UNCOVERED**
  - What it tests: either edge was cut
  - Repair action: encode DONE7
  - Suggested fixture: defect mentioning 'cutEdge1 || cutEdge2'

#### `ShapeFix_Wire.FixIntersectingEdges(const int num1, const int num2)` — lines 3272–3489
(20 branches, 1 covered.)

- **Branch 1** @ line 3274 — *not_ready* — **UNCOVERED**
  - What it tests: wire not ready
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 3287 — *check_failed* — **UNCOVERED**
  - What it tests: intersection analysis failed
  - Repair action: encode FAIL1
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 3** @ line 3291 — *analysis_incomplete* — **UNCOVERED**
  - What it tests: no intersection found
  - Repair action: return false
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 4** @ line 3304 — *same_edge* — **UNCOVERED**
  - What it tests: n1 equals n2
  - Repair action: return false
  - Suggested fixture: defect mentioning 'n1 == n2'
- **Branch 5** @ line 3337 — *vertex_to_intersection_distance* — **UNCOVERED**
  - What it tests: find nearest vertex to intersection
  - Repair action: calculate minimum distance and necessary tolerance
  - Suggested fixture: defect mentioning 'aVtxIPDist', 'aMinDist'
- **Branch 6** @ line 3344 — *intersection_at_vertex* — **UNCOVERED**
  - What it tests: intersection IP closer than vertex distance
  - Repair action: use vertex as reference point
  - Suggested fixture: defect mentioning 'aMinDist > aVtxIPDist', 'aVtxIPDist > aVtxVtxDist'
- **Branch 7** @ line 3366 — *ip_within_resolution* — **UNCOVERED**
  - What it tests: intersection point inside vertex resolution
  - Repair action: skip intersection point
  - Suggested fixture: defect mentioning 'aMinDist < gp::Resolution()'
- **Branch 8** @ line 3372 — *calculate_edge_tolerance* — **UNCOVERED**
  - What it tests: curves available for tolerance calculation
  - Repair action: sample curve points and calculate max deviation
  - Suggested fixture: defect mentioning '!aCurve1.IsNull()', '!aCurve2.IsNull()'
- **Branch 9** @ line 3380 — *sample_curve_points* — **UNCOVERED**
  - What it tests: sample points along curves
  - Repair action: calculate distance to line through vertices
  - Suggested fixture: defect mentioning 'aPointsC', 'aLig.Distance'
- **Branch 10** @ line 3386 — *tolerance_exceeds_edge* — **UNCOVERED**
  - What it tests: deviation d1 exceeds edge tolerance
  - Repair action: update aMaxEdgeTol1
  - Suggested fixture: defect mentioning 'd1 > tole1'
- **Branch 11** @ line 3395 — *tolerance_exceeds_edge2* — **UNCOVERED**
  - What it tests: deviation d2 exceeds edge tolerance
  - Repair action: update aMaxEdgeTol2
  - Suggested fixture: defect mentioning 'd2 > tole2'
- **Branch 12** @ line 3400 — *no_tolerance_needed* — **UNCOVERED**
  - What it tests: both tolerance values remain zero
  - Repair action: skip intersection point
  - Suggested fixture: defect mentioning 'aMaxEdgeTol1 == 0.0', 'aMaxEdgeTol2 == 0.0'
- **Branch 13** @ line 3406 — *vertex_separation_sufficient* — **UNCOVERED**
  - What it tests: vertex distance larger than required tolerance
  - Repair action: clear tolerance updates
  - Suggested fixture: defect mentioning 'aNecessaryVtxTole >'
- **Branch 14** @ line 3417 — *find_nearest_vertex* — **UNCOVERED**
  - What it tests: find which vertex is closest to intersection
  - Repair action: select rank with minimum tolerance
  - Suggested fixture: defect mentioning 'for (int j = 1; j <= 4; j++)'
- **Branch 15** @ line 3426 — *tolerance_within_max* — **UNCOVERED**
  - What it tests: final tolerance <= MaxTolerance
  - Repair action: encode DONE1, update vertex tolerance
  - Suggested fixture: defect mentioning 'finTol <= MaxTolerance()'
- **Branch 16** @ line 3431 — *edge_tolerance_approach* — **UNCOVERED**
  - What it tests: edge tolerance strategy valid
  - Repair action: update edge tolerances instead of vertex
  - Suggested fixture: defect mentioning 'aMaxEdgeTol1', 'aMaxEdgeTol2'
- **Branch 17** @ line 3444 — *tolerance_exceeds_max* — COVERED by: twi066
  - What it tests: tolerance exceeds MaxTolerance
  - Repair action: encode FAIL2
- **Branch 18** @ line 3450 — *apply_edge1_tolerance* — **UNCOVERED**
  - What it tests: edge1 tolerance update needed
  - Repair action: update edge1 and its vertices
  - Suggested fixture: defect mentioning 'aNewTolEdge1 > 0'
- **Branch 19** @ line 3461 — *apply_edge2_tolerance* — **UNCOVERED**
  - What it tests: edge2 tolerance update needed
  - Repair action: update edge2 and its vertices
  - Suggested fixture: defect mentioning 'aNewTolEdge2 > 0'
- **Branch 20** @ line 3476 — *apply_vertex_tolerance* — **UNCOVERED**
  - What it tests: vertex tolerance update needed
  - Repair action: update vertex tolerance
  - Suggested fixture: defect mentioning 'newTolers(i) > 0'

#### `ShapeFix_Wire.FixLacking` — lines 1285–1300
(3 branches, 0 covered.)

- **Branch 1** @ line 1287 — *missing-wire-data* — **UNCOVERED**
  - What it tests: Wire not loaded; gate check
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 1292 — *closed-vs-open-edge-start* — **UNCOVERED**
  - What it tests: Closed loop starts at edge 1; open at edge 2
  - Repair action: Set start = (myClosedMode ? 1 : 2)
  - Suggested fixture: defect mentioning 'myClosedMode ? 1 : 2'
- **Branch 3** @ line 1295 — *missing-connection-edge* — **UNCOVERED**
  - What it tests: Gap between consecutive edges; insert filler edge
  - Repair action: FixLacking(i, force) per edge; may add or remove
  - Suggested fixture: defect mentioning 'FixLacking(i, force)', 'myStatusLacking |= myLastFixStatus'

#### `ShapeFix_Wire.FixLacking(const bool force)` — lines 1285–1300
(2 branches, 0 covered.)

- **Branch 1** @ line 1287 — *not_ready* — **UNCOVERED**
  - What it tests: wire not ready
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 1292 — *closed_mode* — **UNCOVERED**
  - What it tests: wire in closed mode
  - Repair action: iterate from edge 1; otherwise from edge 2
  - Suggested fixture: defect mentioning 'myClosedMode'

#### `ShapeFix_Wire.FixLacking(const int num, const bool force)` — lines 3618–3973
(35 branches, 1 covered.)

- **Branch 1** @ line 3620 — *not_ready* — **UNCOVERED**
  - What it tests: wire not ready
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 3629 — *check_failed* — **UNCOVERED**
  - What it tests: gap analysis failed
  - Repair action: encode FAIL1
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 3** @ line 3633 — *no_gap_detected* — **UNCOVERED**
  - What it tests: no gap found between edges
  - Repair action: return false
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 4** @ line 3667 — *try_bending* — **UNCOVERED**
  - What it tests: geom mode + non-closed edges
  - Repair action: attempt pcurve bending at gap midpoint
  - Suggested fixture: defect mentioning 'myGeomMode', '!BRep_Tool::IsClosed'
- **Branch 5** @ line 3686 — *bending_asymmetric_ok1_fail2* — **UNCOVERED**
  - What it tests: bend ok on E1 but not E2
  - Repair action: retry with p2d2 endpoint
  - Suggested fixture: defect mentioning 'ok1 && !ok2'
- **Branch 6** @ line 3698 — *bending_asymmetric_fail1_ok2* — **UNCOVERED**
  - What it tests: bend ok on E2 but not E1
  - Repair action: retry with p2d1 endpoint
  - Suggested fixture: defect mentioning '!ok1 && ok2'
- **Branch 7** @ line 3710 — *bending_both_fail* — **UNCOVERED**
  - What it tests: bending fails on both edges
  - Repair action: nullify bending curve, try other fixes
  - Suggested fixture: defect mentioning '!ok1 && !ok2'
- **Branch 8** @ line 3727 — *bending_solution_ok* — **UNCOVERED**
  - What it tests: bend curves exist and tolerances acceptable
  - Repair action: select doBend flag
  - Suggested fixture: defect mentioning '!bendc1.IsNull()', '!bendc2.IsNull()'
- **Branch 9** @ line 3735 — *tolerance_increase_acceptable* — **UNCOVERED**
  - What it tests: gap can be closed by tolerance increase
  - Repair action: select doIncrease flag
  - Suggested fixture: defect mentioning 'inctol < Prec'
- **Branch 10** @ line 3741 — *non_degenerated_edges* — **UNCOVERED**
  - What it tests: both edges non-degenerated
  - Repair action: explore topological solutions
  - Suggested fixture: defect mentioning '!BRep_Tool::Degenerated'
- **Branch 11** @ line 3745 — *topo_mode_add_long* — **UNCOVERED**
  - What it tests: topological mode for long edge addition
  - Repair action: calculate 3d endpoints and analyze distance
  - Suggested fixture: defect mentioning 'myTopoMode'
- **Branch 12** @ line 3749 — *cannot_get_curve3d_e1* — **UNCOVERED**
  - What it tests: E1 3d curve extraction failed
  - Repair action: encode FAIL1, return false
  - Suggested fixture: defect mentioning '!sae.Curve3d(E1'
- **Branch 13** @ line 3756 — *cannot_get_curve3d_e2* — **UNCOVERED**
  - What it tests: E2 3d curve extraction failed
  - Repair action: encode FAIL1, return false
  - Suggested fixture: defect mentioning '!sae.Curve3d(E2'
- **Branch 14** @ line 3773 — *zigzag_avoidance* — **UNCOVERED**
  - What it tests: 3d gap large enough and not backward
  - Repair action: allow doAddLong if distance > 1.25*tol0^2
  - Suggested fixture: defect mentioning '!myAnalyzer->LastCheckStatus(ShapeExtend_DONE2)'
- **Branch 15** @ line 3774 — *force_or_large_gap* — **UNCOVERED**
  - What it tests: force flag or gap exceeds precision or tolerance
  - Repair action: enable doAddLong
  - Suggested fixture: defect mentioning 'force || dist3d2 > Prec * Prec'
- **Branch 16** @ line 3781 — *tolerance_increase_to_max* — **UNCOVERED**
  - What it tests: gap fits within MaxTolerance
  - Repair action: increase tolerance or try bending
  - Suggested fixture: defect mentioning 'inctol < MaxTolerance()'
- **Branch 17** @ line 3782 — *surface_not_degenerated* — **UNCOVERED**
  - What it tests: surface not degenerated at gap
  - Repair action: allow tolerance increase without adding edge
  - Suggested fixture: defect mentioning '!myAnalyzer->Surface()->IsDegenerated'
- **Branch 18** @ line 3784 — *bending_within_gap* — **UNCOVERED**
  - What it tests: bending solution within inctol
  - Repair action: select doBend flag
  - Suggested fixture: defect mentioning 'bendtol1 < inctol', 'bendtol2 < inctol'
- **Branch 19** @ line 3796 — *add_edge_selection* — **UNCOVERED**
  - What it tests: decide edge type to add
  - Repair action: select doAddDegen or doAddClosed
  - Suggested fixture: defect mentioning '!doAddLong'
- **Branch 20** @ line 3802 — *midpoint_on_surface* — **UNCOVERED**
  - What it tests: gap midpoint within edge tolerance
  - Repair action: select doAddDegen flag
  - Suggested fixture: defect mentioning 'dist <= tol'
- **Branch 21** @ line 3806 — *add_closed_edge* — **UNCOVERED**
  - What it tests: topological mode + midpoint off surface
  - Repair action: select doAddClosed flag
  - Suggested fixture: defect mentioning 'myTopoMode', 'doAddClosed'
- **Branch 22** @ line 3810 — *degenerated_within_max_tolerance* — **UNCOVERED**
  - What it tests: gap within MaxTolerance
  - Repair action: select doAddDegen + doIncrease
  - Suggested fixture: defect mentioning 'dist <= MaxTolerance()'
- **Branch 23** @ line 3833 — *add_new_edge* — **UNCOVERED**
  - What it tests: any add-edge solution selected
  - Repair action: construct and insert new edge
  - Suggested fixture: defect mentioning 'doAddLong || doAddDegen || doAddClosed'
- **Branch 24** @ line 3838 — *add_long_vertices* — **UNCOVERED**
  - What it tests: long edge with 3d endpoints
  - Repair action: create new vertices at curve endpoints
  - Suggested fixture: defect mentioning 'doAddLong'
- **Branch 25** @ line 3855 — *add_degenerated_edge* — **UNCOVERED**
  - What it tests: mark edge as degenerated
  - Repair action: flag edge degenerated before adding curve
  - Suggested fixture: defect mentioning 'doAddDegen', 'B.Degenerated'
- **Branch 26** @ line 3866 — *build_3d_curve* — **UNCOVERED**
  - What it tests: non-degenerated edge needs 3d curve
  - Repair action: build 3d curve or fail
  - Suggested fixture: defect mentioning '!doAddDegen && !sbe.BuildCurve3d'
- **Branch 27** @ line 3873 — *replace_long_vertices* — **UNCOVERED**
  - What it tests: long edge requires vertex replacement
  - Repair action: replace vertices in adjacent edges
  - Suggested fixture: defect mentioning 'doAddLong'
- **Branch 28** @ line 3877 — *single_edge_wire* — **UNCOVERED**
  - What it tests: n1 == n2 (single edge wire)
  - Repair action: replace both vertices of single edge
  - Suggested fixture: defect mentioning 'n1 == n2'
- **Branch 29** @ line 3892 — *two_edge_wire* — **UNCOVERED**
  - What it tests: n1 != n2 (separate edges)
  - Repair action: replace vertices of both edges
  - Suggested fixture: defect mentioning 'n1 != n2'
- **Branch 30** @ line 3908 — *degen_edge_added* — **UNCOVERED**
  - What it tests: degenerated edge inserted
  - Repair action: encode DONE3
  - Suggested fixture: defect mentioning 'doAddDegen'
- **Branch 31** @ line 3924 — *secondary_tolerance_increase* — **UNCOVERED**
  - What it tests: gap within increased tolerance range
  - Repair action: retry bending or tolerance increase
  - Suggested fixture: defect mentioning 'inctol > tol', 'inctol < MaxTolerance()'
- **Branch 32** @ line 3937 — *bend_pcurves* — **UNCOVERED**
  - What it tests: bend solution selected
  - Repair action: update edges with bent pcurves
  - Suggested fixture: defect mentioning 'doBend'
- **Branch 33** @ line 3949 — *self_intersection_after_bend* — COVERED by: ad086
  - What it tests: bent edges need self-intersection check
  - Repair action: call FixSelfIntersectingEdge
- **Branch 34** @ line 3959 — *increase_vertex_tolerance* — **UNCOVERED**
  - What it tests: tolerance increase selected
  - Repair action: update vertices between edges
  - Suggested fixture: defect mentioning 'doIncrease'
- **Branch 35** @ line 3966 — *no_fix_applied* — **UNCOVERED**
  - What it tests: no repair action taken
  - Repair action: return false with FAIL2
  - Suggested fixture: defect mentioning '!LastFixStatus(ShapeExtend_DONE)'

#### `ShapeFix_Wire.FixNotchedEdges` — lines 3978–4104
(22 branches, 1 covered.)

- **Branch 1** @ line 3980 — *not_ready* — **UNCOVERED**
  - What it tests: wire not ready
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 3993 — *minimum_edge_count* — **UNCOVERED**
  - What it tests: wire has > 2 edges
  - Repair action: process notches only in multi-edge wires
  - Suggested fixture: defect mentioning 'NbEdges() > 2'
- **Branch 3** @ line 3997 — *notch_detected* — COVERED by: twi074
  - What it tests: notch found at edge boundary
  - Repair action: extract notch parameters
- **Branch 4** @ line 4001 — *identify_edges* — **UNCOVERED**
  - What it tests: determine which edge to remove/split
  - Repair action: calculate n1, n2, and removal target
  - Suggested fixture: defect mentioning 'toRemove', 'isRemoveFirst'
- **Branch 5** @ line 4014 — *notch_at_endpoint* — **UNCOVERED**
  - What it tests: split point at edge endpoint
  - Repair action: remove entire edge via FixDummySeam
  - Suggested fixture: defect mentioning 'std::abs(param - (isRemoveFirst ? b : a))'
- **Branch 6** @ line 4015 — *closed_edge_notch* — **UNCOVERED**
  - What it tests: notch on closed 3d edge at opposite end
  - Repair action: remove entire closed edge via FixDummySeam
  - Suggested fixture: defect mentioning 'sae.IsClosed3d(splitE)'
- **Branch 7** @ line 4026 — *negligible_split* — **UNCOVERED**
  - What it tests: split parameter at or very near edge start
  - Repair action: skip this iteration
  - Suggested fixture: defect mentioning 'std::abs((isRemoveFirst ? a : b) - param)'
- **Branch 8** @ line 4034 — *split_and_add* — **UNCOVERED**
  - What it tests: notch requires edge splitting
  - Repair action: split edge into two, insert second
  - Suggested fixture: defect mentioning 'TransferRange'
- **Branch 9** @ line 4036 — *parameter_order* — **UNCOVERED**
  - What it tests: determine first < last for parameter range
  - Repair action: set first and last correctly
  - Suggested fixture: defect mentioning 'a < b'
- **Branch 10** @ line 4047 — *create_split_vertex* — **UNCOVERED**
  - What it tests: create new vertex at split point
  - Repair action: make vertex from surface evaluation
  - Suggested fixture: defect mentioning 'BRepBuilderAPI_MakeVertex'
- **Branch 11** @ line 4052 — *edge_orientation* — **UNCOVERED**
  - What it tests: ensure forward orientation for processing
  - Repair action: set edge to FORWARD
  - Suggested fixture: defect mentioning 'wE.Orientation(TopAbs_FORWARD)'
- **Branch 12** @ line 4054 — *split_first_segment* — **UNCOVERED**
  - What it tests: create first part of split edge
  - Repair action: copy edge from start to split vertex
  - Suggested fixture: defect mentioning 'CopyReplaceVertices(wE, sae.FirstVertex'
- **Branch 13** @ line 4057 — *transfer_first_range* — **UNCOVERED**
  - What it tests: transfer parameter range for first segment
  - Repair action: project parameters onto first segment
  - Suggested fixture: defect mentioning 'TransferRange(newE1'
- **Branch 14** @ line 4058 — *same_range_same_param* — **UNCOVERED**
  - What it tests: reset range and parameter flags
  - Repair action: mark edge as not SameRange/SameParameter
  - Suggested fixture: defect mentioning 'B.SameRange', 'B.SameParameter'
- **Branch 15** @ line 4061 — *split_second_segment* — **UNCOVERED**
  - What it tests: create second part of split edge
  - Repair action: copy edge from split vertex to end
  - Suggested fixture: defect mentioning 'CopyReplaceVertices(wE', 'sae.LastVertex'
- **Branch 16** @ line 4064 — *transfer_second_range* — **UNCOVERED**
  - What it tests: transfer parameter range for second segment
  - Repair action: project parameters onto second segment
  - Suggested fixture: defect mentioning 'TransferRange(newE2'
- **Branch 17** @ line 4068 — *context_update* — **UNCOVERED**
  - What it tests: context tracking for split operation
  - Repair action: replace edge with wire of two edges
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Replace(wE, wire)'
- **Branch 18** @ line 4079 — *reversed_edge_order* — **UNCOVERED**
  - What it tests: original edge orientation REVERSED
  - Repair action: swap split edges and reverse orientations
  - Suggested fixture: defect mentioning 'orient == TopAbs_REVERSED'
- **Branch 19** @ line 4086 — *last_edge_wraparound* — **UNCOVERED**
  - What it tests: notch at wire boundary (last to first)
  - Repair action: identify if removal involves wraparound
  - Suggested fixture: defect mentioning 'n1 == NbEdges()', 'n2 == 1'
- **Branch 20** @ line 4090 — *remove_notched_edge* — **UNCOVERED**
  - What it tests: notched edge identified and location known
  - Repair action: call FixDummySeam to remove
  - Suggested fixture: defect mentioning 'FixDummySeam'
- **Branch 21** @ line 4095 — *context_consistency* — **UNCOVERED**
  - What it tests: context not null after modification
  - Repair action: update wire data
  - Suggested fixture: defect mentioning 'UpdateWire()'
- **Branch 22** @ line 4099 — *notch_fixed* — **UNCOVERED**
  - What it tests: notch repair completed
  - Repair action: encode DONE1
  - Suggested fixture: defect mentioning 'ShapeExtend_DONE1'

#### `ShapeFix_Wire.FixReorder` — lines 488–534
(8 branches, 6 covered.)

- **Branch 1** @ line 490 — *Precondition check* — COVERED by: in014
  - What it tests: Wire not loaded
  - Repair action: Return false if not loaded
- **Branch 2** @ line 497 — *Bi-periodic surface detection* — **UNCOVERED**
  - What it tests: Surface is periodic in both U and V directions
  - Repair action: Use bi-periodic mode for order check
  - Suggested fixture: defect mentioning 'IsUPeriodic', 'IsVPeriodic', 'theModeBoth'
- **Branch 3** @ line 500 — *Order check with 2D shift* — COVERED by: twi064
  - What it tests: Bi-periodic surface allows 2D parameter shifts
  - Repair action: CheckOrder with 2D shift enabled
- **Branch 4** @ line 504 — *Order check standard mode* — COVERED by: twi064
  - What it tests: Non-periodic or single-periodic surface
  - Repair action: CheckOrder with standard mode
- **Branch 5** @ line 509 — *Reorder failure detection* — COVERED by: tfa037, twi066
  - What it tests: FixReorder(sawo) fails to reorder
  - Repair action: Encode FAIL status with FAIL1 or FAIL2
- **Branch 6** @ line 520 — *Order status DONE2* — COVERED by: twi066, twi067, twi078
  - What it tests: Status is ±2: edge orientation or positioning reversed
  - Repair action: Mark DONE2 for reversed reordering
- **Branch 7** @ line 524 — *Order status DONE3* — **UNCOVERED**
  - What it tests: Status < 0: wire is closed
  - Repair action: Mark DONE3 for closed wire detection
  - Suggested fixture: defect mentioning 'Status() < 0', 'DONE3'
- **Branch 8** @ line 528 — *Shifted-only reorder* — COVERED by: tfa037
  - What it tests: Status == 3: only shifted edges without reordering
  - Repair action: Mark DONE5 for shifted-only fix

#### `ShapeFix_Wire.FixSeam_int` — lines 1616–1637
(3 branches, 0 covered.)

- **Branch 1** @ line 1618 — *not_ready* — **UNCOVERED**
  - What it tests: Wire not ready (not loaded/face null)
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 1625 — *seam_not_detected* — **UNCOVERED**
  - What it tests: CheckSeam returns false (no seam defect)
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!myAnalyzer->CheckSeam'
- **Branch 3** @ line 1631 — *seam_edge_detected* — **UNCOVERED**
  - What it tests: Edge identified as seam with two PCurves
  - Repair action: update edge with both PCurves and new range
  - Suggested fixture: defect mentioning 'B.UpdateEdge', 'C2, C1'

#### `ShapeFix_Wire.FixSelfIntersectingEdge` — lines 2709–2913
(23 branches, 7 covered.)

- **Branch 1** @ line 2711 — *uninitialized_wire* — COVERED by: in014
  - What it tests: Wire not ready for analysis
  - Repair action: reject_early_return
- **Branch 2** @ line 2720 — *null_analyzer* — COVERED by: in014
  - What it tests: No shape analyzer available
  - Repair action: reject_early_return
- **Branch 3** @ line 2725 — *check_fail_status* — **UNCOVERED**
  - What it tests: Analysis reported FAIL status
  - Repair action: status_encode_fail1
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)', 'EncodeStatus(ShapeExtend_FAIL1)'
- **Branch 4** @ line 2729 — *check_done_status* — COVERED by: in014
  - What it tests: Analysis did not complete successfully
  - Repair action: reject_early_return
- **Branch 5** @ line 2752 — *remove_loop_mode_variant* — **UNCOVERED**
  - What it tests: Mode < 1: tolerance-based removal
  - Repair action: branch_to_tolerance_increase
  - Suggested fixture: defect mentioning 'myRemoveLoopMode < 1', 'for (int iter = 0'
- **Branch 6** @ line 2763 — *intersection_near_vertex* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Intersection point near edge start/end vertex
  - Repair action: skip_continue
- **Branch 7** @ line 2770 — *geom_mode_enabled* — **UNCOVERED**
  - What it tests: Geometric mode active for loop removal
  - Repair action: attempt_loop_removal
  - Suggested fixture: defect mentioning 'myGeomMode', 'RemoveLoop(E,'
- **Branch 8** @ line 2772 — *pcurve_not_cached* — **UNCOVERED**
  - What it tests: Need to fetch pcurve data
  - Repair action: cache_pcurve
  - Suggested fixture: defect mentioning 'c2d.IsNull()', 'sae.PCurve(E'
- **Branch 9** @ line 2778 — *nested_loop_detected* — **UNCOVERED**
  - What it tests: Intersection nested within previous loop bounds
  - Repair action: skip_continue
  - Suggested fixture: defect mentioning 'firstpar > prevFirst && lastpar < prevLast'
- **Branch 10** @ line 2782 — *loop_removal_success* — **UNCOVERED**
  - What it tests: Loop removal completed without error
  - Repair action: status_done4_and_retry
  - Suggested fixture: defect mentioning 'RemoveLoop(E,', 'myLastFixStatus |= ShapeExtend::EncodeStatus(ShapeExtend_DONE4)'
- **Branch 11** @ line 2796 — *tolerance_within_limits* — **UNCOVERED**
  - What it tests: New tolerance below max threshold
  - Repair action: increase_vertex_tolerance
  - Suggested fixture: defect mentioning 'newtol < MaxTolerance()', 'UpdateVertex'
- **Branch 12** @ line 2800 — *nearest_vertex_selection* — **UNCOVERED**
  - What it tests: Choose vertex V1 vs V2 based on proximity
  - Repair action: conditional_update_v1_or_v2
  - Suggested fixture: defect mentioning 'dist21 < dist22', 'B.UpdateVertex(V1'
- **Branch 13** @ line 2809 — *tolerance_exceeds_max* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Required tolerance exceeds maximum allowed
  - Repair action: status_fail2
- **Branch 14** @ line 2816 — *post_removal_check* — **UNCOVERED**
  - What it tests: Self-intersection persists after loop removal
  - Repair action: recheck_or_break
  - Suggested fixture: defect mentioning 'loopRemoved', 'CheckSelfIntersectingEdge'
- **Branch 15** @ line 2821 — *recheck_done_status* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: Recheck shows intersection still present
  - Repair action: break_iteration
- **Branch 16** @ line 2844 — *remove_loop_mode_variant* — **UNCOVERED**
  - What it tests: Mode == 1: insert vertex approach
  - Repair action: branch_to_vertex_insertion
  - Suggested fixture: defect mentioning 'myRemoveLoopMode == 1'
- **Branch 17** @ line 2854 — *geom_mode_for_insertion* — **UNCOVERED**
  - What it tests: Geometric mode for vertex insertion path
  - Repair action: attempt_loop_removal_vertex
  - Suggested fixture: defect mentioning 'myGeomMode', 'RemoveLoop(E, Face()'
- **Branch 18** @ line 2861 — *loop_removal_with_vertex* — **UNCOVERED**
  - What it tests: Successful loop removal splitting into E1, E2
  - Repair action: append_edges_status_done4
  - Suggested fixture: defect mentioning 'RemoveLoop(E, Face(), points2d.Value(1), E1, E2)', 'myLastFixStatus |= ShapeExtend::EncodeStatus(ShapeExtend_DONE4)'
- **Branch 19** @ line 2865 — *first_edge_notnull* — **UNCOVERED**
  - What it tests: First output edge E1 is valid
  - Repair action: append_e1_and_compute_tol
  - Suggested fixture: defect mentioning '!E1.IsNull()', 'TTSS->Append(E1)'
- **Branch 20** @ line 2879 — *final_tolerance_check* — **UNCOVERED**
  - What it tests: Final edge tolerance exceeds maximum
  - Repair action: status_fail2
  - Suggested fixture: defect mentioning 'newtol > MaxTolerance()', 'EncodeStatus(ShapeExtend_FAIL2)'
- **Branch 21** @ line 2889 — *context_available* — **UNCOVERED**
  - What it tests: Transformation context available for edge replacement
  - Repair action: context_replace_wire
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Replace(E, sewd.Wire())'
- **Branch 22** @ line 2894 — *context_unavailable* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: No transformation context, use wiredata directly
  - Repair action: wiredata_remove_add
- **Branch 23** @ line 2905 — *final_status_and_warning* — **UNCOVERED**
  - What it tests: Fix successful, emit warning message
  - Repair action: send_warning
  - Suggested fixture: defect mentioning 'LastFixStatus(ShapeExtend_DONE)', 'SendWarning'

#### `ShapeFix_Wire.FixSelfIntersectingEdge_int` — lines 2709–2913
(14 branches, 1 covered.)

- **Branch 1** @ line 2711 — *not_ready* — **UNCOVERED**
  - What it tests: Wire not ready
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 2720 — *null_analyzer* — **UNCOVERED**
  - What it tests: Analyzer is null
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning 'theAdvAnalyzer.IsNull()'
- **Branch 3** @ line 2725 — *intersection_check_fail* — **UNCOVERED**
  - What it tests: CheckSelfIntersectingEdge analysis FAIL status
  - Repair action: set FAIL1 status but continue
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 4** @ line 2729 — *no_intersection_detected* — **UNCOVERED**
  - What it tests: No DONE status from analyzer
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 5** @ line 2752 — *tolerance_increase_mode* — **UNCOVERED**
  - What it tests: myRemoveLoopMode < 1 (increase vertex tolerance)
  - Repair action: iterate up to 30 times: check intersections and increase tolerance
  - Suggested fixture: defect mentioning 'myRemoveLoopMode < 1', 'for (int iter = 0; iter < 30'
- **Branch 6** @ line 2763 — *intersection_at_vertex* — **UNCOVERED**
  - What it tests: Intersection point is at vertex
  - Repair action: skip - intersection already at boundary
  - Suggested fixture: defect mentioning 'dist21 < tol1 * tol1 || dist22 < tol2 * tol2'
- **Branch 7** @ line 2770 — *geom_mode_loop_removal* — **UNCOVERED**
  - What it tests: myGeomMode enabled and intersection not at vertex
  - Repair action: attempt RemoveLoop to split edge
  - Suggested fixture: defect mentioning 'myGeomMode', 'RemoveLoop'
- **Branch 8** @ line 2788 — *loop_successfully_removed* — **UNCOVERED**
  - What it tests: RemoveLoop succeeded
  - Repair action: mark DONE4, repeat iteration
  - Suggested fixture: defect mentioning 'loopRemoved = true'
- **Branch 9** @ line 2796 — *tolerance_within_limit* — **UNCOVERED**
  - What it tests: New tolerance less than max
  - Repair action: update vertex tolerance to newtol
  - Suggested fixture: defect mentioning 'newtol < MaxTolerance()'
- **Branch 10** @ line 2811 — *tolerance_exceeds_max* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: New tolerance would exceed max tolerance
  - Repair action: set FAIL2 status (too large tolerance needed)
- **Branch 11** @ line 2844 — *insert_vertex_mode* — **UNCOVERED**
  - What it tests: myRemoveLoopMode == 1 (split edge with new vertex)
  - Repair action: split edge at intersection point
  - Suggested fixture: defect mentioning 'myRemoveLoopMode == 1'
- **Branch 12** @ line 2861 — *loop_remove_split_success* — **UNCOVERED**
  - What it tests: RemoveLoop succeeded in split mode
  - Repair action: collect resulting edges and update wire
  - Suggested fixture: defect mentioning 'RemoveLoop(E, Face(), points2d.Value(1), E1, E2)'
- **Branch 13** @ line 2879 — *tolerance_after_split* — **UNCOVERED**
  - What it tests: Tolerance of split edges exceeds max
  - Repair action: set FAIL2 status
  - Suggested fixture: defect mentioning 'newtol > MaxTolerance()'
- **Branch 14** @ line 2889 — *wire_replacement* — **UNCOVERED**
  - What it tests: Context available for wire replacement
  - Repair action: replace old edge with new split edges
  - Suggested fixture: defect mentioning '!Context().IsNull()', 'Context()->Replace(E, sewd.Wire())'

#### `ShapeFix_Wire.FixSelfIntersection` — lines 1084–1280
(14 branches, 3 covered.)

- **Branch 1** @ line 1086 — *missing-wire-data* — **UNCOVERED**
  - What it tests: Wire not loaded; gate check
  - Repair action: return false
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 1094 — *self-loop-in-single-edge* — COVERED by: ad086
  - What it tests: Single edge has a self-touching loop (e.g., figure-8)
  - Repair action: FixSelfIntersectingEdge per edge; depends on myRemoveLoopMode
- **Branch 3** @ line 1096 — *self-loop-retain* — **UNCOVERED**
  - What it tests: Self-intersecting edge; keep edge, only fix internal loop
  - Repair action: FixSelfIntersectingEdge without removal
  - Suggested fixture: defect mentioning 'myRemoveLoopMode < 1'
- **Branch 4** @ line 1104 — *self-loop-remove-with-recheck* — COVERED by: twi053
  - What it tests: Self-intersecting edge; remove if unfixable, recheck closure
  - Repair action: FixSelfIntersectingEdge, then FixClosed if edges added
- **Branch 5** @ line 1120 — *adjacent-edge-crossing* — **UNCOVERED**
  - What it tests: Two adjacent or nearby edges cross each other
  - Repair action: FixIntersectingEdges per num; may split/reorder/remove
  - Suggested fixture: defect mentioning 'myFixIntersectingEdgesMode', 'FixIntersectingEdges(num)'
- **Branch 6** @ line 1122 — *open-vs-closed-edge-start* — **UNCOVERED**
  - What it tests: Open wire starts from edge 2; closed starts from 1
  - Repair action: Set num = (myClosedMode ? 1 : 2)
  - Suggested fixture: defect mentioning 'myClosedMode ? 1 : 2'
- **Branch 7** @ line 1126 — *intersection-repair-fail* — COVERED by: twi066
  - What it tests: FixIntersectingEdges returns FAIL1 or FAIL2
  - Repair action: Aggregate FAIL status; continue iteration
- **Branch 8** @ line 1134 — *intersection-no-fix-needed* — **UNCOVERED**
  - What it tests: No damage detected; skip edge pair
  - Repair action: continue to next num
  - Suggested fixture: defect mentioning '!LastFixStatus(ShapeExtend_DONE)'
- **Branch 9** @ line 1139 — *intersection-edge-split* — **UNCOVERED**
  - What it tests: Edge split to remove crossing; wire now longer
  - Repair action: Aggregate DONE1 status
  - Suggested fixture: defect mentioning 'LastFixStatus(ShapeExtend_DONE1)'
- **Branch 10** @ line 1152 — *small-wire-tolerance-only* — **UNCOVERED**
  - What it tests: Wire < 3 edges or tolerance adjusted; recheck without full topology
  - Repair action: Possibly re-run FixIntersectingEdges once; continue
  - Suggested fixture: defect mentioning 'nb < 3', 'LastFixStatus(ShapeExtend_DONE7)'
- **Branch 11** @ line 1166 — *self-intersecting-edge-remove* — **UNCOVERED**
  - What it tests: Current edge is self-touching and unfixable; remove it
  - Repair action: sbwd->Remove(num); reset num to start
  - Suggested fixture: defect mentioning 'LastFixStatus(ShapeExtend_DONE4)', 'sbwd->Remove(num)'
- **Branch 12** @ line 1170 — *previous-edge-remove* — **UNCOVERED**
  - What it tests: Previous edge intersects current; remove prev instead
  - Repair action: sbwd->Remove(num-1 or cyclic); reset num
  - Suggested fixture: defect mentioning 'LastFixStatus(ShapeExtend_DONE3)', 'num > 1 ? num-1'
- **Branch 13** @ line 1200 — *non-adjacent-crossing* — **UNCOVERED**
  - What it tests: Non-adjacent edges cross (complex topology)
  - Repair action: FixSelfIntersectWire via ITool; may split/cut/remove
  - Suggested fixture: defect mentioning 'myFixNonAdjacentIntersectingEdgesMode', 'ITool.FixSelfIntersectWire'
- **Branch 14** @ line 1209 — *non-adjacent-split-remove* — **UNCOVERED**
  - What it tests: Non-adjacent fix caused splits or removals; reload wire
  - Repair action: Update analyzer, context, nullify shape cache
  - Suggested fixture: defect mentioning 'NbSplit > 0', 'NbRemoved > 0', 'Load(sbwd)'

#### `ShapeFix_Wire.FixShifted` — lines 1662–2126
(14 branches, 2 covered.)

- **Branch 1** @ line 1664 — *not_ready* — **UNCOVERED**
  - What it tests: Wire not ready
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!IsReady()'
- **Branch 2** @ line 1671 — *closed_surface_check* — **UNCOVERED**
  - What it tests: Neither U nor V closed
  - Repair action: return false - no shift possible
  - Suggested fixture: defect mentioning '!uclosed && !vclosed'
- **Branch 3** @ line 1681 — *revolution_surface_periodic_basis* — **UNCOVERED**
  - What it tests: Surface of revolution with periodic basis curve
  - Repair action: set vclosed and VRange from period
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_SurfaceOfRevolution))', 'aBaseCrv->IsPeriodic()'
- **Branch 4** @ line 1747 — *degenerated_edge_no_pcurve* — **UNCOVERED**
  - What it tests: Degenerated edge without PCurve
  - Repair action: skip edge (don't add to working wire)
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(E1)', '!sae.HasPCurve'
- **Branch 5** @ line 1779 — *adjacent_edges_degenerated* — **UNCOVERED**
  - What it tests: Either E1 or E2 is degenerated
  - Repair action: mark stop point and skip
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(E1) || BRep_Tool::Degenerated(E2)'
- **Branch 6** @ line 1807 — *vertex_on_singularity* — **UNCOVERED**
  - What it tests: Vertex maps to surface singularity
  - Repair action: detect singularity type by U or V
  - Suggested fixture: defect mentioning 'surf->DegeneratedValues'
- **Branch 7** @ line 1821 — *revolution_surface_additional_check* — **UNCOVERED**
  - What it tests: Revolution surface near boundary
  - Repair action: mark as degenerated if at boundary
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_SurfaceOfRevolution))', 'surf->IsDegenerated'
- **Branch 8** @ line 1905 — *bi_meridian_shift_detection* — **UNCOVERED**
  - What it tests: Complex geometric shift around singularity
  - Repair action: compute and apply transformation to PCurves
  - Suggested fixture: defect mentioning 'rot1 * rot2 < 0', 'scld * scln < 0'
- **Branch 9** @ line 2018 — *u_closed_gap_detection* — **UNCOVERED**
  - What it tests: U-closed surface with large X gap
  - Repair action: adjust PCurve X by period
  - Suggested fixture: defect mentioning 'uclosed && isDeg != 1', 'URange - UTol'
- **Branch 10** @ line 2030 — *v_closed_gap_detection* — **UNCOVERED**
  - What it tests: V-closed surface with large Y gap
  - Repair action: adjust PCurve Y by period
  - Suggested fixture: defect mentioning 'vclosed && isDeg != 2', 'VRange - VTol'
- **Branch 11** @ line 2056 — *void_box_overflow* — **UNCOVERED**
  - What it tests: Bounding box is void (no valid edges)
  - Repair action: return false - cannot process
  - Suggested fixture: defect mentioning 'box.IsVoid()'
- **Branch 12** @ line 2063 — *no_shift_needed_overall* — **UNCOVERED**
  - What it tests: Wire already well-positioned
  - Repair action: return false - no overall shift needed
  - Suggested fixture: defect mentioning '!LastFixStatus(ShapeExtend_DONE)'
- **Branch 13** @ line 2086 — *overall_u_shift* — COVERED by: n010
  - What it tests: Wire needs overall U shift
  - Repair action: apply U translation to all PCurves
- **Branch 14** @ line 2093 — *overall_v_shift* — COVERED by: n010
  - What it tests: Wire needs overall V shift
  - Repair action: apply V translation to all PCurves

#### `ShapeFix_Wire.FixSmall` — lines 539–553
(3 branches, 2 covered.)

- **Branch 1** @ line 541 — *Precondition check* — COVERED by: in014
  - What it tests: Wire not loaded
  - Repair action: Return 0 (false) if not loaded
- **Branch 2** @ line 546 — *Per-edge small edge iteration* — COVERED by: ad086, tfa006, tfa007, tfa008, tfa040, tfa041, tfa042, tfa043 (+6 more)
  - What it tests: Each edge may be small (below tolerance)
  - Repair action: Call FixSmall(i, lockvtx, precsmall) per edge
- **Branch 3** @ line 549 — *Status accumulation* — **UNCOVERED**
  - What it tests: Any edge fix produces status
  - Repair action: OR status flags from each edge fix
  - Suggested fixture: defect mentioning 'myLastFixStatus', 'myStatusSmall |='

#### `ShapeFix_Wire.FixSmall_int` — lines 1405–1472
(7 branches, 0 covered.)

- **Branch 1** @ line 1407 — *unloaded_or_single_edge* — **UNCOVERED**
  - What it tests: Wire not loaded or only single edge
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!IsLoaded()', 'NbEdges() <= 1'
- **Branch 2** @ line 1414 — *no_analyzer* — **UNCOVERED**
  - What it tests: Analyzer is null
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning 'theAdvAnalyzer.IsNull()'
- **Branch 3** @ line 1420 — *small_edge_check_fail* — **UNCOVERED**
  - What it tests: CheckSmall analysis returns FAIL status
  - Repair action: set FAIL1 status but continue
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_FAIL)'
- **Branch 4** @ line 1426 — *small_edge_not_detected* — **UNCOVERED**
  - What it tests: No DONE status from analyzer
  - Repair action: return false without repair
  - Suggested fixture: defect mentioning '!LastCheckStatus(ShapeExtend_DONE)'
- **Branch 5** @ line 1433 — *small_edge_with_different_vertices* — **UNCOVERED**
  - What it tests: Small edge detected with different start/end vertices
  - Repair action: merge vertices or fail based on mode
  - Suggested fixture: defect mentioning 'LastCheckStatus(ShapeExtend_DONE2)', 'myTopoMode'
- **Branch 6** @ line 1436 — *vertex_lock_conflict* — **UNCOVERED**
  - What it tests: lockvtx true or not topoMode
  - Repair action: return false refusing vertex merge
  - Suggested fixture: defect mentioning 'lockvtx || !myTopoMode'
- **Branch 7** @ line 1459 — *post_removal_connection_issue* — **UNCOVERED**
  - What it tests: Small edge had different vertices, attempt fix connection
  - Repair action: call FixConnected to fix resulting gap
  - Suggested fixture: defect mentioning 'LastFixStatus(ShapeExtend_DONE2)', 'FixConnected(n'

#### `ShapeFix_Wire.Load` — lines 248–260
(3 branches, 1 covered.)

- **Branch 1** @ line 252 — *Context transformation* — **UNCOVERED**
  - What it tests: Shape context available for transformation
  - Repair action: Apply context transformation to input wire
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'Context()->Apply'
- **Branch 2** @ line 254 — *Shape extraction* — COVERED by: a019, a028, a038, ad056, ad086, gn035, gp014, gp018 (+40 more)
  - What it tests: Result of context.Apply is convertible to wire
  - Repair action: Extract wire from transformed shape
- **Branch 3** @ line 258 — *Analyzer initialization* — **UNCOVERED**
  - What it tests: Wire data loaded into shape analyzer
  - Repair action: Call myAnalyzer->Load(W)
  - Suggested fixture: defect mentioning 'myAnalyzer->Load'

#### `ShapeFix_Wire.Perform` — lines 298–483
(15 branches, 10 covered.)

- **Branch 1** @ line 300 — *Precondition check* — COVERED by: in014
  - What it tests: Wire data not loaded
  - Repair action: Return false immediately if not loaded
- **Branch 2** @ line 305 — *Context propagation* — **UNCOVERED**
  - What it tests: Context exists for downstream tools
  - Repair action: Propagate context to FixEdge tool
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'SetContext'
- **Branch 3** @ line 317 — *Reorder necessity detection* — COVERED by: ad086, twi007, twi028, twi064
  - What it tests: Wire edges in wrong order
  - Repair action: Run FixReorder() if CheckOrder fails
- **Branch 4** @ line 334 — *Small edges topology mode* — COVERED by: ad086, tfa006, tfa007, tfa008, tfa040, tfa041, tfa042, tfa043 (+6 more)
  - What it tests: Topology change allowed and reorder succeeded
  - Repair action: Fix small edges with topology constraints
- **Branch 5** @ line 340 — *Reorder retry after small fix* — **UNCOVERED**
  - What it tests: Small edge fix succeeded, retry reorder
  - Repair action: Re-run FixReorder to handle new topology
  - Suggested fixture: defect mentioning 'FixReorder()', 'ReorderOK'
- **Branch 6** @ line 353 — *Connected mode check* — COVERED by: ad086, twi003
  - What it tests: Edges connected and ordered correctly
  - Repair action: Run FixConnected() to ensure adjacency
- **Branch 7** @ line 368 — *Shifted edge mode override* — **UNCOVERED**
  - What it tests: Reorder failed, disable shifted mode
  - Repair action: Temporarily set myFixShiftedMode = 0
  - Suggested fixture: defect mentioning 'myFixShiftedMode', '!ReorderOK'
- **Branch 8** @ line 386 — *Degenerated edge check* — COVERED by: twi021
  - What it tests: Zero-length 3D curves present
  - Repair action: Run FixDegenerated()
- **Branch 9** @ line 400 — *Notched edge mode* — COVERED by: twi054, twi074
  - What it tests: Tail mode off and reorder succeeded
  - Repair action: Run FixNotchedEdges() for bad vertices
- **Branch 10** @ line 414 — *Tail mode override* — COVERED by: twi011, twi098
  - What it tests: Tail mode explicitly enabled
  - Repair action: Run FixTails() instead of notched edges
- **Branch 11** @ line 428 — *Self-intersection mode* — COVERED by: ad086, twi040
  - What it tests: Wire closed and self-intersections possible
  - Repair action: Run FixSelfIntersection() if closed
- **Branch 12** @ line 432 — *Intersecting edges mode override* — **UNCOVERED**
  - What it tests: Reorder failed, disable intersecting edge fix
  - Repair action: Temporarily set myFixIntersectingEdgesMode = 0
  - Suggested fixture: defect mentioning 'myFixIntersectingEdgesMode', '!ReorderOK'
- **Branch 13** @ line 449 — *Missing edge check* — COVERED by: twi036
  - What it tests: Reorder succeeded, check for missing edges
  - Repair action: Run FixLacking() if reorder OK
- **Branch 14** @ line 464 — *Vertex tolerance fix* — COVERED by: twi048, twi059, twi061
  - What it tests: Each edge vertex tolerance mismatch
  - Repair action: Call FixVertexTolerance per edge
- **Branch 15** @ line 477 — *Context update* — **UNCOVERED**
  - What it tests: Context exists, wire structure changed
  - Repair action: UpdateWire() to apply context changes
  - Suggested fixture: defect mentioning 'UpdateWire', 'Context().IsNull()'


### `src/ModelingAlgorithms/TKShHealing/ShapeFix/ShapeFix_Wireframe.cxx`

4 methods, 106 branches, 58 covered.

#### `ShapeFix_Wireframe.CheckSmallEdges` — lines 588–722
(15 branches, 1 covered.)

- **Branch 1** @ line 598 — *face_orientation_reversed* — **UNCOVERED**
  - What it tests: Face REVERSED → normalize to FORWARD before processing
  - Repair action: face = facet.Oriented(TopAbs_FORWARD)
  - Suggested fixture: defect mentioning 'facet.Orientation() == TopAbs_REVERSED', 'TopAbs_FORWARD'
- **Branch 2** @ line 604 — *non_wire_in_face* — **UNCOVERED**
  - What it tests: Face iterator yields non-WIRE → skip
  - Repair action: continue
  - Suggested fixture: defect mentioning 'itw.Value().ShapeType() != TopAbs_WIRE', 'TopAbs_WIRE'
- **Branch 3** @ line 614 — *seam_edge_detection* — **UNCOVERED**
  - What it tests: Build edge multiplicity map to identify seam/multi-use edges
  - Repair action: populate EdgeMap with edge→count
  - Suggested fixture: defect mentioning 'for (i = 1; i <= SAW.NbEdges()', 'EdgeMap.Bind'
- **Branch 4** @ line 630 — *multi_use_edge* — **UNCOVERED**
  - What it tests: Edge appears >1 time in wire → check if seam
  - Repair action: if not seam, add to theMultyEdges; skip normal processing
  - Suggested fixture: defect mentioning 'EdgeMap.Find(edge) != 1', 'IsSeam'
- **Branch 5** @ line 632 — *multi_use_non_seam* — **UNCOVERED**
  - What it tests: Multi-use edge AND not seam → topology defect
  - Repair action: theMultyEdges.Add(edge)
  - Suggested fixture: defect mentioning '!SAW.WireData()->IsSeam(i)', 'theMultyEdges.Add'
- **Branch 6** @ line 639 — *edge_to_face_mapping* — **UNCOVERED**
  - What it tests: Track which faces use each edge
  - Repair action: theEdgeToFaces.Bind or append to existing list
  - Suggested fixture: defect mentioning 'theEdgeToFaces.IsBound(edge)', 'theEdgeToFaces.Bind'
- **Branch 7** @ line 650 — *small_edge_already_marked* — **UNCOVERED**
  - What it tests: Edge was marked small in earlier iteration
  - Repair action: theEdgeList.Append(edge)
  - Suggested fixture: defect mentioning 'theSmallEdges.Contains(edge)', 'theEdgeList.Append'
- **Branch 8** @ line 654 — *small_edge_check* — **UNCOVERED**
  - What it tests: Edge length < precision → mark as small
  - Repair action: SAW.CheckSmall(i, Precision()) → add to both maps
  - Suggested fixture: defect mentioning 'SAW.CheckSmall(i, Precision())', 'theSmallEdges.Add'
- **Branch 9** @ line 662 — *face_small_edge_list* — **UNCOVERED**
  - What it tests: Face has small edges → record in theFaceWithSmall
  - Repair action: theFaceWithSmall.Bind(facet, theEdgeList)
  - Suggested fixture: defect mentioning 'theEdgeList.Extent()', 'theFaceWithSmall.Bind'
- **Branch 10** @ line 672 — *free_wire_analysis* — **UNCOVERED**
  - What it tests: Free wires (not on face) → parallel small-edge detection
  - Repair action: TopExp_Explorer expw1(myShape, TopAbs_WIRE, TopAbs_FACE) loop
  - Suggested fixture: defect mentioning 'TopAbs_WIRE, TopAbs_FACE', 'expw1.More'
- **Branch 11** @ line 680 — *wire_load_failure* — COVERED by: in014
  - What it tests: Free wire failed to load → early return
  - Repair action: return false
- **Branch 12** @ line 684 — *free_wire_edge_map* — **UNCOVERED**
  - What it tests: Build edge multiplicity for free wire edges
  - Repair action: populate EdgeMap for free-wire context
  - Suggested fixture: defect mentioning 'for (i = 1; i <= SAW.NbEdges()', 'theWire'
- **Branch 13** @ line 700 — *free_wire_multi_use_edge* — **UNCOVERED**
  - What it tests: Free-wire edge appears >1 time → check seam
  - Repair action: if not seam, add to theMultyEdges
  - Suggested fixture: defect mentioning 'EdgeMap.Find(edge) != 1', 'expw1'
- **Branch 14** @ line 710 — *free_wire_small_edge_check* — **UNCOVERED**
  - What it tests: Free-wire edge length < precision
  - Repair action: SAW.CheckSmall(i) → add to theSmallEdges
  - Suggested fixture: defect mentioning 'SAW.CheckSmall(i, Precision())', 'theSmallEdges.Add'
- **Branch 15** @ line 721 — *result_status* — **UNCOVERED**
  - What it tests: Return whether any small edges were found
  - Repair action: return !theSmallEdges.IsEmpty()
  - Suggested fixture: defect mentioning 'return (!theSmallEdges.IsEmpty())', 'CheckSmallEdges'

#### `ShapeFix_Wireframe.FixSmallEdges` — lines 505–575
(8 branches, 1 covered.)

- **Branch 1** @ line 507 — *null_input* — **UNCOVERED**
  - What it tests: Shape is null → early exit
  - Repair action: return false
  - Suggested fixture: defect mentioning 'myShape.IsNull()', 'FixSmallEdges'
- **Branch 2** @ line 512 — *context_state* — **UNCOVERED**
  - What it tests: Context missing → initialize or reuse
  - Repair action: new ShapeBuild_ReShape or Context()->Apply
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'SetContext'
- **Branch 3** @ line 523 — *shape_type_compound* — **UNCOVERED**
  - What it tests: COMPOUND shape → recursive sub-shape processing with caching
  - Repair action: iterate children, use 'cont' cache, rebuild compound
  - Suggested fixture: defect mentioning 'TopAbs_COMPOUND', 'for (TopoDS_Iterator', 'cont.IsBound'
- **Branch 4** @ line 536 — *shape_cache_hit* — **UNCOVERED**
  - What it tests: Sub-shape already processed → reuse with orientation
  - Repair action: fetch from cont, apply location and orientation
  - Suggested fixture: defect mentioning 'cont.IsBound(shape1)', 'cont.Find'
- **Branch 5** @ line 547 — *topology_modification* — **UNCOVERED**
  - What it tests: Result differs from input → mark modified
  - Repair action: set locModified=true
  - Suggested fixture: defect mentioning '!res.IsSame(shape1)', 'locModified'
- **Branch 6** @ line 553 — *result_null_check* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Result shape became null → skip adding
  - Repair action: continue to next child (don't add to rebuilt compound)
- **Branch 7** @ line 561 — *topology_changed* — **UNCOVERED**
  - What it tests: Children were modified → update parent in context
  - Repair action: Context()->Replace(savShape, C)
  - Suggested fixture: defect mentioning 'locModified', 'Context()->Replace'
- **Branch 8** @ line 572 — *delegation_to_analysis* — **UNCOVERED**
  - What it tests: Main logic delegates to helper methods
  - Repair action: CheckSmallEdges populates maps, MergeSmallEdges applies fixes
  - Suggested fixture: defect mentioning 'CheckSmallEdges(', 'MergeSmallEdges('

#### `ShapeFix_Wireframe.FixWireGaps` — lines 93–280
(18 branches, 7 covered.)

- **Branch 1** @ line 95 — *null_input* — COVERED by: ad086
  - What it tests: Shape is null → early exit
  - Repair action: return false
- **Branch 2** @ line 100 — *context_state* — **UNCOVERED**
  - What it tests: Context missing → initialize or reuse
  - Repair action: new ShapeBuild_ReShape or Context()->Apply
  - Suggested fixture: defect mentioning 'Context().IsNull()', 'SetContext'
- **Branch 3** @ line 113 — *shape_type_compound* — **UNCOVERED**
  - What it tests: COMPOUND shape → recursive sub-shape processing
  - Repair action: iterate children, cache results in 'cont' map, rebuild
  - Suggested fixture: defect mentioning 'TopAbs_COMPOUND', 'for (TopoDS_Iterator', 'cont.IsBound'
- **Branch 4** @ line 126 — *shape_cache_hit* — **UNCOVERED**
  - What it tests: Sub-shape already processed → reuse cached result
  - Repair action: fetch from cont map, apply location and orientation
  - Suggested fixture: defect mentioning 'cont.IsBound(shape1)', 'cont.Find'
- **Branch 5** @ line 137 — *topology_modification* — **UNCOVERED**
  - What it tests: Result differs from input → mark as modified
  - Repair action: set locModified=true for Context()->Replace
  - Suggested fixture: defect mentioning '!res.IsSame(shape1)', 'locModified'
- **Branch 6** @ line 162 — *face_orientation_reversed* — **UNCOVERED**
  - What it tests: Face has REVERSED orientation → normalize to FORWARD
  - Repair action: face.Orientation(TopAbs_FORWARD)
  - Suggested fixture: defect mentioning 'TopAbs_REVERSED', 'face.Orientation'
- **Branch 7** @ line 168 — *non_wire_in_face* — **UNCOVERED**
  - What it tests: Face iterator yields non-WIRE shape → skip
  - Repair action: continue to next iterator value
  - Suggested fixture: defect mentioning 'TopAbs_WIRE', 'itw.Value().ShapeType'
- **Branch 8** @ line 177 — *gap_detection_3d* — COVERED by: tfa037, twi066, twi067
  - What it tests: 3D gap fixes applied → encode status DONE1
  - Repair action: StatusGaps3d(DONE) → OR with DONE1 flag
- **Branch 9** @ line 181 — *gap_detection_3d_failure* — COVERED by: tfa037, twi066
  - What it tests: 3D gap fix failed → encode status FAIL1
  - Repair action: StatusGaps3d(FAIL) → OR with FAIL1 flag
- **Branch 10** @ line 186 — *gap_detection_2d* — COVERED by: twi066, twi067, twi078
  - What it tests: 2D gap fixes applied → encode status DONE2
  - Repair action: StatusGaps2d(DONE) → OR with DONE2 flag
- **Branch 11** @ line 190 — *gap_detection_2d_failure* — COVERED by: twi066
  - What it tests: 2D gap fix failed → encode status FAIL2
  - Repair action: StatusGaps2d(FAIL) → OR with FAIL2 flag
- **Branch 12** @ line 194 — *gap_warning_criterion* — **UNCOVERED**
  - What it tests: Any 3D or 2D gap fixed → send warning message
  - Repair action: SendWarning with FixWireGaps.MSG0
  - Suggested fixture: defect mentioning 'StatusGaps3d(ShapeExtend_DONE) || StatusGaps2d', 'SendWarning'
- **Branch 13** @ line 206 — *free_wire_processing* — **UNCOVERED**
  - What it tests: Free wires (not on face) → parallel detection loop
  - Repair action: TopExp_Explorer expw(myShape, TopAbs_WIRE, TopAbs_FACE) loop
  - Suggested fixture: defect mentioning 'TopAbs_WIRE, TopAbs_FACE', 'sfw->Load'
- **Branch 14** @ line 213 — *free_wire_3d_gap* — **UNCOVERED**
  - What it tests: Free wire 3D gaps → encode DONE1 status
  - Repair action: FixGaps3d on free wire
  - Suggested fixture: defect mentioning 'expw.More()', 'sfw->Load', 'sfw->FixGaps3d'
- **Branch 15** @ line 228 — *post_fix_required* — COVERED by: ad086, gp022, n004, n005, n006, sw009, twi044, twi065
  - What it tests: Any gaps were fixed → apply post-fix workflow
  - Repair action: SameParameter + vertex tolerance + self-intersection fixes
- **Branch 16** @ line 240 — *post_fix_face_orientation* — **UNCOVERED**
  - What it tests: Post-fix face orientation REVERSED → normalize
  - Repair action: face.Orientation(TopAbs_FORWARD)
  - Suggested fixture: defect mentioning 'face.Orientation() == TopAbs_REVERSED', 'anExpf2'
- **Branch 17** @ line 246 — *post_fix_non_wire_skip* — **UNCOVERED**
  - What it tests: Post-fix iterator non-WIRE → skip
  - Repair action: continue
  - Suggested fixture: defect mentioning 'TopAbs_WIRE', 'anExpf2', 'itw.More'
- **Branch 18** @ line 262 — *free_wire_post_fix* — COVERED by: a013, a025, a030, ad086, ls044, m006, m049, pmi065 (+1 more)
  - What it tests: Free wires post-fix → apply self-intersection + tolerance
  - Repair action: FixSelfIntersection + FixVertexTolerance loop

#### `ShapeFix_Wireframe.MergeSmallEdges` — lines 735–1934
(65 branches, 49 covered.)

- **Branch 1** @ line 741 — *Empty collection of small edges (outer guard)* — **UNCOVERED**
  - What it tests: Entry guard: if the set of small edges is empty, the entire repair pipeline is skipped.
  - Repair action: Return false without any repairs.
  - Suggested fixture: defect mentioning 'empty small edges', 'IsEmpty', 'no edges to merge'
- **Branch 2** @ line 752 — *Face not in the small-edge map* — COVERED by: a002, a003, a013, a014, a017, a018, a019, a020 (+747 more)
  - What it tests: Checks if the current face has any small edges mapped to it; only faces with small edges proceed to repair.
  - Repair action: Skip this face; move to next face.
- **Branch 3** @ line 754 — *Face-to-small-edges mapping is empty* — COVERED by: gn010, m010, m064, os007, os022, pmi032, pmi091, pmi112 (+13 more)
  - What it tests: Checks if the list of small edges for this face has zero extent (even if face is in map).
  - Repair action: Skip this face; move to next face.
- **Branch 4** @ line 759 — *Face has been modified in context (gka comment)* — **UNCOVERED**
  - What it tests: After applying context, the face differs from the original. Detects shape replacements.
  - Repair action: Remap all small edges from original to new shape in the maps.
  - Suggested fixture: defect mentioning 'IsSame', 'context apply', 'face modified'
- **Branch 5** @ line 766 — *Edge has status pending in context (stat > 0)* — COVERED by: a003, ad043, ad045, ad056, ad086, ad119, gb001, gb002 (+37 more)
  - What it tests: Detects edges that have been marked as modified/replaced in the healing context.
  - Repair action: Update small-edge and edge-to-faces maps to use the new edge shape.
- **Branch 6** @ line 788 — *Wire child is not a WIRE shape type* — **UNCOVERED**
  - What it tests: Filters out non-wire children of face (e.g., internal structures).
  - Repair action: Skip this child; move to next.
  - Suggested fixture: defect mentioning 'ShapeType', 'TopAbs_WIRE', 'child not wire'
- **Branch 7** @ line 793 — *Face has reverse orientation; needs forward reorientation* — COVERED by: a024, a026, ad047, ad057, ad086, bo001, bo002, bo003 (+142 more)
  - What it tests: If face is reversed, create a forward copy for geometric operations.
  - Repair action: Re-orient the face to FORWARD.
- **Branch 8** @ line 812 — *Middle edge is identical to one of its neighbors (self-loop or duplicate seam)* — COVERED by: a095, gn024, gs009, pmi073, pmi075, tfa001, tfa002, tfa003 (+66 more)
  - What it tests: Detects when edge2 is the same object as edge1 or edge3.
  - Repair action: Skip this candidate triplet; advance index.
- **Branch 9** @ line 822 — *Middle edge is in the small-edge set (core repair trigger)* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+895 more)
  - What it tests: Confirms that the middle edge of a triplet is classified as small.
  - Repair action: Evaluate whether to merge it with neighbors.
- **Branch 10** @ line 825 — *All three edges form a closed loop (edge1 == edge3)* — COVERED by: bo005, m072, pmi119, pmi120, tfa022
  - What it tests: Detects wire where first and last neighbors are the same edge.
  - Repair action: Set take_next=true; prefer merging with next edge.
- **Branch 11** @ line 831 — *Cannot extract 3D curves for all three edges in triplet* — COVERED by: ad086, bo002, gn017, gp005, gs006, gs028, gs034, os012 (+18 more)
  - What it tests: If any edge is degenerate (no 3D curve) or fails Curve3d extraction, angle computation is skipped.
  - Repair action: Set angles to default (0.0); skip fine-grained angle logic.
- **Branch 12** @ line 849 — *Edge tangent vector magnitude is near-zero (degenerate or inflection point)* — COVERED by: fi005, gs014, m036, tb013
  - What it tests: Checks if tangent vector at endpoint has negligible magnitude (< tol2).
  - Repair action: Set angle to 90 degrees (M_PI/2) to indicate severe curvature discontinuity.
- **Branch 13** @ line 855 — *Valid tangent vectors exist for angle comparison* — COVERED by: ad014, ad086, ad096, ad114, bo025, bo028, fi001, fi005 (+109 more)
  - What it tests: Both tangent vectors have meaningful magnitude; compute angle between them.
  - Repair action: Calculate Ang1 as absolute angle between tangent vectors.
- **Branch 14** @ line 867 — *Second angle measurement has near-zero tangent (degenerate end)* — **UNCOVERED**
  - What it tests: Similar to branch 12 but for the second angle (Ang2).
  - Repair action: Set Ang2 = 90 degrees.
  - Suggested fixture: defect mentioning 'SquareMagnitude', 'angle2 degenerate', 'inflection'
- **Branch 15** @ line 884 — *Edge is marked as multi-edge (appears on multiple disjoint face pairs)* — COVERED by: ad086, bo005, bo022, bo028, gp013, gs025, gs028, hea015 (+28 more)
  - What it tests: Multi-edges are not mergeable (would violate topology).
  - Repair action: Skip this triplet; increment index.
- **Branch 16** @ line 890 — *Edge1 is not in the edge-to-faces map* — COVERED by: a018, ad086, twi047
  - What it tests: Checks if edge1 has recorded face associations.
  - Repair action: Leave theList1 empty; proceed with empty list.
- **Branch 17** @ line 894 — *Edge2 (middle/small edge) is not in the edge-to-faces map* — COVERED by: a018, ad086
  - What it tests: Checks if the small edge has recorded face associations.
  - Repair action: Leave theList2 empty; proceed with empty list.
- **Branch 18** @ line 898 — *Edge3 is not in the edge-to-faces map* — COVERED by: a018, ad086
  - What it tests: Checks if edge3 has recorded face associations.
  - Repair action: Leave theList3 empty; proceed with empty list.
- **Branch 19** @ line 905 — *Edge1 and edge2 have same face count AND compatible seam status* — **UNCOVERED**
  - What it tests: Checks if edge1 can be merged with edge2 based on face extent and seam markers.
  - Repair action: Set same_set1=true; check face membership.
  - Suggested fixture: defect mentioning 'same_set1', 'face extent match', 'seam compatible'
- **Branch 20** @ line 909 — *Edge3 and edge2 have same face count AND compatible seam status* — **UNCOVERED**
  - What it tests: Checks if edge3 can be merged with edge2 based on face extent and seam markers.
  - Repair action: Set same_set2=true; check face membership.
  - Suggested fixture: defect mentioning 'same_set2', 'face extent match', 'seam compatible'
- **Branch 21** @ line 917 — *same_set1 is true but not all faces of edge1 are in edge2's face set* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: Validates that edge1 and edge2 share the exact same set of faces.
  - Repair action: Set same_set1=false if any face of edge1 is missing from edge2.
- **Branch 22** @ line 927 — *same_set2 is true but not all faces of edge3 are in edge2's face set* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: Validates that edge3 and edge2 share the exact same set of faces.
  - Repair action: Set same_set2=false if any face of edge3 is missing from edge2.
- **Branch 23** @ line 937 — *Both neighbors (edge1 and edge3) can be merged with edge2 (same faces)* — **UNCOVERED**
  - What it tests: Both same_set1 and same_set2 are true; must choose which neighbor to merge.
  - Repair action: Choose the neighbor with smaller angle; set take_next accordingly.
  - Suggested fixture: defect mentioning 'same_set1 && same_set2', 'both merge', 'choose neighbor'
- **Branch 24** @ line 940 — *Angles differ by more than angular tolerance* — COVERED by: n047, tb012
  - What it tests: Checks if |Ang1 - Ang2| > Precision::Angular().
  - Repair action: Choose smaller angle; set take_next = (Ang2 < Ang1).
- **Branch 25** @ line 949 — *Merge would exceed the angular limit (both both neighbors have angles > aLimitAngle)* — COVERED by: pmi097
  - What it tests: Checks if minimum(Ang1, Ang2) > aLimitAngle when aModLimitAngle is true.
  - Repair action: Set isLimAngle=true; skip merge to avoid sharp corners.
- **Branch 26** @ line 951 — *Only edge1 can merge with edge2 (same_set1 true, same_set2 false)* — **UNCOVERED**
  - What it tests: Only first neighbor shares faces with middle edge.
  - Repair action: Set same_set=true; use Ang1 for limit check; merge with edge1.
  - Suggested fixture: defect mentioning 'same_set1 && !same_set2', 'asymmetric merge', 'one neighbor'
- **Branch 27** @ line 956 — *Only edge3 can merge with edge2 (!same_set1 true, same_set2 true)* — **UNCOVERED**
  - What it tests: Only second neighbor shares faces with middle edge.
  - Repair action: Set same_set=true; use Ang2 for limit check; merge with edge3; set take_next=true.
  - Suggested fixture: defect mentioning '!same_set1 && same_set2', 'asymmetric merge', 'one neighbor'
- **Branch 28** @ line 964 — *Merge is permitted: same_set=true and isLimAngle=false* — **UNCOVERED**
  - What it tests: Merger candidacy is established after all face/angle checks.
  - Repair action: Proceed to JoinEdges; merge the selected pair.
  - Suggested fixture: defect mentioning 'same_set && !isLimAngle', 'merge approved', 'join edges'
- **Branch 29** @ line 973 — *Current face is the one being processed (skip cross-face check for this face)* — COVERED by: a012, ad052, ad086, m060, pf030, xp007
  - What it tests: Checks if the face in theList2 is the current face (anExpf2.Current()).
  - Repair action: Skip this face in the isNeedJoin check; continue to next face.
- **Branch 30** @ line 981 — *Wire child is not WIRE type (in cross-face check)* — COVERED by: twi041
  - What it tests: Filters out non-wire children when checking other faces.
  - Repair action: Skip this child; continue to next.
- **Branch 31** @ line 992 — *Edges are not adjacent in the other face's wire (not consecutive)* — COVERED by: a011, a026, a032, a106, ad003, ad014, ad035, ad045 (+118 more)
  - What it tests: Checks if edge1 and edge2 are consecutive in the other face's wire.
  - Repair action: Set isNeedJoin=false; abort merge to prevent non-manifold topology.
- **Branch 32** @ line 1001 — *isNeedJoin is true after cross-face verification* — **UNCOVERED**
  - What it tests: Edges are ready to join (passed all cross-face checks).
  - Repair action: Call JoinEdges; record result in ReplaceFirst.
  - Suggested fixture: defect mentioning 'JoinEdges', 'merge approved', 'join call'
- **Branch 33** @ line 1015 — *JoinEdges returned null edge3 (merge failed)* — COVERED by: gb001, gb002, gb003, gb004, tsh053
  - What it tests: Checks if edge3 is null after JoinEdges attempt.
  - Repair action: Increment index; set status to FAIL1; skip vertex recording.
- **Branch 34** @ line 1026 — *Start vertex of merged edge is not yet mapped to new vertex* — COVERED by: a018, ad086
  - What it tests: Checks if oldV1 already exists in theNewVertices map.
  - Repair action: Create empty copy of oldV1 and record mapping.
- **Branch 35** @ line 1032 — *Start and end vertices of merged edge are different* — COVERED by: gp002, gs021, n009, n043, tfa019, twi099
  - What it tests: Checks if oldV1 != oldV2 (non-closed edge).
  - Repair action: Proceed to map oldV2 as well.
- **Branch 36** @ line 1034 — *End vertex of merged edge is not yet mapped to new vertex* — COVERED by: a018, ad086
  - What it tests: Checks if oldV2 already exists in theNewVertices map.
  - Repair action: Create empty copy of oldV2 and record mapping.
- **Branch 37** @ line 1046 — *Edge1 contains internal or external (NM) vertices* — COVERED by: ad086, tsh021, xp013
  - What it tests: Checks orientation of child vertices of edge1.
  - Repair action: Transfer NM vertices to merged edge3; replace in context.
- **Branch 38** @ line 1060 — *Edge2 contains internal or external (NM) vertices* — COVERED by: ad086, tsh021, xp013
  - What it tests: Checks orientation of child vertices of edge2.
  - Repair action: Transfer NM vertices to merged edge3; replace in context.
- **Branch 39** @ line 1077 — *ReplaceFirst is true (edge1 is the keeper edge)* — **UNCOVERED**
  - What it tests: Determines which of the two merged edges to keep as the primary.
  - Repair action: Replace edge1 with edge3; remove edge2.
  - Suggested fixture: defect mentioning 'ReplaceFirst', 'edge1 kept', 'edge2 removed'
- **Branch 40** @ line 1083 — *ReplaceFirst is false (edge2 is the keeper edge)* — **UNCOVERED**
  - What it tests: Edge2 survives the merge.
  - Repair action: Replace edge2 with edge3; remove edge1.
  - Suggested fixture: defect mentioning 'ReplaceFirst', 'edge2 kept', 'edge1 removed'
- **Branch 41** @ line 1089 — *Merged edge is placed at next position in wire* — **UNCOVERED**
  - What it tests: take_next is true; check if merged edge is still small.
  - Repair action: Set edge3 at next position; check if newsmall.
  - Suggested fixture: defect mentioning 'take_next', 'position next', 'small check'
- **Branch 42** @ line 1094 — *Merged edge is placed at prev position in wire* — **UNCOVERED**
  - What it tests: take_next is false; check if merged edge is still small.
  - Repair action: Set edge3 at prev position; check if newsmall.
  - Suggested fixture: defect mentioning 'take_next', 'position prev', 'small check'
- **Branch 43** @ line 1114 — *Merged edge is still small (newsmall=true)* — **UNCOVERED**
  - What it tests: After merging, the result is still below the small-edge threshold.
  - Repair action: Add edge3 to theSmallEdges for another pass.
  - Suggested fixture: defect mentioning 'newsmall', 'still small', 'iterative merge'
- **Branch 44** @ line 1122 — *Current face has small edges in theFaceWithSmall map* — COVERED by: a018, ad086
  - What it tests: Checks if the current face is bound in theFaceWithSmall.
  - Repair action: Update the edge list for this face.
- **Branch 45** @ line 1125 — *Merged edge is still small (newsmall=true within face update)* — COVERED by: a011, ad038, ad101, lh002, lh005, lh016, ls017, ls024 (+10 more)
  - What it tests: Newsmall flag within face-update context.
  - Repair action: Append edge3 to the face's edge list.
- **Branch 46** @ line 1133 — *Edge in face list matches one of the merged edges (edge1 or edge2)* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+32 more)
  - What it tests: Checks if edge in face's small-edge list is one of the merged edges.
  - Repair action: Remove that edge from the face's list.
- **Branch 47** @ line 1143 — *Face's edge list is now empty after cleanup* — COVERED by: ad015, ad050, gn010, m010, m018, m064, m069, os007 (+20 more)
  - What it tests: Checks if theEdges.Extent() == 0 after removing merged edges.
  - Repair action: Remove the face from theFaceWithSmall map (no more small edges on this face).
- **Branch 48** @ line 1152 — *Merge failed but aModeDrop is true (drop small edges instead)* — COVERED by: ad101, twi051
  - What it tests: Checks if aModeDrop (mode-toggle) is true when merge is not possible.
  - Repair action: Attempt to remove the middle edge instead of merging.
- **Branch 49** @ line 1158 — *take_next is true (drop edge1)* — COVERED by: a019, ad086, ad101, ad102, ls033, m028, m107, pf027 (+16 more)
  - What it tests: Determines which edge to remove when drop mode is active.
  - Repair action: Set remedge=edge1; remove it.
- **Branch 50** @ line 1162 — *take_next is false (drop edge2)* — COVERED by: a019, ad086, ad101, ad102, ls033, m028, m107, pf027 (+16 more)
  - What it tests: take_next false; drop the middle edge instead.
  - Repair action: Set remedge=edge2; remove it.
- **Branch 51** @ line 1170 — *After removing middle edge, neighbors are not properly connected (CheckConnected fails)* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+548 more)
  - What it tests: Checks if the remaining edges form a valid wire after the removal.
  - Repair action: Abort drop; skip this triplet; increment index.
- **Branch 52** @ line 1186 — *After drop, adjacent edges may need fixing (FixConnected/FixDegenerated)* — COVERED by: ad086, twi003, twi021
  - What it tests: Adjacency and degeneracy are checked and repaired.
  - Repair action: Call FixConnected and FixDegenerated on neighbors.
- **Branch 53** @ line 1203 — *After drop and fix, tmpedge1 is still small (in theSmallEdges)* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+895 more)
  - What it tests: Checks if the first neighbor is in the small-edge set.
  - Repair action: Remove old edge; add new edge (after context apply).
- **Branch 54** @ line 1228 — *After drop and fix, tmpedge2 is still small (in theSmallEdges)* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+895 more)
  - What it tests: Checks if the second neighbor is in the small-edge set.
  - Repair action: Remove old edge; add new edge (after context apply).
- **Branch 55** @ line 1262 — *Neither merge nor drop is possible (neither same_set nor aModeDrop)* — COVERED by: a010, a085, ad086, bo006, gn038, le039, ls031, m010 (+14 more)
  - What it tests: Fallback branch when both main strategies fail.
  - Repair action: Attempt last-resort removal (check if edge is a degenerate circle).
- **Branch 56** @ line 1274 — *Edge is a closed curve (circle-like) with significant span* — COVERED by: a084, ad086, gb004, gn015, gn023, gn035, gp023, gp024 (+76 more)
  - What it tests: Checks if distance at midpoint > distance at endpoint (circular arc).
  - Repair action: Skip removal; increment index.
- **Branch 57** @ line 1280 — *take_next && edge1 is a loop AND theList2.Extent() == 1 (single-face edge)* — COVERED by: gs002, hea001, hea009, m066, ps003, tb017, tfa043, tfa052 (+8 more)
  - What it tests: Edge1 connects a vertex to itself on a single face.
  - Repair action: Remove edge1; it's a degenerate seam.
- **Branch 58** @ line 1300 — *!take_next && edge2 is a loop AND theList2.Extent() == 1* — COVERED by: gs002, hea001, hea009, m066, ps003, tb017, tfa043, tfa052 (+8 more)
  - What it tests: Edge2 (middle edge) connects a vertex to itself on a single face.
  - Repair action: Remove edge2; it's a degenerate seam.
- **Branch 59** @ line 1331 — *Wire has exactly one edge remaining AND aModeDrop is true* — COVERED by: gs009, tb002, tb018, tsh019, twi002, twi019, twi037, twi045 (+3 more)
  - What it tests: After merging/dropping, only a single edge remains in the wire.
  - Repair action: If that edge is small, remove it and the wire itself.
- **Branch 60** @ line 1334 — *Remaining single edge is in theSmallEdges* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+895 more)
  - What it tests: The last edge in a wire is classified as small.
  - Repair action: Remove both edge and wire; they form a degenerate structure.
- **Branch 61** @ line 1346 — *Wire has multiple edges or drop mode is disabled* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+34 more)
  - What it tests: Normal case: wire has useful structure and should be kept.
  - Repair action: Call FixConnected to finalize wire; replace original in context.
- **Branch 62** @ line 1355 — *After all repairs on a face, the face has no wires (empty)* — COVERED by: a019, ad077, ad086, ad094, m028, tfa063, tsh023, tsh028 (+3 more)
  - What it tests: Checks if face is empty after context apply (iterator returns false).
  - Repair action: Remove the empty face from the shape.
- **Branch 63** @ line 1366 — *Wire is not lying on any face (free-standing wire)* — COVERED by: ad086, hea001, hea006, p017, tsh018, tsh037
  - What it tests: Detects wires in the shape that are not children of a face.
  - Repair action: Process these free wires separately.
- **Branch 64** @ line 1391 — *Free wire contains small edge (same logic as face-based)* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+898 more)
  - What it tests: Checks if current edge of free wire is in theSmallEdges.
  - Repair action: Evaluate merge/drop/removal.
- **Branch 65** @ line 1893 — *Free wire reduces to single edge AND aModeDrop* — COVERED by: ad086, gs009, hea001, hea006, p017, tb002, tb018, tsh019 (+8 more)
  - What it tests: After repairs on free wire, only one edge remains in drop mode.
  - Repair action: Remove the edge and wire if it's still small.


### `src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_ConvertSurfaceToBezierBasis.cxx`

2 methods, 25 branches, 14 covered.

#### `ShapeUpgrade_ConvertSurfaceToBezierBasis.Build` — lines 631–726
(5 branches, 4 covered.)

- **Branch 1** @ line 635 — *RECURSIVE_UNWRAP* — **UNCOVERED**
  - What it tests: Input surface is RectangularTrimmedSurface
  - Repair action: Extract basis surface for offset detection
  - Suggested fixture: defect mentioning 'RectangularTrimmedSurface', 'BasisSurface'
- **Branch 2** @ line 645 — *OFFSET_DETECTION* — COVERED by: gn021
  - What it tests: Extracted surface is OffsetSurface
  - Repair action: Flag offset and extract offset value for later re-application
- **Branch 3** @ line 667 — *U_PARAMETER_ALIGNMENT* — COVERED by: a003, a004, a013, a014, a028, a031, a032, a034 (+214 more)
  - What it tests: Current split value aligns with composite segment boundary
  - Repair action: Find matching segment index in pre-computed segments
- **Branch 4** @ line 679 — *V_PARAMETER_ALIGNMENT* — COVERED by: a003, a004, a013, a014, a028, a031, a032, a034 (+214 more)
  - What it tests: Current split value aligns with composite segment boundary
  - Repair action: Find matching segment index in pre-computed segments
- **Branch 5** @ line 703 — *OFFSET_REAPPLICATION* — COVERED by: gn021
  - What it tests: Segment comes from offset surface (isOffset flag set)
  - Repair action: Wrap extracted segment in OffsetSurface with original offset value

#### `ShapeUpgrade_ConvertSurfaceToBezierBasis.Compute` — lines 58–534
(20 branches, 10 covered.)

- **Branch 1** @ line 59 — *FINITE_BOUNDS_GUARD* — COVERED by: a106, ad001, ad003, ad005, ad015, ad033, ad077, ad085 (+252 more)
  - What it tests: Non-Segment mode: add finite bounds to split arrays
  - Repair action: Collect infinite bounds from input surface
- **Branch 2** @ line 87 — *RECURSIVE_UNWRAP* — **UNCOVERED**
  - What it tests: RectangularTrimmedSurface delegation
  - Repair action: Recursively convert basis surface, propagate split values back
  - Suggested fixture: defect mentioning 'RectangularTrimmedSurface', 'BasisSurface', 'converter.Compute'
- **Branch 3** @ line 103 — *RECURSIVE_UNWRAP* — COVERED by: gn021
  - What it tests: OffsetSurface delegation
  - Repair action: Recursively convert basis surface, propagate split values back
- **Branch 4** @ line 118 — *CONDITIONAL_MODE_DISPATCH* — **UNCOVERED**
  - What it tests: Plane surface with myPlaneMode flag
  - Repair action: Convert plane to 2x2 Bezier using corner points
  - Suggested fixture: defect mentioning 'Geom_Plane', 'myPlaneMode', 'BezierSurface'
- **Branch 5** @ line 152 — *BOUNDS_PRECISION_CHECK* — COVERED by: a095, ad014, ad077, ad085, ad086, ad099, ad117, fi001 (+121 more)
  - What it tests: Bezier surface covering full parameter range [0,1]
  - Repair action: Use original Bezier if bounds match, else segment it
- **Branch 6** @ line 177 — *CONDITIONAL_MODE_DISPATCH* — **UNCOVERED**
  - What it tests: BSpline surface with myBSplineMode flag
  - Repair action: Convert BSpline to Bezier patches with knot filtering
  - Suggested fixture: defect mentioning 'Geom_BSplineSurface', 'myBSplineMode', 'GeomConvert_BSplineSurfaceToBezierSurface'
- **Branch 7** @ line 203 — *PATCH_THINNESS_FILTER* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+77 more)
  - What it tests: U-direction: knot spacing smaller than precision
  - Repair action: Mark thin patches for rejection, filter from output array
- **Branch 8** @ line 219 — *PATCH_THINNESS_FILTER* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+77 more)
  - What it tests: V-direction: knot spacing smaller than precision
  - Repair action: Mark thin patches for rejection, filter from output array
- **Branch 9** @ line 281 — *KNOT_INSERTION_BOUNDARY_CHECK* — **UNCOVERED**
  - What it tests: U-knot insertion: knot lies within segment bounds
  - Repair action: Insert intermediate knots into split values from BSpline conversion
  - Suggested fixture: defect mentioning 'InsertBefore', 'valknot', 'ULast'
- **Branch 10** @ line 299 — *KNOT_INSERTION_BOUNDARY_CHECK* — **UNCOVERED**
  - What it tests: V-knot insertion: knot lies within segment bounds
  - Repair action: Insert intermediate knots into split values from BSpline conversion
  - Suggested fixture: defect mentioning 'InsertBefore', 'valknot', 'VLast'
- **Branch 11** @ line 317 — *CONDITIONAL_MODE_DISPATCH* — **UNCOVERED**
  - What it tests: SurfaceOfRevolution with myRevolutionMode flag
  - Repair action: Decompose revolution surface via basis curve conversion
  - Suggested fixture: defect mentioning 'Geom_SurfaceOfRevolution', 'myRevolutionMode', 'BasisCurve'
- **Branch 12** @ line 322 — *CURVE_UNWRAP* — **UNCOVERED**
  - What it tests: Basis curve is TrimmedCurve
  - Repair action: Unwrap to get underlying basis curve
  - Suggested fixture: defect mentioning 'Geom_TrimmedCurve', 'BasisCurve'
- **Branch 13** @ line 331 — *BASIS_CURVE_SPECIALIZATION* — COVERED by: a007, a024, a102, ad030, ad044, ad045, ad049, ad086 (+263 more)
  - What it tests: Basis curve of revolution is OffsetCurve
  - Repair action: Convert offset curve to Bezier, then re-apply offset
- **Branch 14** @ line 340 — *CONVERTER_STATUS_PROPAGATION* — **UNCOVERED**
  - What it tests: Curve converter succeeded (ShapeExtend_DONE)
  - Repair action: Propagate DONE status, otherwise set OK
  - Suggested fixture: defect mentioning 'converter.Status', 'ShapeExtend_DONE'
- **Branch 15** @ line 390 — *BOUNDS_PRESERVATION_CHECK* — COVERED by: gp023, le002, le010, m133, pf036, twi055, twi094, xp018
  - What it tests: Revolution surface covers full parameter range
  - Repair action: Use untrimmed revolution, else wrap in RectangularTrimmedSurface
- **Branch 16** @ line 418 — *KNOT_INSERTION_BOUNDARY_CHECK* — **UNCOVERED**
  - What it tests: V-knot insertion: knot lies within segment bounds
  - Repair action: Insert intermediate knots from curve split into V split values
  - Suggested fixture: defect mentioning 'InsertBefore', 'vSVal', 'VLast'
- **Branch 17** @ line 432 — *CONDITIONAL_MODE_DISPATCH* — COVERED by: gn021
  - What it tests: SurfaceOfLinearExtrusion with myExtrusionMode flag
  - Repair action: Decompose extrusion surface via basis curve conversion
- **Branch 18** @ line 490 — *KNOT_INSERTION_BOUNDARY_CHECK* — **UNCOVERED**
  - What it tests: U-knot insertion: knot lies within segment bounds
  - Repair action: Insert intermediate knots from curve split into U split values
  - Suggested fixture: defect mentioning 'InsertBefore', 'uSVal', 'ULast'
- **Branch 19** @ line 505 — *FALLBACK_GENERIC_HANDLER* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+483 more)
  - What it tests: Unknown or unhandled surface type (else clause)
  - Repair action: Wrap surface in RectangularTrimmedSurface if bounds differ
- **Branch 20** @ line 518 — *BOUNDS_PRESERVATION_CHECK* — COVERED by: a095, ad014, ad086, gb001, gn034, gp013, gp020, gp021 (+81 more)
  - What it tests: Unhandled surface covers full parameter range
  - Repair action: Use surface as-is if bounds match, else trim


### `src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_SplitSurface.cxx`

5 methods, 43 branches, 1 covered.

#### `ShapeUpgrade_SplitSurface.Build` — lines 241–635
(25 branches, 0 covered.)

- **Branch 1** @ line 248 — *split_performed_multi_segment* — **UNCOVERED**
  - What it tests: Split values exceed 2 elements in U or V direction
  - Repair action: Set DONE1 status to indicate segmentation occurred
  - Suggested fixture: defect mentioning 'myUSplitValues->Length() > 2 || myVSplitValues->Length() > 2'
- **Branch 2** @ line 255 — *surface_of_revolution_input* — **UNCOVERED**
  - What it tests: Input surface is a surface of revolution
  - Repair action: Split basis curve and reconstruct revolution surfaces
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_SurfaceOfRevolution))'
- **Branch 3** @ line 266 — *revolution_surface_multi_row_split* — **UNCOVERED**
  - What it tests: U-split has >2 values for revolution surface
  - Repair action: Create multi-row array of reconstructed revolution patches
  - Suggested fixture: defect mentioning 'myUSplitValues->Length() > 2', 'NewSurfaceRev'
- **Branch 4** @ line 291 — *revolution_surface_single_row_full_coverage* — **UNCOVERED**
  - What it tests: U-split has 2 values matching full surface bounds
  - Repair action: Directly assign revolution surface without trimming
  - Suggested fixture: defect mentioning 'UFirst == U1 && ULast == U2'
- **Branch 5** @ line 304 — *revolution_surface_single_row_partial_coverage* — **UNCOVERED**
  - What it tests: U-split has 2 values not matching full surface bounds
  - Repair action: Trim reconstructed revolution surface to parameter range
  - Suggested fixture: defect mentioning 'Geom_RectangularTrimmedSurface(NewSurfaceRev,'
- **Branch 6** @ line 319 — *revolution_basis_curve_split_status* — **UNCOVERED**
  - What it tests: Basis curve split propagates DONE1/DONE2/DONE3 status
  - Repair action: OR status flags from basis curve split into result
  - Suggested fixture: defect mentioning 'spc.Status(ShapeExtend_DONE', 'myStatus |='
- **Branch 7** @ line 334 — *surface_of_linear_extrusion_input* — **UNCOVERED**
  - What it tests: Input surface is a surface of linear extrusion
  - Repair action: Split basis curve and reconstruct extrusion surfaces
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_SurfaceOfLinearExtrusion))'
- **Branch 8** @ line 345 — *extrusion_surface_multi_col_split* — **UNCOVERED**
  - What it tests: V-split has >2 values for extrusion surface
  - Repair action: Create multi-column array of reconstructed extrusion patches
  - Suggested fixture: defect mentioning 'myVSplitValues->Length() > 2', 'NewSurfaceEx'
- **Branch 9** @ line 379 — *extrusion_surface_single_col_full_coverage* — **UNCOVERED**
  - What it tests: V-split has 2 values matching full surface bounds
  - Repair action: Directly assign extrusion surface without trimming
  - Suggested fixture: defect mentioning 'VFirst == V1 && VLast == V2'
- **Branch 10** @ line 385 — *extrusion_surface_single_col_partial_coverage* — **UNCOVERED**
  - What it tests: V-split has 2 values not matching full surface bounds
  - Repair action: Trim reconstructed extrusion surface to parameter range
  - Suggested fixture: defect mentioning 'Geom_RectangularTrimmedSurface(NewSurfaceEx,'
- **Branch 11** @ line 398 — *extrusion_basis_curve_split_status* — **UNCOVERED**
  - What it tests: Basis curve split propagates DONE1/DONE2/DONE3 status
  - Repair action: OR status flags from basis curve split into result
  - Suggested fixture: defect mentioning 'spc.Status(ShapeExtend_DONE', 'myStatus |='
- **Branch 12** @ line 413 — *trimmed_surface_recursion* — **UNCOVERED**
  - What it tests: Input is already a rectangular trimmed surface
  - Repair action: Unwrap basis surface and recursively process
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_RectangularTrimmedSurface))'
- **Branch 13** @ line 428 — *offset_surface_patch_reconstruction* — **UNCOVERED**
  - What it tests: Input surface is an offset surface
  - Repair action: Process basis surface recursively, then wrap patches in offsets
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_OffsetSurface))'
- **Branch 14** @ line 473 — *no_split_required_single_patch* — **UNCOVERED**
  - What it tests: Split produces exactly 1x1 patch with full bounds match
  - Repair action: Copy surface directly without trimming
  - Suggested fixture: defect mentioning 'myNbResultingRow == 1 && myNbResultingCol == 1'
- **Branch 15** @ line 484 — *single_patch_bspline_segment_not_requested* — **UNCOVERED**
  - What it tests: 1x1 patch for BSpline but Segment false or DONE2 not set
  - Repair action: Create trimmed surface instead of segmenting
  - Suggested fixture: defect mentioning '!Segment || !mySurface->IsKind(STANDARD_TYPE(Geom_BSplineSurface))'
- **Branch 16** @ line 505 — *bspline_knot_snapping* — **UNCOVERED**
  - What it tests: Multi-patch split with BSpline surface present
  - Repair action: Snap split values to nearest knots for both U and V
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_BSplineSurface))', 'UKnot', 'VKnot'
- **Branch 17** @ line 516 — *knot_snapping_u_above_split_value* — **UNCOVERED**
  - What it tests: U knot exceeds current split value by precision
  - Repair action: Skip to next knot
  - Suggested fixture: defect mentioning 'spval > BsSurface->UKnot(j) + Precision::PConfusion()'
- **Branch 18** @ line 520 — *knot_snapping_u_below_split_value* — **UNCOVERED**
  - What it tests: U knot below current split value by precision
  - Repair action: Snap split value to this knot
  - Suggested fixture: defect mentioning 'spval < BsSurface->UKnot(j) - Precision::PConfusion()'
- **Branch 19** @ line 538 — *knot_snapping_v_above_split_value* — **UNCOVERED**
  - What it tests: V knot exceeds current split value by precision
  - Repair action: Skip to next knot
  - Suggested fixture: defect mentioning 'spval > BsSurface->VKnot(j) + Precision::PConfusion()'
- **Branch 20** @ line 542 — *knot_snapping_v_below_split_value* — **UNCOVERED**
  - What it tests: V knot below current split value by precision
  - Repair action: Snap split value to this knot
  - Suggested fixture: defect mentioning 'spval < BsSurface->VKnot(j) - Precision::PConfusion()'
- **Branch 21** @ line 568 — *bspline_or_bezier_segment_attempt* — **UNCOVERED**
  - What it tests: Multi-patch with BSpline or Bezier surface type
  - Repair action: Attempt native Segment() call with exception handling
  - Suggested fixture: defect mentioning 'isBSpline || isBezier'
- **Branch 22** @ line 575 — *bspline_segment_operation* — **UNCOVERED**
  - What it tests: BSpline surface segmentation by parameter bounds
  - Repair action: Call Segment() on BSpline with U1,U2,V1,V2
  - Suggested fixture: defect mentioning 'BSplineSurface>(theNew)->Segment(U1, U2, V1, V2)'
- **Branch 23** @ line 577 — *bezier_segment_operation* — **UNCOVERED**
  - What it tests: Bezier surface segmentation by parameter bounds
  - Repair action: Call Segment() on Bezier with normalized parameters
  - Suggested fixture: defect mentioning 'BezierSurface>(theNew)->Segment(u1, u2, v1, v2)'
- **Branch 24** @ line 593 — *segment_operation_exception* — **UNCOVERED**
  - What it tests: Segmentation throws Standard_Failure exception
  - Repair action: Fall back to RectangularTrimmedSurface wrapping
  - Suggested fixture: defect mentioning 'catch (Standard_Failure const& anException)'
- **Branch 25** @ line 606 — *non_bspline_trimmed_split* — **UNCOVERED**
  - What it tests: Multi-patch with non-segmentable surface type
  - Repair action: Create RectangularTrimmedSurface for each patch
  - Suggested fixture: defect mentioning 'not a BSpline: trimming instead of segmentation'

#### `ShapeUpgrade_SplitSurface.Init_v1` — lines 61–78
(1 branches, 0 covered.)

- **Branch 1** @ line 71 — *surface_parameter_bounds* — **UNCOVERED**
  - What it tests: Extraction of surface parameter bounds via Bounds() call
  - Repair action: Initialize split values with full surface bounds
  - Suggested fixture: defect mentioning 'mySurface->Bounds(U1, U2, V1, V2)'

#### `ShapeUpgrade_SplitSurface.Init_v2` — lines 88–171
(9 branches, 1 covered.)

- **Branch 1** @ line 104 — *periodic_surface_u_partial_coverage* — **UNCOVERED**
  - What it tests: U-direction periodicity with partial parameter range
  - Repair action: Adjust U bounds to one full period from first parameter
  - Suggested fixture: defect mentioning 'IsUPeriodic()', 'UPeriod()'
- **Branch 2** @ line 109 — *periodic_surface_v_partial_coverage* — **UNCOVERED**
  - What it tests: V-direction periodicity with partial parameter range
  - Repair action: Adjust V bounds to one full period from first parameter
  - Suggested fixture: defect mentioning 'IsVPeriodic()', 'VPeriod()'
- **Branch 3** @ line 115 — *parameter_range_out_of_bounds_u* — **UNCOVERED**
  - What it tests: U parameter range completely outside surface bounds
  - Repair action: Use full surface U bounds when range is invalid
  - Suggested fixture: defect mentioning 'UFirst > U2 - precision || ULast < U1'
- **Branch 4** @ line 122 — *parameter_range_partial_overlap_u* — **UNCOVERED**
  - What it tests: U parameter range partially overlaps surface bounds
  - Repair action: Clamp U range to intersection with surface bounds
  - Suggested fixture: defect mentioning 'std::max(U1, UFirst)', 'std::min(U2, ULast)'
- **Branch 5** @ line 125 — *parameter_range_out_of_bounds_v* — **UNCOVERED**
  - What it tests: V parameter range completely outside surface bounds
  - Repair action: Use full surface V bounds when range is invalid
  - Suggested fixture: defect mentioning 'VFirst > V2 - precision || VLast < V1'
- **Branch 6** @ line 132 — *parameter_range_partial_overlap_v* — **UNCOVERED**
  - What it tests: V parameter range partially overlaps surface bounds
  - Repair action: Clamp V range to intersection with surface bounds
  - Suggested fixture: defect mentioning 'std::max(V1, VFirst)', 'std::min(V2, VLast)'
- **Branch 7** @ line 136 — *area_based_parameter_sizing* — COVERED by: ad003, ad030, gs037, tfa026
  - What it tests: Non-zero myArea triggers iso-curve length computation
  - Repair action: Calculate U and V sizes from mid-surface iso-curves for segmentation
- **Branch 8** @ line 154 — *parameter_range_too_small_u* — **UNCOVERED**
  - What it tests: U parameter interval below precision threshold
  - Repair action: Expand narrow U range symmetrically by precision/2
  - Suggested fixture: defect mentioning 'UL - UF < precision'
- **Branch 9** @ line 160 — *parameter_range_too_small_v* — **UNCOVERED**
  - What it tests: V parameter interval below precision threshold
  - Repair action: Expand narrow V range symmetrically by precision/2
  - Suggested fixture: defect mentioning 'VL - VF < precision'

#### `ShapeUpgrade_SplitSurface.SetUSplitValues` — lines 177–204
(4 branches, 0 covered.)

- **Branch 1** @ line 178 — *null_split_values_sequence* — **UNCOVERED**
  - What it tests: Null or empty U-split values sequence
  - Repair action: Skip processing and return early
  - Suggested fixture: defect mentioning 'UValues.IsNull()'
- **Branch 2** @ line 192 — *split_value_below_segment_start* — **UNCOVERED**
  - What it tests: U-split value falls before current segment start plus precision
  - Repair action: Skip to next candidate value via continue
  - Suggested fixture: defect mentioning 'UFirst + precision >= UValues->Value(i)'
- **Branch 3** @ line 196 — *split_value_above_segment_end* — **UNCOVERED**
  - What it tests: U-split value exceeds current segment end minus precision
  - Repair action: Break loop to move to next segment
  - Suggested fixture: defect mentioning 'ULast - precision <= UValues->Value(i)'
- **Branch 4** @ line 200 — *split_value_within_segment_bounds* — **UNCOVERED**
  - What it tests: U-split value lies strictly within segment interval
  - Repair action: Insert value into split sequence and increment segment index
  - Suggested fixture: defect mentioning 'InsertBefore(ku++, UValues->Value(i))'

#### `ShapeUpgrade_SplitSurface.SetVSplitValues` — lines 210–236
(4 branches, 0 covered.)

- **Branch 1** @ line 211 — *null_split_values_sequence* — **UNCOVERED**
  - What it tests: Null or empty V-split values sequence
  - Repair action: Skip processing and return early
  - Suggested fixture: defect mentioning 'VValues.IsNull()'
- **Branch 2** @ line 224 — *split_value_below_segment_start* — **UNCOVERED**
  - What it tests: V-split value falls before current segment start plus precision
  - Repair action: Skip to next candidate value via continue
  - Suggested fixture: defect mentioning 'VFirst + precision >= VValues->Value(i)'
- **Branch 3** @ line 228 — *split_value_above_segment_end* — **UNCOVERED**
  - What it tests: V-split value exceeds current segment end minus precision
  - Repair action: Break loop to move to next segment
  - Suggested fixture: defect mentioning 'VLast - precision <= VValues->Value(i)'
- **Branch 4** @ line 232 — *split_value_within_segment_bounds* — **UNCOVERED**
  - What it tests: V-split value lies strictly within segment interval
  - Repair action: Insert value into split sequence and increment segment index
  - Suggested fixture: defect mentioning 'InsertBefore(kv++, VValues->Value(i))'


### `src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_SplitSurfaceContinuity.cxx`

1 methods, 45 branches, 18 covered.

#### `ShapeUpgrade_SplitSurfaceContinuity.Compute` — lines 75–408
(45 branches, 18 covered.)

- **Branch 1** @ line 76 — *segment_mode_handling* — COVERED by: pf011
  - What it tests: When Segment=false, applies boundary conditions to split values
  - Repair action: Set boundary split values at surface bounds if not infinite
- **Branch 2** @ line 80 — *infinite_bound_detection* — COVERED by: a082, ad001, ad033, ad086, ad092, ad110, ad112, ad116 (+48 more)
  - What it tests: UFirst boundary is infinite vs finite
  - Repair action: Only add finite UFirst to split values
- **Branch 3** @ line 84 — *infinite_bound_detection* — **UNCOVERED**
  - What it tests: ULast boundary is infinite vs finite
  - Repair action: Only add finite ULast to split values
  - Suggested fixture: defect mentioning 'IsInfinite(UL)', 'myUSplitValues->Length'
- **Branch 4** @ line 88 — *infinite_bound_detection* — **UNCOVERED**
  - What it tests: VFirst boundary is infinite vs finite
  - Repair action: Only add finite VFirst to split values
  - Suggested fixture: defect mentioning 'IsInfinite(VF)', 'VF'
- **Branch 5** @ line 92 — *infinite_bound_detection* — **UNCOVERED**
  - What it tests: VLast boundary is infinite vs finite
  - Repair action: Only add finite VLast to split values
  - Suggested fixture: defect mentioning 'IsInfinite(VL)', 'myVSplitValues->Length'
- **Branch 6** @ line 104 — *insufficient_continuity* — **UNCOVERED**
  - What it tests: Surface continuity less than required criterion
  - Repair action: Mark surface as needing repair with DONE2 status
  - Suggested fixture: defect mentioning 'mySurface->Continuity()', 'myCriterion', 'ShapeExtend_DONE2'
- **Branch 7** @ line 108 — *split_required* — **UNCOVERED**
  - What it tests: Multiple split values in U or V dimension
  - Repair action: Mark surface as requiring splitting with DONE1 status
  - Suggested fixture: defect mentioning 'myUSplitValues->Length() > 2', 'myVSplitValues->Length() > 2'
- **Branch 8** @ line 113 — *surface_type_revolution* — **UNCOVERED**
  - What it tests: Surface is SurfaceOfRevolution type
  - Repair action: Delegate to curve continuity repair on basis curve in V direction
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_SurfaceOfRevolution))', 'ShapeUpgrade_SplitCurve3dContinuity'
- **Branch 9** @ line 117 — *revolution_early_exit* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Revolution surface already meets continuity and has minimal splits
  - Repair action: Skip processing for well-formed revolution surfaces
- **Branch 10** @ line 131 — *curve_repair_status_DONE1* — **UNCOVERED**
  - What it tests: Basis curve repair split the curve
  - Repair action: Propagate DONE1 split status from curve to surface
  - Suggested fixture: defect mentioning 'spc.Status(ShapeExtend_DONE1)', 'myStatus |='
- **Branch 11** @ line 135 — *curve_repair_status_DONE2* — **UNCOVERED**
  - What it tests: Basis curve continuity was insufficient
  - Repair action: Propagate DONE2 defect status from curve to surface
  - Suggested fixture: defect mentioning 'spc.Status(ShapeExtend_DONE2)', 'myStatus |='
- **Branch 12** @ line 139 — *curve_repair_status_DONE3* — **UNCOVERED**
  - What it tests: Basis curve was corrected in place
  - Repair action: Propagate DONE3 correction status from curve to surface
  - Suggested fixture: defect mentioning 'spc.Status(ShapeExtend_DONE3)', 'myStatus |='
- **Branch 13** @ line 145 — *surface_type_linear_extrusion* — **UNCOVERED**
  - What it tests: Surface is SurfaceOfLinearExtrusion type
  - Repair action: Delegate to curve continuity repair on basis curve in U direction
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_SurfaceOfLinearExtrusion))', 'ShapeUpgrade_SplitCurve3dContinuity'
- **Branch 14** @ line 149 — *extrusion_early_exit* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Extrusion surface already meets continuity and has minimal splits
  - Repair action: Skip processing for well-formed extrusion surfaces
- **Branch 15** @ line 163 — *curve_repair_status_DONE1_extruded* — COVERED by: ad086, gs032, gs046
  - What it tests: Extrusion basis curve split occurred
  - Repair action: Propagate DONE1 from curve repair to surface status
- **Branch 16** @ line 167 — *curve_repair_status_DONE2_extruded* — COVERED by: ad086, gs032, gs046
  - What it tests: Extrusion basis curve continuity defect
  - Repair action: Propagate DONE2 from curve repair to surface status
- **Branch 17** @ line 171 — *curve_repair_status_DONE3_extruded_update* — **UNCOVERED**
  - What it tests: Extrusion basis curve was modified
  - Repair action: Update extrusion surface with corrected basis curve
  - Suggested fixture: defect mentioning 'spc.Status(ShapeExtend_DONE3)', 'SetBasisCurve', 'aNewBascurve'
- **Branch 18** @ line 180 — *surface_type_trimmed* — **UNCOVERED**
  - What it tests: Surface is RectangularTrimmedSurface type
  - Repair action: Recursively process underlying basis surface with adjusted bounds
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_RectangularTrimmedSurface))', 'ShapeUpgrade_SplitSurfaceContinuity'
- **Branch 19** @ line 184 — *trimmed_early_exit* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Trimmed surface meets continuity and has minimal splits
  - Repair action: Skip processing for well-formed trimmed surfaces
- **Branch 20** @ line 210 — *surface_type_offset* — **UNCOVERED**
  - What it tests: Surface is OffsetSurface type
  - Repair action: Recursively process basis surface with elevated continuity criterion
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_OffsetSurface))', 'BasCriterion'
- **Branch 21** @ line 213 — *offset_criterion_mapping* — **UNCOVERED**
  - What it tests: Offset surface requires mapping C1->C2, C2->C3, C3/CN->CN
  - Repair action: Elevate continuity criterion for underlying basis surface
  - Suggested fixture: defect mentioning 'switch (myCriterion)', 'BasCriterion = GeomAbs_C2'
- **Branch 22** @ line 234 — *offset_early_exit* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Offset basis surface meets elevated criterion with minimal splits
  - Repair action: Skip processing for well-formed offset surfaces
- **Branch 23** @ line 255 — *surface_type_bspline* — **UNCOVERED**
  - What it tests: Surface is BSplineSurface or convertible to B-spline
  - Repair action: Copy surface for B-spline processing; exit if not B-spline
  - Suggested fixture: defect mentioning 'IsKind(STANDARD_TYPE(Geom_BSplineSurface))', 'Copy()'
- **Branch 24** @ line 259 — *non_bspline_rejection* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Surface cannot be converted to B-spline
  - Repair action: Exit method - cannot repair non-B-spline surfaces
- **Branch 25** @ line 264 — *bspline_sufficient_continuity* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: B-spline surface already meets continuity criterion
  - Repair action: Skip knot analysis for already-continuous surfaces
- **Branch 26** @ line 278 — *u_multiple_knots* — COVERED by: gn017, gs057
  - What it tests: B-spline has multiple internal U knots requiring analysis
  - Repair action: Iterate internal U knots to check and repair continuity
- **Branch 27** @ line 286 — *u_knot_range_before_split* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: U knot value is at or before segment start
  - Repair action: Skip knot analysis for knots before current segment
- **Branch 28** @ line 293 — *u_knot_range_after_split* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: U knot value is at or after segment end
  - Repair action: Stop U knot iteration for knots after current segment
- **Branch 29** @ line 297 — *u_knot_continuity_deficiency* — **UNCOVERED**
  - What it tests: U knot multiplicity causes insufficient continuity
  - Repair action: Attempt knot removal or mark for surface splitting
  - Suggested fixture: defect mentioning 'Continuity = UDeg - MyBSpline->UMultiplicity', 'if (Continuity < myCont)'
- **Branch 30** @ line 303 — *u_knot_removal_attempt* — **UNCOVERED**
  - What it tests: New multiplicity allows knot removal within tolerance
  - Repair action: RemoveUKnot to improve continuity
  - Suggested fixture: defect mentioning 'newMultiplicity >= 0', 'RemoveUKnot'
- **Branch 31** @ line 307 — *u_knot_post_removal_check* — **UNCOVERED**
  - What it tests: After removal, verify continuity meets criterion
  - Repair action: Recompute continuity from updated multiplicity
  - Suggested fixture: defect mentioning 'corrected && newMultiplicity > 0', 'Continuity = UDeg'
- **Branch 32** @ line 312 — *u_knot_removal_success* — **UNCOVERED**
  - What it tests: Continuity successfully corrected by knot removal
  - Repair action: Mark surface corrected; adjust indices if knot fully removed
  - Suggested fixture: defect mentioning 'if (corrected)', 'ShapeExtend_DONE3'
- **Branch 33** @ line 318 — *u_knot_full_removal_index_adjustment* — **UNCOVERED**
  - What it tests: Knot fully removed (multiplicity became zero)
  - Repair action: Decrement indices to account for removed knot
  - Suggested fixture: defect mentioning 'newMultiplicity == 0', 'iknot--', 'ULastInd--'
- **Branch 34** @ line 325 — *u_knot_removal_tolerance_failure* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Knot cannot be removed within tolerance
  - Repair action: Insert knot position as surface split value
- **Branch 35** @ line 340 — *v_multiple_knots* — COVERED by: gn017, gs057
  - What it tests: B-spline has multiple internal V knots requiring analysis
  - Repair action: Iterate internal V knots to check and repair continuity
- **Branch 36** @ line 350 — *v_knot_range_before_split* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: V knot value is at or before segment start
  - Repair action: Skip knot analysis for knots before current segment
- **Branch 37** @ line 354 — *v_knot_range_after_split* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: V knot value is at or after segment end
  - Repair action: Stop V knot iteration for knots after current segment
- **Branch 38** @ line 358 — *v_knot_continuity_deficiency* — **UNCOVERED**
  - What it tests: V knot multiplicity causes insufficient continuity
  - Repair action: Attempt knot removal or mark for surface splitting
  - Suggested fixture: defect mentioning 'Continuity = VDeg - MyBSpline->VMultiplicity', 'if (Continuity < myCont)'
- **Branch 39** @ line 364 — *v_knot_removal_attempt* — **UNCOVERED**
  - What it tests: New multiplicity allows knot removal within tolerance
  - Repair action: RemoveVKnot to improve continuity
  - Suggested fixture: defect mentioning 'newMultiplicity >= 0', 'RemoveVKnot'
- **Branch 40** @ line 368 — *v_knot_post_removal_check* — **UNCOVERED**
  - What it tests: After removal, verify continuity meets criterion
  - Repair action: Recompute continuity from updated multiplicity
  - Suggested fixture: defect mentioning 'corrected && newMultiplicity > 0', 'Continuity = VDeg'
- **Branch 41** @ line 373 — *v_knot_removal_success* — **UNCOVERED**
  - What it tests: Continuity successfully corrected by knot removal
  - Repair action: Mark surface corrected; adjust indices if knot fully removed
  - Suggested fixture: defect mentioning 'if (corrected)', 'ShapeExtend_DONE3'
- **Branch 42** @ line 379 — *v_knot_full_removal_index_adjustment* — **UNCOVERED**
  - What it tests: Knot fully removed (multiplicity became zero)
  - Repair action: Decrement indices to account for removed knot
  - Suggested fixture: defect mentioning 'newMultiplicity == 0', 'iknot--', 'VLastInd--'
- **Branch 43** @ line 386 — *v_knot_removal_tolerance_failure* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: Knot cannot be removed within tolerance
  - Repair action: Insert knot position as surface split value
- **Branch 44** @ line 399 — *bspline_correction_write_back* — **UNCOVERED**
  - What it tests: B-spline surface was modified by knot removal
  - Repair action: Update mySurface to reference corrected B-spline copy
  - Suggested fixture: defect mentioning 'if (Status(ShapeExtend_DONE3))', 'mySurface = MyBSpline'
- **Branch 45** @ line 404 — *final_split_check* — **UNCOVERED**
  - What it tests: Final check if any splits were introduced
  - Repair action: Set DONE1 status if multiple splits exist in U or V
  - Suggested fixture: defect mentioning 'myUSplitValues->Length() > 2', 'myVSplitValues->Length() > 2', 'ShapeExtend_DONE1'


### `src/ModelingAlgorithms/TKShHealing/ShapeUpgrade/ShapeUpgrade_UnifySameDomain.cxx`

12 methods, 151 branches, 68 covered.

#### `ShapeUpgrade_UnifySameDomain.Build` — lines 4455–4469
(2 branches, 0 covered.)

- **Branch 1** @ line 4458 — *FACE_UNIFICATION_ENABLED* — **UNCOVERED**
  - What it tests: Face unification flag is set
  - Repair action: Execute face unification algorithm
  - Suggested fixture: defect mentioning 'myUnifyFaces', 'UnifyFaces()'
- **Branch 2** @ line 4462 — *EDGE_UNIFICATION_ENABLED* — **UNCOVERED**
  - What it tests: Edge unification flag is set
  - Repair action: Execute edge unification algorithm
  - Suggested fixture: defect mentioning 'myUnifyEdges', 'UnifyEdges()'

#### `ShapeUpgrade_UnifySameDomain.FillHistory` — lines 4476–4558
(5 branches, 2 covered.)

- **Branch 1** @ line 4477 — *HISTORY_NOT_REQUESTED* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: History recording disabled
  - Repair action: Early return, skip history filling
- **Branch 2** @ line 4516 — *SHAPE_UNCHANGED_IN_RESULT* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Input shape present in result (not modified)
  - Repair action: Skip unmodified shape
- **Branch 3** @ line 4524 — *SHAPE_REMOVAL_DETECTION* — **UNCOVERED**
  - What it tests: Shape has no modified images
  - Repair action: Record shape as removed
  - Suggested fixture: defect mentioning 'IsEmpty', 'aUSDHistory->Remove'
- **Branch 4** @ line 4540 — *MODIFIED_IMAGE_DIFFERENT* — **UNCOVERED**
  - What it tests: Modified image is different from original
  - Repair action: Record shape-to-image modification
  - Suggested fixture: defect mentioning 'IsSame', 'AddModified', 'aUSDHistory'
- **Branch 5** @ line 4549 — *ALL_IMAGES_REMOVED* — **UNCOVERED**
  - What it tests: All modified images absent from result
  - Repair action: Record shape as removed
  - Suggested fixture: defect mentioning 'bRemoved', 'aUSDHistory->Remove'

#### `ShapeUpgrade_UnifySameDomain.Initialize` — lines 2991–3004
(9 branches, 0 covered.)

- **Branch 1** @ line 2992 — *SHAPE_ASSIGN* — **UNCOVERED**
  - What it tests: Set initial shape for processing
  - Repair action: Copy to both myInitShape and myShape
  - Suggested fixture: defect mentioning 'myInitShape = aShape', 'myShape = aShape'
- **Branch 2** @ line 2994 — *UNIFY_FLAGS_ASSIGN* — **UNCOVERED**
  - What it tests: Set unify behavior flags
  - Repair action: Record edge and face unification options
  - Suggested fixture: defect mentioning 'myUnifyEdges = UnifyEdges', 'myUnifyFaces = UnifyFaces'
- **Branch 3** @ line 2996 — *CONCAT_FLAG_ASSIGN* — **UNCOVERED**
  - What it tests: Set BSpline concatenation option
  - Repair action: Store concatenation behavior
  - Suggested fixture: defect mentioning 'myConcatBSplines = ConcatBSplines'
- **Branch 4** @ line 2998 — *STATE_CLEAR_CONTEXT* — **UNCOVERED**
  - What it tests: Clear transformation context
  - Repair action: Reset context for new shape
  - Suggested fixture: defect mentioning 'myContext->Clear()'
- **Branch 5** @ line 2999 — *STATE_CLEAR_KEEP* — **UNCOVERED**
  - What it tests: Clear shapes to preserve list
  - Repair action: Reset kept shapes set
  - Suggested fixture: defect mentioning 'myKeepShapes.Clear()'
- **Branch 6** @ line 3000 — *STATE_CLEAR_PLANES* — **UNCOVERED**
  - What it tests: Clear planar face cache
  - Repair action: Reset plane mapping
  - Suggested fixture: defect mentioning 'myFacePlaneMap.Clear()'
- **Branch 7** @ line 3001 — *STATE_CLEAR_EF_MAP* — **UNCOVERED**
  - What it tests: Clear edge-face map
  - Repair action: Reset topology mapping
  - Suggested fixture: defect mentioning 'myEFmap.Clear()'
- **Branch 8** @ line 3002 — *STATE_CLEAR_FACE_NEW* — **UNCOVERED**
  - What it tests: Clear face replacement map
  - Repair action: Reset face remapping
  - Suggested fixture: defect mentioning 'myFaceNewFace.Clear()'
- **Branch 9** @ line 3003 — *STATE_CLEAR_HISTORY* — **UNCOVERED**
  - What it tests: Clear modification history
  - Repair action: Reset history tracker
  - Suggested fixture: defect mentioning 'myHistory->Clear()'

#### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces` — lines 3192–4320
(62 branches, 59 covered.)

- **Branch 1** @ line 3217 — *Face has no surface (null geometry)* — COVERED by: a002, a003, a013, a014, a017, a018, a019, a020 (+747 more)
  - What it tests: Checks if face surface is null after ClearRts()
  - Repair action: Skip face, continue to next face
- **Branch 2** @ line 3210 — *Face already processed in previous iteration* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+1165 more)
  - What it tests: Membership in aProcessed set
  - Repair action: Skip face, continue to next
- **Branch 3** @ line 3240 — *Edge is degenerated* — COVERED by: a004, a006, a012, a013, a017, a019, a020, a023 (+646 more)
  - What it tests: BRep_Tool::Degenerated(edge)
  - Repair action: Skip edge, continue to next edge in sequence
- **Branch 4** @ line 3268 — *Non-manifold edge (not myAllowInternal mode and connectivity != 2)* — COVERED by: a003, a010, a019, a037, a075, a078, a085, a089 (+185 more)
  - What it tests: myAllowInternal flag + edge extent != 2 OR edge in keep/free boundary maps
  - Repair action: Skip non-manifold edge, do not unify across it
- **Branch 5** @ line 3276 — *Edge has < 2 adjacent faces in current shape* — COVERED by: a006, a013, a017, a028, a031, a064, a067, a070 (+588 more)
  - What it tests: aList.Extent() < 2
  - Repair action: Skip edge, continue to next edge
- **Branch 6** @ line 3283 — *Base surface is planar and input mode is not safe* — COVERED by: ad086, fi005, gp016, gp036, gs009, gs012, gs024, gs034 (+57 more)
  - What it tests: !mySafeInputMode && IsKind(Geom_Plane)
  - Repair action: Build PCurve for edge on planar face to optimize later operations
- **Branch 7** @ line 3298 — *Cannot compute normal to surface at edge (degenerate/singular point)* — COVERED by: a003, a019, a024, a095, ad047, ad086, ad116, bo002 (+329 more)
  - What it tests: !GetNormalToSurface(...) returns false
  - Repair action: Skip normal check for this face, proceed without angular tolerance validation
- **Branch 8** @ line 3304 — *Adjacent face is the current face itself* — COVERED by: a007, a010, a012, a026, a066, a095, a098, a101 (+349 more)
  - What it tests: aCheckedFace.IsSame(aFace)
  - Repair action: Skip same face, continue to next adjacent face
- **Branch 9** @ line 3309 — *Adjacent face already processed* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+936 more)
  - What it tests: aProcessed.Contains(aCheckedFace)
  - Repair action: Skip already-processed face, continue to next
- **Branch 10** @ line 3314 — *Shells of two faces differ (topology would break)* — COVERED by: a003, a004, a013, a014, a022, a028, a032, a034 (+326 more)
  - What it tests: !isSameSets(pFShells1, pFShells2)
  - Repair action: Do not unify faces from different shell sets, continue to next face
- **Branch 11** @ line 3324 — *Adjacent face normals diverge beyond angular tolerance* — COVERED by: a014, a019, a020, a024, ad014, ad047, ad086, ad096 (+394 more)
  - What it tests: bCheckNormals=true && anAngle > myAngTol
  - Repair action: Do not unify faces with misaligned normals, continue to next face
- **Branch 12** @ line 3330 — *Faces are not in same geometric domain* — COVERED by: a013, a018, a019, a020, a032, a035, a038, a100 (+203 more)
  - What it tests: !IsSameDomain(aFace, aCheckedFace, ...)
  - Repair action: Do not unify geometrically different faces, continue to next
- **Branch 13** @ line 3292 — *Cannot obtain normal to second face at edge* — COVERED by: a019, a024, ad047, ad086, ad116, bo005, bo024, bo025 (+201 more)
  - What it tests: !GetNormalToSurface(aCheckedFace, ...)
  - Repair action: Skip normal check, proceed without angular validation for this adjacent face
- **Branch 14** @ line 3356 — *Multiple faces unified and first face is planar (cache optimization)* — COVERED by: a018, ad086, fi005, gp016, gp036, gs009, gs012, gs024 (+58 more)
  - What it tests: faces.Length() > 1 && myFacePlaneMap.IsBound(faces(1))
  - Repair action: Update RefFace with cached plane to optimize geometry operations
- **Branch 15** @ line 3389 — *Keep edges exist and !myAllowInternal: faces with only multi-connected edges must be removed* — COVERED by: a004, a067, ad086, ad098, ad101, bo001, bo002, bo003 (+46 more)
  - What it tests: !aKeepEdges.IsEmpty() && !myAllowInternal
  - Repair action: Remove faces with no other connecting edges from unified set to avoid topology breaks
- **Branch 16** @ line 3413 — *Face with multi-connected edge has no connections to external faces* — COVERED by: a001, a004, a005, a019, a067, ad038, ad086, ad098 (+87 more)
  - What it tests: !hasConnectAnotherFaces after iterating face edges
  - Repair action: Remove face from unified set and restore its boundary edges to merged area
- **Branch 17** @ line 3419 — *Keep edges exist but already updated unified area boundaries* — COVERED by: ad103, gs057, gs058, hea003, le047, ls024, m003, m010 (+15 more)
  - What it tests: !faces.IsEmpty() after removal pass
  - Repair action: Second pass to remove faces if their keep edges are contained within remaining unified set
- **Branch 18** @ line 3384 — *Multi-connected edges exist and myAllowInternal=true: preserve as internal* — COVERED by: a032, a082, ad086, ad092, ad100, ad103, ad104, ad107 (+129 more)
  - What it tests: !aKeepEdges.IsEmpty() && myAllowInternal (else branch)
  - Repair action: Add multi-connected and keep edges as INTERNAL orientation in new face
- **Branch 19** @ line 3485 — *Edge with 2 PCurves (not seam) detected and BSpline concatenation enabled* — COVERED by: a022, ad043, ad086, bo006, bo025, bo027, bo028, gn016 (+123 more)
  - What it tests: myConcatBSplines && !EdgeWith2pcurves.IsNull() && !SeamFound
  - Repair action: Check continuity of faces across edge; if G1+ smooth, may convert surface to periodic
- **Branch 20** @ line 3473 — *Found seam edge (U or V periodic closure)* — COVERED by: ad086, bo006, bo027, bo028, gn019, gn033, gp002, gp005 (+100 more)
  - What it tests: BRep_Tool::IsClosed && BRepTools::IsReallyClosed
  - Repair action: Mark seam type (U or V) for later periodic-surface handling
- **Branch 21** @ line 3495 — *Edge with 2 PCurves has smooth continuation (G1+)* — COVERED by: a022, a083, ad003, ad015, ad038, ad043, ad059, ad080 (+109 more)
  - What it tests: aIsEdgeWith2pcurvesSmooth = (anOrderOfCont >= GeomAbs_G1)
  - Repair action: Consider converting base surface to periodic BSpline to merge the edge smoothly
- **Branch 22** @ line 3509 — *Base surface is not BSpline but periodic edge detected and smooth continuation exists* — COVERED by: ad003, ad015, ad045, ad059, ad086, gb003, gn001, gn002 (+89 more)
  - What it tests: aIsEdgeWith2pcurvesSmooth && aBSplineSurface.IsNull()
  - Repair action: Approximate non-BSpline surface to BSpline to enable periodicity conversion
- **Branch 23** @ line 3525 — *Non-periodic surface can be made periodic in U direction* — COVERED by: ad086, gb003, gn019, gn031, gn033, gp005, gp011, gp012 (+41 more)
  - What it tests: anIsUclosed && Uperiod == 0.
  - Repair action: Set U-periodicity on BSpline surface and update RefFace PCurves
- **Branch 24** @ line 3531 — *Non-periodic surface can be made periodic in V direction* — COVERED by: ad086, gb003, gn019, gn031, gn033, gp005, gp011, gp012 (+41 more)
  - What it tests: !anIsUclosed && Vperiod == 0.
  - Repair action: Set V-periodicity on BSpline surface and update RefFace PCurves
- **Branch 25** @ line 3542 — *Surface was approximated to BSpline; old RefFace PCurves need migration* — **UNCOVERED**
  - What it tests: aBSplineSurface != aBaseSurface (approximation occurred)
  - Repair action: Update all edges with new PCurves on approximated surface, remove old temporary PCurves
  - Suggested fixture: defect mentioning 'OldRefFace', 'UpdateEdge', 'MapEdgesWithTemporaryPCurves'
- **Branch 26** @ line 3569 — *No seam found in U direction but surface is U-periodic* — **UNCOVERED**
  - What it tests: Uperiod != 0. && !UseamFound
  - Repair action: Try to relocate PCurves to new U-origin to fit all faces in [origin, origin+period]
  - Suggested fixture: defect mentioning 'FindCoordBounds', 'Uperiod', 'UseamFound'
- **Branch 27** @ line 3576 — *No seam found in V direction but surface is V-periodic* — **UNCOVERED**
  - What it tests: Vperiod != 0. && !VseamFound
  - Repair action: Try to relocate PCurves to new V-origin to fit all faces in [origin, origin+period]
  - Suggested fixture: defect mentioning 'FindCoordBounds', 'Vperiod', 'VseamFound'
- **Branch 28** @ line 3587 — *FindCoordBounds fails to compute coordinate bounds* — COVERED by: a001, a003, a004, a013, a014, a028, a032, a034 (+482 more)
  - What it tests: !FindCoordBounds(...)
  - Repair action: Break coordinate relocation, proceed with existing periodic arrangement
- **Branch 29** @ line 3594 — *Coordinate span (max - min) exceeds period tolerance* — COVERED by: a082, ad005, ad033, ad086, ad092, bo006, bo027, bo028 (+166 more)
  - What it tests: aMaxCoord - aMinCoord > aPeriods[ii] - 1.e-5
  - Repair action: Mark as seam found; cannot relocate without breaking faces
- **Branch 30** @ line 3599 — *Coordinate span < period AND only 2 face intervals exist (relocation needed)* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: aMaxCoord - aMinCoord <= period && aNumberOfIntervals == 2
  - Repair action: Relocate PCurves to new origin to fit faces within period window
- **Branch 31** @ line 3639 — *Relocated PCurves now exceed period boundaries (cannot fit in window)* — COVERED by: a004, a012, a019, a020, a023, a034, a065, a068 (+235 more)
  - What it tests: NewCoordMax - NewCoordMin >= aPeriods[ii] - CoordTol OR coords outside [0, period]
  - Repair action: Skip relocation for this direction; keep original PCurves
- **Branch 32** @ line 3655 — *Relocated coordinates fit in period window; need to apply to surface origin* — COVERED by: a066, ad103, bo030, m050, twi038, twi090, xp027
  - What it tests: NewCoordMax - NewCoordMin < aPeriods[ii] - CoordTol (else from 31)
  - Repair action: Create RectangularTrimmedSurface with new origin; update RefFace and edge PCurves
- **Branch 33** @ line 3665 — *New coordinate origin would be below surface minimum bound* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+605 more)
  - What it tests: NewCoordOrigin < aSurfMin[ii]
  - Repair action: Clamp new origin to surface minimum; do not use trimmed surface
- **Branch 34** @ line 3701 — *Surface is closed but not periodic in U or V (need to detect implied period)* — COVERED by: a106, ad001, ad003, ad005, ad015, ad033, ad077, ad086 (+226 more)
  - What it tests: Uperiod == 0 && aSurf->IsUClosed() OR Vperiod == 0 && aSurf->IsVClosed()
  - Repair action: Set Uperiod/Vperiod from surface bounds (Ulast - Ufirst, Vlast - Vfirst)
- **Branch 35** @ line 3707 — *Base surface is RectangularTrimmedSurface (nested geometry)* — COVERED by: ad086, ad112, gn016, gn017, gn018, gn038, gp010, gs026 (+16 more)
  - What it tests: aSurf->IsKind(Geom_RectangularTrimmedSurface)
  - Repair action: Unwrap to basis surface to access true periodic properties
- **Branch 36** @ line 3764 — *Edge has no PCurve on reference face (degenerated or missing)* — COVERED by: a024, ad046, ad050, ad086, ad099, ad101, fi002, gb004 (+139 more)
  - What it tests: aBAcurve.Curve().IsNull()
  - Repair action: Skip edge, continue to next edge in wire-building loop
- **Branch 37** @ line 3781 — *All edges are degenerated in current wire segment* — COVERED by: a038, a088, ad084, ad086, gn014, m026, m109, m160 (+25 more)
  - What it tests: BRep_Tool::Degenerated(StartEdge) && istart < edges.Length()
  - Repair action: Advance to next edge, trying to find non-degenerated edge for wire start
- **Branch 38** @ line 3794 — *Selected start edge has no PCurve on reference face* — COVERED by: a004, a067, ad046, ad086, ad098, ad101, gp001, gp019 (+41 more)
  - What it tests: StartPCurve.IsNull()
  - Repair action: Remove edge from sequence and continue to next edge
- **Branch 39** @ line 3818 — *Current vertex has no adjacent edges in VEmap* — COVERED by: ad086, ad101, bo006, bo027, bo028, gn019, gn033, gp002 (+110 more)
  - What it tests: Elist.IsEmpty()
  - Repair action: Check if wire is closed (back to start); if yes, break; else try seam reconstruction
- **Branch 40** @ line 3827 — *Wire crosses parametric period boundary (seam present in edges)* — COVERED by: a028, a032, ad043, ad056, ad080, ad086, bo001, bo002 (+160 more)
  - What it tests: (Uperiod != 0 && |StartX - CurX| > Uperiod/2) OR (Vperiod != 0 && |StartY - CurY| > Vperiod/2)
  - Repair action: Reconstruct missing seam edge from removed-edges list; add to wire
- **Branch 41** @ line 3846 — *Current vertex is singular point (on singularity in parametric space)* — COVERED by: ad015, ad059, ad064, ad086, gb002, gn002, gn003, gn007 (+22 more)
  - What it tests: IsOnSingularity(Elist) = true
  - Repair action: Do not mark as splitting vertex; continue edge selection
- **Branch 42** @ line 3850 — *Current vertex has multiple candidate next edges (not on singularity)* — COVERED by: a004, a013, a014, a017, a028, a031, a064, a072 (+262 more)
  - What it tests: !anIsOnSingularity && Elist.Extent() > 1
  - Repair action: Add vertex to SplittingVertices; will need to split wire here later
- **Branch 43** @ line 3877 — *Multiple candidate edges but already used/invalid; single edge valid OR periodic surface* — COVERED by: ad014, ad086, ad096, ad114, bo025, bo028, fi001, fi005 (+165 more)
  - What it tests: TmpElist.Extent() <= 1 OR (Uperiod != 0 OR Vperiod != 0)
  - Repair action: Use TmpElist directly without angle-based selection
- **Branch 44** @ line 3869 — *Multiple unused candidate edges from current vertex on non-periodic surface* — COVERED by: a007, a024, ad014, ad030, ad044, ad049, ad086, ad096 (+246 more)
  - What it tests: TmpElist.Extent() > 1 AND Uperiod == 0 AND Vperiod == 0
  - Repair action: Select next edge by maximum turn angle (closest direction continuation)
- **Branch 45** @ line 3913 — *Next edge starting point differs from current point by coordinates* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: DiffU > CoordTol OR DiffV > CoordTol (non-seam case)
  - Repair action: Skip this candidate edge; may be degenerated vertex; try next
- **Branch 46** @ line 3918 — *Next edge coordinate differs from current by approximately period value* — COVERED by: a028, a032, ad043, ad056, ad080, ad086, bo001, bo002 (+216 more)
  - What it tests: (Uperiod != 0 && DiffU > Uperiod/2) OR (Vperiod != 0 && DiffV > Vperiod/2)
  - Repair action: Reconstruct missed seam edge to bridge period boundary; check for wire end
- **Branch 47** @ line 3929 — *Found all edges to complete wire; seam reconstruction returned end-of-wire flag* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+92 more)
  - What it tests: EndOfWire = true
  - Repair action: Break inner edge-selection loop; close current wire
- **Branch 48** @ line 3947 — *No next edge found, but surface is periodic; vertices may match in parametric space* — COVERED by: ad086, gb003, gn019, gn031, gn033, gp005, gp011, gp012 (+40 more)
  - What it tests: NextEdge.IsNull() && (Uperiod != 0 OR Vperiod != 0)
  - Repair action: Check if back at start vertex with small parametric distance; if yes, close wire; else reconstruct seam
- **Branch 49** @ line 3975 — *Wire-building failed: no next edge found and surface is non-periodic* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+465 more)
  - What it tests: NextEdge.IsNull() && Uperiod == 0 && Vperiod == 0
  - Repair action: Return early (abort IntUnifyFaces); wire topology is broken
- **Branch 50** @ line 3990 — *Seam reconstruction returned null edge despite periodic surface* — COVERED by: a004, a013, a020, a034, a097, ad005, ad014, ad015 (+287 more)
  - What it tests: NextEdge.IsNull() after ReconstructMissedSeam on periodic
  - Repair action: Return early (abort); seam cannot be reconstructed
- **Branch 51** @ line 4030 — *Wire contains edge on surface boundary (seam or boundary edge)* — COVERED by: a028, a032, ad043, ad056, ad080, ad086, bo001, bo002 (+207 more)
  - What it tests: BRep_Tool::IsClosed(anEdge, RefFace)
  - Repair action: Mark EdgeOnBoundOfSurfFound; cannot be hole; must create separate face
- **Branch 52** @ line 4041 — *Wire with boundary edge found; create standalone face* — COVERED by: a099, a102, ad026, ad082, ad086, bo001, bo002, bo003 (+120 more)
  - What it tests: EdgeOnBoundOfSurfFound = true
  - Repair action: Make new face with this wire as outer boundary; add to NewFaces sequence
- **Branch 53** @ line 4045 — *Wire is internal (hole) and may need splitting* — COVERED by: a030, a032, a082, a100, ad086, ad092, ad100, ad103 (+233 more)
  - What it tests: !EdgeOnBoundOfSurfFound (else branch)
  - Repair action: If SplittingVertices not empty, split wire at those vertices; else save wire as-is for insertion
- **Branch 54** @ line 4049 — *Internal wire has splitting vertices (must be split into multiple holes)* — COVERED by: a004, a013, a014, a077, ad086, bo005, bo006, bo022 (+131 more)
  - What it tests: !SplittingVertices.IsEmpty()
  - Repair action: Call SplitWire to break wire at singular points and create multiple hole wires
- **Branch 55** @ line 4053 — *Internal wire has no splitting vertices* — COVERED by: a011, a103, ad015, ad038, ad045, ad050, ad086, ad099 (+224 more)
  - What it tests: SplittingVertices.IsEmpty() (else of 54)
  - Repair action: Add wire directly to NewWires sequence
- **Branch 56** @ line 4061 — *Internal edges exist; must build wires from them* — COVERED by: a001, a017, a018, a026, a066, a098, a107, ad026 (+158 more)
  - What it tests: !InternalEdges.IsEmpty()
  - Repair action: Iterate internal edges to build connected wires; same topology as outer wires
- **Branch 57** @ line 4068 — *Internal wire is already closed (single edge or loop)* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+347 more)
  - What it tests: VV[0].IsSame(VV[1])
  - Repair action: Break edge-extending loop; internal wire is complete
- **Branch 58** @ line 4083 — *Cannot find next internal edge to extend current wire* — COVERED by: a071, a097, ad086, ad101, bo028, gn002, gn038, gs005 (+54 more)
  - What it tests: !found after iterating both end vertices
  - Repair action: Break edge-extending loop; internal wire building is complete (open wire)
- **Branch 59** @ line 4118 — *No new faces created; single merged face with holes and internal wires* — COVERED by: bo003, gs002, gs057, hea001, hea009, m066, m165, pf006 (+26 more)
  - What it tests: NewFaces.IsEmpty()
  - Repair action: Create single face with all NewWires as holes and InternalWires as internal; merge old faces
- **Branch 60** @ line 4143 — *Exactly one new face created; insert holes and internal wires into it* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1274 more)
  - What it tests: NewFaces.Length() == 1
  - Repair action: Add all NewWires and InternalWires to single NewFace; merge old faces
- **Branch 61** @ line 4155 — *Multiple new faces created; distribute holes and internal wires among them* — COVERED by: a001, a010, a011, a014, a018, a019, a022, a028 (+105 more)
  - What it tests: else (NewFaces.Length() > 1)
  - Repair action: Call InsertWiresIntoFaces twice to distribute NewWires and InternalWires to correct faces
- **Branch 62** @ line 4155 — *Edge belongs to old face that is mapped to current new face* — COVERED by: a001, a002, a003, a004, a006, a007, a008, a009 (+1133 more)
  - What it tests: Emaps(jj).Contains(anEdge)
  - Repair action: Add corresponding old face to facesForThisFace sequence for merging

#### `ShapeUpgrade_UnifySameDomain.KeepShapes` — lines 3034–3043
(1 branches, 0 covered.)

- **Branch 1** @ line 3038 — *KEEP_SHAPE_TYPE_GUARD* — **UNCOVERED**
  - What it tests: Guard against non-EDGE/non-VERTEX shape preservation
  - Repair action: Skip non-edge and non-vertex shapes
  - Suggested fixture: defect mentioning 'ShapeType', 'TopAbs_EDGE', 'TopAbs_VERTEX'

#### `ShapeUpgrade_UnifySameDomain.MergeEdges` — lines 2763–2877
(11 branches, 0 covered.)

- **Branch 1** @ line 2776 — *VERTEX_ORIENTATION_VALID* — **UNCOVERED**
  - What it tests: Vertex has FORWARD or REVERSED orientation
  - Repair action: Add vertex to V-E mapping
  - Suggested fixture: defect mentioning 'aV.Orientation() == TopAbs_FORWARD || aV.Orientation() == TopAbs_REVERSED'
- **Branch 2** @ line 2812 — *NULL_VERTEX_ENDPOINT* — **UNCOVERED**
  - What it tests: Chain endpoint vertex is null
  - Repair action: Break chain extension loop
  - Suggested fixture: defect mentioning 'V[j].IsNull()'
- **Branch 3** @ line 2820 — *EDGE_ALREADY_USED* — **UNCOVERED**
  - What it tests: Candidate edge already in another chain
  - Repair action: Skip; do not add to current chain
  - Suggested fixture: defect mentioning '!aUsedEdges.Contains(edge)'
- **Branch 4** @ line 2825 — *VERTEX_ALIGNMENT_CHECK* — **UNCOVERED**
  - What it tests: Candidate vertex properly oriented at junction
  - Repair action: Add edge to chain in correct direction
  - Suggested fixture: defect mentioning 'V2[1 - j].IsEqual(V[j].Reversed())'
- **Branch 5** @ line 2827 — *CHAIN_PREPEND_LEFT* — **UNCOVERED**
  - What it tests: Extend chain at left (j=0)
  - Repair action: Prepend edge to chain
  - Suggested fixture: defect mentioning 'j == 0', 'aChain.Prepend'
- **Branch 6** @ line 2833 — *CHAIN_APPEND_RIGHT* — **UNCOVERED**
  - What it tests: Extend chain at right (j=1)
  - Repair action: Append edge to chain
  - Suggested fixture: defect mentioning 'j == 1', 'aChain.Append'
- **Branch 7** @ line 2845 — *SINGLE_EDGE_SKIP* — **UNCOVERED**
  - What it tests: Chain has fewer than 2 edges
  - Repair action: Skip; no merge needed
  - Suggested fixture: defect mentioning 'aChain.Length() < 2'
- **Branch 8** @ line 2851 — *CLOSED_LOOP_DETECTION* — **UNCOVERED**
  - What it tests: Chain endpoints are same vertex
  - Repair action: Mark as closed for processing
  - Suggested fixture: defect mentioning 'V[0].IsSame(V[1])'
- **Branch 9** @ line 2858 — *CHAIN_SPLIT_BY_NONMERGE* — **UNCOVERED**
  - What it tests: Split chain at vertices marked non-mergeable
  - Repair action: Generate subsequences respecting constraints
  - Suggested fixture: defect mentioning 'generateSubSeq'
- **Branch 10** @ line 2867 — *SUBSEQUENCE_TOO_SHORT* — **UNCOVERED**
  - What it tests: Subsequence has fewer than 2 edges
  - Repair action: Skip; no merge performed
  - Suggested fixture: defect mentioning 'SeqOfSubSeqOfEdges(i).SeqsEdges.Length() < 2'
- **Branch 11** @ line 2871 — *SUBSEQUENCE_MERGE* — **UNCOVERED**
  - What it tests: Attempt to merge subsequence
  - Repair action: Call MergeSubSeq; record result in UnionEdges
  - Suggested fixture: defect mentioning 'MergeSubSeq'

#### `ShapeUpgrade_UnifySameDomain.MergeSeq` — lines 2890–2906
(3 branches, 0 covered.)

- **Branch 1** @ line 2892 — *MERGE_EDGES_CALL* — **UNCOVERED**
  - What it tests: MergeEdges processes sequence
  - Repair action: Get subsequences with union edges
  - Suggested fixture: defect mentioning 'MergeEdges'
- **Branch 2** @ line 2896 — *NULL_UNION_EDGE_SKIP* — **UNCOVERED**
  - What it tests: Subsequence has no valid union edge
  - Repair action: Skip; do not merge into context
  - Suggested fixture: defect mentioning 'UnionEdges.IsNull()'
- **Branch 3** @ line 2901 — *CONTEXT_MERGE_APPLY* — **UNCOVERED**
  - What it tests: Union edge created successfully
  - Repair action: Merge subsequence edges into context
  - Suggested fixture: defect mentioning 'myContext->Merge'

#### `ShapeUpgrade_UnifySameDomain.MergeSubSeq` — lines 2170–2501
(17 branches, 0 covered.)

- **Branch 1** @ line 2184 — *DEGENERATED_EDGE_PAIR* — **UNCOVERED**
  - What it tests: Both edges in pair are degenerated curves
  - Repair action: Construct new degenerated edge from 2D points
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated'
- **Branch 2** @ line 2249 — *NULL_3D_CURVE* — **UNCOVERED**
  - What it tests: 3D curve extraction fails
  - Repair action: Abort merge; cannot handle null curve
  - Suggested fixture: defect mentioning 'c3d1.IsNull() || c3d2.IsNull()'
- **Branch 3** @ line 2254 — *TRIMMED_CURVE_UNWRAP* — **UNCOVERED**
  - What it tests: Curve is trimmed; extract basis
  - Repair action: Unwrap to underlying curve
  - Suggested fixture: defect mentioning 'Geom_TrimmedCurve'
- **Branch 4** @ line 2264 — *LINEAR_EDGE_PAIR* — **UNCOVERED**
  - What it tests: Both edges are linear; check parallel
  - Repair action: Mark union possible if parallel
  - Suggested fixture: defect mentioning 'IsLinear', '!aDir1.IsParallel'
- **Branch 5** @ line 2277 — *CIRCLE_EDGE_PAIR* — **UNCOVERED**
  - What it tests: Both edges are circles; check concentric
  - Repair action: Mark union possible if same center
  - Suggested fixture: defect mentioning 'Geom_Circle', 'P01.Distance(P02)'
- **Branch 6** @ line 2293 — *BOTH_UNIONS_IMPOSSIBLE* — **UNCOVERED**
  - What it tests: Both line and circle unions fail
  - Repair action: Return false; cannot merge
  - Suggested fixture: defect mentioning 'IsUnionOfLinesPossible && IsUnionOfCirclesPossible'
- **Branch 7** @ line 2307 — *SAFE_MODE_VERTEX_COPY* — **UNCOVERED**
  - What it tests: Safe input mode; vertex not yet recorded
  - Repair action: Copy and record vertex for tracking
  - Suggested fixture: defect mentioning 'mySafeInputMode', 'myContext->IsRecorded'
- **Branch 8** @ line 2323 — *LINEAR_UNION_BUILD* — **UNCOVERED**
  - What it tests: Union of parallel lines succeeds
  - Repair action: Build new edge with merged line curve
  - Suggested fixture: defect mentioning 'IsUnionOfLinesPossible', 'new Geom_Line'
- **Branch 9** @ line 2354 — *CIRCLE_CHAIN_CLOSED* — **UNCOVERED**
  - What it tests: Circle chain start and end vertices match
  - Repair action: Create closed circle edge
  - Suggested fixture: defect mentioning 'V[0].IsSame(V[1])'
- **Branch 10** @ line 2361 — *CIRCLE_CHAIN_NEARLY_CLOSED* — **UNCOVERED**
  - What it tests: Vertices very close but not identical
  - Repair action: Force closure by setting V[1]=V[0]
  - Suggested fixture: defect mentioning 'aP0.SquareDistance(aP1) < aTol * aTol'
- **Branch 11** @ line 2375 — *CIRCLE_CLOSED_FP_ZERO* — **UNCOVERED**
  - What it tests: First parameter is ~zero; use standard circle
  - Repair action: Use original circle directly
  - Suggested fixture: defect mentioning 'std::abs(FP) < Precision::PConfusion()'
- **Branch 12** @ line 2394 — *CIRCLE_CLOSED_FP_NONZERO* — **UNCOVERED**
  - What it tests: First parameter nonzero; reconstruct circle
  - Repair action: Build new circle from 3 points
  - Suggested fixture: defect mentioning 'GC_MakeCircle'
- **Branch 13** @ line 2408 — *CIRCLE_OPEN_CHAIN* — **UNCOVERED**
  - What it tests: Circle edge chain is open (not closed)
  - Repair action: Compute arc parameters
  - Suggested fixture: defect mentioning 'else // open chain'
- **Branch 14** @ line 2432 — *CIRCLE_PARAM_ANGLE_LIMIT* — **UNCOVERED**
  - What it tests: Arc angle exceeds 7π/8 radians
  - Repair action: Bisect parameter to limit arc
  - Suggested fixture: defect mentioning 'std::abs(ParamLast - ParamFirst) > 7 * M_PI / 8'
- **Branch 15** @ line 2447 — *CIRCLE_ARC_NEGATIVE_ANGLE* — **UNCOVERED**
  - What it tests: Computed arc angle is negative
  - Repair action: Add 2π to normalize to positive
  - Suggested fixture: defect mentioning 'lpar < 0.'
- **Branch 16** @ line 2463 — *BSPLINE_CONCAT_FALLBACK* — **UNCOVERED**
  - What it tests: All edges are BSpline/Bezier curves
  - Repair action: Attempt GLUEedgesWith3DCurves
  - Suggested fixture: defect mentioning 'myConcatBSplines', 'theChain.Length() > 1'
- **Branch 17** @ line 2486 — *BSPLINE_BEZIER_CURVE_FOUND* — **UNCOVERED**
  - What it tests: Edge is BSpline or Bezier
  - Repair action: Continue checking for fallback union
  - Suggested fixture: defect mentioning 'Geom_BSplineCurve', 'Geom_BezierCurve'

#### `ShapeUpgrade_UnifySameDomain.UnifyEdges` — lines 4325–4450
(10 branches, 6 covered.)

- **Branch 1** @ line 4340 — *SAFE_INPUT_MODE_GUARD* — **UNCOVERED**
  - What it tests: Safe mode enabled; update kept shapes map
  - Repair action: Update keep-shape tracking in context
  - Suggested fixture: defect mentioning 'mySafeInputMode', 'UpdateMapOfShapes', 'myKeepShapes'
- **Branch 2** @ line 4360 — *EDGE_MERGE_OCCURRED* — **UNCOVERED**
  - What it tests: Edges were actually merged
  - Repair action: Collect affected faces for rebuild
  - Suggested fixture: defect mentioning 'isMerged', 'aChangedFaces.Add', 'IsRecorded'
- **Branch 3** @ line 4365 — *EDGE_MODIFICATION_IN_CONTEXT* — **UNCOVERED**
  - What it tests: Edge was modified in context
  - Repair action: Collect parent faces for rebuild
  - Suggested fixture: defect mentioning 'IsRecorded', 'aMapEdgeFaces', 'aChangedFaces'
- **Branch 4** @ line 4381 — *NULL_FACE_SKIP* — COVERED by: a019, a028, a038, ad050, ad056, ad086, ad101, fi002 (+59 more)
  - What it tests: Face became invalid after edge merge
  - Repair action: Skip null/invalid face
- **Branch 5** @ line 4388 — *PLANAR_FACE_PCURVE_OPTIMIZATION* — COVERED by: m040
  - What it tests: Non-safe mode allows pcurve caching on planar faces
  - Repair action: Build and cache pcurves on planar faces
- **Branch 6** @ line 4393 — *PLANAR_SURFACE_DETECTION* — COVERED by: m040
  - What it tests: Surface is planar
  - Repair action: Apply planar-specific pcurve optimization
- **Branch 7** @ line 4405 — *FACE_FIX_SAFE_MODE_CONTEXT* — COVERED by: ad086, tfa004, tfa005, tfa011, tfa019, tfa037, tfa038, tfa039 (+1 more)
  - What it tests: Safe mode applies context to face fixer
  - Repair action: Set context on ShapeFix_Face
- **Branch 8** @ line 4424 — *SHELL_ORIENTATION_FIX* — COVERED by: ad086, pf015, tfa034, tsh008, tsh043
  - What it tests: Any faces were changed; shells need reorientation check
  - Repair action: Fix face orientation in parent shells
- **Branch 9** @ line 4436 — *SHELL_MODIFICATION_DETECTED* — COVERED by: a025, ad086, ad103, ad115, bo008, gn014, gn015, gn016 (+33 more)
  - What it tests: Shell orientation was actually fixed
  - Repair action: Replace shell and mark as changed
- **Branch 10** @ line 4442 — *SHELL_CHANGE_REAPPLY* — **UNCOVERED**
  - What it tests: Any shell was modified
  - Repair action: Reapply context to propagate shell changes
  - Suggested fixture: defect mentioning 'isChanged', 'myContext->Apply', 'aRes1'

#### `ShapeUpgrade_UnifySameDomain.UnifyFaces` — lines 3048–3129
(3 branches, 1 covered.)

- **Branch 1** @ line 3069 — *FACE_SHELL_MAPPING_EXISTING* — **UNCOVERED**
  - What it tests: Face already has shell mapping
  - Repair action: Add shell to existing map
  - Suggested fixture: defect mentioning 'ChangeSeek', 'aGMapFaceShells', 'pShells->Add'
- **Branch 2** @ line 3098 — *FREE_BOUNDARY_DETECTION* — COVERED by: m026, m109, os002, pmi053, sw003, tfa005, twi021, twi064 (+2 more)
  - What it tests: Edge is non-degenerated and touches exactly one face
  - Repair action: Mark edge as free boundary
- **Branch 3** @ line 3122 — *FACE_OUT_OF_SHELL_UNIFICATION* — **UNCOVERED**
  - What it tests: Faces exist outside shells
  - Repair action: Unify out-of-shell faces
  - Suggested fixture: defect mentioning 'nbf', 'IntUnifyFaces', 'TopAbs_SHELL'

#### `ShapeUpgrade_UnifySameDomain.UnionPCurves` — lines 1756–2157
(22 branches, 0 covered.)

- **Branch 1** @ line 1770 — *PLANE_FACE_SKIP* — **UNCOVERED**
  - What it tests: Face is planar—no PCurve needed
  - Repair action: Skip plane face from PCurve processing
  - Suggested fixture: defect mentioning 'myFacePlaneMap.IsBound'
- **Branch 2** @ line 1775 — *FACE_MAPPING_REDIRECT* — **UNCOVERED**
  - What it tests: Face was replaced in mapping
  - Repair action: Use new face from myFaceNewFace
  - Suggested fixture: defect mentioning 'myFaceNewFace.IsBound'
- **Branch 3** @ line 1783 — *ADAPTOR_TYPE_PLANE* — **UNCOVERED**
  - What it tests: BRepAdaptor detects plane geometry
  - Repair action: Skip from seam-edge PCurve list
  - Suggested fixture: defect mentioning 'aBAsurf.GetType() == GeomAbs_Plane'
- **Branch 4** @ line 1796 — *DUPLICATE_SURFACE_LOCATION* — **UNCOVERED**
  - What it tests: Same surface and location already in list
  - Repair action: Skip duplicate face
  - Suggested fixture: defect mentioning 'aPrevSurf == aSurf && aPrevLoc == aLoc'
- **Branch 5** @ line 1838 — *NULL_PCURVE* — **UNCOVERED**
  - What it tests: PCurve missing for edge-face pair
  - Repair action: Skip edge if PCurve is null
  - Suggested fixture: defect mentioning 'aPCurve.IsNull()'
- **Branch 6** @ line 1849 — *SEAM_EDGE_DETECTION* — **UNCOVERED**
  - What it tests: Edge has different PCurves in forward/reversed
  - Repair action: Mark as seam and append face
  - Suggested fixture: defect mentioning 'aPCurve != aPCurve2'
- **Branch 7** @ line 1860 — *BSPLINE_TO_LINE_SIMPLIFY* — **UNCOVERED**
  - What it tests: BSpline or Bezier can be approximated as line
  - Repair action: Replace PCurve with line if possible
  - Suggested fixture: defect mentioning 'aType == GeomAbs_BSplineCurve || aType == GeomAbs_BezierCurve'
- **Branch 8** @ line 1891 — *IDENTICAL_CURVE_CONTINUATION* — **UNCOVERED**
  - What it tests: Current PCurve is same object as previous
  - Repair action: Merge into single curve entry
  - Suggested fixture: defect mentioning 'aPCurve == aPCurveSeq.Last()'
- **Branch 9** @ line 1895 — *CURVE_TYPE_MATCH_LINE* — **UNCOVERED**
  - What it tests: Both curves are lines; check collinearity
  - Repair action: Extend line or mark non-mergeable
  - Suggested fixture: defect mentioning 'GeomAbs_Line', 'aPrevLin.Contains'
- **Branch 10** @ line 1921 — *CURVE_TYPE_MATCH_CIRCLE* — **UNCOVERED**
  - What it tests: Both curves are circles; check concentric
  - Repair action: Extend circle or mark non-mergeable
  - Suggested fixture: defect mentioning 'GeomAbs_Circle', 'aCirc.Location().Distance'
- **Branch 11** @ line 1945 — *SAME_CURVE_RANGE_UPDATE* — **UNCOVERED**
  - What it tests: Current edge aligns with previous curve
  - Repair action: Extend range of last sequence entry
  - Suggested fixture: defect mentioning 'isSameCurve', 'aLastsSeq.ChangeLast()'
- **Branch 12** @ line 1970 — *TOLERANCE_VERTEX_ACCUMULATE* — **UNCOVERED**
  - What it tests: Vertex between different curve types
  - Repair action: Record tolerance at junction
  - Suggested fixture: defect mentioning 'TopExp::CommonVertex', 'aTolVerSeq.Append'
- **Branch 13** @ line 1979 — *SINGLE_PCURVE_NO_CONCAT* — **UNCOVERED**
  - What it tests: Only one PCurve in sequence
  - Repair action: Use as-is; no concatenation needed
  - Suggested fixture: defect mentioning 'aPCurveSeq.Length() == 1'
- **Branch 14** @ line 1984 — *REVERSED_PCURVE_REVERSE* — **UNCOVERED**
  - What it tests: Single PCurve requires reversal
  - Repair action: Reverse parameters and PCurve object
  - Suggested fixture: defect mentioning '!aForwardsSeq.Last()', 'aResPCurve->Reverse()'
- **Branch 15** @ line 2001 — *TRIMMED_CURVE_REVERSE* — **UNCOVERED**
  - What it tests: Trimmed PCurve not in forward direction
  - Repair action: Reverse trimmed curve before concat
  - Suggested fixture: defect mentioning '!aForwardsSeq(i)', 'aTrPCurve->Reverse()'
- **Branch 16** @ line 2031 — *MULTI_CURVE_CONCAT_NEEDED* — **UNCOVERED**
  - What it tests: Concatenation resulted in multiple curves
  - Repair action: Further merge using CompCurveToBSpline
  - Suggested fixture: defect mentioning 'concatc2d->Length() > 1'
- **Branch 17** @ line 2060 — *BAD_PARAM_RANGE* — **UNCOVERED**
  - What it tests: PCurve parameter range differs from 3D
  - Repair action: Reparametrize or project onto surface
  - Suggested fixture: defect mentioning 'std::abs(aRange3d - aRange) > aMaxTol'
- **Branch 18** @ line 2076 — *PROJECTION_SUCCESS* — **UNCOVERED**
  - What it tests: Project 3D edge curve onto surface succeeds
  - Repair action: Replace PCurve with projection result
  - Suggested fixture: defect mentioning 'aToolProj.Perform'
- **Branch 19** @ line 2102 — *PCURVE_RANGE_MISMATCH* — **UNCOVERED**
  - What it tests: PCurve start/end not at 3D edge bounds
  - Repair action: Reparametrize PCurve to match 3D
  - Suggested fixture: defect mentioning 'aFirst3d - ResFirsts(ii)', 'aLast3d - ResLasts(ii)'
- **Branch 20** @ line 2107 — *REPARAMETERIZE_LINE* — **UNCOVERED**
  - What it tests: Line needs reparametrization
  - Repair action: Translate and update line coefficients
  - Suggested fixture: defect mentioning 'aType == GeomAbs_Line', 'aNewLine2d'
- **Branch 21** @ line 2118 — *REPARAMETERIZE_CIRCLE* — **UNCOVERED**
  - What it tests: Circle needs reparametrization
  - Repair action: Rotate circle position for new parameter
  - Suggested fixture: defect mentioning 'aType == GeomAbs_Circle', 'aPosition.Rotate'
- **Branch 22** @ line 2146 — *SEAM_EDGE_TWO_PCURVES* — **UNCOVERED**
  - What it tests: Seam edge requires two distinct PCurves
  - Repair action: Update edge with both PCurves
  - Suggested fixture: defect mentioning 'anIsSeam', 'aBuilder.UpdateEdge'

#### `ShapeUpgrade_UnifySameDomain.generateSubSeq` — lines 2695–2752
(6 branches, 0 covered.)

- **Branch 1** @ line 2706 — *LINE_EDGE_DIRECTION_INIT* — **UNCOVERED**
  - What it tests: Extract line direction from reference edge
  - Repair action: Initialize direction vector for comparison
  - Suggested fixture: defect mentioning 'GetLineEdgePoints'
- **Branch 2** @ line 2712 — *MERGING_POSSIBLE_CHECK* — **UNCOVERED**
  - What it tests: Two consecutive edges can be merged
  - Repair action: Append to current subsequence or start new
  - Suggested fixture: defect mentioning 'IsMergingPossible'
- **Branch 3** @ line 2721 — *MERGE_IMPOSSIBLE_NEW_CHAIN* — **UNCOVERED**
  - What it tests: Merging fails; edges belong to different groups
  - Repair action: Start new subsequence with current edge
  - Suggested fixture: defect mentioning '!isOk', 'SeqOfSubSeqOfEdges.Append'
- **Branch 4** @ line 2726 — *NEW_CHAIN_DIRECTION_UPDATE* — **UNCOVERED**
  - What it tests: New chain requires new direction computation
  - Repair action: Recompute direction for new edge
  - Suggested fixture: defect mentioning 'GetLineEdgePoints(edge2'
- **Branch 5** @ line 2734 — *CLOSED_CHAIN_WRAPAROUND* — **UNCOVERED**
  - What it tests: Chain is closed; check last→first connection
  - Repair action: Merge last and first subsequences if compatible
  - Suggested fixture: defect mentioning 'IsClosed && SeqOfSubSeqOfEdges.Length() > 1'
- **Branch 6** @ line 2738 — *CLOSED_CHAIN_MERGE_CHECK* — **UNCOVERED**
  - What it tests: Last and first edges can be merged in closed loop
  - Repair action: Append first to last and remove first
  - Suggested fixture: defect mentioning 'IsMergingPossible(edge1, edge2', 'SeqOfSubSeqOfEdges.Remove(1)'


### `src/ModelingAlgorithms/TKTopAlgo/BRepBuilderAPI/BRepBuilderAPI_Sewing.cxx`

22 methods, 270 branches, 101 covered.

#### `BRepBuilderAPI_Sewing.AnalysisNearestEdges` — lines 1624–1782
(15 branches, 0 covered.)

- **Branch 1** @ line 1627 — *Empty Work Candidate* — **UNCOVERED**
  - What it tests: workfaces.IsEmpty() after lookup
  - Repair action: Return early (no analysis needed)
  - Suggested fixture: defect mentioning 'workfaces.IsEmpty'
- **Branch 2** @ line 1631 — *Unbound Work Edge* — **UNCOVERED**
  - What it tests: mySectionBound.IsBound(bnd)
  - Repair action: Remap bnd to bound value
  - Suggested fixture: defect mentioning 'mySectionBound.IsBound'
- **Branch 3** @ line 1634 — *Work Edge Not in Faces* — **UNCOVERED**
  - What it tests: !myBoundFaces.Contains(bnd)
  - Repair action: workfaces stays empty
  - Suggested fixture: defect mentioning 'myBoundFaces.Contains'
- **Branch 4** @ line 1645 — *Candidate Index Match* — **UNCOVERED**
  - What it tests: index == workIndex
  - Repair action: Remove from seqIndCandidate
  - Suggested fixture: defect mentioning 'index == workIndex'
- **Branch 5** @ line 1651 — *Candidate Unbound Remap* — **UNCOVERED**
  - What it tests: mySectionBound.IsBound(bnd2)
  - Repair action: Remap bnd2 to bound value
  - Suggested fixture: defect mentioning 'mySectionBound.IsBound(bnd2)'
- **Branch 6** @ line 1655 — *Candidate Faces Missing* — **UNCOVERED**
  - What it tests: !myBoundFaces.Contains(bnd2)
  - Repair action: Remove candidate from seqIndCandidate
  - Suggested fixture: defect mentioning 'myBoundFaces.Contains(bnd2)'
- **Branch 7** @ line 1661 — *Closed Surface Check (U)* — **UNCOVERED**
  - What it tests: IsUClosedSurface(surf, bnd2, loc)
  - Repair action: Skip if surface is closed in U
  - Suggested fixture: defect mentioning 'IsUClosedSurface'
- **Branch 8** @ line 1661 — *Closed Surface Check (V)* — **UNCOVERED**
  - What it tests: IsVClosedSurface(surf, bnd2, loc)
  - Repair action: Skip if surface is closed in V
  - Suggested fixture: defect mentioning 'IsVClosedSurface'
- **Branch 9** @ line 1662 — *Merged Closed Edge Check* — **UNCOVERED**
  - What it tests: IsMergedClosed(...)
  - Repair action: Validate merged edges on closed face
  - Suggested fixture: defect mentioning 'IsMergedClosed'
- **Branch 10** @ line 1666 — *Not Merged (Reject Candidate)* — **UNCOVERED**
  - What it tests: !isMerged
  - Repair action: Add to seqNotCandidate; remove from seqIndCandidate
  - Suggested fixture: defect mentioning 'seqNotCandidate.Append'
- **Branch 11** @ line 1678 — *Empty or Single Candidate* — **UNCOVERED**
  - What it tests: seqIndCandidate.Length() == 0 OR seqNotCandidate.Length() == 1
  - Repair action: Return early (no analysis possible)
  - Suggested fixture: defect mentioning 'seqIndCandidate.Length() == 0'
- **Branch 12** @ line 1681 — *Skip Distance Eval* — **UNCOVERED**
  - What it tests: !evalDist
  - Repair action: Return early (distance eval disabled)
  - Suggested fixture: defect mentioning 'evalDist'
- **Branch 13** @ line 1707 — *Filter Out-of-Tolerance Distances* — **UNCOVERED**
  - What it tests: tabDist(n + 1) == -1 OR tabDist(n + 1) > myTolerance
  - Repair action: Add index to MapIndex for removal
  - Suggested fixture: defect mentioning 'myTolerance'
- **Branch 14** @ line 1714 — *Nearer Candidate Found* — **UNCOVERED**
  - What it tests: tabDist(n + 1) < TotTabDist(1, n)
  - Repair action: Add n to MapIndex for removal
  - Suggested fixture: defect mentioning 'TotTabDist'
- **Branch 15** @ line 1722 — *Final Removal by Index Map* — **UNCOVERED**
  - What it tests: MapIndex.Contains(i2)
  - Repair action: Remove indexed candidates from result
  - Suggested fixture: defect mentioning 'MapIndex.Contains(i2)'

#### `BRepBuilderAPI_Sewing.CreateCuttingNodes` — lines 5489–5665
(12 branches, 9 covered.)

- **Branch 1** @ line 5491 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'nbProj'
- **Branch 2** @ line 5497 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 3** @ line 5505 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 4** @ line 5521 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'nbProj'
- **Branch 5** @ line 5554 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 6** @ line 5563 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing
- **Branch 7** @ line 5571 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 8** @ line 5582 — *tolerance_validation* — COVERED by: a032, a097, ad005, ad045, ad049, ad086, ad090, ad095 (+388 more)
  - What it tests: geometric distance vs tolerance
  - Repair action: adjust_tolerance
- **Branch 9** @ line 5608 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 10** @ line 5625 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 11** @ line 5629 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 12** @ line 5635 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing

#### `BRepBuilderAPI_Sewing.CreateOutputInformations` — lines 5257–5363
(15 branches, 14 covered.)

- **Branch 1** @ line 5266 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 2** @ line 5275 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 3** @ line 5280 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 4** @ line 5283 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing
- **Branch 5** @ line 5289 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing
- **Branch 6** @ line 5306 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 7** @ line 5310 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 8** @ line 5312 — *degenerate_edge* — COVERED by: m026, m109, os002, pmi053, sw003, tfa005, twi021, twi064 (+2 more)
  - What it tests: edge degeneracy
  - Repair action: handle_degenerate
- **Branch 9** @ line 5321 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 10** @ line 5334 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 11** @ line 5340 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 12** @ line 5343 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing
- **Branch 13** @ line 5349 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 14** @ line 5353 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing
- **Branch 15** @ line 5355 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing

#### `BRepBuilderAPI_Sewing.CreateSections` — lines 5672–5878
(13 branches, 6 covered.)

- **Branch 1** @ line 5691 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 2** @ line 5731 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 3** @ line 5746 — *collection_cardinality* — COVERED by: a031, a082, a084, a106, ad001, ad015, ad033, ad035 (+212 more)
  - What it tests: number of elements in container
  - Repair action: classify_cardinality
- **Branch 4** @ line 5755 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 5** @ line 5763 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 6** @ line 5789 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 7** @ line 5797 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 8** @ line 5819 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 9** @ line 5827 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 10** @ line 5839 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 11** @ line 5840 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 12** @ line 5846 — *exception_handling* — COVERED by: a002, a003, a011, a013, a014, a016, a017, a021 (+625 more)
  - What it tests: geometric operation failure
  - Repair action: handle_exception
- **Branch 13** @ line 5855 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'

#### `BRepBuilderAPI_Sewing.CreateSewedShape` — lines 5030–5244
(32 branches, 14 covered.)

- **Branch 1** @ line 5045 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 2** @ line 5048 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 3** @ line 5059 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numsh'
- **Branch 4** @ line 5066 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 5** @ line 5070 — *shape_type_check* — COVERED by: tsh018
  - What it tests: entity type (edge/face/shell)
  - Repair action: classify_entity
- **Branch 6** @ line 5072 — *manifold_topology* — **UNCOVERED**
  - What it tests: manifold vs non-manifold shape
  - Repair action: classify_topology
  - Suggested fixture: defect mentioning 'myNonmanifold'
- **Branch 7** @ line 5079 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 8** @ line 5080 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 9** @ line 5085 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 10** @ line 5089 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 11** @ line 5099 — *shape_type_check* — COVERED by: tsh018
  - What it tests: entity type (edge/face/shell)
  - Repair action: classify_entity
- **Branch 12** @ line 5101 — *manifold_topology* — **UNCOVERED**
  - What it tests: manifold vs non-manifold shape
  - Repair action: classify_topology
  - Suggested fixture: defect mentioning 'myNonmanifold'
- **Branch 13** @ line 5126 — *manifold_topology* — **UNCOVERED**
  - What it tests: manifold vs non-manifold shape
  - Repair action: classify_topology
  - Suggested fixture: defect mentioning 'myNonmanifold'
- **Branch 14** @ line 5128 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'nbOldShells'
- **Branch 15** @ line 5129 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'nbOldShells'
- **Branch 16** @ line 5134 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 17** @ line 5135 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 18** @ line 5140 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 19** @ line 5144 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 20** @ line 5161 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 21** @ line 5163 — *edge_sharing* — COVERED by: a001, a002, a003, a004, a007, a008, a009, a010 (+893 more)
  - What it tests: edge adjacency and sharing
  - Repair action: detect_sharing
- **Branch 22** @ line 5168 — *null_empty_check* — **UNCOVERED**
  - What it tests: shape or container emptiness
  - Repair action: validate_shape
  - Suggested fixture: defect mentioning 'IsNull', 'IsEmpty'
- **Branch 23** @ line 5172 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 24** @ line 5177 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 25** @ line 5188 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 26** @ line 5195 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 27** @ line 5201 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 28** @ line 5212 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 29** @ line 5214 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 30** @ line 5219 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 31** @ line 5223 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numf'
- **Branch 32** @ line 5234 — *count_comparison* — **UNCOVERED**
  - What it tests: count threshold
  - Repair action: classify_by_count
  - Suggested fixture: defect mentioning 'numsh'

#### `BRepBuilderAPI_Sewing.Cutting` — lines 4442–4600
(14 branches, 8 covered.)

- **Branch 1** @ line 4444 — *no_vertices_to_cut* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Early exit if assembly has no vertices
  - Repair action: Skip entire cutting process
- **Branch 2** @ line 4448 — *bounding_box_tree_construction* — COVERED by: twi079
  - What it tests: Build spatial index of assembly vertices
  - Repair action: Create UBTree with vertex bounding boxes
- **Branch 3** @ line 4476 — *skip_floating_edges* — COVERED by: ad027, ad050, ad086, ad101, fi002, gn003, gn037, hea011 (+28 more)
  - What it tests: Skip floating edges (no adjacent faces)
  - Repair action: Continue to next bound
- **Branch 4** @ line 4482 — *bound_curve_retrieval_failure* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Bound edge has no 3D curve
  - Repair action: Skip to next bound
- **Branch 5** @ line 4486 — *curve_location_transformation* — **UNCOVERED**
  - What it tests: Curve has non-identity location
  - Repair action: Apply transformation to get local curve
  - Suggested fixture: defect mentioning '!loc.IsIdentity()', 'c3d->Transform', 'loc.Transformation'
- **Branch 6** @ line 4501 — *candidate_vertex_bounding_box_filtering* — **UNCOVERED**
  - What it tests: Filter vertices within curve bounding box
  - Repair action: Use aTree selector to find candidates in tolerance
  - Suggested fixture: defect mentioning 'aGlobalBox', 'aTree.Select', 'aSelector'
- **Branch 7** @ line 4506 — *no_candidates_in_bound_box* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: No vertices in curve vicinity
  - Repair action: Skip bound if no candidates
- **Branch 8** @ line 4520 — *exclude_bound_endpoints* — **UNCOVERED**
  - What it tests: Filter out bound's own vertices from candidates
  - Repair action: Add only interior candidate vertices to map
  - Suggested fixture: defect mentioning 'Node.IsSame(Node1)', 'Node.IsSame(Node2)', '!Node.IsSame'
- **Branch 9** @ line 4529 — *no_interior_candidates* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: All candidates filtered as bound endpoints
  - Repair action: Skip bound if no interior candidates remain
- **Branch 10** @ line 4540 — *project_vertices_onto_bound_curve* — **UNCOVERED**
  - What it tests: Project candidates onto bound curve to find cutting points
  - Repair action: Compute distance and parameter for each candidate
  - Suggested fixture: defect mentioning 'ProjectPointsOnCurve', 'arrPara', 'arrDist'
- **Branch 11** @ line 4553 — *no_valid_cutting_nodes* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Projection created no usable cutting nodes
  - Repair action: Skip bound if no cutting nodes generated
- **Branch 12** @ line 4560 — *multiple_cutting_sections_created* — **UNCOVERED**
  - What it tests: Bound successfully split into multiple sections
  - Repair action: Record sections in myBoundSections and update node maps
  - Suggested fixture: defect mentioning 'listSections.Extent() > 1', 'myBoundSections.Bind'
- **Branch 13** @ line 4573 — *section_vertex_to_node_conversion* — **UNCOVERED**
  - What it tests: Section vertex may be a pre-existing assembly node
  - Repair action: Convert to assembly node if it exists
  - Suggested fixture: defect mentioning 'myVertexNode.Contains', 'FindFromKey'
- **Branch 14** @ line 4578 — *update_node_section_record* — COVERED by: a018, a019, a029, a074, a101, a102, ad003, ad026 (+35 more)
  - What it tests: Record section in node's section list
  - Repair action: Append section to myNodeSections(vertex) or create new

#### `BRepBuilderAPI_Sewing.Dump` — lines 2542–2584
(1 branches, 0 covered.)

- **Branch 1** @ line 2548 — *bound_has_sections* — **UNCOVERED**
  - What it tests: Boundary edge is associated with multiple sections
  - Repair action: Sum all section extents if bound maps to sections, else add 1
  - Suggested fixture: defect mentioning 'myBoundSections.IsBound()'

#### `BRepBuilderAPI_Sewing.EdgeProcessing` — lines 4913–4996
(12 branches, 4 covered.)

- **Branch 1** @ line 4925 — *single_face_bound_edge* — **UNCOVERED**
  - What it tests: Bound edge belongs to exactly one face
  - Repair action: Mark as free edge for degenerate processing
  - Suggested fixture: defect mentioning 'listFaces.Extent() == 1'
- **Branch 2** @ line 4927 — *bound_has_cutting_sections* — COVERED by: twi087
  - What it tests: Bound was split during Cutting phase
  - Repair action: Process sections instead of bound
- **Branch 3** @ line 4932 — *section_not_merged* — **UNCOVERED**
  - What it tests: Section not recorded as merged
  - Repair action: Add to free edges map
  - Suggested fixture: defect mentioning '!myMergedEdges.Contains', 'MapFreeEdges.Add'
- **Branch 4** @ line 4935 — *edge_already_free_mapped* — **UNCOVERED**
  - What it tests: Edge already in free edges map
  - Repair action: Skip to avoid duplicate
  - Suggested fixture: defect mentioning '!MapFreeEdges.Contains'
- **Branch 5** @ line 4946 — *uncut_bound_not_merged* — COVERED by: a002, a017, a018, a019, a020, a026, a028, a029 (+453 more)
  - What it tests: Original bound not merged and not cut
  - Repair action: Add to free edges map
- **Branch 6** @ line 4960 — *free_edges_exist* — **UNCOVERED**
  - What it tests: At least one free edge found
  - Repair action: Call GetFreeWires to assemble into wires
  - Suggested fixture: defect mentioning '!MapFreeEdges.IsEmpty()', 'GetFreeWires', 'seqWires'
- **Branch 7** @ line 4967 — *degenerate_wire_check* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Wire contains degenerate edges
  - Repair action: Skip degenerate wires, continue to next
- **Branch 8** @ line 4976 — *edge_face_association* — **UNCOVERED**
  - What it tests: Retrieve face associated with free edge
  - Repair action: Use EdgeFace map to find adjacent face context
  - Suggested fixture: defect mentioning 'EdgeFace.IsBound', 'EdgeFace.Find'
- **Branch 9** @ line 4980 — *degenerate_section_creation* — **UNCOVERED**
  - What it tests: Try to create degenerate edge from geometric context
  - Repair action: Call DegeneratedSection to generate degenerate edge
  - Suggested fixture: defect mentioning 'DegeneratedSection', 'degedge'
- **Branch 10** @ line 4981 — *degenerate_section_failure* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: DegeneratedSection returned null
  - Repair action: Skip edge, continue to next
- **Branch 11** @ line 4985 — *degenerate_edge_replacement* — **UNCOVERED**
  - What it tests: Created degenerate differs from original
  - Repair action: Replace original edge with degenerate via myReShape
  - Suggested fixture: defect mentioning '!degedge.IsSame', 'ReplaceEdge'
- **Branch 12** @ line 4989 — *degenerate_edge_marking* — **UNCOVERED**
  - What it tests: Verify created edge is actually degenerate
  - Repair action: Add to myDegenerated set for tracking
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated', 'myDegenerated.Add'

#### `BRepBuilderAPI_Sewing.EdgeRegularity` — lines 5003–5026
(1 branches, 1 covered.)

- **Branch 1** @ line 5010 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate

#### `BRepBuilderAPI_Sewing.EvaluateDistances` — lines 1294–1522
(18 branches, 1 covered.)

- **Branch 1** @ line 1295 — *Forward Init* — **UNCOVERED**
  - What it tests: Initialize secForward array
  - Repair action: Set to true
  - Suggested fixture: defect mentioning 'secForward.Init(true)'
- **Branch 2** @ line 1299 — *Null Curve* — **UNCOVERED**
  - What it tests: BRep_Tool::Curve returns null
  - Repair action: Continue to next edge
  - Suggested fixture: defect mentioning 'c3d.IsNull'
- **Branch 3** @ line 1299 — *Non-Identity Location* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+115 more)
  - What it tests: !loc.IsIdentity()
  - Repair action: Copy curve and apply transformation
- **Branch 4** @ line 1314 — *Reference Edge Setup* — **UNCOVERED**
  - What it tests: i == indRef
  - Repair action: Save as c3dRef, firstRef, lastRef
  - Suggested fixture: defect mentioning 'c3dRef = c3d'
- **Branch 5** @ line 1334 — *First Point (T param)* — **UNCOVERED**
  - What it tests: j == 1
  - Repair action: Use curve start parameter
  - Suggested fixture: defect mentioning 'T = first'
- **Branch 6** @ line 1336 — *Last Point (T param)* — **UNCOVERED**
  - What it tests: j == npt
  - Repair action: Use curve end parameter
  - Suggested fixture: defect mentioning 'T = last'
- **Branch 7** @ line 1340 — *Mid-point Uniform Sample* — **UNCOVERED**
  - What it tests: 1 < j < npt
  - Repair action: Interpolate T parameter
  - Suggested fixture: defect mentioning 'T = first + (j - 1) * deltaT'
- **Branch 8** @ line 1348 — *Reference Point Accumulation* — **UNCOVERED**
  - What it tests: i == indRef && j > 1
  - Repair action: Accumulate distance for length calc
  - Suggested fixture: defect mentioning 'i == indRef', 'SquareDistance'
- **Branch 9** @ line 1354 — *Section Point Accumulation* — **UNCOVERED**
  - What it tests: i != indRef && j > 1
  - Repair action: Accumulate distance for length calc
  - Suggested fixture: defect mentioning 'ptsSec(j)', 'SquareDistance'
- **Branch 10** @ line 1362 — *Forward Direction Distance* — **UNCOVERED**
  - What it tests: pt.Distance(ptsRef(j))
  - Repair action: Track max distance in forward direction
  - Suggested fixture: defect mentioning 'ptsRef(j)'
- **Branch 11** @ line 1369 — *Reverse Direction Distance* — **UNCOVERED**
  - What it tests: pt.Distance(ptsRef(npt - j + 1))
  - Repair action: Track max distance in reverse direction
  - Suggested fixture: defect mentioning 'ptsRef(npt - j + 1)'
- **Branch 12** @ line 1378 — *Dot Product Sign* — **UNCOVERED**
  - What it tests: (aVecRef * aVec1) * (aVecRef * aVec2) < 0
  - Repair action: Count points between reference vertices
  - Suggested fixture: defect mentioning 'aVecRef * aVec1', 'nbFound'
- **Branch 13** @ line 1390 — *Orientation Determination* — **UNCOVERED**
  - What it tests: distFor < distRev
  - Repair action: Set isForward forward/reverse
  - Suggested fixture: defect mentioning 'isForward = (distFor < distRev)'
- **Branch 14** @ line 1394 — *Accepted Distance/nbFound* — **UNCOVERED**
  - What it tests: i == indRef OR (dist < myTolerance AND nbFound >= npt*0.5)
  - Repair action: Record tabDst and tabMinDist
  - Suggested fixture: defect mentioning 'nbFound >= npt * 0.5'
- **Branch 15** @ line 1399 — *Projection Fallback (Ref Longer)* — **UNCOVERED**
  - What it tests: arrLen(indRef) >= arrLen(i)
  - Repair action: Project ptsSec onto c3dRef
  - Suggested fixture: defect mentioning 'arrLen(indRef) >= arrLen(i)'
- **Branch 16** @ line 1402 — *Projection Fallback (Sec Longer)* — **UNCOVERED**
  - What it tests: arrLen(indRef) < arrLen(i)
  - Repair action: Project ptsRef onto c3d
  - Suggested fixture: defect mentioning 'ProjectPointsOnCurve', 'ptsRef'
- **Branch 17** @ line 1406 — *Skip Negative Projection* — **UNCOVERED**
  - What it tests: arrDist(j) < 0.0
  - Repair action: Skip invalid projections
  - Suggested fixture: defect mentioning 'arrDist(j) < 0'
- **Branch 18** @ line 1414 — *Min Projection Count* — **UNCOVERED**
  - What it tests: nbFound > 1
  - Repair action: Record tabDst and tabMinDist if >1 points projected
  - Suggested fixture: defect mentioning 'nbFound > 1'

#### `BRepBuilderAPI_Sewing.FaceAnalysis` — lines 2598–2867
(13 branches, 1 covered.)

- **Branch 1** @ line 2599 — *input_loaded_as_shape_field* — **UNCOVERED**
  - What it tests: Input was loaded via Load() into myShape instead of Add()
  - Repair action: Call Add(myShape) to transfer from field to oldShapes collection
  - Suggested fixture: defect mentioning 'myShape.IsNull()', 'myOldShapes.IsEmpty()', 'Add(myShape)'
- **Branch 2** @ line 2632 — *non_wire_children_in_face* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face contains non-wire topology children
  - Repair action: Skip non-WIRE elements when iterating face children
- **Branch 3** @ line 2653 — *degenerated_edge_preserved* — **UNCOVERED**
  - What it tests: Edge marked as degenerate in topology
  - Repair action: Keep degenerate edge in wire as-is, add to tracking map
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated(edge)', 'myDegenerated.Add(edge)'
- **Branch 4** @ line 2668 — *edge_with_no_3d_curve* — **UNCOVERED**
  - What it tests: Edge has no 3D curve, cannot measure compactness
  - Repair action: Skip small-edge detection, keep edge as-is with warning
  - Suggested fixture: defect mentioning 'c3d.IsNull()'
- **Branch 5** @ line 2689 — *small_edge_compact_curve* — **UNCOVERED**
  - What it tests: Curve deviates minimally from endpoints (high compactness)
  - Repair action: Mark edge as small and degenerate it if 2*maxdist <= MinTolerance
  - Suggested fixture: defect mentioning 'isSmall = (2. * maxdist', 'MinTolerance()'
- **Branch 6** @ line 2714 — *small_edge_first_vertex_already_glued* — **UNCOVERED**
  - What it tests: First vertex of small edge already replaced by ReShape
  - Repair action: Append second vertex to existing glued vertex list
  - Suggested fixture: defect mentioning '!nv1.IsSame(v1)', 'GluedVertices.ChangeFromKey(nv1)'
- **Branch 7** @ line 2718 — *small_edge_both_vertices_already_glued* — **UNCOVERED**
  - What it tests: Both endpoints of small edge already glued to different vertices
  - Repair action: Merge two glued vertex lists into one
  - Suggested fixture: defect mentioning '!nv2.IsSame(v2)', '!nv1.IsSame(nv2)', 'GluedVertices.RemoveKey(nv2)'
- **Branch 8** @ line 2734 — *small_edge_second_vertex_glued_only* — **UNCOVERED**
  - What it tests: Only second vertex of small edge is glued
  - Repair action: Add first vertex to second's glued list and replace first
  - Suggested fixture: defect mentioning '!nv2.IsSame(v2)', 'GluedVertices.ChangeFromKey(nv2).Append(v1)'
- **Branch 9** @ line 2746 — *small_edge_create_new_glued_vertex* — **UNCOVERED**
  - What it tests: Small edge has two distinct endpoints not yet glued
  - Repair action: Create new synthetic vertex and glue both endpoints to it
  - Suggested fixture: defect mentioning '!v1.IsSame(v2)', 'B.MakeVertex(nv)'
- **Branch 10** @ line 2772 — *small_edge_no_2d_curve* — **UNCOVERED**
  - What it tests: Small edge has no 2D curve on face surface
  - Repair action: Skip degeneration when 2D curve unavailable
  - Suggested fixture: defect mentioning 'c2d.IsNull()'
- **Branch 11** @ line 2808 — *all_edges_small_face* — **UNCOVERED**
  - What it tests: Face contains only degenerate/small edges
  - Repair action: Remove entire face from model via myReShape->Remove(face)
  - Suggested fixture: defect mentioning 'nbSmall == nbEdges', 'myReShape->Remove(face)'
- **Branch 12** @ line 2816 — *face_modified_by_edge_replacement* — **UNCOVERED**
  - What it tests: Face structure changed by small edge processing
  - Repair action: Replace entire face with new geometry containing processed wires
  - Suggested fixture: defect mentioning 'isFaceChanged', 'myReShape->Replace(face, nface'
- **Branch 13** @ line 2840 — *glued_vertices_empty_list* — **UNCOVERED**
  - What it tests: Glued vertex group has zero contributing vertices
  - Repair action: Skip vertex coordinate averaging when list is empty
  - Suggested fixture: defect mentioning 'nbPoints', 'continue_without_update'

#### `BRepBuilderAPI_Sewing.FindCandidates` — lines 1790–2086
(20 branches, 4 covered.)

- **Branch 1** @ line 1792 — *Empty/Null Input* — COVERED by: in014
  - What it tests: seqSections has <= 1 elements
  - Repair action: Return false (no candidates found)
- **Branch 2** @ line 1819 — *Unbound Reference* — **UNCOVERED**
  - What it tests: Edge not in mySectionBound map
  - Repair action: Skip mapping; use original edge
  - Suggested fixture: defect mentioning 'mySectionBound.IsBound', 'bnd = Edge1'
- **Branch 3** @ line 1823 — *Missing Bound Faces* — **UNCOVERED**
  - What it tests: bnd not in myBoundFaces map
  - Repair action: Skip face lookup
  - Suggested fixture: defect mentioning 'myBoundFaces.Contains'
- **Branch 4** @ line 1855 — *Distance Filter (OOB)* — **UNCOVERED**
  - What it tests: aMaxDist >= 0.0 AND aMaxDist <= myTolerance
  - Repair action: Skip candidates outside tolerance
  - Suggested fixture: defect mentioning 'aMaxDist >= 0.0', 'myTolerance'
- **Branch 5** @ line 1857 — *Length Guard* — **UNCOVERED**
  - What it tests: arrLen(i) > myMinTolerance
  - Repair action: Filter out degenerate/short sections
  - Suggested fixture: defect mentioning 'arrLen', 'myMinTolerance'
- **Branch 6** @ line 1869 — *Precision Ambiguity* — COVERED by: gp013, tb001, tb007, tb018, tb019, tfa006, twi040
  - What it tests: aDelta < Precision::Confusion()
  - Repair action: Reorder candidates by distance
- **Branch 7** @ line 1872 — *Tiebreaker (Min Distance)* — **UNCOVERED**
  - What it tests: fabs(aDelta) > RealSmall() OR arrMinDist comparison
  - Repair action: Use minDist to break ties
  - Suggested fixture: defect mentioning 'RealSmall', 'arrMinDist'
- **Branch 8** @ line 1900 — *No Candidates (Validation)* — COVERED by: in014
  - What it tests: nbCandidates == 0 after filtering
  - Repair action: Return false
- **Branch 9** @ line 1914 — *Non-manifold Mode* — **UNCOVERED**
  - What it tests: myNonmanifold && nbCandidates > 1
  - Repair action: Run AnalysisNearestEdges to filter
  - Suggested fixture: defect mentioning 'myNonmanifold', 'AnalysisNearestEdges'
- **Branch 10** @ line 1920 — *Iteration Failure (Tier-3)* — **UNCOVERED**
  - What it tests: First iteration of AnalysisNearestEdges yields no candidates
  - Repair action: Return false (tier-3 lint failure)
  - Suggested fixture: defect mentioning 'k == 1', 'seqCandidates.Length'
- **Branch 11** @ line 1926 — *Empty Candidate Sequence* — **UNCOVERED**
  - What it tests: seqCandidates.Length() == 0 mid-loop
  - Repair action: Continue loop without appending
  - Suggested fixture: defect mentioning 'seqCandidates.Length'
- **Branch 12** @ line 1935 — *Reference Not Found* — **UNCOVERED**
  - What it tests: mapReference.Contains(indCandidate) at top of while
  - Repair action: Break (candidate approved)
  - Suggested fixture: defect mentioning 'mapReference.Contains'
- **Branch 13** @ line 1944 — *Recursive Candidate Search* — **UNCOVERED**
  - What it tests: isFound from recursive FindCandidates call
  - Repair action: Validate seqCandidates1.Length() > 0
  - Suggested fixture: defect mentioning 'FindCandidates', 'seqCandidates1'
- **Branch 14** @ line 1949 — *Circular Reference (Ref Check)* — **UNCOVERED**
  - What it tests: indCandidate1 == indReference
  - Repair action: Break (mutual best match found)
  - Suggested fixture: defect mentioning 'indCandidate1 == indReference'
- **Branch 15** @ line 1954 — *Circular Reference (Map Check)* — **UNCOVERED**
  - What it tests: mapReference.Contains(indCandidate1)
  - Repair action: Prepend and break (close cycle)
  - Suggested fixture: defect mentioning 'mapReference.Contains(indCandidate1)'
- **Branch 16** @ line 1970 — *Repeated Removal* — **UNCOVERED**
  - What it tests: isFound == false after all checks
  - Repair action: Remove candidate #1, decrement counter
  - Suggested fixture: defect mentioning 'seqCandidates.Remove(1)'
- **Branch 17** @ line 1977 — *Bound Face Mismatch* — **UNCOVERED**
  - What it tests: Candidate has different bound faces
  - Repair action: Return false
  - Suggested fixture: defect mentioning 'myBoundFaces.Contains(bnd)'
- **Branch 18** @ line 1985 — *Common Face Exclusion* — **UNCOVERED**
  - What it tests: Faces1.Contains(Face2)
  - Repair action: Check IsMergedClosed() for closed face
  - Suggested fixture: defect mentioning 'Faces1.Contains', 'IsMergedClosed'
- **Branch 19** @ line 1988 — *Merge Validation Failure* — COVERED by: in014
  - What it tests: !Faces1.Contains && !IsMergedClosed
  - Repair action: Return false (merge not allowed)
- **Branch 20** @ line 2000 — *Final Count Validation* — **UNCOVERED**
  - What it tests: nbCandidates > 0
  - Repair action: Return true if candidates found
  - Suggested fixture: defect mentioning 'nbCandidates > 0'

#### `BRepBuilderAPI_Sewing.FindFreeBoundaries` — lines 2879–3074
(14 branches, 8 covered.)

- **Branch 1** @ line 2882 — *context_shape_with_empty_oldshapes* — **UNCOVERED**
  - What it tests: Context shape provided but no shapes added yet
  - Repair action: Call Add(myShape) to transfer context shape to collection
  - Suggested fixture: defect mentioning 'myShape.IsNull()', 'myOldShapes.IsEmpty()', 'Add(myShape)'
- **Branch 2** @ line 2889 — *context_shape_with_existing_shapes* — **UNCOVERED**
  - What it tests: Context shape provided alongside previously added shapes
  - Repair action: Apply ReShape to context, add to NewShapes if not null
  - Suggested fixture: defect mentioning 'myReShape->Apply(myShape)', 'NewShapes.Add'
- **Branch 3** @ line 2906 — *null_shape_in_collection* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Shape in myOldShapes is null (previously removed)
  - Repair action: Skip null shape when building edge-face map
- **Branch 4** @ line 2932 — *duplicate_face_in_newshapes* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Same face appears in multiple input shapes
  - Repair action: Skip face if already in mapFaces to avoid duplicate processing
- **Branch 5** @ line 2943 — *non_wire_children_in_face_boundary* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Face contains non-wire topology when exploring boundaries
  - Repair action: Skip non-WIRE elements in face iteration
- **Branch 6** @ line 2975 — *internal_orientation_edge* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge has TopAbs_INTERNAL orientation
  - Repair action: Skip internal edges from boundary classification
- **Branch 7** @ line 2980 — *single_face_seam_edge* — **UNCOVERED**
  - What it tests: Edge bounds single face and is a seam (closed curve on surface)
  - Repair action: Detect seam with BRep_Tool::IsClosed, process seam topology
  - Suggested fixture: defect mentioning 'nbFaces == 1', 'BRep_Tool::IsClosed'
- **Branch 8** @ line 2984 — *seam_edge_duplicate_curves* — **UNCOVERED**
  - What it tests: Seam edge needs two 2D curves, one from each surface side
  - Repair action: Create new edge with two 2D curves (c2d and c2dold)
  - Suggested fixture: defect mentioning 'c2d', 'c2dold', 'B.UpdateEdge'
- **Branch 9** @ line 3020 — *floating_edge_no_faces* — **UNCOVERED**
  - What it tests: Edge has no adjacent faces (floating geometry)
  - Repair action: Include as boundary if myFloatingEdgesMode true and nbFaces=0
  - Suggested fixture: defect mentioning 'myFloatingEdgesMode', '!nbFaces'
- **Branch 10** @ line 3021 — *nonmanifold_or_free_edge* — **UNCOVERED**
  - What it tests: Edge is nonmanifold (many faces) or free (single face boundary)
  - Repair action: Classify edge as boundary if myFaceMode+myNonmanifold or single free edge
  - Suggested fixture: defect mentioning 'myFaceMode', 'myNonmanifold', 'nbFaces == 1'
- **Branch 11** @ line 3025 — *degenerated_boundary_edge* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Classified boundary edge is actually degenerate
  - Repair action: Skip degenerate edges even if classified as boundary
- **Branch 12** @ line 3040 — *edge_with_null_vertices* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge endpoints are null (invalid topology)
  - Repair action: Skip edge when vertex extraction fails
- **Branch 13** @ line 3044 — *internal_orientation_vertices* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge vertices have TopAbs_INTERNAL orientation
  - Repair action: Skip edges with internal vertices
- **Branch 14** @ line 3048 — *vertex_classification_by_edge_type* — COVERED by: a018, ad086
  - What it tests: Boundary vs floating edge determines vertex classification
  - Repair action: Add to myVertexNode (bound) or myVertexNodeFree (floating) accordingly

#### `BRepBuilderAPI_Sewing.GetFreeWires` — lines 4657–4705
(4 branches, 3 covered.)

- **Branch 1** @ line 4661 — *build_vertex_edge_map* — COVERED by: a011, a018, a019, a029, a074, a101, a102, ad003 (+45 more)
  - What it tests: Build adjacency map of vertices to free edges
  - Repair action: Populate VertEdge map for wire assembly
- **Branch 2** @ line 4686 — *edge_already_processed* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge already included in a wire
  - Repair action: Skip and continue to next edge
- **Branch 3** @ line 4691 — *trace_contiguous_edge_sequence* — **UNCOVERED**
  - What it tests: Trace contiguous edges from start edge via vertex connections
  - Repair action: Call GetSeqEdges to build sequence and remove from map
  - Suggested fixture: defect mentioning 'GetSeqEdges', 'seqEdges'
- **Branch 4** @ line 4700 — *all_edges_processed* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: All free edges assigned to wires
  - Repair action: Break early if no edges remain

#### `BRepBuilderAPI_Sewing.IsDegenerated` — lines 2467–2494
(4 branches, 2 covered.)

- **Branch 1** @ line 2470 — *degenerated_face* — COVERED by: tsh018
  - What it tests: Shape is a face and was removed by ReShape
  - Repair action: Return true if face is null after reshape (face deleted as degenerate)
- **Branch 2** @ line 2474 — *non_face_null_reshape* — COVERED by: in014
  - What it tests: Non-face shape became null after ReShape
  - Repair action: Return false for non-face shapes that reshaped to null
- **Branch 3** @ line 2479 — *degenerated_edge* — **UNCOVERED**
  - What it tests: Shape is an edge with zero-length 3D curve
  - Repair action: Test with BRep_Tool::Degenerated for edge classification
  - Suggested fixture: defect mentioning 'TopAbs_EDGE', 'BRep_Tool::Degenerated'
- **Branch 4** @ line 2484 — *degenerated_wire_all_edges* — **UNCOVERED**
  - What it tests: Wire contains all degenerated edges
  - Repair action: Iterate wire edges and return true only if all are degenerate
  - Suggested fixture: defect mentioning 'TopAbs_WIRE', 'TopoDS_Iterator', 'isDegenerated'

#### `BRepBuilderAPI_Sewing.Load` — lines 2138–2167
(1 branches, 0 covered.)

- **Branch 1** @ line 2140 — *null_shape_input* — **UNCOVERED**
  - What it tests: Input shape is null, requires state clearing
  - Repair action: Nullify myShape, clear all internal maps
  - Suggested fixture: defect mentioning 'IsNull()', 'myShape.Nullify()'

#### `BRepBuilderAPI_Sewing.MergedNearestEdges` — lines 4246–4431
(12 branches, 3 covered.)

- **Branch 1** @ line 4251 — *edge_node_presence_check* — **UNCOVERED**
  - What it tests: Determine if edge nodes are in vertex assembly
  - Repair action: Map original vertices to assembly nodes
  - Suggested fixture: defect mentioning 'isNode1', 'isNode2', 'myVertexNode.Contains'
- **Branch 2** @ line 4265 — *cutting_node_recursion_endpoint* — **UNCOVERED**
  - What it tests: Node1 has cutting sub-nodes (two-level graph)
  - Repair action: Build complete connectivity map including sub-nodes
  - Suggested fixture: defect mentioning 'myCuttingNode.IsBound', 'mapVert1', 'ilv.More'
- **Branch 3** @ line 4272 — *non_assembled_cutting_node_expansion* — **UNCOVERED**
  - What it tests: Endpoint has cutting nodes that also have cutting sub-nodes
  - Repair action: Recursively include grandchild nodes
  - Suggested fixture: defect mentioning '!isNode1', 'myCuttingNode.IsBound(v1)', 'ilvn'
- **Branch 4** @ line 4287 — *cutting_node_recursion_endpoint2* — **UNCOVERED**
  - What it tests: Node2 has cutting sub-nodes (analogous to Node1)
  - Repair action: Build connectivity map for second endpoint
  - Suggested fixture: defect mentioning 'mapVert2', 'myCuttingNode.IsBound(nno2)'
- **Branch 5** @ line 4314 — *edge_section_connectivity_check* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Check if node has recorded sections
  - Repair action: Skip nodes with no section history
- **Branch 6** @ line 4338 — *contiguous_edge_bridging* — **UNCOVERED**
  - What it tests: Found edge that bridges mapVert1 to mapVert2
  - Repair action: Add to candidate sequence if not rejected
  - Suggested fixture: defect mentioning 'mapVert1.Contains', 'mapVert2.Contains', 'seqEdges.Append'
- **Branch 7** @ line 4344 — *candidate_rejection_pre_merged* — **UNCOVERED**
  - What it tests: Candidate edge already merged in prior phases
  - Repair action: Skip candidate
  - Suggested fixture: defect mentioning 'isRejected', 'myMergedEdges.Contains'
- **Branch 8** @ line 4345 — *candidate_rejection_split_sections* — **UNCOVERED**
  - What it tests: Candidate edge is split and sections already merged
  - Repair action: Reject candidate
  - Suggested fixture: defect mentioning 'myBoundSections.IsBound', 'isRejected'
- **Branch 9** @ line 4358 — *candidate_rejection_bound_conflict* — **UNCOVERED**
  - What it tests: Candidate is a section whose bound is unbound or merged
  - Repair action: Reject candidate
  - Suggested fixture: defect mentioning 'mySectionBound.IsBound', '!myBoundSections.IsBound'
- **Branch 10** @ line 3382 — *longest_edge_priority* — **UNCOVERED**
  - What it tests: Nonmanifold mode: prioritize longest edge for merging
  - Repair action: Swap reference edge to position 1 if nonmanifold
  - Suggested fixture: defect mentioning 'myNonmanifold', 'lenRef', 'GCPnts_AbscissaPoint::Length'
- **Branch 11** @ line 4410 — *candidates_found_and_returned* — COVERED by: a003, a004, a013, a075, a097, ad081, ad100, ad103 (+32 more)
  - What it tests: At least one candidate found by FindCandidates
  - Repair action: Return success and append candidates to SeqMergedEdge/Ori
- **Branch 12** @ line 4421 — *manifold_single_candidate_mode* — COVERED by: a003, a004, a013, a014, a028, a032, a034, a067 (+88 more)
  - What it tests: Manifold mode: process one candidate then stop
  - Repair action: Break after first candidate if !myNonmanifold

#### `BRepBuilderAPI_Sewing.Merging` — lines 3791–4239
(21 branches, 9 covered.)

- **Branch 1** @ line 3804 — *already_merged_bound* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Skip bounds already processed
  - Repair action: Continue to next bound
- **Branch 2** @ line 3809 — *free_edge_no_faces* — COVERED by: a078, a095, ad045, ad086, ad103, bo001, bo002, bo003 (+193 more)
  - What it tests: Floating edge with no adjacent faces
  - Repair action: Merge vertices only, mark as merged
- **Branch 3** @ line 3823 — *vertex_remapping_node1* — **UNCOVERED**
  - What it tests: First vertex needs node replacement
  - Repair action: Replace vertex with mapped node
  - Suggested fixture: defect mentioning 'nno1', 'no1.IsSame', 'myReShape->Replace'
- **Branch 4** @ line 3828 — *vertex_remapping_node2* — **UNCOVERED**
  - What it tests: Second vertex needs node replacement
  - Repair action: Replace vertex with mapped node
  - Suggested fixture: defect mentioning 'nno2', 'no2.IsSame', 'myReShape->Replace'
- **Branch 5** @ line 3840 — *cutting_sections_present* — **UNCOVERED**
  - What it tests: Bound has cutting sections from previous Cutting() phase
  - Repair action: Build BoundWire from sections
  - Suggested fixture: defect mentioning 'hasCuttingSections', 'myBoundSections.IsBound', 'BoundWire'
- **Branch 6** @ line 3851 — *previous_split_detection* — COVERED by: a014, ad035, ad051, ad080, ad086, ad097, ad099, ad117 (+272 more)
  - What it tests: At least one section already merged
  - Repair action: Set isPrevSplit flag for later wire replacement
- **Branch 7** @ line 3860 — *bound_edge_merging* — **UNCOVERED**
  - What it tests: Attempt to merge bound with nearest edges
  - Repair action: Call MergedNearestEdges to find candidates
  - Suggested fixture: defect mentioning '!isPrevSplit', 'MergedNearestEdges', 'seqMergedWithBound'
- **Branch 8** @ line 3875 — *edge_rejection_already_merged* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+32 more)
  - What it tests: Candidate edge already processed in prior merge
  - Repair action: Skip edge, remove from sequence
- **Branch 9** @ line 3878 — *edge_rejection_sections_conflict* — COVERED by: a014, ad035, ad051, ad080, ad086, ad097, ad099, ad117 (+272 more)
  - What it tests: Candidate edge is split but sections already merged
  - Repair action: Reject edge to avoid cross-cutting merges
- **Branch 10** @ line 3891 — *section_rejection_bound_conflict* — **UNCOVERED**
  - What it tests: Candidate edge is section but its bound already merged
  - Repair action: Reject edge to maintain consistency
  - Suggested fixture: defect mentioning 'mySectionBound.IsBound', 'isRejected'
- **Branch 11** @ line 3915 — *successful_bound_merge* — **UNCOVERED**
  - What it tests: At least one edge successfully merged with bound
  - Repair action: Create same-parameter merged edge via SameParameterEdge
  - Suggested fixture: defect mentioning 'nbMerged', 'SameParameterEdge', 'MergedEdge'
- **Branch 12** @ line 3934 — *orientation_forward_vs_reverse* — **UNCOVERED**
  - What it tests: Merged edge is forward or reverse oriented
  - Repair action: Adjust candidate orientation based on merged edge direction
  - Suggested fixture: defect mentioning 'isForward', 'TopAbs_FORWARD', 'TopAbs::Reverse'
- **Branch 13** @ line 3943 — *bidirectional_merge_orientation* — COVERED by: a007, a024, a026, a034, a101, ad027, ad047, ad057 (+211 more)
  - What it tests: Candidate requires reverse orientation in merge sequence
  - Repair action: Flip orientation if seqMergedWithBoundOri is false
- **Branch 14** @ line 3979 — *cutting_sections_merge_attempt* — COVERED by: a014, ad035, ad051, ad080, ad086, ad097, ad099, ad117 (+272 more)
  - What it tests: Attempt to merge cutting sections independently
  - Repair action: Iterate sections and find candidates via MergedNearestEdges
- **Branch 15** @ line 3988 — *section_already_merged_skip* — COVERED by: a014, ad035, ad050, ad051, ad080, ad086, ad097, ad099 (+288 more)
  - What it tests: Cutting section already processed
  - Repair action: Skip to next section
- **Branch 16** @ line 4005 — *section_candidate_rejection* — COVERED by: a004, a067, ad086, ad098, ad101, gs009, hea011, le049 (+32 more)
  - What it tests: Candidate for section merge conflicts with prior merges
  - Repair action: Reject candidate (analogous to bound merging)
- **Branch 17** @ line 4106 — *merge_failure_abort_sections* — **UNCOVERED**
  - What it tests: Bound merge succeeded but section merge fails
  - Repair action: Clear section merge map to avoid partial merges
  - Suggested fixture: defect mentioning 'isMerged && !isMergedSplit', 'MergedWithSections.Clear()'
- **Branch 18** @ line 4116 — *no_merge_activity* — **UNCOVERED**
  - What it tests: Neither bound nor sections merged
  - Repair action: Replace previously split bound or skip
  - Suggested fixture: defect mentioning '!isMerged && !isMergedSplit', 'isPrevSplit'
- **Branch 19** @ line 4131 — *merge_strategy_selection* — **UNCOVERED**
  - What it tests: Choose section merging over bound merging based on tolerance
  - Repair action: Compare MinSplitTol vs BoundEdgeTol to decide split vs bound
  - Suggested fixture: defect mentioning 'isSplitted', 'MinSplitTol', 'BoundEdgeTol'
- **Branch 20** @ line 4187 — *split_merge_replacement* — **UNCOVERED**
  - What it tests: Execute section merging strategy
  - Repair action: Replace bound with BoundWire and update sections in myReShape
  - Suggested fixture: defect mentioning 'isSplitted', 'myReShape->Replace', 'SectionsReShape'
- **Branch 21** @ line 4206 — *bound_merge_replacement* — **UNCOVERED**
  - What it tests: Execute bound merging strategy
  - Repair action: Replace edges in myReShape with merged edges
  - Suggested fixture: defect mentioning '!isSplitted', 'ReplaceEdge', 'myMergedEdges.Add'

#### `BRepBuilderAPI_Sewing.Perform` — lines 2189–2343
(7 branches, 1 covered.)

- **Branch 1** @ line 2200 — *analysis_skip_condition* — **UNCOVERED**
  - What it tests: Analysis flag controls whether to run FaceAnalysis stage
  - Repair action: Skip FaceAnalysis if myAnalysis is false
  - Suggested fixture: defect mentioning 'myAnalysis', 'FaceAnalysis()'
- **Branch 2** @ line 2208 — *progress_cancellation* — COVERED by: a004, a013, a034, a097, ad014, ad043, ad045, ad056 (+149 more)
  - What it tests: Progress scope exhausted during analysis
  - Repair action: Return early to avoid incomplete processing
- **Branch 3** @ line 2219 — *empty_input_skip* — **UNCOVERED**
  - What it tests: Input has no shapes and myShape is null
  - Repair action: Skip all sewing stages if no input geometry
  - Suggested fixture: defect mentioning 'myNbShapes', 'myShape.IsNull()'
- **Branch 4** @ line 2224 — *no_bound_faces* — **UNCOVERED**
  - What it tests: No boundary faces found after FaceAnalysis
  - Repair action: Skip vertex assembly and merging when no edges to sew
  - Suggested fixture: defect mentioning 'myBoundFaces.Extent()'
- **Branch 5** @ line 2242 — *cutting_stage_skip* — **UNCOVERED**
  - What it tests: Cutting flag controls optional edge cutting
  - Repair action: Skip Cutting stage if myCutting is false
  - Suggested fixture: defect mentioning 'myCutting', 'Cutting()'
- **Branch 6** @ line 2290 — *sewing_stage_enabled* — **UNCOVERED**
  - What it tests: Sewing flag controls whether to create output sewed shape
  - Repair action: Skip EdgeProcessing and CreateSewedShape if mySewing false
  - Suggested fixture: defect mentioning 'mySewing', 'EdgeProcessing()', 'CreateSewedShape()'
- **Branch 7** @ line 2311 — *same_parameter_mode* — **UNCOVERED**
  - What it tests: Both mySameParameterMode and myFaceMode enabled
  - Repair action: Apply SameParameterShape reparameterization when both modes true
  - Suggested fixture: defect mentioning 'mySameParameterMode', 'myFaceMode', 'SameParameterShape()'

#### `BRepBuilderAPI_Sewing.ProjectPointsOnCurve` — lines 5374–5476
(6 branches, 6 covered.)

- **Branch 1** @ line 5387 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 2** @ line 5394 — *exception_handling* — COVERED by: a002, a003, a011, a013, a014, a016, a017, a021 (+625 more)
  - What it tests: geometric operation failure
  - Repair action: handle_exception
- **Branch 3** @ line 5404 — *iteration_control* — COVERED by: a001, a002, a003, a004, a005, a006, a007, a008 (+1149 more)
  - What it tests: loop condition
  - Repair action: iterate
- **Branch 4** @ line 5438 — *tolerance_validation* — COVERED by: a032, a097, ad005, ad045, ad049, ad086, ad090, ad095 (+388 more)
  - What it tests: geometric distance vs tolerance
  - Repair action: adjust_tolerance
- **Branch 5** @ line 5447 — *exception_handling* — COVERED by: a002, a003, a011, a013, a014, a016, a017, a021 (+625 more)
  - What it tests: geometric operation failure
  - Repair action: handle_exception
- **Branch 6** @ line 5459 — *tolerance_validation* — COVERED by: a032, a097, ad005, ad045, ad049, ad086, ad090, ad095 (+388 more)
  - What it tests: geometric distance vs tolerance
  - Repair action: adjust_tolerance

#### `BRepBuilderAPI_Sewing.SameParameterEdge` — lines 670–1186
(30 branches, 3 covered.)

- **Branch 1** @ line 3 — *floating_edge_no_faces* — **UNCOVERED**
  - What it tests: Edges without incident faces on either first or last position
  - Repair action: return null edge early
  - Suggested fixture: defect mentioning '!listFacesFirst.Extent() || !listFacesLast.Extent()', 'floating edges'
- **Branch 2** @ line 10 — *first_call_edge_ordering* — **UNCOVERED**
  - What it tests: Whether this is initial call to determine longer edge first
  - Repair action: sort edges by computed length to prioritize processing
  - Suggested fixture: defect mentioning 'if (firstCall)', 'Take the longest edge'
- **Branch 3** @ line 20 — *edge_length_inversion* — **UNCOVERED**
  - What it tests: Swap edges if second is longer than first
  - Repair action: swap edge ordering and update whichSec flag
  - Suggested fixture: defect mentioning 'if (len1 < len2)', 'edge1 = edgeLast'
- **Branch 4** @ line 68 — *curve_location_transform* — **UNCOVERED**
  - What it tests: 3D curve with non-identity location transformation
  - Repair action: copy and transform curve to local coordinates
  - Suggested fixture: defect mentioning 'if (!loc3d.IsIdentity())', 'c3d->Transform'
- **Branch 5** @ line 89 — *closed_edge_topology* — **UNCOVERED**
  - What it tests: Edge with coincident start and end vertices (closed)
  - Repair action: flag topology for special closed-edge handling
  - Suggested fixture: defect mentioning 'bool isClosed1 = V11.IsSame(V12)'
- **Branch 6** @ line 91 — *non_closed_open_edges_vertex_mismatch* — **UNCOVERED**
  - What it tests: Two open edges with improper vertex alignment
  - Repair action: return null edge if vertices don't match expected pairing
  - Suggested fixture: defect mentioning 'if (!isClosed1 && !isClosed2)', 'if (V11.IsSame(V22) || V12.IsSame(V21))'
- **Branch 7** @ line 116 — *at_least_one_closed_edge* — **UNCOVERED**
  - What it tests: At least one of the two edges is closed
  - Repair action: compute tolerance vertex merging from closed edge
  - Suggested fixture: defect mentioning 'if (isClosed1 || isClosed2)', 'ComputeToleranceVertex'
- **Branch 8** @ line 119 — *both_edges_closed* — **UNCOVERED**
  - What it tests: Both edges are closed curves
  - Repair action: merge tolerances from both closed edge endpoints
  - Suggested fixture: defect mentioning 'if (isClosed1 && isClosed2)'
- **Branch 9** @ line 124 — *first_edge_closed_second_open* — **UNCOVERED**
  - What it tests: First edge closed, second edge open
  - Repair action: use second edge endpoints and first edge reference point
  - Suggested fixture: defect mentioning 'else if (isClosed1)', 'ComputeToleranceVertex(V22, V21, V11, V1New)'
- **Branch 10** @ line 130 — *first_edge_open_second_closed* — COVERED by: bo006, ls031, n009, tb013, twi046, twi083, u039, wr048
  - What it tests: First edge open, second edge closed
  - Repair action: use first edge endpoints and second edge reference point
- **Branch 11** @ line 139 — *open_edges_forward_pairing_check* — **UNCOVERED**
  - What it tests: Whether edges are already connected (forward pairing)
  - Repair action: flag existing connections to skip redundant sewing
  - Suggested fixture: defect mentioning 'bool isOldFirst = (secForward ? V11.IsSame(V21) : V11.IsSame(V22))'
- **Branch 12** @ line 144 — *first_vertex_needs_recompute* — **UNCOVERED**
  - What it tests: First vertex not already sewed
  - Repair action: compute merged tolerance for first vertex pair
  - Suggested fixture: defect mentioning 'if (!isOldFirst)', 'ComputeToleranceVertex(V11, V21, V1New)'
- **Branch 13** @ line 148 — *last_vertex_needs_recompute* — **UNCOVERED**
  - What it tests: Last vertex not already sewed
  - Repair action: compute merged tolerance for last vertex pair
  - Suggested fixture: defect mentioning 'if (!isOldLast)', 'ComputeToleranceVertex(V12, V22, V2New)'
- **Branch 14** @ line 215 — *seam_edge_on_closed_surface* — **UNCOVERED**
  - What it tests: Second edge is seam on U or V closed surface
  - Repair action: extract reversed PCurve for non-manifold seam handling
  - Suggested fixture: defect mentioning 'bool isSeam2 = ((IsUClosedSurface', 'BRep_Tool::IsClosed'
- **Branch 15** @ line 219 — *seam_edge_non_manifold_forbidden* — **UNCOVERED**
  - What it tests: Non-manifold seams detected but flag disabled
  - Repair action: return null edge to reject non-manifold configuration
  - Suggested fixture: defect mentioning 'if (!myNonmanifold)', 'return TopoDS_Edge()'
- **Branch 16** @ line 227 — *missing_pcurves_both_directions* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: No PCurve found on surface for either direction
  - Repair action: skip this face in merging process (continue)
- **Branch 17** @ line 235 — *reverse_seam_pcurve_line_type* — **UNCOVERED**
  - What it tests: Reversed seam PCurve is linear and needs parameter reversal
  - Repair action: trim line and reverse parameter bounds
  - Suggested fixture: defect mentioning 'if (!secForward)', 'c2d21->IsKind(STANDARD_TYPE(Geom2d_Line))'
- **Branch 18** @ line 267 — *null_pcurve_after_samerange* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: SameRange operation failed to normalize PCurve bounds
  - Repair action: skip face processing (continue)
- **Branch 19** @ line 295 — *first_edge_seam_surface_closed* — **UNCOVERED**
  - What it tests: First edge is seam on U or V closed surface
  - Repair action: extract both PCurve directions for seam handling
  - Suggested fixture: defect mentioning 'bool isSeam1 = ((IsUClosedSurface(surf1, edge1'
- **Branch 20** @ line 306 — *seam_non_manifold_first_edge_forbidden* — **UNCOVERED**
  - What it tests: Non-manifold seams on first edge but disabled
  - Repair action: return null edge
  - Suggested fixture: defect mentioning 'if (!myNonmanifold)', 'isSeam1'
- **Branch 21** @ line 313 — *seam_orientation_decision_first_edge* — **UNCOVERED**
  - What it tests: Seam on first edge with forward vs reversed orientation
  - Repair action: swap PCurve order based on orientation
  - Suggested fixture: defect mentioning 'if (Ori == TopAbs_FORWARD)', 'aBuilder.UpdateEdge(edge, c2d1, c2d11'
- **Branch 22** @ line 332 — *same_surface_both_edges* — **UNCOVERED**
  - What it tests: Both edges lie on same surface
  - Repair action: detect and handle seam merging on shared surface
  - Suggested fixture: defect mentioning 'if (surf2 == surf1)'
- **Branch 23** @ line 335 — *same_surface_identical_location* — **UNCOVERED**
  - What it tests: Same surface with identical location (not transformed)
  - Repair action: check closed-surface seam distance heuristic
  - Suggested fixture: defect mentioning 'if (!loc2.IsDifferent(loc1))', 'IsUClosedSurface'
- **Branch 24** @ line 349 — *seam_distance_threshold_closed_surface* — **UNCOVERED**
  - What it tests: Merged PCurve distance exceeds 75% of closed surface bound
  - Repair action: flag as seam and use dual PCurve representation
  - Suggested fixture: defect mentioning 'isSeam = ((uclosed && aDist > 0.75', 'fabs(U2 - U1)'
- **Branch 25** @ line 405 — *same_parameter_enforcement_needed* — **UNCOVERED**
  - What it tests: Edge has valid PCurve representation requiring parameter sync
  - Repair action: call SameParameter to enforce parametric equivalence
  - Suggested fixture: defect mentioning 'if (isResEdge)', 'SameParameter(edge)'
- **Branch 26** @ line 422 — *merge_quality_insufficient_or_tolerance_large* — **UNCOVERED**
  - What it tests: First attempt produces edge without PCurves, wrong params, or excessive tolerance
  - Repair action: attempt second merge strategy on alternate face section
  - Suggested fixture: defect mentioning 'if (firstCall && (!isResEdge || !isSamePar || tolReached > myTolerance))'
- **Branch 27** @ line 437 — *tolerance_comparison_second_vs_first* — **UNCOVERED**
  - What it tests: Second merge produces valid result with lower tolerance
  - Repair action: accept second result and update edge reference
  - Suggested fixture: defect mentioning 'second_ok = (BRep_Tool::SameParameter(s_edge) && tolReached_2 < tolReached)'
- **Branch 28** @ line 494 — *computed_tolerance_improvement* — **UNCOVERED**
  - What it tests: Point-to-surface distance yields lower tolerance than SameParameter
  - Repair action: override edge tolerance with computed max distance bound
  - Suggested fixture: defect mentioning 'if (maxTol >= 0. && maxTol < tolReached)'
- **Branch 29** @ line 496 — *tolerance_exceeds_maximum* — **UNCOVERED**
  - What it tests: Edge tolerance already exceeds MaxTolerance threshold
  - Repair action: directly overwrite BRep_TEdge tolerance via type cast
  - Suggested fixture: defect mentioning 'if (tolReached > MaxTolerance())', 'static_cast<BRep_TEdge*>'
- **Branch 30** @ line 512 — *final_edge_tolerance_validation* — **UNCOVERED**
  - What it tests: Final edge tolerance exceeds global maximum
  - Repair action: nullify edge to reject result and return null
  - Suggested fixture: defect mentioning 'if (tolEdge1 > MaxTolerance())', 'edge.Nullify()'

#### `BRepBuilderAPI_Sewing.VerticesAssembling` — lines 3550–3602
(5 branches, 4 covered.)

- **Branch 1** @ line 3554 — *no_vertices_to_assemble* — **UNCOVERED**
  - What it tests: Early exit if no vertices exist
  - Repair action: Skip entire assembly process
  - Suggested fixture: defect mentioning 'nbVert', 'nbVertFree', 'Extent()'
- **Branch 2** @ line 3558 — *vertex_binding_population* — COVERED by: a011, a018, a019, a029, a074, a101, a102, ad003 (+45 more)
  - What it tests: Build node-to-sections map from bound faces
  - Repair action: Fill myNodeSections map with face references per node
- **Branch 3** @ line 3577 — *face_bound_vertex_assembly* — COVERED by: a004, a010, a021, a101, a106, ad005, ad015, ad026 (+102 more)
  - What it tests: Glue vertices on bounded faces
  - Repair action: Call GlueVertices until convergence on myVertexNode
- **Branch 4** @ line 3587 — *progress_exhaustion* — COVERED by: a004, a013, a026, a034, a097, ad014, ad043, ad045 (+156 more)
  - What it tests: Check if progress scope exhausted mid-process
  - Repair action: Early return to avoid partial state
- **Branch 5** @ line 3591 — *free_floating_edge_assembly* — COVERED by: a004, a010, a021, a101, a106, ad005, ad015, ad026 (+102 more)
  - What it tests: Glue vertices on floating edges (non-bounded)
  - Repair action: Call GlueVertices on myVertexNodeFree until convergence


### `src/ModelingAlgorithms/TKTopAlgo/BRepLib/BRepLib.cxx`

17 methods, 194 branches, 26 covered.

#### `BRepLib.BuildCurve3d` — lines 306–456
(18 branches, 2 covered.)

- **Branch 1** @ line 321 — *existing-3d-curve-shortcut* — **UNCOVERED**
  - What it tests: edge already has valid 3D curve
  - Repair action: return true immediately, no work needed
  - Suggested fixture: defect mentioning 'BRep_Tool::Curve', 'C.IsNull()'
- **Branch 2** @ line 330 — *same-range-prereq-check* — **UNCOVERED**
  - What it tests: edge satisfies SameRange constraint
  - Repair action: force SameRange repair before building 3D curve
  - Suggested fixture: defect mentioning 'CheckSameRange()', 'SameRange()'
- **Branch 3** @ line 342 — *planar-surface-search* — **UNCOVERED**
  - What it tests: iterate to find planar surface (optimization path)
  - Repair action: unwrap RectangularTrimmedSurface if needed
  - Suggested fixture: defect mentioning 'down_cast<Geom_RectangularTrimmedSurface>', 'BasisSurface()'
- **Branch 4** @ line 348 — *surface-is-plane* — **UNCOVERED**
  - What it tests: surface is planar or contains planar basis
  - Repair action: use fast planar projection instead of full approximation
  - Suggested fixture: defect mentioning 'Geom_Plane', 'IsNull()'
- **Branch 5** @ line 358 — *plane-found-optimization* — **UNCOVERED**
  - What it tests: planar case: project 2D curve to 3D via plane axes
  - Repair action: call GeomLib::To3d for direct projection
  - Suggested fixture: defect mentioning 'Position().Ax2()', 'GeomLib::To3d'
- **Branch 6** @ line 363 — *plane-projection-failed* — **UNCOVERED**
  - What it tests: 3D projection failed (degenerate or invalid)
  - Repair action: return false, cannot build 3D curve
  - Suggested fixture: defect mentioning 'C3d.IsNull()'
- **Branch 7** @ line 371 — *planar-edge-update* — **UNCOVERED**
  - What it tests: update edge with projected 3D curve
  - Repair action: UpdateEdge with 3D curve and validate range from surface
  - Suggested fixture: defect mentioning 'B.UpdateEdge', 'B.Range', 'LocalLoc'
- **Branch 8** @ line 375 — *non-planar-fallback* — **UNCOVERED**
  - What it tests: no planar surface found, use general approximation
  - Repair action: collect all 2D curves on non-planar surfaces and approximate
  - Suggested fixture: defect mentioning 'else {'
- **Branch 9** @ line 382 — *degenerate-edge-check* — **UNCOVERED**
  - What it tests: edge is degenerate (point-like)
  - Repair action: skip building curve for degenerate edge
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated'
- **Branch 10** @ line 386 — *multi-surface-curve-collection* — COVERED by: gb004, gp035, in014, twi100
  - What it tests: edge has multiple 2D curves (up to 2) on different surfaces
  - Repair action: collect all non-null curves and surfaces
- **Branch 11** @ line 396 — *valid-pcurve-accumulation* — **UNCOVERED**
  - What it tests: 2D curve is valid and count < 2
  - Repair action: store curve, surface, location, and parameter range
  - Suggested fixture: defect mentioning 'Curve2dPtr.IsNull()', 'jj < 2'
- **Branch 12** @ line 411 — *adaptor-setup-primary* — **UNCOVERED**
  - What it tests: construct adaptors for first 2D curve on surface
  - Repair action: create Geom2dAdaptor and GeomAdaptor for approximation input
  - Suggested fixture: defect mentioning 'Geom2dAdaptor_Curve', 'GeomAdaptor_Surface'
- **Branch 13** @ line 417 — *curve-on-surface-reference* — **UNCOVERED**
  - What it tests: create combined 3D reference via curve-on-surface adaptor
  - Repair action: Adaptor3d_CurveOnSurface evaluates 3D points from 2D curves
  - Suggested fixture: defect mentioning 'Adaptor3d_CurveOnSurface'
- **Branch 14** @ line 421 — *approximation-call* — COVERED by: a032, ad045, ad086, bo008, bo025, bo027, bo028, bo030 (+370 more)
  - What it tests: approximate curve-on-surface to target continuity/degree
  - Repair action: call GeomLib::BuildCurve3d with tolerance and degree constraints
- **Branch 15** @ line 436 — *approximation-success-check* — **UNCOVERED**
  - What it tests: approximation produced valid 3D curve
  - Repair action: update edge with new curve or return false on failure
  - Suggested fixture: defect mentioning 'NewCurvePtr.IsNull()'
- **Branch 16** @ line 440 — *edge-update-with-tolerance* — **UNCOVERED**
  - What it tests: update edge curve and tolerance after approximation
  - Repair action: UpdateEdge with new curve, location, and max deviation
  - Suggested fixture: defect mentioning 'B.UpdateEdge', 'max_deviation'
- **Branch 17** @ line 441 — *same-parameter-qualification* — **UNCOVERED**
  - What it tests: only one 2D curve means edge can be marked SameParameter
  - Repair action: set SameParameter flag if jj == 1
  - Suggested fixture: defect mentioning 'jj == 1', 'B.SameParameter'
- **Branch 18** @ line 450 — *degenerate-edge-fallback* — **UNCOVERED**
  - What it tests: degenerate edge detected in non-planar case
  - Repair action: return false, cannot build curve for degenerate
  - Suggested fixture: defect mentioning 'else { return false'

#### `BRepLib.BuildCurves3d` — lines 473–489
(4 branches, 2 covered.)

- **Branch 1** @ line 476 — *shape-edge-iteration* — COVERED by: tsh018
  - What it tests: iterate all edges in shape (TopExp_Explorer)
  - Repair action: traverse shape topology for edges
- **Branch 2** @ line 480 — *duplicate-edge-deduplication* — **UNCOVERED**
  - What it tests: edge not already processed in this shape
  - Repair action: use map to skip shared edges (avoid double processing)
  - Suggested fixture: defect mentioning 'a_counter.Add', 'NCollection_Map'
- **Branch 3** @ line 483 — *per-edge-build-success* — COVERED by: a032, ad045, ad086, bo008, bo025, bo027, bo028, bo030 (+370 more)
  - What it tests: BuildCurve3d succeeds for this edge
  - Repair action: call BuildCurve3d with same parameters for each edge
- **Branch 4** @ line 484 — *aggregate-success-tracking* — **UNCOVERED**
  - What it tests: overall shape build success (all edges succeeded)
  - Repair action: combine status: ok = ok && boolean_value
  - Suggested fixture: defect mentioning 'ok = ok && boolean_value'

#### `BRepLib.ContinuityOfFaces` — lines 2201–2419
(20 branches, 1 covered.)

- **Branch 1** @ line 2202 — *SEAM_EDGE_DETECTION* — **UNCOVERED**
  - What it tests: Both faces identical (seam edge on single surface)
  - Repair action: Flag seam=true; simplify continuity logic
  - Suggested fixture: defect mentioning 'isSeam = theFace1.IsEqual(theFace2)'
- **Branch 2** @ line 2209 — *EDGE_CLOSED_ON_BOTH_FACES* — **UNCOVERED**
  - What it tests: Edge is closed on both distinct faces (shared seam)
  - Repair action: Handle as seam: extract oriented edge representations
  - Suggested fixture: defect mentioning '!theFace1.IsSame(theFace2) && BRep_Tool::IsClosed'
- **Branch 3** @ line 2225 — *EDGE_NOT_FOUND_IN_FACE* — **UNCOVERED**
  - What it tests: Edge topology not found in face boundary
  - Repair action: Return C0 (no continuity); topology error
  - Suggested fixture: defect mentioning 'anEdgeInFace1.IsNull()', 'return GeomAbs_C0'
- **Branch 4** @ line 2250 — *MISSING_PCURVE_REPRESENTATION* — **UNCOVERED**
  - What it tests: One or both PCurves missing from faces
  - Repair action: Return C0 (geometric continuity undefined)
  - Suggested fixture: defect mentioning 'aCurve1.IsNull() || aCurve2.IsNull()', 'return GeomAbs_C0'
- **Branch 5** @ line 2261 — *RECTANGULAR_TRIMMED_SURFACE* — **UNCOVERED**
  - What it tests: Surface is RectangularTrimmedSurface wrapper
  - Repair action: Extract basis surface for continuity analysis
  - Suggested fixture: defect mentioning 'STANDARD_TYPE(Geom_RectangularTrimmedSurface)', 'BasisSurface()'
- **Branch 6** @ line 2271 — *ELEMENTARY_SEAM_CONTINUITY* — **UNCOVERED**
  - What it tests: Seam edge on elementary surfaces (plane, sphere, cylinder, etc.)
  - Repair action: Return CN (infinite continuity) for elementary surfaces
  - Suggested fixture: defect mentioning 'isSeam && isElementary', 'return GeomAbs_CN'
- **Branch 7** @ line 2300 — *G1_CONTINUITY_CANDIDATE* — **UNCOVERED**
  - What it tests: Loop sample 21 points along edge; test G1 at each
  - Repair action: Evaluate tangent vectors and normal consistency
  - Suggested fixture: defect mentioning 'for (int i = 0; i <= 20)', 'aSP1.Calculate(u)', 'aSP2.Calculate(u)'
- **Branch 8** @ line 2319 — *TANGENT_VECTOR_ALIGNMENT* — **UNCOVERED**
  - What it tests: Tangent vectors parallel (cross product <= tolerance)
  - Repair action: Flag isSmoothSuspect=true; test normal consistency
  - Suggested fixture: defect mentioning 'aDer1.CrossSquareMagnitude(aDer2) <= anAngleTol2'
- **Branch 9** @ line 2333 — *NORMAL_VECTOR_OPPOSITE* — **UNCOVERED**
  - What it tests: Surface normals point in opposite directions
  - Repair action: Return C0; normals must be codirectional for any continuity
  - Suggested fixture: defect mentioning 'aNormal1 * aNormal2 < 0.', 'return GeomAbs_C0'
- **Branch 10** @ line 2339 — *PROJECTION_REFINEMENT* — **UNCOVERED**
  - What it tests: Tangents not aligned; refine via projection onto second surface
  - Repair action: Locate closest point on second PCurve; recompute tangent
  - Suggested fixture: defect mentioning '!isSmoothSuspect', 'ext.Perform', 'aSP2.Calculate(poc.Parameter())'
- **Branch 11** @ line 2360 — *G1_CONTINUITY_CONFIRMED* — **UNCOVERED**
  - What it tests: After refinement, tangents are parallel (G1 test)
  - Repair action: Tentatively set aCurCont=G1; test for C1
  - Suggested fixture: defect mentioning 'aCurCont = GeomAbs_G1'
- **Branch 12** @ line 2361 — *C1_CONTINUITY_CONFIRMED* — **UNCOVERED**
  - What it tests: Tangent vectors equal magnitude and codirectional (C1 test)
  - Repair action: Upgrade from G1 to C1 continuity
  - Suggested fixture: defect mentioning 'std::abs(std::sqrt(aSqLen1) - std::sqrt(aSqLen2)) < Confusion', 'aCurCont = GeomAbs_C1'
- **Branch 13** @ line 2372 — *G2_TEST_SKIP* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Current continuity < G2 (not worth testing G2/C2)
  - Repair action: Skip second-derivative tests; continue to next sample
- **Branch 14** @ line 2382 — *PRINCIPAL_CURVATURE_ANALYSIS* — **UNCOVERED**
  - What it tests: Loop over principal curvature directions (2 per surface)
  - Repair action: Test alignment of principal curvatures and magnitudes
  - Suggested fixture: defect mentioning 'aSP1.Curvature', 'aSP2.Curvature', 'for (int aStep = 0; aStep <= 1)'
- **Branch 15** @ line 2386 — *CURVATURE_DIRECTION_ALIGNMENT* — **UNCOVERED**
  - What it tests: Principal curvature directions parallel (exact alignment)
  - Repair action: Test magnitude and second principal direction alignment
  - Suggested fixture: defect mentioning 'aCrvDir1[0].XYZ().CrossSquareMagnitude(aCrvDir2[aStep].XYZ()) <= SquareConfusion'
- **Branch 16** @ line 2388 — *CURVATURE_MAGNITUDE_MATCH* — **UNCOVERED**
  - What it tests: Principal curvature magnitudes equal
  - Repair action: Test second principal direction and magnitude
  - Suggested fixture: defect mentioning 'std::abs(aCrvLen1[0] - aCrvLen2[aStep]) < Confusion'
- **Branch 17** @ line 2393 — *C2_CONTINUITY_CONFIRMED* — **UNCOVERED**
  - What it tests: Both principal curvatures/directions match + C1 continuity
  - Repair action: Upgrade from C1 to C2 continuity
  - Suggested fixture: defect mentioning 'aCurCont == GeomAbs_C1 && aCrvDir1[0].Dot(aCrvDir2[aStep]) > Confusion', 'aCurCont = GeomAbs_C2'
- **Branch 18** @ line 2400 — *G2_CONTINUITY_CONFIRMED* — **UNCOVERED**
  - What it tests: Curvatures aligned but not codirectional (G2 vs C2)
  - Repair action: Set G2 continuity (geometric smoothness without parametric match)
  - Suggested fixture: defect mentioning 'aCurCont = GeomAbs_G2'
- **Branch 19** @ line 2406 — *CONTINUITY_DOWNGRADE* — **UNCOVERED**
  - What it tests: Current sample has lower continuity than previous minimum
  - Repair action: Update global continuity to minimum (aCont=aCurCont)
  - Suggested fixture: defect mentioning 'aCurCont < aCont', 'aCont = aCurCont'
- **Branch 20** @ line 2414 — *ELEMENTARY_SURFACE_CN_UPGRADE* — **UNCOVERED**
  - What it tests: C2 continuity on elementary surfaces (plane/sphere/cylinder/etc.)
  - Repair action: Upgrade C2 to CN (infinite continuity for elementary surfaces)
  - Suggested fixture: defect mentioning 'isElementary && aCont == GeomAbs_C2', 'aCont = GeomAbs_CN'

#### `BRepLib.EncodeRegularity` — lines 2570–2590
(2 branches, 2 covered.)

- **Branch 1** @ line 2576 — *G0-discontinuity* — COVERED by: bo028
  - What it tests: Checks if edge continuity is already C0 or better
  - Repair action: Compute actual continuity via ContinuityOfFaces; tag edge with appropriate GeomAbs_Shape regularity
- **Branch 2** @ line 2583 — *computation-failure* — COVERED by: ad086
  - What it tests: Exception handler for continuity computation failures
  - Repair action: Silently catch and skip; edge remains untagged

#### `BRepLib.EncodeRegularity_1st_overload` — lines 2548–2563
(2 branches, 0 covered.)

- **Branch 1** @ line 2550 — *EDGE_NORMALIZATION* — **UNCOVERED**
  - What it tests: Edge shape normalization: remove location and orientation
  - Repair action: Store pure edge (no transformation, FORWARD orientation)
  - Suggested fixture: defect mentioning 'aNullLoc', 'TopAbs_FORWARD', 'Add(aPureEdges)'
- **Branch 2** @ line 2562 — *REGULARITY_ENCODING* — **UNCOVERED**
  - What it tests: Delegate to internal ::EncodeRegularity function
  - Repair action: Encode continuity information for all edges
  - Suggested fixture: defect mentioning '::EncodeRegularity(S, TolAng, aMap, aPureEdges)'

#### `BRepLib.EnsureNormalConsistency` — lines 2597–2725
(15 branches, 2 covered.)

- **Branch 1** @ line 2611 — *null-surface* — **UNCOVERED**
  - What it tests: Surface handle is null
  - Repair action: Skip face; no geometry to compute normals from
  - Suggested fixture: defect mentioning 'aSurf.IsNull()'
- **Branch 2** @ line 2617 — *missing-triangulation* — **UNCOVERED**
  - What it tests: Triangulation absent
  - Repair action: Skip face; no mesh to set normals on
  - Suggested fixture: defect mentioning 'aPT.IsNull()'
- **Branch 3** @ line 2621 — *normals-already-present* — **UNCOVERED**
  - What it tests: Normals exist AND not forcing recompute
  - Repair action: Mark isNormalsFound=true; skip computation; continue
  - Suggested fixture: defect mentioning 'theForceComputeNormals', 'HasNormals'
- **Branch 4** @ line 2634 — *undefined-surface-normal* — **UNCOVERED**
  - What it tests: GeomLProp_SLProps cannot compute normal at UV (e.g. singular point)
  - Repair action: Set zero normal (0,0,0); flag for debug; continue
  - Suggested fixture: defect mentioning 'IsNormalDefined'
- **Branch 5** @ line 2644 — *face-orientation-reversal* — **UNCOVERED**
  - What it tests: Face has REVERSED orientation
  - Repair action: Flip computed normal direction before storing
  - Suggested fixture: defect mentioning 'Orientation() == TopAbs_REVERSED'
- **Branch 6** @ line 2656 — *no-normals-found-early-exit* — **UNCOVERED**
  - What it tests: isNormalsFound stays false (all faces skipped)
  - Repair action: Return aRetVal immediately (no correction done)
  - Suggested fixture: defect mentioning '!isNormalsFound'
- **Branch 7** @ line 2669 — *edge-not-shared-by-two-faces* — **UNCOVERED**
  - What it tests: Edge has != 2 adjacent faces (boundary or singular)
  - Repair action: Skip edge; no continuity check needed
  - Suggested fixture: defect mentioning 'anEdgList.Extent() != 2'
- **Branch 8** @ line 2681 — *missing-dual-triangulation* — **UNCOVERED**
  - What it tests: Either adjacent face lacks triangulation
  - Repair action: Skip edge pair; cannot compare normals
  - Suggested fixture: defect mentioning 'aPT1.IsNull() || aPT2.IsNull()'
- **Branch 9** @ line 2686 — *missing-dual-normals* — **UNCOVERED**
  - What it tests: Either triangulation lacks normals
  - Repair action: Skip edge pair
  - Suggested fixture: defect mentioning 'HasNormals()'
- **Branch 10** @ line 2696 — *polygon-edge-index-mismatch* — **UNCOVERED**
  - What it tests: Edge polygons on two triangulations have different node index ranges
  - Repair action: Skip edge; cannot establish node correspondence
  - Suggested fixture: defect mentioning 'Nodes().Lower()', 'Nodes().Upper()'
- **Branch 11** @ line 2702 — *inconsistent-normal-direction* — **UNCOVERED**
  - What it tests: Loop: normal dot product > angle threshold (same hemisphere)
  - Repair action: Average normals; set on both faces; mark aRetVal=true
  - Suggested fixture: defect mentioning 'aDot > aThresDot'
- **Branch 12** @ line 2713 — *normal-dot-comparison* — **UNCOVERED**
  - What it tests: Compute dot product of dual normals
  - Repair action: If > threshold, average; else skip (opposing hemisphere)
  - Suggested fixture: defect mentioning 'aDot = aNorm1 * aNorm2'
- **Branch 13** @ line 2716 — *normal-averaging* — **UNCOVERED**
  - What it tests: Normals are aligned enough to average
  - Repair action: Normalize sum of both normals; write back to both triangulations
  - Suggested fixture: defect mentioning '(aNorm1 + aNorm2).Normalized()'
- **Branch 14** @ line 2606 — *face-iteration* — COVERED by: tsh018
  - What it tests: Loop over all faces in shape
  - Repair action: Process each face independently for normal computation
- **Branch 15** @ line 2664 — *edge-iteration* — COVERED by: gn010, m010, m064, os007, os022, pmi032, pmi091, pmi112 (+12 more)
  - What it tests: Loop over all edges in shape
  - Repair action: For each edge, check normal consistency on adjacent faces

#### `BRepLib.OrientClosedSolid` — lines 2088–2102
(3 branches, 1 covered.)

- **Branch 1** @ line 2092 — *SOLID_ORIENTATION_INVERTED* — **UNCOVERED**
  - What it tests: Infinite point is classified as INSIDE the solid
  - Repair action: Reverse solid orientation to correct outward normal convention
  - Suggested fixture: defect mentioning 'where.State() == TopAbs_IN', 'solid.Reverse()'
- **Branch 2** @ line 2096 — *SOLID_CLASSIFICATION_AMBIGUOUS* — COVERED by: in014
  - What it tests: Infinite point classified as ON surface or UNKNOWN
  - Repair action: Return false; cannot reliably fix orientation
- **Branch 3** @ line 2101 — *SOLID_ORIENTATION_CORRECT* — **UNCOVERED**
  - What it tests: Infinite point classified as OUTSIDE (expected state)
  - Repair action: Return true; solid orientation is correct
  - Suggested fixture: defect mentioning 'where.State() == TopAbs_OUT', 'return true'

#### `BRepLib.ReverseSortFaces` — lines 2955–3009
(7 branches, 2 covered.)

- **Branch 1** @ line 2968 — *null-surface* — **UNCOVERED**
  - What it tests: Surface is null
  - Repair action: Add to LTri
  - Suggested fixture: defect mentioning '!S.IsNull()'
- **Branch 2** @ line 2973 — *geometry-type-plane* — **UNCOVERED**
  - What it tests: Type is Plane
  - Repair action: Add to LPlan
  - Suggested fixture: defect mentioning 'GeomAbs_Plane'
- **Branch 3** @ line 2977 — *geometry-type-cylinder* — COVERED by: gn014, n030
  - What it tests: Type is Cylinder
  - Repair action: Add to LCyl
- **Branch 4** @ line 2981 — *geometry-type-cone* — **UNCOVERED**
  - What it tests: Type is Cone
  - Repair action: Add to LCon
  - Suggested fixture: defect mentioning 'GeomAbs_Cone'
- **Branch 5** @ line 2985 — *geometry-type-sphere* — **UNCOVERED**
  - What it tests: Type is Sphere
  - Repair action: Add to LSphere
  - Suggested fixture: defect mentioning 'GeomAbs_Sphere'
- **Branch 6** @ line 2989 — *geometry-type-torus* — **UNCOVERED**
  - What it tests: Type is Torus
  - Repair action: Add to LTor
  - Suggested fixture: defect mentioning 'GeomAbs_Torus'
- **Branch 7** @ line 2993 — *geometry-type-other* — COVERED by: a005, a006, a037, a038, a068, a076, a103, ad044 (+90 more)
  - What it tests: Type is other
  - Repair action: Add to LOther

#### `BRepLib.SameParameter` — lines 1255–1740
(31 branches, 1 covered.)

- **Branch 1** @ line 1256 — *ALREADY_SAME_PARAMETER* — **UNCOVERED**
  - What it tests: Edge already marked with SameParameter flag
  - Repair action: Return empty edge (early exit, no repair needed)
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter(theEdge)'
- **Branch 2** @ line 1265 — *MISSING_3D_CURVE* — **UNCOVERED**
  - What it tests: No 3D curve representation exists
  - Repair action: Return empty edge (cannot repair without 3D geometry)
  - Suggested fixture: defect mentioning 'C3d.IsNull()', 'GetCurve3d'
- **Branch 3** @ line 1273 — *EDGE_REUSE_STRATEGY* — **UNCOVERED**
  - What it tests: Whether to modify original edge or create copy
  - Repair action: Use original edge (IsUseOldEdge) vs create EmptyCopied
  - Suggested fixture: defect mentioning 'IsUseOldEdge', 'EmptyCopied'
- **Branch 4** @ line 1306 — *TRIMMED_CURVE_TYPE* — **UNCOVERED**
  - What it tests: Detect TrimmedCurve wrapping periodic basis curve
  - Repair action: Flag m_TrimmedPeriodical for parameter range adjustment
  - Suggested fixture: defect mentioning 'Geom_TrimmedCurve', 'm_TrimmedPeriodical'
- **Branch 5** @ line 1313 — *NON_PERIODIC_CURVE_RANGE* — **UNCOVERED**
  - What it tests: Non-periodic curve with clipped parameter bounds
  - Repair action: Adjust f3d, l3d to curve domain, respecting TrimmedPeriodical flag
  - Suggested fixture: defect mentioning '!C3d->IsPeriodic()', 'FirstParameter', 'LastParameter'
- **Branch 6** @ line 1333 — *TRANSFORMED_LOCATION* — COVERED by: a017, a067, ad086, gp016
  - What it tests: Curve has non-identity transformation
  - Repair action: Apply transformation to 3D curve
- **Branch 7** @ line 1360 — *CURVE_ON_SURFACE_MISSING* — **UNCOVERED**
  - What it tests: Curve-on-surface representation exists (YaPCu flag)
  - Repair action: Skip 2D/surface processing for purely 3D edges
  - Suggested fixture: defect mentioning 'IsCurveOnSurface()', 'YaPCu'
- **Branch 8** @ line 1366 — *SURFACE_LOCATION_TRANSFORM* — **UNCOVERED**
  - What it tests: Surface has non-identity location
  - Repair action: Apply transformation to surface
  - Suggested fixture: defect mentioning '!PCLoc.IsIdentity()', 'Surface->Transformed'
- **Branch 9** @ line 1372 — *CLOSED_SURFACE_DUAL_PCURVE* — **UNCOVERED**
  - What it tests: Closed surface with dual PCurves (seam edge)
  - Repair action: Load both PC[0] and PC[1] representations
  - Suggested fixture: defect mentioning 'IsCurveOnClosedSurface()', 'PCurve2()'
- **Branch 10** @ line 1387 — *PCURVE_RANGE_MISMATCH* — **UNCOVERED**
  - What it tests: PCurve parameter range differs from 3D curve range
  - Repair action: Call GeomLib::SameRange to reparametrize PCurve
  - Suggested fixture: defect mentioning '!SameRange', 'GeomLib::SameRange'
- **Branch 11** @ line 1398 — *NUMERICAL_ERROR_EXPLOSION* — **UNCOVERED**
  - What it tests: Tolerance error exceeds BigError (1e10) threshold
  - Repair action: Abandon processing, mark maxdist=error, break loop
  - Suggested fixture: defect mentioning 'error > BigError', 'BigError = 1.e10'
- **Branch 12** @ line 1404 — *BSPLINE_C0_CONTINUITY_DISCONTINUITY* — **UNCOVERED**
  - What it tests: BSpline PCurve with C0 continuity (has knot discontinuities)
  - Repair action: Upgrade C0 to C1 using Geom2dConvert::C0BSplineToC1BSplineCurve
  - Suggested fixture: defect mentioning 'GeomAbs_BSplineCurve && GeomAbs_C0', 'C0BSplineToC1BSplineCurve'
- **Branch 13** @ line 1419 — *PERIODIC_BSPLINE_ORIGIN_SHIFT* — **UNCOVERED**
  - What it tests: Periodic BSpline origin shifted after C0->C1 conversion
  - Repair action: SetOrigin to nearest knot that maintains parameterization
  - Suggested fixture: defect mentioning 'bs2d->IsPeriodic()', 'SetOrigin'
- **Branch 14** @ line 1444 — *REMAINING_C0_AFTER_FIRST_PASS* — **UNCOVERED**
  - What it tests: C0 discontinuity persists after initial C0->C1 conversion
  - Repair action: Attempt alternative tolerance (EvalTol) to force smoother spline
  - Suggested fixture: defect mentioning 'bs2d->Continuity() == GeomAbs_C0', 'EvalTol'
- **Branch 15** @ line 1447 — *EVALUATED_TOLERANCE_FALLBACK* — **UNCOVERED**
  - What it tests: EvalTol succeeds: alternative tolerance available
  - Repair action: Retry C0->C1 with computed fallback tolerance (Tol2dbail)
  - Suggested fixture: defect mentioning 'EvalTol(curPC, S, GAC, theTolerance, tolbail)'
- **Branch 16** @ line 1471 — *PERIODIC_ORIGIN_SHIFT_FALLBACK* — **UNCOVERED**
  - What it tests: Periodic BSpline origin shifted after fallback C0->C1
  - Repair action: SetOrigin to nearest knot for fallback spline
  - Suggested fixture: defect mentioning 'bs2d->IsPeriodic()', 'SetOrigin (fallback)'
- **Branch 17** @ line 1496 — *IRRECONCILABLE_C0_DISCONTINUITY* — **UNCOVERED**
  - What it tests: Both C0->C1 attempts fail (revert to original noisy spline)
  - Repair action: goodpc=true, repar=false; keep original bs2d unmodified
  - Suggested fixture: defect mentioning 'bs2d = bs2dsov', 'repar = false'
- **Branch 18** @ line 1509 — *ACCEPTABLE_PCURVE* — **UNCOVERED**
  - What it tests: PCurve passes quality gates (goodpc=true)
  - Repair action: Proceed to reparametrization and SameParameter check
  - Suggested fixture: defect mentioning 'if (goodpc)'
- **Branch 19** @ line 1513 — *BSPLINE_REPARAMETRIZATION_BY_PARAMETER* — **UNCOVERED**
  - What it tests: BSpline needs reparametrization to match 3D curve range
  - Repair action: Reparametrize knots from [fC0,lC0] to [f3d,l3d]
  - Suggested fixture: defect mentioning 'BSplCLib::Reparametrize', 'repar = true'
- **Branch 20** @ line 1523 — *REPARAMETRIZATION_ERROR_DETERIORATION* — **UNCOVERED**
  - What it tests: Reparametrized spline error worse than original
  - Repair action: Revert to original spline, set isANA=true
  - Suggested fixture: defect mentioning 'error1 > error', 'isANA = true'
- **Branch 21** @ line 1541 — *KNOT_RATIO_ANOMALY* — **UNCOVERED**
  - What it tests: BSpline has irregular knot spacing (ratio > 10:1)
  - Repair action: Flag as IsBad, attempt curvilinear reparametrization
  - Suggested fixture: defect mentioning 'dtratio > critratio', 'dtratio = 10'
- **Branch 22** @ line 1573 — *KNOT_RESOLUTION_INSUFFICIENT* — **UNCOVERED**
  - What it tests: After knot ratio check, min knot interval too small
  - Repair action: Attempt Approx_CurvilinearParameter (arc-length parameterization)
  - Suggested fixture: defect mentioning 'IsBad', 'dtmin < dtcur', 'Approx_CurvilinearParameter'
- **Branch 23** @ line 1589 — *CONTINUITY_DOWNGRADE_FOR_APPROXIMATION* — **UNCOVERED**
  - What it tests: Curvilinear approx target continuity (C2 cap)
  - Repair action: Force continuity <= C2 for arc-length reparametrization
  - Suggested fixture: defect mentioning 'if (cont > GeomAbs_C2)', 'cont = GeomAbs_C2'
- **Branch 24** @ line 1604 — *CURVILINEAR_APPROXIMATION_SUCCESS* — **UNCOVERED**
  - What it tests: Approx_CurvilinearParameter succeeded (IsDone || HasResult)
  - Repair action: Replace spline with arc-length-parameterized curve
  - Suggested fixture: defect mentioning 'AppCurPar.IsDone() || AppCurPar.HasResult()'
- **Branch 25** @ line 1610 — *CURVILINEAR_OUTPUT_RANGE_MISMATCH* — **UNCOVERED**
  - What it tests: Output spline from Approx differs from expected [fC0,lC0]
  - Repair action: Reparametrize output to [fC0,lC0]
  - Suggested fixture: defect mentioning 'FirstParameter - fC0', 'LastParameter - lC0'
- **Branch 26** @ line 1633 — *SAME_PARAMETER_CHECK_PASSED* — **UNCOVERED**
  - What it tests: Approx_SameParameter detected SameParameter satisfied
  - Repair action: Accept PCurve as-is, update only if modified
  - Suggested fixture: defect mentioning 'SameP.IsSameParameter()'
- **Branch 27** @ line 1648 — *SAME_PARAMETER_APPROXIMATED* — **UNCOVERED**
  - What it tests: Approx_SameParameter generated approximation with tolreached <= error
  - Repair action: Accept approximated PCurve, replace original
  - Suggested fixture: defect mentioning 'SameP.IsDone()', 'tolreached <= error'
- **Branch 28** @ line 1657 — *APPROXIMATION_ERROR_TOO_HIGH* — **UNCOVERED**
  - What it tests: Approx_SameParameter error exceeds original error
  - Repair action: Keep original PCurve, reject approximation
  - Suggested fixture: defect mentioning 'tolreached > error', 'maxdist = error'
- **Branch 29** @ line 1673 — *APPROX_SAME_PARAMETER_FAILED* — **UNCOVERED**
  - What it tests: Approx_SameParameter algorithm did not converge
  - Repair action: Fallback to GeomLib::SameRange, mark IsSameP=false
  - Suggested fixture: defect mentioning '!SameP.IsDone()', 'GeomLib::SameRange (fallback)'
- **Branch 30** @ line 1704 — *TOLERANCE_ABSORPTION_VIA_PRECISION* — **UNCOVERED**
  - What it tests: error <= (anEdgeTol + max(Prec_C3d, Prec_Surf))
  - Repair action: Accept edge tolerance instead of enforcing SameParameter
  - Suggested fixture: defect mentioning 'CurTol >= error', 'IsSameP = true'
- **Branch 31** @ line 1728 — *TOLERANCE_UPDATE_FROM_MAXDIST* — **UNCOVERED**
  - What it tests: YaPCu=true and IsSameP=true: edge has PCurves and passed checks
  - Repair action: Update edge tolerance to max of all repair tolerances
  - Suggested fixture: defect mentioning 'YaPCu', 'theNewTol = maxdist', 'aNTE->Tolerance'

#### `BRepLib.SameParameter_1st_overload` — lines 1238–1247
(2 branches, 1 covered.)

- **Branch 1** @ line 1241 — *TOLERANCE_PROPAGATION* — COVERED by: a072
  - What it tests: Edge tolerance from SameParameter repair is positive (aNewTol > 0)
  - Repair action: UpdateVTol: propagate new tolerance to both vertices
- **Branch 2** @ line 1241 — *TOLERANCE_NOT_UPDATED* — **UNCOVERED**
  - What it tests: Edge tolerance from SameParameter repair is invalid (aNewTol <= 0)
  - Repair action: Skip vertex tolerance update; edge tolerance unchanged
  - Suggested fixture: defect mentioning 'aNewTol <= 0', 'early return'

#### `BRepLib.SameParameter_2nd_overload` — lines 1255–1740
(20 branches, 0 covered.)

- **Branch 1** @ line 1256 — *EDGE_ALREADY_SAMEPARAMETER* — **UNCOVERED**
  - What it tests: Edge already has SameParameter property set
  - Repair action: Return null edge; skip processing
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter(theEdge)', 'return TopoDS_Edge()'
- **Branch 2** @ line 1265 — *MISSING_3D_CURVE* — **UNCOVERED**
  - What it tests: Edge has no 3D curve representation
  - Repair action: Return null edge; cannot repair without 3D curve
  - Suggested fixture: defect mentioning 'C3d.IsNull()', 'return TopoDS_Edge()'
- **Branch 3** @ line 1273 — *EDGE_COPY_STRATEGY* — **UNCOVERED**
  - What it tests: IsUseOldEdge flag: reuse original or create copy
  - Repair action: ModifyInPlace: use original edge geometry (IsUseOldEdge=true)
  - Suggested fixture: defect mentioning 'IsUseOldEdge', 'aNE = theEdge'
- **Branch 4** @ line 1278 — *EDGE_COPY_STRATEGY* — **UNCOVERED**
  - What it tests: IsUseOldEdge flag: reuse original or create copy
  - Repair action: CreateCopy: make new edge with copied geometry (IsUseOldEdge=false)
  - Suggested fixture: defect mentioning 'EmptyCopied()', 'GetCurve3d(aNE'
- **Branch 5** @ line 1306 — *PERIODIC_CURVE_TRIMMING* — **UNCOVERED**
  - What it tests: 3D curve is TrimmedCurve wrapping periodic basis
  - Repair action: Set m_TrimmedPeriodical flag to avoid incorrect boundary clipping
  - Suggested fixture: defect mentioning 'STANDARD_TYPE(Geom_TrimmedCurve)', 'gtC->IsPeriodic()'
- **Branch 6** @ line 1313 — *CURVE_BOUNDARY_CLAMPING* — **UNCOVERED**
  - What it tests: Non-periodic 3D curve: check parameter ranges
  - Repair action: Clamp edge domain to curve bounds if non-periodic
  - Suggested fixture: defect mentioning '!C3d->IsPeriodic()', 'Udeb > f3d', 'l3d > Ufin'
- **Branch 7** @ line 1360 — *PCURVE_ON_SURFACE* — **UNCOVERED**
  - What it tests: Edge has PCurve representation on surface (YaPCu)
  - Repair action: Activate parametric repair: process PCurve synchronization
  - Suggested fixture: defect mentioning 'GCurve->IsCurveOnSurface()', 'YaPCu = true'
- **Branch 8** @ line 1372 — *CLOSED_SURFACE_SEAM* — **UNCOVERED**
  - What it tests: Surface is closed (seam edge with dual PCurve)
  - Repair action: Load second PCurve for closed surface handling
  - Suggested fixture: defect mentioning 'GCurve->IsCurveOnClosedSurface()', 'PC[1]'
- **Branch 9** @ line 1387 — *SAMERANGE_MISMATCH* — **UNCOVERED**
  - What it tests: Edge lacks SameRange property (3D/2D param mismatch)
  - Repair action: Reparametrize PCurve to match 3D curve range
  - Suggested fixture: defect mentioning '!SameRange', 'GeomLib::SameRange'
- **Branch 10** @ line 1404 — *BSPLINE_C0_DISCONTINUITY* — **UNCOVERED**
  - What it tests: PCurve is B-spline with C0 (parametric) discontinuity
  - Repair action: Upgrade B-spline continuity to C1 via Geom2dConvert
  - Suggested fixture: defect mentioning 'GeomAbs_BSplineCurve && Continuity == C0', 'C0BSplineToC1BSplineCurve'
- **Branch 11** @ line 1419 — *PERIODIC_BSPLINE_ORIGIN_SHIFT* — **UNCOVERED**
  - What it tests: After C0->C1 upgrade, periodic B-spline origin shifted
  - Repair action: Restore origin point by SetOrigin to maintain knot alignment
  - Suggested fixture: defect mentioning 'bs2d->IsPeriodic()', 'SetOrigin'
- **Branch 12** @ line 1444 — *C0_DISCONTINUITY_TOLERANCE_FAILURE* — **UNCOVERED**
  - What it tests: C1 upgrade fails with C0 discontinuity still present
  - Repair action: EvalTol: compute higher tolerance to suppress C0 conversion
  - Suggested fixture: defect mentioning 'bs2d->Continuity() == GeomAbs_C0', 'EvalTol'
- **Branch 13** @ line 1496 — *TOLERANCE_EXCEEDS_ERROR* — **UNCOVERED**
  - What it tests: Computed tolerance exceeds geometric error even after C0 resolution
  - Repair action: Revert to original B-spline, skip reparametrization (repar=false)
  - Suggested fixture: defect mentioning 'bs2d->Continuity() == GeomAbs_C0', 'repar = false'
- **Branch 14** @ line 1539 — *BSPLINE_KNOT_RATIO_ANOMALY* — **UNCOVERED**
  - What it tests: High knot span ratio (>10) detected causing approximation instability
  - Repair action: Trigger curvilinear reparametrization via arc-length approximation
  - Suggested fixture: defect mentioning 'dtratio > critratio', 'IsBad = true', 'Approx_CurvilinearParameter'
- **Branch 15** @ line 1573 — *CURVILINEAR_APPROXIMATION_TRIGGERED* — **UNCOVERED**
  - What it tests: PCurve selected for arc-length reparametrization (IsBad=true)
  - Repair action: Approx_CurvilinearParameter: reparametrize by arc length
  - Suggested fixture: defect mentioning 'IsBad', 'Approx_CurvilinearParameter', 'AppCurPar.IsDone()'
- **Branch 16** @ line 1633 — *SAMEPARAMETER_ALREADY_ACHIEVED* — **UNCOVERED**
  - What it tests: PCurve already has SameParameter property (no fitting needed)
  - Repair action: Accept PCurve, set tolerance from SameP.TolReached()
  - Suggested fixture: defect mentioning 'SameP.IsSameParameter()', 'updatepc = false'
- **Branch 17** @ line 1648 — *SAMEPARAMETER_FITTING_SUCCESS* — **UNCOVERED**
  - What it tests: SameParameter fitting completed with acceptable tolerance
  - Repair action: Replace PCurve with fitted curve if error improves
  - Suggested fixture: defect mentioning 'SameP.IsDone()', 'tolreached <= error', 'Curve2d()'
- **Branch 18** @ line 1673 — *SAMEPARAMETER_FITTING_FAILURE* — **UNCOVERED**
  - What it tests: SameParameter approximation failed; fallback to SameRange
  - Repair action: GeomLib::SameRange: reparametrize without fitting
  - Suggested fixture: defect mentioning '!SameP.IsDone()', 'GeomLib::SameRange', 'IsSameP = false'
- **Branch 19** @ line 1704 — *TOLERANCE_MARGIN_RECOVERY* — **UNCOVERED**
  - What it tests: Edge tolerance absorbs SameParameter error (CurTol >= error)
  - Repair action: Accept IsSameP=true using existing edge tolerance
  - Suggested fixture: defect mentioning '!IsSameP', 'CurTol >= error', 'IsSameP = true'
- **Branch 20** @ line 1721 — *SAMEPARAMETER_PROPERTY_ACHIEVED* — **UNCOVERED**
  - What it tests: All PCurves synchronized (IsSameP=true)
  - Repair action: Set SameParameter flag and record maxdist as new tolerance
  - Suggested fixture: defect mentioning 'IsSameP', 'B.SameParameter(aNE, true)', 'aNTE->Tolerance(maxdist)'

#### `BRepLib.SameRange` — lines 188–266
(11 branches, 1 covered.)

- **Branch 1** @ line 199 — *existing-3d-curve-check* — **UNCOVERED**
  - What it tests: edge already has 3D curve reference from BRep_Tool
  - Repair action: set first_time_in false if 3D curve exists
  - Suggested fixture: defect mentioning 'BRep_Tool::Curve', 'C.IsNull()'
- **Branch 2** @ line 205 — *curve-rep-iteration* — **UNCOVERED**
  - What it tests: iterate all curve representations on edge
  - Repair action: loop through list with iterator
  - Suggested fixture: defect mentioning 'while (an_Iterator.More())', 'an_Iterator.Next()'
- **Branch 3** @ line 207 — *gcurve-downcast-null* — **UNCOVERED**
  - What it tests: curve representation is valid geometric curve
  - Repair action: downcast and skip nulls
  - Suggested fixture: defect mentioning 'down_cast<BRep_GCurve>', 'IsNull()'
- **Branch 4** @ line 213 — *surface-pcurve-existence* — **UNCOVERED**
  - What it tests: 2D curve exists on surface
  - Repair action: extract primary 2D curve (first surface)
  - Suggested fixture: defect mentioning 'IsCurveOnSurface()', 'PCurve()'
- **Branch 5** @ line 218 — *closed-surface-pcurve* — **UNCOVERED**
  - What it tests: edge on closed surface (seam edge) with two 2D curves
  - Repair action: extract secondary 2D curve for closed surface
  - Suggested fixture: defect mentioning 'IsCurveOnClosedSurface()', 'PCurve2()'
- **Branch 6** @ line 223 — *has-curves-guard* — **UNCOVERED**
  - What it tests: at least one 2D curve present
  - Repair action: proceed with reparametrization only if curves exist
  - Suggested fixture: defect mentioning 'has_curve || has_closed_curve'
- **Branch 7** @ line 225 — *baseline-param-capture* — **UNCOVERED**
  - What it tests: first PCurve sets reference parameters
  - Repair action: capture current_first/current_last from first curve
  - Suggested fixture: defect mentioning 'first_time_in', 'current_first', 'current_last'
- **Branch 8** @ line 232 — *param-range-deviation* — COVERED by: gp013, tb001, tb007, tb018, tb019, twi040
  - What it tests: PCurve parameters deviate from baseline beyond tolerance
  - Repair action: reparametrize 2D curves to match baseline range
- **Branch 9** @ line 235 — *repair-primary-pcurve* — **UNCOVERED**
  - What it tests: first surface's 2D curve needs reparametrization
  - Repair action: call GeomLib::SameRange to reparametrize primary curve
  - Suggested fixture: defect mentioning 'GeomLib::SameRange', 'PCurve()'
- **Branch 10** @ line 246 — *repair-secondary-pcurve* — **UNCOVERED**
  - What it tests: seam edge's second 2D curve (closed surface) needs repair
  - Repair action: call GeomLib::SameRange for secondary curve
  - Suggested fixture: defect mentioning 'GeomLib::SameRange', 'PCurve2()'
- **Branch 11** @ line 262 — *update-edge-range-metadata* — **UNCOVERED**
  - What it tests: edge parameters after all reparametrizations
  - Repair action: update edge 3D range and set SameRange flag
  - Suggested fixture: defect mentioning 'B.Range()', 'B.SameRange()'

#### `BRepLib.SortFaces` — lines 2894–2951
(8 branches, 2 covered.)

- **Branch 1** @ line 2906 — *null-surface* — **UNCOVERED**
  - What it tests: Surface is null
  - Repair action: Add to LTri (triangulation-only faces)
  - Suggested fixture: defect mentioning '!S.IsNull()'
- **Branch 2** @ line 2908 — *trimmed-surface-unwrap* — **UNCOVERED**
  - What it tests: Surface is RectangularTrimmedSurface
  - Repair action: Extract basis surface for type classification
  - Suggested fixture: defect mentioning 'STANDARD_TYPE(Geom_RectangularTrimmedSurface)'
- **Branch 3** @ line 2915 — *geometry-type-plane* — **UNCOVERED**
  - What it tests: GeomAdaptor reports type as Plane
  - Repair action: Add to LPlan list
  - Suggested fixture: defect mentioning 'GeomAbs_Plane'
- **Branch 4** @ line 2919 — *geometry-type-cylinder* — COVERED by: gn014, n030
  - What it tests: Type is Cylinder
  - Repair action: Add to LCyl
- **Branch 5** @ line 2923 — *geometry-type-cone* — **UNCOVERED**
  - What it tests: Type is Cone
  - Repair action: Add to LCon
  - Suggested fixture: defect mentioning 'GeomAbs_Cone'
- **Branch 6** @ line 2927 — *geometry-type-sphere* — **UNCOVERED**
  - What it tests: Type is Sphere
  - Repair action: Add to LSphere
  - Suggested fixture: defect mentioning 'GeomAbs_Sphere'
- **Branch 7** @ line 2931 — *geometry-type-torus* — **UNCOVERED**
  - What it tests: Type is Torus
  - Repair action: Add to LTor
  - Suggested fixture: defect mentioning 'GeomAbs_Torus'
- **Branch 8** @ line 2935 — *geometry-type-other* — COVERED by: a005, a006, a037, a038, a068, a076, a103, ad044 (+90 more)
  - What it tests: Type is BSpline, Bezier, or other
  - Repair action: Add to LOther

#### `BRepLib.UpdateDeflection` — lines 2793–2890
(11 branches, 1 covered.)

- **Branch 1** @ line 2800 — *null-surface* — **UNCOVERED**
  - What it tests: Surface is null
  - Repair action: Skip face; no parametric space to evaluate
  - Suggested fixture: defect mentioning 'aSurf.IsNull()'
- **Branch 2** @ line 2807 — *missing-triangulation-or-uvnodes* — **UNCOVERED**
  - What it tests: Triangulation absent or has no UV node data
  - Repair action: Skip face; cannot compute deflection without mesh UV
  - Suggested fixture: defect mentioning 'HasUVNodes'
- **Branch 3** @ line 2820 — *degenerate-edge-node-skip* — **UNCOVERED**
  - What it tests: Edge is marked degenerate
  - Repair action: Collect its nodes in aDegNodes set; later skip triangles using these nodes
  - Suggested fixture: defect mentioning 'BRep_Tool::Degenerated'
- **Branch 4** @ line 2847 — *degenerate-node-in-triangle* — **UNCOVERED**
  - What it tests: Triangle uses node from degenerate edge
  - Repair action: Skip triangle; avoid UV↔3D distortion at degeneracies
  - Suggested fixture: defect mentioning 'aDegNodes.Contains'
- **Branch 5** @ line 2865 — *triangle-midpoint-deflection* — **UNCOVERED**
  - What it tests: Evaluate deflection at triangle centroid
  - Repair action: Compare UV midpoint evaluated at surface vs 3D midpoint; track max squared deviation
  - Suggested fixture: defect mentioning 'aTool.Eval(aMid2d_t', 'aMid3d_t'
- **Branch 6** @ line 2871 — *edge-midpoint-deflection* — **UNCOVERED**
  - What it tests: For each edge in each triangle, if not yet added to aLinks, evaluate midpoint
  - Repair action: Compute deflection at edge midpoint; update max squared deflection
  - Suggested fixture: defect mentioning 'aLinks.Add(aLink)'
- **Branch 7** @ line 2867 — *edge-duplication-tracking* — **UNCOVERED**
  - What it tests: Try to add edge to aLinks set
  - Repair action: If already exists (internal edge), evaluate; if new (boundary), skip (distortion at boundary)
  - Suggested fixture: defect mentioning 'aLinks.Add'
- **Branch 8** @ line 2841 — *triangle-iteration* — **UNCOVERED**
  - What it tests: Loop over all triangles in mesh
  - Repair action: For each non-degenerate triangle, probe centroid and interior edges
  - Suggested fixture: defect mentioning 'aTriIt <= aPT->NbTriangles'
- **Branch 9** @ line 2888 — *deflection-storage* — **UNCOVERED**
  - What it tests: Max deflection computed (possibly 0 if all skipped)
  - Repair action: Write sqrt(aSqDeflection) to triangulation deflection field
  - Suggested fixture: defect mentioning 'aPT->Deflection'
- **Branch 10** @ line 2816 — *face-iteration* — COVERED by: tsh018
  - What it tests: Loop over all faces
  - Repair action: Process each face for deflection update
- **Branch 11** @ line 2883 — *internal-edge-deflection* — **UNCOVERED**
  - What it tests: Edge belongs to 2 triangles (internal)
  - Repair action: Check midpoint deflection; boundary edges skipped
  - Suggested fixture: defect mentioning '// Do not estimate boundary links'

#### `BRepLib.UpdateEdgeTol` — lines 496–687
(26 branches, 5 covered.)

- **Branch 1** @ line 508 — *degenerate-edge-skip* — COVERED by: in014
  - What it tests: edge is degenerate (point-like)
  - Repair action: return false immediately, no tolerance update needed
- **Branch 2** @ line 512 — *edge-tolerance-excessive* — **UNCOVERED**
  - What it tests: edge tolerance already above MaxToleranceToCheck threshold
  - Repair action: return false, no need to update high tolerance
  - Suggested fixture: defect mentioning 'BRep_Tool::Tolerance', 'MaxToleranceToCheck'
- **Branch 3** @ line 528 — *reference-curve-3d-exists* — **UNCOVERED**
  - What it tests: edge has 3D reference curve
  - Repair action: use 3D curve for sampling and tolerance evaluation
  - Suggested fixture: defect mentioning 'BRep_Tool::Curve', 'geom_reference_curve_flag'
- **Branch 4** @ line 532 — *location-transformation* — COVERED by: a017, a067, ad086, gp016
  - What it tests: 3D curve has non-identity location
  - Repair action: transform curve by location before using as reference
- **Branch 5** @ line 538 — *quasi-uniform-sampling-3d* — COVERED by: pf021, tsh012
  - What it tests: initialize sampler for 3D reference curve
  - Repair action: GCPnts_QuasiUniformDeflection for parameter spacing
- **Branch 6** @ line 545 — *no-3d-curve-fallback* — **UNCOVERED**
  - What it tests: no 3D curve found, search for first surface curve
  - Repair action: extract first curve-on-surface as reference
  - Suggested fixture: defect mentioning 'not_done = 1', 'while (not_done && an_iterator.More())'
- **Branch 7** @ line 550 — *surface-curve-extraction* — **UNCOVERED**
  - What it tests: curve representation is valid surface curve
  - Repair action: downcast to BRep_GCurve and extract 2D curve and surface
  - Suggested fixture: defect mentioning 'down_cast<BRep_GCurve>', 'IsCurveOnSurface()'
- **Branch 8** @ line 561 — *surface-location-transform* — COVERED by: a017, a067, ad086, gp016
  - What it tests: surface has non-identity location
  - Repair action: transform surface before using for evaluation
- **Branch 9** @ line 574 — *curve-on-surface-adaptor* — **UNCOVERED**
  - What it tests: create adaptors for curve-on-surface reference
  - Repair action: Geom2dAdaptor_Curve and GeomAdaptor_Surface setup
  - Suggested fixture: defect mentioning 'Geom2dAdaptor_Curve', 'GeomAdaptor_Surface'
- **Branch 10** @ line 581 — *sample-curve-on-surface* — **UNCOVERED**
  - What it tests: initialize sampler for curve-on-surface reference
  - Repair action: GCPnts_QuasiUniformDeflection with surface curve adaptor
  - Suggested fixture: defect mentioning 'a_sampler.Initialize', 'curve_on_surface_reference'
- **Branch 11** @ line 591 — *sample-count-densify* — **UNCOVERED**
  - What it tests: sampler produced fewer than min_sampling_points
  - Repair action: densify parameter array to minimum point count
  - Suggested fixture: defect mentioning 'GeomLib::DensifyArray1OfReal'
- **Branch 12** @ line 595 — *sample-count-reduce* — **UNCOVERED**
  - What it tests: sampler produced more than max_sampling_points
  - Repair action: remove excess points from parameter array
  - Suggested fixture: defect mentioning 'GeomLib::RemovePointsFromArray'
- **Branch 13** @ line 599 — *sample-count-nominal* — **UNCOVERED**
  - What it tests: sample count is within acceptable range
  - Repair action: use sampled parameters as-is for distance evaluation
  - Suggested fixture: defect mentioning 'parameters_ptr = new NCollection_HArray1'
- **Branch 14** @ line 614 — *multi-curve-rep-iteration* — **UNCOVERED**
  - What it tests: iterate curve representations excluding reference curve
  - Repair action: evaluate distance for each non-reference curve
  - Suggested fixture: defect mentioning 'while (second_iterator.More())', 'curve_index != curve_on_surface_index'
- **Branch 15** @ line 621 — *curve-on-surface-flag* — **UNCOVERED**
  - What it tests: curve representation is valid surface curve
  - Repair action: extract 2D curve for distance evaluation
  - Suggested fixture: defect mentioning 'IsCurveOnSurface()', 'PCurve()'
- **Branch 16** @ line 626 — *closed-surface-curve-flag* — **UNCOVERED**
  - What it tests: curve on closed surface (seam edge secondary curve)
  - Repair action: extract secondary 2D curve (seam curve)
  - Suggested fixture: defect mentioning 'IsCurveOnClosedSurface()', 'PCurve2()'
- **Branch 17** @ line 632 — *has-curves-for-eval* — **UNCOVERED**
  - What it tests: at least one 2D curve present for distance check
  - Repair action: proceed with distance evaluation
  - Suggested fixture: defect mentioning 'has_curve || has_closed_curve'
- **Branch 18** @ line 634 — *eval-surface-location-transform* — COVERED by: a017, a067, ad086, gp016
  - What it tests: surface for distance eval has non-identity location
  - Repair action: transform surface before adaptor setup
- **Branch 19** @ line 643 — *eval-adaptor-setup* — **UNCOVERED**
  - What it tests: create adaptors for distance evaluation curve
  - Repair action: Geom2dAdaptor_Curve and GeomAdaptor_Surface for eval
  - Suggested fixture: defect mentioning 'an_adaptor_curve2d', 'an_adaptor_surface'
- **Branch 20** @ line 649 — *eval-curve-on-surface* — **UNCOVERED**
  - What it tests: create curve-on-surface for distance calculation
  - Repair action: Adaptor3d_CurveOnSurface for 3D point evaluation
  - Suggested fixture: defect mentioning 'Adaptor3d_CurveOnSurface', 'a_curve_on_surface'
- **Branch 21** @ line 651 — *same-parameter-distance-method* — **UNCOVERED**
  - What it tests: edge has SameParameter flag set
  - Repair action: use parametric distance evaluation (EvalMaxParametricDistance)
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter', 'EvalMaxParametricDistance'
- **Branch 22** @ line 660 — *reference-3d-distance-method* — **UNCOVERED**
  - What it tests: reference 3D curve exists but SameParameter not set
  - Repair action: use parameter-based distance vs 3D curve (EvalMaxDistanceAlongParameter)
  - Suggested fixture: defect mentioning 'geom_reference_curve_flag', 'EvalMaxDistanceAlongParameter'
- **Branch 23** @ line 670 — *curve-on-surface-ref-distance* — **UNCOVERED**
  - What it tests: no 3D reference, use first surface curve as reference
  - Repair action: evaluate distance against curve-on-surface reference
  - Suggested fixture: defect mentioning 'curve_on_surface_reference', 'EvalMaxDistanceAlongParameter'
- **Branch 24** @ line 677 — *distance-safety-factor* — **UNCOVERED**
  - What it tests: apply safety factor to computed maximum distance
  - Repair action: multiply by 1.4 safety factor
  - Suggested fixture: defect mentioning 'safe_factor', 'max_distance *='
- **Branch 25** @ line 678 — *aggregate-tolerance-max* — **UNCOVERED**
  - What it tests: track maximum distance across all curves
  - Repair action: keep running max of all curve distances
  - Suggested fixture: defect mentioning 'edge_tolerance = std::max'
- **Branch 26** @ line 685 — *tolerance-update-commit* — **UNCOVERED**
  - What it tests: apply computed tolerance to edge metadata
  - Repair action: update edge tolerance in BRep representation
  - Suggested fixture: defect mentioning 'TE->Tolerance(edge_tolerance)'

#### `BRepLib.UpdateEdgeTolerance` — lines 694–715
(4 branches, 1 covered.)

- **Branch 1** @ line 695 — *shape-edge-iteration* — COVERED by: tsh018
  - What it tests: iterate all edges in shape
  - Repair action: TopExp_Explorer to traverse edges
- **Branch 2** @ line 702 — *duplicate-edge-dedup* — **UNCOVERED**
  - What it tests: edge not already processed
  - Repair action: use map to avoid reprocessing shared edges
  - Suggested fixture: defect mentioning 'a_counter.Add', 'NCollection_Map'
- **Branch 3** @ line 704 — *per-edge-tolerance-update* — **UNCOVERED**
  - What it tests: UpdateEdgeTol succeeds for this edge
  - Repair action: call UpdateEdgeTol with tolerance parameters
  - Suggested fixture: defect mentioning 'BRepLib::UpdateEdgeTol'
- **Branch 4** @ line 707 — *first-success-capture* — **UNCOVERED**
  - What it tests: first edge had successful update
  - Repair action: set return_status to true on first success
  - Suggested fixture: defect mentioning 'if (local_flag && !return_status)', 'return_status = true'

#### `BRepLib.UpdateInnerTolerances` — lines 1984–2083
(10 branches, 2 covered.)

- **Branch 1** @ line 1993 — *NON_GEOMETRIC_EDGE_SKIP* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge is topological (no geometric curve data)
  - Repair action: Skip edge; cannot measure geometric error
- **Branch 2** @ line 2015 — *DEGENERATE_EDGE* — COVERED by: ad050, ad101, fi002, gn003, gn037, hea011, le014, le052 (+12 more)
  - What it tests: Edge is degenerate or has no adjacent faces
  - Repair action: Skip measurement; update only vertex tolerances vs 3D curve
- **Branch 3** @ line 2028 — *SAMEPARAMETER_SAMPLING_DENSITY* — **UNCOVERED**
  - What it tests: Edge has SameParameter property
  - Repair action: Dense sampling (23 points) for accurate mismeasurement
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter(anEdge)', 'NbSamples = 23'
- **Branch 4** @ line 2028 — *PARAMETER_MISMATCH_SPARSE_SAMPLING* — **UNCOVERED**
  - What it tests: Edge lacks SameParameter property (3D/2D param mismatch)
  - Repair action: Sparse sampling (2 points: endpoints) to detect drift
  - Suggested fixture: defect mentioning '!BRep_Tool::SameParameter(anEdge)', 'NbSamples = 2'
- **Branch 5** @ line 2038 — *PARAMETER_CORRESPONDENCE* — **UNCOVERED**
  - What it tests: SameParameter: direct param use vs endpoint mapping
  - Repair action: Use same parameter on both curves (synchronized)
  - Suggested fixture: defect mentioning 'BRep_Tool::SameParameter(anEdge)', 'ParamOnCurve = ParamOnCenter'
- **Branch 6** @ line 2040 — *PARAMETER_ENDPOINT_MAPPING* — **UNCOVERED**
  - What it tests: No SameParameter: use endpoint parameters instead
  - Repair action: Map interior to endpoints; only measure endpoint gaps
  - Suggested fixture: defect mentioning '!BRep_Tool::SameParameter(anEdge)', 'FirstParameter()/LastParameter()'
- **Branch 7** @ line 2051 — *VERTEX_TOLERANCE_START* — **UNCOVERED**
  - What it tests: Sample point at edge start (k=0)
  - Repair action: UpdateVertex V1 with distance to surface sample point
  - Suggested fixture: defect mentioning 'k == 0 && !V1.IsNull()', 'UpdateVertex(V1, aDist1)'
- **Branch 8** @ line 2057 — *VERTEX_TOLERANCE_END* — **UNCOVERED**
  - What it tests: Sample point at edge end (k=NbSamples)
  - Repair action: UpdateVertex V2 with distance to surface sample point
  - Suggested fixture: defect mentioning 'k == NbSamples && !V2.IsNull()', 'UpdateVertex(V2, aDist2)'
- **Branch 9** @ line 2068 — *FINAL_VERTEX_TOLERANCE_START* — **UNCOVERED**
  - What it tests: Endpoint gap after edge tolerance update (V1)
  - Repair action: UpdateVertex V1: max(endpoint_dist, edge_tolerance)
  - Suggested fixture: defect mentioning '!V1.IsNull()', 'Value(fpar)', 'UpdateVertex(V1, std::max(dist1, TolEdge))'
- **Branch 10** @ line 2075 — *FINAL_VERTEX_TOLERANCE_END* — **UNCOVERED**
  - What it tests: Endpoint gap after edge tolerance update (V2)
  - Repair action: UpdateVertex V2: max(endpoint_dist, edge_tolerance)
  - Suggested fixture: defect mentioning '!V2.IsNull()', 'Value(lpar)', 'UpdateVertex(V2, std::max(dist2, TolEdge))'

