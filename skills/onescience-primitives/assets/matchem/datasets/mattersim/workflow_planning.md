## description
为 MatterSim 高精度水体系 extxyz 数据选择读取、划分、训练和评测路线的规划知识。

## when_to_use
当任务需要使用 `matchem/mattersim/high_level_water.xyz` 做水体系能量/力训练、MatterSim 微调或 extxyz 数据接入验证时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mattersim`。任务输入规范：包含 192 原子周期水帧的 extxyz 文件。

## outputs
输出为帧索引、train/val/test 划分、AtomicData schema、能量/力 loss 配置和水体系评测指标。

## procedure
1. 使用 ASE 或 extxyz parser 读取首帧，确认 `species/pos/forces/energy/Lattice/pbc`。
2. 统计文件总帧数、原子数是否固定、元素集合和能量/力范围。
3. 按连续帧区间或固定随机种子建立 split。
4. 转换为 AtomicData，保留周期 cell 和 PBC。
5. 做单 batch 构图检查，确认 cutoff 下邻接边规模。
6. 运行小样本训练，输出 energy/force loss。
7. 按整体和 O/H 原子类型报告 force 误差。

## constraints
不要启用未提供的 stress 监督；不要丢弃 PBC/cell；轨迹相邻帧相关性强，评测划分要避免泄漏。

## next_phase_recommendation
若单 batch 构图和 loss 正常，进入 MatterSim/MACE/UMA 微调；若显存不足，先降低 batch size 或 cutoff。

## fallback
若 extxyz 个别帧解析失败，记录 frame id 并跳过；若 energy 单位与模型预期不一致，先做单位转换配置，不改原始文件。
