# launch

Protenix 用于 AF3-style 的蛋白、核酸、配体及其复合物结构预测。用户说“用 Protenix 跑 complex inference”“使用 OneScience/Protenix PyTorch 入口预测蛋白-配体/蛋白-DNA/蛋白-RNA/多链复合物结构”“有 Protenix JSON 想做复合物推理”时召回。若用户明确要求 AlphaFold3、AF3 JAX、`run_alphafold.py`、`model_dir` 或官方 AF3 data pipeline，不要抢 Protenix，应转 AlphaFold3 路线。

带 MSA 的复合物推理示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/protenix/runner/inference_unified.py --input_json_path examples/biosciences/protenix/infer_datasets/example.json --load_checkpoint_path "$ONESCIENCE_MODELS_DIR/protenix/checkpoint.pt" --dump_dir "$RUN_DIR/protenix_out" --seeds 101 --use_msa true --dtype bf16 --model.N_cycle 10 --sample_diffusion.N_sample 5 --sample_diffusion.N_step 200
```

快速无 MSA 连通性检查示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/protenix/runner/inference_unified.py --input_json_path examples/biosciences/protenix/infer_datasets/example_without_msa.json --load_checkpoint_path "$ONESCIENCE_MODELS_DIR/protenix/checkpoint.pt" --dump_dir "$RUN_DIR/protenix_nomsa_check" --seeds 101 --use_msa false --dtype bf16 --model.N_cycle 1 --sample_diffusion.N_sample 1 --sample_diffusion.N_step 20
```

多 seed 复合物候选示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/protenix/runner/inference_unified.py --input_json_path "$RUN_DIR/protenix_input.json" --load_checkpoint_path "$ONESCIENCE_MODELS_DIR/protenix/checkpoint.pt" --dump_dir "$RUN_DIR/protenix_multi_seed" --seeds 101 202 303 --use_msa true --dtype bf16 --model.N_cycle 10 --sample_diffusion.N_sample 5 --sample_diffusion.N_step 200
```

# input_schema

- 输入对象：Protenix JSON 或入口脚本支持的 AF3-style JSON、checkpoint、输出目录、seed、是否使用 MSA、扩散采样参数和 dtype。
- JSON 应明确实体类型、链/实体 ID、蛋白序列、RNA/DNA 序列、配体或 CCD 信息、MSA/template 相关字段。
- 小分子或修饰残基场景需要 CCD/RDKit 等化学依赖可用；不要把普通 FASTA 当作 Protenix JSON。
- 常用默认/显式参数：`dtype=bf16`，`model.N_cycle=10`，`sample_diffusion.N_sample=5`，`sample_diffusion.N_step=200`；快速检查可降低 cycle/sample/step。
- AF3 JSON、Protenix JSON 与 Protenix 模型 feature dict 概念相近但不能直接混用；执行前需确认入口脚本支持的 JSON 字段。
- 智能体召回时建议记录：`usage_mode=complex_structure_prediction | ligand_complex | nucleic_acid_complex | design_validation`，`entrypoint=inference_unified.py`，`input_artifacts=input_json | msa | ligand_ccd`，`output_artifacts=cif | pdb | confidence | contact`，`preflight_checks=json_schema | checkpoint | chemical_components | msa_flag | attention_backend`。

# runtime_interfaces

- `inference_unified.py`：Protenix 统一推理入口，负责读取 JSON、加载 checkpoint、执行采样并写出结构结果。
- `DataPipeline`：把 JSON、MSA、template、配体和化学组件转换为模型特征。
- `Protenix.forward`：模型前向与结构生成主体。
- `SampleDiffusion`：控制扩散采样数量和步数。

# main_functions

- `forward`
- `sample`

# execution_resources

- 推荐 GPU，`bf16` 通常用于降低显存；复合物规模、MSA、扩散样本数和 step 会显著影响资源。
- 需要 Protenix checkpoint、输入 JSON、MSA/template/化学组件资源和可写输出目录。
- 输出通常包括结构文件、置信度、接触或排名相关结果；可用于复合物候选筛选。
- 观察项应包含：是否生成 CIF/PDB、采样数是否符合预期、置信度是否可解析、失败是否来自 JSON 字段、化学组件、MSA、checkpoint、attention 或显存。

# operation_limits

- 不用于 RFdiffusion 式从头生成 backbone；骨架生成应召回 RFdiffusion。
- 不用于给定 backbone 的序列设计；序列设计应召回 ProteinMPNN。
- 不把 OpenFold feature dict 或普通 FASTA 直接当作 Protenix 输入。
- 不替代 AlphaFold3 JAX 路线；用户显式要求 AlphaFold3、AF3 `model_dir` 或 JAX data pipeline 时，应选择 AlphaFold3。
- 小分子、离子、修饰残基和核酸输入必须按 Protenix 支持的字段和化学组件规范准备。
