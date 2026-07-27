## description
为 DPA3 CH_3787 DeepMD 格式数据选择微调和评测路线的规划知识。

## when_to_use
当任务需要使用 `matchem/dpa3/CH_3787` 做 DPA3 微调、CH 体系能量/力训练或验证集评测时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/dpa3`。任务输入规范：`train_CH` 和 `val_CH` 下的 `sys_*` DeepMD system。

## outputs
输出为 train/val 数据索引、元素映射、frame 级样本列表、DPA3 训练配置、loss 字段和验证指标。

## procedure
1. 以 `CH_3787/train_CH` 和 `CH_3787/val_CH` 建立 split。
2. 枚举 `sys_*`，检查每个目录的 `type.raw` 与 `set.000/*.npy`。
3. 抽检多个 system 的原子数、帧数、dtype、能量范围和力范围。
4. 从配置或数据说明解析 type 编号到元素的映射。
5. 构建支持变长原子数的 datapipe 或 DPA3 原生数据输入。
6. 做单 batch shape 检查，确认 `pos/forces`、`cell`、`energy` 维度正确。
7. 使用 `val_CH` 执行 energy/force 指标评测。

## constraints
`val_CH` 是验证集，不应参与训练；缺少 `type_map.raw` 时不能凭编号猜元素；stress/virial、电荷、自旋均需有真实字段才能启用。

## next_phase_recommendation
若元素映射和 batch schema 已确认，进入训练任务；若映射不明确，先回到数据说明或模型配置中补充元素表。

## fallback
若个别 `sys_*` 缺少 `box/coord/energy/force`，将其列为不可用样本；若 dtype 与模型不一致，在 datapipe 层转换为训练 dtype。
