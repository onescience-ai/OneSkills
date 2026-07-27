## description
为 OC20 S2EF extxyz/ASE LMDB 数据选择 UMA 微调、材料势训练和评测路线的规划知识。

## when_to_use
当任务需要使用 `matchem/oc20` 训练 OC20 S2EF、UMA ESCN 或其它吸附-催化材料势模型时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/oc20`。任务输入规范：extxyz split 或 UMA `aselmdb` train/val 分片。

## outputs
输出为 train/val 数据配置、ASE LMDB 或 extxyz reader、AtomicData 字段映射、固定原子/tags 处理、energy/force metric。

## procedure
1. 选择入口：UMA 微调优先使用 `uma_oc20_finetune`；通用读取测试可用浅层 extxyz。
2. 检查 train/val split、`metadata.npz` 和 YAML 配置是否配套。
3. 枚举样本文件时排除 `.lock`、`.failed`、`.log`。
4. 抽样读取 AtomicData，确认 energy、forces、cell、pbc、tags、fixed、sid/fid。
5. 设置 `max_atoms`、cutoff、采样策略和 batch size。
6. 做单 batch 前向和 loss 检查。
7. 使用 val split 按 S2EF 指标输出 energy/force 误差。

## constraints
不得重复计入浅层 extxyz 和 `orig_data` 中的同源样本；tags/fixed/cell/pbc 不能在转换中丢失；LMDB 分片和 metadata 必须同 split 使用。

## next_phase_recommendation
若目标是 UMA，直接基于模板 YAML 生成微调配置；若目标是自定义势模型，先把 extxyz 或 LMDB 转换为通用 AtomicData datapipe。

## fallback
若 LMDB 读取失败，使用 extxyz 做最小 smoke test；若 metadata 不完整，先禁用依赖 metadata 的过滤条件并记录限制。
