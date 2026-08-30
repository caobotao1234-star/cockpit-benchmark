# G3 blind calibration human review

Reviewed: 2026-08-29  
Batch: `g3`  
Decision: **accepted for the G3 half-production gate**

## Scope and method

- Reviewed all 20 canonical blind results against the exact manifest HEAD and coordinator mapping.
- `g3-blind-results.json` deterministically validated all 641 evidence anchors for safe repository-relative path, declared local ref, file existence, schema, score/status semantics, oracle non-scored status, HEAD, and summary consistency.
- `g3-blind-anchor-worklist.md` selected two bounded anchors per repository (40 total): one stronger dimension and one weakest/materially limited dimension. The coordinator read the cited source at the exact HEAD/ref and compared symbol/location and observation to the excerpt.
- Reviewed all 20 result narratives, exploration counts, truncation state, and the eight controlled-family comparisons. The minimum-gap Media and Settings pairs received explicit contrast review.
- Audited raw events and run records with `g3-blind-run-audit.json`. Outlier `files_opened` counts for APP-15 and FW-16 were traced to read-only per-file inventories/diffs in their raw commands; they were not inferred or copied from manifest facts.

## Run integrity

| Check | Result |
|---|---:|
| Canonical results | 20 / 20 |
| Raw runs audited | 20 / 20 |
| Shell tool calls | 391 |
| Files opened/reported | 3,354 |
| Directories visited/reported | 696 |
| Evidence anchors | 641 |
| Aggregate wall time | 6,605.434 s |
| Truncated runs | 0 |
| Timed-out/failed runs | 0 |
| MCP/web/file-change events | 0 / 0 / 0 |
| Network/build/push policy violations | 0 |
| Clone immutability errors | 0 |

Every job used `gpt-5.6-sol`, high reasoning, one turn, the unchanged
`g2-code-health-v2` rubric, a 900-second budget, network disabled, user apps/plugins/MCP disabled,
and an isolated single-repository clone with no remote. All source repositories remained clean and
unchanged.

## Gradient result

| Kind | High mean | Medium mean | Low mean | Ordering |
|---|---:|---:|---:|---|
| APP | 1.888889 | 1.666667 | 1.083333 | pass |
| FRAMEWORK | 2.166667 | 2.000000 | 1.118056 | pass |

All eight controlled families pass strict `high > low` ordering:

| Family | High | Low | Gap |
|---|---:|---:|---:|
| app-launcher-medium | 2.000000 | 1.222222 | 0.777778 |
| app-media-small | 1.666667 | 1.111111 | 0.555556 |
| app-settings-large | 1.777778 | 1.222222 | 0.555556 |
| fw-audio-binder-small | 2.111111 | 1.250000 | 0.861111 |
| fw-car-api-compat-large | 2.333333 | 1.111111 | 1.222222 |
| fw-vehicle-hal-medium | 2.111111 | 1.222222 | 0.888889 |
| hvac-controlled-pair | 2.111111 | 0.777778 | 1.333333 |
| vehicle-property-controlled-pair | 2.111111 | 0.888889 | 1.222222 |

## Per-repository coordinator review

| Repository | Tier | Blind mean | Manual anchor result |
|---|---|---:|---|
| APP-01 | high | 1.777778 | accepted; four Gradle boundaries and local-Binder test limitation match source |
| APP-02 | high | 2.000000 | accepted; config-only platform reuse and copied ProtoDataSource TODO match source |
| APP-03 | high | 2.111111 | accepted; delegated signal catalog and local Stub-only instrumentation limitation match source |
| APP-04 | high | 1.666667 | accepted; three modules and concrete-object composition limitation match source |
| APP-08 | medium | 2.000000 | accepted; seven Gradle modules, typed HAL factory, and uneven voice lifecycle coverage match source |
| APP-09 | medium | 1.333333 | accepted; Dagger shell composition, coarse cluster lifecycle, reflection, and test gaps match source |
| APP-15 | low | 1.222222 | accepted; mature local controller coexists with duplicated legacy/modern generations |
| APP-16 | low | 1.222222 | accepted; typed Binder exists but 8155/8295 product trees are duplicated |
| APP-17 | low | 0.777778 | accepted; bounded release config coexists with coarse unversioned climate AIDL |
| APP-18 | low | 1.111111 | accepted; typed media AIDL coexists with identical cross-platform policy stacks |
| FW-01 | high | 2.333333 | accepted; typed watchdog AIDL and directional Soong boundaries match source |
| FW-02 | high | 2.111111 | accepted; config-only platform branch and real property callback tests match source |
| FW-03 | high | 2.111111 | accepted; common VehicleStub reuse and bounded-but-unallowlisted parcelable reflection match source |
| FW-04 | high | 2.111111 | accepted; shared audio HAL abstraction and directional modules match source |
| FW-09 | medium | 2.000000 | accepted; modern HAL abstraction dominates, while untested vendor normalization remains a local gap |
| FW-10 | medium | 2.000000 | accepted after repair; generic Bundle gateway, listener permission asymmetry, reflection fallback, and missing gateway tests were independently observed |
| FW-15 | low | 0.888889 | accepted; release config is bounded but the only local unit test is `assertTrue(true)` |
| FW-16 | low | 1.111111 | accepted; strong inherited tests coexist with a complete legacy car-lib duplicate and compat debt |
| FW-17 | low | 1.250000 | accepted; common HAL interface remains, but complete platform audio copies and hub debt dominate |
| FW-18 | low | 1.222222 | accepted; inherited power test depth coexists with coarse legacy/migration aggregate modules |

No sampled observation depended on repository ID, source mode, size band, README quality prose, or
oracle data. The evaluator did not assign an overall high/medium/low label.

## Calibration feedback retained

The first valid FW-10 run scored 2.333333 and made FRAMEWORK high and medium means equal. This was
treated as a benchmark-design failure rather than accepted. FW-10 was evolved with a real
ICarImpl-connected Manager gateway, coarse `String + Bundle` AIDL, permission-aware invocation,
callback lifecycle, and bounded vendor reflection fallback; the new AIDL/Java compiled to 21 class
files against Android 35 plus narrow platform stubs. The pre-repair canonical result and four raw
artifacts are preserved under `calibration/results/g3/rejected/` and
`calibration/raw/g3/rejected/`. Only the new HEAD/result is canonical.

## Remaining boundary

This acceptance closes blind calibration for the 20-repository G3 half-set only. It does not claim
full AAOS product builds, device execution, G4 completion, the final 40-repository distribution, or
G5 delivery audit. The external evaluation service remains unavailable; this batch uses the same
documented isolated Codex CLI equivalent as G2.
