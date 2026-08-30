# G3 APP Media Control Family Acceptance

Date: 2026-08-29  
Status: **RE-ACCEPTED UNDER PROBE 1.1.0**

The original figures below are retained as historical v1.0.0 evidence. Probe 1.1.0 correctly
excluded localized Android `values-*` resources and temporarily reopened both repositories. A
reviewed repair then added connected, non-localized media behavior and tests. Current canonical
facts are APP-04 `174 files / 10,037 LOC` at
`fb12fe8e07d48404739ca20e99a9cb0a1addb2e7` and APP-18 `180 / 10,016` at
`a88e94b024b5a13653d20034e3db753640371c0e`; file and LOC ratios are `1.034` and `1.002`.

APP-04 now compiles 58 runtime class files and passes 27/27 JVM tests across 16 test sources. Its
deterministic signals remain 0 reflection, 0 broad catches, and 0 near-duplicate pairs. APP-18
compiles 42 runtime/hub class files and has 19 reflection sites, 16 broad catches, 6 global-state
sites, 48 near-duplicate pairs, and only one inherited platform test source. Both were restored to
the active manifest and verified matrix status after the probe-1.1 validation pass.

## Repositories

| ID | Repository | Tier | Build | HEAD | Source files | Source LOC | Band |
|---|---|---|---|---|---:|---:|---|
| APP-04 | `repos/app/wave-media` | high | Gradle | `dd500754ffb8f0079ae7220a4995f10f0df2e4b0` | 217 | 10,073 | small |
| APP-18 | `repos/app/stream-media` | low | Gradle | `5d30a3cf99792572012f0b7770c32fb675582b62` | 215 | 10,050 | small |

The actual high/low ratios are `217/215 = 1.009` for source files and
`10,073/10,050 = 1.002` for source LOC. Both are below the `1.35` controlled-family cap and both
members satisfy the APP small dual threshold.

## Lineage and construction

Both repositories use Apache-2.0 public Android Automotive lineages locked before construction:

- Car Media `8666e534a0b568d6647a7f5c518975213519628a`;
- LocalMediaPlayer `e154cff25a803a24a673c24b862ee23ce9973b5a`;
- services/Car media slice `0be103dc50a93e57ff6e0e8064f35f30df8c9e79`.

APP-04 keeps the media app, local provider, platform Binder layer, and typed playback runtime in
four recognized Gradle modules. APP-18 keeps three recognized Gradle modules and connects its
shared runtime directly to `LocalMediaBrowserService`; subsequent local history adds global
reflection, copied player facades, static listener state, hard-coded platform policy, and branches
that do not contain the last two main runtime commits. Exact upstream URLs, commits, and local
modifications are recorded in `manifest.json` and each repository's `provenance/UPSTREAM.md`.

## Deterministic quality evidence

| Signal | APP-04 | APP-18 |
|---|---:|---:|
| Production/test source files | 45 / 6 | 49 / 1 |
| Reflection sites | 0 | 3 |
| Broad catches | 0 | 2 |
| Near-duplicate pairs at 0.80 | 0 | 3 |
| Near-duplicate file ratio | 0 | 0.06 |

APP-04's runtime separates immutable playback state, reducer, bounded queue/ledger, source
registry, failure policy, and audio-focus lifecycle. APP-18's `StreamMediaRuntime` uses a process
singleton, reflected `ServiceManager`, `setAccessible`, broad `Throwable`, and uncancelled polling;
`PlaybackCoordinator` aggregates unrelated responsibilities; `PlaybackNotificationState` retains
static listeners without detach; and three 39-line platform facades form three near-duplicate
pairs with similarities from `0.868613` to `0.882353`.

APP-04's develop/release/platform branches use current main as merge base and share `0.995833` of
blobs. APP-18's corresponding branches share the older `40583fdeec685752e7bd17986851f0a9b51096bd`
merge base and omit two later main files, with `0.987288` identical-blob ratio.

## Verification

- `repo_probe.py` and `quality_signals.py` reports were regenerated from the formal HEADs.
- Added APP-04 main Java compiled against Android 35 and produced 17 class files; added APP-18
  runtime Java compiled and produced 16 class files. The only compiler note was deprecated-API use.
- Four APP-04 JVM test classes ran through JUnit 4.13.2: `OK (5 tests)`.
- Both formal repositories pass `git fsck --full`, have clean worktrees, distinct semantic branch
  heads, and have no configured remote.
- Source intake found an Apache-2.0 root license in each repository, no sparse missing files, no
  submodule entries, and no file at least 10 MiB.
- A high-confidence credential-pattern scan found zero matches; forbidden truth/quality-label terms
  found zero matches inside either tested repository.
- `validate_benchmark.py --allow-partial` passed the current 10 repositories with fresh
  `git clone --no-hardlinks`: `valid: true`, `issues: []`, `probed_count: 10`.
- G3 matrix validation remains `valid: true`, `issues: []`; control tests remain 18/18 passing.

## Limits

Both full applications depend on AAOS platform libraries, `android.car`, and hidden/system APIs.
Their manifest `buildability` is therefore `aosp_required`. The local runtime compilation and JVM
tests do not establish a complete AAOS build or device result. APP-04's instrumentation contract
test is present and detected but was not executed on a device in this round.

No command pushed, uploaded, published, or created a remote/PR.
