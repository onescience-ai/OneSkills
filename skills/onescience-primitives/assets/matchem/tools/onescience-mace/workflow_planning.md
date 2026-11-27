## description
本工具连接候选势验证 Task 与 models/mace 的原生重构及物理图推理接口，区分安装身份、原生兼容和科学模型准入。

## when_to_use
用于 OneScience MACE portable 模型原生构造、strict 加载与能量/力验证。仅有文件可读时可做资产定位和失败交付；不能据此启动尚未准入的 MD。GPU 分支需独立核验真实设备与依赖。

## inputs
实际软件安装与版本；模型卡给出的完整同身份 checkpoint/config；还原类型后的完整 model_config；合格目标结构/周期图、原始标签及训练暴露/独立性证据。

## outputs
软件入口和版本身份；原生导入、构造、strict、实际 energy/forces、独立精度和 MD 准入各阶段的真实状态。失败时交最后健康权重/config、错误、影响范围与恢复依赖，不生成未运行结果。

## procedure
1. 核实 launch 的真实安装入口与依赖组合，计划部署位置不可当实际包使用。
2. 沿模型卡取得完整配置和权重，核对同一身份，还原 Irreps、interaction 类、gate 与 float64 构造条件。
3. 原生导入后构造 ScaleShiftMACE，strict=True 加载并 eval；错误保留，绝不伪造设备或降低 strict。
4. 在合格目标周期图上计算 energy/forces，再用独立原始标签验证精度与最差构型；工程成功与科学通过分别报告。
5. 仅在输入和模型科学准入具备后交接超胞/MD；同时继续可行数据血缘与失败交付。

## constraints
模型卡是完整权重及物理参数的主体，此工具不另造替代权重。源码接口核对不等于执行通过；既有包失败不等于已发布修复。设备查询必须尊重真实 CPU/GPU 状态，保留 CPU 与 GPU 相邻分支的验证缺口。

## next_phase_recommendation
向 s02 提供实际入口、依赖边界和模型卡的加载参数关系。原生 strict 和目标独立验证分别具备证据后再考虑 MD 与部署等价性；科学输入不足时保留未验证。

## fallback
CPU 导入若沿可选天气/分布式链触发 GPU 属性查询失败，交工具所有者延迟可选导入与设备查询，并验证 CPU 导入、严格构造/加载、真实 energy/forces 及实际 GPU 分支。修复版本、发布包来源及部署未确认前保留最后健康模型文件和具体错误；继续可行数据审计。strict 的真实不匹配应拒绝，不用其他模型或合成标签填补。
