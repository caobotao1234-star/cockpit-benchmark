# Cockpit Code Health Benchmark

Status: production-rubric realignment in progress. The earlier `g2-code-health-v2` G5 checkpoint
remains historical evidence; it is not a substitute for the new production-rubric scores.

This directory is the delivery root for the cockpit Android code-health benchmark. Locally, each
directory below `repos/app/` and `repos/framework/` is an independent, remote-free Git repository.
The outer repository is only a public transport wrapper: it stores verified Git metadata archives and never
records the children as gitlinks. See `TRANSPORT.md` and run
`Restore-CockpitBenchmark.ps1` after a fresh wrapper clone.

The final set contains 20 APP and 20 FRAMEWORK repositories. Each kind has 7 high, 7 medium and
6 low quality samples. The authoritative inventory is `manifest.json`; final acceptance and audit
evidence are under `reports/validation/g5-acceptance.md`.

## Evaluation isolation

Give the evaluation Agent exactly one repository directory as its input. Do not give it this parent directory, `manifest.json`, or `oracle/`; those contain benchmark labels and ground truth.

## Layout

- `repos/app/`: 20 independent APP repositories.
- `repos/framework/`: 20 independent FRAMEWORK repositories.
- `oracle/`: repository-level evidence and expected ordinal behavior, outside tested repositories.
- `reports/validation/`: deterministic validation and calibration evidence.
- `manifest.json`: structured source of truth.
- `manifest.md`: human-readable summary.
- `.cockpit-transport/`: SHA-bound child-repository metadata archives and restore index.
- `TRANSPORT.md`: download, restoration and isolation instructions.
- `LICENSE` / `NOTICE`: wrapper-level Apache-2.0 terms and child-license scope boundary.
- `reports/validation/g5-acceptance.md`: historical completion evidence for the prior rubric.

## Safety

No evaluated child repository may retain an external remote. Provenance belongs in the parent
manifest. Only the outer wrapper uses the recorded, user-owned GitHub transport remote. Because
the wrapper is public, its oracle and quality labels must never be included in blind evaluator input.

Complete AAOS/AOSP builds remain environment-dependent where `buildability` is `aosp_required` or
`bsp_stubbed`; those limits are recorded per repository and are not represented as successful
standalone builds. Public transport does not change evaluator isolation or calibration status.
