# G3 APP Settings Control Family Acceptance

Date: 2026-08-29  
Status: **ACCEPTED UNDER PROBE 1.1.0**

| ID | Repository | Tier | Build | HEAD | Source files | Source LOC | Band |
|---|---|---|---|---|---:|---:|---|
| APP-01 | `repos/app/aurora-settings` | high | Gradle | `7d347803ae70eb01fdeafaff3094404909377c59` | 1,443 | 106,170 | large |
| APP-15 | `repos/app/atlas-settings` | low | Gradle | `33e092be7f1376ae652adbf1c96fc4d7841c45da` | 1,331 | 101,808 | large |

The file ratio is `1,443/1,331 = 1.084`; the LOC ratio is `106,170/101,808 = 1.043`.
Both satisfy APP large and the shared 1,200–1,500 file /100k–120k LOC window.

APP-01 retains the complete locked modern AAOS Settings source, 477 tests and real resources, but
localized `values-*` are excluded from size by probe 1.1. Four Gradle modules separate app,
common/QC/search, connectivity, and account/security/enterprise domains. It has one reflection
site, 15 near-duplicate pairs (ratio 0.017336), and current-main product branches with blob reuse
0.999416.

APP-15 retains the locked NXP Android 10 application and adds a bounded modern generation for
applications, bluetooth, wifi, security, accounts, profiles and common plus 104 matching modern
tests. The global `LegacySettingsRuntime`/`SettingsPageCoordinator` bridge is connected to every
`BaseCarSettingsActivity`; it uses reflection, static cache/callback state, hard-coded platform
packages and uncancelled polling. The repository has 89 near-duplicate pairs (ratio 0.161818), and
its 398 tests do not exercise the bridge or cross-generation consistency. Five side branches omit
the later journal/fallback commits.

Verification:

- Formal probe, quality, source-intake and branch reports match the table.
- APP-15 bridge Java compiles to 10 class files against Android 35.
- Both repositories pass `git fsck --full`, clean-worktree, no-remote, Apache-2.0 license,
  no-submodule, no >=10 MiB file, truth-leak and high-confidence credential checks.
- The active 14-repository benchmark passes fresh `git clone --no-hardlinks` and deterministic
  validation with `issues: []`; G3 matrix validation is green.
- Quality-signal 1.1 fixes bare `placeholder` UI-word false positives while retaining actual
  assert/reflection/TODO placeholder checks.

Both full apps remain `aosp_required`; no complete product build or device run is claimed. No
command pushed, uploaded, published or created a remote/PR.
