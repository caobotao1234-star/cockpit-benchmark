# Cockpit Benchmark Manifest

Status: **FINAL CANDIDATE**

| Metric | Current | Target |
|---|---:|---:|
| APP repositories | 20 | 20 |
| FRAMEWORK repositories | 20 | 20 |
| Deterministically verified | 40 | 40 |
| Blind calibrated | 23 | 40 |

## Registered repositories

| ID | Repository | Kind | Tier | Size band | Source files | Source LOC | Modules | Build | First known issue |
|---|---|---|---|---|---:|---:|---:|---|---|
| APP-01 | `aurora-settings` | APP | high | large | 1,443 | 106,170 | 4 | Gradle | 依赖 AAOS SettingsLib、car-lib、系统/隐藏 API 与资源，完整构建需要产品树。 |
| APP-02 | `horizon-launcher` | APP | high | medium | 412 | 36,268 | 8 | Soong | 完整构建依赖 AAOS Launcher/SystemUI/WindowManager 隐藏和系统 API，只声明 a... |
| APP-03 | `climatix-hvac` | APP | high | small | 222 | 10,774 | 7 | Gradle | ServiceManager 通过 vehicle-api 内单一反射适配器访问，运行仍要求系统权限与平台服务。 |
| APP-04 | `wave-media` | APP | high | small | 174 | 10,037 | 4 | Gradle | 完整 APP 仍依赖未随仓交付的 AAOS UI/common 库、android.car 和隐藏 API，只声明 a... |
| APP-05 | `link-phone` | APP | high | medium | 394 | 33,507 | 7 | Gradle | 完整 Gradle 图仍依赖 AAOS car-* 库、Hilt 与平台 Telecom/CarService。 |
| APP-06 | `navpilot` | APP | high | large | 1,362 | 102,866 | 19 | Gradle | 完整 Car App/SystemUI/CarService 产品仍需要 AAOS 平台 SDK、资源和隐藏 API 输入。 |
| APP-07 | `id-hub` | APP | high | small | 222 | 10,552 | 6 | Gradle | 完整 Android instrumentation 仍需要设备/模拟器；本轮只静态编译 app service 边界... |
| APP-08 | `echo-voice` | APP | medium | medium | 430 | 38,617 | 7 | Gradle | VoiceCommandRouter 与 PlatformPhraseOverrides 仍包含集中式规则和平台条件。 |
| APP-09 | `prism-cluster` | APP | medium | medium | 648 | 40,309 | 11 | Soong | MainClusterActivity 继续承担显示、导航、输入、电话和信号绑定，并注册未持有引用的广播接收器。 |
| APP-10 | `vehicle-insight` | APP | medium | medium | 379 | 43,032 | 3 | Gradle | CarManager 集中管理多个 property subject，使用 unchecked value cast ... |
| APP-11 | `motion-control` | APP | medium | medium | 410 | 46,142 | 11 | Gradle | MotionBinderService 未接入实时 moving/occupant context，安全策略以固定 f... |
| APP-12 | `orbit-ota` | APP | medium | medium | 771 | 49,243 | 4 | Gradle | 四模块共享 Settings 资源目录，source ownership 在 policy/compat 间存在重叠。 |
| APP-13 | `market-hub` | APP | medium | small | 264 | 21,482 | 11 | Gradle | MarketActivity 只提供 catalog 入口，尚未连接完整筛选/详情/下载 UI。 |
| APP-14 | `cockpit-shell` | APP | medium | large | 1,267 | 121,978 | 18 | Soong | 多产品源在同一 Soong 闭包中保留各自入口，组合层集成测试不覆盖完整启动顺序。 |
| APP-15 | `atlas-settings` | APP | low | large | 1,331 | 101,808 | 4 | Gradle | LegacySettingsRuntime 是 Context 单例，反射 ServiceManager/任意方法并重... |
| APP-16 | `nova-launcher` | APP | low | medium | 513 | 40,967 | 9 | Soong | VendorLauncherRuntime 以 Context 单例反射 ServiceManager/SystemP... |
| APP-17 | `thermo-control` | APP | low | small | 166 | 11,981 | 2 | Gradle | ClimateCenterActivity 聚合 UI、状态、诊断、车辆控制和生命周期职责。 |
| APP-18 | `stream-media` | APP | low | small | 180 | 10,016 | 5 | Gradle | GlobalVehicleMediaHub 是 Context 进程级单例并聚合 media/audio/phone/... |
| APP-19 | `companion-voice` | APP | low | medium | 421 | 43,262 | 12 | Gradle | VoiceGlobalState 暴露 mutable static session/callback/executo... |
| APP-20 | `drive-center` | APP | low | large | 1,030 | 111,095 | 10 | Gradle | IDriveCenterFacade 以 String/Bundle 聚合十二个业务域，权限、类型与错误语义无法按域隔离。 |
| FW-01 | `car-api-core` | FRAMEWORK | high | large | 1,622 | 216,059 | 41 | Soong | 完整构建需要 AAOS Soong/HAL/系统库。 |
| FW-02 | `vehicle-property-service` | FRAMEWORK | high | small | 271 | 51,791 | 5 | Soong | 依赖 AOSP 私有平台 API 和车辆 HAL，不能作为普通 Java/Gradle 工程独立构建。 |
| FW-03 | `vehicle-hal-adapter` | FRAMEWORK | high | medium | 632 | 103,426 | 7 | Soong | 依赖完整 AAOS/AOSP 平台类型与 Soong 产品树，未声明普通 SDK 独立构建。 |
| FW-04 | `cockpit-audio-service` | FRAMEWORK | high | small | 262 | 38,637 | 5 | Soong | 完整服务依赖 AAOS 平台 API、audio-control HAL、生成资源与系统静态库，只声明 aosp_re... |
| FW-05 | `car-power-service` | FRAMEWORK | high | large | 1,619 | 215,870 | 41 | Soong | 完整 Java/C++ 产品构建需要 AAOS Soong 与 power HAL。 |
| FW-06 | `occupant-zone-service` | FRAMEWORK | high | medium | 673 | 139,008 | 18 | Soong | 完整服务依赖 AAOS UserManager、display/occupant 配置与 VHAL。 |
| FW-07 | `vehicle-diagnostics` | FRAMEWORK | high | large | 2,019 | 230,955 | 42 | Soong | 完整 native/Java 诊断产品构建需要 AAOS、VHAL、statsd/watchdog 和生成 proto... |
| FW-08 | `soa-gateway` | FRAMEWORK | medium | medium | 606 | 97,493 | 3 | Gradle | soa-service Gradle module 仍覆盖完整 CarService source，职责和依赖面显著大... |
| FW-09 | `vendor-signal-service` | FRAMEWORK | medium | medium | 639 | 103,443 | 8 | Soong | 新增 VendorSignalNormalization 无专门测试。 |
| FW-10 | `cockpit-manager-kit` | FRAMEWORK | medium | small | 282 | 51,721 | 4 | Gradle | IManagerGateway 以 manager/operation 字符串和 Bundle 承载跨域调用，契约粒度... |
| FW-11 | `hvac-binder-service` | FRAMEWORK | medium | medium | 677 | 82,119 | 14 | Soong | HvacBinderService.execute 未接入实时 vehicle-moving context，驾驶限制... |
| FW-12 | `media-routing-service` | FRAMEWORK | medium | medium | 694 | 86,581 | 14 | Gradle | createRoute 为 synchronized 且在锁内执行 RemoteCallbackList 广播，慢 c... |
| FW-13 | `projection-service` | FRAMEWORK | medium | medium | 734 | 91,835 | 14 | Soong | connect() 持有 service monitor 时执行 transport open 与远端 callbac... |
| FW-14 | `update-manager-service` | FRAMEWORK | medium | large | 1,613 | 213,289 | 40 | Soong | 完整 service/car-lib/test closure 远宽于 update manager 业务，增加探索与... |
| FW-15 | `car-runtime-service` | FRAMEWORK | low | small | 342 | 41,407 | 5 | Soong | ICarRuntime 将 18 个领域的 54 个方法放入同一 Binder 契约，接口隔离不足。 |
| FW-16 | `platform-compat-service` | FRAMEWORK | low | large | 1,979 | 246,978 | 51 | Soong | IPlatformCompat 以 Bundle invoke/rawService 聚合 vehicle/audio... |
| FW-17 | `binder-hub-service` | FRAMEWORK | low | small | 263 | 37,015 | 6 | Soong | ICockpitServiceHub 通过 Bundle invoke 聚合四域，契约缺少版本化错误、细粒度权限和类型... |
| FW-18 | `vehicle-platform-service` | FRAMEWORK | low | medium | 836 | 88,725 | 3 | Soong | 旧平台与现代迁移树产生 4 组完全重复、6 对 0.80 阈值近重复及多个同语义双栈类。 |
| FW-19 | `can-middleware` | FRAMEWORK | low | medium | 767 | 93,357 | 16 | Gradle | 8155/8295 各 20 个 decoder 保留高比例复制，修复与 signal mapping 需双侧同步。 |
| FW-20 | `system-service-facade` | FRAMEWORK | low | large | 1,613 | 213,136 | 39 | Soong | ICarImpl 反向 import facade，而 facade 以 Object/反射持有 CarService... |

The machine-readable source of truth is `manifest.json`. Ground-truth files under `oracle/`
must not be supplied to the evaluation Agent.
