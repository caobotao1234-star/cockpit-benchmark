# APP / FW 现行 LLM 子维度评分标准（Benchmark 版）

> 用途：供 codex 按标准为被测仓库制作 benchmark、给出各子维度标准分。

> 来源：平台 MySQL `t_prompt`（status=1 已发布，全部 version=1）正文，绑定来自 `t_agents_strategy`（平台基线-APP / 平台基线-FW）+ `t_agents_catalog`（max_score）。提取日 2026-08-31。

> 纪律：分档标准逐条摘自提示词原文；「需要的评分信息」= 打分前必须先收集的事实及其判定口径。每个子维度独立成节、自包含，可单独评分。

> 范围说明：只收录以 LLM 提示词评分的子维度。APP 的 integration_test 走 GBOP 流水线、无评分提示词，不在 benchmark 范围内（故 APP 为 8 个子维度）。

---

## 0. 总表

### APP（8 个）

| 子维度 | 满分 | promptKey |

|---|---|---|

| architecture.componentization | 5 | architecture.scoring |

| architecture.decoupling | 3 | architecture.scoring |

| architecture.modularization | 3 | architecture.scoring |

| compilation.ci_independence | 3 | compilation.ci_independence |

| compilation.compilation_independence | 3 | compilation.compilation_independence |

| compilation.api_version_management | 3 | compilation.api_version_management |

| platform_reuse.platform_upgrade | 10 | platform_reuse.platform_upgrade |

| platform_reuse.release_branch_strategy | 10 | platform_reuse.branch_strategy |

### FW（17 个）

| 子维度 | 满分 | promptKey |

|---|---|---|

| architecture.componentization | 5 | architecture.scoring_embedded |

| architecture.decoupling | 3 | architecture.scoring_embedded |

| architecture.modularization | 3 | architecture.scoring_embedded |

| compilation.ci_independence | 3 | compilation.ci_independence（与 APP 同一提示词） |

| compilation.compilation_independence | 3 | compilation.independence_embedded |

| compilation.api_version_management | 3 | compilation.api_version_embedded |

| platform_coupling.system_api | 3 | platform_coupling.scoring_embedded |

| platform_coupling.internal_non_standard_api | 3 | platform_coupling.scoring_embedded |

| platform_coupling.ipc_interface_standardization | 3 | platform_coupling.scoring_embedded |

| platform_reuse.platform_upgrade | 10 | platform_reuse.platform_upgrade_embedded |

| platform_reuse.release_branch_strategy | 10 | platform_reuse.branch_strategy（与 APP 同一提示词） |

| quality.integration_test | 3 | quality.integration_test_scoring_embedded |

| solid_principle.single_responsibility | 4 | solid.scoring |

| solid_principle.open_closed | 4 | solid.scoring |

| solid_principle.liskov_substitution | 4 | solid.scoring |

| solid_principle.interface_segregation | 4 | solid.scoring |

| solid_principle.dependency_inversion | 4 | solid.scoring |

---

## 1. APP 子维度

### 1.1 architecture.componentization（组件化架构）｜满分 5｜architecture.scoring

**需要的评分信息（先提取事实，再打分）**

- module_count：独立模块总数。含业务组件模块、基础库模块、app 模块；排除 test、androidTest、buildSrc、build-logic。

- standard_named_module_count：规范命名模块数。命名规范=小写字母+连字符/下划线；匹配关键字 base/core/common/util/widget/app/main/library/sdk/feature/biz/module。

- has_layered_directory：存在职责分层目录。UI 层标识=ui/view/presentation/page；领域层=domain/usecase/interactor/business/logic；数据层=data/repository/remote/local/network/database。任一标识目录存在→true。

- has_file_type_packages：仅文件类型分包。目录标识=activity/activities/fragment/fragments/adapter/adapters/utils/helper/helpers/constant/widget。**文件类型分包 ≠ 职责分层架构**。

- has_base_layered_architecture：同时存在 UI 层目录 + 领域层目录。

- is_component_friendly：满足任意 ≥3 项→true：①无模块间循环依赖 ②业务边界隔离、无跨模块目录侵入 ③公共能力下沉至 base/core 模块 ④支持模块独立编译 ⑤无跨模块硬编码依赖。

- 附加判断：业务分包结构是否存在；至少 2 个业务模块是否含职责分层目录；代码是否未存放于根包。

**强制约束**：评分前生成唯一不可变更的架构事实集合；评分必须基于该事实集合，禁止冲突性事实；不引入外部先验与主观推断。

**评分标准（从高档向低档判定）**

- **5 分 高级组件化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥2 ④至少 2 个业务模块包含职责分层目录 ⑤is_component_friendly=true

- **3 分 中等模块化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥1 ④存在业务分包结构

- **1 分 基础结构化**，满足任意 1 项：①has_layered_directory=true ②has_file_type_packages=true ③代码未存放于根包

- **0 分 无结构**：不满足以上所有条件

### 1.2 architecture.decoupling（代码解耦）｜满分 3｜architecture.scoring

**需要的评分信息**（事实口径独立列出，可单独评分）

- module_count：独立模块总数（含业务组件/基础库/app 模块；排除 test/androidTest/buildSrc/build-logic）。

- standard_named_module_count：小写+连字符/下划线命名、含关键字 base/core/common/util/widget/app/main/library/sdk/feature/biz/module 的模块数。

- has_layered_directory：UI 层（ui/view/presentation/page）/领域层（domain/usecase/interactor/business/logic）/数据层（data/repository/remote/local/network/database）任一标识目录存在。

- has_file_type_packages：仅 activity/activities/fragment/fragments/adapter/adapters/utils/helper/helpers/constant/widget 类目录；**文件类型分包 ≠ 职责分层**。

- has_base_layered_architecture：同时存在 UI 层目录 + 领域层目录。

- is_component_friendly：任意 ≥3 项：无模块间循环依赖 / 业务边界隔离无跨模块目录侵入 / 公共能力下沉 base/core / 模块可独立编译 / 无跨模块硬编码依赖。

- 附加判断：业务分包结构是否存在；至少 2 个业务模块是否含职责分层目录；代码是否未存放于根包。

**强制约束**：先有唯一事实集合，评分与事实一致，禁止冲突性事实、禁止外部先验。

**评分标准**

- **3 分 优秀解耦**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥2 ④至少 2 个业务模块包含职责分层目录 ⑤is_component_friendly=true

- **2 分 良好解耦**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥1 ④存在业务分包结构

- **1 分 基础解耦**，满足任意 1 项：①has_layered_directory=true ②has_file_type_packages=true ③代码未存放于根包

- **0 分 未解耦**：不满足以上所有条件

### 1.3 architecture.modularization（模块化程度）｜满分 3｜architecture.scoring

**需要的评分信息**

- has_circular_dependency：模块依赖图存在环状依赖→true（**一票否决项**）。

- module_count / standard_named_module_count / has_layered_directory / has_file_type_packages / has_base_layered_architecture / is_component_friendly：口径同 1.2 所列。

- 附加判断：业务分包结构是否存在；至少 2 个业务模块是否含职责分层目录；代码是否未存放于根包。

**强制约束**：先有唯一事实集合，评分与事实一致，禁止冲突性事实、禁止外部先验。

**评分标准**

- **Step 1 异常（0 分）**：has_circular_dependency=true → 直接 0 分

- **3 分 高度模块化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥2 ④至少 2 个业务模块包含职责分层目录 ⑤is_component_friendly=true

- **2 分 中等模块化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥1 ④存在业务分包结构

- **1 分 基础结构化**，满足任意 1 项：①has_layered_directory=true ②has_file_type_packages=true ③代码未存放于根包

- **0 分 无结构**：不满足以上所有条件

### 1.4 compilation.ci_independence（CI 独立性）｜满分 3｜compilation.ci_independence

**需要的评分信息**：检查 .github/workflows/、.gitlab-ci.yml、Jenkinsfile、azure-pipelines.yml、APP_BUILD 等 CI 配置文件是否存在及其内容。

**评分标准**

- **0 分**：无 CI（无任何 CI 配置文件）

- **1 分**：依赖安卓系统层 CI

- **2 分**：独立 CI 但非标准流水线

- **3 分**：完整标准化 CI/CD 流水线

**输出键**：ci_independence_score、ci_type、ci_configuration_files、ci_workflow_details、score_reasoning。

### 1.5 compilation.compilation_independence（编译独立性）｜满分 3｜compilation.compilation_independence

**需要的评分信息**：检查 build.gradle、pom.xml、package.json，评估模块化程度、依赖管理方式、构建独立性。

**评分标准**

- **0 分**：源码依赖（直接依赖源代码）

- **1 分**：依赖 framework.jar

- **2 分**：依赖 SDK/AAR

- **3 分**：带版本管理的稳定 SDK

**输出键**：compilation_modularity_score、dependency_type、build_configuration_files、dependency_analysis、score_reasoning。

### 1.6 compilation.api_version_management（API 版本管理）｜满分 3｜compilation.api_version_management

**需要的评分信息**：检查 version.properties、package.json version 字段等，评估版本控制成熟度与兼容性管理。

**评分标准**

- **0 分**：无版本管理

- **1 分**：手动版本不可控

- **2 分**：语义化版本

- **3 分**：版本可控 + 前后兼容

**输出键**：version_management_score、version_strategy、version_control_files、compatibility_analysis、score_reasoning。

### 1.7 platform_reuse.platform_upgrade（车机平台升级适配能力）｜满分 10｜platform_reuse.platform_upgrade

**强制约束（人工特别评估方法）**

1. 事实唯一性：先完成全局适配特征提取，生成唯一不可变更的事实集合，评分基于同一套事实。

2. 定向 Grep 模拟模式：仅扫描 src/main/java、src/main/kotlin、src/main/cpp、src/main/res、AndroidManifest.xml 及模块级 build.gradle/CMakeLists.txt；严格忽略 /test/、/androidTest/、/build/、/generated/、/third_party/；禁止逐行逐文件全量扫描，仅模式快照匹配。

3. 负向过滤：所有关键字/正则命中必须排除注释、字符串字面量、日志输出（Log.*）、测试 Mock 代码、IDE 自动生成代码；同类特征全局仅计 1 次状态，不做数量累加。

4. 权限边界：仅评估版本升级带来的适配成本，不评判合规性与风险等级。

5. 严格降级打分：按 10→8→3→0 依次判定，满足当前档即锁定，不再向下校验。

**需要的评分信息（7 个事实字段）**

- has_non_compatible_api：是否使用非兼容 API。客观定义=@hide 非公开 API、反射调用系统类（Class.forName/Method.invoke）、已废弃/移除 API、厂商私有 API。

- has_arch_specific_deps：是否依赖仅支持单一架构的闭源 SO（无 fallback 或多 ABI 打包）。

- version_bound_status（严格枚举 0-3，非行数统计）：版本绑定特征=Build.VERSION.SDK_INT、Build.VERSION_CODES，正则 `if\s*\(\s*Build\.VERSION\.SDK_INT\s*[><=]+\s*\d+`、`@RequiresApi\(api\s*=\s*Build\.VERSION_CODES\.\w+\)`、`@TargetApi\(\d+\)`；仅出现在业务逻辑控制流或 API 调用中才计命中。0=全局未命中或仅 @RequiresApi 等标准注解；1=仅存在于统一工具类/基类/单文件封装；2=2~3 个独立业务模块硬编码 if(SDK_INT)；3=核心链路（HAL/框架/启动流程）深度耦合版本逻辑。**出现在工具类/常量定义/统一兼容层→等级降级为 ≤1**。

- arch_bound_status（严格枚举 0-3）：架构绑定特征=Build.SUPPORTED_ABIS、Build.CPU_ABI、abiFilters、ndk.abiFilters、System.loadLibrary(、.so（仅与 loadLibrary 或 CMake add_library 相邻时）。0=未命中或已配置多 ABI；1=仅单模块 loadLibrary 且含 try-catch fallback；2=2~3 模块硬编码架构判断无统一策略抽象；3=依赖单架构闭源 SO 或底层强耦合 CPU_ABI 无兼容方案。字符串常量中的架构名（如 `String arch = "arm64";`）不计；**有 fallback 机制或多 ABI 打包→降级为 ≤1**。

- has_interface_abstraction：平台/架构逻辑是否用接口/抽象类/策略模式解耦隔离。

- has_light_permission_adaptation：仅轻量权限适配=仅需 AndroidManifest 声明权限、无业务代码修改。

- has_complex_permission_adaptation：复杂权限适配=蓝牙/存储/位置/通知权限在高版本需修改运行时逻辑（动态申请、分区存储适配、通知渠道创建等）。

- **豁免规则**：若版本/架构检查被 has_interface_abstraction=true 覆盖，或仅用于 @RequiresApi/兼容性封装层，强制将对应 status 降级为 ≤1。

**评分标准**（total_bound_status = version_bound_status + arch_bound_status，直接相加，范围 0~6）

- **10 分 极速适配**，满足任意 2 条：①has_non_compatible_api=false 且 has_arch_specific_deps=false ②total_bound_status≤1 ③has_interface_abstraction=true ④has_complex_permission_adaptation=false

- **8 分 快速适配**，满足任意 2 条：①has_non_compatible_api=false 且 has_arch_specific_deps=false ②total_bound_status≤3 ③has_light_permission_adaptation=true ④has_interface_abstraction=true

- **3 分 常规适配**，满足任意 1 条：①has_non_compatible_api=false 或 has_arch_specific_deps=false ②total_bound_status≤4 ③has_light_permission_adaptation=true ④has_interface_abstraction=true

- **0 分 难以适配（一票否决）**，满足任意 1 条：①has_non_compatible_api=true ②has_arch_specific_deps=true ③total_bound_status≥5 ④高版本权限逻辑硬编码耦合导致核心功能无法运行或无法兼容

### 1.8 platform_reuse.release_branch_strategy（Git 分支通用性）｜满分 10｜platform_reuse.branch_strategy

**需要的评分信息**：仓库真实分支列表；分支命名模式（SOP 分支的平台/车型后缀，如 _8295/_e04/-a1/-a2）；同版本下 SOP 分支数量；main/master 通用性（有无无后缀统一主干）。

**核心原则**：分支越统一分越高，拆分越细分越低。

**评分标准**

- **0 分**：无分支策略（无明确 release 分支规划）

- **3 分**：单车型单 SOP（一车型一分支，最细分）

- **8 分**：同平台同一分支（一平台一分支，平台内车型共用）

- **10 分**：跨平台同一分支（合一、无后缀统一主干）

**输出键**：score、score_reasoning、analysis、branch_analysis{sop_branch_count, main_branches, release_branches, has_unified_main, branch_pattern(single_vehicle|multi_vehicle|cross_platform|unified), version}。

⚠️ **benchmark 注意**：提示词「重要背景」中的分支名（origin/main_8295、main_e04、sop/flymeauto2.0.0.j1/q8295_p789 等）是示例，不是被测仓事实；提示词亦明言「目前不存在跨平台同一分支的项目，几乎不可能得 10 分」。定标准分必须以被测仓真实分支对照四档，禁止把示例分支当事实。

---

## 2. FW 子维度

### 2.1 architecture.componentization（组件化架构）｜满分 5｜architecture.scoring_embedded

适用对象：FW/QNX（C++）与 MCU（纯 C）嵌入式系统。

**需要的评分信息（先提取事实，再打分）**

- module_count：CMake 子目录数（add_subdirectory 调用数），不是简单目录数量。

- standard_named_module_count：分层标准命名模块数。命名规范=小写字母+下划线；匹配关键字 hal/bsp/driver/middleware/app/application/common/lib/shared/utils/core/base。

- has_layered_directory：存在职责分层目录。HAL 标识=hal/hardware/hal_driver/hardware_abstraction；BSP=bsp/board/board_support；驱动=driver/drivers/peripheral/device_driver；中间件=middleware/middleware_layer/service/services；应用=app/application/main_app/user_app；公共=common/common_lib/shared/utils/utility。任一存在→true。

- 基础文件组织（非职责分层）：目录标识=src/source/code/lib/inc/include/test/tests；仅有这些→「仅基础文件组织」。**基础文件组织 ≠ 职责分层架构**。

- has_base_layered_architecture：同时存在 HAL 层目录（hal/hardware）+ 应用层目录（app/application）。

- is_component_friendly：满足任意 ≥3 项→true：①无模块间循环 #include ②业务边界隔离、无跨模块直接访问私有数据 ③公共能力下沉至 common/lib 模块 ④模块可独立编译 ⑤无跨模块硬编码依赖（通过配置化或接口抽象）。

- has_interface_abstraction：存在函数指针表、回调函数、接口结构体（struct 包含函数指针）→true。

- build_system_type：cmake | makefile | makefile_cmake | other；total_source_files：.c/.h/.cpp/.hpp 总数。

**强制约束**：评分前生成唯一不可变更的架构事实集合；评分基于该集合，禁止冲突性事实；不引入外部先验。

**评分标准**

- **5 分 高级组件化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥3 ③standard_named_module_count≥3 ④is_component_friendly=true ⑤has_interface_abstraction=true

- **3 分 中等组件化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥2 ④存在分层目录结构（至少 2 层）

- **1 分 基础分层**，满足任意 1 项：①has_layered_directory=true ②module_count≥1 ③存在基本文件组织结构（src/inc 分离）

- **0 分 无结构**：不满足以上所有条件

**特别关注点**：FW/QNX（C++）看类封装硬件访问、RAII 与智能指针、模板在硬件抽象中的应用；MCU（纯 C）看函数指针表驱动接口（如 struct hal_gpio_ops）、回调事件通知、配置结构体参数化、头文件包含规范性。

### 2.2 architecture.decoupling（代码解耦）｜满分 3｜architecture.scoring_embedded

**需要的评分信息**（口径独立列出）

- module_count：CMake add_subdirectory 调用数；排除 test、tests、third_party、external、vendor。

- standard_named_module_count：小写+下划线命名、含关键字 hal/bsp/driver/middleware/app/application/common/lib/shared/utils/core/base 的模块数。

- has_layered_directory：HAL（hal/hardware/hal_driver/hardware_abstraction）/BSP（bsp/board/board_support）/驱动（driver/drivers/peripheral/device_driver）/中间件（middleware/middleware_layer/service/services）/应用（app/application/main_app/user_app）/公共（common/common_lib/shared/utils/utility）任一标识目录存在。

- has_base_layered_architecture：HAL 层目录 + 应用层目录同时存在。

- is_component_friendly：任意 ≥3 项：无循环 #include / 业务边界隔离无跨模块私有数据直访 / 公共能力下沉 common/lib / 模块可独立编译 / 无跨模块硬编码依赖。

- has_interface_abstraction：函数指针表、回调函数、接口结构体（struct 含函数指针）。

- 附加判断：是否存在跨模块直接访问全局变量（应通过接口或消息传递）；是否存在基本文件组织结构。

**强制约束**：先有唯一事实集合，评分与事实一致，禁止冲突性事实、禁止外部先验。

**评分标准**

- **3 分 优秀解耦**，满足任意 2 项：①has_base_layered_architecture=true ②is_component_friendly=true ③has_interface_abstraction=true ④无跨模块直接访问全局变量（通过接口或消息传递）

- **2 分 良好解耦**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥2 ④存在分层目录结构

- **1 分 基础解耦**，满足任意 1 项：①has_layered_directory=true ②module_count≥1 ③存在基本文件组织结构

- **0 分 未解耦**：不满足以上所有条件

**特别关注点**：同 2.1（C++ 看类封装/RAII/模板；MCU 看函数指针表/回调/配置结构体）。

### 2.3 architecture.modularization（模块化程度）｜满分 3｜architecture.scoring_embedded

**需要的评分信息**

- has_circular_dependency：模块间存在循环 #include 或循环链接依赖→true（**一票否决项**）。

- module_count：CMake add_subdirectory 调用数。

- standard_named_module_count / has_layered_directory / has_base_layered_architecture / is_component_friendly：口径同 2.2 所列。

- 附加判断：每个模块可否独立编译；是否存在分层目录结构（至少 2 层）；是否存在基本文件组织结构。

**强制约束**：先有唯一事实集合，评分与事实一致，禁止冲突性事实、禁止外部先验。

**评分标准**

- **Step 1 异常（0 分）**：has_circular_dependency=true → 直接 0 分

- **3 分 高度模块化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥3 ③standard_named_module_count≥3 ④is_component_friendly=true ⑤每个模块可独立编译

- **2 分 中等模块化**，满足任意 2 项：①has_base_layered_architecture=true ②module_count≥2 ③standard_named_module_count≥2 ④存在分层目录结构

- **1 分 基础结构化**，满足任意 1 项：①has_layered_directory=true ②module_count≥1 ③存在基本文件组织结构

- **0 分 无结构**：不满足以上所有条件

**特别关注点**：同 2.1。构建系统看 CMake 子目录组织、Makefile 模块化；模块独立性看每个模块可否独立编译和测试；公共能力看 common/lib 模块的管理和使用。

### 2.4 compilation.ci_independence（CI 独立性）｜满分 3｜compilation.ci_independence

与 APP 1.4 同一提示词，标准完全相同：检查 .github/workflows/、.gitlab-ci.yml、Jenkinsfile、azure-pipelines.yml、APP_BUILD；0 分=无 CI / 1 分=依赖系统层 CI / 2 分=独立但非标准流水线 / 3 分=完整标准化 CI/CD 流水线。

### 2.5 compilation.compilation_independence（编译独立性）｜满分 3｜compilation.independence_embedded

**需要的评分信息**：检查 CMakeLists.txt/*.cmake、Makefile/*.mk、Kconfig*、vcpkg.json/conanfile.txt/west.yml、project.yaml/package.xml。

关键检查点：add_subdirectory 指向外部路径=源码依赖；include 路径指向 bsp//sdk//hal/=BSP 头文件依赖；find_package(FreeRTOS)/FetchContent 引入第三方库=版本管理第三方库；find_package 带版本约束（如 Zephyr 3.5.0 REQUIRED）/vcpkg 版本锁定=稳定 SDK；.gitmodules 子模块版本标签、west.yml manifest 版本。

**评分标准**

- **0 分**：源码依赖（add_subdirectory/外部源码目录编译）

- **1 分**：BSP 头文件/静态库（target_include_directories 指向 BSP 路径）

- **2 分**：版本管理的第三方库（FreeRTOS/LWIP/CMSIS，git submodule/包管理器）

- **3 分**：稳定 SDK（版本号 + 兼容性说明）

### 2.6 compilation.api_version_management（API 版本管理）｜满分 3｜compilation.api_version_embedded

**需要的评分信息**，检查 5 组：

1. 头文件版本宏：include//api/ 目录中的 #define API_VERSION_MAJOR/MINOR/PATCH 或 <MODULE>_VERSION 宏。

2. CMake 版本：project(NAME VERSION x.y.z)、set(*_VERSION_*)、configure_file 生成版本头。

3. 版本记录文件：CHANGELOG、RELEASE_NOTES、VERSION 文件。

4. 兼容性条件编译：#if API_VERSION_MAJOR>=2 等版本兼容检查。

5. 自动化：git describe、version.cmake、version.h.in + configure_file。

**评分标准**

- **0 分**：头文件无版本号定义

- **1 分**：手动管理、无自动化

- **2 分**：语义化版本（版本宏定义齐全）

- **3 分**：版本宏 + 代码中版本兼容性检查（版本可控 + 兼容）

### 2.7 platform_coupling.system_api（平台专有 API 调用）｜满分 3｜platform_coupling.scoring_embedded

**评估对象**：代码对底层平台（QNX、RTOS、BSP）专有 API 的直接调用情况；耦合度越低分越高。

**平台专有 API 示例**：QNX=MsgSend*/MsgReceive*/resmgr_*/pulse_*/ChannelCreate/ConnectAttach；RTOS=xTaskCreate/xTaskCreatePinnedToCore/osMutex*/osSemaphore*/osThread*；BSP=BSP 专有初始化函数、硬件抽象层私有接口。

**需要的评分信息**：全扫 .c/.cpp/.h/.hpp；对平台专有 API 直接调用计数；识别是否存在平台适配层/抽象接口/封装模块（如 platform_adapter.c、os_wrapper.c）；重点评估业务逻辑模块而非测试/工具代码。

**评分标准**

- **3 分**：无直接调用、完全通过抽象层——所有平台操作经抽象接口或适配层完成，平台依赖封装在独立模块中，业务逻辑代码不含任何平台特定函数调用

- **2 分**：极少调用、仅在初始化阶段——调用 ≤5 处，集中在启动代码或配置模块，运行时业务逻辑不依赖平台专有 API

- **1 分**：已封装在适配层但存在少量直接调用——业务代码中仍有直接调用（5-15 处），适配层设计不完全、存在绕过

- **0 分**：大量直接调用——业务代码中 >15 处，无统一适配层或封装机制，平台依赖散布各模块、难以移植

**通用注意事项**：评分基于代码实际质量而非代码量；小型项目天然耦合低，但大型项目的良好封装更值得高分；有明确重构计划或 TODO 注释可酌情考虑。

### 2.8 platform_coupling.internal_non_standard_api（内部非规范 API 使用）｜满分 3｜platform_coupling.scoring_embedded

**评估对象**：对内部非规范 API 的使用——未公开接口、已废弃函数、内部命名约定函数。

**非规范 API 示例**：未公开头文件 `*_internal.h`/`*_private.h`/`*_impl.h`/`*_p.h`；deprecated 函数（`__attribute__((deprecated))`、QNX_DEPRECATED）；以 `_` 或 `__` 开头的内部函数；编译器特定扩展、非 POSIX 标准函数。

**需要的评分信息**：全扫 .c/.cpp/.h/.hpp；对上述非规范 API 使用计数；区分核心业务代码与测试/工具代码；检查是否有封装/抽象与迁移计划注释。

**评分标准**

- **3 分**：无内部非规范 API 使用——无内部头文件 #include、无 deprecated 调用、不调用 `_`/`__` 开头内部函数、仅用公开标准 API

- **2 分**：极少使用——≤3 处，集中在测试代码或工具代码，核心业务不依赖，有注释说明原因

- **1 分**：集中在适配层——3-10 处集中在适配层/封装模块，业务代码不直接使用，有适当封装抽象，存在向标准 API 迁移的计划或注释

- **0 分**：大量使用——业务代码 >10 处，无封装抽象，依赖未公开接口实现关键功能，或使用已废弃 API 且无替代方案

**通用注意事项**：同 2.7。

### 2.9 platform_coupling.ipc_interface_standardization（IPC 接口标准化）｜满分 3｜platform_coupling.scoring_embedded

**评估对象**：进程间通信接口的规范化程度——接口定义、版本管理、文档完整性。

**常见 IPC 机制**：QNX MsgSend/MsgReceive 消息传递、DBus、共享内存（shm_open/mmap）、消息队列（mq_open/msgget）、Socket（UNIX domain/TCP/UDP）。

**需要的评分信息**：识别所有 IPC 通信点；查找 IDL 定义文件（.idl、.dbus、.proto、.fbs）；查找版本号定义（如 INTERFACE_VERSION = "1.2.0"）；查找接口文档（接口描述、参数说明、错误码定义、使用示例）与版本兼容性说明。

**评分标准**

- **3 分**：全部标准化——所有 IPC 接口有 IDL 定义、每个接口有明确版本号、文档完整（描述/参数/错误码/示例）、接口变更有兼容性说明

- **2 分**：主要使用 IDL 定义——≥70% 接口有 IDL，版本号定义可能不够规范，文档基本完整（描述+参数说明），部分缺文档或版本

- **1 分**：少量未统一——30%-70% 接口有定义文件或文档，定义格式不统一（混用多种 IPC 机制），部分缺版本号，文档不完整（缺参数说明或错误码）

- **0 分**：无定义——无定义文件或文档，接口参数仅靠代码常量/宏定义，无版本管理，使用方式仅靠注释或口头约定

**通用注意事项**：同 2.7。

### 2.10 platform_reuse.platform_upgrade（RTOS 升级/芯片迁移适配能力）｜满分 10｜platform_reuse.platform_upgrade_embedded

**强制约束（与 APP 1.7 同构）**

1. 事实唯一性：先提取全局适配特征，生成唯一不可变更事实集合。

2. 定向 Grep 模拟模式：仅扫描源码与构建配置，忽略 test/external/vendor 等目录，禁止逐行全量扫描。

3. 负向过滤：命中须排除注释/字符串/日志/测试 Mock/生成代码；同类特征全局仅计 1 次状态。

4. 严格降级打分：10→8→3→0 依次判定，满足即锁定。

**需要的评分信息（7 个事实字段）**

- has_non_compatible_api：是否使用非兼容 API（平台私有/废弃/反射式调用）。

- has_arch_specific_deps：是否依赖仅支持单一芯片架构的闭源库（无 fallback）。

- rtos_bound_status（枚举 0-3）：RTOS 绑定特征=FreeRTOS xTaskCreate/vTaskDelay/xQueueSend/xSemaphoreTake、RT-Thread rt_thread_*、QNX MsgSend/MsgReceive/pulse_attach；已封装在统一抽象层（osTaskCreate 式）→≤1。0=无；1=仅封装层；2=多模块直调；3=核心链路深度绑定。

- bsp_bound_status（枚举 0-3）：BSP 绑定特征=BSP_Init/Board_Init/SystemInit/HAL_Init 及 `(BSP_|Board_|SystemInit|HAL_)\w+`；有 HAL/BSP 封装层→≤1。档位含义同上。

- hw_bound_status（枚举 0-3）：硬件直绑特征=寄存器直访 `*(volatile T*)0x…`、`#define X_REG 0x…`（仅驱动层计，HAL 封装→≤1）、中断 NVIC_*/`_IRQHandler`（有中断抽象层→≤1）、芯片宏 `STM32F\d+`/`CHIP_\w+` 及条件编译（有平台抽象层→≤1）。档位含义同上。

- has_interface_abstraction：平台逻辑是否经接口抽象解耦（函数指针表/适配层）。

- has_light_adaptation：轻量适配=仅改配置参数（时钟/引脚）。

- has_complex_adaptation：复杂适配=需改 RTOS 调用方式/中断逻辑/驱动架构。

- **豁免规则**：被接口抽象覆盖或仅在封装层的绑定特征，强制 status ≤1。

**评分标准**（判定流程与 APP 1.7 逐条对应，total = 各绑定 status 之和）

- **10 分 极速适配**，满足任意 2 条：①无非兼容 API 且无架构专属依赖 ②total≤1 ③has_interface_abstraction=true ④无复杂适配

- **8 分 快速适配**，满足任意 2 条：①同上① ②total≤3 ③轻量适配=true ④接口抽象=true

- **3 分 常规适配**，满足任意 1 条：①无非兼容 API 或无架构专属依赖 ②total≤4 ③轻量适配=true ④接口抽象=true

- **0 分 难以适配（一票否决）**，满足任意 1 条：①有非兼容 API ②有架构专属依赖 ③total≥5 ④硬件/权限逻辑硬编码耦合导致核心功能无法运行或无法兼容

### 2.11 platform_reuse.release_branch_strategy（Git 分支通用性）｜满分 10｜platform_reuse.branch_strategy

与 APP 1.8 同一提示词，标准完全相同：0 分=无分支策略 / 3 分=单车型单 SOP / 8 分=同平台同一分支 / 10 分=跨平台同一分支；以被测仓真实分支命名模式与数量定档；提示词中的示例分支名是背景示例非仓库事实，10 分几乎不可能。

### 2.12 quality.integration_test（集成测试）｜满分 3｜quality.integration_test_scoring_embedded

**需要的评分信息**，检查 4 组：

1. 测试框架存在性：CMakeLists.txt 是否引用 gtest/unity/cpputest/cmock；是否存在 test/、tests/、test_suite/ 目录；是否存在 *_test.c、*_test.cpp、test_*.c；是否存在 unity.h、gtest/gtest.h、CppUTest/Utest.h 的 #include。

2. Mock 框架使用：CMock（cmock.h、_Mock.c、Mock_*.h）、FFF（fff.h、FAKE_FUNCTION）、Google Mock（gmock/gmock.h、MOCK_METHOD）。

3. 测试覆盖率：测试文件数与模块文件数比值；模块间接口是否被覆盖；覆盖率配置（gcov、lcov、gcovr）。

4. CI 自动化：Jenkinsfile test stage、.github/workflows test job、.gitlab-ci.yml test stage、测试报告输出配置。

**评分标准**

- **0 分**：无集成测试或仅冒烟脚本——无任何测试框架引用，仅手工冒烟脚本（如 smoke_test.sh），无测试配置文件

- **1 分**：有集成测试、覆盖关键模块间接口——引用嵌入式测试框架（Unity/CppUTest/Google Test/CMock），测试文件覆盖 HAL↔中间件、driver↔app 等关键模块间接口，测试用例 ≥5 个

- **2 分**：目标明确、主要模块交互覆盖 ≥50%——框架配置完整（CMake add_test() 或 Unity 配置），主要模块间交互覆盖率 ≥50%，通过率 ≥80%，使用 Mock 框架（CMock/FFF）隔离部分依赖

- **3 分**：完整集成测试——通过率 100%、覆盖率 >80%、Mock 框架完善隔离外部依赖、CI 自动化测试流水线（Jenkins/GitHub Actions/GitLab CI）、测试报告自动生成

**输出键**：score、max_score、test_framework、mock_framework、test_file_count、coverage_estimate、ci_automation、score_reasoning、analysis。

### 2.13–2.17 solid_principle（SOLID 五原则，各自独立打分，各满分 4）｜solid.scoring

**2.13 single_responsibility（单一职责 SRP）**：模块/类/函数职责是否单一，有无上帝类、职责混杂。

**2.14 open_closed（开闭原则 OCP）**：是否对扩展开放、对修改关闭，扩展点与抽象设计是否合理。

**2.15 liskov_substitution（里氏替换 LSP）**：继承关系是否正确，子类能否恰当替换基类。

**2.16 interface_segregation（接口隔离 ISP）**：接口是否职责聚焦，有无依赖不必要的接口。

**2.17 dependency_inversion（依赖倒置 DIP）**：是否依赖抽象，有无直接依赖具体实现。

五原则共用同一套分档标准（对每个原则独立适用），评分需结合汽车领域软件开发实践；对每个原则分别分析：①代码中对该原则的遵循情况 ②是否存在违反该原则的设计 ③相关设计（职责/扩展点/继承关系/接口/依赖）是否合理 ④是否符合汽车领域可靠性、可维护性要求：

- **0 分**：严重违反该原则，存在明显设计缺陷

- **1 分**：多处违反该原则，代码设计不合理

- **2 分**：基本遵循该原则，但有少量改进空间

- **3 分**：良好遵循该原则，符合汽车领域软件开发规范

- **4 分**：优秀遵循该原则，体现汽车领域软件开发优秀实践

**输出键**（每个原则）：{score, score_reasoning, analysis, issues, recommendations}。

---

## 3. 特别评估方法汇总（benchmark 定分必读）

1. **档内「任意 N 条满足」机制**：architecture 全系、platform_upgrade 全系——逐档数条件命中数，满足即锁定该档。

2. **锁定流程 10→8→3→0**：platform_upgrade 系从高分向低分判，命中即停，禁止继续向下校验。

3. **事实唯一性原则**：architecture、platform_upgrade 系先出事实集，评分必须与事实自洽；事实与评分矛盾即为错分。

4. **豁免/降级规则**：绑定特征若已被接口/基类/适配层封装→对应 status 强制 ≤1。

5. **负向过滤**：注释/字符串/日志/测试 Mock/IDE 生成代码中的命中不计；同类特征全局计 1 次状态、不累加数量。

6. **严格枚举 0-3**：status 是等级枚举，不是行数统计。

7. **branch_strategy 示例分支非事实**：提示词背景中的分支名仅为示例；以真实分支定档；10 分几乎不可能（先验）。

8. **文件类型分包 ≠ 职责分层**（APP）；**基础文件组织 ≠ 职责分层**（FW）——仅 activity/fragment/utils 或仅 src/inc 不能拿分层档，只能进 1 分档。

9. **模块化一票否决**：循环依赖（模块依赖环 / 循环 #include）→ modularization 直接 0 分。

10. **接口抽象识别口径**：APP 看接口/抽象类/策略模式；FW 看函数指针表/回调/接口结构体（含函数指针的 struct）。

11. **耦合度计数阈值**：system_api 以 ≤5 / 5-15 / >15 处定档；internal_non_standard_api 以 ≤3 / 3-10 / >10 处定档；评分基于质量而非代码量，大项目良好封装更值得高分。

12. **输出契约**：全部纯 JSON、无 markdown 包裹、一次性完整返回（benchmark 可据此校验被测系统输出形态）。