# description

用于规划 Protenix 内部投影层选择和初始化策略。

# when_to_use

- 需要 Protenix 风格无 bias 投影。
- 需要零初始化 residual。
- 需要 bias 初始化门控。
- 需要固定 precision 投影。

# inputs

- 输入/输出维度。
- 是否需要 bias。
- initializer 和 precision。
- 所属 Protenix 子模块。

# outputs

```text
component_choice:
  name: protenix_linear
  style: ProtenixLinear | ProtenixLinearNoBias | ProtenixBiasInitLinear
  action: reuse | adjust_initializer | reject
```

# procedure

1. 确认是否需要 bias。
2. 选择初始化策略。
3. 检查混合精度需求。
4. 替换投影层时核对 checkpoint 兼容性。

# constraints

不要随意用普通 `nn.Linear` 替换；不要把 `OneFC` 当成 Protenix linear。

# next_phase_recommendation

根据所在模块继续检查 Protenix embedding、attention、MSA、Pairformer 或 diffusion 的维度约束。

# fallback

初始化不确定时优先沿用现有 Protenix 配置；checkpoint 不兼容时避免重命名参数。
