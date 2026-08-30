# G3 APP Launcher Control Family Acceptance

Date: 2026-08-29  
Status: **RE-ACCEPTED UNDER PROBE 1.1.0**

## Current repositories

| ID | Repository | Tier | Build | HEAD | Source files | Source LOC | Band |
|---|---|---|---|---|---:|---:|---|
| APP-02 | `repos/app/horizon-launcher` | high | Soong | `be0ba1df6a22d6db71add7e1bab11166ac9fa632` | 413 | 36,269 | medium |
| APP-16 | `repos/app/nova-launcher` | low | Soong | `7e60333d1980be7209b8b2d81fb33873dd50f3ea` | 514 | 40,968 | medium |

The actual file ratio is `514/413 = 1.245`; the LOC ratio is `40,968/36,269 = 1.130`.
Both are below 1.35 and both satisfy the APP medium dual threshold after localized values are
excluded.

## Construction and quality evidence

APP-02 retains the locked public Car Launcher SHA and adds the public Car SystemUI SHA
`435ba702f1198e1c249a8b5550c37f27bba73b03`: systembar, userswitcher, window, notification, and
17 corresponding test sources. It now has eight recognized Soong modules, 71 test sources,
12,241 test logical LOC, and zero deterministic near-duplicate pairs. TEST_MAPPING references only
the six retained Launcher/system-shell targets. All product/presubmit branches use current main as
merge base and share `0.999026` of blobs.

APP-16 retains its public customized Launcher SHA and the already connected vendor runtime. At the
pre-ledger/fallback common point, it now preserves full 8155 and 8295 Launcher source stacks as
separate Soong modules. It has nine recognized modules and 183 near-duplicate pairs with a
near-duplicate file ratio of `0.45481`; 53 inherited tests do not reference the vendor/product or
copied platform paths. Five side branches intentionally omit the later signal-ledger and task-
fallback commits.

## Verification

- Probe 1.1 reports, quality signals, source intake, and branch reuse were regenerated from formal
  HEADs.
- Both repositories pass `git fsck --full`, have clean worktrees, no configured remote, no
  forbidden truth-label term, no high-confidence credential pattern, no submodule, and no file at
  least 10 MiB.
- Source headers and root license identify Apache-2.0. APP-02 provenance separately records the
  secondary SystemUI URL/SHA; APP-16 provenance describes the local platform stack copies.
- The active 12-repository benchmark passes fresh `git clone --no-hardlinks` and deterministic
  validation: `valid: true`, `issues: []`. G3 matrix validation is also green.

## Limits

Both repositories require AAOS/AOSP Launcher, SystemUI, WindowManager, hidden/system APIs and Soong
product inputs; `buildability` remains `aosp_required`. No complete product build or device test is
claimed in this round.

No command pushed, uploaded, published, or created a remote/PR.
