# launch

RFdiffusion 用于蛋白骨架生成、motif scaffolding、binder design、partial diffusion 和对称设计。用户说“生成蛋白骨架”“保留这个 motif 重新设计 scaffold”“围绕靶标设计 binder”“对已有结构做 partial diffusion”时召回。

无条件骨架生成示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/RFdiffusion" && python scripts/run_inference.py inference.output_prefix="$RUN_DIR/rfdiffusion/design" inference.num_designs=10 contigmap.contigs='[100-150]' inference.model_directory_path="$ONESCIENCE_MODELS_DIR/RFdiffusion/models"
```

motif scaffolding 示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/RFdiffusion" && python scripts/run_inference.py inference.input_pdb="$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/examples/input_pdbs/5TPN.pdb" inference.output_prefix="$RUN_DIR/rfdiffusion/motif" inference.num_designs=10 contigmap.contigs='[10-40/A163-181/10-40]' inference.model_directory_path="$ONESCIENCE_MODELS_DIR/RFdiffusion/models"
```

binder design 示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/RFdiffusion" && python scripts/run_inference.py inference.input_pdb="$RUN_DIR/target.pdb" inference.output_prefix="$RUN_DIR/rfdiffusion/binder" inference.num_designs=20 contigmap.contigs='[A1-150/0 80-120]' ppi.hotspot_res='[A30,A67,A91]' inference.model_directory_path="$ONESCIENCE_MODELS_DIR/RFdiffusion/models"
```

# input_schema

- 基础输入：Hydra override 参数、`inference.output_prefix`、`inference.num_designs`、`contigmap.contigs`、模型权重目录。
- 无条件生成：至少需要 contig 长度，如 `'[100-150]'`。
- motif scaffolding：需要 `inference.input_pdb` 和含固定 motif 片段的 contig，如 `'[10-40/A163-181/10-40]'`。
- binder design：需要目标 PDB、目标链 contig、binder 长度范围，可选 `ppi.hotspot_res` 指定热点残基。
- partial diffusion：需要输入 PDB、与输入长度一致的 contig，并设置 `diffuser.partial_T`。
- 常见默认参数：`diffuser.T=50`，`diffuser.partial_T=null`，`inference.num_designs=10`；首次运行可能生成 IGSO3 缓存。
- 智能体召回时建议记录：`usage_mode=unconditional | motif_scaffolding | binder_design | partial_diffusion | symmetry_design`，`entrypoint=run_inference.py`，`input_artifacts=contig | input_pdb | hotspot_res`，`output_artifacts=backbone_pdb | trb | trajectory`，`preflight_checks=contig_syntax | checkpoint_dir | output_prefix | input_pdb_chain_ids`。

# runtime_interfaces

- `run_inference.py`：Hydra CLI 推理入口，接收 contig、输入 PDB、checkpoint 和输出前缀。
- `Sampler`：根据任务配置选择 checkpoint、解析 contig、准备扩散输入并调度采样。
- `Diffuser`：执行坐标与旋转扩散过程。
- `RoseTTAFoldModule.forward`：RFdiffusion 的结构预测/去噪主体。

# main_functions

- `sample`
- `forward`

# execution_resources

- 推荐 GPU；设计数量、长度、轨迹保存和对称设计会增加运行时间和磁盘占用。
- 需要 RFdiffusion 权重目录、可写输出目录；有条件设计还需要输入 PDB 的链 ID 与 contig 一致。
- 输出通常包括 backbone PDB、TRB 元数据、可选轨迹文件；这些输出可直接进入 ProteinMPNN 序列设计。
- 观察项应包含：PDB 数量是否达到 `num_designs`、TRB 是否存在、contig 是否解析成功、失败是否来自 checkpoint、PDB 链号、热点残基或显存。

# operation_limits

- RFdiffusion 主要生成骨架，不负责输出最终可表达的氨基酸序列；通常必须后接 ProteinMPNN。
- 不用于给定序列的结构预测；序列折叠应召回 OpenFold、SimpleFold、ESMFold 或 Protenix。
- partial diffusion 要求输入结构长度、mask 和 contig 对齐；不满足时不要硬跑。
- binder design 成功率依赖靶标裁剪、热点选择和后续筛选；不能把生成 PDB 数量等同于成功设计数量。
