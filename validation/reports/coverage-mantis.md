# OCCT Mantis / GitHub Coverage vs STEP Problem Catalog

Gap report: which OCCT-tracked defects (Mantis bug IDs and GitHub PR/issue numbers) appear in the STEP-related code paths and which are missing from `STEP_PROBLEM_CATALOG.md`. Companion JSON: `/tmp/cad-coverage-mantis.json` (canonical form with full uncited list per category).

## Methodology

- Mined `git log --all` of `/tmp/cad-occt` for commits whose subject matches the STEP/Shape-Healing module surface (STEP, ShHealing, XSControl, Shape{Fix,Upgrade,Analysis,Construct}, UnifySameDomain, etc.). Yielded 458 commits.
- Extracted Mantis IDs (`0NNNNNN`, range 002NNNN-003NNNN) and GitHub PR/issue numbers (`#NNN`) from subjects; augmented with `tests/.../bug{NNNN}` and `tests/.../OCC{NNNN}` filenames whose path matches `step|heal|xde|shape` (438 unique test-derived IDs).
- Per-ID description: commit subject (paraphrased), or for test-only IDs the first comment block of the `.tcl` script.
- Cross-reference: each ID string searched in `STEP_PROBLEM_CATALOG.md` and `STEP_PROBLEM_CATALOG.json`. Mantis IDs accepted in any of `0NNNNNN`, `NNNNN`, `OCCNNNN`, `bugNNNN` form. Bare `#NNN` does *not* count for GitHub matching (the catalog uses `#NNN` for STEP entity references) — only PR-context patterns (`PR #NNN`, `pull/NNN`, `#NNN` near OCCT/github/opencascade) count.

## Totals

| Bucket | Count |
|--------|------:|
| Total IDs enumerated | **614** |
| Mantis bug IDs | 559 |
| GitHub PR/issue numbers | 55 |
| Cited in catalog | **106** (17%) |
| - Mantis cited | 105 / 559 (18%) |
| - GitHub cited (PR-context only) | 1 / 55 |
| **Not cited** | **508** (82%) |

## Per-defect-class breakdown of uncited IDs

Primary class assigned by keyword classifier; secondary classes (e.g. `regression`, `refactor`) suppressed in favor of the most descriptive defect family. Each row shows the bucket size + up to 6 representative IDs.

| Defect class | Uncited | Sample IDs (newest first) |
|--------------|--------:|---------------------------|
| other/uncategorized | 157 | `0033737`, `0033657`, `0033487`, `0033183`, `0033101`, `0033080`, … (+151) |
| crash/robustness | 54 | `0033631`, `0033421`, `0033398`, `0033377`, `0033312`, `0033179`, … (+48) |
| UnifySameDomain | 31 | `0033028`, `0032332`, `0032328`, `0032213`, `0032140`, `0031441`, … (+25) |
| face/sewing | 30 | `0033171`, `0032666`, `0032619`, `0032561`, `0031736`, `0030831`, … (+24) |
| writer/export | 28 | `0033703`, `0032817`, `0032556`, `0032350`, `0032264`, `0030189`, … (+22) |
| assembly/metadata | 26 | `0033641`, `0033530`, `0033331`, `0033165`, `0033053`, `0030779`, … (+20) |
| shape healing (general) | 24 | `0033806`, `0033791`, `0033788`, `0033751`, `0033022`, `0033018`, … (+18) |
| refactor/maintenance | 17 | `0033039`, `0032696`, `0032667`, `0022848`, `0022642`, `#888`, … (+11) |
| reader (general) | 12 | `0033616`, `0029978`, `0029394`, `0028345`, `0027170`, `0026715`, … (+6) |
| tessellation | 12 | `0033596`, `0033498`, `0033484`, `0033410`, `0033100`, `0032719`, … (+6) |
| performance | 12 | `0033350`, `0030593`, `0029502`, `0028467`, `0027570`, `0027085`, … (+6) |
| regression | 11 | `0032596`, `0031855`, `0031491`, `0031466`, `0030378`, `0029888`, … (+5) |
| wire/edge | 10 | `0030927`, `0028414`, `0026282`, `0025923`, `0025843`, `0023451`, … (+4) |
| appearance/colour | 10 | `0030856`, `0028641`, `0026657`, `0025910`, `0022982`, `0022962`, … (+4) |
| PMI/GD&T | 9 | `0033095`, `0032731`, `0032681`, `0029854`, `0029525`, `0027313`, … (+3) |
| units/transform | 8 | `0033564`, `0032452`, `0031382`, `0026951`, `0023597`, `0023009`, … (+2) |
| tolerance/precision | 8 | `0029338`, `0027729`, `0026554`, `0024922`, `0023722`, `0023552`, … (+2) |
| pcurve | 8 | `0028595`, `0026198`, `0025634`, `0022873`, `#967`, `#894`, … (+2) |
| parser/syntax | 7 | `0033665`, `0033603`, `0032314`, `0031970`, `0031481`, `0030876`, … (+1) |
| memory/loops | 6 | `0033529`, `0031075`, `0031066`, `0026671`, `0022941`, `0022807` |
| shell/orientation | 6 | `0032174`, `0030221`, `0028449`, `0023193`, `#699`, `#324` |
| analytic surface | 5 | `0029945`, `0029369`, `0023771`, `0022535`, `0022492` |
| encoding/strings | 4 | `0033602`, `0031851`, `0030694`, `0028454` |
| empty/missing geometry | 4 | `0033261`, `0031191`, `0029241`, `0022680` |
| thread safety | 3 | `0033351`, `0029269`, `#307` |
| header/schema | 2 | `0033611`, `0031000` |
| supplemental/FEA | 2 | `#768`, `#744` |
| kinematics | 1 | `0031388` |
| nurbs/bspline | 1 | `0006542` |

## Highest-priority uncited defects (top 50)

Mantis IDs only (GitHub PRs lean toward refactor / build hygiene). Sorted newest first — these are the most recent unsolved or only-recently-solved STEP/healing defects not yet captured in the catalog.

| Mantis ID | Class | Paraphrased one-liner | OCCT source |
|-----------|-------|----------------------|-------------|
| `0033806` | shape healing (general) | Shape Healing - ShapeCustom optimization while rebuilding compounds | `d0e33902bc` |
| `0033791` | shape healing (general) | Shape Healing - ShapeCustom not take location of source shape for the cached context an... | `2736652117` |
| `0033788` | shape healing (general) | Data Exchange, DE Wrapper - Shape Healing configuration node | `677f383561` |
| `0033751` | shape healing (general) | Shape Healing - Use static values in case of an absent Resource file | `f39f9838e4` |
| `0033737` | other/uncategorized | Data Exchange, XCAF - Implementing filter tree functionality | `818c68f22e` |
| `0033703` | writer/export | Data Exchange, Step Export - Transfer edge speed improvement | `ed20837d8b` |
| `0033665` | parser/syntax | Data Exchange, Step Import - TransferRoots crashes for invalid STEP files | `e5998666ee` |
| `0033657` | other/uncategorized | [test] tests/.../bug33657 | `tests/bugs/step/bug33657_2` |
| `0033641` | assembly/metadata | Data Exchange, Step Import - Changing default value for metadata flag | `32f7b4e5bf` |
| `0033631` | crash/robustness | Data Exchange, Step import - Crash by reading STEP file | `d5bcd33386` |
| `0033616` | reader (general) | Application Framework - Using filter while reading XBF may result in unresolved links | `d3e00bfaa6` |
| `0033611` | header/schema | Data Exchange - Incorrect header guard for STEP property | `993da38d54` |
| `0033603` | parser/syntax | Data Exchange, Step Import - Crash reading corrupted STEP file | `3888b58c27` |
| `0033602` | encoding/strings | Data Exchange, Step - Carriage return removing | `d1eae5b0d0` |
| `0033596` | tessellation | Documentation - Incorrect default value read.step.tessellated | `a9becad233` |
| `0033564` | units/transform | Data Exchange, STEP - Making default unit parameter | `cdc6566c3c` |
| `0033530` | assembly/metadata | Data Exchange, Step Import - Implement GENERAL_PROPERTY support | `f286953d85` |
| `0033529` | memory/loops | Data Exchange, Step - Move on IncAllocator functionality | `ed85665b55` |
| `0033498` | tessellation | Data Exchange, Step Export - Meshed pretessellated geometry is skipped on write | `ff15a5d1ab` |
| `0033487` | other/uncategorized | Data Exchange, Step Import - Unresolved reference crashes | `539ddf30fb` |
| `0033484` | tessellation | Data Exchange, Step Import - Pretessellated geometry is translated incompletely | `2b5ee7c791` |
| `0033421` | crash/robustness | Modeling Algorithms - ShapeUpgrade_UnifySameDomain throws exception | `eb2be8bb46` |
| `0033410` | tessellation | Data Exchange, Step Import - TRIANGULATED_FACE from STEP where there are no pnval entries | `983e35ed71` |
| `0033398` | crash/robustness | Modeling Algorithms - ShapeUpgrade_UnifySameDomain throws exception on specific STEP model | `96d1fe2b05` |
| `0033377` | crash/robustness | Data Exchange - STEPCAFControl_Reader crash in OCC 7.7.0 | `e4f00dbb7e` |
| `0033351` | thread safety | Data Exchange, Step - Improvement for thread safety of the STEP translator | `28b505b27b` |
| `0033350` | performance | Data Exchange, Step Import - Improving parsing performance | `5d8b1a4076` |
| `0033331` | assembly/metadata | Data Exchange, Step Import - Unsupported Representation Items | `efe960751c` |
| `0033312` | crash/robustness | Data Exchange - NULL-dereference in StepToTopoDS_TranslateShell::Init() | `fc72568ba9` |
| `0033261` | empty/missing geometry | Data Exchange, Step Import - Empty shape after reading process | `20955d88da` |
| `0033183` | other/uncategorized | Data Exchange - Lose texture after saving XBF file | `a948803521` |
| `0033179` | crash/robustness | Modeling Algorithms - Crash in ShapeFix_Shape with the attached object, when healing fo... | `c325231de6` |
| `0033171` | face/sewing | Modeling Algorithms - Invalid result of faces unification | `d444cc35c6` |
| `0033165` | assembly/metadata | Data exchange - Instance name is not saved during writing step file | `3c9178dd5c` |
| `0033101` | other/uncategorized | Data Exchange - STEP reader makes unexpected enormous scaling of some parts | `53152e6dd9` |
| `0033100` | tessellation | Modeling Algorithms - XCAFDoc_Editor::RescaleGeometry does not rescale triangulations | `fd5c113a03` |
| `0033095` | PMI/GD&T | Data Exchange, Step Import - Wrong PMI values when loading a *.stp file in m | `621ed3bc36` |
| `0033080` | other/uncategorized | Wrong projection point from ShapeAnalysis_Surface | `92d22d7d62` |
| `0033053` | assembly/metadata | Data Exchange, Step Export - Compound with vertex is ignored | `acac44d571` |
| `0033039` | refactor/maintenance | Coding - get rid of unused headers [StepData to StlAPI] | `b2bce1d928` |
| `0033028` | UnifySameDomain | Standard_ConstructionError while using ShapeUpgrade_UnifySameDomain | `581016faeb` |
| `0033022` | shape healing (general) | Coding - get rid of unused headers [ShapeBuild to STEPControl] | `b1970c8a47` |
| `0033018` | shape healing (general) | Coding - get rid of unused headers [Plugin to ShapeAnalysis] | `a1f027b66e` |
| `0033011` | other/uncategorized | Data Exchange - Backward compatibility XBF format | `4f53e7b37c` |
| `0033006` | crash/robustness | Modelling Algorithms - UnifySameDomain raises exception | `e1b097eb67` |
| `0032999` | other/uncategorized | Modeling Algorithms - New option in ShapeUpgrade_ShapeDivide algorithm: splitting into... | `07e803dee1` |
| `0032980` | crash/robustness | Data Exchange - STEP import produce a crash | `dec56592dd` |
| `0032826` | other/uncategorized | Data Exchange - use OSD_FileSystem within RWStl::ReadAscii() and StepFile_Read() | `2922a73ea7` |
| `0032817` | writer/export | Data Exchange - Step export - writing untrimmed Curve | `452ba192d5` |
| `0032814` | other/uncategorized | Modeling algorithms - Unifysamedom produces invalid result | `600ee85631` |

_Remaining 404 uncited Mantis IDs and all 54 uncited GitHub PRs are in `/tmp/cad-coverage-mantis.json` under `uncited_by_category`._

## All uncited GitHub PRs (compact list)

Most are post-2022 cleanups / refactors of the STEP toolkits and would not normally need a catalog entry, but listed here for triage:

- `#1067` Data Exchange, STEP - Refactor pnindex handling in CreatePolyTriang...
- `#981` Shape Healing - GlueEdgesWithPCurves is not valid
- `#967` Shape Healing - Unstable PCurve Processing
- `#941` Shape Healing - Remove edges from map during face unification in Sh...
- `#894` Shape Healing - Revert BSpline check for ShapeConstruct_ProjectCurv...
- `#890` Shape Healing - Optimize PCurve projection
- `#888` Coding - Refactor RWStepAP214 module to use custom hasher for strin...
- `#876` Modelling - ShapeUpgrade_UnifySameDomain crash
- `#786` Data Exchange, STEP - Refactor StepType selection
- `#784` Data Exchange, STEP - use std::string_view for STEP type names and API
- `#779` Data Exchange, Step Import - Add import of coordinate system connec...
- `#769` Shape Healing - Regression after
- `#768` Revert "Data Exchange - Step supplemental geometry support (#744)"
- `#756` Data Exchange, STEP - Replace String typedef and global temp buffer...
- `#753` Shape Healing - Regression after
- `#745` Mesh - Import of STEP file crashes at the very end when visualizing...
- `#744` Revert "Data Exchange - Step supplemental geometry support (#744)"
- `#733` Data Exchange - Hang in STEPCAFControl_Reader
- `#720` Testing - Add ShapeAnalysis_CanonicalRecognition unit tests
- `#699` Shape Healing, STP Import - Revolved shape in STEP file is imported...
- `#672` Coding, StepData - Translation to English
- `#634` Data Exchange, STEP Export - General Attributes
- `#624` Modeling - Fix null surface crash in UnifySameDomain
- `#601` Data Exchange, Step Export - Preserving control directives
- `#600` Modeling, ShapeAnalysis_Curve - Mismatch between projected point an...
- `#584` Shape Healing - Regression after
- `#577` Data Exchange, Step Export - Ignoring unit factors during tessellat...
- `#565` Shape Healing - Reusing Surface Analysis for Wire fixing
- `#545` Coding - Add conversion utilities for STEP geometrical and visual e...
- `#543` Coding - Small optimization of StepData_StepReaderData
- `#513` Data Exchange, Step Export - Apply a scaling transformation
- `#498` Coding - MSVC warning fix for STEP Rendering properties
- `#479` Data Exchange - Step Direction optimization
- `#475` Data Exchange, Step Export - Decreasing file size
- `#448` Data Exchange, Step - AP242 SchemaName Remove dot
- `#447` Data Exchange, Step - Vis Material support
- `#372` Modeling - SIGSEGV BRepAdaptor_Curve2d and UnifySameDomain
- `#371` Modeling Algorithms - UnifySameDomain improvement
- `#358` Data Exchange, Step Import - Disable Product Metadata mode by default
- `#357` Data Exchange - Step Import metadata crash protecting
- `#355` Data Exchange - STEP Export ignore write schema
- `#346` Coding - Refactor ShapeHealingMap to NCollection
- `#324` Data Exchange - StepExport non-manifold missed parameter
- `#315` Data Exchange, Step Import - Adding product attributes to metadata
- `#307` Data Exchange - Step thread safety improvement
- `#284` Data Exchange - Losing attributes on NonManifold STEP
- `#283` Data Exchange - Clear up Step from Static_Interface
- `#282` Data Exchange - DE Wrapper Shape Healing Parameters
- `#268` Testing - Retesting step for GH Actions
- `#261` Coding - Move StepData_ConfParameters to DESTEP package
- `#247` Data Exchange - Update Readers with ShapeHealing parameters
- `#223` Coding - Disable exporting internal RWStep* includes
- `#189` Shape Healing interface update
- `#179` Coding - Missing include in TopoDSToStep_Builder.hxx

## Cited IDs (already represented)

106 IDs were found in the catalog text. Sample (newest first):

| ID | Cite form | Paraphrase |
|----|-----------|------------|
| `0033815` | `33815` | [test] tests/.../bug33815 |
| `0033661` | `0033661` | Data Exchange, Step Import - Tessellated GDTs are not imported |
| `0033638` | `0033638` | Data Exchange, Step Import - Style for tessellated object missed |
| `0033569` | `0033569` | Data Exchange, STEP - Crash when reading multi-body file |
| `0033491` | `0033491` | Data Exchange, Step Import - Incorrect import of ComplexTriangulatedFace |
| `0033317` | `bug33317` | Data Exchange, Step Export - Ignoring color attached to the reference shape l... |
| `0033307` | `bug33307` | Data Exchange, Step Import - Crash after reading empty edge loop |
| `0033193` | `0033193` | Modeling Algorithms - Regression: UnifySameDomain raises SIGSEGV |
| `0032977` | `0032977` | OCC V7.5, V7.6 cannot read STEP color correctly for the root label, but v6.8 can |
| `0032922` | `0032922` | Data Exchange, STEP - The torus is stored incorrectly in STEP format |
| `0032914` | `0032914` | Data Exchange - Some parts of compound are lost while writing STEP in nonmani... |
| `0032748` | `0032748` | Data Exchange, Step Import - xstep.cascade.unit doesn't work [regression sinc... |
| `0032715` | `0032715` | Modelling Algorithms - UnifySameDomain does incomplete union |
| `0032679` | `0032679` | Data Exchange - STEP writer loses assembly instance name |
| `0032623` | `0032623` | [Regression] Modelling Algorithms - UnifySameDomain invalid result only in re... |
| `0032581` | `0032581` | Modelling Algorithms - UnifySameDomain produces invalid result |
| `0032310` | `32310` | Data Exchange - Invalid STEP export/import of backslashes in names [Regressio... |
| `0032049` | `0032049` | Data Exchange - STEP file import problems |
| `0031926` | `0031926` | Shape Healing - ShapeAnalysis::OuterWire() considers next iteration element a... |
| `0031825` | `0031825` | Data Exchange, STEP - NULL dereference while re-exporting model with empty Da... |
| `0031711` | `0031711` | Data Exchange - STEPCAFControl_Reader hangs on attached file in an infinite loop |
| `0031685` | `0031685` | Data Exchange, STEPCAFControl_Reader - NULL dereference on translating PLACED... |
| `0031617` | `31617` | Export STEP in nonmanifold mode corrupts the shape |
| `0031568` | `0031568` | Data Exchange - invalid model produced after STEP import |
| `0031550` | `0031550` | Data Exchange, STEP Import - surface transparency is ignored (SURFACE_STYLE_T... |
| `0031485` | `0031485` | Data Exchange - Export STEP in nonmanifold mode looses all faces except one |
| `0031472` | `0031472` | Exception raised during translation of the STEP entity Constructive Geometry... |
| `0031435` | `0031435` | Data Exchange - Problem importing STEP files |
| `0031301` | `0031301` | Data Exchange - Export to STEP corrupts the shape |
| `0031292` | `0031292` | Data Exchange - SIGSEGV on reading STEP file with references to invalid entities |
| … | | _(+76 more in JSON)_ |

## Caveats

- The OCCT clone has a sparse history (~7K commits, only 94 touching the current `TKShHealing` / `TKDESTEP` paths after the modular reorg). Older Mantis fixes were captured by full-log subject mining, not path-restricted log.
- GitHub `#NNN` cross-reference deliberately undercounts: bare `#NNN` collides with STEP entity references in the catalog. Only PR-context occurrences count as hits. The 54 uncited GitHub PRs are mostly post-2022 module cleanups that would not warrant a catalog entry on their own.
- The catalog cross-reference is exact-string only. If the catalog paraphrases a defect without quoting the Mantis ID, this report flags it NOT_CITED even when the substance is present. Use the description column to triage before adding entries.
- Test-only IDs (no associated commit) likely correspond to bugs fixed before the current git history was cut — they are still valuable defect signals because the test fixture preserves the reproducer description.
- Defect-class assignment is single-primary (most-descriptive of the multi-label set). The full multi-label classification is in the JSON.

_Source: `/tmp/cad-occt` git log + tests scan vs `/Users/zellyn/gh/cad/research/STEP_PROBLEM_CATALOG.{md,json}`. Canonical machine form: `/tmp/cad-coverage-mantis.json`._
