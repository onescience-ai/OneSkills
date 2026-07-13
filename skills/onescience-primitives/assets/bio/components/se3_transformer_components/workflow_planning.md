# description

该卡用于 RFdiffusion 结构轨道或自定义 SE(3) 等变图任务中的组件规划。

# when_to_use

- 明确需要修改 RFdiffusion 的 SE(3) structure track。
- 输入是 DGL 图和 fiber features。
- 需要分析等变 attention、basis 或 tensor field convolution。

# inputs

- DGL graph with `rel_pos`。
- `fiber_in`、`fiber_hidden`、`fiber_out`。
- degree feature dict 和 edge features。

# outputs

- SE3Transformer 或 wrapper 选择。
- fiber shape 检查。
- 与 RFdiffusion 后续模块的兼容性判断。

# procedure

1. 确认任务不是普通 RFdiffusion 推理。
2. 校验图、`rel_pos` 和 fiber degree。
3. 选择 SE3Transformer 或 RFdiffusion wrapper。
4. 若修改通道或 degree，同步检查后续 structure track。

# constraints

- 不把标量 tensor 当成高阶 fiber。
- 不缺省 `rel_pos`。
- 不让 SE3Transformer 承担 sampler 或 diffusion schedule 职责。

# next_phase_recommendation

若任务是完整 RFdiffusion 采样，回到 `rfdiffusion_components`；若只是等变层实验，补最小图输入测试。

# fallback

若 DGL 或 basis 构造失败，先退回到 graph preprocessing；若是 RFdiffusion wrapper shape 不匹配，按原 checkpoint 配置恢复通道和 degree。
