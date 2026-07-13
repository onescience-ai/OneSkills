# launch

```sh
python -c "from onescience.models.simplefold.torch.architecture import FoldingDiT; print(FoldingDiT.__name__)"
```

# input_schema

准备 SimpleFold atom-token feature dict，重点检查 `noised_pos`、`t`、`atom_to_token`、`atom_to_token_idx`、`ref_atom_name_chars` 和 `esm_s`。`esm_s` 的层数和 hidden 维必须与 `esm_model` 配置一致。

# runtime_interfaces

- `FoldingDiT.forward`: 输入 noised coordinates 和特征，返回 velocity 与 token latent。
- `SimpleFold` training step: 调用 velocity model 计算 flow matching 目标。
- sampler: 用 velocity field 积分得到坐标轨迹。

# main_functions

- `forward`

# execution_resources

需要加载 ESM 条件表征和 SimpleFold 模型权重。atom local attention 的窗口大小、`hidden_size` 和 token/atom 数共同决定显存。

# operation_limits

`contract_only` 表示不能直接假设 `OneTransformer(style="SimpleFoldFoldingDiT")` 可运行。输出是 velocity，不是最终坐标；最终坐标来自 sampler 对速度场积分。
