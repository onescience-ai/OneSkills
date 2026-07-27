## description
为 MACE 数据集合选择 extxyz/HDF5 接入、训练和评测路线的规划知识。

## when_to_use
当任务需要使用 `matchem/mace` 下 ANI1x、water、DMC 或 nanotube 数据训练/测试 MACE 或其它等变原子势模型时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mace`。任务输入规范：ASE 可读结构文件、ANI1x HDF5 分片、能量和力标签。

## outputs
输出为子集选择、train/val/test split、元素表、统计量、MACE dataloader 配置和 energy/force metric。

## procedure
1. 根据任务选择子集：ANI1x、water、DMC、nanotube 或多子集混合。
2. 对 extxyz 使用 ASE 抽样读取，确认 properties 中的 energy/forces/cell/pbc。
3. 对 ANI1x HDF5 先探测内部 group 和 dataset，再写 reader。
4. 按现有文件名和目录使用 train/val/test split。
5. 统计元素集合、原子数分布、能量均值/尺度和力分布。
6. 构建 AtomicData batch，检查 MACE 所需 `r_max`、元素表和归一化。
7. 分子集或子集分别输出评测指标。

## constraints
不同子集不能无单位校准直接合并；HDF5 字段需要真实探测；没有 stress 的文件不得启用应力 head；非周期分子要补合适 cell。

## next_phase_recommendation
若目标是标准 MACE 训练，优先从 extxyz split 建立最小可运行配置；若目标是 ANI1x 全量训练，先完成 HDF5 reader 和统计量校验。

## fallback
若 HDF5 依赖或字段不明确，先使用已拆分的 `ani1x_train.xyz/ani1x_test.xyz` 或其它 extxyz 子集完成 smoke test。
