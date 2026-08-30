# G2 Blind Calibration Human Review

Date: 2026-08-29  
Status: **PASSED**

## Controlled result

All four reports were produced by independent repository-only jobs using `gpt-5.6-sol`, high
reasoning, one turn, a 900-second wall-clock budget, and prompt `g2-code-health-v2`. The canonical
result validator reports `valid: true`, four results, zero issues, and correct ordering in both
controlled families.

| Repository | Truth tier | Mean | Failed | Files opened | Directories | Tool calls | Wall clock | Truncated |
|---|---|---:|---|---:|---:|---:|---:|---|
| APP-03 | high | 2.111111 | compilation independence | 63 | 32 | 16 | 296.854 s | no |
| APP-17 | low | 0.444444 | compilation independence | 165 | 18 | 16 | 286.185 s | no |
| FW-02 | high | 2.222222 | compilation independence | 273 | 24 | 20 | 309.683 s | no |
| FW-15 | low | 0.666667 | compilation independence | 33 | 14 | 13 | 220.652 s | no |

- HVAC controlled pair: APP-03 `2.111111` > APP-17 `0.444444`; gap `1.666667`.
- Vehicle-property controlled pair: FW-02 `2.222222` > FW-15 `0.666667`; gap `1.555555`.
- Every one of the ten dimensions in every report has repository evidence. All nine scored
  dimensions in each report have at least one anchor, and the one failed dimension also has
  concrete build-boundary evidence.

## Manual source review

The coordinator checked representative positive and negative anchors against the exact repository
HEAD and declared branch. The deterministic validator separately resolved every cited path/ref.

### APP-03

- Confirmed the positive Binder boundary: `BinderClimateGateway` registers/unregisters the typed
  listener, links/unlinks death recipients, retries after `RemoteException`, and closes resources.
- Confirmed the architecture evidence: the domain repository is small and Binder-free, and the
  application composition root assembles the comfort, diagnostics, telemetry, and vehicle layers.
- Confirmed the reported limitation: retained upstream `HvacController` contains ten repeated
  `AsyncTask` sites and remains a large direct `android.car` compatibility path.
- Confirmed the test limitation: the Binder contract tests call `Stub.asInterface(local.asBinder())`
  in one process, so score 1 for integration testing is conservative but supported.

### APP-17

- Confirmed `ClimateCenterActivity` owns service access, controller construction, persisted state,
  and polling; polling is restarted on resume without a corresponding callback removal.
- Confirmed the exported `CockpitClimateService` has no manifest permission and returns the
  manager's raw Binder instead of an `ILegacyClimateService.Stub` implementation.
- Confirmed the platform bridges and feature controllers are near copies, while the only device
  test merely loads the Activity class.

### FW-02

- Confirmed typed AIDL, `oneway` event callbacks, Binder death cleanup, request IDs, pending maps,
  timeouts, and explicit AIDL/HIDL status mapping.
- Confirmed meaningful tests for AIDL/HIDL death handling, pending-request cleanup, callback
  deadlock avoidance, subscriptions, large parcel behavior, and vehicle-property flow.
- Confirmed the reported limitation that the standalone `VehicleHALTest` `android_test` stanza is
  commented out and the slice still depends on AAOS/AOSP platform inputs.

### FW-15

- Confirmed `ICarRuntime` is a 54-method String-based aggregate contract and `CarRuntimeService`
  repeats read/write/reset implementations for 18 domains; reset paths omit the caller check used
  by read/write paths.
- Confirmed the runtime tests are `assertTrue(true)` and `Class.forName` placeholders.
- Confirmed large-scale copied Handler/Facade families and 538-line product coordinators, including
  repeated route methods and hard-coded signal/capability tables.

## Review decision

No sampled anchor was fabricated, misattributed to the wrong ref, or inferred from a quality label,
repository name, source mode, or size. The reports found real limitations in both high-tier
repositories instead of treating them as perfect, and the low-tier scores were driven by code and
test evidence rather than synthetic origin. Exploration was sufficient for the observed systemic
patterns, no job was truncated, and original repositories remained unchanged with no remote.

G2 blind calibration and gradient review are accepted. G3 may start; this does not imply that the
40-repository Goal is complete.
