# Cockpit Code Health Benchmark

> [!IMPORTANT]
> **当前阶段固定只交付和验收 6 个 benchmark 示例，不需要再向用户询问“是哪 6 个”。**
> 其余 34 个仓库只是保留库存，状态为 `pending`，不属于当前评分分母。精确名单、路径和
> APP/FW 评分合同见 [ACTIVE_SIX.md](ACTIVE_SIX.md)。

| ID | 仓库 | 类型 | 质量档 | 恢复后路径 | 标准分 |
|---|---|---|---|---|---:|
| APP-01 | aurora-settings | APP | 高 | `repos/app/aurora-settings` | **33/40** |
| APP-11 | motion-control | APP | 中 | `repos/app/motion-control` | **26/40** |
| APP-15 | atlas-settings | APP | 低 | `repos/app/atlas-settings` | **15/40** |
| FW-03 | vehicle-hal-adapter | FW | 高 | `repos/framework/vehicle-hal-adapter` | **63/72** |
| FW-08 | soa-gateway | FW | 中 | `repos/framework/soa-gateway` | **52/72** |
| FW-19 | can-middleware | FW | 低 | `repos/framework/can-middleware` | **34/72** |

Status: `transport-v0.3.0` is the scored active-six checkpoint. The complete machine-readable
truth is [STANDARD_SCORES.json](STANDARD_SCORES.json); the human matrices and all 75 evidence rows
are in [SCORECARD.md](SCORECARD.md) and [SCORECARD.csv](SCORECARD.csv). The exact APP/FW contract is
[SCORE_RULES.md](SCORE_RULES.md). Do not reuse historical calibration or add dimensions outside it.

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
embedded C/C++ contract. See [ACTIVE_SIX.md](ACTIVE_SIX.md). Keep `STANDARD_SCORES.json`,
`SCORECARD.*`, `oracle/` and the parent manifest outside the evaluator input; compare the evaluator
result with the matching standard-score record only after its run completes.

## Layout

- `repos/app/`: 20 independent APP repositories.
- `repos/framework/`: 20 independent FRAMEWORK repositories.
- `oracle/`: repository-level evidence and expected ordinal behavior, outside tested repositories.
- `reports/validation/`: deterministic validation and calibration evidence.
- `manifest.json`: structured source of truth.
- `manifest.md`: human-readable summary.
- `STANDARD_SCORES.json`: current-head benchmark standard scores for the active six.
- `SCORECARD.md` / `SCORECARD.csv`: human-readable matrices and 75 evidence-bearing leaves.
- `SCORE_RULES.md`: sole APP/FW scoring contract used by this checkpoint.
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
standalone builds. Focused compile/test evidence is recorded in the scorecard and validation pack;
public transport does not change evaluator isolation.
