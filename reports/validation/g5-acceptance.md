# G5 Acceptance — Final Cockpit Code-Health Benchmark

Accepted: 2026-08-30  
Delivery root: `D:\Project\Git.temp\cockpit-benchmark`  
Decision: **Goal completion criteria satisfied**

## Final inventory

The delivery contains exactly 40 independent, remote-free Git repositories: 20 APP and
20 FRAMEWORK.

| Dimension | APP | FRAMEWORK |
|---|---:|---:|
| High / medium / low | 7 / 7 / 6 | 7 / 7 / 6 |
| Gradle / Soong | 16 / 4 | 4 / 16 |
| Small / medium / large | 6 / 9 / 5 | 5 / 9 / 6 |

- Public upstream lineage: 31/40; explicitly synthetic: 9/40.
- Controlled families: four APP and four FRAMEWORK; all remain same-domain/build/size and within
  both 1.35 file/LOC ratio limits.
- `manifest.json` is the machine-readable source of truth; `manifest.md` reports 40/40
  deterministically verified and 40/40 blind calibrated.
- All 40 oracle files have `review_status=blind_validated`; all manifest and frozen-matrix rows are
  `calibrated`.

## Final deterministic validation

- `g5-final-40-no-clone.json`: final mode, 40 repositories/probes, zero issues, valid.
- `g5-final-40-clone.json`: final mode, all 40 freshly cloned with `git clone --no-hardlinks`,
  reprobed at exact HEAD, `clone_smoke=true`, zero issues, valid.
- `g5-final-matrix.json`: exact final quotas, 31 public lineages, nine synthetic, four families per
  kind, 40 calibrated, zero issues.
- Candidate catalog: 58 records, 40/40 slots, zero errors.
- Control tests: 23/23 pass, including the G4→G5 calibrated-status lifecycle regression.

## Blind calibration

The 20 G4 additions were independently evaluated in batch `g5` with repository-only isolated
clones, fixed `gpt-5.6-sol`/high reasoning, one turn, the unchanged `g2-code-health-v2` rubric,
900-second per-run budgets, network disabled and all MCP/apps/plugins disabled.

`g5-blind-results-final.json` and `g5-blind-human-review.md` pass with 20/20 canonical results,
zero issues, zero truncation and strict ordering:

| G5 additions | High | Medium | Low |
|---|---:|---:|---:|
| APP | 1.847222 | 1.816667 | 1.000000 |
| FRAMEWORK | 2.370370 | 1.816667 | 0.944445 |

`g5-blind-run-audit.json` reports 402 shell calls, 4,715 files opened/reported, 610 evidence
anchors and 5,294.835 aggregate seconds, with zero MCP, web, file-change, timeout, forbidden-command
or clone-mutation events.

`g5-full-calibration-audit.json` reconstructs the latest accepted result for all 40 repositories
across G3/G5 and passes with zero issues:

| Full 40 | High | Medium | Low |
|---|---:|---:|---:|
| APP | 1.871032 | 1.773810 | 1.055555 |
| FRAMEWORK | 2.253968 | 1.869048 | 1.060185 |

All eight controlled high/low family orderings pass with gaps from 0.555556 to 1.333333. Across
the current 40 results, the evaluator recorded 1,251 evidence anchors, 8,069 files opened/reported,
793 tool calls and 11,900.269 aggregate seconds with no truncation.

## Calibration repairs retained

- The first complete G5 APP snapshot failed high > medium ordering. APP-06 received real build/test
  ownership and navigation-runtime repairs; APP-07 received source, runtime, typed-service and test
  repairs. Their pre-repair results/raw artifacts remain under G5 `rejected/` directories.
- FW-19 blind review exposed a raw Java U+0000 and Gradle ownership gaps. A full scan found the same
  source-key issue in APP-11 and FW-11/12/13. All five were repaired, compiled/tested where locally
  possible, re-evaluated at new HEADs, and their pre-repair results were retained.
- Final tracked Java/XML/AIDL/Gradle source NUL count is zero. APP-11 compiles 30 classes with 4/4
  tests; FW-19 compiles 60 classes with 3/3 tests; all four affected framework dispatch tables
  compile independently.

## Safety, legal and binary audit

`g5-delivery-audit.json` passes with zero issues:

- 40/40 clean worktrees, zero remotes, 40/40 root licenses;
- 31/31 applicable final source-intake records pass; nine synthetic repositories are explicit;
- zero high-confidence secrets, LFS pointers, submodules, tracked cache/generated directories,
  source NULs, or individual files at least 10 MiB;
- 32 retained upstream test/tool binaries total 17,108,049 bytes and remain an explicit warning.
  They are excluded from production-size statistics and include test keys/libraries, Gradle wrapper
  JARs and computepipe test shared libraries.

No repository was pushed, uploaded, published, used to create a remote, PR or paid operation.

## Honest limitations

- The originally described external evaluation service was unavailable. G2/G3/G5 used the
  documented independently isolated Codex CLI equivalent; reports do not represent it as an
  external-service run.
- Many public AAOS/CarService/SystemUI slices require an AOSP/AAOS/BSP product tree. Their manifest
  `buildability` and failed/non-scored calibration dimensions state this explicitly. Local
  AIDL/Java/JVM compilation evidence is not presented as a complete product build or device run.
- Retained upstream test/tool binaries and all licenses should be re-audited if the delivery is
  redistributed or modified.

With these explicit limits, G0–G5 completion criteria are satisfied and the benchmark is accepted
for local reuse.
