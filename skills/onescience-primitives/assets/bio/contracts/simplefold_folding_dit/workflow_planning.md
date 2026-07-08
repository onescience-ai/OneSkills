# description

该卡用于 SimpleFold flow matching 折叠任务中选择和规划 FoldingDiT 主干，明确其与 AF2/AF3 trunk 的边界。

# when_to_use

- 任务是 SimpleFold 训练、微调或采样。
- 输入包含 noised atom coordinates、SimpleFold feats 和 ESM 表征。
- 需要修改 atom encoder/decoder local attention 或 velocity head。

# inputs

- `noised_pos`、`t`、`feats`、可选 `self_cond`。
- ESM 模型配置与 `esm_s` shape。
- atom local window 配置。

# outputs

- FoldingDiT 调用策略。
- velocity 输出解释。
- shape 和 feature 风险清单。

# procedure

1. 确认任务是 SimpleFold flow matching，而非 AF2/AF3。
2. 检查 atom-token 映射和 ESM 表征维度。
3. 使用 FoldingDiT 预测 velocity。
4. 若要得到坐标，继续由 sampler 对速度场积分。

# constraints

- 不把 `predict_velocity` 当作最终 atom positions。
- 不缺省构造 `esm_s`。
- 不把 Protenix feature dict 直接传入 SimpleFold。

# next_phase_recommendation

若用户要运行采样，继续检查 sampler 与 checkpoint；若要迁移到 `OneTransformer`，先补 wrapper 和 registry。

# fallback

若 ESM 条件缺失，退回到数据准备阶段；若原生 SimpleFold API 可用，优先沿用原生入口。
