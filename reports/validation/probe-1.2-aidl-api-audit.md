# Probe 1.2 aidl_api exclusion audit

- Active repositories: 20
- Generated `aidl_api` paths tracked by active repositories: 0
- Active manifest fact changes: 0
- Decision: migrate manifest stats method to `cockpit-repo-probe` 1.2.0 and exclude all `aidl_api` directories from future tracked/source/LOC statistics.

Frozen AIDL API snapshots remain valid upstream artifacts when retained, but they are generated history and cannot satisfy production-size thresholds.
