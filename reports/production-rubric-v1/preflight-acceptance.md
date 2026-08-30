# Production rubric preflight acceptance

Status: `accepted_preflight_only` — this is not a completed production score calibration.

Two independent full recomputations (`run-m` and `run-n`) produced 41 files each with zero byte differences. Their common index file SHA-256 is `3cead03feb24b0e5b4ac6273a2e19ddb8e4b3381daaf726ccf96d53ec5b91809`; the embedded index facts hash is `0b927ef4177244580bbfb885b0f446dfe3d7041cf923659af2af6a15b1715ebf`.

- Current exact HEAD and clean worktree: 40/40.
- Fresh local clone smoke (`--no-hardlinks`) and full structural probe: 40/40, zero issues.
- APP / FRAMEWORK: 20/20.
- Current candidate quality metrics: 40/40; every metric remains explicitly `non_scoring`.
- Branch comparisons recomputed: 161; manifest-consistent repositories: 40/40.
- Gradle/Soong modules reprobed: 538; internal build edges: 413; anonymous modules, dependency probe errors, and module-cycle repositories: 0.
- Module inventory and branch comparison facts are manifest-consistent for 40/40 repositories.
- Missing production-contract leaves: 14/26 in every repository, all represented as `failed` with `score: null`.
- Production score documents accepted: 0/40.

Accepted facts are under `reports/production-rubric-v1/preflight/accepted/repositories/`. The prior accepted copy was moved intact to `preflight/rejected/pre-probe-1.4-accepted`; probe 1.3 refresh candidates are also retained under `preflight/rejected/`.

APP-12, APP-20, FW-08, and FW-16 have repaired current HEADs and are intentionally `verified`, not `calibrated`; their old-head blind runs remain historical. Fourteen production leaves per repository remain `failed/null` because their exact production detector/schema/maximum/lookup contract was not supplied.

No repository file or HEAD was changed by preflight, and no remote push/upload occurred.
