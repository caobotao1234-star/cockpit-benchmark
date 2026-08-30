# G5 blind anchor review worklist

Coordinator-only bounded excerpts. This file is evidence input, not the final human acceptance record.
Every selected anchor is read from the exact manifest HEAD or its declared local branch.

## APP-05

- Blind ID: `blind-64c0fd8fd870`
- HEAD: `e4537531ded2613e49b369bd241fe431c3155ed4`
- Tier / blind mean: `high` / `1.875`
- Exploration: 277 files, 64 directories, 20 tool calls, 256.247 seconds, truncated=false

### solid = 2

- Path/ref: `src/com/android/car/dialer/telecom/ProjectionCallHandler.java` / `HEAD`
- Symbol: `lines 64-75, 211-212` (locator `declared_line`)
- Observation: 生产构造器委托给可注入的 CarProjectionManagerProvider，使平台管理器可被替换测试。

```text
   62:     private List<ProjectionStatus> mProjectionDetails = Collections.emptyList();
   63: 
   64:     @Inject
   65:     ProjectionCallHandler(@ApplicationContext Context context, TelecomManager telecomManager) {
   66:         this(context, telecomManager,
   67:                 car -> (CarProjectionManager) car.getCarManager(Car.PROJECTION_SERVICE));
```

### architecture = 1

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `line 4` (locator `declared_line`)
- Observation: 声明 framework、testing、voice-assist、platform-services、link-runtime、link-tests 六个顶层模块。

```text
    2: dependencyResolutionManagement { repositories { google(); mavenCentral() } }
    3: rootProject.name="LinkPhone"
    4: include(":framework",":testing",":voice-assist",":platform-services",":link-runtime",":link-tests")
```

## APP-06

- Blind ID: `blind-897981a4cf01`
- HEAD: `0793e20235ec761a1b42b7454e8771794d660a04`
- Tier / blind mean: `high` / `1.777778`
- Exploration: 55 files, 28 directories, 21 tool calls, 245.962 seconds, truncated=false

### solid = 2

- Path/ref: `launcher-shell/libs/appgrid/lib/src/com/android/car/carlauncher/repositories/AppGridRepository.kt` / `HEAD`
- Symbol: `AppGridRepositoryImpl constructor, lines 107-120` (locator `declared_line`)
- Observation: 仓库实现依赖多个细粒度 DataSource、工厂、PackageManager 和 CoroutineDispatcher，均由构造函数注入。

```text
  105:  * *  Providing real-time updates of the app grid as changes occur.
  106:  */
  107: class AppGridRepositoryImpl(
  108:     private val launcherActivities: LauncherActivitiesDataSource,
  109:     private val mediaTemplateApps: MediaTemplateAppsDataSource,
  110:     private val disabledApps: DisabledAppsDataSource,
```

### architecture = 1

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `lines 4-6` (locator `declared_line`)
- Observation: 声明应用样例、cluster-ui、system-shell、launcher-shell、voice-guidance、navigation-platform、nav-runtime 和 nav-tests 等模块。

```text
    2: dependencyResolutionManagement { repositories { google(); mavenCentral() } }
    3: rootProject.name="NavPilot"
    4: include(":car_app_library:navigation:automotive",":car_app_library:navigation:common",":car_app_library:navigation:mobile")
    5: include(":car_app_library:showcase:automotive",":car_app_library:showcase:common",":car_app_library:showcase:mobile")
    6: include(":car-lib:CarGearViewerKotlin:automotive",":cluster-ui",":system-shell",":launcher-shell",":voice-guidance",":navigation-platform",":nav-runtime",":nav-tests")
```

## APP-07

- Blind ID: `blind-9a8df941e552`
- HEAD: `2c664340f515e34f31a1c05b0be9c804eae698bb`
- Tier / blind mean: `high` / `1.888889`
- Exploration: 99 files, 18 directories, 16 tool calls, 232.568 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `product/platform.properties` / `platform/8155`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: 8155 分支只声明 sa8155 与 legacy keystore。

```text
    1: identity.platform=sa8155
    2: identity.keystore=legacy
```

### aidl_sdk_call = 1

- Path/ref: `identity-api/src/main/aidl/com/cockpitbench/idhub/api/IIdentityService.aidl` / `HEAD`
- Symbol: `IIdentityService, line 9` (locator `declared_line`)
- Observation: 提供类型化认证、登出和监听器注册接口，但没有显式错误模型、版本协商或异步执行语义。

```text
    7: import com.cockpitbench.idhub.api.IIdentityListener;
    8: import com.cockpitbench.idhub.api.RoleAssignment;
    9: interface IIdentityService { IdentityAccount getActiveAccount(int userId); AuthResult authenticate(in AuthRequest request); void signOut(String sessionId); void registerListener(IIdentityListener listener); void unregisterListener(IIdentityListener listener); }
```

## APP-10

- Blind ID: `blind-54da785c4fb2`
- HEAD: `0ad37f52f83e7bbcbb1a005dc930f320c0d6c54e`
- Tier / blind mean: `medium` / `2.111111`
- Exploration: 259 files, 52 directories, 20 tool calls, 317.233 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `vehicle-platform/upstream/service/src/com/android/car/hal/HalPropConfig.java` / `HEAD`
- Symbol: `HalPropConfig, lines 29-169` (locator `declared_line`)
- Observation: 统一抽象承载属性配置读取和到 CarPropertyConfig 的完整公共映射，AIDL/HIDL 后端复用同一策略。

```text
   27:  * HalPropConfig represents a vehicle property config.
   28:  */
   29: public abstract class HalPropConfig {
   30: 
   31:     private static final int[] DEFAULT_AREA_IDS = {VehicleAreaType.VEHICLE_AREA_TYPE_GLOBAL};
   32: 
```

### hidden_api_reflection = 1

- Path/ref: `car-ui-lib/src/main/java/com/android/car/ui/utils/CarUiUtils.java` / `HEAD`
- Symbol: `readSystemProperty, lines 279-304` (locator `declared_line`)
- Observation: 隐藏 SystemProperties 访问被局部封装，并对类、方法或调用失败记录日志后返回 null。

```text
  277:     }
  278: 
  279:     @Nullable
  280:     private static String readSystemProperty(String propertyName) {
  281:         Class<?> systemPropertiesClass;
  282:         try {
```

## APP-11

- Blind ID: `blind-e8f750fa009b`
- HEAD: `0ecc89a31ed4f6cecad8c6690f56862a07e78d57`
- Tier / blind mean: `medium` / `1.555556`
- Exploration: 414 files, 28 directories, 17 tool calls, 254.246 seconds, truncated=false

### architecture = 2

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `lines 1-4` (locator `declared_line`)
- Observation: 显式声明 11 个 foundation、motion API/core/platform/app/test 模块。

```text
    1: rootProject.name='CockpitAppFoundation'
    2: include ':foundation-api', ':foundation-core', ':foundation-platform', ':foundation-storage', ':foundation-observability', ':foundation-testkit'
    3: 
    4: include ':motion-api', ':motion-core', ':motion-platform', ':motion-app', ':motion-tests'
```

### aidl_sdk_call = 1

- Path/ref: `motion-api/src/main/aidl/com/cockpitbench/motion/IMotionControl.aidl` / `HEAD`
- Symbol: `line 3` (locator `declared_line`)
- Observation: 提供 typed capability/state/command、场景和回调注册接口，但 execute/applyScene 为无返回值同步调用。

```text
    1: package com.cockpitbench.motion;
    2: import com.cockpitbench.motion.MotionCommand; import com.cockpitbench.motion.MotionState; import com.cockpitbench.motion.ActuatorCapability; import com.cockpitbench.motion.IMotionCallback;
    3: interface IMotionControl { List<ActuatorCapability> capabilities(int zoneId); MotionState state(String actuatorId); void execute(in MotionCommand command); void applyScene(String sceneId, int zoneId); void registerCallback(IMotionCallback callback); void unregisterCallback(IMotionCallback callback); }
```

## APP-12

- Blind ID: `blind-b321d769a45e`
- HEAD: `19f223c96217e89918a40fa6847fa6de2d87808a`
- Tier / blind mean: `medium` / `1.555556`
- Exploration: 215 files, 24 directories, 22 tool calls, 274.245 seconds, truncated=false

### solid = 2

- Path/ref: `settings-platform/upstream/src/com/android/car/settings/common/PreferenceController.java` / `HEAD`
- Symbol: `class and lifecycle dispatch, lines 93-95, 221-264, 271-353` (locator `declared_line`)
- Observation: 抽象控制器以 final 生命周期调度、类型检查和可覆盖钩子约束扩展行为。

```text
   91:  *            expects to operate.
   92:  */
   93: public abstract class PreferenceController<V extends Preference> implements
   94:         DefaultLifecycleObserver,
   95:         OnUxRestrictionsChangedListener {
   96: 
```

### architecture = 1

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: 声明 updater-app、update-policy、settings-compat、update-tests 四个模块。

```text
    1: rootProject.name='OrbitOta'
    2: include ':updater-app', ':update-policy', ':settings-compat', ':update-tests'
```

## APP-13

- Blind ID: `blind-62fcf0e17219`
- HEAD: `3f421d00c591dc47b7de81f77292aa512eb34992`
- Tier / blind mean: `medium` / `1.75`
- Exploration: 78 files, 28 directories, 18 tool calls, 231.761 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `product/platform.properties` / `platform/8155`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: 8155 差异集中为 market.platform=sa8155 与 market.installer=legacy。

```text
    1: market.platform=sa8155
    2: market.installer=legacy
```

### aidl_sdk_call = 1

- Path/ref: `foundation-api/src/main/aidl/com/cockpitbench/foundation/api/ICockpitGateway.aidl` / `HEAD`
- Symbol: `ICockpitGateway, line 3` (locator `declared_line`)
- Observation: execute 以 domain、operation 字符串和 Bundle 承载任意操作，契约粒度粗且缺少类型化错误。

```text
    1: package com.cockpitbench.foundation.api;
    2: import com.cockpitbench.foundation.api.ICockpitEventListener;
    3: interface ICockpitGateway { android.os.Bundle execute(String domain, String operation, in android.os.Bundle arguments); void registerListener(String domain, ICockpitEventListener listener); void unregisterListener(ICockpitEventListener listener); }
```

## APP-14

- Blind ID: `blind-fd7c14d2f1c0`
- HEAD: `bf4a421f8084c139e4ea097d4256e9394008dd8e`
- Tier / blind mean: `medium` / `2.111111`
- Exploration: 48 files, 33 directories, 22 tool calls, 293.973 seconds, truncated=false

### aidl_sdk_call = 3

- Path/ref: `platform/services-car/car-lib/src/android/car/watchdog/ICarWatchdogService.aidl` / `HEAD`
- Symbol: `ICarWatchdogService，27-58 行` (locator `token:ICarWatchdogService`)
- Observation: 合约区分客户端健康检查、资源统计、监听器和配置操作，并明确说明哪些调用因调用方 PID/UID 语义不能使用 oneway。

```text
   17: package android.car.watchdog;
   18: 
   19: import android.car.watchdog.ICarWatchdogServiceCallback;
   20: import android.car.watchdog.IResourceOveruseListener;
   21: import android.car.watchdog.PackageKillableState;
   22: import android.car.watchdog.ResourceOveruseConfiguration;
```

### hidden_api_reflection = 1

- Path/ref: `src/com/android/systemui/car/window/SystemUIOverlayWindowManager.java` / `HEAD`
- Symbol: `startServices 与 resolve，61-98 行` (locator `token:startServices`)
- Observation: 优先使用 Dagger provider map 是积极边界，但随后以 Class.forName/构造器回退；多种反射异常被包装为 RuntimeException，且未捕获参数类型错误。

```text
   56:         String[] names = mContext.getResources().getStringArray(
   57:                 R.array.config_carSystemUIOverlayViewsMediators);
   58:         startServices(names);
   59:     }
   60: 
   61:     private void startServices(String[] services) {
```

## APP-19

- Blind ID: `blind-78bb4145b9bf`
- HEAD: `890487cb6e20114d92aadd509c7c5d6797039dbf`
- Tier / blind mean: `low` / `1.0`
- Exploration: 426 files, 29 directories, 19 tool calls, 258.848 seconds, truncated=false

### release_branch_strategy = 2

- Path/ref: `product/release.properties` / `release/2026.1`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: The release-only change freezes voice.channel and voice.contract in a two-line configuration file; the branch commit also carries tag companion-voice-2026.1.

```text
    1: voice.channel=sop-2026.1
    2: voice.contract=3
```

### code_duplication = 0

- Path/ref: `voice-platform-8155/src/main/java/com/cockpitbench/voice/platform/p8155/VoiceProvider0.java` / `HEAD`
- Symbol: `lines 18-43, VoiceProvider0` (locator `declared_line`)
- Observation: Implements the same enrich/supports/generation/platform/providerId/timestamp template repeated throughout the 8155 family.

```text
   16: package com.cockpitbench.voice.platform.p8155;
   17: import android.os.Bundle;
   18: public final class VoiceProvider0 {
   19:     private static final int BASE = 100;
   20:     public void enrich(Bundle result) {
   21:         String domain = result.getString("domain", "unknown");
```

## APP-20

- Blind ID: `blind-444bc3ea2815`
- HEAD: `c6f4a1efa1836f9181742740e6e8b32caf962eb2`
- Tier / blind mean: `low` / `1.0`
- Exploration: 64 files, 34 directories, 23 tool calls, 405.753 seconds, truncated=false

### integration_testing = 2

- Path/ref: `tests/carservice_unit_test/src/com/android/car/power/CarPowerManagementServiceUnitTest.java` / `HEAD`
- Symbol: `setUp()/setService() and tests at lines 153-373` (locator `declared_line`)
- Observation: 使用模拟 Power HAL、可替换 SystemInterface 与等待式断言覆盖开机、关机、休眠、立即执行和取消等跨组件状态迁移。

```text
  151:     }
  152: 
  153:     @Before
  154:     public void setUp() throws Exception {
  155:         mPowerHal = new MockedPowerHalService(/*isPowerStateSupported=*/true,
  156:                 /*isDeepSleepAllowed=*/true,
```

### hidden_api_reflection = 0

- Path/ref: `drive-runtime/src/main/java/com/cockpitbench/drivecenter/PlatformAdapterRegistry.java` / `HEAD`
- Symbol: `PlatformAdapterRegistry.get(), lines 8-20` (locator `declared_line`)
- Observation: 类名由平台和未验证的 domain 字符串拼接后通过 Class.forName 实例化，所有异常静默转换为 null。

```text
    6:     private static String activePlatform = "8155";
    7:     public PlatformAdapterRegistry(String platform) { activePlatform = platform == null ? "8155" : platform; }
    8:     public DomainAdapter get(String domain) {
    9:         DomainAdapter cached = ADAPTERS.get(domain);
   10:         if (cached != null) return cached;
   11:         String prefix = "8295".equals(activePlatform)
```

## FW-05

- Blind ID: `blind-e13e93358b13`
- HEAD: `75743bb11957ac8d69ed010618dded632061f50d`
- Tier / blind mean: `high` / `2.444444`
- Exploration: 508 files, 31 directories, 23 tool calls, 265.347 seconds, truncated=false

### aidl_sdk_call = 3

- Path/ref: `car-lib/src/android/car/hardware/power/ICarPower.aidl` / `HEAD`
- Symbol: `ICarPower, lines 24-50` (locator `declared_line`)
- Observation: 合同分离监听器注册、完成确认、状态查询、策略应用及过滤回调，没有暴露无类型命令通道。

```text
   22: import android.car.hardware.power.ICarPowerStateListener;
   23: 
   24: /** @hide */
   25: interface ICarPower {
   26:     void registerListener(in ICarPowerStateListener listener);
   27: 
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `lines 3-30, CarPowerApiBoundary / CarPowerServiceBoundary / CarPowerBoundaryTests` (locator `declared_line`)
- Observation: 顶层构建明确区分 API、服务和测试边界，服务静态依赖 API。

```text
    1: package { default_applicable_licenses: ["Android-Apache-2.0"] }
    2: 
    3: java_library {
    4:     name: "CarPowerApiBoundary",
    5:     srcs: [
    6:         "car-lib/src/android/car/hardware/power/**/*.java",
```

## FW-06

- Blind ID: `blind-782b96660b4f`
- HEAD: `54d2aa88b2a105feee961ace11be504fca8a08df`
- Tier / blind mean: `high` / `2.222222`
- Exploration: 51 files, 25 directories, 20 tool calls, 207.316 seconds, truncated=false

### integration_testing = 3

- Path/ref: `tests/carservice_test/src/com/android/car/vms/VmsClientTest.java` / `HEAD`
- Symbol: `setUpTest() and registration tests, lines 97-139` (locator `declared_line`)
- Observation: 通过真实 Car manager 连接 VMS，验证多个客户端之间的当前 layer/subscription 状态及异步回调。

```text
   95:     private VmsClientManager mClientManager;
   96: 
   97:     @Before
   98:     public void setUpTest() {
   99:         mClientManager = (VmsClientManager) getCar().getCarManager(Car.VEHICLE_MAP_SERVICE);
  100:         LARGE_PAYLOAD[0] = 123;
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `lines 3-32, OccupantZoneApiBoundary / OccupantZoneServiceBoundary / OccupantZoneBoundaryTests` (locator `declared_line`)
- Observation: 构建定义显式区分 API、服务实现和测试，并保持单向静态依赖。

```text
    1: package { default_applicable_licenses: ["Android-Apache-2.0"] }
    2: 
    3: java_library {
    4:     name: "OccupantZoneApiBoundary",
    5:     srcs: [
    6:         "car-lib/src/android/car/*Occupant*.java",
```

## FW-07

- Blind ID: `blind-d87ab577ddcb`
- HEAD: `a0897a82ce7b27bfcfe28f07242669fd513ca9eb`
- Tier / blind mean: `high` / `2.444444`
- Exploration: 43 files, 31 directories, 22 tool calls, 215.207 seconds, truncated=false

### aidl_sdk_call = 3

- Path/ref: `car-lib/src/android/car/vms/IVmsBrokerService.aidl` / `HEAD`
- Symbol: `IVmsBrokerService methods 0-8` (locator `token:IVmsBrokerService`)
- Observation: 契约按客户端、订阅者和发布者操作分组，使用显式事务编号，并为大包提供 SharedMemory 边界。

```text
   30:  * @hide
   31:  */
   32: interface IVmsBrokerService {
   33:     // Client operations
   34:     // Restricted to callers with android.car.permission.VMS_SUBSCRIBER
   35:     // or android.car.permission.VMS_PUBLISHER
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `VehicleDiagnosticsApiBoundary / VehicleDiagnosticsServiceBoundary / VehicleDiagnosticsBoundaryTests` (locator `token:VehicleDiagnosticsServiceBoundary`)
- Observation: 构建入口按 API、服务实现和测试形成单向静态依赖。

```text
   17: 
   18: android_library {
   19:     name: "VehicleDiagnosticsServiceBoundary",
   20:     srcs: [
   21:         "service/src/com/android/car/CarDiagnosticService.java",
   22:         "service/src/com/android/car/telemetry/**/*.java",
```

## FW-08

- Blind ID: `blind-6a96cb943408`
- HEAD: `d793dd6d3164dff8ce75e3cab2e73cb96fe2063a`
- Tier / blind mean: `medium` / `2.222222`
- Exploration: 459 files, 74 directories, 20 tool calls, 289.87 seconds, truncated=false

### aidl_sdk_call = 3

- Path/ref: `car-lib/src/android/car/vms/IVmsBrokerService.aidl` / `HEAD`
- Symbol: `IVmsBrokerService，lines 32-77` (locator `declared_line`)
- Observation: 契约将注册、订阅、provider、普通包和大包操作分离，并为方法保留稳定事务编号。

```text
   30:  * @hide
   31:  */
   32: interface IVmsBrokerService {
   33:     // Client operations
   34:     // Restricted to callers with android.car.permission.VMS_SUBSCRIBER
   35:     // or android.car.permission.VMS_PUBLISHER
```

### architecture = 2

- Path/ref: `service/src/com/android/car/vms/VmsBrokerService.java` / `HEAD`
- Symbol: `VmsBrokerService，lines 64-89, 130-228` (locator `declared_line`)
- Observation: Broker 边界独立负责注册、订阅、发布和路由，并把客户端状态、可用层计算及 provider 存储委派给专门类型。

```text
   62: import java.util.stream.Collectors;
   63: 
   64: /**
   65:  * Message broker service for routing Vehicle Map Service messages between clients.
   66:  *
   67:  * This service is also responsible for tracking VMS client connections and broadcasting
```

## FW-11

- Blind ID: `blind-1db9772e8714`
- HEAD: `340a98a1fb783a561d4a240e9c0b420949c94c2d`
- Tier / blind mean: `medium` / `1.375`
- Exploration: 96 files, 40 directories, 17 tool calls, 232.14 seconds, truncated=false

### solid = 2

- Path/ref: `hvac-service/src/com/cockpitbench/hvac/service/HvacSignalRouter.java` / `HEAD`
- Symbol: `Adapter and HvacSignalRouter, lines 18-19` (locator `declared_line`)
- Observation: 车辆属性读写被隔离在可替换的 Adapter 接口后，路由器只负责映射和缩放。

```text
   16: package com.cockpitbench.hvac.service;
   17: import java.util.*;
   18: public final class HvacSignalRouter {public interface Adapter{void write(int property,int area,float value)throws Exception;float read(int property,int area)throws Exception;}public static final class Mapping{public final String operation;public final int property,area;public final float scale;public Mapping(String o,int p,int a,float s){operation=o;property=p;area=a;scale=s;}}
   19:  private final Adapter adapter;private final Map<String,Mapping> mappings=new HashMap<>();public HvacSignalRouter(Adapter a,Collection<Mapping> values){adapter=Objects.requireNonNull(a);for(Mapping v:values)mappings.put(v.operation,v);}public void write(String operation,float value)throws Exception{Mapping m=require(operation);adapter.write(m.property,m.area,value*m.scale);}public float read(String operation)throws Exception{Mapping m=require(operation);return adapter.read(m.property,m.area)/m.scale;}private Mapping require(String operation){Mapping m=mappings.get(operation);if(m==null)throw new IllegalArgumentException(operation);return m;}}
```

### integration_testing = 0

- Path/ref: `framework-testkit/Android.bp` / `HEAD`
- Symbol: `lines 1-6` (locator `declared_line`)
- Observation: 模块 srcs 指向 src/main/java/**/*.java，而七个已检查测试均位于 src/test/java，且模块类型是 java_library。

```text
    1: java_library {
    2:     name: "framework-foundation-testkit",
    3:     srcs: ["src/main/java/**/*.java", "src/main/aidl/**/*.aidl"],
    4:     resource_dirs: ["src/main/res"],
```

## FW-12

- Blind ID: `blind-419fa87cbf67`
- HEAD: `3a474c0b4e1d30474362fb3e01cc480da00be29a`
- Tier / blind mean: `medium` / `1.625`
- Exploration: 85 files, 38 directories, 18 tool calls, 260.555 seconds, truncated=false

### architecture = 2

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `lines 1-14` (locator `declared_line`)
- Observation: 声明 framework-api、shared-core、九个专用运行时/适配模块、framework-testkit，以及 media-api、media-routing、media-tests，共 14 个模块。

```text
    1: rootProject.name='CockpitFrameworkFoundation'
    2: include ':framework-api'
    3: include ':shared-core'
    4: include ':binder-runtime'
```

### aidl_sdk_call = 1

- Path/ref: `media-api/src/main/aidl/com/cockpitbench/mediarouting/IMediaRoutingService.aidl` / `HEAD`
- Symbol: `IMediaRoutingService, line 3` (locator `declared_line`)
- Observation: 服务合约使用 MediaEndpoint、RouteRequest 和 RouteState，并提供显式注册/注销回调。

```text
    1: package com.cockpitbench.mediarouting;
    2: import com.cockpitbench.mediarouting.RouteRequest; import com.cockpitbench.mediarouting.RouteState; import com.cockpitbench.mediarouting.MediaEndpoint; import com.cockpitbench.mediarouting.IMediaRouteCallback;
    3: interface IMediaRoutingService { List<MediaEndpoint> endpoints(int zoneId); RouteState createRoute(in RouteRequest request); void releaseRoute(String sessionId); void registerCallback(IMediaRouteCallback callback); void unregisterCallback(IMediaRouteCallback callback); }
```

## FW-13

- Blind ID: `blind-7abeaf0eb14f`
- HEAD: `5c25a7c4b6605077e6396de67509b7273a1bb9ad`
- Tier / blind mean: `medium` / `1.75`
- Exploration: 90 files, 20 directories, 22 tool calls, 274.615 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `platform-adapters/src/main/java/com/cockpitbench/frameworkfoundation/adapter/PlatformAdapterRegistry.java` / `HEAD`
- Symbol: `lines 18-19, Adapter and registry` (locator `declared_line`)
- Observation: 平台差异通过统一 Adapter 接口及按平台键注册/选择集中管理。

```text
   16: package com.cockpitbench.frameworkfoundation.adapter;
   17: import android.os.Bundle;import java.util.*;
   18: public final class PlatformAdapterRegistry {public interface Adapter{String platform();boolean supports(String capability);Bundle invoke(String operation,Bundle input)throws Exception;}private final Map<String,Adapter> values=new LinkedHashMap<>();
   19:  public synchronized void register(Adapter value){if(values.putIfAbsent(value.platform(),value)!=null)throw new IllegalStateException("duplicate platform");}public synchronized Adapter require(String platform){Adapter value=values.get(platform);if(value==null)throw new IllegalArgumentException("unknown platform");return value;}public synchronized List<String> platforms(){return Collections.unmodifiableList(new ArrayList<>(values.keySet()));}}
```

### aidl_sdk_call = 1

- Path/ref: `projection-api/src/com/cockpitbench/projection/IProjectionService.aidl` / `HEAD`
- Symbol: `line 3, IProjectionService` (locator `declared_line`)
- Observation: 服务以 ProjectionDevice、ProjectionCapability、ProjectionSession 等类型化对象定义连接和回调生命周期。

```text
    1: package com.cockpitbench.projection;
    2: import com.cockpitbench.projection.ProjectionDevice; import com.cockpitbench.projection.ProjectionSession; import com.cockpitbench.projection.ProjectionCapability; import com.cockpitbench.projection.IProjectionCallback;
    3: interface IProjectionService { List<ProjectionCapability> capabilities(in ProjectionDevice device); ProjectionSession connect(in ProjectionDevice device, String protocol); void disconnect(String sessionId); void registerCallback(IProjectionCallback callback); void unregisterCallback(IProjectionCallback callback); }
```

## FW-14

- Blind ID: `blind-4ae028ec439b`
- HEAD: `61df54de49560c6ab56df4310a9883997731d24d`
- Tier / blind mean: `medium` / `2.111111`
- Exploration: 638 files, 100 directories, 22 tool calls, 263.557 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `product/platform.properties` / `platform/8155`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: 平台特有内容仅为 update.platform=sa8155 和 update.slot=legacy-ab。

```text
    1: update.platform=sa8155
    2: update.slot=legacy-ab
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `line 1` (locator `declared_line`)
- Observation: 顶层明确声明 service、car-lib、car-builtin-lib、tests、updater-app 和 update-manager 子模块。

```text
    1: subdirs = ["service", "car-lib", "car-builtin-lib", "tests", "updater-app", "update-manager"]
```

## FW-19

- Blind ID: `blind-807c81bf2180`
- HEAD: `f201a8a4fd2ce4fdaf1b5d3a16d2347552332756`
- Tier / blind mean: `low` / `1.0`
- Exploration: 772 files, 45 directories, 19 tool calls, 271.492 seconds, truncated=false

### release_branch_strategy = 2

- Path/ref: `product/release.properties` / `release/2026.1`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: 发布分支相对 main 的唯一内容差异是发布渠道和契约版本配置。

```text
    1: can.channel=sop-2026.1
    2: can.contract=3
```

### code_duplication = 0

- Path/ref: `can-platform-8155/src/main/java/com/cockpitbench/can/platform/p8155/CanDecoder0.java` / `HEAD`
- Symbol: `lines 18-47` (locator `declared_line`)
- Observation: 完整实现属性映射、转换、支持范围、代次和时间戳逻辑。

```text
   16: package com.cockpitbench.can.platform.p8155;
   17: import com.cockpitbench.can.service.PlatformDecoder;
   18: public final class CanDecoder0 implements PlatformDecoder {
   19:     private static final int BASE = 1000;
   20:     @Override public int property(int frame, int offset) {
   21:         if (frame < 0x100 || offset < 0) throw new IllegalArgumentException("frame");
```

## FW-20

- Blind ID: `blind-3d6aa9fca710`
- HEAD: `0171c05a0e48eabd0bf83b073809a6f28b1f2172`
- Tier / blind mean: `low` / `0.888889`
- Exploration: 38 files, 21 directories, 21 tool calls, 243.9 seconds, truncated=false

### integration_testing = 2

- Path/ref: `tests/OccupantAwareness/src/com/android/car/test/OccupantAwarenessServiceIntegrationTest.java` / `HEAD`
- Symbol: `testDetectionEvents/testSystemTransitionsToReady lines 91-111` (locator `declared_line`)
- Observation: 测试跨 Manager、CarService 和 mock HAL 等待异步事件，并断言检测内容及系统状态迁移。

```text
   89: 
   90:     @Test
   91:     public void testDetectionEvents() throws Exception {
   92:         // Since the test assumes mock hal is the source of detections, the pattern of driver and
   93:         // passenger detection is pre-determined. The test verifies that detections from occupant
   94:         // awareness manager matches expected detections.
```

### hidden_api_reflection = 0

- Path/ref: `facade-runtime/src/com/cockpitbench/systemfacade/ReflectionDispatcher.java` / `HEAD`
- Symbol: `dispatch lines 8-18` (locator `declared_line`)
- Observation: 动态拼接平台端点类名并 Class.forName；catch(Exception ignored) 丢失加载、输入和执行失败的区别。

```text
    6:         Object target = FacadeState.SERVICES.get(service);
    7:         try {
    8:             String platform = System.getProperty("ro.boot.soc_model", "8155").contains("8295")
    9:                     ? "8295" : "8155";
   10:             String type = Character.toUpperCase(service.charAt(0)) + service.substring(1);
   11:             String className = "com.cockpitbench.systemfacade.platform" + platform
```

Selected anchors: 40 across 20 repositories.
