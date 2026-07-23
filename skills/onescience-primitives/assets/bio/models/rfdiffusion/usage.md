# launch

RFdiffusion 的模型主体是 `RoseTTAFoldModule`。上层扩散循环负责构造每一时间步的 MSA、序列、模板和坐标特征，模型 `forward` 预测结构更新、序列 logits 与置信度。

```sh
python -c "from onescience.models.rfdiffusion.RoseTTAFoldModel import RoseTTAFoldModule; import inspect; print(inspect.signature(RoseTTAFoldModule)); print(inspect.signature(RoseTTAFoldModule.forward))"
```

# input_schema

- 必需张量：`msa_latent`、`msa_full`、`seq`、初始 `xyz`、残基索引 `idx` 和扩散时间 `t`。
- 模板条件由 `t1d`、`t2d`、`xyz_t`、`alpha_t` 提供；`motif_mask` 标记固定/条件残基。
- recycling 可传 `msa_prev`、`pair_prev`、`state_prev`；`return_raw`、`return_full`、`return_infer` 控制返回层级。
- 构造参数描述 extra/main/refinement block 数、MSA/pair/template 宽度、attention heads、SE(3) 参数、总时间步和 motif 策略。
- `return_infer=True` 返回 MSA、pair、最终坐标、state、torsion、序列 logits 和 pLDDT；默认训练返回 distogram/orientation、序列、resolved、轨迹坐标、torsion、LDDT logits。

# runtime_interfaces

- `RoseTTAFoldModule(...)`：RFdiffusion 完整神经网络主体。
- `RoseTTAFoldModule.forward(...)`：单个扩散/回收步骤的训练与推理接口。
- `MSA_emb`、`Extra_emb`、`Templ_emb`、`Recycling`：输入与 recycling 模块。
- `IterativeSimulator`：结构/序列迭代更新主干。
- `DistanceNetwork`、`MaskedTokenNetwork`、`LDDTNetwork`：辅助预测头。

# main_functions

- `RoseTTAFoldModule.forward`
- `IterativeSimulator.forward`
- `Recycling.forward`

# execution_resources

- 依赖 PyTorch、SE(3) 模块以及与网络配置一致的 RFdiffusion checkpoint。
- 长链、模板数、MSA 深度和扩散步数共同决定显存与耗时；GPU/DCU 是常规运行环境。
- 完整生成需由上层采样器维护扩散时间表、self-conditioning/recycling 状态和输出结构。

# operation_limits

- `forward` 是单步模型接口，不会自行执行完整反向扩散循环或保存 PDB。
- motif mask、contig 映射、模板坐标和残基索引必须处于同一编号体系。
- 网络宽度、SE(3) 参数、时间步和输入序列表示必须与 checkpoint 一致。
- 生成骨架仍需 ProteinMPNN 等序列设计及独立结构验证。
