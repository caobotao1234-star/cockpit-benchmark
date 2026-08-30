# G3 FRAMEWORK Car API/Compatibility Family Acceptance

Date: 2026-08-29  
Status: **ACCEPTED UNDER PROBE 1.1.0**

| ID | Repository | Tier | HEAD | Files | LOC | Modules | Band |
|---|---|---|---|---:|---:|---:|---|
| FW-01 | `car-api-core` | high | `83c5c24261f986c7b8586eb7093ac9124712f7ab` | 1,622 | 216,059 | 41 | large |
| FW-16 | `platform-compat-service` | low | `e5ef0b5ba39ed54205d427ace5f4bba24458f151` | 1,978 | 246,971 | 51 | large |

File/LOC ratios are 1.219/1.143. Both use the same locked Apache-2.0 services/Car SHA and actual
car-lib, car-builtin, service and tests closure. Source intake reports every tracked file present,
no submodule or >=10 MiB file, clean worktrees and no remote.

FW-01 retains 606 tests (105,210 test LOC), type-safe ICar/manager/service boundaries and one
near-duplicate pair. FW-16 adds a full legacy car-lib module and connected Bundle/raw-Binder compat
service: 166 near-duplicate pairs, 17 reflection sites, global callback/cache/registry state and
uncancelled polling; existing upstream tests do not target compat. Its two AIDL files generate Java
and the new layer compiles to 22 class files.

Both pass `git fsck`, truth/credential scans and the active 16-repository fresh-clone validation
with zero issues. Full builds remain `aosp_required`; no remote push or publication occurred.
