# 当前 6 仓 Benchmark 使用说明

## 结论先行

当前阶段的 benchmark 集合已经固定为下列 6 个仓库。不要再询问用户“选哪 6 个”，也不要
把另外 34 个库存仓加入评分、平均分、完成率或盲评任务。

| ID | 仓库 | 类型 | 质量档 | 恢复后输入目录 | 叶子数 / 满分 | 标准分 |
|---|---|---|---|---|---:|---:|
| APP-01 | aurora-settings | APP | 高 | `repos/app/aurora-settings` | 8 / 40 | **33/40** |
| APP-11 | motion-control | APP | 中 | `repos/app/motion-control` | 8 / 40 | **26/40** |
| APP-15 | atlas-settings | APP | 低 | `repos/app/atlas-settings` | 8 / 40 | **15/40** |
| FW-03 | vehicle-hal-adapter | FW | 高 | `repos/framework/vehicle-hal-adapter` | 17 / 72 | **63/72** |
| FW-08 | soa-gateway | FW | 中 | `repos/framework/soa-gateway` | 17 / 72 | **52/72** |
| FW-19 | can-middleware | FW | 低 | `repos/framework/can-middleware` | 17 / 72 | **34/72** |

## 版本状态

- `transport-v0.3.0` 是当前 scored active-six checkpoint；`transport-v0.2.0` 保持不动，仅作旧运输快照。
- `STANDARD_SCORES.json` 是机器可读标准分；`SCORECARD.md` / `SCORECARD.csv` 是人类审阅表。
- 标准分严格绑定表中 current HEAD 和 `SCORE_RULES.md`。旧 calibration、旧 rubric 和额外维度均不得复用。
- 34 个 pending 仓没有当前标准分；不得给它们补 0、猜分或纳入完成率。

## APP 评分合同：8 叶 / 40 分

| 维度.子维度 | 满分 |
|---|---:|
| `architecture.componentization` | 5 |
| `architecture.decoupling` | 3 |
| `architecture.modularization` | 3 |
| `compilation.ci_independence` | 3 |
| `compilation.compilation_independence` | 3 |
| `compilation.api_version_management` | 3 |
| `platform_reuse.platform_upgrade` | 10 |
| `platform_reuse.release_branch_strategy` | 10 |

APP 的 `integration_test` 不属于本 benchmark 的 8 个 canonical 叶子。任何其他叶子也不得
临时加入、改名或从历史评分换算。

## FW 评分合同：17 叶 / 72 分

| 维度.子维度 | 满分 |
|---|---:|
| `architecture.componentization` | 5 |
| `architecture.decoupling` | 3 |
| `architecture.modularization` | 3 |
| `compilation.ci_independence` | 3 |
| `compilation.compilation_independence` | 3 |
| `compilation.api_version_management` | 3 |
| `platform_coupling.system_api` | 3 |
| `platform_coupling.internal_non_standard_api` | 3 |
| `platform_coupling.ipc_interface_standardization` | 3 |
| `platform_reuse.platform_upgrade` | 10 |
| `platform_reuse.release_branch_strategy` | 10 |
| `quality.integration_test` | 3 |
| `solid_principle.single_responsibility` | 4 |
| `solid_principle.open_closed` | 4 |
| `solid_principle.liskov_substitution` | 4 |
| `solid_principle.interface_segregation` | 4 |
| `solid_principle.dependency_inversion` | 4 |

FW 必须按 FW/QNX/MCU 嵌入式 C/C++ 事实评分，包括 CMake/Make/Soong、HAL/BSP/driver/
middleware 分层、循环 `#include`、函数指针/回调/接口结构体、RTOS/BSP/硬件绑定、平台内部
API、IPC 定义和嵌入式集成测试。不得套用 APP 的 Android system/hidden API、反射或 AIDL
计数口径。

## 下载与恢复

```powershell
git clone https://github.com/caobotao1234-star/cockpit-benchmark.git
Set-Location .\cockpit-benchmark
.\Restore-CockpitBenchmark.ps1
```

恢复完成后，一次只把上表中的一个子仓目录交给评估 Agent。例如：

```text
<clone-root>/repos/app/aurora-settings
```

不要把包装仓根目录、`manifest.json`、`oracle/`、`reports/` 或
`.cockpit-transport/transport-index.json` 交给盲评 Agent；这些内容会泄露 benchmark 真值或
协调信息。

评估完成后，再用仓 ID 到 `STANDARD_SCORES.json` 读取对应的 8 或 17 个叶子进行逐叶对比。
不要只比总分：benchmark 的主要用途是发现 Agent 在哪一个评分口径上偏高、偏低或缺证据。

## 标准分与人类评分表

本 checkpoint 在仓库根目录提供：

- `STANDARD_SCORES.json`：6 仓机器可读标准分、HEAD、逐叶理由和证据。
- `SCORECARD.md`：6 仓摘要、APP 3×8 矩阵、FW 3×17 矩阵，以及 75 条逐仓逐叶明细。
- `SCORECARD.csv`：同样的 75 条明细，便于 Excel 打开、筛选和评审。

每条明细包含分数/满分、具体理由、代码 `path:line` 证据和 current HEAD。标准分不是把
高/中/低标签反填成数值，而是由仓库真实事实独立评审、争议复核后得出；目标矩阵与结果不同时，
以实际 rubric 结果为准。
