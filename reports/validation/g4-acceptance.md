# G4 Acceptance — Full 40-Repository Production Set

Accepted: 2026-08-30

## Decision

G4 is accepted. The delivery contains exactly 20 APP and 20 FRAMEWORK independent Git
repositories, and all deterministic production, quota, clone and safety gates pass. This does not
complete the Goal: 20 G4 repositories remain `verified` rather than `calibrated`, so G5 isolated
blind evaluation and final audit are still required.

## Final production distribution

| Dimension | APP | FRAMEWORK |
|---|---:|---:|
| Repository count | 20 | 20 |
| High / medium / low | 7 / 7 / 6 | 7 / 7 / 6 |
| Gradle / Soong | 16 / 4 | 4 / 16 |
| Small / medium / large | 6 / 9 / 5 | 5 / 9 / 6 |

- Public upstream lineage: 31/40; honest synthetic: 9/40.
- Frozen controlled families: four APP and four FRAMEWORK; all retained same build/domain/size
  constraints and both source-file/LOC ratios at or below 1.35.
- Feature probes: AIDL 34/40, Binder 40/40, reflection 34/40, hidden/system API 36/40 and
  integration-test evidence 37/40.
- All 40 repositories have a release/SOP branch and a platform branch with an actual branch commit.

## Final two repositories

- APP-20 `drive-center`: 1,030 source files, 111,052 LOC, 10 Gradle modules, APP large. Its two
  local AIDL interfaces and 30 local Java sources compile against Android 35 into 41 class files.
  Connected low-tier evidence includes a coarse twelve-domain Binder facade, 277 near-duplicate
  pairs, 86 reflection sites and 37 global-state sites.
- FW-20 `system-service-facade`: 1,613 source files, 213,136 LOC, 39 Soong modules, FRAMEWORK
  large. Its two local AIDL interfaces and 24 local Java sources compile against Android 35 into
  34 class files. The facade is wired into `ICarImpl`; duplicated 8155/8295 endpoints yield 191
  near-duplicate pairs alongside 90 reflection and 73 global-state sites.

The first FW-20 shape (1,592 files/212,453 LOC) met the contractual large threshold but was not
accepted because it missed the frozen 1,600-file production window and its local facade was too
small relative to the mature upstream closure. The accepted revision adds connected dual-platform
endpoint stacks and rebases all product branches onto the final main HEAD.

## Deterministic and clone evidence

- `g4-final-candidates.json`: 58 candidates, 40/40 slots covered, zero errors.
- `g4-final-matrix.json`: exact 40-repository final quotas, 31 public lineages, nine synthetic,
  four families per kind, zero issues.
- Control tests: 22/22 pass.
- `g4-final-40-repos-no-clone.json`: `repository_count=40`, `probed_count=40`, `issues=[]`,
  `valid=true`.
- `g4-final-40-repos-clone.json`: all 40 repositories cloned with `git clone --no-hardlinks` into
  fresh temporary paths and reprobed; `clone_smoke=true`, `issues=[]`, `valid=true`.
- APP-20/FW-20 compilation evidence is reproducible with
  `scripts/verify_final_low_large_compile.py` from the control workspace.

## Safety and legal audit

`g4-delivery-audit.json` passes with zero issues:

- 40/40 clean worktrees, zero configured remotes and 40/40 root licenses;
- 31/31 applicable final source-intake reports pass; nine synthetic repositories are explicitly
  not applicable;
- zero high-confidence secret matches, LFS pointers, submodules, tracked cache/generated
  directories or files at least 10 MiB;
- 31 retained upstream test/tool binaries total 17,053,720 bytes and remain an explicit warning.
  They include test JKS/JARs, two Gradle wrapper JARs and four computepipe test `.so` files; none is
  treated as production LOC or a secret, and G5 must re-audit the inventory.

No repository was pushed, uploaded, published, or used to create a remote or PR.

## G5 boundary

`g4-g5-gate-check.json` deliberately runs final validation without partial mode and is rejected
only with `calibration_incomplete` for the 20 new G4 repositories. This proves the G4 dataset-ready
state cannot be mislabeled as Goal completion. G5 must now run repository-only isolated blind
evaluation for those 20 exact HEADs, validate gradients/evidence/exploration, update oracle and
manifest statuses, repeat the 40-repository final clone/safety audit, and only then consider the
Goal complete.
