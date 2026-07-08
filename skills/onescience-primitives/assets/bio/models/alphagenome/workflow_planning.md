# description

AlphaGenome 规划知识用于把基因组区间预测、变异效应分析、轨迹评估和微调任务转换成可执行脚本或 SDK 调用，并确保参考基因组、物种、模型 fold、输出类型和资源约束一致。

# when_to_use

- 用户处理 DNA 序列、基因组区间、调控组学轨迹、Hi-C 接触图或剪接信号。
- 用户需要 SNV/VCF 变异效应评分。
- 用户需要 ATAC、DNase、CAGE、RNA-seq、ChIP、PRO-cap、Hi-C 或 splicing 预测。
- 不用于蛋白 FASTA、PDB、配体或小分子任务。

# inputs

- 任务模式: inference、variant_scoring、track_eval、finetuning。
- 基因组输入: FASTA、FAI、chromosome/start/end、VCF 或内置 variant。
- 模型输入: model_dir、model_version、organism。
- 输出需求: `.npy` 轨迹、CSV 评分、评估结果或微调 checkpoint。
- 资源输入: 是否允许下载、GPU/CPU、数据目录。

# outputs

- 调用决策: 是否使用 AlphaGenome。
- 执行计划: 对应脚本、参数、输入文件和输出目录。
- 产物说明: 预测轨迹、评分表、summary CSV、评估指标或 finetuned checkpoint。
- 下游建议: 调控注释、候选变异排序、轨迹可视化或实验验证。

# procedure

1. 判断任务是否属于 DNA/调控基因组学。
2. 确认物种、参考基因组和坐标系统。
3. 选择推理、变异评分、轨迹评估或微调入口。
4. 检查模型权重来源和是否允许下载。
5. 生成命令或 SDK 调用。
6. 检查输出 shape、track 类型、CSV 汇总和失败日志。
7. 将结果交给下游可视化、排序或统计分析。

# constraints

- 只支持 DNA/基因组语义输入。
- FASTA、FAI、organism、model version 和 metadata 必须一致。
- 变异评分必须校验 reference allele。
- `all_folds` 资源成本更高。
- 微调 BigWig 与 regions 必须在坐标和长度上匹配。

# next_phase_recommendation

- 轨迹输出可进入可视化、peak/track 比较和功能注释。
- 变异评分可进入候选排序、基因注释和实验优先级评估。
- 微调结果应在独立验证区间上评估。

# fallback

- 无本地权重时显式允许下载或提供 `model_dir`。
- 显存不足时使用单 fold、缩小 batch 或减少输出类型。
- FASTA/坐标错误时先用小区间 smoke test。
