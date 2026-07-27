## description
为 DP DeepMD raw/npy 数据选择接入、预处理、训练和评测路线的规划知识。

## when_to_use
当任务属于 materials/matchem 领域，且目标是使用 `matchem/dp` 下 water 或 dpa3_finetune 数据训练 Deep Potential、DPA3 或其它能量/力势模型时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/dp`。任务输入规范：DeepMD system 目录、原子类型、帧级坐标、晶胞、能量和力标签。

## outputs
输出为训练/验证 datapipe 配置、元素映射、frame 索引、AtomicData batch schema、能量/力 loss 配置和评测指标定义。

## procedure
1. 校验数据目录是否存在，区分 `water` 与 `dpa3_finetune` 子集。
2. 枚举 system，检查 `type.raw`、`type_map.raw`、`set.000` 和四类 `npy` 文件。
3. 抽样读取数组 shape，确认帧数一致和 `atoms * 3` 关系。
4. 建立元素类型映射，将 `coord/force` reshape 为 `[frames, atoms, 3]`。
5. 按已有 split 使用 `train_data/val_data`；未显式 split 的 water 固定划分策略。
6. 生成 datapipe 或 DeepMD 原生训练配置，并执行单 batch 检查。
7. 运行小样本训练，记录 energy/force loss 和验证指标。

## constraints
不得随机混合已有 `train_data` 与 `val_data`；没有 stress/virial 时不得启用相关监督；所有 system 的 type map、帧数和数组 shape 必须先检查。

## next_phase_recommendation
若 schema 和 split 已确认，进入训练脚本或 datapipe adapter 实现；若元素映射缺失，先补齐 type map；若数组 shape 不一致，先生成坏样本清单。

## fallback
若某个 system 缺文件或 shape 不匹配，跳过该 system 并记录路径；若统计文件不可读，仍可用原始 `npy` 进行无统计训练，但需要在配置中禁用依赖该统计文件的归一化。
