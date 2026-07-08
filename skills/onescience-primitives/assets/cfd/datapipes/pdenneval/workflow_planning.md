# description

该原语用于 PDEBench/PDE neural operator 任务编排，在同一 HDF5 数据源上按模型族选择合适的数据协议。

# when_to_use

- 用户数据是 PDEBench 风格 HDF5/H5。
- 目标是 FNO、DeepONet、UNet、UNO、PINO 或 MPNN。
- 需要空间/时间降采样和 initial_step 历史输入。
- 需要多模型评估但允许每个模型使用不同 batch 协议。

# inputs

- HDF5 数据路径和文件名。
- 是否单文件、降采样参数、initial_step、test_ratio。
- 目标模型族。
- 模型族特定参数，例如 MPNN 的 PDE 定义或 PINO 的 PDE residual 配置。

# outputs

- 对应模型族的 train/val dataloader。
- 模型所需 history、target、grid 或 graph creator。
- PINO 的 PDE residual dataloader。

# procedure

1. 先确认任务模型族，不要只按文件名选择 datapipe。
2. 打开 HDF5 检查字段键和维度。
3. 设定降采样和 initial_step，确保输出 shape 匹配模型。
4. 根据模型族实例化对应 Datapipe。
5. 在训练脚本中按该 datapipe 的协议解包 batch。

# constraints

- 返回协议差异是核心约束。
- 不存在统一的默认 LSM datapipe。
- 部分源码分支需要补齐或验证后才能用于正式实验。

# next_phase_recommendation

若用户要求 CFD_Benchmark 默认 FNO/U-Net/LSM 路线，先核对模型卡和示例路径；若数据不是 HDF5，而是 case 目录或 pickle，改用 CFDBench 或 DeepCFD；若数据是非结构网格，改用 AirfRANS/ShapeNetCar。

# fallback

- 字段不匹配时先离线转换为 PDEBench 标准键。
- 内存不足时从 single_file 切换到多文件懒加载。
- 模型协议不清时先打印一个 batch 的结构再接训练。
