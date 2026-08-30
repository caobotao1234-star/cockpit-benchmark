# G2 Pilot Acceptance

Date: 2026-08-29  
Status: **PASSED; G3 MAY START**

## Deterministic result

`g2-production-size-final.json` reports `valid: true`, four repositories probed, fresh local clone
smoke enabled, and zero issues. The validator checked manifest/schema agreement, Git head and branch
facts, source/module/features statistics, clean worktrees, zero configured remotes, parent oracle
schema/evidence/commit validity, production-size classification, controlled-family size parity, and
ground-truth leakage.

| ID | Kind | Tier | Size band | Source files | Source LOC | Modules | Commits | Branch-reuse signal |
|---|---|---|---|---:|---:|---:|---:|---|
| APP-03 | APP | high | small | 222 | 10,774 | 7 Gradle | 303 including retained upstream history | about 0.992 platform / 0.996 release |
| APP-17 | APP | low | small | 166 | 11,981 | 2 Gradle | 19 | about 0.31 |
| FW-02 | FRAMEWORK | high | small | 270 | 51,726 | 5 Soong | 19 | about 0.996 |
| FW-15 | FRAMEWORK | low | small | 342 | 41,407 | 5 Soong | 19 | about 0.44 platform / 0.67 release |

The APP pair controls for HVAC business semantics. The FRAMEWORK pair controls for car API,
vehicle-property/Binder, platform mapping, and AAOS system-service semantics. All four expose AIDL,
Binder, reflection, hidden API, and integration-test detection signals, so absence of a feature does
not explain the intended quality ordering. The final APP pair's max/min ratios are 1.337 for source
files and 1.112 for source LOC; the FRAMEWORK pair's are 1.267 and 1.249. All are below the 1.35
confounding limit and both members of each family are in the same size band.

The post-assembly structural audit also checks non-scoring signals. APP-03 has 33 test source files,
no placeholder-test signal, no near-duplicate pair at the 0.80 threshold, and a 0.297
test-to-production file ratio; APP-17 has one placeholder test, 1,726 near-duplicate pairs, and a
0.007 test ratio. FW-02 has 68 test files, one near-duplicate pair, and a largest AIDL contract of
14 methods; FW-15 has two test files, 3,397 near-duplicate pairs, 56 production files over 500
logical lines, and a 54-method aggregate AIDL interface.

APP-03 additionally passed compilation and 37 unit tests across the independently buildable
`domain`, `vehicle-api`, `comfort`, `diagnostics`, and `telemetry` modules. Full APP assembly stops
at the retained upstream `hvac-core` because the ordinary SDK does not include
`android.car`/`CarHvacManager`; the manifest therefore remains honestly `aosp_required`.

## Blind calibration result

The first APP-03 judgment exposed mechanically repeated feature shells and a disconnected runtime.
That result was rejected and archived. APP-03 was rebuilt from the reviewed baseline with
data-driven comfort/diagnostics/telemetry, typed Binder lifecycle handling, focused tests, and
meaningful local commits before the accepted batch was generated.

The accepted batch used four independent repository-only Codex CLI jobs with fixed
`gpt-5.6-sol`, high reasoning, one turn, a 900-second budget, prompt `g2-code-health-v2`, network
disabled, and no user apps/plugins/MCP. `g2-blind-results.json` reports 4/4 results, zero issues,
and both controlled-family orderings passed:

| Family | High | Low | High mean | Low mean | Gap |
|---|---|---|---:|---:|---:|
| HVAC | APP-03 | APP-17 | 2.111111 | 0.444444 | 1.666667 |
| Vehicle property/runtime | FW-02 | FW-15 | 2.222222 | 0.666667 | 1.555555 |

The four runs opened 534 files across 88 directories, used 65 shell calls, and none was truncated.
Every dimension had repository evidence. Human review checked representative positive and negative
anchors against exact HEAD/branch content and found no fabricated, escaped, or label-derived
evidence. The high-tier reports retained real limitations instead of treating those repositories as
perfect. All four oracle records are now `blind_validated`; all four manifest entries are
`calibrated`.

## Evidence boundary

- Evaluator-safe inputs: `calibration/blind/g2-inputs.json`.
- Coordinator-only key: `calibration/coord/g2-key.json`.
- Ground truth: `oracle/APP-03.json`, `oracle/APP-17.json`, `oracle/FW-02.json`, `oracle/FW-15.json`.
- Branch measurements: `APP-03-branch-reuse.json`, `APP-17-branch-reuse.json`,
  `FW-02-branch-reuse.json`, and `FW-15-branch-reuse.json`.
- Production-size/fresh-clone validation: `g2-production-size-final.json`.
- Canonical blind validation: `g2-blind-results.json`.
- Human source review: `g2-blind-human-review.md`.
- Canonical outputs: `calibration/results/g2/<blind-id>.json`; raw events and runner metadata:
  `calibration/raw/g2/`.

The evaluator received only one child repository per job. The delivery parent and every
coordinator-only file listed above remained outside its filesystem/context.

## Honest limitations

- Full Gradle/Soong product builds were not claimed: all four require AAOS/AOSP platform APIs and
  remain classified `aosp_required`. The APP-03 five-module unit-test result is narrower than a full
  APK/product build.
- The originally described evaluation service remained unavailable. The accepted evidence comes
  from an equivalent independent Codex CLI evaluator with the same repository-only isolation,
  fixed settings, canonical output, raw logs, and post-run immutability checks; it is not described
  as a service run.
- APP-03 retains a large upstream HVAC compatibility controller and local-process Binder contract
  tests. FW-02 retains platform build/test wiring limitations. These are oracle/report limitations,
  not hidden exceptions.
- G2 acceptance opens G3 only. The overall Goal remains incomplete until 20 APP + 20 FRAMEWORK,
  final quotas, 40 clone checks, full blind calibration, and final audit all pass.
