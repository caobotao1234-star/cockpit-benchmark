# G3 FRAMEWORK Audio/Binder Control Family Acceptance

Date: 2026-08-29  
Status: **ACCEPTED FOR G3 INVENTORY**

## Repositories

| ID | Repository | Tier | Build | HEAD | Source files | Source LOC | Band |
|---|---|---|---|---|---:|---:|---|
| FW-04 | `repos/framework/cockpit-audio-service` | high | Soong | `be95188ed46871d0f4a7352de12745d24498b3d2` | 262 | 38,637 | small |
| FW-17 | `repos/framework/binder-hub-service` | low | Soong | `7a2bc2cbb17a2e9c407958a38dd1d1884ec0a0c8` | 263 | 37,015 | small |

The actual source-file ratio is `263/262 = 1.004`; the source-LOC ratio is
`38,637/37,015 = 1.044`. Both are below the controlled-family cap of `1.35`. Each repository has
275 effective tracked files and satisfies the FRAMEWORK production-small dual threshold.

## Controlled lineage and source-mode revision

Both repositories are adapted from Apache-2.0 services/Car commit
`0be103dc50a93e57ff6e0e8064f35f30df8c9e79`. They share the same audio/media,
user/occupant, power, focus, system, car-internal, car-builtin, and resource boundary.

FW-17 was revised from synthetic to adapted before construction under the slot's `S/A` allowance.
Producing more than 250 original files solely to make one low-tier hub would recreate the rejected
mechanical feature-shell failure and confound source mode with quality. Candidate and matrix
validators pass after the revision; G3 now has two pure synthetic members, and G4 must preserve the
final 8–12 quota.

## Deterministic quality evidence

| Signal | FW-04 | FW-17 |
|---|---:|---:|
| Recognized Soong modules | 5 | 6 |
| Production/test source files | 155 / 62 | 260 / 0 |
| Test logical LOC | 12,265 | 0 |
| Reflection sites | 1 | 4 |
| Global-state sites | 1 | 3 |
| Near-duplicate pairs at 0.80 | 0 | 102 |
| Near-duplicate file ratio | 0 | 0.392308 |

FW-04 separates audio API, occupant/user API, power API, system support, and audio service modules.
`CarAudioService` enforces volume/settings permissions on Binder entry points;
`BinderInterfaceContainer` links callback death and removes dead binders; the audio service also
links/unlinks HAL death and releases callbacks. Its 62 tests cover service, focus, zones, callback,
HAL wrapper, API, permissions, configurations, and an exercise app. Two retained upstream test
TODO markers and inherited user/power hotspots are recorded limitations rather than hidden.

FW-17 adds a single Bundle-based `ICockpitServiceHub` for audio, power, user, and media. Its service
constructs but never enforces `HubPermissionTable`; callback lists, service cache, state cache, and
journal use process-global mutable state; reflected ServiceManager results are exposed as raw
binders; `HubRecoveryLoop.stop()` does not cancel polling. The shared, 8155, and 8295 source stacks
produce 102 near-duplicate pairs, while the repository contains no tests.

## Branch behavior

- Every FW-04 development/release/platform branch uses the accepted main HEAD as merge base,
  changes one two-line product file, and shares `0.996377` of blobs.
- Every FW-17 side branch uses `7db22c9f10b656d8f4e88ba2690016bef819928b` as merge base,
  changes three files relative to main, and omits the later pulse/fallback evolution. The
  identical-blob ratio is `0.98913`.
- A branch and directory both named `platform/8155` exposed a Git short-ref ambiguity. The
  branch-reuse probe now resolves `refs/heads/...`; a dedicated regression test passes.

## Verification

- Formal probes, quality signals, branch reuse, and source-intake reports were regenerated after
  completing the same-upstream direct dependency closure.
- SDK 35 AIDL generated two Java interfaces for FW-17; generated plus hub Java compiled to 30
  class files against Android 35.
- Both formal repositories pass `git fsck --full`, have clean worktrees, have no configured remote,
  and have distinct semantic branch heads.
- Source intake confirms exact formal HEADs, Apache-2.0 root licenses, no sparse missing files, no
  submodules, and no file at least 10 MiB.
- Forbidden truth/quality-label terms and high-confidence credential patterns each have zero
  matches in both tested repositories.
- `validate_benchmark.py --allow-partial` passes all 12 registered repositories using fresh
  `git clone --no-hardlinks`: `valid: true`, `issues: []`, `probed_count: 12`.
- G3 matrix validation remains `valid: true`, `issues: []`; control tests pass 19/19.

## Limits

The full audio/user/power services require AAOS platform APIs, generated resources, audio-control
HAL types, and system libraries. Both manifest entries therefore use `buildability: aosp_required`.
The successful FW-17 hub compilation does not prove a complete Soong product build, and no device
test was executed in this round.

No command pushed, uploaded, published, or created a remote/PR.
