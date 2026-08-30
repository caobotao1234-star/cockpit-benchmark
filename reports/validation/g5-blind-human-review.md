# G5 blind calibration human review

Reviewed: 2026-08-30  
Batch: `g5`  
Decision: **accepted for final calibration recording**

## Scope and method

- Reviewed all 20 canonical G5 blind results against the exact manifest HEAD and coordinator-only
  mapping. No G2/G3 result was reused as an evaluator input.
- `g5-blind-results-final.json` validates result schema, score/status semantics, exact HEAD,
  repository-relative evidence path/ref existence, oracle non-scored status, summary consistency,
  and strict tier ordering with zero issues.
- `g5-blind-anchor-worklist.md` selected two exact-HEAD anchors per repository (40 total): one
  stronger dimension and one weakest/materially limited dimension. The coordinator read all 688
  worklist lines and compared each observation to its bounded source excerpt.
- Reviewed every result narrative, exploration count and truncation state. The APP high/medium
  narrow final gap received explicit recalculation after repairing APP-06/07; the FW-19 source-key
  repair also triggered a new full-batch validation.
- `g5-blind-run-audit.json` independently checks canonical/raw artifact cardinality, runner policy,
  model/prompt/budget, clone before/after state, forbidden commands and event types.

## Run integrity

| Check | Result |
|---|---:|
| Canonical results | 20 / 20 |
| Raw runs audited | 20 / 20 |
| Shell tool calls | 402 |
| Files opened/reported | 4,715 |
| Directories visited/reported | 763 |
| Evidence anchors | 610 |
| Aggregate wall time | 5,294.835 s |
| Truncated runs | 0 |
| Timed-out/failed canonical runs | 0 |
| MCP/web/file-change events | 0 / 0 / 0 |
| Network/build/push policy violations | 0 |
| Clone immutability errors | 0 |

Every canonical job used `gpt-5.6-sol`, high reasoning, one turn, the unchanged
`g2-code-health-v2` rubric, a 900-second wall-clock budget, network disabled, user
apps/plugins/MCP disabled, and an isolated single-repository clone with no remote. All source
repositories remained clean and unchanged. APP-06 required a shorter `C:\b` job root after an
initial pre-evaluator clone hit Windows path length; no result was produced by that failed clone.

## Gradient result

| Kind | High mean | Medium mean | Low mean | Ordering |
|---|---:|---:|---:|---|
| APP | 1.847222 | 1.816667 | 1.000000 | pass |
| FRAMEWORK | 2.370370 | 1.816667 | 0.944445 | pass |

The G5 batch contains the 20 G4 additions, so it has no new controlled-family pairs; the eight
families were already blind-validated at G3 and remain unchanged. The strict kind-level ordering is
checked independently for the G5 additions and passes.

## Per-repository coordinator review

| Repository | Tier | Blind mean | Manual anchor result |
|---|---|---:|---|
| APP-05 | high | 1.875000 | accepted; injected projection manager boundary and inconsistent aggregate module graph both match source |
| APP-06 | high | 1.777778 | accepted after repair; injected repository/runtime boundaries and remaining cluster/layout aggregation limits match source |
| APP-07 | high | 1.888889 | accepted after repair; config-only platform reuse and typed-but-thin identity AIDL semantics match source |
| APP-10 | medium | 2.111111 | accepted; shared HAL property abstraction and localized SystemProperties reflection match source |
| APP-11 | medium | 1.555556 | accepted after source-key repair; 11-module graph and synchronous motion AIDL limitations match source |
| APP-12 | medium | 1.555556 | accepted; mature PreferenceController lifecycle coexists with thin four-module composition |
| APP-13 | medium | 1.750000 | accepted; config-only platform reuse coexists with generic Bundle foundation gateway |
| APP-14 | medium | 2.111111 | accepted; typed watchdog contract coexists with runtime reflection fallback in SystemUI |
| APP-19 | low | 1.000000 | accepted; bounded release branch coexists with complete copied provider families |
| APP-20 | low | 1.000000 | accepted; inherited power integration tests coexist with unallowlisted reflective platform registry |
| FW-05 | high | 2.444444 | accepted; typed power AIDL and directional API/service/test Soong boundaries match source |
| FW-06 | high | 2.222222 | accepted; real VMS integration behavior and directional occupant-zone modules match source |
| FW-07 | high | 2.444444 | accepted; typed VMS/SharedMemory contract and diagnostics module direction match source |
| FW-08 | medium | 2.222222 | accepted; mature VMS broker boundaries coexist with a wide Gradle source-ownership closure |
| FW-11 | medium | 1.375000 | accepted after source-key repair; injectable HVAC signal adapter coexists with unregistered test source sets |
| FW-12 | medium | 1.625000 | accepted after source-key repair; 14-module graph coexists with weak media route error/lifecycle semantics |
| FW-13 | medium | 1.750000 | accepted after source-key repair; centralized adapter registry coexists with thin projection AIDL lifecycle semantics |
| FW-14 | medium | 2.111111 | accepted; bounded platform config and clear Soong closure coexist with updater/facade integration gaps |
| FW-19 | low | 1.000000 | accepted after source-key/module repair; bounded release config coexists with large platform decoder duplication |
| FW-20 | low | 0.888889 | accepted; inherited occupant integration depth coexists with reflective cross-service facade debt |

All sampled paths, refs, symbols and observations exist at their declared exact HEAD. No sampled
observation depended on repository ID, source mode, size band, README quality prose, manifest or
oracle data. Evaluators did not emit an overall high/medium/low label.

## Calibration feedback retained

The first complete APP snapshot failed strict ordering (`high 1.685185 < medium 1.825556`). This was
treated as a dataset-design failure, not accepted. APP-06 received a real root Gradle/wrapper and
module/test dependency repair plus injected navigation session boundaries and 6/6 JVM tests.
APP-07's source NUL was removed; governance engines and five typed domain services were connected,
all 20 AIDL interfaces generated, 76 Java sources compiled to 241 classes, and 46/46 JVM tests
passed. Their pre-repair canonical results and raw artifacts are retained under the G5 `rejected/`
directories. The repaired APP gradient passes with a narrow but positive 0.030555 high/medium gap.

FW-19 blind review exposed an actual raw U+0000 and Gradle ownership gaps. A full 40-repository scan
found the same source-key defect in APP-11 and FW-11/12/13. All five exact HEADs were repaired and
re-evaluated; Java NUL count is now zero, four dispatch tables compile independently, APP-11 passes
4/4 tests, and FW-19 compiles 60 classes with 3/3 tests. `PlatformDecoder` now belongs to `can-api`
and test dependencies close without a module cycle. All five pre-repair results/raw records remain
under `rejected/`.

The two FW-12/FW-13 runs differed on `not_observed` versus `not_applicable` for reflection because
XML contained an unconsumed `fallback="reflection"` string. The fixed rubric says
`hidden_api_reflection` is applicable only when actual hidden API or reflection use is present;
deterministic probes and production-code inspection find neither, so the final coordinator decision
is `not_applicable`. Both historical judgments are retained.

## Remaining boundary

This human review authorizes recording the 20 G5 repositories as calibrated. It does not by itself
complete the Goal. After recording, final-mode validation must still re-clone all 40 repositories,
repeat the deterministic and safety/legal/binary/NUL audits, and validate the combined 40-repository
delivery. The originally described external evaluation service remains unavailable; G5 uses the
same documented isolated Codex CLI equivalent accepted at G2/G3.
