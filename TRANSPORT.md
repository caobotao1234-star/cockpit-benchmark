# GitHub transport

This wrapper repository transports the complete cockpit benchmark without turning the 40 nested
repositories into Git submodules or mode-160000 gitlinks. Fourteen public-lineage children
retain an intentional shallow boundary; ordinary Git bundles are not self-contained for those
repositories, so the transport preserves their complete `.git` metadata directories instead.

## Representation

- `.cockpit-transport/repositories/` contains one path-safe `.git.tar` metadata archive for every
  APP/FRAMEWORK repository, including shallow markers where applicable.
- `.cockpit-transport/transport-index.json` binds every archive to its SHA-256, typed and peeled
  refs, symbolic HEAD, object format, shallow boundaries, object/reflog/config/index inventories,
  raw Git tracked-file count, manifest entry and destination path. This raw count is deliberately
  distinct from the probe-filtered `manifest.tracked_files`.
- `Restore-CockpitBenchmark.ps1` is a thin PowerShell launcher. The restore implementation is
  `Restore-CockpitBenchmark.py`, and `Verify-CockpitTransport.py` is the independent transport
  verifier. Python 3.12 or newer is required and is the version tested for this release.
- The restore implementation verifies the index and archive hashes, recreates the 40 independent
  worktrees, enables repository-local `core.longpaths=true` before checkout, checks refs/HEAD/raw
  Git tracked-file counts, runs `git fsck --full`, and confirms no child remote exists.
- `repos/` is intentionally ignored by the outer wrapper. On the authoring computer it contains
  the live independent repositories; after a fresh wrapper clone it is reconstructed from archives.

The current 40 metadata archives total 807,383,040 bytes. The largest archive is 58,583,040 bytes,
below GitHub's 100 MB per-file hard limit. Git LFS is therefore not enabled and no paid LFS quota
is used. This index was generated at `2026-09-02T15:10:47.659338Z` and binds manifest SHA-256
`79979245c03b553e84f068b66d09c0697a9a210b32e6e1aee63be27ec5413c4e`. The rejected bundle experiment is documented at
`reports/validation/private-transport-bundle-rejection.json`.

The wrapper is public at `https://github.com/caobotao1234-star/cockpit-benchmark`. Its manifest,
oracle and historical calibration artifacts are therefore public ground truth. Never give the
wrapper root to a blind evaluator; give it exactly one restored child repository root.

## Restore after cloning

From PowerShell in the cloned wrapper repository:

```powershell
.\Restore-CockpitBenchmark.ps1
```

To restore into another empty root:

```powershell
.\Restore-CockpitBenchmark.ps1 -DestinationRoot 'D:\Project\Git.temp\cockpit-benchmark-restored'
```

To retain a machine-readable restore report:

```powershell
.\Restore-CockpitBenchmark.ps1 -DestinationRoot 'D:\Project\Git.temp\cockpit-benchmark-restored' `
  -ReportPath '.\reports\validation\private-transport-restore.json'
```

To exercise one repository only:

```powershell
.\Restore-CockpitBenchmark.ps1 -DestinationRoot "$env:TEMP\cockpit-restore-probe" -RepositoryId APP-03
```

Do not give this outer wrapper, `manifest.json`, `oracle/`, `calibration/`, or the transport index
to an evaluation Agent. The Agent receives exactly one restored repository root.
