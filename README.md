# Cockpit Code Health Benchmark

> [!IMPORTANT]
> **当前阶段固定只交付和验收 6 个 benchmark 示例，不需要再向用户询问“是哪 6 个”。**
> 其余 34 个仓库只是保留库存，状态为 `pending`，不属于当前评分分母。精确名单、路径和
> APP/FW 评分合同见 [ACTIVE_SIX.md](ACTIVE_SIX.md)。

| ID | 仓库 | 类型 | 质量档 | 恢复后路径 |
|---|---|---|---|---|
| APP-01 | aurora-settings | APP | 高 | `repos/app/aurora-settings` |
| APP-11 | motion-control | APP | 中 | `repos/app/motion-control` |
| APP-15 | atlas-settings | APP | 低 | `repos/app/atlas-settings` |
| FW-03 | vehicle-hal-adapter | FW | 高 | `repos/framework/vehicle-hal-adapter` |
| FW-08 | soa-gateway | FW | 中 | `repos/framework/soa-gateway` |
| FW-19 | can-middleware | FW | 低 | `repos/framework/can-middleware` |

Status: active-six production-rubric realignment in progress. Public tag `transport-v0.2.0`
is the latest verified 40-repository **transport snapshot**, but it does not contain the final
current-head six-repository scores or `SCORECARD.md`. Do not invent those scores or reuse historical
calibration. A later non-rewriting checkpoint will add the final human scorecard.

This directory is the delivery root for the cockpit Android code-health benchmark. Locally, each
directory below `repos/app/` and `repos/framework/` is an independent, remote-free Git repository.
The outer repository is only a public transport wrapper: it stores verified Git metadata archives and never
records the children as gitlinks. See `TRANSPORT.md` and run
`Restore-CockpitBenchmark.ps1` after a fresh wrapper clone.

The transport inventory contains 20 APP and 20 FRAMEWORK repositories. The current benchmark
completion scope is the six repositories listed above: three APP examples and three FW examples,
covering high/medium/low quality. The other 34 repositories remain preserved but pending. The
authoritative transport inventory is `manifest.json`; `reports/validation/g5-acceptance.md` is
historical evidence for the earlier rubric, not current active-six scoring evidence.

## Evaluation isolation

Give the evaluation Agent exactly one repository directory as its input. Do not give it this parent directory, `manifest.json`, or `oracle/`; those contain benchmark labels and ground truth.

For the current stage, select only one of the six child paths in the table above. The repository
selection is fixed; an evaluator must not ask the user to choose another set. APP repositories use
the APP 8-leaf/40-point contract, while FW repositories use the distinct FW 17-leaf/72-point
embedded C/C++ contract. See [ACTIVE_SIX.md](ACTIVE_SIX.md).

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
