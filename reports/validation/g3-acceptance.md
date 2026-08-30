# G3 half-production acceptance

Date: 2026-08-29  
Gate: G3 - 10 APP + 10 FRAMEWORK  
Decision: **PASS**

G3 is accepted at the 20-repository half-production boundary. This report does not accept G4 or the
final 40-repository delivery.

## Accepted inventory

| Dimension | APP | FRAMEWORK |
|---|---:|---:|
| Repositories | 10 | 10 |
| High / medium / low | 4 / 2 / 4 | 4 / 2 / 4 |
| Gradle / Soong | 7 / 3 | 1 / 9 |
| Small / medium / large | 4 / 4 / 2 | 5 / 3 / 2 |
| Public adapted lineage / synthetic | 9 / 1 | 10 / 0 |
| AIDL | 5 | 10 |
| Binder or real SDK boundary | 10 | 10 |
| Reflection | 9 | 10 |
| Hidden/system API | 10 | 10 |
| Integration-test evidence | 8 | 9 |
| Release/SOP branch | 10 | 10 |
| Platform branch | 10 | 10 |

All 20 manifest entries and oracle records are `calibrated` / `blind_validated` at their exact
current HEAD. Nineteen repositories have exact locked public lineage; APP-17 is explicitly
synthetic and does not claim external origin.

## Deterministic acceptance

- `g3-acceptance-20-repos-final.json`: 20/20 repositories reprobed and cloned with
  `git clone --no-hardlinks`; `clone_smoke: true`, zero issues.
- `g3-matrix-20-repos.json` and the post-repair matrix validation: 10 APP + 10 FRAMEWORK, four
  controlled families per kind, one pure synthetic repository, zero issues.
- Candidate catalog: 51 records, 40/40 final slots covered, every slot has a primary and fallback,
  zero schema/coverage errors.
- Control tests: 21/21 pass, including probe 1.1 localized-resource exclusion, branch/ref collision,
  controlled-family size parity, blind isolation, evidence-path semantics, and strict tier ordering.
- APP-08 pure Java voice runtime self-test and APP-09 cluster runtime self-test pass.
- FW-10 repaired AIDL/Java generates and compiles to 21 class files against Android 35 plus narrow
  CarPropertyService/CarPropertyValue compile stubs. Full AAOS builds remain correctly recorded as
  `aosp_required`.

All eight controlled families use the same kind/domain/build/size band and satisfy both 1.35
limits:

| Family | Members | Band/build | File ratio | LOC ratio |
|---|---|---|---:|---:|
| app-launcher-medium | APP-02 / APP-16 | medium / Soong | 1.245 | 1.130 |
| app-media-small | APP-04 / APP-18 | small / Gradle | 1.034 | 1.002 |
| app-settings-large | APP-01 / APP-15 | large / Gradle | 1.084 | 1.043 |
| hvac-controlled-pair | APP-03 / APP-17 | small / Gradle | 1.337 | 1.112 |
| fw-audio-binder-small | FW-04 / FW-17 | small / Soong | 1.004 | 1.044 |
| fw-car-api-compat-large | FW-01 / FW-16 | large / Soong | 1.219 | 1.143 |
| fw-vehicle-hal-medium | FW-03 / FW-18 | medium / Soong | 1.323 | 1.166 |
| vehicle-property-controlled-pair | FW-02 / FW-15 | small / Soong | 1.267 | 1.249 |

## Blind calibration acceptance

The external evaluation service remains unavailable. G3 used the same documented equivalent as G2:
20 independent, offline, repository-only Codex CLI jobs with fixed `gpt-5.6-sol`, high reasoning,
one turn, the unchanged `g2-code-health-v2` rubric, and a 900-second per-repository wall-clock
budget.

- `g3-blind-results.json`: 20/20 canonical results, 641 evidence anchors, zero schema/ref/path/HEAD/
  score-status issues.
- `g3-blind-run-audit.json`: 20/20 raw runs, 391 shell calls, 3,354 files opened/reported,
  696 directories, 6,605.434 aggregate seconds, zero truncation, zero network/MCP/web/file-change
  events, and zero clone immutability errors.
- `g3-blind-human-review.md`: all 20 narratives and exploration records reviewed; 40 source anchors
  (two per repository) compared to exact HEAD/ref content, with no fabricated or label-derived
  observation.

Tier means pass the strict gradient gate:

| Kind | High | Medium | Low |
|---|---:|---:|---:|
| APP | 1.888889 | 1.666667 | 1.083333 |
| FRAMEWORK | 2.166667 | 2.000000 | 1.118056 |

All controlled families pass `high > low`; gaps range from 0.555556 to 1.333333. The smallest gaps
are Media and Settings, and both received explicit manual contrast review.

The first valid FW-10 result (2.333333) is not canonical because it made FRAMEWORK high and medium
means equal. The sample was repaired at the code/design level and independently rerun at the new
HEAD. The rejected result and raw artifacts are retained under `calibration/**/g3/rejected/`.

## Source, safety, and co-linearity audit

`g3-delivery-audit.json` reports zero errors:

- 20/20 clean worktrees, 0 configured remotes, 20/20 root licenses;
- 19/19 applicable final source-intake reports match HEAD with no sparse omissions, submodules, LFS,
  or files at least 10 MiB; APP-17 is synthetic and intake is not applicable;
- 0 high-confidence secret patterns, 0 tracked generated/cache directories;
- 16,368 tracked files audited; source probe excludes binaries and localized resources from size.

The audit inventories 24 small upstream binaries (about 2.93 MiB total): identical 2,593-byte
public AOSP Launcher test keystores in APP-02/APP-16, plus eleven BugReport test dependency JARs in
each of FW-01/FW-16. The keystore SHA-256 is
`976D3E7062C7F9EFD2A072D6BC6F72B0D267DBEC4F5BAB418B4A6A333A001867` in both repositories. These are
locked public test inputs, not production credentials; no current remote exists and they do not
contribute to source size. They remain an explicit G5 re-audit item rather than an unrecorded risk.

Quality is not fully collinear with size or build: APP and FRAMEWORK high/low each span small,
medium, and large; APP Soong appears in high/medium/low; FRAMEWORK Soong appears in all tiers; public
adapted lineage appears in all tiers. G3 APP medium currently contains only medium-size repositories,
and FRAMEWORK Gradle currently appears only in medium. This is a partial-set warning, not a final
quota claim: G4 must add APP medium samples in another size band, three further FRAMEWORK Gradle
slots, and enough legitimate synthetic S/A slots to reach the final 8–12 synthetic quota without
making source mode a quality shortcut.

## Gate boundary and next step

G3 is closed. G4 may begin from this accepted snapshot, but it must not weaken any existing family,
probe, blind, lineage, license, branch, or isolation invariant. G4 still needs ten APP and ten
FRAMEWORK repositories, final 7/7/6 quality distributions per kind, final 16/4 build distributions,
APP 6/9/5 and FRAMEWORK 5/9/6 size quotas, final source-mode targets, and then the separate G5
40-repository clone/calibration/security/license/remote audit.

No repository was pushed, uploaded, published, or used to create a remote or PR.
