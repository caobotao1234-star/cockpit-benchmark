# G3 blind anchor review worklist

Coordinator-only bounded excerpts. This file is evidence input, not the final human acceptance record.
Every selected anchor is read from the exact manifest HEAD or its declared local branch.

## APP-01

- Blind ID: `blind-3f544ea3efd4`
- HEAD: `7d347803ae70eb01fdeafaff3094404909377c59`
- Tier / blind mean: `high` / `1.777778`
- Exploration: 49 files, 27 directories, 22 tool calls, 372.131 seconds, truncated=false

### architecture = 2

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `lines 1-4` (locator `declared_line`)
- Observation: 声明 app、settings-common、settings-connectivity、settings-security 四个 Gradle 模块。

```text
    1: pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
    2: dependencyResolutionManagement { repositories { google(); mavenCentral() } }
    3: rootProject.name = "AuroraSettings"
    4: include(":app", ":settings-common", ":settings-connectivity", ":settings-security")
```

### integration_testing = 1

- Path/ref: `tests/robotests/src/com/android/car/settings/security/InitialLockSetupServiceTest.java` / `HEAD`
- Symbol: `lines 82-222` (locator `declared_line`)
- Observation: 行为覆盖较深，但 IInitialLockSetupService.Stub.asInterface 接收的是服务直接返回的本地 Binder，没有进程死亡或重连场景。

```text
   80: 
   81:     @Test
   82:     public void testBindReturnsInstanceOfServiceInterface_ifLockNotSet() throws RemoteException {
   83:         assertThat(mInitialLockSetupService.onBind(
   84:                 new Intent()) instanceof IInitialLockSetupService.Stub).isTrue();
   85:     }
```

## APP-02

- Blind ID: `blind-bcc8acfa07b8`
- HEAD: `be0ba1df6a22d6db71add7e1bab11166ac9fa632`
- Tier / blind mean: `high` / `2.0`
- Exploration: 56 files, 38 directories, 19 tool calls, 317.511 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `product/platform.properties` / `platform/8155`
- Symbol: `launcher.platform/taskview.max_surfaces（1-2）` (locator `token:max_surfaces`)
- Observation: 8155 特性被隔离为配置，没有维护独立源码家族。

```text
    1: launcher.platform=sa8155
    2: launcher.taskview.max_surfaces=2
```

### code_duplication = 1

- Path/ref: `libs/car-launcher-common/src/com/android/car/carlaunchercommon/proto/ProtoDataSource.kt` / `HEAD`
- Symbol: `ProtoDataSource（36-37）` (locator `token:ProtoDataSource`)
- Observation: 源码 TODO 明确说明该类从 AppGrid 复制并应复用；app-grid 中仍有独立的 Java ProtoDataSource 实现。

```text
   35: </T> */
   36: // TODO: b/301482942 This class is copied from AppGrid. We should reuse it in AppGrid
   37: abstract class ProtoDataSource<T : MessageLite>(private val dataFile: File) {
   38:     private var mInputStream: FileInputStream? = null
   39:     private var mOutputStream: FileOutputStream? = null
   40: 
```

## APP-03

- Blind ID: `blind-27a7a19bd9e6`
- HEAD: `ac879cfbd59347cbc7a607f9cd7799f5b30aebda`
- Tier / blind mean: `high` / `2.111111`
- Exploration: 77 files, 32 directories, 19 tool calls, 329.945 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `vehicle-api/src/main/java/com/cockpitbench/climatix/vehicle/catalog/CatalogBackedClimatePlatformProfile.kt` / `HEAD`
- Symbol: `CatalogBackedClimatePlatformProfile, lines 21-41` (locator `declared_line`)
- Observation: 通过 delegate 复用公共平台行为，只从集中目录覆盖六个核心信号映射，并验证目录完整性。

```text
   19: import com.cockpitbench.climatix.vehicle.*
   20: 
   21: class CatalogBackedClimatePlatformProfile(
   22:     private val catalog: VehicleSignalCatalog,
   23:     private val delegate: ClimatePlatformProfile = DefaultClimatePlatformProfile,
   24: ) : ClimatePlatformProfile by delegate {
```

### integration_testing = 1

- Path/ref: `app/src/androidTest/java/com/cockpitbench/climatix/ClimateServiceContractTest.kt` / `HEAD`
- Symbol: `typedBinderRoundTripPreservesIdentityAndResult, lines 27-46` (locator `declared_line`)
- Observation: 验证类型和值，但服务是测试方法内的本地 IClimateControl.Stub；未覆盖跨进程 marshalling、权限或死亡恢复。

```text
   25: @RunWith(AndroidJUnit4::class)
   26: class ClimateServiceContractTest {
   27:     @Test fun typedBinderRoundTripPreservesIdentityAndResult() {
   28:         var captured: ClimateWriteRequest? = null
   29:         val local = object : IClimateControl.Stub() {
   30:             override fun readSignal(propertyId: Int, areaId: Int) = ClimateSignal(propertyId, areaId, 21.5f, 42L, true)
```

## APP-04

- Blind ID: `blind-2b9f2b0b4244`
- HEAD: `fb12fe8e07d48404739ca20e99a9cb0a1addb2e7`
- Tier / blind mean: `high` / `1.666667`
- Exploration: 40 files, 14 directories, 17 tool calls, 281.898 seconds, truncated=false

### architecture = 2

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `line 4 include` (locator `declared_line`)
- Observation: 构建声明 local-source、media-platform、media-runtime 三个模块。

```text
    2: dependencyResolutionManagement { repositories { google(); mavenCentral() } }
    3: rootProject.name = "WaveMedia"
    4: include(":local-source", ":media-platform", ":media-runtime")
```

### solid = 1

- Path/ref: `media-runtime/src/com/cockpitbench/wavemedia/PlaybackSessionRuntime.java` / `HEAD`
- Symbol: `fields/constructor, lines 27-57` (locator `declared_line`)
- Observation: 运行时内部硬编码构造 reducer、队列、账本、目录、策略、遥测等大量具体对象及系统 Clock，替换和组合能力有限。

```text
   25: import java.util.concurrent.atomic.AtomicLong;
   26: 
   27: public final class PlaybackSessionRuntime implements AudioFocusBoundary.Listener {
   28:     private final PlaybackReducer reducer = new PlaybackReducer();
   29:     private final QueueCoordinator queues = new QueueCoordinator(200);
   30:     private final SessionLedger ledger = new SessionLedger(256, Clock.systemUTC());
```

## APP-08

- Blind ID: `blind-a082461d66e4`
- HEAD: `5979fd66bc999bdd6119226be98cd9ad44b8138a`
- Tier / blind mean: `medium` / `2.0`
- Exploration: 57 files, 26 directories, 21 tool calls, 362.691 seconds, truncated=false

### solid = 2

- Path/ref: `audio-platform/upstream/service/src/com/android/car/audio/hal/AudioControlFactory.java` / `HEAD`
- Symbol: `newAudioControl, lines 36-65` (locator `declared_line`)
- Observation: 工厂按 AIDL、HIDL V2、HIDL V1 选择实现，消费者依赖 AudioControlWrapper 而非具体版本，新增实现的影响被集中。

```text
   34:     }
   35: 
   36:     /**
   37:      * Generates {@link AudioControlWrapper} for interacting with IAudioControl HAL service. The HAL
   38:      * version priority is: Current AIDL, HIDL V2, HIDL V1. The wrapper will try to fetch the
   39:      * highest priority service, and then fall back to older versions if it's not available. The
```

### architecture = 2

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `lines 3-5` (locator `declared_line`)
- Observation: 根工程声明 voice-app、voice-runtime、telephony、telephony:framework、telephony:testing、audio-platform 和 voice-tests，形成可辨识的模块入口。

```text
    1: pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
    2: dependencyResolutionManagement { repositories { google(); mavenCentral() } }
    3: rootProject.name = "EchoVoice"
    4: include(":voice-app", ":voice-runtime", ":telephony", ":telephony:framework",
    5:         ":telephony:testing", ":audio-platform", ":voice-tests")
```

## APP-09

- Blind ID: `blind-6e087540b475`
- HEAD: `2021dc74f9e199e037efc010725845ac6d52ac8b`
- Tier / blind mean: `medium` / `1.333333`
- Exploration: 50 files, 29 directories, 17 tool calls, 294.814 seconds, truncated=false

### architecture = 2

- Path/ref: `system-shell/src/com/android/systemui/CarSysUIComponent.java` / `HEAD`
- Symbol: `CarSysUIComponent, lines 33-51` (locator `declared_line`)
- Observation: 通过明确的 Dagger 子组件和模块列表集中组合 Car SystemUI。

```text
   31:  * Dagger Subcomponent for Core SysUI.
   32:  */
   33: @SysUISingleton
   34: @Subcomponent(modules = {
   35:         CarComponentBinder.class,
   36:         DependencyProvider.class,
```

### aidl_sdk_call = 1

- Path/ref: `DirectRenderingCluster/AndroidManifest.xml` / `HEAD`
- Symbol: `ClusterRenderingService declaration, lines 61-68` (locator `declared_line`)
- Observation: 渲染服务以 BIND_INSTRUMENT_CLUSTER_RENDERER_SERVICE 权限保护，且不导出。

```text
   59:                  android:icon="@mipmap/ic_launcher"
   60:                  android:directBootAware="true">
   61:         <service android:name=".ClusterRenderingService"
   62:                  android:exported="false"
   63:                  android:singleUser="true"
   64:                  android:permission="android.car.permission.BIND_INSTRUMENT_CLUSTER_RENDERER_SERVICE"/>
```

## APP-15

- Blind ID: `blind-af733aac52fc`
- HEAD: `33e092be7f1376ae652adbf1c96fc4d7841c45da`
- Tier / blind mean: `low` / `1.222222`
- Exploration: 1055 files, 97 directories, 19 tool calls, 389.555 seconds, truncated=false

### solid = 2

- Path/ref: `src/com/android/car/settings/common/PreferenceController.java` / `HEAD`
- Symbol: `PreferenceController<V>（第87-151行）、setPreference（第205-214行）` (locator `token:PreferenceController`)
- Observation: 泛型 Preference 上界、运行时类型校验以及受控生命周期钩子让扩展保持明确契约。

```text
   55:  *     android:icon="@drawable/ic_settings"
   56:  *     android:fragment="com.android.settings.foo.MyFragment"
   57:  *     settings:controller="com.android.settings.foo.MyPreferenceController"/>
   58:  * }</pre>
   59:  *
   60:  * <p>Subclasses must implement {@link #getPreferenceType()} to define the upper bound type on the
```

### code_duplication = 0

- Path/ref: `src/com/android/car/settings/common/PreferenceController.java` / `HEAD`
- Symbol: `PreferenceController（第87行起）` (locator `token:PreferenceController`)
- Observation: legacy 版本约 426 行，与 modern 同包同名基类形成独立演进的大型副本。

```text
   55:  *     android:icon="@drawable/ic_settings"
   56:  *     android:fragment="com.android.settings.foo.MyFragment"
   57:  *     settings:controller="com.android.settings.foo.MyPreferenceController"/>
   58:  * }</pre>
   59:  *
   60:  * <p>Subclasses must implement {@link #getPreferenceType()} to define the upper bound type on the
```

## APP-16

- Blind ID: `blind-c199615f0c53`
- HEAD: `7e60333d1980be7209b8b2d81fb33873dd50f3ea`
- Tier / blind mean: `low` / `1.222222`
- Exploration: 61 files, 45 directories, 18 tool calls, 370.833 seconds, truncated=false

### aidl_sdk_call = 2

- Path/ref: `app/src/com/android/car/carlauncher/recents/CarQuickStepService.java` / `HEAD`
- Symbol: `onBind/CarLauncherProxyBinder，57-103、225-231 行` (locator `token:CarLauncherProxyBinder`)
- Observation: 返回 ILauncherProxy.Stub，使用 IRecentTasks.Stub.asInterface 解包类型化代理，并在远程回调失败时捕获 RemoteException。

```text
   58:     @Override
   59:     public IBinder onBind(Intent intent) {
   60:         return new CarLauncherProxyBinder();
   61:     }
   62: 
   63:     @Override
```

### code_duplication = 0

- Path/ref: `platform/8155/Android.bp` / `HEAD`
- Symbol: `NovaLauncher8155Stack，3-6 行` (locator `token:NovaLauncher8155Stack`)
- Observation: 模块将 platform/8155/app/src 下的整棵 Java 树作为独立库编译；有界目录比较确认其 70 个源码文件与 8295 树完全一致。

```text
    2: 
    3: android_library {
    4:     name: "NovaLauncher8155Stack",
    5:     srcs: ["app/src/**/*.java"],
    6:     platform_apis: true,
    7: }
```

## APP-17

- Blind ID: `blind-d4d90a7ebecf`
- HEAD: `85fca70e962f51ebffbc52ab75084e58d3789efb`
- Tier / blind mean: `low` / `0.777778`
- Exploration: 35 files, 17 directories, 19 tool calls, 274.089 seconds, truncated=false

### release_branch_strategy = 2

- Path/ref: `app/src/main/res/xml/release_channel.xml` / `release/0.9`
- Symbol: `lines 1-2` (locator `declared_line`)
- Observation: release/0.9 相对共同基点只新增 pilot-sop 发布通道配置。

```text
    1: <?xml version="1.0" encoding="utf-8"?>
    2: <release-channel name="pilot-sop" />
```

### aidl_sdk_call = 0

- Path/ref: `vehicle/src/main/aidl/com/cockpitbench/thermo/vehicle/ILegacyClimateService.aidl` / `HEAD`
- Symbol: `ILegacyClimateService, lines 3-11` (locator `declared_line`)
- Observation: 接口由通用 read/write、字符串 preset、reset 和 dumpState 组成，没有结果类型、回调或错误契约。

```text
    1: package com.cockpitbench.thermo.vehicle;
    2: 
    3: interface ILegacyClimateService {
    4:     int read(int propertyId, int areaId);
    5:     float readFloat(int propertyId, int areaId);
    6:     void write(int propertyId, int areaId, int value);
```

## APP-18

- Blind ID: `blind-23cabcca60c3`
- HEAD: `a88e94b024b5a13653d20034e3db753640371c0e`
- Tier / blind mean: `low` / `1.111111`
- Exploration: 59 files, 14 directories, 18 tool calls, 272.295 seconds, truncated=false

### aidl_sdk_call = 2

- Path/ref: `media-platform/src/android/car/media/ICarMedia.aidl` / `HEAD`
- Symbol: `ICarMedia, lines 28-42` (locator `declared_line`)
- Observation: 媒体源获取、设置、监听注册/注销、历史和独立播放配置被拆成明确的类型化调用。

```text
   26:  * @hide
   27:  */
   28: interface ICarMedia {
   29:     /** Gets the currently active media source for the provided mode */
   30:     ComponentName getMediaSource(int mode);
   31:     /** Sets the currently active media source for the provided mode */
```

### code_duplication = 0

- Path/ref: `platform-8155/src/com/android/car/media/localmediaplayer/runtime/VehicleMediaPolicy.java` / `HEAD`
- Symbol: `lines 28-101` (locator `declared_line`)
- Observation: 该平台模块包含 8155、8295、xinqing 全部策略；与 platform-8295 同路径文件逐行相同，而非仅包含平台差异。

```text
   26: 
   27:     public VehicleMediaPolicy() {
   28:         maximumVolumes.put("8155", 34);
   29:         maximumVolumes.put("8295", 40);
   30:         maximumVolumes.put("xinqing", 28);
   31:         fallbackSources.put("8155", "local");
```

## FW-01

- Blind ID: `blind-5d41ad31c1bc`
- HEAD: `83c5c24261f986c7b8586eb7093ac9124712f7ab`
- Tier / blind mean: `high` / `2.333333`
- Exploration: 47 files, 25 directories, 20 tool calls, 310.221 seconds, truncated=false

### aidl_sdk_call = 3

- Path/ref: `car-lib/src/android/car/watchdog/ICarWatchdogService.aidl` / `HEAD`
- Symbol: `ICarWatchdogService, lines 27-58` (locator `declared_line`)
- Observation: 合约明确说明哪些调用因需要调用方 PID/UID 而不能 oneway，并把监听器、用户和错误返回拆为类型化操作。

```text
   25: 
   26: /** @hide */
   27: interface ICarWatchdogService {
   28:     // registerClient needs to get callingPid, so cannot be oneway.
   29:     void registerClient(in ICarWatchdogServiceCallback client, in int timeout);
   30:     void unregisterClient(in ICarWatchdogServiceCallback client);
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `lines 3-14, CarApiCoreBoundary and CarApiServiceBoundary` (locator `declared_line`)
- Observation: 核心 API/内建桥接先组成 Java 库，服务边界静态依赖核心库，依赖方向清晰。

```text
    1: package { default_applicable_licenses: ["Android-Apache-2.0"] }
    2: 
    3: java_library {
    4:     name: "CarApiCoreBoundary",
    5:     srcs: ["car-lib/src/**/*.java", "car-lib/src/**/*.aidl", "car-builtin-lib/src/**/*.java"],
    6:     platform_apis: true,
```

## FW-02

- Blind ID: `blind-7fa7c1f510a7`
- HEAD: `6428daa9cbcd11a087f58871a20fda0a0ce282fd`
- Tier / blind mean: `high` / `2.111111`
- Exploration: 56 files, 18 directories, 19 tool calls, 322.663 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `config/platform.xml` / `platform/8155`
- Symbol: `line 1` (locator `declared_line`)
- Observation: 相对 main 唯一差异选择 sa8155、hidl 和订阅上限；无平台专属生产源码副本。

```text
    1: <vehicle-platform name="sa8155" transport="hidl" maxSubscriptions="128" />
```

### integration_testing = 1

- Path/ref: `tests/integration/com/android/car/CarPropertyManagerTest.java` / `HEAD`
- Symbol: `testReceiveOnErrorEvent/testNotReceiveOnErrorEventAfterUnregister, lines 454-490` (locator `declared_line`)
- Observation: 验证跨 Manager、Binder 服务和 HAL 注入的错误回调归属及注销后的生命周期行为。

```text
  452:     }
  453: 
  454:     @Test
  455:     public void testReceiveOnErrorEvent() throws Exception {
  456:         TestErrorCallback callback = new TestErrorCallback();
  457:         mManager.registerCallback(callback, VehiclePropertyIds.HVAC_TEMPERATURE_SET,
```

## FW-03

- Blind ID: `blind-627291ab9722`
- HEAD: `6f29358f3951a2efd68ac93515be97231cbab325`
- Tier / blind mean: `high` / `2.111111`
- Exploration: 51 files, 20 directories, 22 tool calls, 335.221 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `service/src/com/android/car/VehicleStub.java` / `HEAD`
- Symbol: `newVehicleStub lines 76-88 and abstract contract lines 93-181` (locator `declared_line`)
- Observation: 同一工厂优先 AIDL、回退 HIDL，并向上提供统一接口。

```text
   74:      * @return a vehicle stub to connect to Vehicle HAL.
   75:      */
   76:     public static VehicleStub newVehicleStub() throws IllegalStateException {
   77:         VehicleStub stub = new AidlVehicleStub();
   78:         if (stub.isValid()) {
   79:             return stub;
```

### hidden_api_reflection = 1

- Path/ref: `car-lib/src/com/android/car/internal/LargeParcelable.java` / `HEAD`
- Symbol: `toLargeParcelable/reconstructStableAIDLParcelable lines 175-235, 253-304` (locator `declared_line`)
- Observation: 通过字符串 sharedMemoryFd/readFromParcel 反射字段、构造器和方法；异常被类型化包装，但无显式允许列表。

```text
  173:      */
  174:     @Nullable
  175:     public static Parcelable toLargeParcelable(
  176:             @Nullable Parcelable p, @Nullable Callable<Parcelable> constructEmptyParcelable) {
  177:         if (p == null) {
  178:             return null;
```

## FW-04

- Blind ID: `blind-ee507aff68d9`
- HEAD: `be95188ed46871d0f4a7352de12745d24498b3d2`
- Tier / blind mean: `high` / `2.111111`
- Exploration: 220 files, 45 directories, 19 tool calls, 272.922 seconds, truncated=false

### platform_reuse = 3

- Path/ref: `service/src/com/android/car/audio/hal/AudioControlWrapper.java` / `HEAD`
- Symbol: `AudioControlWrapper，lines 35-159` (locator `declared_line`)
- Observation: 共同接口统一焦点、ducking、muting、gain callback、能力查询及死亡通知语义。

```text
   33: import java.util.List;
   34: 
   35: /**
   36:  * AudioControlWrapper wraps IAudioControl HAL interface, handling version specific support so that
   37:  * the rest of CarAudioService doesn't need to know about it.
   38:  */
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `CockpitAudioApi、CockpitOccupantUserApi、CockpitPowerApi、CockpitAudioSystemSupport、CockpitAudioService` (locator `token:CockpitAudioSystemSupport`)
- Observation: 模块依赖由 API/支持层指向服务层，测试模块依赖服务模块，整体依赖方向清楚。

```text
   39: 
   40: android_library {
   41:     name: "CockpitAudioSystemSupport",
   42:     srcs: [
   43:         "service/src/com/android/car/user/**/*.java",
   44:         "service/src/com/android/car/power/**/*.java",
```

## FW-09

- Blind ID: `blind-3e3daf67c2f9`
- HEAD: `a8745e64918984feeda68b7a26e39f193a11e523`
- Tier / blind mean: `medium` / `2.0`
- Exploration: 53 files, 22 directories, 17 tool calls, 334.779 seconds, truncated=false

### solid = 2

- Path/ref: `service/src/com/android/car/VehicleStub.java` / `HEAD`
- Symbol: `VehicleStub.newVehicleStub and abstract transport API, lines 33-181` (locator `declared_line`)
- Observation: 调用方依赖统一抽象，工厂优先选择 AIDL、不可用时回退 HIDL，两种实现共享订阅、死亡通知、读写与调试契约。

```text
   31: import java.util.ArrayList;
   32: 
   33: /**
   34:  * VehicleStub represents an IVehicle service interface in either AIDL or legacy HIDL version. It
   35:  * exposes common interface so that the client does not need to care about which version the
   36:  * underlying IVehicle service is in.
```

### architecture = 2

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `VehicleHalAdapterContracts / VehicleHalAdapterRuntime, lines 12-64` (locator `declared_line`)
- Observation: 契约源与运行时源分为两个 Soong 库，Runtime 通过 static_libs 单向依赖 Contracts。

```text
   10: }
   11: 
   12: java_library {
   13:     name: "VehicleHalAdapterContracts",
   14:     srcs: [
   15:         "car-lib/src/android/car/hardware/**/*.java",
```

## FW-10

- Blind ID: `blind-6e5ec6f5d251`
- HEAD: `0a844e957b1269cd0e1faa61c40e1e0b9f778434`
- Tier / blind mean: `medium` / `2.0`
- Exploration: 41 files, 16 directories, 15 tool calls, 311.151 seconds, truncated=false

### solid = 2

- Path/ref: `runtime/src/com/android/car/VehicleStub.java` / `HEAD`
- Symbol: `VehicleStub and SubscriptionClient, lines 33-59 and 62-181` (locator `declared_line`)
- Observation: 以统一抽象隔离 AIDL/HIDL 传输差异，并明确订阅、死亡通知、读取、写入等契约。

```text
   31: import java.util.ArrayList;
   32: 
   33: /**
   34:  * VehicleStub represents an IVehicle service interface in either AIDL or legacy HIDL version. It
   35:  * exposes common interface so that the client does not need to care about which version the
   36:  * underlying IVehicle service is in.
```

### architecture = 2

- Path/ref: `settings.gradle` / `HEAD`
- Symbol: `line 3` (locator `declared_line`)
- Observation: 声明 manager-api、manager-runtime、manager-platform、manager-tests 四个模块。

```text
    1: pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
    2: rootProject.name="CockpitManagerKit"
    3: include(":manager-api",":manager-runtime",":manager-platform",":manager-tests")
```

## FW-15

- Blind ID: `blind-00727545d250`
- HEAD: `8ec949ad990392a014d95b04236b71181039b952`
- Tier / blind mean: `low` / `0.888889`
- Exploration: 49 files, 16 directories, 25 tool calls, 352.25 seconds, truncated=false

### release_branch_strategy = 2

- Path/ref: `config/release-channel.xml` / `release/0.8`
- Symbol: `line 1` (locator `declared_line`)
- Observation: release/0.8 的唯一专属补丁是 pilot-sop freeze 配置，变更边界很小。

```text
    1: <release-channel name="pilot-sop" freeze="true" />
```

### integration_testing = 0

- Path/ref: `tests/unit/com/cockpitbench/carruntime/RuntimeConfigTest.java` / `HEAD`
- Symbol: `placeholder, lines 22-23` (locator `declared_line`)
- Observation: 唯一单元测试只执行 assertTrue(true)。

```text
   20: import org.junit.Test;
   21: 
   22: public final class RuntimeConfigTest {
   23:     @Test public void placeholder() { assertTrue(true); }
   24: }
```

## FW-16

- Blind ID: `blind-72caa63dd88d`
- HEAD: `e5ef0b5ba39ed54205d427ace5f4bba24458f151`
- Tier / blind mean: `low` / `1.111111`
- Exploration: 986 files, 136 directories, 21 tool calls, 406.831 seconds, truncated=false

### integration_testing = 2

- Path/ref: `tests/carservice_unit_test/src/com/android/car/VehicleStubTest.java` / `HEAD`
- Symbol: `death and remote-failure tests, lines 118-188` (locator `declared_line`)
- Observation: 分别验证 AIDL/HIDL descriptor、link/unlink death 及 RemoteException 行为，后续还覆盖大 Parcelable。

```text
  116:     }
  117: 
  118:     @Test
  119:     public void testGetInterfaceDescriptorHidl() throws Exception {
  120:         mHidlVehicleStub.getInterfaceDescriptor();
  121: 
```

### code_duplication = 0

- Path/ref: `car-lib/src/android/car/Car.java` / `HEAD`
- Symbol: `Car class, line 105; file length 2118` (locator `declared_line`)
- Observation: 该核心 API 文件与 legacy 路径对应文件逐字相同。

```text
  103:  *   Calling this API on a device with no such feature will lead to an exception.
  104:  */
  105: public final class Car {
  106: 
  107:     /**
  108:      *  Represents the platform SDK_INT version with which this car API is developed.
```

## FW-17

- Blind ID: `blind-2167d60d323e`
- HEAD: `7a2bc2cbb17a2e9c407958a38dd1d1884ec0a0c8`
- Tier / blind mean: `low` / `1.25`
- Exploration: 265 files, 35 directories, 19 tool calls, 340.655 seconds, truncated=false

### solid = 2

- Path/ref: `service/src/com/android/car/audio/hal/AudioControlWrapper.java` / `HEAD`
- Symbol: `lines 35-39 and 57-158` (locator `declared_line`)
- Observation: 版本无关的 HAL 接口封装功能、回调和死亡通知，调用者无需依赖具体 AIDL/HIDL 类型。

```text
   33: import java.util.List;
   34: 
   35: /**
   36:  * AudioControlWrapper wraps IAudioControl HAL interface, handling version specific support so that
   37:  * the rest of CarAudioService doesn't need to know about it.
   38:  */
```

### code_duplication = 0

- Path/ref: `service/src/com/android/car/audio/CarAudioService.java` / `HEAD`
- Symbol: `class CarAudioService; init() and release()` (locator `token:CarAudioService`)
- Observation: 与 platform/8155 副本约 1,562 行近乎相同，仅共享版本增加 CockpitBinderHubRuntime 导入、字段和生命周期调用。

```text
  104:  * Service responsible for interaction with car's audio system.
  105:  */
  106: public class CarAudioService extends ICarAudio.Stub implements CarServiceBase {
  107: 
  108:     static final String TAG = CarLog.TAG_AUDIO;
  109: 
```

## FW-18

- Blind ID: `blind-3f168d5d3871`
- HEAD: `74db57addbc12585ca258f0e054efa07492078a4`
- Tier / blind mean: `low` / `1.222222`
- Exploration: 47 files, 24 directories, 25 tool calls, 352.979 seconds, truncated=false

### integration_testing = 2

- Path/ref: `tests/carservice_test/src/com/android/car/CarPowerManagementTest.java` / `HEAD`
- Symbol: `testImmediateShutdown/testDisplayOnOff and PowerStatePropertyHandler, lines 62-240` (locator `declared_line`)
- Observation: 通过 MockedVehicleHal 注入电源状态，等待订阅和异步状态报告，并断言显示与启动完成行为。

```text
   60:     }
   61: 
   62:     private void setupPowerPropertyAndStart(boolean allowSleep) throws Exception {
   63:         addProperty(VehicleProperty.AP_POWER_STATE_REQ, mPowerStateHandler)
   64:                 .setConfigArray(Lists.newArrayList(
   65:                         allowSleep ? VehicleApPowerStateConfigFlag.ENABLE_DEEP_SLEEP_FLAG : 0));
```

### architecture = 1

- Path/ref: `Android.bp` / `HEAD`
- Symbol: `java_library VehiclePlatformLegacyCore / VehiclePlatformRuntime, lines 12-44` (locator `declared_line`)
- Observation: LegacyCore 将 car-lib、service 和 vehicle-hal-support-lib 全量汇入单库；Runtime 再静态依赖 LegacyCore 与整个 AIDL migration 库，模块边界非常粗。

```text
   10: }
   11: 
   12: java_library {
   13:     name: "VehiclePlatformLegacyCore",
   14:     srcs: [
   15:         "car-lib/src/**/*.java",
```

Selected anchors: 40 across 20 repositories.
